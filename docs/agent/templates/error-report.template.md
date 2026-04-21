# Error Report

story_id: <story-id>
failed_stage: brainstorm | red_test | green_code | refactor | quality_gate
failed_at: <iso-timestamp>
worktree_preserved_at: .agent-runs/<story-id>
branch: story/<story-id>

## Failure evidence
- Paste or link: test output, stack trace, failed self-check item, build error, gate verdict
- Files touched during the failed stage (from handoff.md):
  -

## Attempted fix
- What, if anything, was retried
- Why the retry was allowed (transient tooling only) or not attempted

## Root cause hypothesis
- Best current explanation
- What evidence would confirm or refute it

## Next actions
1. Concrete ordered list — what a human or retry should do
2. ...

## Related learnings
- LRN-XXXX (if any existing learnings predicted this failure)
