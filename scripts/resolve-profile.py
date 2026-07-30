#!/usr/bin/env python3
"""Resolve a local RGR workflow profile from immutable task facts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from schema_validation import validate_instance

ROOT = Path(__file__).resolve().parents[1]
PROFILES_PATH = ROOT / "docs" / "agent" / "workflow-profiles.json"
SCHEMA_PATH = ROOT / "docs" / "agent" / "schemas" / "profile-resolution.schema.json"
PROFILE_RANK = {"small": 1, "standard": 2, "high-risk": 3}
HIGH_RISK_TAGS = {"security", "domain:auth", "pii", "migration", "domain:db", "infra", "breaking-contract"}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def require_facts(raw: Any) -> tuple[str, dict[str, Any]]:
    if not isinstance(raw, dict):
        raise ValueError("task facts root must be an object")
    story_id = raw.get("story_id")
    facts = raw.get("facts")
    if not isinstance(story_id, str) or not story_id:
        raise ValueError("story_id must be a non-empty string")
    if not isinstance(facts, dict):
        raise ValueError("facts must be an object")
    defaults = {
        "risk_tags": [],
        "blast_radius": "low",
        "uncertainty": "low",
        "changed_module_count": 1,
        "cross_service": False,
        "contract_change": False,
        "data_migration": False,
        "security_sensitive": False,
        "infrastructure_change": False,
    }
    unknown = sorted(set(facts) - set(defaults))
    if unknown:
        raise ValueError(f"unknown task fact fields: {unknown}")
    merged = {**defaults, **facts}
    if merged["blast_radius"] not in {"low", "medium", "high"}:
        raise ValueError("blast_radius must be low, medium or high")
    if merged["uncertainty"] not in {"low", "medium", "high"}:
        raise ValueError("uncertainty must be low, medium or high")
    if not isinstance(merged["changed_module_count"], int) or merged["changed_module_count"] < 0:
        raise ValueError("changed_module_count must be a non-negative integer")
    if not isinstance(merged["risk_tags"], list) or not all(isinstance(tag, str) and tag for tag in merged["risk_tags"]):
        raise ValueError("risk_tags must be non-empty strings")
    for field in ["cross_service", "contract_change", "data_migration", "security_sensitive", "infrastructure_change"]:
        if not isinstance(merged[field], bool):
            raise ValueError(f"{field} must be boolean")
    merged["risk_tags"] = sorted(set(merged["risk_tags"]))
    return story_id, merged


def classify(facts: dict[str, Any]) -> tuple[str, list[str], list[str]]:
    rules: list[str] = []
    reasons: list[str] = []
    tags = set(facts["risk_tags"])

    high_conditions = [
        (facts["security_sensitive"], "RISK-SECURITY", "security-sensitive change"),
        (facts["data_migration"], "RISK-MIGRATION", "data migration"),
        (facts["infrastructure_change"], "RISK-INFRASTRUCTURE", "infrastructure change"),
        (facts["blast_radius"] == "high", "RISK-BLAST-HIGH", "high blast radius"),
        (facts["uncertainty"] == "high", "RISK-UNCERTAINTY-HIGH", "high unresolved uncertainty"),
        (bool(tags & HIGH_RISK_TAGS), "RISK-TAG-HIGH", f"high-risk tags: {sorted(tags & HIGH_RISK_TAGS)}"),
    ]
    for active, rule, reason in high_conditions:
        if active:
            rules.append(rule)
            reasons.append(reason)
    if rules:
        return "high-risk", rules, reasons

    standard_conditions = [
        (facts["cross_service"], "SCOPE-CROSS-SERVICE", "cross-service scope"),
        (facts["contract_change"], "SCOPE-CONTRACT", "contract or compatibility change"),
        (facts["changed_module_count"] > 1, "SCOPE-MULTI-MODULE", f"{facts['changed_module_count']} changed modules"),
        (facts["blast_radius"] == "medium", "RISK-BLAST-MEDIUM", "medium blast radius"),
        (facts["uncertainty"] == "medium", "RISK-UNCERTAINTY-MEDIUM", "medium uncertainty"),
    ]
    for active, rule, reason in standard_conditions:
        if active:
            rules.append(rule)
            reasons.append(reason)
    if rules:
        return "standard", rules, reasons
    return "small", ["DEFAULT-BOUNDED"], ["bounded low-risk single-module change"]


def resolve_specialists(profile: dict[str, Any], facts: dict[str, Any]) -> list[str]:
    tags = set(facts["risk_tags"])
    if facts["security_sensitive"]:
        tags.add("security")
    if facts["data_migration"]:
        tags.add("migration")
    if facts["infrastructure_change"]:
        tags.add("infra")
    if facts["contract_change"]:
        tags.add("breaking-contract")
    roles = set(profile.get("specialist_roles", []))
    conditional = profile.get("conditional_specialists", {})
    for tag in tags:
        role = conditional.get(tag)
        if isinstance(role, str):
            roles.add(role)
    return sorted(roles)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("facts_file", type=Path)
    parser.add_argument("--minimum-profile", choices=sorted(PROFILE_RANK, key=PROFILE_RANK.get))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        story_id, facts = require_facts(load_json(args.facts_file))
        profiles_doc = load_json(PROFILES_PATH)
        profiles = {item["id"]: item for item in profiles_doc["profiles"]}
        selected, rule_ids, reasons = classify(facts)
        overridden = False
        override_reason: str | None = None
        if args.minimum_profile and PROFILE_RANK[args.minimum_profile] > PROFILE_RANK[selected]:
            selected = args.minimum_profile
            overridden = True
            override_reason = f"operator minimum profile raised classification to {selected}"
            rule_ids.append("OPERATOR-MINIMUM")
            reasons.append(override_reason)
        profile = profiles[selected]
        resolution = {
            "schema_version": "1.0",
            "story_id": story_id,
            "selected_profile": selected,
            "facts": facts,
            "rule_ids": rule_ids,
            "reasons": reasons,
            "specialist_roles": resolve_specialists(profile, facts),
            "manual_checkpoints": profile["manual_checkpoints"],
            "overridden": overridden,
            "override_reason": override_reason,
        }
        schema = load_json(SCHEMA_PATH)
        errors = validate_instance(resolution, schema)
        if errors:
            raise ValueError("; ".join(errors))
        payload = json.dumps(resolution, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)
        return 0
    except (ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
