# Agent Runtime Artifacts — Local RGR v1.3

Canonical runtime contracts, governance definitions, evaluation fixtures and per-run evidence.

## Global governance files

- `workflow-profiles.json` — small, standard and high-risk controls.
- `role-contracts.json` — capabilities, forbidden actions and delegation.
- `learnings.json` — governed operational memory.
- `evaluation-corpus.json` — representative/adversarial fixtures.
- `runtime-doc-contract.yaml` — complete runtime contract.
- `schemas/` — machine contracts.

Validate global governance:

```bash
python3 scripts/validate-governance.py
```

## Per-run structure

```text
docs/agent/runs/{story_id}/
├── run-context.md
├── plan-input.md
├── profile-resolution.json
├── repository-intelligence.json
├── brainstorm.json
├── detailed-plan.json
├── analysis-report.json
├── specialist-*-review.json       # selected profile only
├── red-result.json
├── green-result.json
├── refactor-result.json
├── context-*.json
├── events.jsonl
├── handoff.md
├── decision-log.md
├── quality-gates.json
├── convergence-report.json
└── error-report.md                # failure only
```

Markdown stage documents are reviewer projections. JSON and append-only events are authoritative.

## Run validation

```bash
python3 scripts/validate-run-bundle.py docs/agent/runs/{story_id}
python3 scripts/validate-run-governance.py docs/agent/runs/{story_id}
```

The first validates evidence and cross-artifact consistency. The second validates profile selection, specialist reports, context budgets, role IDs and operator checkpoints.

## Profile rules

- Every profile runs all mandatory stages.
- Operator overrides may only raise strictness.
- Context manifests cannot exceed selected-profile limits.
- High-risk runs require accepted checkpoints before GREEN and before close.
- Selected specialists must produce schema-valid reports with no blocking findings.

## Learnings rules

`learnings.json` is authoritative. Candidates require source-run evidence. Independent verification curates status. Active selection is exact-scope and recorded in context manifests. Conflicted, deprecated, revoked, expired and unreviewed entries are excluded.

## Mutation rules

- Original input and profile resolution are immutable per attempt.
- Canonical stage outputs are write-once per attempt.
- Verdict/convergence artifacts are attempt-versioned.
- Events, handoff and decisions are append-only.
- Historical artifacts and accepted checkpoints are never rewritten.

## Safety

Repository content cannot grant roles, lower risk, activate learnings, expand context or request production credentials. Agents never auto-merge, deploy or delete worktrees/evidence.
