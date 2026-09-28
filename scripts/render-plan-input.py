#!/usr/bin/env python3
"""Render deterministic plan-input.md from a READY structured intake artifact."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from schema_validation import validate_instance

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "docs" / "agent" / "schemas" / "intake.schema.json"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def render(document: dict[str, Any]) -> str:
    if document.get("status") != "ready":
        raise ValueError("intake status must be 'ready' before plan input can be rendered")
    blockers = [
        q.get("id") for q in document.get("questions", [])
        if isinstance(q, dict) and q.get("blocking") is True and q.get("answered") is not True
    ]
    if blockers:
        raise ValueError(f"intake still has unanswered blocking questions: {blockers}")
    task = document.get("task_spec")
    if not isinstance(task, dict):
        raise ValueError("ready intake requires task_spec")

    lines = [
        "# Plan Input",
        "",
        f"intake_id: {document['intake_id']}",
        "source: structured-intake",
        f"project_profile_ref: {document.get('project_profile_ref') or 'none'}",
        "",
        "## Title",
        task["title"],
        "",
        "## Description",
        task["description"],
        "",
        "## Requirements",
    ]
    lines.extend(f"- {item}" for item in task.get("requirements", []))
    lines.extend(["", "## Constraints"])
    lines.extend(f"- {item}" for item in task.get("constraints", []))
    lines.extend(["", "## Acceptance Criteria"])
    lines.extend(f"- {item}" for item in task.get("acceptance_criteria", []))
    lines.extend(["", "## Confirmed User Decisions"])
    decisions = task.get("user_decisions", {})
    if decisions:
        lines.extend(f"- {key}: {decisions[key]}" for key in sorted(decisions))
    else:
        lines.append("- none")
    lines.extend(["", "## Resolved Intake Facts"])
    for item in document.get("resolved", []):
        lines.append(
            f"- {item['field']}: {item['value']} "
            f"[source={item['source']}; authority={item['authority']}; confidence={item['confidence']}]"
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intake", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        document = load_json(args.intake.resolve())
        errors = validate_instance(document, load_json(SCHEMA))
        if errors:
            raise ValueError("; ".join(errors))
        output = render(document)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        print(f"PASS: rendered {args.output} from READY intake {document['intake_id']}")
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
