# AGENTS.md — Local RGR v1.3

Canonical role, profile and delegation model.

## Architecture

`PREPARE → BRAINSTORM → PLAN → ANALYZE → RED → GREEN → REFACTOR → VERIFY → CONVERGE`

The orchestrator owns state. Every invocation binds to one role contract, one immutable context manifest and one selected workflow profile.

## Profiles

- `small`: bounded low-risk work, compact budgets, one convergence attempt.
- `standard`: normal multi-file work, full regression/contract awareness, two attempts.
- `high-risk`: security, data, infrastructure, architecture or broad work; specialists and operator checkpoints required.

All profiles retain every mandatory stage. Profile selection is deterministic from immutable facts and may only be raised by operator minimum policy.

## Core roles

| Role | Stage | Story writes | Verdict authority |
|---|---|---:|---:|
| repository_analyst | PREPARE | No | No |
| specifier | BRAINSTORM | No | No |
| orchestrator/planner | PLAN/state | Artifacts only | No final verdict |
| consistency_analyst | ANALYZE | No | Findings only |
| test_author | RED | Tests only | No |
| implementer | GREEN | Bounded source/config/migrations | No |
| refactorer | REFACTOR | Bounded source/tests/config | No |
| independent_verifier | VERIFY | No | PASS/WARN/FAIL |
| convergence_reviewer | CONVERGE | No | Convergence decision |

## Specialist roles

- risk_reviewer
- threat_modeler
- migration_reviewer
- infrastructure_reviewer
- contract_reviewer
- accessibility_reviewer

Specialists are selected by `profile-resolution.json`. They are read-only, return typed reports and cannot transition stages, lower risk, modify implementation, approve merge/deployment or access production credentials.

## Delegation

- Only roles with explicit `may_delegate_to` entries may delegate.
- Delegated capabilities are the intersection of parent, child and context authority.
- A subagent cannot inherit hidden conversation state or broaden file/tool/network scope.
- Every delegation is recorded in events and artifact provenance.

## Checkpoints

High-risk runs require operator acceptance before GREEN and before close. Checkpoints are request/evidence-specific; changed scope, commands, facts or evidence invalidate them.

## Learnings

`docs/agent/learnings.json` is canonical.

- Stage agents may propose candidates.
- Independent verification curates lifecycle.
- Active entries require reviewer and evidence.
- Selection is deterministic by scope tags.
- Conflicted, deprecated, revoked, expired or unreviewed entries are excluded.

## Validation

- `scripts/validate-governance.py` checks global profiles, roles, learnings and fixture references.
- `scripts/validate-run-bundle.py` checks machine evidence.
- `scripts/validate-run-governance.py` checks per-run profile, specialist, checkpoint and budget compliance.

## Boundaries

The local repository does not implement hosted auth, multi-tenancy, remote worker scheduling, credential custody, billing, UI or integrations. Those remain Rigor Route concerns.
