# Quality Gates

story_id: <story-id>
checked_at: <iso-timestamp>
verdict: PASS | FAIL | WARN
checked_by: ai-pipeline-quality-gate

## 1. Success Criteria → Test trace

| SC | Statement (from brainstorm.md) | Test(s) | Status |
| --- | --- | --- | --- |
| SC-1 | | | ✓ / ✗ |

Every ✗ is a FAIL.

## 2. Mandatory evidence matrix

Tick only what the story actually required (others: N/A).

- [ ] Unit tests for changed logic — list:
- [ ] Integration / e2e test (if external systems or cross-module flows involved) — list:
- [ ] Security test (if authz touched) — list positive + negative per role:
- [ ] Data / migration / schema check (if persistence or message schema changed) — details:
- [ ] Contract compatibility check via `skill-contract-guard` — report:
- [ ] Observability evidence (logs/metrics) — list:
- [ ] Compliance evidence block via `skill-compliance` — see section 5
- [ ] Coverage ≥ threshold on touched modules (no regression) — report path:

## 3. Hard-FAIL checklist

If ANY box below is checked, verdict = FAIL.

- [ ] Dead code / commented-out blocks / stale TODOs in change set
- [ ] Premature abstraction — new interface/base class/hook with fewer than 3 callers
- [ ] File > 300 LOC (non-test, non-generated) without justified split
- [ ] Method / function > 30 LOC or > 3 nested levels without justification
- [ ] Any stage's `handoff.md` section missing self-check block
- [ ] Comprehension evidence empty (`files_read`, `patterns_searched`, or `reuse_decisions`)
- [ ] `reuse_decisions` empty AND duplicated existing pattern
- [ ] Incremental verification checkpoints missing
- [ ] Hardcoded secrets, URLs, or env-specific values (grep-verified)
- [ ] Novel pattern introduced without decision-log justification
- [ ] Test(s) failing or skipped

## 4. Merge gates

- [ ] All tests pass — runner summary:
- [ ] Coverage ≥ threshold on touched modules — link:
- [ ] No blocker/critical findings
- [ ] Security review complete (if applicable)
- [ ] All `[UNCERTAIN]` entries resolved or downgraded to WARN-level preference

## 5. Compliance Evidence (from skill-compliance)

| Control | Status | Evidence |
| --- | --- | --- |
| AuthN on entry points | ✓ / ✗ / N/A | |
| AuthZ per role | ✓ / ✗ / N/A | |
| Input validation | ✓ / ✗ / N/A | |
| Audit log | ✓ / ✗ / N/A | |
| Sensitive data sanitization | ✓ / ✗ / N/A | |
| Contract compatible | ✓ / ✗ / N/A | |
| Coverage ≥ threshold | ✓ / ✗ | |

## 6. Uncertainty resolution

| [UNCERTAIN] ID | Statement | Resolution | Impact on verdict |
| --- | --- | --- | --- |
| U-1 | | resolved / accepted-as-WARN / blocker | PASS / WARN / FAIL |

## 7. Learnings curated

| learning_id | prior status | new status | note |
| --- | --- | --- | --- |
| LRN-XXXX | candidate | active | evidenced by this run |

## 8. Notes
- (one-line summary for decision-index.md, ≤120 chars)

## 9. Final verdict
- **PASS** / **FAIL** / **WARN**
- Justification (one paragraph; cite specific rows above):
