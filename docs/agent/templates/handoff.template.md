# Handoff Projection

story_id: <story-id>

Append-only reviewer projection. Canonical stage state lives in JSON artifacts and `events.jsonl`.

## PREPARE
- agent: ai-pipeline-prepare
- timestamp:
- canonical_artifact: repository-intelligence.json
- revision:
- inspected_paths:
- omitted_paths:
- likely_impact:
- warnings:
- next_stage: brainstorm

## BRAINSTORM
- agent: ai-pipeline-brainstorm
- timestamp:
- canonical_artifact: brainstorm.json
- success_criteria_count:
- input_trace_complete: y/n
- blocking_uncertainties: none | [list]
- next_stage: plan

## PLAN
- agent: ai-pipeline-rgr-orchestrator
- timestamp:
- canonical_artifact: detailed-plan.json
- status: locked
- task_count:
- criterion_test_map_complete: y/n
- dependency_graph_acyclic: y/n
- next_stage: analyze

## ANALYZE
- agent: ai-pipeline-analyze
- timestamp:
- canonical_artifact: analysis-report.json
- hard_findings: none | [list]
- warnings: none | [list]
- unresolved_uncertainties: none | [list]
- next_stage: red_test | failed

## RED
- agent: ai-pipeline-red-test
- actor_role: test_author
- timestamp:
- canonical_artifact: red-result.json
- files_read:
- patterns_searched:
- reuse_decisions:
- commands_and_output_refs:
- criterion_evidence_summary:
- self_check_complete: y/n
- next_stage: green_code

## GREEN
- agent: ai-pipeline-green-code
- actor_role: implementer
- timestamp:
- canonical_artifact: green-result.json
- files_read:
- patterns_searched:
- reuse_decisions:
- changed_files:
- commands_and_output_refs:
- criterion_evidence_summary:
- self_check_complete: y/n
- next_stage: refactor

## REFACTOR
- agent: ai-pipeline-refactor
- actor_role: refactorer
- timestamp:
- canonical_artifact: refactor-result.json
- improvements_or_no_op_reason:
- changed_files:
- commands_and_output_refs:
- criterion_evidence_summary:
- self_check_complete: y/n
- next_stage: quality_gate

## VERIFY
- agent: ai-pipeline-quality-gate
- actor_role: independent_verifier
- reviewer_identity:
- timestamp:
- canonical_artifact: quality-gates.json
- verdict: PASS | WARN | FAIL
- independently_executed_checks:
- hard_failures: none | [list]
- criterion_evidence_complete: y/n
- next_stage: converge

## CONVERGE
- agent: ai-pipeline-converge
- timestamp:
- canonical_artifact: convergence-report.json
- attempt: 1 | 2
- outcome: CONVERGED | REMEDIATE | FAILED
- blocking_gaps: none | [list]
- earliest_invalid_stage: null | <stage>
- next_stage: close | <earliest-invalid-stage> | failed

## CLOSE
- agent: ai-pipeline-rgr-orchestrator
- timestamp:
- bundle_validation: PASS | FAIL
- final_verdict: PASS | WARN | FAIL
- worktree_preserved: y
- decision_index_updated: y/n
