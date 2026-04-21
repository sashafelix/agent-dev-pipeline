# Claude Code Sub-Agents

Sub-agent definitions for Claude Code. Each file uses YAML frontmatter (`name`, `description`) followed by the agent body.

The pipeline is stack-agnostic. A unit of work may be a Jira story, a feature description, a free-form user request, or a RAG-derived task. The target may be backend, frontend, mobile, infra, or polyglot.

## Agents
- `ai-pipeline-rgr-orchestrator.md` — run lifecycle, worktree isolation, stage transitions
- `ai-pipeline-brainstorm.md` — spec refinement into declarative success criteria
- `ai-pipeline-red-test.md` — encode SCs as failing tests
- `ai-pipeline-green-code.md` — minimal code to make RED tests pass
- `ai-pipeline-refactor.md` — cleanup without behavior drift
- `ai-pipeline-quality-gate.md` — final PASS/FAIL/WARN verdict

## Skills
Skill reference docs live under `docs/skills/`. Agents read them as context — they are not Claude Code auto-discovered skills.

## Entry policy
- Start from Plan output (Claude Code plan mode or `Plan` sub-agent) and invoke `ai-pipeline-rgr-orchestrator` only.
- Stage sub-agents are orchestrator-invoked, not direct entrypoints.
- Runtime doc behavior is defined in `docs/agent/runtime-doc-contract.yaml`.

## Execution order
1. Plan step produces a high-level plan in chat.
2. `ai-pipeline-rgr-orchestrator` receives plan + task context (identifier, `input_source`, `stack`, `project_root`); creates worktree at `.agent-runs/{story_id}` and run folder at `docs/agent/runs/{story_id}/`.
3. `ai-pipeline-rgr-orchestrator` persists `plan-input.md` (write-once).
4. `ai-pipeline-rgr-orchestrator` invokes `ai-pipeline-brainstorm` — refines input intent (Jira ACs, feature bullets, free-form request, RAG findings) into declarative SCs in `brainstorm.md`.
5. `ai-pipeline-rgr-orchestrator` writes `detailed-plan.md` (numbered micro-tasks) from `brainstorm.md`, then locks it.
6. `ai-pipeline-rgr-orchestrator` executes `ai-pipeline-red-test` → `ai-pipeline-green-code` → `ai-pipeline-refactor` → `ai-pipeline-quality-gate`.
7. `ai-pipeline-rgr-orchestrator` closes run as `done` (PASS) or `failed` (FAIL/WARN); preserves worktree.

## Required stage evidence
Every stage records in `handoff.md`:
- `files_read`, `patterns_searched`, `reuse_decisions`
- `checkpoints` (incremental verification)
- `self_check` block

Missing any = automatic FAIL at quality gate.

## Required docs
Use `docs/agent/templates/` for canonical run-document structure.
Use `docs/agent/learnings.md` as the single shared learnings register (tag-filtered per story).

## Failure handling
- Halt immediately; write `error-report.md`; preserve worktree.
- One retry max for transient tooling failures only.
- Never retry on assertion failures, compile errors, self-check gaps, security or contract violations.
- See orchestrator `Resume Policy` for recovering from mid-run crashes.
