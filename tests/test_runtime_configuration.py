import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from runtime_configuration import binding_hash, inspect_configuration, resolve_configuration, validate_configuration


class RuntimeConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((ROOT / 'tests/fixtures/runtime-configuration.json').read_text())
        routing = json.loads((ROOT / 'docs/agent/runtime-routing.json').read_text())
        capabilities = sorted({c for r in routing['routes'] for c in r['required_model_capabilities']})
        providers = {p['id']: p for p in self.document['providers']}
        self.inventory = {'schema_version': '1.0', 'registrations': [
            {'model_id': model['id'], 'protocol': providers[model['providerId']]['protocol'],
             'binding_sha256': binding_hash(providers[model['providerId']], model), 'ready': True, 'capabilities': capabilities}
            for model in self.document['profile']['models']]}
        self.request = {'stage': 'green_code', 'role': 'implementer'}

    def resolve(self):
        return resolve_configuration(self.document, self.request, self.inventory, 'operator', 'trusted_platform')

    def test_ui_export_contract_and_inspection_are_non_executing(self):
        self.assertEqual(validate_configuration(self.document), [])
        report = inspect_configuration(self.document)
        self.assertFalse(report['execution_authority'])
        self.assertTrue(all(b['adapter_status'] == 'requires_trusted_registration' for b in report['bindings']))

    def test_primary_and_explicit_fallback_preserve_order(self):
        primary = self.resolve()
        self.assertEqual(primary['model_id'], 'local-coder')
        self.assertFalse(primary['fallback'])
        self.inventory['registrations'][0]['ready'] = False
        fallback = self.resolve()
        self.assertEqual(fallback['model_id'], 'frontier-reviewer')
        self.assertEqual(fallback['unavailable_before_selection'], ['local-coder'])
        self.assertFalse(fallback['execution_authority'])

    def test_local_only_rejects_external_models_including_fallbacks(self):
        self.document['profile']['localOnly'] = True
        self.assertTrue(validate_configuration(self.document))

    def test_secret_authority_and_unknown_fields_are_rejected(self):
        for field in ('secret', 'apiKey', 'approved', 'execution', 'diagnostics', 'stage_order'):
            value = copy.deepcopy(self.document)
            value[field] = 'injected'
            self.assertTrue(validate_configuration(value), field)
        self.document['providers'][1]['auth']['credentialRef'] = 'sk-raw-secret'
        self.assertTrue(validate_configuration(self.document))

    def test_all_governed_roles_and_known_model_references_required(self):
        for mutation in (
            lambda d: d['profile']['routes'].pop(),
            lambda d: d['profile']['routes'][0].update(models=['unknown']),
            lambda d: d['profile']['models'][0].update(providerId='unknown'),
            lambda d: d['providers'].append(copy.deepcopy(d['providers'][0])),
            lambda d: d['profile']['models'][0].update(maxOutputTokens=200, contextWindow=100),
            lambda d: d['profile']['models'][0].update(temperature=float('nan')),
            lambda d: d['profile'].update(name='x' * 121),
        ):
            value = copy.deepcopy(self.document)
            mutation(value)
            self.assertTrue(validate_configuration(value))

    def test_url_and_header_safety_and_explicit_local_http(self):
        provider = self.document['providers'][0]
        provider['baseUrl'] = 'http://192.168.1.20:11434/v1'
        self.assertTrue(validate_configuration(self.document))
        provider['allowInsecureHttp'] = True
        self.assertEqual(validate_configuration(self.document), [])
        for url in ('file:///etc/passwd', 'https://user:secret@example.test/v1', 'https://example.test/v1?key=secret'):
            provider['baseUrl'] = url
            self.assertTrue(validate_configuration(self.document))
        provider['baseUrl'] = 'http://localhost:11434/v1'
        provider['auth']['header'] = 'Host'
        self.assertTrue(validate_configuration(self.document))

    def test_repository_source_and_unregistered_adapters_cannot_resolve(self):
        with self.assertRaises(ValueError):
            resolve_configuration(self.document, self.request, self.inventory, 'repository', 'operator')
        self.inventory['registrations'] = []
        with self.assertRaisesRegex(ValueError, 'No independently registered'):
            self.resolve()

    def test_capability_mismatch_blocks_instead_of_silently_falling_back(self):
        self.inventory['registrations'][0]['capabilities'] = []
        with self.assertRaisesRegex(ValueError, 'lacks required'):
            self.resolve()

    def test_changed_binding_invalidates_runtime_registration(self):
        self.document['profile']['models'][0]['model'] = 'different-model'
        self.assertEqual(self.resolve()['model_id'], 'frontier-reviewer')
        self.document['profile']['models'][1]['maxOutputTokens'] = 123
        with self.assertRaisesRegex(ValueError, 'No independently registered'):
            self.resolve()

    def test_stage_role_mismatch_and_duplicate_registration_rejected(self):
        self.request['stage'] = []
        with self.assertRaises(ValueError):
            self.resolve()
        self.request['stage'] = 'brainstorm'
        with self.assertRaises(ValueError):
            self.resolve()
        self.request['stage'] = 'green_code'
        self.inventory['registrations'].append(self.inventory['registrations'][0])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.resolve()

    def test_cli_report_is_create_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'inspection.json'
            command = [sys.executable, str(ROOT / 'scripts/validate-runtime-configuration.py'),
                       str(ROOT / 'tests/fixtures/runtime-configuration.json'), '--output', str(output)]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            before = output.read_bytes()
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
            self.assertEqual(output.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
