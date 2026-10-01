"""Regression coverage for the optional configuration/review boundary."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from pipeline_support.common import MAX_BYTES, read_bytes, save_new
from pipeline_support.onboarding import onboard
from pipeline_support.reconciliation import reconcile
from pipeline_support.review import review_plan

spec = importlib.util.spec_from_file_location("fixture", ROOT / "scripts/generate-contract-fixture.py")
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


class OperatorToolsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run = self.root / "run"
        fixture.generate(self.run)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "--allow-empty", "-qm", "Base")
        self.base = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True, text=True).stdout

    def edit(self, name, change):
        path = self.run / name
        value = json.loads(path.read_text())
        change(value)
        path.write_text(json.dumps(value))

    def prepare_changes(self):
        self.edit("repository-intelligence.json", lambda value: value.update(revision=self.base))
        for name in ("backend/fixture.py", "frontend/fixture.ts", "test_fixture.py"):
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("fixture\n")

    def test_valid_plan_and_read_only_review(self):
        original = {p.name: p.read_bytes() for p in self.run.glob("*.json")}
        result = review_plan(self.run)
        self.assertEqual(result["status"], "clear")
        self.assertEqual(result["authority"], "advisory")
        self.assertEqual(original, {p.name: p.read_bytes() for p in self.run.glob("*.json")})

    def test_cycles_and_missing_coverage_block(self):
        def corrupt(plan):
            plan["tasks"][0]["depends_on"] = ["TASK-2"]
            plan["criterion_test_map"][0]["sc_id"] = "SC-99"
        self.edit("detailed-plan.json", corrupt)
        codes = {item["code"] for item in review_plan(self.run)["findings"]}
        self.assertTrue({"dependency_graph", "test_coverage"} <= codes)

    def test_unknown_criteria_and_traversal_block(self):
        def corrupt(plan):
            plan["tasks"][0].update(criteria=["SC-99"], outputs=["../outside.py"])
        self.edit("detailed-plan.json", corrupt)
        self.assertEqual(review_plan(self.run)["status"], "blocked")

    def test_subjective_wording_is_advisory_and_questions_bounded(self):
        def alter(brainstorm):
            base = brainstorm["success_criteria"][0]
            brainstorm["success_criteria"] = [dict(base, id=f"SC-{i}", statement="The response is fast and appropriate.") for i in range(1, 9)]
        self.edit("brainstorm.json", alter)
        result = review_plan(self.run)
        self.assertEqual(len(result["questions"]), 5)
        self.assertEqual(next(f for f in result["findings"] if f["code"] == "testability_review")["severity"], "warning")

    def test_reconciliation_captures_staged_and_untracked_changes(self):
        self.prepare_changes()
        self.git("add", "backend/fixture.py")
        result = reconcile(self.run, self.repo, self.base)
        self.assertEqual(result["status"], "review")  # No documentation task: explicit human review.
        self.assertEqual(len(result["changed_files"]), 3)
        self.assertEqual(len(result["changed_file_sha256"]["backend/fixture.py"]), 64)
        self.assertTrue(result["evidence_sha256"])

    def test_scope_drift_cannot_rewrite_locked_plan(self):
        self.prepare_changes()
        (self.repo / "unexpected.py").write_text("unplanned")
        before = (self.run / "detailed-plan.json").read_bytes()
        result = reconcile(self.run, self.repo, self.base)
        self.assertIn("scope_drift", [f["code"] for f in result["findings"]])
        self.assertEqual(before, (self.run / "detailed-plan.json").read_bytes())

    def test_wrong_base_missing_evidence_and_symlink_block(self):
        self.prepare_changes()
        self.edit("repository-intelligence.json", lambda value: value.update(revision="f" * 40))
        self.edit("quality-gates.json", lambda value: value["criterion_evidence"][0].update(evidence_refs=["../outside.log"]))
        (self.repo / "backend/fixture.py").unlink()
        (self.repo / "backend/fixture.py").symlink_to(self.run / "brainstorm.json")
        codes = {f["code"] for f in reconcile(self.run, self.repo, self.base)["findings"]}
        self.assertTrue({"base_mismatch", "missing_evidence", "uninspectable_change"} <= codes)
        with self.assertRaises(ValueError):
            reconcile(self.run, self.repo, "HEAD")

    def test_onboarding_is_create_only_and_does_not_execute_commands(self):
        sentinel = self.root / "not-executed"
        answers = dict(purpose="Example product", stack="Python", test_command=f"touch {sentinel}", build_command="", constraints="")
        paths = onboard(self.repo, answers)
        self.assertEqual(len(paths), 6)
        self.assertFalse(sentinel.exists())
        self.assertIn("advisory", (self.repo / "docs/knowledge/INDEX.md").read_text())
        with self.assertRaises(ValueError):
            onboard(self.repo, answers)
        with self.assertRaises(ValueError):
            onboard(self.repo, answers, "../outside")

    def test_bounded_inputs_and_create_only_reports(self):
        target = self.root / "large.json"
        target.write_bytes(b" " * (MAX_BYTES + 1))
        with self.assertRaises(ValueError):
            read_bytes(self.root, target.name)
        save_new(self.root / "report.json", "first")
        with self.assertRaises(ValueError):
            save_new(self.root / "report.json", "replacement")
        (self.root / "linked").symlink_to(target)
        with self.assertRaises(ValueError):
            read_bytes(self.root, "linked")

    def test_cli_failure_exit_codes(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/pipeline.py"), "reconcile", str(self.run),
                                 "--repo", str(self.repo), "--base", "HEAD"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
