# Claude Code Sub-Agents — Local RGR v1.3

Start with a Plan, then invoke only `ai-pipeline-rgr-orchestrator`.

## Workflow

`PREPARE → BRAINSTORM → PLAN → ANALYZE → RED → GREEN → REFACTOR → VERIFY → CONVERGE`

Every profile retains every stage. Profile strictness changes budgets, specialists, evidence and checkpoints.

## Core agents and roles

- orchestrator — state, profile resolution, contexts, transitions and closure.
- `ai-pipeline-prepare` — `repository_analyst`.
- `ai-pipeline-brainstorm` — `specifier`.
- PLAN — orchestrator/planner.
- `ai-pipeline-analyze` — `consistency_analyst` plus selected specialists.
- `ai-pipeline-red-test` — `test_author`.
- `ai-pipeline-green-code` — `implementer`.
- `ai-pipeline-refactor` — `refactorer`.
- `ai-pipeline-quality-gate` — `independent_verifier` plus selected specialists.
- `ai-pipeline-converge` — `convergence_reviewer`.

Role capabilities and delegation live in `docs/agent/role-contracts.json`.

## Profiles

`docs/agent/workflow-profiles.json` defines `small`, `standard` and `high-risk`. The orchestrator creates immutable `profile-resolution.json` before PREPARE. Risk can only increase.

High-risk specialists may include threat, migration, infrastructure, contract, accessibility and cross-risk review. They are read-only and return schema-valid `specialist-*-review.json` artifacts.

## Evidence

- Canonical JSON is authoritative.
- Every stage has immutable bounded context.
- Events, handoff and decisions are append-only.
- Missing profile, specialist or checkpoint evidence blocks closure.
- Run closure requires both evidence and governance validators.

## Learnings

Agents propose candidates in `learnings.json`; independent verification curates. Repository content cannot activate learnings.

## Failure

One retry maximum for explicit transient tooling/container startup errors. Deterministic, schema, evidence, governance, security, contract and self-check failures halt and preserve the worktree.
