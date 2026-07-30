#!/usr/bin/env python3
"""Validate and compare local RGR evaluation results using only stdlib."""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

from schema_validation import validate_instance

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "docs" / "agent" / "schemas"
DEFAULT_CORPUS = ROOT / "docs" / "agent" / "evaluation-corpus.json"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def validate_with_schema(instance: Any, schema_name: str, label: str) -> list[str]:
    schema = load_json(SCHEMA_DIR / schema_name)
    return [f"{label}: {error}" for error in validate_instance(instance, schema)]


def fixture_map(corpus: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    fixtures: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for fixture in corpus.get("fixtures", []):
        fixture_id = fixture.get("id")
        if fixture_id in fixtures:
            errors.append(f"duplicate fixture id: {fixture_id}")
        elif isinstance(fixture_id, str):
            fixtures[fixture_id] = fixture
    return fixtures, errors


def load_results(directory: Path, fixtures: dict[str, dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    results: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for fixture_id in sorted(fixtures):
        path = directory / f"{fixture_id}.json"
        if not path.is_file():
            errors.append(f"missing evaluation result: {path}")
            continue
        result = load_json(path)
        errors.extend(validate_with_schema(result, "evaluation-result.schema.json", str(path)))
        if result.get("fixture_id") != fixture_id:
            errors.append(f"{path}: fixture_id must be {fixture_id!r}")
        results[fixture_id] = result
    extra = sorted(path.name for path in directory.glob("*.json") if path.stem not in fixtures)
    for name in extra:
        errors.append(f"unexpected evaluation result: {directory / name}")
    return results, errors


def check_behaviours(fixture: dict[str, Any], result: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    fixture_id = fixture["id"]
    checks = result.get("behaviour_checks", {})
    for behaviour in fixture["required_behaviours"]:
        if checks.get(behaviour) is not True:
            errors.append(f"{fixture_id}: required behaviour not demonstrated: {behaviour}")
    for behaviour in fixture["forbidden_behaviours"]:
        if checks.get(behaviour) is not False:
            errors.append(f"{fixture_id}: forbidden behaviour was not explicitly rejected: {behaviour}")
    if result.get("outcome") != fixture.get("expected_outcome"):
        errors.append(
            f"{fixture_id}: expected outcome {fixture.get('expected_outcome')}, got {result.get('outcome')}"
        )
    return errors


def aggregate(results: dict[str, dict[str, Any]]) -> dict[str, float]:
    metric_names = [
        "success_criterion_coverage",
        "evidence_completeness",
        "unnecessary_changed_files",
        "convergence_attempts",
        "reviewer_corrections",
        "elapsed_seconds",
        "estimated_tokens",
    ]
    summary: dict[str, float] = {}
    for name in metric_names:
        values = [float(result["metrics"][name]) for result in results.values()]
        summary[f"mean_{name}"] = statistics.fmean(values) if values else 0.0
    return summary


def compare_baseline(current: dict[str, dict[str, Any]], baseline: dict[str, dict[str, Any]]) -> list[str]:
    regressions: list[str] = []
    lower_is_bad = ["success_criterion_coverage", "evidence_completeness"]
    higher_is_bad = ["unnecessary_changed_files", "convergence_attempts", "reviewer_corrections"]
    for fixture_id, result in current.items():
        previous = baseline.get(fixture_id)
        if previous is None:
            continue
        for metric in lower_is_bad:
            if float(result["metrics"][metric]) + 1e-9 < float(previous["metrics"][metric]):
                regressions.append(
                    f"{fixture_id}: {metric} regressed from {previous['metrics'][metric]} to {result['metrics'][metric]}"
                )
        for metric in higher_is_bad:
            if float(result["metrics"][metric]) > float(previous["metrics"][metric]):
                regressions.append(
                    f"{fixture_id}: {metric} regressed from {previous['metrics'][metric]} to {result['metrics'][metric]}"
                )
    return regressions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", nargs="?", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--results-dir", type=Path)
    parser.add_argument("--baseline-dir", type=Path)
    parser.add_argument("--output", type=Path, default=Path("evaluation-report.json"))
    parser.add_argument("--fail-on-regression", action="store_true")
    args = parser.parse_args()

    corpus = load_json(args.corpus)
    errors = validate_with_schema(corpus, "evaluation-corpus.schema.json", str(args.corpus))
    fixtures, fixture_errors = fixture_map(corpus)
    errors.extend(fixture_errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if args.results_dir is None:
        profiles: dict[str, int] = {}
        for fixture in fixtures.values():
            profiles[fixture["profile"]] = profiles.get(fixture["profile"], 0) + 1
        print(f"PASS: {args.corpus} contains {len(fixtures)} valid fixtures {profiles}")
        return 0

    current, result_errors = load_results(args.results_dir, fixtures)
    errors.extend(result_errors)
    for fixture_id, result in current.items():
        errors.extend(check_behaviours(fixtures[fixture_id], result))

    regressions: list[str] = []
    if args.baseline_dir is not None:
        baseline, baseline_errors = load_results(args.baseline_dir, fixtures)
        errors.extend(f"baseline: {error}" for error in baseline_errors)
        regressions = compare_baseline(current, baseline)

    pipeline_versions = sorted({result.get("pipeline_version") for result in current.values()})
    if len(pipeline_versions) > 1:
        errors.append(f"results contain multiple pipeline versions: {pipeline_versions}")

    report = {
        "schema_version": "1.0",
        "corpus_contract_version": corpus["pipeline_contract_version"],
        "pipeline_version": pipeline_versions[0] if len(pipeline_versions) == 1 else None,
        "fixture_count": len(fixtures),
        "result_count": len(current),
        "aggregate_metrics": aggregate(current),
        "contract_failures": errors,
        "baseline_regressions": regressions,
        "fixtures": [
            {
                "fixture_id": fixture_id,
                "expected_outcome": fixtures[fixture_id]["expected_outcome"],
                "actual_outcome": current.get(fixture_id, {}).get("outcome"),
                "metrics": current.get(fixture_id, {}).get("metrics"),
            }
            for fixture_id in sorted(fixtures)
        ],
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    for regression in regressions:
        print(f"REGRESSION: {regression}", file=sys.stderr)

    if errors or (args.fail_on_regression and regressions):
        return 1
    print(f"PASS: wrote evaluation report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
