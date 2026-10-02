# Decision Log

story_id: <story-id>

Append-only. Every entry is timestamped. Non-trivial decisions only — not a narration log.

## Entry format
```
<iso-timestamp> | agent: <agent-id> | [skill: <skill-id>] | decision: <what> | rationale: <why> | [related_learning_ids: LRN-XXXX] | [tag: UNCERTAIN]
```

## [UNCERTAIN] tag
Use for a fact or choice that remains unconfirmed. Do not implement a correctness-sensitive assumption. Include:
- What you assumed
- What evidence would confirm or refute it
- Impact if the assumption is wrong

Block at the first stage where uncertainty affects correctness, security or scope; return it to the orchestrator for resolution. VERIFY reviews remaining entries. Only a non-correctness preference may be accepted as WARN.

## Entries
- <iso-timestamp> | agent: ai-pipeline-brainstorm | decision: mapped AC-1 to SC-1 + SC-2 (split by success and failure paths) | rationale: single criterion conflated two observable outcomes
- <iso-timestamp> | agent: ai-pipeline-red-test | decision: used WireMock-style stub for external client | rationale: real endpoint not available in CI
- <iso-timestamp> | agent: ai-pipeline-green-code | tag: UNCERTAIN | decision: blocked numeric-id assumption and requested contract clarification | rationale: contract allows strings while samples contain only digits | impact_if_wrong: validation would reject valid ids
