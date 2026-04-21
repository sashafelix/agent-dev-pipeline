# CLAUDE.md — agent-dev-pipeline

Operating guide for Claude Code in this repository. Auto-loaded every session.

## Scope
- Applies to all agent-dev-pipeline work unless a closer instruction file overrides it.
- **Stack-agnostic.** Target may be backend, frontend, mobile, infra, or polyglot.
- Deliver in small, deployable slices. A unit of work is any of: Jira story, feature description, free-form user request, or RAG-derived task (declared as `input_source` in `plan-input.md`).

## Entry rule
- Start from a Plan (use Claude Code plan mode, or the `Plan` sub-agent).
- Then invoke the `ai-pipeline-rgr-orchestrator` sub-agent — it owns the run end-to-end.
- Stage sub-agents (`ai-pipeline-brainstorm`, `ai-pipeline-red-test`, `ai-pipeline-green-code`, `ai-pipeline-refactor`, `ai-pipeline-quality-gate`) are orchestrator-invoked only. Calling them directly will redirect to the orchestrator.

## Non-Negotiables

- **Deterministic flow**: BRAINSTORM → RED → GREEN → REFACTOR → VERIFY. No skipping.
- **Declarative success criteria**: every input intent point (Jira AC, feature bullet, request line, RAG finding) is converted into a GIVEN/WHEN/THEN success criterion in `brainstorm.md` before any code is planned.
- **Tests as goal state**: RED tests are the machine-checkable definition of done. GREEN loops until they pass. Nothing ships without a test encoding it.
- **Read before write**: every stage agent reads existing code and traces the call chain before modifying files. Evidence appears in `handoff.md`.
- **Search before creating**: grep/glob the codebase for existing patterns, utilities, and similar implementations before writing new code. Reuse over reinvent. Evidence appears in `handoff.md > reuse_decisions`.
- **Verify incrementally**: compile and run affected tests after *each* micro-task, not only at the end. Checkpoints appear in `handoff.md > checkpoints`.
- **Self-check before exit**: every stage agent runs a self-check block and records the result in `handoff.md`. No stage exits silently.
- **Flag uncertainty**: any silent assumption becomes a bug. Tag `[UNCERTAIN]` in `decision-log.md` with assumption + rationale.
- **Rule of Three**: no new abstraction (interface, base class, generic helper) without 3+ concrete callers. Inline speculative abstractions.
- **Scope discipline**: no unrelated refactors, no "while I'm here" cleanups. One change set, one story.
- **No breaking API/DB contracts** without explicit alignment in decision-log.
- **Worktree isolation**: the orchestrator runs every story in its own git worktree under `.agent-runs/{story_id}`. The main checkout is untouched until human-driven merge.

## PR Ownership
- Final reviewer/approver is the project owner.
- Agents prepare PR-ready changes only (no self-approval/auto-merge).

## PR Must Show
- BRAINSTORM evidence (brainstorm.md with SCs + trace matrix).
- RED evidence (failing tests first, one per SC).
- GREEN evidence (tests passing after minimal implementation).
- REFACTOR note (what improved; behavior unchanged; all tests green).
- VERIFY verdict (quality-gates.md PASS/FAIL/WARN + evidence matrix).

## Merge Gates
- All tests pass.
- Coverage does not regress on touched modules (target 80%+).
- No blocker/critical findings from quality-gate hard-FAIL checklist.
- Security-relevant changes reviewed via `skill-compliance`.
- No unresolved correctness-blocking `[UNCERTAIN]` entries.

## Prompt Contract (All Agents)
Include:
- Context (identifier — Jira key / feature slug / request slug; `input_source`; `stack`; `project_root`; scope boundaries from brainstorm.md)
- Declarative success criteria (SC-{n} list)
- Constraints (conventions matching the stack, security, performance, applicable learnings filtered by `scope_tags`)
- Inputs (contracts/schemas/examples)
- Expected outputs (code/tests/migrations/docs — idiomatic to the stack)
- Done evidence (stage-specific: comprehension + self-check + checkpoints)

## Agent Boundaries
- `Plan`: plan/order/scope and dependencies.
- `ai-pipeline-rgr-orchestrator`: owns stage transitions and worktree.
- `ai-pipeline-brainstorm`: spec refinement into declarative SCs.
- `ai-pipeline-red-test`, `ai-pipeline-green-code`, `ai-pipeline-refactor`, `ai-pipeline-quality-gate`: stage execution.
- `devops`: pipelines/deploy/runtime config (via `skill-devops`).
- `compliance`: evidence/controls/release docs (via `skill-compliance`).

Rules:
- One agent owns one change set at a time.
- Cross-boundary work requires explicit handoff notes.

## Collaboration
- API-first for shared backend/frontend flows: backend provides contract + sample payloads; frontend can start with mocks (MSW, fakes) and switch to the real API.
- When the target is polyglot (both backend and frontend in one unit of work), split SCs by stack and ensure the contract appears as its own SC row.
- Escalate blockers early — in autonomous mode, halt and write `error-report.md`.

## Definition of Done
- Every input intent point traced to at least one passing test via brainstorm SCs.
- Handoff evidence present for every stage (comprehension + self-check + checkpoints).
- Merge gates pass.
- Required contract/config/doc updates included.
- Change is deployable without hidden manual steps.

## Learnings Register
- Single shared file: `docs/agent/learnings.md`.
- Tag every entry with `scope_tags` from the vocabulary defined in the register.
- Agents **filter by tags** matching the current story — reading the whole register is noise.
- Stage agents append `candidate` rows with evidence; quality gate curates to `active`/`deprecated`/`conflicted`.

## Reference
- Design principles and agent/skill catalog: `AGENTS.md`.
- Runtime-document contract: `docs/agent/runtime-doc-contract.yaml`.
- Sub-agent definitions: `.claude/agents/**`.
- Skill reference docs: `docs/skills/**`.
- Stack conventions: `docs/conventions/**`.
