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
- Lock the plan before ANALYZE begins; later scope changes require a new attempt.

## Task graph

| Task ID | Stage | Description | Depends on | Outputs | Covers SCs | Verification |
|---|---|---|---|---|---|---|
| TASK-1 | red_test | Add failing backend and frontend tests | — | `backend/tests/example.test`, `frontend/tests/example.test` | SC-1 | Intended failures captured |
| TASK-2 | green_code | Implement backend behaviour | TASK-1 | `backend/src/example` | SC-1 | Backend test passes |
| TASK-3 | green_code | Implement frontend behaviour against the locked contract | TASK-1 | `frontend/src/example` | SC-1 | Frontend test passes |
| TASK-4 | refactor | Simplify implementation without behaviour change | TASK-2, TASK-3 | `backend/src/example`, `frontend/src/example` | SC-1 | Required suite stays green |

## Implementation lanes

Declare lanes only when GREEN tasks can be partitioned cleanly by literal repository path prefix. The deterministic resolver may still serialize them.

| Lane ID | Kind | GREEN tasks | Write surfaces | Depends on lanes |
|---|---|---|---|---|
| LANE-backend | backend | TASK-2 | `backend/` | — |
| LANE-frontend | frontend | TASK-3 | `frontend/` | — |

Rules:
- every declared GREEN task belongs to exactly one lane;
- a task output must live beneath its lane's declared write surfaces;
- lane dependencies are inferred from the task DAG and unioned with explicit lane dependencies;
- same-wave surface overlap forces sequential fallback;
- runtime concurrency never changes role authority or the locked plan.

## Criterion-to-test map

| SC | Planned test IDs | Test type | Expected RED reason |
|---|---|---|---|
| SC-1 | TEST-1, TEST-2 | unit | Required behaviour absent |

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
- [ ] Explicit GREEN lanes, if declared, partition all GREEN tasks exactly once.
- [ ] Lane write surfaces are literal relative prefixes and cover planned outputs.

## VERIFY and CONVERGE expectations

- VERIFY reconstructs evidence from stage-result artifacts, diff and independently executed checks.
- CONVERGE compares locked intent, plan, tests, implementation, docs and verdict.
- Remediation resumes from the earliest invalid stage and never edits prior evidence.
