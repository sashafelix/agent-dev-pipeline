# Claude Code Sub-Agents — Local RGR v1.2

Stage agents are orchestrator-invoked only. Start with a Plan, then invoke `ai-pipeline-rgr-orchestrator`.

## Execution order

`PREPARE → BRAINSTORM → PLAN → ANALYZE → RED → GREEN → REFACTOR → VERIFY → CONVERGE`

## Agents

- `ai-pipeline-rgr-orchestrator.md` — worktree, context, schemas, events, transitions, remediation and closure.
- `ai-pipeline-prepare.md` — read-only repository intelligence and impact map.
- `ai-pipeline-brainstorm.md` — declarative success criteria and uncertainty register.
- `ai-pipeline-analyze.md` — pre-implementation cross-artifact consistency gate.
- `ai-pipeline-red-test.md` — failing executable evidence; actor role `test_author`.
- `ai-pipeline-green-code.md` — minimum passing implementation; actor role `implementer`.
- `ai-pipeline-refactor.md` — behaviour-preserving cleanup; actor role `refactorer`.
- `ai-pipeline-quality-gate.md` — independent verification; no source writes.
- `ai-pipeline-converge.md` — final consistency check and bounded remediation decision.

PLAN is orchestrator-owned and produces the locked task graph.

## Evidence model

- Every stage has an immutable `context-{stage}.json` manifest.
- Canonical outputs validate against `docs/agent/schemas/`.
- Markdown is a reviewer projection only.
- `events.jsonl`, `handoff.md` and `decision-log.md` are append-only.
- The GREEN implementer cannot issue the final VERIFY verdict.
- Completed bundles must pass `scripts/validate-run-bundle.py`.

## Failure handling

- Halt and preserve the worktree on failure.
- One retry maximum for explicitly transient tooling/container startup failures.
- No transient retry for assertion, compile, schema, evidence, security, contract or self-check failures.
- CONVERGE allows at most two remediation attempts and preserves prior evidence.

## Skills

Skill documentation lives under `docs/skills/`. Skills may contribute evidence through the calling stage agent, but cannot advance state, widen authority, approve actions or bypass deterministic gates.
