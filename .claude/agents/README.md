# Claude Code Sub-Agents — Local RGR v2

For ambiguous/raw tasks, `ai-pipeline-intake` may run first. It is outside the governed run and only produces a READY intake/plan handoff.

Invoke only `ai-pipeline-rgr-orchestrator` for the governed delivery run.

## Portable protocol

Pack manifest: `packs/rgr-software-v2/pack.json`

`PREPARE → BRAINSTORM → PLAN → ANALYZE → RED → GREEN → REFACTOR → VERIFY → CONVERGE`

Each stage is governed by a versioned JSON contract declaring its role, artifacts, capabilities, exit conditions, failures and next stage.

## Agents

- `ai-pipeline-intake` — optional pre-run requirements resolver; no governed delivery authority.

- orchestrator — validates pack/profile/context and owns transitions.
- `ai-pipeline-prepare` — repository analyst.
- `ai-pipeline-brainstorm` — specifier.
- PLAN — orchestrator/planner.
- `ai-pipeline-analyze` — consistency analyst plus selected specialists.
- `ai-pipeline-red-test` — test author.
- `ai-pipeline-green-code` — implementer.
- `ai-pipeline-refactor` — refactorer.
- `ai-pipeline-quality-gate` — independent verifier plus specialists.
- `ai-pipeline-converge` — convergence reviewer.

## Closure

A run closes only after pack, evidence and governance validation pass. Portable evidence may then be exported and independently verified.

```bash
python3 scripts/export-run-bundle.py docs/agent/runs/{story_id} evidence.tar.gz
python3 scripts/verify-export-bundle.py evidence.tar.gz
```

The archive contains no story source, secrets or publication authority.


## Trusted project profiles and GREEN lanes

Operator/trusted-platform `project-profile.json` snapshots provide authoritative project facts but cannot alter governance. PLAN resolves `lane-resolution.json`; GREEN may execute disjoint lanes concurrently only when the resolver and runtime both allow it, otherwise it executes the same lane plan sequentially.
