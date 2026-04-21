# Backend Conventions — General

**Scope: backend stacks.** Apply this file when `run-context.md > stack` is `backend-*` (Java/Spring, Node, Python, Go, …). For other stacks, follow the stack's own convention file under `docs/conventions/` (or derive from the existing project code when no convention file exists). The stack-agnostic RGR flow lives in `backend-conventions-rgr.md`.

The `backend-conventions-*` files below are currently Java/Spring-centric (the historical reference stack). Treat the *principles* (layering, explicit error paths, log sanitization, test boundaries, coverage targets) as portable; translate the *mechanisms* to your stack.

## Load Specialized Conventions When Needed
- `docs/conventions/backend-conventions-java-style.md`: function/class formatting for Java code changes.
- `docs/conventions/backend-conventions-testing-style.md`: test formatting and test-type expectations (Java/Spring examples; principles generalize).
- `docs/conventions/backend-conventions-database.md`: Flyway/migration rules (principles generalize to Liquibase/Drizzle/Prisma/Alembic — see `skill-database`).
- `docs/conventions/backend-conventions-entity-mapping.md`: entity/repository/mapper rules.
- `docs/conventions/backend-conventions-api-service.md`: controller/service contract rules.
- `docs/conventions/backend-conventions-security.md`: auth/authz and secure coding rules.
- `docs/conventions/backend-conventions-integration.md`: external adapter and reliability rules.
- `docs/conventions/backend-conventions-quality-ops.md`: contract guard, observability, devops, compliance.

## Reference Stack Baseline
The examples in these files assume the historical reference stack below. Your project may differ — follow the existing project's versions/frameworks rather than these defaults, and record any deviation in `decision-log.md`.
- Java 21
- Spring Boot 3.4.x
- Maven
- PostgreSQL + Flyway
- MapStruct + Lombok

## Architecture
- Layered structure: `api -> service -> model (dto/entity/repository/mapper) -> config -> utils`.
- Keep controllers thin, business logic in services.
- Never expose JPA entities directly via API.

## Coding Rules
- Constructor injection only (`@RequiredArgsConstructor` preferred).
- Keep methods focused; extract private helpers when needed.
- Keep naming explicit and domain-driven.
- Log only meaningful events; sanitize user-controlled values.

## Data + Mapping
- Request/response DTO separation.
- Use MapStruct for mappings.
- Entity relationships explicit; avoid lazy-load pitfalls in API paths.

## Error Handling
- Use domain exceptions.
- Use global exception handling for consistent API error payloads.

## Security Basics
- Explicit role checks.
- Fail-closed auth behavior.
- No secrets in code/config tracked in repo.

## Testing + TDD
- Mandatory BRAINSTORM -> RED -> GREEN -> REFACTOR -> VERIFY.
- Add/adjust tests for each behavior change.
- Keep test names behavior-focused (`method_condition_expectedBehavior` in JUnit; adapt to the stack's convention).

## Quality Gates
- Tests pass.
- Coverage no-regression (target 80%+ for touched modules).
- No blocker/critical findings.

## Docs + Handoff
- Update run artifacts in `docs/agent/runs/{story_id}/`.
- Add key design decisions to story decision log.



