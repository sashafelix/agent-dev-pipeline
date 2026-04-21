# Decision Log

story_id: <story-id>

Append-only. Every entry is timestamped. Non-trivial decisions only — not a narration log.

## Entry format
```
<iso-timestamp> | agent: <agent-id> | [skill: <skill-id>] | decision: <what> | rationale: <why> | [related_learning_ids: LRN-XXXX] | [tag: UNCERTAIN]
```

## [UNCERTAIN] tag
Use when you made an assumption instead of confirming a fact. Include:
- What you assumed
- What evidence would confirm or refute it
- Impact if the assumption is wrong

Quality gate reviews every `[UNCERTAIN]` entry and decides: resolve, accept as WARN, or FAIL.

## Entries
- <iso-timestamp> | agent: ai-pipeline-brainstorm | decision: mapped AC-1 to SC-1 + SC-2 (split by success and failure paths) | rationale: single criterion conflated two observable outcomes
- <iso-timestamp> | agent: ai-pipeline-red-test | decision: used WireMock-style stub for external client | rationale: real endpoint not available in CI
- <iso-timestamp> | agent: ai-pipeline-green-code | tag: UNCERTAIN | decision: assumed id field is numeric | rationale: contract shows string, but all sample payloads are numeric | impact_if_wrong: validation rejects valid ids
