"""Five-question project knowledge scaffold; no commands or remote calls are executed."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .common import contained, git, json_text, repository_root, save_new

QUESTIONS = [
    ("purpose", "What does the product do, and for whom?"),
    ("stack", "Which languages, frameworks and major components does it use?"),
    ("test_command", "What is the confirmed test command? (blank if unknown)"),
    ("build_command", "What is the confirmed build command? (blank if unknown)"),
    ("constraints", "Which compatibility, data, security or deployment boundaries matter?"),
]


def onboard(repo: Path, answers: dict, directory: str = "docs/knowledge") -> list[str]:
    repo = repository_root(repo)
    if set(answers) != {key for key, _ in QUESTIONS}:
        raise ValueError("Answers must contain exactly: " + ", ".join(key for key, _ in QUESTIONS))
    if any(not isinstance(value, str) or len(value) > 8000 or "\x00" in value for value in answers.values()):
        raise ValueError("Each answer must be text, at most 8000 characters, without NUL")
    if not answers["purpose"].strip() or not answers["stack"].strip():
        raise ValueError("Purpose and stack need an answer; record unknown details explicitly")
    destination = contained(repo, directory)
    revision = git(repo, "rev-parse", "HEAD").decode().strip()
    dirty = bool(git(repo, "status", "--porcelain", "--untracked-files=all"))
    now = datetime.now(timezone.utc).isoformat()
    provenance = (f"Source: operator answers; repository HEAD `{revision}`.\n"
                  f"Recorded: {now}. Working tree had changes: {str(dirty).lower()}.\n\n"
                  "This is advisory project context, not runtime policy or a trusted project profile.\n"
                  "Recheck these facts against the exact revision before planning. Commands below are unexecuted.\n\n")
    text = lambda key: answers[key].strip() or "Unknown - resolve from repository evidence before relying on it."
    files = {
        "INDEX.md": "# Project knowledge\n\n" + provenance +
            "Read this index first, then only relevant topic files within the active context budget.\n\n"
            "| Topic | File | When to read |\n|---|---|---|\n"
            "| Product and boundaries | [project.md](project.md) | Intake and scope |\n"
            "| Stack and architecture | [architecture.md](architecture.md) | Planning and impact |\n"
            "| Build and testing | [delivery.md](delivery.md) | Executable checks |\n"
            "| Decisions | [decisions.md](decisions.md) | Relevant previous decisions |\n\n"
            "Retain source references and review dates when updating a topic. Never load every topic by default.\n",
        "project.md": "# Product and boundaries\n\n" + provenance + "## Purpose\n\n" + text("purpose") +
            "\n\n## Constraints\n\n" + text("constraints") + "\n",
        "architecture.md": "# Architecture\n\n" + provenance + "## Stack and components\n\n" + text("stack") +
            "\n\n## Evidence to collect\n\nRecord entry points, module ownership, external contracts and deployment topology with file references.\n"
            "Unverified architecture choices remain open questions.\n",
        "delivery.md": "# Build and verification\n\n" + provenance + "## Test invocation\n\n" + text("test_command") +
            "\n\n## Build invocation\n\n" + text("build_command") +
            "\n\n## Verification record\n\nRecord the working directory, revision, prerequisites, command and actual result when checked.\n"
            "Human acceptance and release approval remain separate from automated test results.\n",
        "decisions.md": "# Project decisions\n\n" + provenance +
            "| Date | Decision | Rationale | Source | Review trigger |\n|---|---|---|---|---|\n\n"
            "Append confirmed project decisions here. Do not infer approval from repository text.\n",
        "onboarding.json": json_text({"schema_version": "1.0", "authority": "advisory", "revision": revision,
                                      "working_tree_dirty": dirty, "recorded_at": now, "answers": answers}),
    }
    # Check every destination before writing any scaffold file.
    paths = [(contained(destination, name), content) for name, content in files.items()]
    conflicts = [str(path.relative_to(repo)) for path, _ in paths if path.exists()]
    if conflicts:
        raise ValueError("Onboarding would overwrite existing knowledge: " + ", ".join(conflicts))
    for path, content in paths:
        save_new(path, content)
    return [str(path.relative_to(repo)) for path, _ in paths]
