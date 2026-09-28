#!/usr/bin/env python3
"""Validate an operator/platform supplied project profile before it enters a run."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from schema_validation import validate_instance

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "docs" / "agent" / "schemas" / "project-profile.schema.json"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def validate(path: Path, expected_project_id: str | None = None) -> list[str]:
    document = load_json(path)
    schema = load_json(SCHEMA)
    errors = [f"{path}: {error}" for error in validate_instance(document, schema)]
    if not isinstance(document, dict):
        return errors or [f"{path}: root must be an object"]

    provenance = document.get("provenance", {})
    if provenance.get("source") not in {"operator", "trusted_platform"}:
        errors.append(f"{path}: provenance.source must be operator or trusted_platform")
    if expected_project_id and document.get("project_id") != expected_project_id:
        errors.append(f"{path}: project_id must be {expected_project_id!r}")

    forbidden = {
        "stage_order", "workflow_profile", "risk_profile", "role", "roles",
        "capability", "capabilities", "runtime", "model", "checkpoint",
        "approval", "permission", "permissions", "merge", "deploy"
    }
    decisions = document.get("decisions", {})
    if isinstance(decisions, dict):
        for key in decisions:
            if key.lower().replace("-", "_") in forbidden:
                errors.append(f"{path}: decision key {key!r} attempts to express protocol authority")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    parser.add_argument("--expected-project-id")
    args = parser.parse_args()
    try:
        errors = validate(args.profile.resolve(), args.expected_project_id)
    except (ValueError, TypeError) as exc:
        errors = [str(exc)]
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {args.profile} is a trusted project-facts profile")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
