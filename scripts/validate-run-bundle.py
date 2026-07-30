#!/usr/bin/env python3
"""Validate the local RGR run-bundle invariants using only the Python standard library."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

STAGES = ["prepare", "brainstorm", "plan", "analyze", "red_test", "green_code", "refactor", "quality_gate", "converge"]
REQUIRED_FILES = [
    "run-context.md", "plan-input.md", "repository-intelligence.json",
    "brainstorm.md", "brainstorm.json", "detailed-plan.md", "detailed-plan.json",
    "analysis-report.json", "handoff.md", "quality-gates.md", "quality-gates.json",
    "convergence-report.json", "decision-log.md", "events.jsonl",
]


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def require_keys(path: Path, obj: Any, keys: set[str]) -> list[str]:
    if not isinstance(obj, dict):
        return [f"{path}: root must be an object"]
    return [f"{path}: missing key '{key}'" for key in sorted(keys - obj.keys())]


def validate_events(path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    events: list[dict[str, Any]] = []
    previous = 0
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_no}: invalid JSON: {exc}")
            continue
        if not isinstance(event, dict):
            errors.append(f"{path}:{line_no}: event must be an object")
            continue
        missing = {"sequence", "story_id", "attempt", "stage", "event_type", "actor_role", "artifact_refs"} - event.keys()
        if missing:
            errors.append(f"{path}:{line_no}: missing keys {sorted(missing)}")
            continue
        sequence = event["sequence"]
        if not isinstance(sequence, int) or sequence != previous + 1:
            errors.append(f"{path}:{line_no}: sequence must be contiguous; expected {previous + 1}, got {sequence!r}")
        previous = sequence if isinstance(sequence, int) else previous
        events.append(event)
    return errors, events


def validate(run_dir: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_FILES:
        if not (run_dir / name).is_file():
            errors.append(f"missing required artifact: {name}")
    if errors:
        return errors

    repository = load_json(run_dir / "repository-intelligence.json")
    errors += require_keys(run_dir / "repository-intelligence.json", repository, {"schema_version", "story_id", "revision", "project_root", "stack", "commands", "modules", "impact", "inspection"})
    brainstorm = load_json(run_dir / "brainstorm.json")
    errors += require_keys(run_dir / "brainstorm.json", brainstorm, {"schema_version", "story_id", "success_criteria", "input_trace", "uncertainties"})
    plan = load_json(run_dir / "detailed-plan.json")
    errors += require_keys(run_dir / "detailed-plan.json", plan, {"schema_version", "story_id", "status", "tasks", "criterion_test_map"})
    analysis = load_json(run_dir / "analysis-report.json")
    errors += require_keys(run_dir / "analysis-report.json", analysis, {"schema_version", "story_id", "hard_findings", "warnings", "artifact_refs"})
    gates = load_json(run_dir / "quality-gates.json")
    errors += require_keys(run_dir / "quality-gates.json", gates, {"schema_version", "story_id", "verdict", "criterion_evidence", "hard_failures", "reviewer_role"})
    convergence = load_json(run_dir / "convergence-report.json")
    errors += require_keys(run_dir / "convergence-report.json", convergence, {"schema_version", "story_id", "attempt", "outcome", "blocking_gaps", "artifact_refs"})

    sc_ids = {item.get("id") for item in brainstorm.get("success_criteria", []) if isinstance(item, dict)}
    planned_ids = {item.get("sc_id") for item in plan.get("criterion_test_map", []) if isinstance(item, dict)}
    evidence_ids = {item.get("sc_id") for item in gates.get("criterion_evidence", []) if isinstance(item, dict)}
    if None in sc_ids or not sc_ids:
        errors.append("brainstorm.json: success_criteria must contain non-empty ids")
    for label, ids in (("detailed-plan.json criterion_test_map", planned_ids), ("quality-gates.json criterion_evidence", evidence_ids)):
        missing = sc_ids - ids
        if missing:
            errors.append(f"{label}: missing success criteria {sorted(missing)}")

    if analysis.get("hard_findings"):
        errors.append("analysis-report.json: hard_findings must be empty before RED")
    if gates.get("reviewer_role") != "independent_verifier":
        errors.append("quality-gates.json: reviewer_role must be independent_verifier")
    if gates.get("verdict") == "PASS" and gates.get("hard_failures"):
        errors.append("quality-gates.json: PASS cannot contain hard_failures")
    if convergence.get("outcome") == "CONVERGED" and convergence.get("blocking_gaps"):
        errors.append("convergence-report.json: CONVERGED cannot contain blocking_gaps")
    attempt = convergence.get("attempt")
    if not isinstance(attempt, int) or attempt < 1 or attempt > 2:
        errors.append("convergence-report.json: attempt must be 1 or 2")

    event_errors, events = validate_events(run_dir / "events.jsonl")
    errors += event_errors
    completed = [event.get("stage") for event in events if event.get("event_type") == "stage.completed"]
    cursor = 0
    for stage in completed:
        if cursor < len(STAGES) and stage == STAGES[cursor]:
            cursor += 1
    if cursor < len(STAGES):
        errors.append(f"events.jsonl: completed stages do not contain required order; next expected '{STAGES[cursor]}'")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    errors = validate(args.run_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {args.run_dir} satisfies local RGR v1.1 bundle invariants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
