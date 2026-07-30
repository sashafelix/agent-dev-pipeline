# Detailed Plan Projection

story_id: <story-id>
owner_agent: ai-pipeline-rgr-orchestrator
status: draft | locked
canonical_artifact: detailed-plan.json
derived_from:
- brainstorm.json
- repository-intelligence.json

This Markdown file is a reviewer projection. `detailed-plan.json` is authoritative.

## Planning rules

- Tasks are small, ordered, independently verifiable and acyclic.
- Every task declares exact outputs, dependencies and covered `SC-{n}` criteria.
- Every SC maps to at least one planned test ID before ANALYZE.
- Lock the plan before ANALYZE exits; later scope changes require a new attempt.

## Task graph

| Task ID | Stage | Description | Depends on | Outputs | Covers SCs | Verification |
|---|---|---|---|---|---|---|
| TASK-1 | red_test | Add failing test for happy path | — | `<test-path>` | SC-1 | Intended failure captured |
| TASK-2 | green_code | Implement minimum happy-path behaviour | TASK-1 | `<source-path>` | SC-1 | SC-1 test passes |
| TASK-3 | refactor | Simplify implementation without behaviour change | TASK-2 | `<source-path>` | SC-1 | Full required suite stays green |

## Criterion-to-test map

| SC | Planned test IDs | Test type | Expected RED reason |
|---|---|---|---|
| SC-1 | TEST-1 | unit | Required behaviour absent |

## Contract and risk surfaces

| Surface | Planned change | Compatibility risk | Required evidence |
|---|---|---|---|
| `<API / DB / event / config>` | `<change>` | `<none / bounded / breaking>` | `<contract / migration / security checks>` |

## ANALYZE readiness

- [ ] Every input-derived SC is represented.
- [ ] Every SC maps to planned test evidence.
- [ ] Every task has outputs and valid dependencies.
- [ ] No dependency cycles exist.
- [ ] Repository impact and likely tests were considered.
- [ ] Scope, architecture and compatibility assumptions are explicit.
- [ ] Canonical JSON status is `locked`.

## VERIFY and CONVERGE expectations

- VERIFY reconstructs evidence from stage-result artifacts, diff and independently executed checks.
- CONVERGE compares locked intent, plan, tests, implementation, docs and verdict.
- Remediation resumes from the earliest invalid stage and never edits prior evidence.
