# Skill Catalog

Skills are reusable capabilities called by stage agents. They do not own stage transitions.

The pipeline is **stack-agnostic**. Skills fall into two groups:
1. **Stack-neutral**: apply to any stack. Called on every run when relevant.
2. **Stack-specific**: apply only when the target `stack` matches (e.g., Java/Spring backend). The calling agent decides based on `run-context.md > stack` and `scope_tags`.

## Stack-neutral skills
- `skill-codebase-comprehension.md` — systematic read-and-understand before any write
- `skill-project-scaffold.md` — bootstrap module/project structure (stack-agnostic with mapping table)
- `skill-api-service.md` — HTTP/RPC surface patterns
- `skill-security.md` — auth/authz + security tests
- `skill-integration.md` — resilient external adapters
- `skill-validation.md` — input validation at boundaries
- `skill-exception-handling.md` — centralized error handling
- `skill-test-maintenance.md` — deterministic, readable tests
- `skill-contract-guard.md` — API/DTO/DB compatibility checks
- `skill-observability.md` — logs/metrics/tracing quality
- `skill-devops.md` — CI/CD + runtime config changes
- `skill-compliance.md` — traceable evidence for release controls
- `skill-decision-index.md` — compact update of `decision-index.md`
- `skill-rag-search.md` — query RAG (with fallback semantics)

## Stack-specific skills (invoke only when the stack matches)
- `skill-database.md` — SQL migrations + safety matrix *(stacks with a relational persistence layer; Flyway examples, generalizes to Liquibase/Drizzle/Prisma/Alembic)*
- `skill-entity-mapping.md` — entity / repository / DTO / mapper boundaries *(ORM-backed backends)*
- `skill-transaction-policy.md` — transactional boundaries *(backends with DB writes)*
- `skill-java-cleanup.md` — dead code, file size, Rule of Three, naming *(Java-style cleanup; the principles generalize; agent may apply analogous cleanup tools for other stacks if no equivalent skill exists)*

## Conditional skills (create when needed)
- `skill-scheduling.md` — when scheduled tasks / cron jobs are in scope (backend-cron, CI schedules, client polling)
- `skill-caching.md` *(future)*
- `skill-xml-jaxb.md` *(future — XML import/export)*
- Frontend-specific skills (`skill-component-patterns`, `skill-state-management`, `skill-a11y`) *(future, as needed)*

## Shared rules
- Follow `CLAUDE.md`. Apply `docs/conventions/backend-conventions-general.md` only when the stack is backend.
- Write only within the scope requested by the calling agent.
- Record non-trivial decisions to `docs/agent/runs/{story_id}/decision-log.md` with rationale and related learning IDs.
- Read `docs/agent/learnings.md` at start, **filtered by `scope_tags`** matching the task (especially `stack:*`); append reusable candidate learnings with evidence.
- Use `{project_root}` from run-context for all file paths.
- No skill may unilaterally change stage; return control to the calling agent.
