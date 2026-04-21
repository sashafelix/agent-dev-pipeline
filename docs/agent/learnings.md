# Operational Learnings Register

This file is the single cross-story memory for operational learnings.

## Usage

- All agents read this file at run start and before major tool/setup decisions.
- Agents **filter by scope_tags** matching the current story's domain before acting. Reading 100+ unrelated entries is noise; filtering is the discipline.
- Stage agents (`ai-pipeline-brainstorm`, `ai-pipeline-red-test`, `ai-pipeline-green-code`, `ai-pipeline-refactor`) append `candidate` rows when a reusable rule is discovered.
- `ai-pipeline-quality-gate` curates entries and can promote to `active`, deprecate, or mark `conflicted`.
- Keep entries concise, testable, and scoped with tags.

## How to read this file (agent protocol)

1. Read the `scope_tags` vocabulary below.
2. Identify which tag groups match the current story (e.g., story touches a scheduled job → read entries tagged `scheduling:*`; story on Windows workstation → read `os:windows` entries).
3. Read **only** the filtered rows. Skim others lazily.
4. If a filtered entry is `active`, follow it. If `candidate`, treat as advisory. If `conflicted`, log `[UNCERTAIN]` and proceed with caller discretion.

## Scope tag vocabulary

Use these tag namespaces. A row can have multiple tags, semicolon-separated. Extend the vocabulary as new stacks / domains are exercised — add the new tag here before using it in an entry.

### Stack
- `stack:backend-java`, `stack:backend-node`, `stack:backend-python`, `stack:backend-go`
- `stack:frontend-react`, `stack:frontend-vue`, `stack:frontend-svelte`, `stack:frontend-next`
- `stack:mobile-flutter`, `stack:mobile-react-native`, `stack:mobile-ios`, `stack:mobile-android`
- `stack:infra-terraform`, `stack:infra-pulumi`, `stack:infra-kubernetes`
- `stack:polyglot` (task spans multiple stacks)

### Environment
- `os:windows`, `os:macos`, `os:linux`
- `shell:bash`, `shell:powershell`, `shell:zsh`

### Tooling + build
- `tooling:java`, `tooling:node`, `tooling:python`, `tooling:go`, `tooling:docker`, `tooling:git`
- `build:maven`, `build:gradle`, `build:npm`, `build:pnpm`, `build:vite`, `build:webpack`, `build:bazel`, `build:cargo`, `build:go`
- Framework-specific tags (e.g., `lombok`, `mapstruct`, `react`, `nextjs`, `spring`, `fastapi`, `django`) for known gotchas

### Infrastructure
- `infra:nexus`, `infra:artifactory`, `infra:kafka`, `infra:s3`, `infra:postgres`, `infra:mysql`, `infra:redis`, `infra:opensearch`
- `secrets:vault`, `secrets:k8s`, `secrets:env`

### Code domain
- `domain:api`, `domain:db`, `domain:auth`, `domain:integration`, `domain:scheduling`, `domain:observability`, `domain:ui`, `domain:state`, `domain:routing`, `domain:forms`
- `layer:controller`, `layer:service`, `layer:repository`, `layer:mapper`, `layer:component`, `layer:hook`, `layer:store`, `layer:adapter`

### Practice
- `testing:unit`, `testing:integration`, `testing:contract`, `testing:security`, `testing:e2e`, `testing:visual`, `testing:a11y`
- `migration:flyway`, `migration:liquibase`, `migration:drizzle`, `migration:prisma`, `migration:alembic`
- `style:naming`, `style:exception-handling`, `style:error-boundaries`

### Risk / compliance
- `pii`, `audit`, `breaking-contract`, `deprecation`

## Schema

| Field | Meaning |
| --- | --- |
| `learning_id` | LRN-NNNN, monotonically increasing |
| `status` | `candidate` (new) → `active` (validated) → `deprecated` (superseded) / `conflicted` (clash) |
| `statement` | The rule itself — imperative, testable, one sentence |
| `scope_tags` | Semicolon-separated tags from the vocabulary above |
| `conflict_key` | Short slug for deduplication — two entries with the same key + different statements = conflict |
| `source_story` | Story ID that originated the learning |
| `evidence` | Concrete: file/test/log/date — not "we noticed that..." |
| `owner_agent` | Agent that promoted the entry to its current status |
| `created_at` | ISO timestamp |
| `last_verified_at` | ISO timestamp of most recent story that re-evidenced the rule |
| `supersedes` | LRN-NNNN of a deprecated entry this replaces (or `-`) |

## Lifecycle

- **candidate**: newly observed. Any agent may add. Advisory only.
- **active**: validated by quality-gate on at least one run. Agents should follow.
- **deprecated**: superseded by a newer rule (`supersedes` points back). Do not apply.
- **conflicted**: two `active` entries share a `conflict_key` with contradictory statements. Agents halt, log `[UNCERTAIN]`, escalate to operator.

## Entries

Register is empty. Stage agents append `candidate` rows as reusable rules are discovered; `ai-pipeline-quality-gate` promotes validated entries to `active`. The first entry should be `LRN-0001`.

| learning_id | status | statement | scope_tags | conflict_key | source_story | evidence | owner_agent | created_at | last_verified_at | supersedes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
