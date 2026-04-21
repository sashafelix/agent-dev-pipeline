# Skill: skill-codebase-comprehension

## Purpose
Systematically read and understand existing code before making changes. Ensures agents never write blind.

## When invoked
- At the start of GREEN and REFACTOR stages, before any file writes.
- Optionally by RED stage when test targets touch complex existing code.

## Reads
- `docs/agent/runs/{story_id}/detailed-plan.md` (to identify change scope)
- `docs/conventions/backend-conventions-general.md`
- All files in the change scope and their direct dependencies

## Writes
- Comprehension summary appended to `docs/agent/runs/{story_id}/decision-log.md`

## Steps
1. Identify all files in the change scope from `detailed-plan.md`.
2. Read each file and its direct dependencies (imports, called services, injected beans).
3. Trace the call chain: controller → service → repository → entity for the feature area.
4. Search the codebase for similar patterns (naming, structure, error handling, test style).
5. Identify: existing utilities to reuse, patterns to match, anti-patterns to avoid.
6. Document findings as a brief comprehension summary in the decision-log.

## Output format
```markdown
### Comprehension Summary
- **Files read**: [list]
- **Call chain**: [traced path]
- **Patterns to follow**: [list existing conventions observed]
- **Reusable utilities found**: [list or "none"]
- **Risks/conflicts with plan**: [list or "none"]
```

## Guardrails
- Do not write any production or test code during comprehension.
- Flag any conflicts between the plan and existing code structure.
- If the codebase has no prior examples for the planned pattern, note it explicitly.

