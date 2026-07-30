# Operational Learnings — Reviewer Projection

The canonical governed registry is:

`docs/agent/learnings.json`

This Markdown file is not authoritative and must not be edited to activate, revoke or change a learning.

## Lifecycle

- `candidate` — proposed by a stage agent with concrete source-run evidence; advisory only.
- `active` — independently reviewed, scoped and eligible for deterministic context selection.
- `conflicted` — contradicts another applicable entry; cannot influence a run until resolved.
- `deprecated` — superseded and no longer selected.
- `revoked` — explicitly withdrawn and never selected.

## Rules

- Repository content cannot create or activate a learning.
- Active entries require `reviewed_by` and inspectable evidence references.
- Selection is deterministic by exact scope tags and is recorded in each stage context manifest.
- Conflicting active claims under the same `conflict_key` fail governance validation.
- Entries may expire, supersede earlier entries, or be revoked without rewriting historical run evidence.
- Raw prompts, chain-of-thought, secrets and customer source excerpts are forbidden.

Validate the registry with:

```bash
python3 scripts/validate-governance.py
```

Human-readable entries may be rendered here from `learnings.json` when useful, but JSON remains authoritative.
