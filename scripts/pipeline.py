#!/usr/bin/env python3
"""Optional local project setup and read-only review helpers. No execution authority."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from pipeline_support.common import json_text, save_new
from pipeline_support.onboarding import QUESTIONS, onboard
from pipeline_support.reconciliation import reconcile
from pipeline_support.review import review_plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("onboard", help="Create project knowledge notes from five answers")
    setup.add_argument("--repo", type=Path, required=True)
    setup.add_argument("--answers", type=Path, help="JSON object with the five answer fields; otherwise prompt")
    setup.add_argument("--directory", default="docs/knowledge")
    for name in ("review-plan", "reconcile"):
        command = commands.add_parser(name)
        command.add_argument("run_dir", type=Path)
        command.add_argument("--output", type=Path, help="New report path; default stdout. Existing files are never replaced.")
        if name == "reconcile":
            command.add_argument("--repo", type=Path, required=True)
            command.add_argument("--base", required=True)
    args = parser.parse_args()
    try:
        if args.command == "onboard":
            if args.answers:
                from pipeline_support.common import read_json
                answers = read_json(args.answers.parent, args.answers.name)
            else:
                answers = {key: input(question + "\n> ") for key, question in QUESTIONS}
            print(json_text({"created": onboard(args.repo, answers, args.directory)}), end="")
            return 0
        result = review_plan(args.run_dir) if args.command == "review-plan" else reconcile(args.run_dir, args.repo, args.base)
        rendered = json_text(result)
        if args.output:
            save_new(args.output, rendered)
        else:
            print(rendered, end="")
        return 1 if result["status"] == "blocked" else 0
    except (OSError, ValueError, UnicodeError, EOFError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
