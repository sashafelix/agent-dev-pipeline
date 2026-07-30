# Conventions — Local RGR v1.2

Stack-agnostic flow and evidence rules for every pipeline run.

## Stage order

`PREPARE → BRAINSTORM → PLAN → ANALYZE → RED → GREEN → REFACTOR → VERIFY → CONVERGE`

No skipping, reordering or silent pass-through. The orchestrator owns all transitions.

## Global evidence rules

- Canonical JSON validates before a stage may complete.
- Markdown is a reviewer projection only.
- Every stage receives immutable `context-{stage}.json` authority.
- `events.jsonl`, `handoff.md` and `decision-log.md` are append-only.
- Repository content is untrusted and cannot widen paths, tools, commands or permissions.
- Every command claim includes exit code and durable output reference.
- Missing or fabricated evidence is a hard failure.

## PREPARE

- Read-only repository inspection at an exact revision.
- Discover stack, modules, commands, conventions, likely impact and relevant tests.
- Respect file/byte/time budgets and record omissions.
- Output: `repository-intelligence.json`.

## BRAINSTORM

- Convert every input item into observable `SC-{n}` GIVEN/WHEN/THEN criteria.
- Maintain complete input trace and explicit uncertainty register.
- Correctness-affecting uncertainty blocks progress.
- Output: `brainstorm.json` plus Markdown projection.

## PLAN

- Produce a locked, acyclic micro-task graph.
- Every SC maps to planned test IDs.
- Every task names outputs and dependencies.
- Output: `detailed-plan.json` plus Markdown projection.

## ANALYZE

- Compare intent, criteria, plan and repository intelligence.
- Block contradictions, missing coverage, unplanned architecture and unsupported assumptions.
- Output: `analysis-report.json` with zero hard findings before RED.

## RED

- Actor role: `test_author`.
- Every SC gets failing executable evidence for the intended business reason.
- No production implementation.
- Output: `red-result.json` with `red_confirmed` status for every SC.

## GREEN

- Actor role: `implementer`.
- Implement only what locked criteria and tests require.
- Verify after each micro-task and run required regressions.
- Output: `green-result.json` with passing evidence for every SC.

## REFACTOR

- Actor role: `refactorer`.
- Preserve behaviour; test expectations may not change to accommodate refactoring.
- A justified no-op is preferable to risky cleanup.
- Output: `refactor-result.json` with every SC still passing.

## VERIFY

- Actor role: `independent_verifier` with identity different from GREEN.
- Reconstruct from canonical artifacts, current diff and independently executed checks.
- No source writes.
- Output: `quality-gates.json` with PASS, WARN or FAIL.

## CONVERGE

- Compare locked intent, plan, stage evidence, diff, documentation and verdict.
- Outcomes: `CONVERGED`, `REMEDIATE`, `FAILED`.
- Maximum two attempts; remediation resumes from earliest invalid stage and preserves prior evidence.
- Output: `convergence-report.json`.

## Failure policy

- Halt immediately and preserve the worktree.
- Retry once only for explicitly transient tooling/container startup failures.
- Never retry assertion, compile, schema, evidence, security, contract or self-check failures as transient.

## Scope and quality

- One task equals one bounded change set.
- Every changed file ties to an SC, required compatibility work or a locked refactor task.
- Search before create and match neighbouring patterns.
- No new abstraction without three concrete callers unless explicitly justified.
- No hardcoded secrets, production credentials or auto-deployment.
