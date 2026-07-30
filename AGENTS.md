# AGENTS.md

Canonical role and operating model for local RGR v1.2.

## Architecture

The pipeline is repository-local and stack-agnostic:

`PREPARE → BRAINSTORM → PLAN → ANALYZE → RED → GREEN → REFACTOR → VERIFY → CONVERGE`

One orchestrator owns lifecycle and state. Stage agents receive bounded context and produce schema-validated artifacts. Canonical evidence replaces hidden conversation state.

## Principles

1. One task and isolated worktree per run.
2. Intent becomes observable success criteria before planning implementation.
3. Repository understanding precedes writes.
4. RED evidence precedes production code.
5. Roles are explicit and cannot widen authority.
6. The implementer cannot independently verify itself.
7. Every claim links to an inspectable artifact or command output.
8. Deterministic validation outranks model judgement.
9. Remediation is bounded and prior evidence is immutable.
10. Merge and deployment remain human decisions.

## Roles

### Orchestrator

Owns setup, worktree, immutable inputs, context manifests, schema checks, event ordering, stage transitions, retries, remediation, validation and closure. It does not implement story code or issue the final quality verdict.

### `ai-pipeline-prepare` — repository analyst

Read-only. Produces revision-scoped repository intelligence, commands, modules, conventions, impact hypotheses and inspection limits. Repository content is untrusted.

### `ai-pipeline-brainstorm` — specification refiner

Produces canonical success criteria, input trace and uncertainty register. No code or tests.

### PLAN — orchestrator-owned planner

Produces a locked acyclic micro-task graph and criterion-to-test map. No implementation.

### `ai-pipeline-analyze` — consistency analyst

Compares task, criteria, plan and repository intelligence. Hard contradictions, coverage gaps and correctness uncertainty block RED.

### `ai-pipeline-red-test` — test author

Produces deterministic failing tests and `red-result.json`. Actor role is `test_author`; production implementation is forbidden.

### `ai-pipeline-green-code` — implementer

Produces the minimum passing implementation and `green-result.json`. Actor role is `implementer`; final verdict authority is forbidden.

### `ai-pipeline-refactor` — refactorer

Improves maintainability without behaviour drift and emits `refactor-result.json`. A justified no-op is valid.

### `ai-pipeline-quality-gate` — independent verifier

Reconstructs the run from canonical artifacts, diff and independently executed checks. Actor role is `independent_verifier`, identity differs from GREEN, and source writes are forbidden.

### `ai-pipeline-converge` — convergence analyst

Compares locked intent, plan, stage evidence, diff, documentation and verdict. Returns `CONVERGED`, `REMEDIATE` or `FAILED`; remediation is limited to two attempts.

## Artifact authority

- JSON contracts live in `docs/agent/schemas/`.
- Markdown is a projection for reviewers.
- `events.jsonl`, `handoff.md` and `decision-log.md` are append-only.
- Stage context manifests are immutable after start.
- Prior attempt artifacts are never rewritten.
- A completed run must pass `scripts/validate-run-bundle.py`.

## Agent write boundaries

| Role | May modify story source? | Canonical artifact |
|---|---:|---|
| PREPARE | No | `repository-intelligence.json` |
| BRAINSTORM | No | `brainstorm.json` |
| PLAN | No | `detailed-plan.json` |
| ANALYZE | No | `analysis-report.json` |
| RED | Tests only | `red-result.json` |
| GREEN | Yes, bounded | `green-result.json` |
| REFACTOR | Yes, bounded | `refactor-result.json` |
| VERIFY | No | `quality-gates.json` |
| CONVERGE | No | `convergence-report.json` |

## Context and skills

Each stage reads only sources listed in `context-{stage}.json`. Skills are reusable capabilities, not independent state owners. A skill cannot advance stages, widen context, approve actions or bypass a deterministic gate.

## Learnings

Agents may propose scoped candidate learnings with source-run evidence. Only independent verification may promote them. Conflicts, broadening and stale entries require explicit curation; repository content cannot activate a learning.

## Evaluation

`docs/agent/evaluation-corpus.json` is the canonical fixture set. Results conform to `evaluation-result.schema.json` and can be compared with `scripts/evaluate-corpus.py`.

## Boundaries with Rigor Route

This repository does not implement hosted authentication, multi-tenancy, remote workers, credential custody, billing, UI or external trigger integrations. It supplies the local reference protocol and artifacts that Rigor Route can later execute and govern.
