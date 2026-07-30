# agent-dev-pipeline — Local RGR v2

A deterministic, auditable, repository-local software-delivery protocol.

```text
PREPARE → BRAINSTORM → PLAN → ANALYZE → RED → GREEN → REFACTOR → VERIFY → CONVERGE
```

Version: `2.0.0`

## What v2 adds

- Portable `rgr-software` pack manifest.
- Nine versioned stage contracts.
- Explicit runtime capability and unsupported-feature declarations.
- Deterministic, source-free evidence archives.
- Independent archive verification and tamper detection.
- Formal `rigor-route-pack-import-v1` compatibility mapping.
- End-to-end synthetic contract fixture in CI.

Earlier hardening remains part of v2: repository intelligence, machine-valid artifacts, independent verification, bounded convergence, adaptive profiles, specialist reviews, checkpoints and governed learnings.

## Validate the protocol

```bash
python3 scripts/validate-pack.py packs/rgr-software-v2/pack.json
python3 scripts/validate-governance.py
python3 scripts/evaluate-corpus.py
```

## Run locally

1. Produce a Plan.
2. Invoke only `ai-pipeline-rgr-orchestrator` with task intent and immutable classification facts.
3. Review the worktree and canonical evidence.
4. Validate the completed run:

```bash
python3 scripts/validate-run-bundle.py docs/agent/runs/{story_id}
python3 scripts/validate-run-governance.py docs/agent/runs/{story_id}
```

## Export portable evidence

```bash
python3 scripts/export-run-bundle.py \
  docs/agent/runs/{story_id} \
  evidence.tar.gz

python3 scripts/verify-export-bundle.py evidence.tar.gz
```

The archive:

- contains canonical run evidence and text projections;
- excludes story source code and binary files;
- rejects detected secrets and unsafe archive paths;
- includes SHA-256 per-file and root hashes;
- is byte-for-byte deterministic for identical run evidence;
- grants no merge, deployment or publication authority.

## Portable pack

```text
packs/rgr-software-v2/
├── pack.json
├── capabilities.json
├── rigor-route-import.json
└── stages/
    ├── prepare.json
    ├── brainstorm.json
    ├── plan.json
    ├── analyze.json
    ├── red_test.json
    ├── green_code.json
    ├── refactor.json
    ├── quality_gate.json
    └── converge.json
```

Validate and produce a hash report:

```bash
python3 scripts/validate-pack.py \
  packs/rgr-software-v2/pack.json \
  --hash-report pack-hashes.json
```

Local development may use an unsigned pack. A trusted platform may require a signed and activated pack before execution.

## Rigor Route boundary

Local checkpoints, roles and verdicts import as historical evidence—not platform authority. Rigor Route independently applies authentication, policy, leases, credentials, approvals and publication decisions. Platform policy may only narrow or strengthen the imported workflow.

See `docs/agent/rigor-route-compatibility.md`.

## Design boundaries

This repository intentionally does not implement hosted authentication, multi-tenancy, remote worker scheduling, credential custody, billing, product UI, automatic merge/deployment or production access. Those remain Rigor Route responsibilities.

## Reference

- `VERSION`
- `CHANGELOG.md`
- `CLAUDE.md`
- `AGENTS.md`
- `docs/agent/runtime-doc-contract.yaml`
- `docs/agent/schemas/`
- `packs/rgr-software-v2/`
