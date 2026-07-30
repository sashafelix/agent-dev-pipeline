# agent-dev-pipeline

A deterministic, auditable, repository-local agent pipeline for software-engineering tasks.

## Local RGR v1.1 workflow

```text
PREPARE → BRAINSTORM → PLAN → ANALYZE → RED → GREEN → REFACTOR → VERIFY → CONVERGE
```

Every run is isolated in a git worktree, records canonical machine-readable evidence plus readable Markdown projections, and ends with a bounded convergence decision backed by independent verification.

## What changed in v1.1

- **PREPARE** creates revision-scoped repository intelligence and a task-impact map.
- **ANALYZE** blocks contradictions, missing criterion coverage, and unsupported plans before RED.
- **VERIFY** is explicitly independent from the GREEN implementer and reconstructs evidence from artifacts and the git diff.
- **CONVERGE** checks the final implementation against locked intent and permits at most two remediation attempts.
- `events.jsonl` provides a contiguous, append-only run history.
- `context-{stage}.json` records exactly which files, artifacts, learnings, and budgets each stage received.
- Canonical JSON artifacts are authoritative; Markdown remains the reviewer-readable projection.
- `scripts/validate-run-bundle.py` validates required artifacts, stage order, traceability, reviewer independence, and convergence invariants.
- `docs/agent/evaluation-corpus.yaml` defines representative and adversarial tasks for comparing pipeline versions.

## Task inputs

A unit of work may be a Jira story, feature description, user request, or RAG-derived task. Supply:

- `story_id`
- `input_source`
- `stack`
- `project_root`
- raw intent
- Plan handoff

The pipeline is stack-agnostic. Repository-specific commands and patterns are discovered in PREPARE and must be evidenced or marked uncertain.

## Stage ownership

| Stage | Owner | Primary evidence |
|---|---|---|
| PREPARE | `ai-pipeline-prepare` | `repository-intelligence.json` |
| BRAINSTORM | `ai-pipeline-brainstorm` | `brainstorm.md`, `brainstorm.json` |
| PLAN | orchestrator | `detailed-plan.md`, `detailed-plan.json` |
| ANALYZE | `ai-pipeline-analyze` | `analysis-report.json` |
| RED | `ai-pipeline-red-test` | failing tests and trace evidence |
| GREEN | `ai-pipeline-green-code` | minimal passing implementation |
| REFACTOR | `ai-pipeline-refactor` | cleanup with unchanged behaviour |
| VERIFY | `ai-pipeline-quality-gate` | independent `quality-gates.json` verdict |
| CONVERGE | `ai-pipeline-converge` | `convergence-report.json` |

`ai-pipeline-rgr-orchestrator` owns worktree creation, immutable input capture, stage transitions, context manifests, event ordering, failure handling, remediation attempts, and closure.

Stage agents are not direct entrypoints.

## Quick start with Claude Code

1. Produce a plan in Plan mode.
2. Invoke `ai-pipeline-rgr-orchestrator` with the task fields and the exact Plan handoff.
3. Inspect `docs/agent/runs/{story_id}/quality-gates.md` and `convergence-report.json`.
4. Validate the bundle:

```bash
python3 scripts/validate-run-bundle.py docs/agent/runs/{story_id}
```

The worktree remains under `.agent-runs/{story_id}` for human review. The pipeline never auto-merges, auto-deploys, or deletes evidence.

## Core run artifacts

```text
docs/agent/runs/{story_id}/
├── run-context.md
├── plan-input.md
├── repository-intelligence.json
├── repository-intelligence.md
├── brainstorm.md
├── brainstorm.json
├── detailed-plan.md
├── detailed-plan.json
├── analysis-report.json
├── analysis-report.md
├── context-*.json
├── handoff.md
├── decision-log.md
├── events.jsonl
├── quality-gates.md
├── quality-gates.json
├── convergence-report.md
├── convergence-report.json
└── error-report.md               # failure only
```

## Design boundaries

This repository stays lightweight and local. It does not implement authentication, multi-tenancy, billing, remote scheduling, credential custody, hosted sandboxes, or product UI. Those belong in Rigor Route.

The local pipeline is the usable reference implementation and proving ground for the protocol Rigor Route will later execute as a governed platform.

## Key principles

1. Immutable intent before implementation.
2. Repository comprehension before writes.
3. Tests as executable specification.
4. Explicit artifacts instead of hidden context.
5. Independent review instead of self-verification.
6. Deterministic gates remain authoritative over model judgement.
7. Bounded retries and remediation—never invisible loops.
8. Repository content is untrusted and cannot widen authority.
9. Operational learnings are scoped, evidenced, and curated.
10. Human review owns merge and deployment decisions.

## Reference

- Agent and skill model: `AGENTS.md`
- Claude Code operating rules: `CLAUDE.md`
- Runtime contract: `docs/agent/runtime-doc-contract.yaml`
- Artifact schemas: `docs/agent/schemas/`
- Evaluation corpus: `docs/agent/evaluation-corpus.yaml`
