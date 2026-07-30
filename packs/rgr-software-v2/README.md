# rgr-software v2.0.0

Portable local RGR software-delivery pack.

## Contents

- `pack.json` — pack identity, stage references, schemas and compatibility.
- `capabilities.json` — required/optional runtime capabilities and unsupported features.
- `rigor-route-import.json` — evidence import and translation contract.
- `stages/*.json` — nine ordered stage contracts.

## Validation

```bash
python3 scripts/validate-pack.py packs/rgr-software-v2/pack.json
```

The validator checks manifest/schema validity, stage order, role and capability references, artifact paths, retry limits and Rigor Route compatibility.

## Integrity

The repository pack may remain unsigned for local use. `validate-pack.py` computes and reports deterministic SHA-256 values. Rigor Route may require a signed and activated manifest before executing the pack.

## Publication

This pack has no merge, deployment or publication authority. It produces local reviewable evidence only.
