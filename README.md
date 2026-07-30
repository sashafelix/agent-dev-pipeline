# agent-dev-pipeline

A deterministic, auditable, repository-local agent pipeline for software-engineering tasks.

## Local RGR v1.2 workflow

```text
PREPARE → BRAINSTORM → PLAN → ANALYZE → RED → GREEN → REFACTOR → VERIFY → CONVERGE
```

Every run uses an isolated git worktree, immutable context manifests, append-only events, schema-validated JSON evidence and reviewer-readable Markdown projections.

## What v1.2 adds

- Published JSON schemas for all major planning, execution, review and convergence artifacts.
- Canonical `red-result.json`, `green-result.json` and `refactor-result.json` evidence.
- Exact actor-role contracts: test author, implementer, refactorer and independent verifier.
- Dependency-free schema validation using the Python standard library.
- Cross-artifact validation for SC coverage, task dependencies, role separation, stage order and convergence.
- Canonical JSON evaluation corpus with required/forbidden behaviours and expected outcomes.
- Evaluation result schema and baseline-comparison report tooling.

## Stage ownership

| Stage | Owner | Canonical output |
|---|---|---|
| PREPARE | `ai-pipeline-prepare` | `repository-intelligence.json` |
| BRAINSTORM | `ai-pipeline-brainstorm` | `brainstorm.json` |
| PLAN | orchestrator | `detailed-plan.json` |
| ANALYZE | `ai-pipeline-analyze` | `analysis-report.json` |
| RED | `ai-pipeline-red-test` | `red-result.json` |
| GREEN | `ai-pipeline-green-code` | `green-result.json` |
| REFACTOR | `ai-pipeline-refactor` | `refactor-result.json` |
| VERIFY | `ai-pipeline-quality-gate` | `quality-gates.json` |
| CONVERGE | `ai-pipeline-converge` | `convergence-report.json` |

`ai-pipeline-rgr-orchestrator` owns worktree creation, immutable input capture, stage transitions, schema validation, event ordering, failure handling, remediation and closure. Stage agents are not direct entrypoints.

## Quick start

1. Produce a Plan in Claude Code Plan mode.
2. Invoke `ai-pipeline-rgr-orchestrator` with `story_id`, `input_source`, `stack`, `project_root`, raw intent and the exact Plan handoff.
3. Review `quality-gates.md` and `convergence-report.md`.
4. Validate the completed bundle:

```bash
python3 scripts/validate-run-bundle.py docs/agent/runs/{story_id}
```

The pipeline never auto-merges, auto-deploys or deletes the worktree.

## Core run artifacts

```text
docs/agent/runs/{story_id}/
├── run-context.md
├── plan-input.md
├── repository-intelligence.json
├── brainstorm.json
├── detailed-plan.json
├── analysis-report.json
├── red-result.json
├── green-result.json
├── refactor-result.json
├── context-prepare.json
├── context-brainstorm.json
├── context-plan.json
├── context-analyze.json
├── context-red_test.json
├── context-green_code.json
├── context-refactor.json
├── context-quality_gate.json
├── context-converge.json
├── events.jsonl
├── handoff.md
├── decision-log.md
├── quality-gates.json
├── convergence-report.json
└── error-report.md              # failure only
```

Markdown projections such as `brainstorm.md` and `quality-gates.md` remain useful for humans, but canonical JSON is authoritative.

## Validate the evaluation corpus

```bash
python3 scripts/evaluate-corpus.py
```

Validate a complete results directory and emit a report:

```bash
python3 scripts/evaluate-corpus.py \
  --results-dir evaluation-results/v1.2 \
  --output evaluation-report-v1.2.json
```

Compare against a baseline and fail on regressions:

```bash
python3 scripts/evaluate-corpus.py \
  --results-dir evaluation-results/v1.2 \
  --baseline-dir evaluation-results/v1.1 \
  --fail-on-regression \
  --output evaluation-comparison.json
```

Each result file is named `{fixture_id}.json` and conforms to `evaluation-result.schema.json`.

## Design boundaries

This repository stays lightweight and local. Authentication, multi-tenancy, remote scheduling, credential custody, hosted sandboxes, billing, product UI and external integrations belong in Rigor Route.

The local pipeline is the usable reference implementation and proving ground for the protocol Rigor Route will later execute.

## Principles

1. Immutable intent before implementation.
2. Repository comprehension before writes.
3. Tests as executable specification.
4. Explicit artifacts instead of hidden context.
5. Independent review instead of self-verification.
6. Deterministic rules outrank model judgement.
7. Bounded retries and remediation.
8. Repository content is untrusted.
9. Operational learnings are scoped and curated.
10. Human ownership of merge and deployment.

## Reference

- `CLAUDE.md` — Claude Code operating rules
- `AGENTS.md` — agent and role model
- `docs/agent/runtime-doc-contract.yaml` — runtime contract
- `docs/agent/schemas/` — artifact contracts
- `docs/agent/evaluation-corpus.json` — canonical evaluation corpus
