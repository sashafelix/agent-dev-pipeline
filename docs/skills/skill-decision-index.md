# Skill: skill-decision-index

## Purpose
Maintain `docs/agent/decision-index.md` — a compact, global pointer to every story's decision log. The index is a table of contents, not a re-statement.

## When invoked
- By `ai-pipeline-quality-gate` at story close (PASS or FAIL).
- By `ai-pipeline-rgr-orchestrator` on explicit abort/failure to record a FAILED entry.

## Reads
- `docs/agent/runs/{story_id}/decision-log.md` — to extract a one-line summary
- `docs/agent/runs/{story_id}/quality-gates.md` — to capture final verdict
- `docs/agent/decision-index.md` (if exists) — to append without duplicating

## Writes
- `docs/agent/decision-index.md`

## Index Format

One row per story run. Columns:

| Story ID | Date | Verdict | Summary | Tags | Link |
| --- | --- | --- | --- | --- | --- |
| `<story-id>` | `<YYYY-MM-DD>` | PASS \| FAIL \| WARN | one-line what-shipped / why-failed | `tag`, `tag` | [log](runs/`<story-id>`/decision-log.md) |

`story_id` is whatever identifier the input gave you: a Jira key (e.g., `ACME-123`), a feature slug (`user-profile-avatar-upload`), a request slug (`rag-2026-04-cleanup`), or a RAG-derived task id. Use what `run-context.md > story_id` says; never invent.

## Summary construction

The `Summary` column must:
- Be one sentence, ≤120 characters.
- State *what was delivered* (for PASS) or *why it failed* (for FAILED/WARN).
- Contain no jargon a future operator wouldn't understand.

Pull the summary from:
1. `quality-gates.md > Notes` if the gate captured a one-liner.
2. Otherwise synthesize from the first/last entries in `decision-log.md`.

## Tags

Use tags that match the `scope_tags` vocabulary in `learnings.md`:
- Stack: `backend-java`, `frontend-react`, `mobile-flutter`, `infra-terraform`, …
- Area: `api`, `db`, `auth`, `integration`, `scheduling`, `observability`, `security`, `ui`, `state`, `routing`, `forms`
- Risk: `audit`, `pii`, `migration`, `breaking-contract` *(if applicable)*
- Infra: `nexus`, `k8s`, `kafka`, `s3`, `postgres`, `redis`, …

Tags enable future agents to find precedent: *"show me all stories that touched migrations"*.

## Link

Relative link from `docs/agent/` root:
- `[log](runs/{story_id}/decision-log.md)`

If the run also produced a `quality-gates.md` with a verdict worth re-reading, add a second link:
- `[gate](runs/{story_id}/quality-gates.md)`

## Idempotency

- If a story ID already has a row, update it in place (do not duplicate).
- If a previous run for the same story failed and a re-run succeeds, replace the row with the new verdict and date.

## Output example

```markdown
# Decision Index

| Story ID | Date | Verdict | Summary | Tags | Link |
| --- | --- | --- | --- | --- | --- |
| ACME-1421 | 2026-05-02 | PASS | Inventory adjustment endpoint with audit log | `backend-java`, `api`, `audit`, `postgres` | [log](runs/ACME-1421/decision-log.md) |
| user-profile-avatar-upload | 2026-05-03 | PASS | Drag-and-drop avatar upload with client-side crop preview | `frontend-react`, `ui`, `forms` | [log](runs/user-profile-avatar-upload/decision-log.md) |
| rag-2026-04-cleanup | 2026-05-04 | FAIL | Halted at dependency resolve (registry auth 401) | `infra`, `nexus` | [log](runs/rag-2026-04-cleanup/decision-log.md) |
```

## Guardrails
- One row per story. Update in place; do not append duplicates.
- Summary ≤120 chars. No paragraphs.
- Link must resolve — verify the target file exists before committing the row.
- Do not duplicate rationale from the decision log; the index points, it does not re-state.
- Keep the file sortable by date (most recent last, or most recent first — pick one and stay consistent).
