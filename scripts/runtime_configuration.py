"""Validate a secret-free operator configuration and preflight trusted runtime registrations.

This module never loads a runtime, reads credentials, executes tools or grants authority.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit

from schema_validation import validate_instance

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'docs/agent/schemas/runtime-configuration.schema.json'
ROLES = {r['id'] for r in json.loads((ROOT / 'docs/agent/role-contracts.json').read_text())['roles']}
LIMIT = 2 * 1024 * 1024


def load(path: Path):
    with path.open('rb') as stream:
        data = stream.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError('Configuration exceeds the 2 MiB limit')
    return json.loads(data)


def _text_limits(value, schema: dict, path='$') -> list[str]:
    """The shared minimal schema engine does not implement maxLength."""
    errors = []
    if isinstance(value, float) and not math.isfinite(value):
        errors.append(f'{path}: non-finite numbers are not valid JSON')
    if isinstance(value, str):
        if not value.strip() or len(value) > schema.get('maxLength', 2048) or re.search(r'[\x00-\x1f\x7f]', value):
            errors.append(f'{path}: blank, excessive or control-containing text')
    if isinstance(value, dict):
        for key, item in value.items():
            errors.extend(_text_limits(item, schema.get('properties', {}).get(key, {}), path + '.' + key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(_text_limits(item, schema.get('items', {}), f'{path}[{index}]'))
    return errors


def validate_configuration(document) -> list[str]:
    schema = json.loads(SCHEMA.read_text())
    errors = validate_instance(document, schema)
    if errors:
        return errors
    errors.extend(_text_limits(document, schema))
    providers = {p['id']: p for p in document['providers']}
    profile = document['profile']
    models = {m['id']: m for m in profile['models']}
    if len(providers) != len(document['providers']):
        errors.append('Provider IDs must be unique')
    if len(models) != len(profile['models']):
        errors.append('Model IDs must be unique')
    roles = [r['role'] for r in profile['routes']]
    if len(roles) != len(set(roles)) or set(roles) != ROLES:
        errors.append('Routes must cover every governed role exactly once')
    used_providers = {m['providerId'] for m in models.values()}
    if used_providers != set(providers):
        errors.append('Providers must match model references exactly (no unknown or unused providers)')
    for provider in providers.values():
        try:
            url = urlsplit(provider['baseUrl'])
            _ = url.port
            if url.scheme not in {'http', 'https'} or not url.hostname or url.username is not None or url.password is not None or url.query or url.fragment:
                raise ValueError('Expected HTTP(S) API base URL without credentials, query or fragment')
            loopback = url.hostname in {'localhost', '127.0.0.1', '::1'}
            if url.scheme == 'http' and not loopback and not (provider['locality'] == 'local' and provider['allowInsecureHttp']):
                raise ValueError('Remote HTTP needs explicit local-service opt-in')
            if provider['locality'] == 'external' and provider['allowInsecureHttp']:
                raise ValueError('External services cannot enable local HTTP opt-in')
        except ValueError as exc:
            errors.append(f"Provider {provider['id']}: {exc}")
        auth = provider['auth']
        if not re.fullmatch(r'[A-Za-z0-9-]+', auth['header']) or auth['header'].lower() in {
            'host', 'content-length', 'content-type', 'accept', 'connection', 'cookie', 'proxy-authorization', 'anthropic-version'
        }:
            errors.append(f"Provider {provider['id']}: unsafe authentication header")
        if auth['mode'] == 'none' and auth['credentialRef'] is not None:
            errors.append('Unauthenticated provider has a credential reference')
        if auth['mode'] != 'none' and (not isinstance(auth['credentialRef'], str) or not re.fullmatch(r'env:[A-Z][A-Z0-9_]{0,127}', auth['credentialRef'])):
            errors.append('Credential must be an environment reference, never a key value')
    for model in models.values():
        provider = providers.get(model['providerId'])
        if profile['localOnly'] and provider and provider['locality'] != 'local':
            errors.append('Local-only configuration contains an external model or fallback')
        if model['contextWindow'] is not None and model['maxOutputTokens'] > model['contextWindow']:
            errors.append(f"Model {model['id']}: output limit exceeds context budget")
    for route in profile['routes']:
        if set(route['models']) - set(models):
            errors.append(f"Role {route['role']}: unknown model reference")
    return errors


def binding_hash(provider: dict, model: dict) -> str:
    canonical = json.dumps({'provider': provider, 'model': model}, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def inspect_configuration(document: dict) -> dict:
    errors = validate_configuration(document)
    if errors:
        raise ValueError('; '.join(errors[:20]))
    providers = {p['id']: p for p in document['providers']}
    return {'kind': 'runtime-configuration-inspection', 'schema_version': '1.0',
            'profile_id': document['profile']['id'], 'execution_authority': False,
            'bindings': [{'model_id': m['id'], 'protocol': providers[m['providerId']]['protocol'],
                          'binding_sha256': binding_hash(providers[m['providerId']], m),
                          'adapter_status': 'requires_trusted_registration'} for m in document['profile']['models']],
            'warnings': ['Configuration validity and UI probe results do not establish adapter availability, model quality or approval.',
                         'Locality is operator-declared; verify any gateway upstreams independently.']}


def resolve_configuration(document: dict, request: dict, inventory: dict, configuration_source: str, inventory_source: str) -> dict:
    """Read-only preflight. The independently trusted host must implement the actual adapter."""
    if configuration_source not in {'operator', 'trusted_platform'} or inventory_source not in {'operator', 'trusted_platform'}:
        raise ValueError('Configuration and adapter registrations must be independently supplied by operator or trusted platform')
    errors = validate_configuration(document)
    if errors:
        raise ValueError('; '.join(errors[:20]))
    if not isinstance(request, dict) or set(request) != {'stage', 'role'}:
        raise ValueError('Request must contain exactly stage and role')
    # Required model capabilities and stage/role relationships always come from the pack.
    routing = json.loads((ROOT / 'docs/agent/runtime-routing.json').read_text())
    stage, role = request['stage'], request['role']
    known_stages = {r['stage'] for r in routing['routes']} - {'*'}
    if not isinstance(stage, str) or not isinstance(role, str) or stage not in known_stages or role not in ROLES:
        raise ValueError('Unknown governed stage or role')
    exact = [r for r in routing['routes'] if r['stage'] == stage and r['role'] == role]
    matches = exact or [r for r in routing['routes'] if r['stage'] == '*' and r['role'] == role]
    if len(matches) != 1:
        raise ValueError('Stage/role does not resolve to one canonical route')
    required = set(matches[0]['required_model_capabilities'])
    if not isinstance(inventory, dict) or set(inventory) != {'schema_version', 'registrations'} or inventory['schema_version'] != '1.0' or not isinstance(inventory['registrations'], list) or len(inventory['registrations']) > 100:
        raise ValueError('Invalid runtime inventory')
    registrations = {}
    for item in inventory['registrations']:
        if not isinstance(item, dict) or set(item) != {'model_id', 'protocol', 'binding_sha256', 'ready', 'capabilities'}:
            raise ValueError('Invalid runtime registration fields')
        if not isinstance(item['model_id'], str) or item['model_id'] in registrations or not isinstance(item['protocol'], str) or not isinstance(item['ready'], bool) or not isinstance(item['binding_sha256'], str) or not re.fullmatch('[a-f0-9]{64}', item['binding_sha256']) or not isinstance(item['capabilities'], list) or not all(isinstance(c, str) for c in item['capabilities']):
            raise ValueError('Malformed or duplicate runtime registration')
        registrations[item['model_id']] = item
    providers = {p['id']: p for p in document['providers']}
    models = {m['id']: m for m in document['profile']['models']}
    if set(registrations) - set(models):
        raise ValueError('Inventory references unknown model bindings')
    route = next(r for r in document['profile']['routes'] if r['role'] == role)
    unavailable = []
    for model_id in route['models']:
        model = models[model_id]
        provider = providers[model['providerId']]
        registration = registrations.get(model_id)
        if not registration or not registration['ready'] or registration['protocol'] != provider['protocol'] or registration['binding_sha256'] != binding_hash(provider, model):
            unavailable.append(model_id)
            continue
        missing = required - set(registration['capabilities'])
        if missing:
            raise ValueError(f'Runtime {model_id} lacks required model capabilities: {sorted(missing)}')
        return {'kind': 'runtime-configuration-resolution', 'schema_version': '1.0', 'execution_authority': False,
                'stage': stage, 'role': role, 'profile_id': document['profile']['id'], 'model_id': model_id,
                'provider_id': provider['id'], 'protocol': provider['protocol'], 'binding_sha256': binding_hash(provider, model),
                'fallback': bool(unavailable), 'unavailable_before_selection': unavailable,
                'required_model_capabilities': sorted(required)}
    raise ValueError('No independently registered compatible runtime is available for the configured route')
