# Agent Runtime Artifacts — Local RGR v2

This folder contains portable schemas, governance subcontracts, evaluation fixtures and per-run evidence.

## Portable pack

- `../../packs/rgr-software-v2/pack.json`
- nine versioned stage contracts
- capability declaration
- Rigor Route import contract

Validate the pack:

```bash
python3 scripts/validate-pack.py packs/rgr-software-v2/pack.json
```

## Per-run evidence

```text
docs/agent/runs/{story_id}/
├── run-context.md
├── plan-input.md
├── profile-resolution.json
├── repository-intelligence.json
├── brainstorm.json
├── detailed-plan.json
├── analysis-report.json
├── specialist-*-review.json       # selected profile only
├── red-result.json
├── green-result.json
├── refactor-result.json
├── context-*.json
├── events.jsonl
├── handoff.md
├── decision-log.md
├── quality-gates.json
├── convergence-report.json
└── error-report.md                # failure only
```

JSON and append-only events are authoritative. Markdown is a reviewer projection.

## Validate a completed run

```bash
python3 scripts/validate-run-bundle.py docs/agent/runs/{story_id}
python3 scripts/validate-run-governance.py docs/agent/runs/{story_id}
```

## Export and verify

```bash
python3 scripts/export-run-bundle.py docs/agent/runs/{story_id} evidence.tar.gz
python3 scripts/verify-export-bundle.py evidence.tar.gz
```

The export is deterministic for identical evidence, includes a hash manifest, excludes story source/binaries/secrets, and grants no publication authority.

## Governance subcontracts

- `workflow-profiles.json` — adaptive strictness.
- `role-contracts.json` — core/specialist permissions.
- `learnings.json` — governed memory.
- `evaluation-corpus.json` — comparison fixtures.

These remain independently versioned subcontracts referenced by the v2 pack.

## Rigor Route compatibility

See `rigor-route-compatibility.md`. Local events and artifacts can be imported, but local checkpoints and verdicts never transfer authenticated platform authority.

## Safety

No source archive, symlink, binary, detected secret, production credential, automatic merge or deployment is permitted in the portable evidence format.
