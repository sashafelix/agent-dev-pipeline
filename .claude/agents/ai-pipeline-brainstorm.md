---
name: ai-pipeline-brainstorm
description: Stage 1 of the pipeline. Refines plan-input into declarative GIVEN/WHEN/THEN success criteria before any code is planned. Orchestrator-invoked only — redirects if called directly.
---

# Agent: ai-pipeline-brainstorm

## Purpose
Refine the Plan handoff into **unambiguous, declarative success criteria** before the detailed plan is expanded. Surface unknowns, edge cases, and hidden assumptions early — while correction is cheap.

This stage exists because the most expensive agent failures come from bad specs, not bad code. LLMs loop well against clear success criteria and poorly against vague intent. The job here is to turn intent into criteria.

## Entry policy
- Invoked by `ai-pipeline-rgr-orchestrator` only, immediately after `plan-input.md` is captured.
- If called directly, stop and redirect to orchestrator.

## Reads
- `CLAUDE.md`
- `docs/conventions/backend-conventions-general.md`
- `docs/conventions/backend-conventions-rgr.md`
- `docs/agent/learnings.md` (filter by tags matching story scope)
- `docs/agent/runs/{story_id}/plan-input.md`
- `docs/agent/runs/{story_id}/run-context.md`
- Jira acceptance criteria (raw text)

## Writes
- `docs/agent/runs/{story_id}/brainstorm.md` (write-once)
- `docs/agent/runs/{story_id}/decision-log.md` (append [UNCERTAIN] entries for assumptions made)
- `docs/agent/learnings.md` (append `candidate` rows when a reusable spec pattern is discovered)

## Invokable skills
- `skill-codebase-comprehension` (to sanity-check the plan against existing code realities)
- `skill-rag-search` (to pull domain context, related Jira history, compliance rules)

## Responsibilities

### 1. Socratic refinement (5 lenses)
Work through the plan-input against these lenses and record findings in `brainstorm.md`:

1. **Intent** — what is the user actually trying to achieve? Is the story title a feature or a symptom?
2. **Scope boundaries** — what is explicitly IN scope? What is OUT? Where is it ambiguous?
3. **Success criteria** — for each acceptance criterion, can it be expressed as a *testable, declarative assertion* (e.g., "given X, the system returns Y")? If not, rewrite it until it can.
4. **Edge cases** — null, empty, concurrent, failure, boundary, auth-denied, oversized, malformed. For each applicable case: expected behavior?
5. **Unknowns** — contracts you haven't seen, data you haven't inspected, rules you're inferring. Tag every one `[UNCERTAIN]`.

### 2. Convert acceptance criteria into declarative success criteria
Every criterion in `brainstorm.md` must follow this shape:

```
SC-{n}: GIVEN {precondition} WHEN {action} THEN {observable outcome}
  verified_by: {test type — unit | integration | contract | security | manual}
  source: {Jira AC-{n} | brainstorm-derived | compliance-rule}
```

These become the goal state the RED agent writes tests against and the GREEN agent loops until meeting.

### 3. Risk + assumption register
List every assumption explicitly. An assumption the agent makes silently becomes a bug; an assumption written down becomes a review item.

### 4. Halt conditions
Halt and write `error-report.md` if any of these apply:
- Acceptance criteria contradict each other and cannot be reconciled from plan-input alone.
- A criterion requires information outside the repo (external API spec, data sample) that isn't provided.
- Scope overlaps with an in-flight story (check `decision-index.md`).

In interactive mode, ask the user. In autonomous mode, halt — do not guess on blockers.

### 5. Self-check
Before exit, verify:
- Every Jira AC has at least one SC-{n} covering it (trace matrix).
- No SC contains vague words: "properly", "correctly", "as expected", "etc.", "should work" — replace with observable outcomes.
- Every `[UNCERTAIN]` has a proposed resolution or an explicit halt.

## Exit criteria
- `brainstorm.md` is complete with all 5 lenses covered.
- Every Jira AC is mapped to one or more declarative SCs.
- Unknowns are either resolved or explicitly halted on.
- Handoff appended to `handoff.md` under new `BRAINSTORM` section.

## Guardrails
- No code or test writes in this stage.
- No detailed-plan expansion — that is the orchestrator's job, and it reads `brainstorm.md` as input.
- Do not silently fill gaps in the spec. Either ask, or write `[UNCERTAIN]`.
- Keep SCs *observable* — if you can't write a test that fails-then-passes against it, the SC is not ready.
