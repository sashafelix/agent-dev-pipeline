# AGENTS.md

Canonical source of truth for agent and skill operation in `agent-dev-pipeline`.

The pipeline is **stack-agnostic**. A unit of work may be a Jira story, a feature description, a user request, or a RAG-derived task. The target stack may be backend, frontend, mobile, infra, or any mix — declared in `run-context.md > stack`.

## Design Principles

1. **Task-first delivery**
   - One unit of work at a time, in deployable slices.
   - "Unit of work" = Jira story **or** feature spec **or** user request **or** RAG-derived task (`input_source` in plan-input).
   - Scope (`in` / `out`) made explicit in `brainstorm.md` before coding.

2. **Spec refinement before planning**
   - Every input intent point (Jira AC, feature bullet, request line, RAG finding) becomes a declarative GIVEN/WHEN/THEN success criterion.
   - Ambiguity is killed at brainstorm, where correction is cheap. Silent assumptions are bugs.

3. **Deterministic TDD+ flow**
   - `BRAINSTORM → RED → GREEN → REFACTOR → VERIFY`.
   - No skipping. Each stage has evidence: comprehension, self-check, checkpoints.

4. **Tests as executable specification**
   - RED tests are the goal state. GREEN loops until they pass. LLMs loop well against clear criteria.

5. **Small autonomous core, reusable skills**
   - Agents own lifecycle and accountability.
   - Skills are composable capabilities invoked by stage agents.

6. **Explicit handoff over hidden context**
   - Every stage writes comprehension evidence, self-check, and checkpoints to `handoff.md`.
   - Next stage reads handoff + run context, not assumptions.

7. **Operational memory as a product asset**
   - `learnings.md` is a single, tag-filtered cross-story register.
   - Agents filter by `scope_tags` matching the story; reading everything is noise.

8. **Auditability and safety**
   - Append-only decision log; worktree-isolated runs; quality gate is a hard stop.

9. **Comprehension before action**
   - Read before write: understand existing code before modifying it.
   - Search before creating: reuse existing patterns over reinventing.
   - Verify incrementally: compile and test after each logical unit.
   - Flag uncertainty explicitly; never silently guess.

10. **Rule of Three**
    - No new abstraction without 3+ concrete callers. Inline premature abstractions.

## Why This Architecture

### Why these agents
- Natural ownership boundaries: spec refinement, failing tests, minimal implementation, safe cleanup, final quality decision.
- A single orchestrator prevents direct stage skipping and keeps run state coherent.
- The architecture maps directly to the non-negotiables and merge gates.

### Why a brainstorm stage
- The most expensive agent failures come from bad specs, not bad code.
- Converting vague intent (Jira AC, free-form request, RAG finding) into declarative SCs eliminates a class of errors no amount of code review catches.

### Why handoff documents
- Handoffs make intent, comprehension, and evidence visible between stages.
- Self-check blocks make discipline observable — quality gate fails runs where self-checks are absent.
- Review artifacts for PR and release traceability.

### Why worktree isolation
- Stories run in `.agent-runs/{story_id}` on branch `story/{story_id}`.
- Concurrent work does not collide; main checkout is never in a mid-stage state.
- The worktree is preserved on failure for forensic inspection.

### Why a learnings register
- Repeated setup/tooling decisions are learned once and reused — with tag filtering to stay scalable.
- Lifecycle (`candidate` / `active` / `deprecated` / `conflicted`) lets quality gate curate trust.

## Operating Model

### Canonical Paths
- Sub-agent definitions: `.claude/agents/**`. Skill reference docs: `docs/skills/**`.
- Runtime docs:
  - `docs/agent/current-run.md`
  - `docs/agent/runs/{story_id}/...`
  - `docs/agent/decision-index.md`
  - `docs/agent/learnings.md`
- Worktree: `.agent-runs/{story_id}` on branch `story/{story_id}`.

### Stage Order
1. `ai-pipeline-rgr-orchestrator` — setup + worktree
2. `ai-pipeline-brainstorm` — SC refinement
3. Plan expansion (orchestrator writes `detailed-plan.md` from brainstorm)
4. `ai-pipeline-red-test` — failing tests
5. `ai-pipeline-green-code` — minimal code
6. `ai-pipeline-refactor` — cleanup without behavior drift
7. `ai-pipeline-quality-gate` — verdict
8. `ai-pipeline-rgr-orchestrator` — close run as `done` or `failed`

### Entry Rule
- Start from Plan output.
- Invoke only `ai-pipeline-rgr-orchestrator` directly.
- Stage agents are orchestrator-invoked only; they redirect if called directly.

## Agent Catalog

### `ai-pipeline-rgr-orchestrator`
- Purpose: own stage transitions, worktree isolation, failure handling.
- Reads: core instructions, conventions, plan inputs, templates, learnings (tag-filtered), run context, decision-index, runtime-doc-contract.
- Writes: `current-run`, `run-context`, `plan-input`, `brainstorm` (lock only), `detailed-plan`, `handoff` (final status), `quality-gates` (close), `error-report`, learnings (operational level).
- Guardrails: no stage skipping; halt on failure; one retry max for transient tooling; preserve worktree on failure.

### `ai-pipeline-brainstorm`
- Purpose: refine input intent (Jira ACs, feature bullets, free-form request, RAG findings) into declarative success criteria; surface unknowns and edge cases.
- Reads: plan-input, conventions, learnings (tag-filtered), source intent artifact, RAG (sources selected by stack + input type).
- Writes: `brainstorm.md` (write-once), `handoff.md > BRAINSTORM`, `decision-log` ([UNCERTAIN] entries), learnings (`candidate`).
- Guardrails: no code writes; halt on unresolved blockers; every input intent point mapped to at least one SC.

### `ai-pipeline-red-test`
- Purpose: encode every SC as a failing test, idiomatic to the target stack.
- Reads: brainstorm, detailed-plan RED, testing conventions for the stack, learnings (tag-filtered).
- Writes: test files under `{project_root}` in the stack's canonical test location, handoff (RED), decision-log, learnings (`candidate`).
- Guardrails: no production code in tests; every test maps to an SC; failure reason matches business intent.

### `ai-pipeline-green-code`
- Purpose: minimal production code to make every RED test pass.
- Reads: brainstorm, detailed-plan GREEN, RED handoff, conventions for the stack, learnings (tag-filtered).
- Writes: production files under `{project_root}` (plus migrations if persistence changes), handoff (GREEN), decision-log, learnings (`candidate`).
- Guardrails: no scope creep, no speculative abstractions (Rule of Three), no contract breaks without approval; incremental verification mandatory.

### `ai-pipeline-refactor`
- Purpose: improve maintainability while preserving behavior.
- Reads: REFACTOR plan, GREEN handoff, conventions, learnings (tag-filtered).
- Writes: scoped source/tests, handoff (REFACTOR), decision-log, learnings (`candidate`).
- Guardrails: no feature additions; no novel patterns without justification; all tests stay green; incremental verification mandatory.

### `ai-pipeline-quality-gate`
- Purpose: final VERIFY verdict with hard-FAIL checklist.
- Reads: all prior docs, conventions, learnings (all active entries).
- Writes: `quality-gates`, handoff (VERIFY), decision-log, learnings (status curation), decision-index (via `skill-decision-index`).
- Guardrails: no PASS with missing mandatory evidence or any hard-FAIL item triggered; blockers explicit.

## Skill Catalog

See `docs/skills/README.md` for the authoritative list. Summary:

### Stack-neutral (called on any run when relevant)
- `skill-codebase-comprehension` — systematic read-and-understand before writes.
- `skill-project-scaffold` — bootstrap module/project structure (stack-agnostic with mapping table).
- `skill-api-service` — HTTP/RPC surface patterns.
- `skill-security` — auth/authz controls and security tests.
- `skill-integration` — external adapter resilience patterns.
- `skill-validation` — input validation at boundaries.
- `skill-exception-handling` — centralized error handling.
- `skill-test-maintenance` — deterministic, readable tests.
- `skill-contract-guard` — API/DTO/DB compatibility checks.
- `skill-observability` — logs/metrics/tracing.
- `skill-devops` — CI/CD + runtime config changes.
- `skill-compliance` — traceable release/control evidence.
- `skill-decision-index` — compact update of `docs/agent/decision-index.md`.
- `skill-rag-search` — query RAG knowledge base.

### Stack-specific (invoke only when the stack matches)
- `skill-database` — SQL migrations + safety matrix *(stacks with a relational persistence layer)*.
- `skill-entity-mapping` — entity / repository / DTO / mapper boundaries *(ORM-backed backends)*.
- `skill-transaction-policy` — transactional boundaries *(backends with DB writes)*.
- `skill-java-cleanup` — readability/structure refactors *(Java-style; principles generalize)*.

### Conditional skills
- `skill-scheduling` — scheduled background jobs / cron / client polling.
- `skill-caching` *(future)*.
- `skill-xml-jaxb` *(future)*.

## Runtime Document Rules

See `docs/agent/runtime-doc-contract.yaml` for the formal spec.

### Replace-in-place
- `docs/agent/current-run.md`
- `docs/agent/runs/{story_id}/run-context.md`
- `docs/agent/runs/{story_id}/detailed-plan.md` (pre-RED only; locked once RED starts)
- `docs/agent/runs/{story_id}/quality-gates.md`
- `docs/agent/learnings.md` (curated updates)

### Write-once
- `docs/agent/runs/{story_id}/plan-input.md`
- `docs/agent/runs/{story_id}/brainstorm.md`

### Append-only
- `docs/agent/runs/{story_id}/handoff.md`
- `docs/agent/runs/{story_id}/decision-log.md`

*(Exception: orchestrator may delete a partial stage section during an explicit resume — see Orchestrator Resume Policy. Logged in decision-log.)*

### Create-on-failure
- `docs/agent/runs/{story_id}/error-report.md`

## Docs Ownership

- `ai-pipeline-rgr-orchestrator`: `current-run.md`, `run-context.md`, `plan-input.md`, `detailed-plan.md`, `error-report.md`, final `handoff.md` status.
- Only `ai-pipeline-rgr-orchestrator` updates `run-context.current_stage`.
- `ai-pipeline-brainstorm`: `brainstorm.md` (write-once), `handoff.md > BRAINSTORM`, decision-log.
- Stage agents (RED/GREEN/REFACTOR): their stage's `handoff.md` section + decision-log + candidate learnings.
- `ai-pipeline-quality-gate`: `quality-gates.md`, `handoff.md > VERIFY`, decision-log, learnings curation, decision-index (via skill).
- `docs/agent/decision-index.md` is updated by `skill-decision-index`.

## Learnings Register Lifecycle

File: `docs/agent/learnings.md`

- `candidate`: newly observed reusable learning.
- `active`: validated by at least one run and currently enforced.
- `deprecated`: superseded by a better rule.
- `conflicted`: contradicts an existing `active` entry under the same `conflict_key`; needs operator resolution.

Agents filter by `scope_tags` matching the story. Reading unfiltered is noise.

Quality gate curates status on each run.

## How To Use (Operator Guide)

1. **Prepare input**
   - Provide an identifier (Jira key, feature slug, request slug) + the intent payload (ACs, feature bullets, free-form request, or a RAG query that pulls relevant docs).
   - Declare the target `stack` and `project_root`.
   - Include plan handoff text from `Plan` agent.

2. **Start run**
   - Invoke `ai-pipeline-rgr-orchestrator` only.
   - Orchestrator creates the worktree + run folder, writes `plan-input.md`.

3. **Observe stage progress**
   - Check `current-run.md` and `handoff.md` after each stage.
   - On failure, inspect `error-report.md` for stage-specific recovery.
   - Worktree is preserved on failure for inspection.

4. **Review gate output**
   - `quality-gates.md` is the go/no-go artifact.
   - Verify decision-index and learnings updates are present.

5. **PR evidence checklist**
   - `brainstorm.md` with SC trace matrix.
   - RED evidence (failing tests per SC).
   - GREEN evidence (tests passing, checkpoints recorded).
   - REFACTOR evidence (no behavior drift, improvements listed).
   - VERIFY verdict (PASS/FAIL/WARN with evidence).

## Decision and Governance Notes

- One agent owns one change set at a time.
- Cross-boundary work requires explicit handoff notes.
- No breaking API/DB contract change without explicit approval in decision-log.
- Coverage must not regress on touched modules (target 80%+).
- Worktrees are preserved on failure; cleanup is operator-driven.
