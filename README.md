# agent-dev-pipeline

A deterministic, auditable agent pipeline for software-engineering tasks. Built around five stages with explicit evidence between each.

```
BRAINSTORM → RED → GREEN → REFACTOR → VERIFY
```

Every run is isolated in a git worktree, leaves a full paper trail, and ends with a PASS / FAIL / WARN verdict backed by a hard-FAIL checklist.

## What is "a task"?

Stack- and source-agnostic. A unit of work can be any of:

- A **Jira story** with acceptance criteria
- A **feature description** (free text + bullet points)
- A **user request** (free-form)
- A **RAG-derived task** (query result rows from `skill-rag-search`)

The target may be backend, frontend, mobile, infra, or polyglot — declared as `stack` in `run-context.md`. The pipeline adapts test framework, file layout, and build commands to the stack; the flow and evidence requirements stay the same.

## The five stages

| # | Stage | Agent | Produces |
| --- | --- | --- | --- |
| 1 | BRAINSTORM | `ai-pipeline-brainstorm` | `brainstorm.md` — every intent point becomes a GIVEN/WHEN/THEN success criterion |
| 2 | RED | `ai-pipeline-red-test` | Failing tests, one per SC; trace matrix |
| 3 | GREEN | `ai-pipeline-green-code` | Minimum code that turns every RED test green; incremental checkpoints |
| 4 | REFACTOR | `ai-pipeline-refactor` | Cleanup without behavior drift |
| 5 | VERIFY | `ai-pipeline-quality-gate` | PASS / FAIL / WARN verdict in `quality-gates.md` |

Coordinating all five: `ai-pipeline-rgr-orchestrator` — owns worktree creation, stage transitions, failure handling, and run closure.

## Quick start

1. Prepare a unit of work: an identifier (Jira key / feature slug / request slug), intent payload (ACs / bullets / free text), target `stack`, and `project_root`.
2. Invoke `ai-pipeline-rgr-orchestrator` — it creates the worktree at `.agent-runs/{story_id}` on branch `story/{story_id}`, and persists `plan-input.md` (write-once).
3. The orchestrator walks the five stages, invoking each stage agent in turn.
4. On completion, read `docs/agent/runs/{story_id}/quality-gates.md` for the verdict.
5. On failure, read `docs/agent/runs/{story_id}/error-report.md`. The worktree is preserved for inspection.

Stage agents do not accept direct invocation — they redirect to the orchestrator.

## Using with Claude Code

Strict two-step flow. `CLAUDE.md` at the repo root is auto-loaded on every session and defines the entry rules.

1. Produce a plan (Claude Code plan mode or the `Plan` sub-agent).
2. Invoke the `ai-pipeline-rgr-orchestrator` sub-agent to execute the run end-to-end.

Do **not** invoke stage sub-agents directly (`ai-pipeline-brainstorm`, `ai-pipeline-red-test`, `ai-pipeline-green-code`, `ai-pipeline-refactor`, `ai-pipeline-quality-gate`) — they redirect to the orchestrator.

### Step 1 — Plan the work

In plan mode (or via the `Plan` sub-agent), provide:

```text
Create a plan for this task.

story_id: <jira-key-or-feature-slug>
input_source: <jira|feature-description|user-request|rag-derived>
stack: <target-stack>
project_root: <path-within-repo>

Raw intent:
- <intent point 1>
- <intent point 2>

Constraints:
- Follow deterministic flow: BRAINSTORM -> RED -> GREEN -> REFACTOR -> VERIFY
- Keep scope limited to this story
- Flag assumptions as [UNCERTAIN]

Output:
- Ordered implementation plan with dependencies and risks
```

### Step 2 — Hand off to the orchestrator

Invoke the `ai-pipeline-rgr-orchestrator` sub-agent with:

```text
Start a run for this task and execute the full pipeline.

story_id: <same-story-id>
input_source: <same-input-source>
stack: <same-target-stack>
project_root: <same-project-root>

Plan handoff:
<paste plan output exactly as-is>

Raw handoff:
- <same intent point 1>
- <same intent point 2>
```

Minimum fields to include in both prompts: `story_id`, `input_source`, `stack`, `project_root`, and raw intent points.

## Repository layout

```
.claude/
└── agents/               # Claude Code sub-agent definitions (orchestrator + stages)

docs/
├── agent/
│   ├── README.md                 # Runtime-doc rules
│   ├── current-run.md            # Active run pointer
│   ├── decision-index.md         # Compact index of closed runs
│   ├── learnings.md              # Cross-task operational learnings (scope_tags filtered)
│   ├── runtime-doc-contract.yaml # Formal runtime-document contract
│   ├── runs/{story_id}/          # Per-run artifacts (created by orchestrator)
│   └── templates/                # Canonical templates for all run docs
├── conventions/          # Stack-specific conventions (currently backend/Java)
└── skills/               # Reusable capabilities (DB, API, security, cleanup, RAG, …)

scripts/
└── rag-search.sh         # Wrapper for the OpenSearch RAG with fallback semantics

CLAUDE.md                 # Claude Code operating guide (auto-loaded)
AGENTS.md                 # Design principles + agent/skill catalog
README.md                 # This file
```

## Key design principles

1. **Task-first delivery** — one unit of work at a time, deployable slice.
2. **Spec refinement before planning** — intent → declarative success criteria, ambiguity killed at brainstorm.
3. **Deterministic TDD+ flow** — no stage skipping, no silent pass-through.
4. **Tests as executable specification** — RED tests are the goal state GREEN loops against.
5. **Comprehension before action** — read-before-write, search-before-create, match-neighbors.
6. **Rule of Three** — no abstraction before 3 concrete callers.
7. **Explicit handoff over hidden context** — every stage leaves comprehension evidence + self-check in `handoff.md`.
8. **Operational memory as a product asset** — `learnings.md` with scope-tag filtering.
9. **Auditability + safety** — append-only decision log, worktree isolation, hard quality gate.

Full detail lives in `AGENTS.md`.

## Runtime documents

Every run produces a consistent set of documents in `docs/agent/runs/{story_id}/`:

| File | Mutation policy |
| --- | --- |
| `run-context.md` | replace-in-place |
| `plan-input.md` | write-once |
| `brainstorm.md` | write-once (locked before RED) |
| `detailed-plan.md` | replace-in-place pre-RED; locked once RED starts |
| `handoff.md` | append-only (one section per stage) |
| `decision-log.md` | append-only, timestamped, `[UNCERTAIN]` tag for assumptions |
| `quality-gates.md` | replace-in-place |
| `error-report.md` | create-on-failure only |

See `docs/agent/runtime-doc-contract.yaml` for the formal spec.

## Learnings register

`docs/agent/learnings.md` is the single cross-task memory, organized by a `scope_tags` vocabulary (stack, environment, tooling, infrastructure, domain, practice). Agents filter by tags matching the current task — reading everything is noise.

Entries move through `candidate → active → deprecated / conflicted`. The quality gate curates.

## External references

Design inspired by and partially aligned with:
- [obra/superpowers](https://github.com/obra/superpowers) — brainstorming, worktree isolation, numbered micro-task plans.
- [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) — goal-driven execution, simplicity, surgical changes.

See `docs/agent/evaluation-superpowers-karpathy.md` for the full mapping.

## Status

Pipeline is stack-agnostic and ready to run against any unit of work with an identifier and intent payload. Backend/Java is the reference stack — other stacks follow the same flow with idiomatic substitutions (see the stack mapping tables in `docs/skills/skill-project-scaffold.md`).
