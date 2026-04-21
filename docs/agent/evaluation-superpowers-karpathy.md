# Agent & Skill Evaluation: Integrating Superpowers + Karpathy Principles

**Date:** 2026-04-20
**Scope:** Full review of the agent/skill architecture against [obra/superpowers](https://github.com/obra/superpowers) and [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) principles.
**Status:** **Implemented.** All HIGH and MED recommendations below have been applied. This document is retained as a historical rationale for why the current pipeline looks the way it does. See the *Implementation status* block after the Executive Summary for a per-recommendation map.

---

## 1. Executive Summary

The agent architecture is **well-structured** with clear stage ownership, deterministic TDD flow, and explicit handoffs. The original review found that several high-impact principles from both source repos were missing. The gap analysis and recommendations below have all been applied — the pipeline now codifies comprehension protocols, incremental verification, self-check blocks, Rule of Three, and the search-before-create mandate.

### Implementation status (snapshot)

| Recommendation | Status | Lives in |
| --- | --- | --- |
| 3.1 Comprehension Protocol on all stage agents | ✅ applied | `.claude/agents/ai-pipeline-red-test.md`, `.claude/agents/ai-pipeline-green-code.md`, `.claude/agents/ai-pipeline-refactor.md` |
| 3.2 Incremental Verification in GREEN & REFACTOR | ✅ applied | same agents — `checkpoints:` in handoff |
| 3.3 "Don't guess — search" mandate | ✅ applied | `CLAUDE.md` non-negotiables |
| 3.4 Self-Check block per stage | ✅ applied | each stage agent's `Self-Check` section; recorded in `handoff.md` |
| 3.5 Karpathy code-simplicity rules | ✅ applied | `backend-conventions-java-style.md` (Code Simplicity Rules); principles echoed in `CLAUDE.md` |
| 3.6 Quality-gate hard-FAIL checklist | ✅ applied | `.claude/agents/ai-pipeline-quality-gate.md` + `quality-gates.template.md` section 3 |
| 3.7 Uncertainty protocol in decision-log | ✅ applied | `backend-conventions-rgr.md` + `decision-log.template.md` `[UNCERTAIN]` section |
| 4.0 `skill-codebase-comprehension` | ✅ created | `docs/skills/skill-codebase-comprehension.md` |

Extensions added beyond the original review:
- **Brainstorm stage**: declarative SCs now gate planning and RED.
- **Worktree isolation**: every run lives in `.agent-runs/{story_id}` on `story/{story_id}`.
- **Learnings register with `scope_tags` + lifecycle**: candidate → active → deprecated/conflicted.
- **Stack-agnostic framing**: pipeline accepts Jira stories, feature descriptions, free-form requests, or RAG-derived tasks; target may be backend/frontend/mobile/infra/polyglot.

---

## 2. Principle Mapping & Gap Analysis

### 2.1 Superpowers Principles (obra/superpowers)

| Principle | Current Status | Gap | Priority |
|-----------|---------------|-----|----------|
| **Read before write** — always read existing code before modifying | Partially implied in conventions | Not enforced in agent instructions | 🔴 HIGH |
| **Verify after every change** — run tests/checks after each edit | Quality gate at end only; no per-edit verification | Missing incremental verification in GREEN/REFACTOR | 🔴 HIGH |
| **Understand before changing** — trace full call chain before edits | Not mentioned in any agent/skill | Missing comprehension step in GREEN agent | 🔴 HIGH |
| **Plan before executing** — break work into steps, state them, then execute | Covered well via detailed-plan.md | ✅ Strong | ✅ OK |
| **Check your work** — self-review before declaring done | Quality gate exists but stage agents don't self-check | Missing self-verification in RED/GREEN/REFACTOR | 🟡 MED |
| **Be explicit about uncertainty** — flag assumptions clearly | Decision-log exists for this | Partially covered; could be stronger | 🟡 MED |
| **Minimal changes** — smallest possible diff | GREEN agent says "minimum" but no explicit diff-size guardrail | Could add explicit single-responsibility-per-commit rule | 🟢 LOW |
| **Don't guess — search** — use tools to find facts, don't assume | RAG search available but not mandatory | Should mandate codebase search before writing new code | 🔴 HIGH |
| **One thing at a time** — don't mix concerns in a single change | Covered by story-first + scope boundaries | ✅ Strong | ✅ OK |
| **Preserve existing patterns** — match the style of surrounding code | Conventions exist but no explicit "match neighbors" rule | Add pattern-matching mandate to GREEN/REFACTOR | 🟡 MED |

### 2.2 Karpathy Principles (andrej-karpathy-skills)

| Principle | Current Status | Gap | Priority |
|-----------|---------------|-----|----------|
| **Write simple, boring code** — avoid cleverness, prefer readability | Java style conventions mention readability | Not explicit enough as a core mandate | 🟡 MED |
| **Avoid premature abstraction** — don't DRY until 3+ duplications | GREEN says "no speculative abstractions" | Good. Could strengthen with Rule of Three | 🟢 LOW |
| **Flat > nested** — reduce nesting, early returns | Java style mentions "return early" | ✅ Covered | ✅ OK |
| **Functions should do one thing** — SRP at function level | Mentioned but not enforced/checked | Add to quality-gate checklist | 🟡 MED |
| **Explicit > implicit** — no magic, clear data flow | GREEN says "prefer explicit code over magic" | ✅ Covered | ✅ OK |
| **Delete dead code aggressively** — no commented-out code | Not mentioned anywhere | Add to REFACTOR and java-cleanup skill | 🟡 MED |
| **Keep files small** — split when files grow too large | Not mentioned | Add file-size awareness to REFACTOR | 🟢 LOW |
| **Name things well** — names should explain intent | Java style says "naming explicit and domain-driven" | ✅ Covered | ✅ OK |
| **Write tests that test behavior, not implementation** — black-box tests | Testing style says "describe observable behavior" | ✅ Covered | ✅ OK |
| **Don't mock what you don't own** — use integration tests for boundaries | Not mentioned | Add to testing conventions | 🟡 MED |
| **Prefer composition over inheritance** — favor interfaces/delegation | Not mentioned | Add to java-style conventions | 🟡 MED |
| **Error handling is a feature** — explicit error paths | exception-handling skill exists | ✅ Covered | ✅ OK |
| **Log thoughtfully** — structured, actionable logs only | Observability skill exists, log sanitization required | ✅ Covered | ✅ OK |

---

## 3. Recommended Changes

### 3.1 Add "Comprehension Protocol" to all stage agents (HIGH)

Add to `.claude/agents/ai-pipeline-green-code.md`, `.claude/agents/ai-pipeline-refactor.md`, and `.claude/agents/ai-pipeline-red-test.md`:

```markdown
## Comprehension Protocol (before writing any code)
1. **Read** all files you intend to modify — never write blind.
2. **Trace** the call chain: controller → service → repository → entity for the feature area.
3. **Search** the codebase (`grep`/semantic search) for existing patterns that solve similar problems.
4. **Match** the style and patterns of neighboring code — don't introduce new conventions.
5. **State** your understanding in the decision-log before writing code.
```

### 3.2 Add "Incremental Verification" to GREEN and REFACTOR agents (HIGH)

Add to `.claude/agents/ai-pipeline-green-code.md` and `.claude/agents/ai-pipeline-refactor.md`:

```markdown
## Incremental Verification
- After each logical unit of change (e.g., one class, one method group), compile and run affected tests.
- Do not batch all changes and test only at the end.
- If a test fails unexpectedly, stop and diagnose before continuing.
- Record each verification checkpoint in handoff evidence.
```

### 3.3 Add "Don't Guess — Search" mandate (HIGH)

Add to `CLAUDE.md` under Non-Negotiables:

```markdown
- **Search before creating**: Before writing new code, search the codebase for existing implementations, utilities, or patterns that already solve the problem. Reuse over reinvent.
```

### 3.4 Add "Self-Check" step to each stage agent (MED)

Add to each stage agent's Responsibilities (before exit):

```markdown
- **Self-check**: Before declaring stage complete, re-read your own changes and verify they meet the detailed-plan tasks, follow conventions, and introduce no unintended side effects.
```

### 3.5 Strengthen java-style and java-cleanup with Karpathy principles (MED)

Add to `backend-conventions-java-style.md`:

```markdown
## Code Simplicity Rules
- Write simple, boring code. Clever code is a liability.
- Rule of Three: don't abstract until a pattern appears 3+ times.
- Prefer composition over inheritance; use interfaces and delegation.
- Delete dead code — no commented-out blocks, no unused imports, no orphaned methods.
- Keep files focused; split when a class exceeds ~300 lines or has >2 responsibilities.
- Don't mock what you don't own — for external boundaries, use integration tests or test containers.
```

### 3.6 Add to quality-gate mandatory checklist (MED)

Add to `.claude/agents/ai-pipeline-quality-gate.md` Mandatory Test Evidence Matrix:

```markdown
## Code Quality Checks
- [ ] No dead code or commented-out blocks in changed files
- [ ] Functions do one thing (SRP at method level)
- [ ] No premature abstractions introduced
- [ ] Existing codebase patterns followed (no novel conventions without decision-log justification)
- [ ] File sizes reasonable (<300 lines per class, excluding tests)
```

### 3.7 Add uncertainty flagging to decision-log convention (MED)

Add to `backend-conventions-rgr.md`:

```markdown
## Uncertainty Protocol
- If you are unsure about a design choice, business rule, or edge case:
  1. Flag it explicitly in `decision-log.md` with `[UNCERTAIN]` tag.
  2. State what you assumed and why.
  3. Mark it for review in quality gate.
- Never silently guess — wrong assumptions compound across stages.
```

---

## 4. New Skill Recommendation

### `skill-codebase-comprehension` (NEW)

```markdown
# Skill: skill-codebase-comprehension

## Purpose
Systematically read and understand existing code before making changes.

## When invoked
- At the start of GREEN and REFACTOR stages, before any file writes.

## Steps
1. Identify all files in the change scope from detailed-plan.
2. Read each file and its direct dependencies (imports, called services).
3. Search for similar patterns in the codebase (naming, structure, error handling).
4. Document findings: existing patterns to follow, utilities to reuse, anti-patterns to avoid.
5. Output a brief "comprehension summary" to decision-log.

## Guardrails
- Do not write any production code during comprehension.
- Flag any conflicts between plan and existing code.
```

---

## 5. Summary of Changes by File

| File | Change |
|------|--------|
| `CLAUDE.md` | Add "Search before creating" non-negotiable |
| `.claude/agents/ai-pipeline-red-test.md` | Add Comprehension Protocol + Self-Check |
| `.claude/agents/ai-pipeline-green-code.md` | Add Comprehension Protocol + Incremental Verification + Self-Check |
| `.claude/agents/ai-pipeline-refactor.md` | Add Comprehension Protocol + Incremental Verification + Self-Check |
| `.claude/agents/ai-pipeline-quality-gate.md` | Add Code Quality Checks to mandatory checklist |
| `docs/conventions/backend-conventions-java-style.md` | Add Code Simplicity Rules section |
| `docs/conventions/backend-conventions-rgr.md` | Add Uncertainty Protocol section |
| `docs/conventions/backend-conventions-testing-style.md` | Add "Don't mock what you don't own" rule |
| `AGENTS.md` | Add `skill-codebase-comprehension` to skill catalog, add Design Principle #7 |
| NEW: `docs/skills/skill-codebase-comprehension.md` | New skill definition |

---

## 6. Decision

**Resolved:** All HIGH and MED recommendations above were implemented. See the *Implementation status* block at the top of this document for the per-recommendation map to the live files.
