# Detailed Plan

story_id: <story-id>
owner_agent: ai-pipeline-rgr-orchestrator
status: draft | locked
derived_from: docs/agent/runs/<story-id>/brainstorm.md

## How to read this
Each stage is broken into **numbered micro-tasks**. Each micro-task is:
- Small enough to verify in isolation (target: one class/component/module, one method/hook, one migration).
- Annotated with exact **file paths**, target **SC-{n}** mappings, and a **verification step**.
- Executed in order; the stage agent checkpoints each one in `handoff.md`.

Keep micro-tasks at 2–10 minutes of agent work each. If a task is bigger, split it.

File paths are **stack-agnostic** — use paths that match the target `project_root` and stack (e.g., `src/services/...` for a Node service, `src/main/java/...` for a Spring app, `app/components/...` for a Next.js app).

---

## RED — failing tests that encode every SC
Input: `brainstorm.md` success criteria SC-1..SC-n.
Output: failing tests that will drive GREEN.

| # | Task | Files | Covers SCs | Verify |
| --- | --- | --- | --- | --- |
| R1 | Add test for SC-1 happy path | `<test-path>` | SC-1 | Run test → fails with <expected failure message> |
| R2 | Add test for SC-2 (edge case: null input) | `<test-path>` | SC-2 | Run test → fails with <expected> |
| R3 | Add contract/security/e2e test as applicable | `<test-path>` | SC-3 | Run test → fails |

**Trace matrix**: every SC from brainstorm.md must appear in at least one row.

| SC | Tests |
| --- | --- |
| SC-1 | R1 |
| SC-2 | R2 |
| SC-3 | R3 |

---

## GREEN — minimal code to make every RED test pass
Input: failing RED tests.
Output: smallest production code that turns each red to green.

| # | Task | Files | Turns green | Verify |
| --- | --- | --- | --- | --- |
| G1 | Create <module / component / entity> | `<src-path>` | (scaffold for R1-R3) | Module builds |
| G2 | Add persistence / state layer if needed | `<path>` | (scaffold for R1) | Build + smoke test clean |
| G3 | Add core logic for SC-1 | `<path>` | R1 | R1 passes |
| G4 | Add edge-case handling for SC-2 | `<path>` | R2 | R2 passes |
| G5 | Add contract/auth/etc. for SC-3 | `<path>` | R3 | R3 passes |

**Contract compatibility**: list the API / data / message touchpoints and confirm non-breaking.

| Contract | Change | Breaking? | Mitigation |
| --- | --- | --- | --- |
| `<endpoint / schema / event>` | new / modified | no / yes | — |

---

## REFACTOR — preserve behavior, improve quality
Input: all RED tests green, GREEN code in place.
Output: cleaner code, same behavior.

| # | Task | Files | Improvement | Verify |
| --- | --- | --- | --- | --- |
| F1 | Extract <thing> from <container> | `<paths>` | SRP, remove duplication | All tests still pass |
| F2 | Remove dead commented-out block in <file> | `<path>` | dead-code cleanup | All tests still pass |
| F3 | Rename <old> → <new> | `<path>` | readable naming | All tests still pass |

**Refactor safety**: for each task, confirm it is a pure refactor.

| # | Changes observable behavior? | Changes public API? | Changes tests? |
| --- | --- | --- | --- |
| F1 | no | no | no |
| F2 | no | no | no |
| F3 | no | no (private) | no |

---

## VERIFY — quality gate evidence checklist
Input: all stages complete.
Output: quality-gates.md verdict.

| # | Check | Evidence expected |
| --- | --- | --- |
| V1 | All SCs mapped to passing tests | Trace matrix from brainstorm + handoff |
| V2 | Coverage ≥ threshold on touched modules | Coverage report path (format depends on stack) |
| V3 | Contract compatibility | `skill-contract-guard` output in handoff |
| V4 | Security evidence | positive + negative auth tests listed (if applicable) |
| V5 | No file > 300 LOC in changed set | cleanup skill output |
| V6 | No dead code / TODO in changed set | cleanup skill output |
| V7 | Compliance evidence block filled | `skill-compliance` output (if applicable) |
| V8 | Decision log entries present for non-trivial choices | decision-log.md review |

Every row must be ✓ or have explicit justification in decision-log.
