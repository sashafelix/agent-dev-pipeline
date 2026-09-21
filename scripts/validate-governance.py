#!/usr/bin/env python3
"""Validate local RGR v1.3 governance contracts and cross-file invariants."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from schema_validation import validate_instance

ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = ROOT / "docs" / "agent"
SCHEMA_DIR = AGENT_DIR / "schemas"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def validate_document(path: Path, schema_name: str) -> tuple[Any, list[str]]:
    document = load_json(path)
    schema = load_json(SCHEMA_DIR / schema_name)
    return document, [f"{path}: {error}" for error in validate_instance(document, schema)]


def validate_profiles(profiles_doc: dict[str, Any], role_ids: set[str]) -> list[str]:
    errors: list[str] = []
    mandatory = profiles_doc["mandatory_stage_order"]
    profiles = profiles_doc["profiles"]
    ids = [profile["id"] for profile in profiles]
    ranks = [profile["rank"] for profile in profiles]
    if len(ids) != len(set(ids)):
        errors.append("workflow-profiles.json: profile ids must be unique")
    if set(ids) != {"small", "standard", "high-risk"}:
        errors.append("workflow-profiles.json: must define small, standard and high-risk")
    if sorted(ranks) != [1, 2, 3]:
        errors.append("workflow-profiles.json: ranks must be exactly 1, 2 and 3")

    ordered = sorted(profiles, key=lambda item: item["rank"])
    budget_fields = ["max_context_files", "max_context_bytes", "max_tokens", "max_convergence_attempts"]
    previous: dict[str, int] | None = None
    for profile in ordered:
        if profile["required_stages"] != mandatory:
            errors.append(f"workflow profile {profile['id']}: required_stages must equal mandatory stage order")
        referenced_roles = set(profile["specialist_roles"]) | set(profile["conditional_specialists"].values())
        unknown = referenced_roles - role_ids
        if unknown:
            errors.append(f"workflow profile {profile['id']}: unknown specialist roles {sorted(unknown)}")
        if previous is not None:
            for field in budget_fields:
                if profile["budgets"][field] < previous[field]:
                    errors.append(f"workflow profile {profile['id']}: {field} cannot be lower than less strict profile")
        previous = profile["budgets"]
    high = next(profile for profile in profiles if profile["id"] == "high-risk")
    if not high["specialist_roles"]:
        errors.append("high-risk profile must require at least one specialist role")
    if "before green_code" not in high["manual_checkpoints"] or "before close" not in high["manual_checkpoints"]:
        errors.append("high-risk profile must checkpoint before GREEN and before close")
    return errors


def validate_roles(roles_doc: dict[str, Any]) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    roles = roles_doc["roles"]
    ids = [role["id"] for role in roles]
    role_ids = set(ids)
    if len(ids) != len(role_ids):
        errors.append("role-contracts.json: role ids must be unique")
    required = {"orchestrator", "repository_analyst", "specifier", "consistency_analyst", "test_author", "implementer", "refactorer", "independent_verifier", "convergence_reviewer"}
    missing = required - role_ids
    if missing:
        errors.append(f"role-contracts.json: missing core roles {sorted(missing)}")

    allowed_source_writers = {"implementer", "refactorer"}
    for role in roles:
        role_id = role["id"]
        capabilities = set(role["capabilities"])
        unknown_delegates = set(role["may_delegate_to"]) - role_ids
        if unknown_delegates:
            errors.append(f"role {role_id}: unknown delegation targets {sorted(unknown_delegates)}")
        if "source_write" in capabilities and role_id not in allowed_source_writers:
            errors.append(f"role {role_id}: source_write is restricted to implementer/refactorer")
        if "migration_write" in capabilities and role_id != "implementer":
            errors.append(f"role {role_id}: migration_write is restricted to implementer")
        if "verdict_issue" in capabilities and role_id in {"test_author", "implementer", "refactorer", "repository_analyst", "specifier"}:
            errors.append(f"role {role_id}: execution roles cannot issue verdicts")
        if "learning_curate" in capabilities and role_id != "independent_verifier":
            errors.append(f"role {role_id}: only independent_verifier may curate learnings")

    verifier = next((role for role in roles if role["id"] == "independent_verifier"), None)
    if verifier:
        write_capabilities = {"source_write", "test_write", "config_write", "migration_write"}
        if set(verifier["capabilities"]) & write_capabilities:
            errors.append("independent_verifier must not have story write capabilities")
        if "verdict_issue" not in verifier["capabilities"]:
            errors.append("independent_verifier must have verdict_issue")
    return role_ids, errors


def validate_learnings(learnings_doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if learnings_doc.get("authority") != "advisory":
        errors.append("learnings.json: learnings must remain advisory and cannot become canonical evidence")
    entries = learnings_doc["entries"]
    ids = [entry["id"] for entry in entries]
    id_set = set(ids)
    if len(ids) != len(id_set):
        errors.append("learnings.json: learning ids must be unique")

    active_by_key: dict[str, str] = {}
    for entry in entries:
        if entry["status"] == "active":
            if not entry["reviewed_by"]:
                errors.append(f"learning {entry['id']}: active entry requires reviewed_by")
            previous_claim = active_by_key.get(entry["conflict_key"])
            if previous_claim is not None and previous_claim != entry["claim"]:
                errors.append(f"learning {entry['id']}: conflicting active claim for {entry['conflict_key']}")
            active_by_key[entry["conflict_key"]] = entry["claim"]
        if entry["status"] == "candidate" and entry["reviewed_by"] is not None:
            errors.append(f"learning {entry['id']}: candidate must not pretend to be reviewed")
        supersedes = entry["supersedes"]
        if supersedes is not None and supersedes not in id_set:
            errors.append(f"learning {entry['id']}: supersedes unknown entry {supersedes}")
        if entry["id"] in entry["evidence_refs"]:
            errors.append(f"learning {entry['id']}: evidence cannot self-reference the learning id")
    return errors


def main() -> int:
    try:
        profiles_doc, profile_schema_errors = validate_document(AGENT_DIR / "workflow-profiles.json", "workflow-profiles.schema.json")
        roles_doc, role_schema_errors = validate_document(AGENT_DIR / "role-contracts.json", "role-contracts.schema.json")
        learnings_doc, learning_schema_errors = validate_document(AGENT_DIR / "learnings.json", "learnings-registry.schema.json")
        corpus_doc = load_json(AGENT_DIR / "evaluation-corpus.json")

        errors = profile_schema_errors + role_schema_errors + learning_schema_errors
        role_ids, role_errors = validate_roles(roles_doc)
        errors.extend(role_errors)
        errors.extend(validate_profiles(profiles_doc, role_ids))
        errors.extend(validate_learnings(learnings_doc))

        profile_ids = {profile["id"] for profile in profiles_doc["profiles"]}
        for fixture in corpus_doc.get("fixtures", []):
            if fixture.get("profile") not in profile_ids:
                errors.append(f"evaluation fixture {fixture.get('id')}: unknown profile {fixture.get('profile')}")

        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"PASS: governance contracts valid ({len(profile_ids)} profiles, {len(role_ids)} roles, {len(learnings_doc['entries'])} learnings)")
        return 0
    except (ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
