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
scope_tags:                   # used to filter learnings.json and decision-index.md
  - stack:<stack>
  - domain:<domain>
  - layer:<layer>
contracts:
  - ...
constraints:
  - ...
current_stage: prepare     # prepare | brainstorm | plan | analyze | red_test | green_code | refactor | quality_gate | converge | done | failed
owner_agent: ai-pipeline-rgr-orchestrator
inputs:
  - docs/agent/runs/<story-id>/plan-input.md
  - docs/agent/learnings.json
outputs:                       # canonical JSON; Markdown files are projections
  - docs/agent/runs/<story-id>/repository-intelligence.json
  - docs/agent/runs/<story-id>/profile-resolution.json
  - docs/agent/runs/<story-id>/brainstorm.json
  - docs/agent/runs/<story-id>/detailed-plan.json
  - docs/agent/runs/<story-id>/lane-resolution.json
  - docs/agent/runs/<story-id>/analysis-report.json
  - docs/agent/runs/<story-id>/red-result.json
  - docs/agent/runs/<story-id>/green-result.json
  - docs/agent/runs/<story-id>/refactor-result.json
  - docs/agent/runs/<story-id>/context-<stage>.json
  - docs/agent/runs/<story-id>/events.jsonl
  - docs/agent/runs/<story-id>/quality-gates.json
  - docs/agent/runs/<story-id>/convergence-report.json
  - docs/agent/runs/<story-id>/brainstorm.md
  - docs/agent/runs/<story-id>/detailed-plan.md
  - docs/agent/runs/<story-id>/handoff.md
  - docs/agent/runs/<story-id>/quality-gates.md
next_agent: ai-pipeline-prepare
```
