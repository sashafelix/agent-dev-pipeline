# Rigor Route Compatibility — Local RGR v2

Local RGR v2 is a repository-local reference protocol. Rigor Route is the future trusted control plane. Compatibility is evidence-based rather than authority-preserving.

## Portable inputs

- `packs/rgr-software-v2/pack.json`
- versioned `stages/*.json`
- `capabilities.json`
- workflow profiles and role contracts
- published artifact/event schemas

## Portable run evidence

```bash
python3 scripts/export-run-bundle.py \
  docs/agent/runs/{story_id} \
  evidence.tar.gz
```

The archive contains canonical run artifacts, projections and text evidence only. It excludes story source code, binary files and detected secrets. Tar metadata and gzip timestamps are normalised for deterministic bytes.

Verify independently:

```bash
python3 scripts/verify-export-bundle.py evidence.tar.gz
```

## Import semantics

The exact translation rules live in `packs/rgr-software-v2/rigor-route-import.json`.

- Event sequence, role, attempt and artifact references are preserved.
- Artifact bytes are imported unchanged after SHA-256 verification.
- Local profile selection is evidence; platform policy may require a stricter route.
- Local role IDs are intersected with platform/workspace/repository policy.
- Local operator checkpoints are historical evidence only and never grant platform authority.
- Local VERIFY/CONVERGE verdicts are imported as evidence and independently validated.

## Authority boundary

The local pack has no merge, deployment or publication authority. It does not carry credentials or authenticated approval identity into Rigor Route. The platform creates fresh leases, credentials, approvals and publication decisions.

## Signing

Local packs may remain unsigned for development. The manifest and stage hashes are deterministically computable with `validate-pack.py`. A trusted Rigor Route environment may require a signed, reviewed and activated pack version before execution.
