"""Compare locked intent, verification evidence and an explicitly selected Git diff."""
from __future__ import annotations

from pathlib import Path
import re

from .common import contained, finding, git, read_bytes, read_json, report, repository_root, sha256
from .review import check_plan, load_plan


def reconcile(run: Path, repo: Path, base: str) -> dict:
    repo = repository_root(repo)
    run = run.resolve()
    if not re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", base):
        raise ValueError("--base must be the full immutable Git commit SHA used for repository intelligence")
    base = git(repo, "rev-parse", "--verify", base + "^{commit}").decode().strip()
    brainstorm, plan, hashes = load_plan(run)
    findings = check_plan(brainstorm, plan)
    quality = read_json(run, "quality-gates.json", "quality-gates.schema.json")
    intelligence = read_json(run, "repository-intelligence.json", "repository-intelligence.schema.json")
    for name in ("quality-gates.json", "repository-intelligence.json"):
        hashes[name] = sha256(read_bytes(run, name))
    def add(code: str, message: str, refs: list[str], severity: str = "blocking") -> None:
        findings.append(finding(code, message, refs, severity))
    for name, document in (("quality-gates.json", quality), ("repository-intelligence.json", intelligence)):
        if document["story_id"] != plan["story_id"]:
            add("story_mismatch", f"{name} identifies a different story.", [name])
    if intelligence["revision"] != base:
        add("base_mismatch", "Selected base differs from the recorded repository-intelligence revision.", ["repository-intelligence.json"])
    if quality["verdict"] == "FAIL" or quality["hard_failures"]:
        add("verification_failed", "Independent verification contains blocking failures.", ["quality-gates.json"])
    expected = {item["id"] for item in brainstorm["success_criteria"]}
    actual = [item["sc_id"] for item in quality["criterion_evidence"]]
    if set(actual) != expected or len(actual) != len(set(actual)):
        add("verification_coverage", "Verification must cover each locked criterion exactly once.", ["brainstorm.json", "quality-gates.json"])
    tests = {item["sc_id"]: set(item["test_ids"]) for item in plan["criterion_test_map"]}
    evidence_hashes = {}
    for item in quality["criterion_evidence"]:
        if item["status"] != "PASS":
            add("criterion_result", f"{item['sc_id']} verification status is {item['status']}.", ["quality-gates.json"],
                "blocking" if item["status"] == "FAIL" else "warning")
        if tests.get(item["sc_id"], set()) - set(item["tests"]):
            add("test_drift", f"{item['sc_id']} omits tests from the locked map.", ["detailed-plan.json", "quality-gates.json"])
        for ref in item["evidence_refs"]:
            try:
                evidence_hashes[ref] = sha256(read_bytes(run, ref))
            except ValueError as exc:
                add("missing_evidence", str(exc), ["quality-gates.json"])
    raw = git(repo, "diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--name-only", "-z", base, "--")
    raw += git(repo, "ls-files", "--others", "--exclude-standard", "-z")
    changed = sorted(set(name.decode("utf-8") for name in raw.split(b"\0") if name))
    # Canonical run evidence is not a story source edit. No other path is excluded.
    if run != repo and run.is_relative_to(repo):
        prefix = run.relative_to(repo).as_posix() + "/"
        changed = [name for name in changed if not name.startswith(prefix)]
    outputs = {name for task in plan["tasks"] for name in task["outputs"]}
    undeclared = sorted(set(changed) - outputs)
    if undeclared:
        add("scope_drift", f"Changed files outside locked task outputs: {undeclared}", ["detailed-plan.json"])
    if set(quality["changed_files"]) != set(changed):
        add("changed_files_drift", "VERIFY changed_files differs from the selected base-to-working-tree diff (including untracked files).", ["quality-gates.json"])
    source_hashes = {}
    for name in changed:
        try:
            path = contained(repo, name)
            source_hashes[name] = sha256(read_bytes(repo, name)) if path.exists() else None
        except ValueError as exc:
            add("uninspectable_change", str(exc), ["detailed-plan.json"])
    document_outputs = {name for task in plan["tasks"] if task["stage"] == "documentation" for name in task["outputs"]}
    if changed and not document_outputs:
        add("documentation_review", "No documentation task was declared. Record which user/API/operations docs are affected, or why none need changing.",
            ["detailed-plan.json"], "warning")
    for name in sorted(document_outputs):
        try:
            read_bytes(repo, name)
        except ValueError as exc:
            add("documentation_missing", str(exc), ["detailed-plan.json"])
    result = report("reconciliation", plan["story_id"], hashes, findings)
    result.update({"base_revision": base, "head_revision": git(repo, "rev-parse", "HEAD").decode().strip(),
                   "changed_files": changed, "changed_file_sha256": source_hashes, "evidence_sha256": evidence_hashes,
                   "limits": ["Run validators and independent semantic review remain required; files and hashes do not prove tests ran.",
                              "This report is a point-in-time inspection, not an atomic Git snapshot or an approval."]})
    return result
