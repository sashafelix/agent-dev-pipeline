#!/usr/bin/env python3
"""Resolve safe deterministic GREEN implementation lanes from a locked detailed plan."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from schema_validation import validate_instance

ROOT = Path(__file__).resolve().parents[1]
PLAN_SCHEMA = ROOT / "docs" / "agent" / "schemas" / "detailed-plan.schema.json"
OUT_SCHEMA = ROOT / "docs" / "agent" / "schemas" / "lane-resolution.schema.json"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def normalize_surface(value: str) -> str:
    if not value or value.startswith("/") or any(ch in value for ch in "*?[]"):
        raise ValueError(f"write surface must be a literal relative path prefix: {value!r}")
    path = PurePosixPath(value)
    if ".." in path.parts or "." in path.parts:
        raise ValueError(f"write surface must not contain dot traversal: {value!r}")
    normalized = path.as_posix().rstrip("/")
    if not normalized:
        raise ValueError("write surface cannot resolve to repository root")
    return normalized


def within(surface: str, path: str) -> bool:
    candidate = PurePosixPath(path).as_posix().rstrip("/")
    return candidate == surface or candidate.startswith(surface + "/")


def overlap(left: str, right: str) -> bool:
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def resolve(plan: dict[str, Any]) -> dict[str, Any]:
    story_id = plan["story_id"]
    tasks = {task["id"]: task for task in plan.get("tasks", [])}
    green_ids = sorted(task_id for task_id, task in tasks.items() if task.get("stage") == "green_code")
    declared = plan.get("implementation_lanes", [])

    if not declared:
        lanes = []
        waves = []
        if green_ids:
            lanes = [{
                "id": "LANE-default",
                "kind": "generic",
                "task_ids": green_ids,
                "write_surfaces": [],
                "depends_on_lanes": [],
            }]
            waves = [{"wave": 1, "lane_ids": ["LANE-default"]}]
        return {
            "schema_version": "1.0",
            "story_id": story_id,
            "mode": "sequential",
            "reason": "plan declares no implementation lanes; preserve deterministic sequential GREEN execution",
            "lanes": lanes,
            "waves": waves,
            "overlap_checks": [],
        }

    lane_by_id: dict[str, dict[str, Any]] = {}
    task_to_lane: dict[str, str] = {}
    for raw in declared:
        lane_id = raw["id"]
        if lane_id in lane_by_id:
            raise ValueError(f"duplicate implementation lane {lane_id}")
        surfaces = [normalize_surface(value) for value in raw["write_surfaces"]]
        lane = {
            "id": lane_id,
            "kind": raw["kind"],
            "task_ids": sorted(raw["task_ids"]),
            "write_surfaces": sorted(set(surfaces)),
            "depends_on_lanes": sorted(set(raw.get("depends_on_lanes", []))),
        }
        lane_by_id[lane_id] = lane
        for task_id in lane["task_ids"]:
            task = tasks.get(task_id)
            if task is None:
                raise ValueError(f"{lane_id} references unknown task {task_id}")
            if task.get("stage") != "green_code":
                raise ValueError(f"{lane_id} may contain GREEN tasks only; {task_id} is {task.get('stage')}")
            if task_id in task_to_lane:
                raise ValueError(f"GREEN task {task_id} is assigned to multiple lanes")
            task_to_lane[task_id] = lane_id
            for output in task.get("outputs", []):
                if not any(within(surface, output) for surface in lane["write_surfaces"]):
                    raise ValueError(
                        f"{lane_id} output {output!r} is outside declared write surfaces {lane['write_surfaces']}"
                    )

    missing = sorted(set(green_ids) - set(task_to_lane))
    extra = sorted(set(task_to_lane) - set(green_ids))
    if missing:
        raise ValueError(f"GREEN tasks missing lane assignment: {missing}")
    if extra:
        raise ValueError(f"non-GREEN tasks assigned to lanes: {extra}")

    for task_id, lane_id in task_to_lane.items():
        lane = lane_by_id[lane_id]
        deps = set(lane["depends_on_lanes"])
        for dep_task in tasks[task_id].get("depends_on", []):
            dep_lane = task_to_lane.get(dep_task)
            if dep_lane and dep_lane != lane_id:
                deps.add(dep_lane)
        if lane_id in deps:
            raise ValueError(f"{lane_id} cannot depend on itself")
        unknown = deps - set(lane_by_id)
        if unknown:
            raise ValueError(f"{lane_id} depends on unknown lanes {sorted(unknown)}")
        lane["depends_on_lanes"] = sorted(deps)

    remaining = set(lane_by_id)
    completed: set[str] = set()
    candidate_waves: list[list[str]] = []
    while remaining:
        ready = sorted(
            lane_id for lane_id in remaining
            if set(lane_by_id[lane_id]["depends_on_lanes"]).issubset(completed)
        )
        if not ready:
            raise ValueError(f"implementation lane dependency cycle: {sorted(remaining)}")
        candidate_waves.append(ready)
        completed.update(ready)
        remaining.difference_update(ready)

    checks: list[dict[str, Any]] = []
    conflicts: list[str] = []
    for wave in candidate_waves:
        for index, left_id in enumerate(wave):
            for right_id in wave[index + 1:]:
                overlaps = sorted({
                    f"{left} <-> {right}"
                    for left in lane_by_id[left_id]["write_surfaces"]
                    for right in lane_by_id[right_id]["write_surfaces"]
                    if overlap(left, right)
                })
                conflict = bool(overlaps)
                checks.append({
                    "left_lane": left_id,
                    "right_lane": right_id,
                    "conflict": conflict,
                    "overlap_surfaces": overlaps,
                })
                if conflict:
                    conflicts.append(f"{left_id}/{right_id}: {', '.join(overlaps)}")

    if conflicts:
        flattened = [lane_id for wave in candidate_waves for lane_id in wave]
        waves = [{"wave": i + 1, "lane_ids": [lane_id]} for i, lane_id in enumerate(flattened)]
        mode = "sequential"
        reason = "parallelism disabled because same-wave write surfaces overlap: " + "; ".join(conflicts)
    else:
        waves = [{"wave": i + 1, "lane_ids": wave} for i, wave in enumerate(candidate_waves)]
        mode = "parallel" if any(len(wave) > 1 for wave in candidate_waves) else "sequential"
        reason = (
            "at least one dependency wave has disjoint write surfaces and may execute concurrently"
            if mode == "parallel"
            else "lane dependencies permit only one implementation lane at a time"
        )

    result = {
        "schema_version": "1.0",
        "story_id": story_id,
        "mode": mode,
        "reason": reason,
        "lanes": [lane_by_id[key] for key in sorted(lane_by_id)],
        "waves": waves,
        "overlap_checks": checks,
    }
    errors = validate_instance(result, load_json(OUT_SCHEMA))
    if errors:
        raise ValueError("lane resolution output invalid: " + "; ".join(errors))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        plan = load_json(args.plan.resolve())
        plan_errors = validate_instance(plan, load_json(PLAN_SCHEMA))
        if plan_errors:
            raise ValueError("detailed plan invalid: " + "; ".join(plan_errors))
        result = resolve(plan)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"PASS: {result['mode']} GREEN lane plan -> {args.output}")
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
