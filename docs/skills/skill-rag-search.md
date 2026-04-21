# Skill: skill-rag-search

## Purpose
Retrieve relevant context from the pipeline RAG knowledge base (OpenSearch on localhost:9200) to augment agent decisions with project-specific domain knowledge, company standards, Jira context, and reference material.

## Knowledge Base

| Source | Approx. docs | Description | Use when |
|--------|------|-------------|----------|
| `standards_it_security` | ~1280 | IT security standards | Security decisions, auth patterns, vulnerability checks |
| `standards_it_iam` | ~300 | Identity & access management | Role design, authentication, authorization rules |
| `standards_it_swdev` | ~110 | Software development standards | Architecture decisions, coding standards, SDLC compliance |
| `jira` | ~100 | Jira stories and context | Understanding story history, related work, requirements |
| `standards_company_java` | ~65 | Company Java coding standards | Java conventions, framework choices, code style |
| `standards_it_ai` | ~50 | AI usage standards | AI-related features or compliance |
| `access_db` | ~30 | Access database records | Access control data, permission models |
| `confluence` | ~25 | Confluence documentation | Project documentation, architecture decisions |

Source names reflect whatever the operator loaded into the index. Rename freely to match your environment — agents only care about the `--source` string matching what exists in OpenSearch.

## Document Schema
Each document contains:
- `id` — unique identifier (`{source}:{page_id}:{chunk}`)
- `source` — category (see table above)
- `source_ref` — URL to original document (e.g. Confluence page)
- `title` — document/section title
- `text` — content body
- `embedding` — vector embedding (used internally by OpenSearch)
- `updated_at` — last update timestamp

## How to Invoke

Run the search script from terminal:

```bash
./scripts/rag-search.sh "your search query" [--source SOURCE] [--size N] [--index NAME]
```

**Arguments:**
| Flag | Default | Description |
|------|---------|-------------|
| *(positional)* | *(required)* | Natural language search query |
| `--source` | *(all sources)* | Filter to a specific source (e.g. `jira`, `standards_company_java`) |
| `--size` | `5` | Max results to return |
| `--index` | `ai-pipeline-rag` | OpenSearch index name |

**Examples:**
```bash
# Broad domain search
./scripts/rag-search.sh "warehouse order lifecycle"

# Company Java standards only
./scripts/rag-search.sh "exception handling" --source standards_company_java

# Security standards for auth
./scripts/rag-search.sh "authentication token validation" --source standards_it_security

# Jira context for related stories
./scripts/rag-search.sh "inventory management" --source jira --size 10

# IAM standards for role design
./scripts/rag-search.sh "role based access control" --source standards_it_iam
```

**Environment variables (optional):**
| Var | Default | Description |
|-----|---------|-------------|
| `OPENSEARCH_URL` | `http://localhost:9200` | OpenSearch endpoint |
| `OPENSEARCH_USER` | *(none)* | Basic auth username |
| `OPENSEARCH_PASS` | *(none)* | Basic auth password |
| `OPENSEARCH_CACERT` | *(none)* | Path to CA bundle for TLS verification |
| `OPENSEARCH_INSECURE` | `0` | `1` skips TLS verification (dev only) |
| `RAG_TIMEOUT` | `10` | Connect timeout in seconds |
| `RAG_REQUIRED` | `0` | `1` makes RAG unavailability a hard error |

**Exit codes (agents interpret these):**
| Code | Meaning | Agent behavior |
| --- | --- | --- |
| 0 | Success | Consume results |
| 1 | Usage error | Fix the invocation |
| 2 | OpenSearch unavailable (connect/timeout) | Continue without RAG unless `RAG_REQUIRED=1`; note in decision-log |
| 3 | OpenSearch error response (bad query / index missing) | Adjust query or index; do not silently retry |
| 4 | Auth failed (401/403) | Check `OPENSEARCH_USER`/`OPENSEARCH_PASS`; do not retry blindly |

## Search Strategy

1. **Start broad** — search across all sources for the domain concept.
2. **Narrow by source** — use `--source` to focus on the most relevant category.
3. **Search multiple angles** — try synonyms or related terms if results are insufficient.
4. **Layer searches** — combine a Jira search (for story context) with a standards search (for compliance rules).
5. **Cap results** — use `--size 3` for focused lookups, `--size 10` for exploration.

### Recommended search patterns per agent

| Agent | Recommended searches |
|-------|---------------------|
| `ai-pipeline-rgr-orchestrator` | `--source jira` for story context, `--source confluence` for architecture docs |
| `ai-pipeline-red-test` | `--source jira` for acceptance criteria context, `--source standards_company_java` for test patterns |
| `ai-pipeline-green-code` | `--source standards_company_java` for coding patterns, `--source standards_it_swdev` for architecture, `--source standards_it_security` for security requirements |
| `ai-pipeline-refactor` | `--source standards_company_java` for code quality patterns |
| `ai-pipeline-quality-gate` | `--source standards_it_security` + `--source standards_it_iam` for security review, `--source standards_it_swdev` for compliance |

## Reads
- OpenSearch index on `localhost:9200` (read-only queries)
- `docs/agent/runs/{story_id}/run-context.md` (to understand current story scope)

## Writes
- No file writes. RAG results are consumed in-memory by the calling agent.
- If a RAG result materially influences a design decision, the calling agent should note it in `decision-log.md` with the `source_ref` URL.

## Fallback behavior (RAG unavailable)

RAG is **supplementary, not blocking** by default. The agent protocol when the script exits with code 2:

1. Log a `WARN` entry in `decision-log.md`: `RAG unavailable at {timestamp} — proceeding without RAG context.`
2. Proceed with the stage. Use conventions + learnings + codebase comprehension as the primary inputs.
3. If the story explicitly requires a RAG-sourced rule (e.g., "apply the company Java exception handling standard"), halt and write `error-report.md` with reason `rag_required_unavailable`.
4. Operator may set `RAG_REQUIRED=1` for runs where RAG is truly mandatory; the script then exits non-zero on unavailability.

For exit codes 3 and 4 (OpenSearch returned an error / auth failed), do not silently retry — log in `decision-log.md` and escalate. These indicate a configuration problem, not transient unavailability.

## Guardrails
- Read-only; never write to OpenSearch from agent workflows.
- Do not treat RAG results as authoritative over explicit conventions in `docs/conventions/`. Conventions override RAG when they conflict.
- If RAG results conflict with conventions or learnings, follow conventions and note the conflict in `decision-log.md`.
- RAG unavailability is not a silent failure — always note in `decision-log.md` whether RAG was consulted successfully for the story.
- Do not pass sensitive data (credentials, PII) as search queries. Queries may be logged on the OpenSearch side.
- Always cite `source_ref` when a RAG result drives a decision.
