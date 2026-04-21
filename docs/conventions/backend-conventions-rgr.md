# Conventions — BRAINSTORM + RGR Stage Flow

Applies to: `ai-pipeline-rgr-orchestrator`, `ai-pipeline-brainstorm`, `ai-pipeline-red-test`, `ai-pipeline-green-code`, `ai-pipeline-refactor`, `ai-pipeline-quality-gate`.

**Stack-agnostic.** This file defines the *flow* and *evidence requirements* that every run must follow regardless of target stack (backend / frontend / mobile / infra / polyglot). Stack-specific idiom (test naming, build commands, file layout) belongs in the stack's own convention file under `docs/conventions/`.

## Orchestration
- Execute strictly in order: **BRAINSTORM → RED → GREEN → REFACTOR → QUALITY_GATE**.
- Halt immediately on failure; write `error-report.md`; preserve the worktree.
- Allow **max 1 retry** for transient tooling failures only (network, container startup). Never retry assertion failures, build/compile errors, or incomplete self-checks.
- Every run is isolated in `.agent-runs/{story_id}` (git worktree on branch `story/{story_id}`). `{story_id}` is whatever identifier the input supplied (Jira key, feature slug, request slug, RAG-derived task id).

## BRAINSTORM Stage (`ai-pipeline-brainstorm`)
- Refine every input intent point (Jira AC, feature bullet, request line, RAG finding) into at least one declarative success criterion: `SC-{n}: GIVEN ... WHEN ... THEN ...`.
- Walk the 5 lenses: Intent, Scope, Success criteria, Edge cases, Unknowns.
- Every `[UNCERTAIN]` has either a resolution plan or an explicit halt. No silent assumptions.
- Output: `brainstorm.md` (write-once). Locked before RED starts.

## RED Stage (`ai-pipeline-red-test`)
- Write failing tests directly from `brainstorm.md` SCs in the stack's test framework (JUnit / Vitest / PyTest / Go `testing` / …).
- Every SC has at least one test; every test maps to an SC.
- Do not implement production behavior.
- Each test fails for the intended business reason (not scaffolding / compile / import errors).
- Trace matrix required in `handoff.md > RED`.

## GREEN Stage (`ai-pipeline-green-code`)
- Implement the minimum production code that turns every RED test green, idiomatic to the target stack.
- No scope creep, no speculative features, no abstraction without 3+ callers (Rule of Three).
- Incremental verification: build/typecheck + run tests after each micro-task from `detailed-plan.md`.

## REFACTOR Stage (`ai-pipeline-refactor`)
- Improve readability, structure, and hygiene only.
- No behavior changes; no test modifications that change assertion intent.
- Delete dead code, remove commented-out blocks, split files over 300 LOC when natural.
- Incremental verification: build + run tests after every refactor step.

## QUALITY_GATE Stage (`ai-pipeline-quality-gate`)
- Verify SC → test trace is complete.
- Run hard-FAIL checklist (dead code, premature abstraction, file size, missing self-checks, hardcoded secrets).
- Produce explicit PASS/FAIL/WARN verdict with evidence for every claim.

## Stage Evidence (required in `handoff.md` for every stage)
- **files_read** — list of files read during comprehension
- **patterns_searched** — what was grepped/globbed and what was found
- **reuse_decisions** — existing utilities/patterns reused (or "searched, none applicable")
- **checkpoints** — incremental verification results per micro-task
- **self_check** — explicit checklist result (every box ticked or `[UNCERTAIN]` logged)

Missing any of these = automatic FAIL at quality gate.

## Comprehension Before Action
- **Read before write**: every stage agent must read all files it intends to modify before making changes. Record in `handoff.md > files_read`.
- **Search before creating**: grep/glob the codebase for existing patterns, utilities, and similar implementations. Record in `handoff.md > patterns_searched` and `reuse_decisions`.
- **Match neighbors**: follow the style and conventions of surrounding code. Do not introduce novel patterns without decision-log justification.

## Uncertainty Protocol
- If you are unsure about a design choice, business rule, or edge case:
  1. Flag it explicitly in `decision-log.md` with `[UNCERTAIN]` tag.
  2. State what you assumed and why.
  3. Provide the evidence that would resolve it (which file, which test, which contract).
  4. Mark it for review in quality gate.
- Never silently guess — wrong assumptions compound across stages.

## Incremental Verification
- After each micro-task in `detailed-plan.md`, compile and run affected tests.
- Do not batch all changes and test only at the end.
- Record a checkpoint in `handoff.md > checkpoints` (e.g., `✓ G3: OrderService.create — RED test X now passes`).
- On unexpected failure: STOP and diagnose before continuing. Do not plow forward.

## Self-Check Block (required at stage exit)
Each stage agent has its own checklist in its agent file. Every box must be ✓, or the unchecked item must have an `[UNCERTAIN]` entry in decision-log. A missing or empty self-check block is an automatic FAIL.

## Rule of Three
- No new interface, base class, or generic helper unless there are **3+ concrete callers**.
- Speculative "we'll need this later" abstractions are deleted. Future needs are future stories.

## File Size
- Non-test, non-generated files should stay under 300 LOC.
- Over 300 LOC: split if natural, or justify in decision-log.
- Methods should stay under 30 LOC or 3 nested levels without justification.

## Scope Discipline
- One task = one change set. No "while I'm here" refactors of unrelated code.
- Every file in the diff must tie back to an SC or a documented REFACTOR task.
- Out-of-scope changes require a separate task or an explicit approved scope expansion in decision-log.
