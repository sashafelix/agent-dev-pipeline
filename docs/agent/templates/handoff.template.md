# Handoff

story_id: <story-id>

Append-only. Each stage appends its own section; never overwrite a previous stage.

## BRAINSTORM
- agent: ai-pipeline-brainstorm
- timestamp:
- files_read:
  -
- patterns_searched: (what you grepped/globbed for and what you found)
  -
- sc_count: N (number of declarative success criteria produced)
- uncertain_count: N (number of [UNCERTAIN] items in decision-log)
- halt_conditions_triggered: none | [list]
- self_check:
  - [ ] Every input item mapped to at least one SC
  - [ ] No vague wording in SCs
  - [ ] All [UNCERTAIN] items have resolution plan or explicit halt
  - [ ] SCs are observable (testable)
- next_stage: red_test

## RED
- agent: ai-pipeline-red-test
- timestamp:
- files_read: (production + test files read during comprehension)
  -
- patterns_searched: (existing test patterns, naming conventions, fixtures found)
  -
- reuse_decisions: (existing test utilities / builders / base classes reused — list them)
  -
- risks: (conflicts between brainstorm SCs and existing architecture)
  -
- tests_added:
  - `<test-id>` → covers SC-{n} → fails with: `<failure message>`
- trace_matrix:
  | SC | Tests |
  | --- | --- |
  | SC-1 | |
- checkpoints: (incremental verification of test writes)
  - ✓ R1: added <test> → fails with expected business reason
- self_check:
  - [ ] Every SC has at least one failing test
  - [ ] Every test maps to an SC
  - [ ] Tests fail for intended business reason, not scaffold/compile errors
  - [ ] No production logic hidden in test utilities
  - [ ] Tests follow the stack's naming convention (record the convention in decision-log)
  - [ ] Searched for existing test patterns before writing new
  - [ ] No wall-clock, network, or ordering-by-accident dependence
- next_stage: green_code

## GREEN
- agent: ai-pipeline-green-code
- timestamp:
- files_read:
  -
- patterns_searched: (existing services, mappers, components, utilities searched for)
  -
- reuse_decisions: (existing utilities reused — list them; if none applied, say "searched, none applicable")
  -
- risks: (divergences from existing architecture flagged for review)
  -
- changes:
  - `<file>` — <what changed>
- checkpoints: (build + test after each micro-task)
  - ✓ G1: <file> builds
  - ✓ G3: <test-id> now passes
- test_runner_summary:
  - <build/test command> → N tests, N passed, 0 failed
- self_check:
  - [ ] Every RED test passes
  - [ ] No previously-passing test now fails
  - [ ] No code added that isn't exercised by a test
  - [ ] Reused existing utilities where available
  - [ ] No new abstraction without 3+ callers (Rule of Three)
  - [ ] No file in changed set exceeds 300 LOC (or split is justified)
  - [ ] No dead code, TODOs, or commented-out blocks
  - [ ] No hardcoded secrets, URLs, or env-specific values
  - [ ] All [UNCERTAIN] items resolved or still flagged
- next_stage: refactor

## REFACTOR
- agent: ai-pipeline-refactor
- timestamp:
- files_read:
  -
- patterns_searched: (duplication, dead code, complexity hotspots found)
  -
- risks: (refactors considered but deferred as risky)
  -
- improvements:
  - `<file>` — <what was cleaned up>
- checkpoints: (build + test after each refactor step)
  - ✓ F1: extracted <thing> → all tests still green
- test_runner_summary:
  - <build/test command> → N tests, N passed, 0 failed
- self_check:
  - [ ] Every test passing at end of GREEN still passes
  - [ ] No test was modified to accommodate refactored code
  - [ ] No feature, contract, or API addition introduced
  - [ ] No new abstraction without 3+ callers
  - [ ] No file exceeds 300 LOC (or split justified)
  - [ ] No dead code or commented-out blocks remain
  - [ ] Changes match existing module patterns
- next_stage: quality_gate

## VERIFY
- agent: ai-pipeline-quality-gate
- timestamp:
- verdict: PASS | FAIL | WARN
- evidence_matrix_complete: y/n
- blockers: none | [list]
- warn_justifications: none | [list]
- next_stage: done | failed
