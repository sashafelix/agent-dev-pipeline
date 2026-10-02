# Quality Gates Projection

story_id: <story-id>
checked_at: <iso-timestamp>
verdict: PASS | WARN | FAIL
checked_by: ai-pipeline-quality-gate
canonical_artifact: quality-gates.json

This is a reviewer projection. Populate canonical JSON against `quality-gates.schema.json` and the VERIFY stage contract first. The independent verifier must not be the GREEN implementer. VERIFY is followed by CONVERGE; its verdict grants no merge or deployment authority.

## Success criteria and independent evidence

| SC from brainstorm.json | Planned test IDs | Independent command/check | Evidence path | Result |
| --- | --- | --- | --- | --- |
| SC-1 | TEST-1 | <actual check> | <actual output> | PASS / FAIL |

Every required criterion must have current evidence. Record actual commands, results, reviewer identity and evidence references in the canonical artifacts; never substitute an implementer's narrative for independent verification.

## Required checks

Derive requirements from the selected workflow profile, locked plan, role contracts and applicable project rules. Mark optional checks N/A with a reason.

- [ ] Pack, current artifact schemas and applicable governance checks pass.
- [ ] Full completed-run validation is scheduled for orchestrator closure after CONVERGE; do not require future artifacts before VERIFY can finish.
- [ ] Required test/build/static checks were independently run and pass.
- [ ] SC-to-test trace and RED/GREEN evidence are complete.
- [ ] Required security, contract, migration and specialist reviews are complete.
- [ ] Required checkpoints, context/comprehension evidence and stage results are present.
- [ ] Scope and protected surfaces match the locked plan and role authority.
- [ ] Coverage meets the project's recorded threshold, where applicable.
- [ ] Required documentation and runtime configuration match the implementation.

## Blocking findings

Missing or invalid required evidence, failing required checks, scope/role violations, incompatible contracts and unresolved correctness/security issues require FAIL. WARN is limited to non-correctness preferences. A warning cannot waive a blocker.

Code-size and abstraction heuristics are review prompts unless an applicable project rule makes them mandatory. Do not invent universal 300-line, 30-line or three-caller release gates.

| Finding | Requirement/source | Evidence | Resolution | Verdict impact |
| --- | --- | --- | --- | --- |
| <finding> | <contract or rule> | <path> | <resolved / preference warning / blocker> | PASS / WARN / FAIL |

## Applicable control evidence

| Control | Result or N/A reason | Evidence |
| --- | --- | --- |
| Authentication and role authorization | | |
| Input validation | | |
| Audit/correlation logging | | |
| Sensitive data omitted or masked | | |
| API/event/database compatibility | | |
| Coverage and regression checks | | |

## Learnings and next stage

Record any learning status change under the governed learning rules with supporting evidence. Learnings remain advisory and cannot replace proof.

- Verdict and rationale: <cite findings and actual evidence>
- Summary for the decision index: <at most 120 characters>
- Next: CONVERGE checks locked intent, plan, tests, code, docs and this verdict; the orchestrator owns closure or bounded remediation.
