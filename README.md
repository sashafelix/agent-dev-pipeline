# agent-dev-pipeline

A deterministic, auditable, repository-local agent pipeline for software-engineering tasks.

## Local RGR v1.3

```text
PREPARE → BRAINSTORM → PLAN → ANALYZE → RED → GREEN → REFACTOR → VERIFY → CONVERGE
```

All profiles retain every stage. Task risk changes evidence depth, context budgets, specialist reviews and operator checkpoints—not the mandatory workflow.

## What v1.3 adds

- Deterministic `small`, `standard` and `high-risk` workflow profiles.
- Immutable `profile-resolution.json` with rule IDs and reasons.
- Operator minimum-profile overrides that may only increase strictness.
- Explicit role/capability contracts for core and specialist agents.
- Read-only threat, migration, infrastructure, contract, accessibility and cross-risk reviews.
- High-risk checkpoints before GREEN and before close.
- Canonical governed `learnings.json` lifecycle and scope selection.
- Global and per-run governance validators.

## Resolve a profile

Prepare immutable facts:

```json
{
  "story_id": "FEATURE-123",
  "facts": {
    "risk_tags": ["domain:auth"],
    "blast_radius": "medium",
    "uncertainty": "low",
    "changed_module_count": 2,
    "cross_service": false,
    "contract_change": false,
    "data_migration": false,
    "security_sensitive": true,
    "infrastructure_change": false
  }
}
```

Resolve deterministically:

```bash
python3 scripts/resolve-profile.py task-facts.json --output profile-resolution.json
```

A minimum profile can make a run stricter:

```bash
python3 scripts/resolve-profile.py task-facts.json \
  --minimum-profile high-risk \
  --output profile-resolution.json
```

There is no option to force a weaker profile.

## Profiles

| Profile | Intended use | Extra governance |
|---|---|---|
| `small` | bounded single-module, low-risk change | compact budgets and one convergence attempt |
| `standard` | normal multi-file feature/bug/refactor | larger context, full regressions, conditional contract/accessibility review |
| `high-risk` | security, data, infrastructure, architecture or broad changes | specialists, safety evidence, rollback evidence, operator checkpoints |

Profile definitions live in `docs/agent/workflow-profiles.json`.

## Governed roles

Core roles include repository analyst, specifier, consistency analyst, test author, implementer, refactorer, independent verifier and convergence reviewer. Specialist roles are read-only and cannot modify story source, transition stages, lower risk or approve publication.

Role contracts live in `docs/agent/role-contracts.json`.

## Run validation

Validate machine evidence:

```bash
python3 scripts/validate-run-bundle.py docs/agent/runs/{story_id}
```

Validate selected-profile governance:

```bash
python3 scripts/validate-run-governance.py docs/agent/runs/{story_id}
```

Validate global profiles, roles, learnings and corpus references:

```bash
python3 scripts/validate-governance.py
```

A run closes only when both per-run validators pass, CONVERGE reports `CONVERGED`, and required checkpoints are accepted.

## Governed learnings

`docs/agent/learnings.json` is authoritative. Agents may propose evidence-backed candidates; only independent verification may curate status. Active selection is deterministic by scope tags. Conflicted, deprecated, revoked, expired or unreviewed entries cannot influence context.

## Evaluation

The canonical fixture corpus remains `docs/agent/evaluation-corpus.json` and is validated/compared with:

```bash
python3 scripts/evaluate-corpus.py
```

## Design boundaries

This repository remains lightweight and local. Authentication, multi-tenancy, remote workers, credential custody, hosted sandboxes, billing, product UI and external trigger integrations belong in Rigor Route.

## Reference

- `CLAUDE.md` — execution rules
- `AGENTS.md` — role model
- `docs/agent/runtime-doc-contract.yaml` — complete runtime contract
- `docs/agent/workflow-profiles.json` — adaptive profiles
- `docs/agent/role-contracts.json` — permissions and delegation
- `docs/agent/learnings.json` — governed learnings
- `docs/agent/schemas/` — artifact contracts
