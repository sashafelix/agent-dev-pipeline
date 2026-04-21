# Backend Conventions — Database and Flyway

**Scope: backend stacks with a SQL persistence layer.** Examples below target PostgreSQL + Flyway. The *safety principles* (forward-only migrations, backfill before NOT NULL, explicit PK/FK/index naming, auditable DDL) generalize to Liquibase / Drizzle / Prisma Migrate / Alembic / ActiveRecord / Knex. See `docs/skills/skill-database.md` for the stack-agnostic variant.

Applies to: `ai-pipeline-database`, `ai-pipeline-contract-guard`, `ai-pipeline-green-code` (when migration changes are needed).

## Migration Naming
- Format: `V{YYYYMMDDHHMM}__description.sql`
- Examples:
  - `V202310131548__create_schema.sql`

## Schema + DDL Rules
- Use schema `ai_pipeline`.
- Forward-only migrations.
- Deterministic SQL (no environment-specific behavior).
- Explicit PK/FK/index names.

## Schema Setup Pattern
```sql
create schema if not exists ai_pipeline;
create sequence if not exists {entity}_seq start 1 increment 1 minValue 1;
```

## Naming Conventions

| Element | Pattern | Example |
|---------|---------|---------|
| Schema | lowercase | `hst`, `ai_pipeline` |
| Table | snake_case | `outlet`, `legal_entity` |
| Column | snake_case | `outlet_number`, `date_created` |
| Primary Key | `ID` or `id` | `ID bigserial primary key` |
| Sequence | `{entity}_seq` | `dealer_seq`, `history_seq` |
| Foreign Key | `fk_{table}_{referenced}` | `fk_dealer_legal_entity` |
| Unique Index | `uk_{column}` | `uk_outlet_number` |
| View | descriptive_name | `outlet_overview`, `retail_partners_view` |

## Table Creation Pattern
```sql
CREATE TABLE ai_pipeline.outlet (
    ID                  bigserial primary key,
    OUTLET_NUMBER       VARCHAR(255) NOT NULL,
    NAME                VARCHAR(255) NOT NULL,
    LEGAL_ENTITY_FK     bigint constraint fk_outlet_legal_entity 
                        references ai_pipeline.legal_entity,
    date_created        timestamp DEFAULT now(),
    user_created        character varying(50),
    date_changed        timestamp DEFAULT now(),
    user_changed        character varying(50)
);
```

## Audit Columns (mutable tables)
- `date_created` - timestamp with `DEFAULT now()`, not updatable
- `user_created` - varchar(50), not updatable
- `date_changed` - timestamp with `DEFAULT now()`
- `user_changed` - varchar(50)

## PostgreSQL-Specific Types
- Use `bigserial` for auto-increment primary keys.
- Use `character varying(n)` or `VARCHAR(n)` for strings.
- Use `timestamp` for datetime fields.
- Use `numeric(precision, scale)` for decimal fields.
- Use `boolean` for flags.

## Flyway Configuration
```yaml
spring:
  flyway:
    enabled: true
    validate-on-migrate: true
    baseline-on-migrate: true
    out-of-order: true
    schemas: ai_pipeline
```

## Compatibility
- Document migration impact in story `decision-log.md`.
- Mark breaking vs non-breaking contract impact in `handoff.md`.

## Verification
- Migrations run clean on empty database.
- No hidden manual patch steps.
- Test with H2 in PostgreSQL compatibility mode for unit tests.


