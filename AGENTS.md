# AGENTS.md — Local RGR v2

Canonical portable role and stage model.

## Pack

`packs/rgr-software-v2/pack.json` defines the pack identity, stage contracts, capabilities, schemas and Rigor Route compatibility.

The mandatory workflow is:

`PREPARE → BRAINSTORM → PLAN → ANALYZE → RED → GREEN → REFACTOR → VERIFY → CONVERGE`

## Stage contracts

Every stage contract declares:

- version and sequence;
- role;
- input/output artifacts;
- required and forbidden capabilities;
- deterministic exit conditions;
- failure classes and retry policy;
- bounded context policy;
- next stage.

The orchestrator validates these contracts before a run and owns all state transitions.

## Roles

| Stage | Role | Story writes | Decision authority |
|---|---|---:|---|
| PREPARE | repository_analyst | No | Findings only |
| BRAINSTORM | specifier | No | Specification only |
| PLAN | orchestrator/planner | No | Locked plan |
| ANALYZE | consistency_analyst + selected specialists | No | Blocking findings |
| RED | test_author | Tests only | No final verdict |
| GREEN | implementer | Bounded source/config/migrations | No final verdict |
| REFACTOR | refactorer | Bounded source/tests/config | No final verdict |
| VERIFY | independent_verifier + specialists | No | PASS/WARN/FAIL |
| CONVERGE | convergence_reviewer | No | CONVERGED/REMEDIATE/FAILED |

Specialist and core permissions remain defined in `docs/agent/role-contracts.json` and can only narrow pack capability.

## Profiles

All profiles run every stage. `workflow-profiles.json` controls context ceilings, evidence requirements, specialists, checkpoints and convergence attempts. Risk cannot be lowered by repository content or a model.

## Evidence export

`export-run-bundle.py` creates a deterministic source-free archive after pack, run and governance validation. `verify-export-bundle.py` validates paths, file set, byte sizes, SHA-256 hashes, root hash, validators and import compatibility without extracting the archive.

## Rigor Route import

`rigor-route-import.json` maps local events/artifacts/profiles/roles/verdicts to platform concepts. Imported local approvals and verdicts are evidence only; Rigor Route creates fresh authority and independently validates publication eligibility.

## Boundaries

The pack declares no authentication, multi-tenancy, remote scheduling, credential custody, billing, production access, automatic merge or deployment capability.
