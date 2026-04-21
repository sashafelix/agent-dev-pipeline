# Run Context

```yaml
story_id: <story-id>          # Any identifier: jira key, feature slug, or generated id (e.g., FEAT-20260420-login)
date: <iso-date>
project_root: <path>          # e.g., apps/backend, services/inventory, apps/web — wherever the change lives
stack: <stack>                # e.g., java-spring, node-express, react, nextjs, python-fastapi
worktree_path: .agent-runs/<story-id>
branch: story/<story-id>
goal: ...
scope_in:
  - ...
scope_out:
  - ...
scope_tags:                   # used to filter learnings.md and decision-index.md
  - stack:<stack>
  - domain:<domain>
  - layer:<layer>
contracts:
  - ...
constraints:
  - ...
current_stage: brainstorm     # brainstorm | red_test | green_code | refactor | quality_gate | done | failed
owner_agent: ai-pipeline-rgr-orchestrator
inputs:
  - docs/agent/runs/<story-id>/plan-input.md
  - docs/agent/learnings.md
outputs:
  - docs/agent/runs/<story-id>/brainstorm.md
  - docs/agent/runs/<story-id>/detailed-plan.md
  - docs/agent/runs/<story-id>/handoff.md
  - docs/agent/runs/<story-id>/quality-gates.md
next_agent: ai-pipeline-brainstorm
```
