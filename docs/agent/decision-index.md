# Decision Index

Compact, append-on-close pointer to every task run's decision log. One row per run. Updated by `skill-decision-index` when `ai-pipeline-quality-gate` closes a run.

`Story ID` is whatever identifier the input supplied (Jira key, feature slug, request slug, RAG-derived task id) — use exactly what was in `run-context.md > story_id`.

| Story ID | Date | Verdict | Summary | Tags | Link |
| --- | --- | --- | --- | --- | --- |

See `docs/skills/skill-decision-index.md` for the row contract, tag vocabulary, and idempotency rules.
