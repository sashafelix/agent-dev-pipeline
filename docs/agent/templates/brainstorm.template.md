# Brainstorm

story_id: <story-id>
captured_at: <iso-timestamp>
owner_agent: ai-pipeline-brainstorm
status: draft | locked
input_source: jira | feature-description | user-request | rag-derived | other

## 1. Intent
- What is the user / stakeholder actually trying to achieve?
- What would "done" look like in one sentence?

## 2. Scope
### In scope
-

### Out of scope
-

### Ambiguous / needs confirmation
-

## 3. Declarative Success Criteria
Every SC must be a testable GIVEN/WHEN/THEN assertion. These are the goal state for RED/GREEN.

| SC ID | Statement | Verified by | Source |
| --- | --- | --- | --- |
| SC-1 | GIVEN ... WHEN ... THEN ... | unit \| integration \| contract \| e2e \| security | jira AC-1 \| brainstorm-derived \| compliance-rule |
| SC-2 | GIVEN ... WHEN ... THEN ... | ... | ... |

## 4. Edge Cases Considered
| Case | Applicable? | Expected behavior |
| --- | --- | --- |
| Null / empty input | y/n | |
| Concurrent request | y/n | |
| Downstream failure / timeout | y/n | |
| Boundary values (min/max) | y/n | |
| Unauthorized / forbidden | y/n | |
| Oversized payload | y/n | |
| Malformed payload | y/n | |
| Idempotency / replay | y/n | |

## 5. Assumptions & Unknowns
| ID | Assumption or unknown | [UNCERTAIN]? | Resolution plan |
| --- | --- | --- | --- |
| A-1 | | | |

## 6. Input → Success Criteria Trace
If input has explicit acceptance criteria (e.g., a jira story), map each AC to the SCs covering it.
If input is a free-form feature description, list the extracted intent points and map those.

| Input item (AC / intent point) | Covered by SCs |
| --- | --- |
| AC-1 / intent point #1 | SC-1, SC-2 |

## 7. Halt conditions triggered
- None | [list]

## 8. Self-check
- [ ] Every input item mapped to at least one SC
- [ ] No vague wording in SCs ("properly", "correctly", "should work", "etc.")
- [ ] All `[UNCERTAIN]` items have a resolution plan or explicit halt
- [ ] SCs are observable (a test can fail-then-pass against each)
