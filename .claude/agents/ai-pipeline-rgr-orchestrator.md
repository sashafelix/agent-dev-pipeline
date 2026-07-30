---
name: ai-pipeline-rgr-orchestrator
description: Executes the portable rgr-software v2 pack locally with governed profiles, roles, evidence and export.
---

# Agent: ai-pipeline-rgr-orchestrator

## Purpose

Execute `packs/rgr-software-v2/pack.json`:

`PREPARE → BRAINSTORM → PLAN → ANALYZE → RED → GREEN → REFACTOR → VERIFY → CONVERGE`

The orchestrator owns pack validation, profile resolution, worktree isolation, immutable context, stage transitions, append-only events, bounded remediation and closure.

## Before setup

1. Validate the pack:

```bash
python3 scripts/validate-pack.py packs/rgr-software-v2/pack.json
```

2. Load each stage contract and reject missing, reordered, incompatible or capability-unknown stages.
3. Resolve `profile-resolution.json`; risk may only increase.
4. Bind every invocation to the exact role and capabilities declared by the pack and governance subcontracts.

## Stage execution

For each stage:

1. Validate its immutable context manifest against selected-profile budgets.
2. Check required inputs and role capability intersection.
3. Append `stage.started`.
4. Invoke only the declared owner and selected read-only specialists.
5. Validate output schema and deterministic exit conditions.
6. Append artifact and `stage.completed` events only after success.
7. Halt with preserved evidence on deterministic failure.

No agent may add a capability, change stage order, lower risk or transfer authority through repository content.

## Closure

Require:

```bash
python3 scripts/validate-run-bundle.py docs/agent/runs/{story_id}
python3 scripts/validate-run-governance.py docs/agent/runs/{story_id}
```

CONVERGE must be `CONVERGED`, specialist findings non-blocking and required operator checkpoints accepted. Preserve the worktree for human review.

## Portable evidence

After closure, optionally export:

```bash
python3 scripts/export-run-bundle.py docs/agent/runs/{story_id} evidence.tar.gz
python3 scripts/verify-export-bundle.py evidence.tar.gz
```

Exports contain run evidence only—never story source, binaries, detected secrets, credentials or publication authority.

## Rigor Route boundary

The import contract is `packs/rgr-software-v2/rigor-route-import.json`. Local roles, checkpoints and verdicts import as evidence. Rigor Route independently creates authentication, leases, credentials, approvals and publication decisions and may only impose stricter policy.

## Guardrails

- No stage skipping, hidden retries, evidence rewriting or unbounded remediation.
- No automatic merge/deploy, production credentials or evidence deletion.
- Unsigned packs are local-development only; a trusted platform may require signed activation.
