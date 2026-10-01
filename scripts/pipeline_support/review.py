"""Deterministic planning checks; semantic questions remain human/agent review."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

from .common import finding, read_bytes, read_json, relative_path, report, sha256


def load_plan(run: Path) -> tuple[dict, dict, dict[str, str]]:
    documents = {}
    hashes = {}
    for name in ("brainstorm", "detailed-plan"):
        filename = name + ".json"
        documents[name] = read_json(run, filename, name + ".schema.json")
        hashes[filename] = sha256(read_bytes(run, filename))
    return documents["brainstorm"], documents["detailed-plan"], hashes


def check_plan(brainstorm: dict, plan: dict) -> list[dict]:
    findings = []
    refs = ["brainstorm.json", "detailed-plan.json"]
    add = lambda code, message: findings.append(finding(code, message, refs))
    if brainstorm["story_id"] != plan["story_id"]:
        add("story_mismatch", "Specification and plan identify different stories.")
    criteria = [item["id"] for item in brainstorm["success_criteria"]]
    task_ids = [task["id"] for task in plan["tasks"]]
    mapped = [item["sc_id"] for item in plan["criterion_test_map"]]
    for label, values in (("criterion", criteria), ("task", task_ids), ("test_map", mapped)):
        duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
        if duplicates:
            add("duplicate_" + label, f"Duplicate {label} IDs: {', '.join(duplicates)}")
    if set(mapped) != set(criteria):
        add("test_coverage", "Test map must cover exactly the locked criteria; missing: " +
            str(sorted(set(criteria) - set(mapped))) + "; unknown: " + str(sorted(set(mapped) - set(criteria))))
    covered = set()
    remaining = {}
    for task in plan["tasks"]:
        covered.update(task["criteria"])
        if not task["criteria"] or set(task["criteria"]) - set(criteria):
            add("task_criteria", f"{task['id']} must reference known success criteria.")
        if set(task["depends_on"]) - set(task_ids):
            add("unknown_dependency", f"{task['id']} references an unknown dependency.")
        remaining[task["id"]] = set(task["depends_on"])
        for output in task["outputs"]:
            if not relative_path(output):
                add("unsafe_output", f"{task['id']} output is not a literal relative path: {output!r}")
    if set(criteria) - covered:
        add("task_coverage", f"Criteria without tasks: {sorted(set(criteria) - covered)}")
    # Kahn's algorithm avoids recursive traversal of a repository-supplied graph.
    while remaining:
        ready = {key for key, dependencies in remaining.items() if not dependencies}
        if not ready:
            add("dependency_graph", "Task dependencies contain a cycle or unresolved reference.")
            break
        remaining = {key: dependencies - ready for key, dependencies in remaining.items() if key not in ready}
    for item in brainstorm["uncertainties"]:
        if item["status"] == "blocking":
            add("unresolved_uncertainty", f"{item['id']}: {item['description']}")
    return findings


def review_plan(run: Path) -> dict:
    brainstorm, plan, hashes = load_plan(run)
    findings = check_plan(brainstorm, plan)
    questions = []
    for item in brainstorm["success_criteria"]:
        if re.search(r"\b(fast|easy|seamless|robust|user.friendly|appropriate|as needed)\b", item["statement"], re.I):
            questions.append(f"{item['id']}: Which observable example or threshold makes this criterion decidable?")
    if questions:
        findings.append(finding("testability_review", "Review potentially subjective criteria; wording alone is not proof of a defect.",
                                ["brainstorm.json"], "warning"))
    result = report("plan-review", plan["story_id"], hashes, findings)
    result["questions"] = questions[:5]
    result["limits"] = ["Structural checks do not prove semantic consistency or sufficient test coverage.",
                        "Questions share the existing intake round/question budget; they do not create another round."]
    return result
