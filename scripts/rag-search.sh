#!/usr/bin/env bash
# rag-search.sh — Query the AI-PIPELINE RAG index in OpenSearch
#
# Usage:
#   ./scripts/rag-search.sh "search query" [--source SOURCE] [--size N] [--index NAME]
#
# Examples:
#   ./scripts/rag-search.sh "Java security best practices"
#   ./scripts/rag-search.sh "authentication" --source standards_company_java
#   ./scripts/rag-search.sh "warehouse order" --source jira --size 10
#
# Sources available (see docs/skills/skill-rag-search.md for full catalog):
#   standards_it_security   (~1280 docs) IT security standards
#   standards_it_iam        (~300 docs)  IAM / identity & access management
#   standards_it_swdev      (~110 docs)  Software development standards
#   jira                    (~100 docs)  Jira stories and context
#   standards_company_java  (~65 docs)   Company Java coding standards
#   standards_it_ai         (~50 docs)   AI usage standards
#   access_db               (~30 docs)   Access database records
#   confluence              (~25 docs)   Confluence documentation
#
# Environment:
#   OPENSEARCH_URL              default: http://localhost:9200
#   OPENSEARCH_USER             optional, basic auth username
#   OPENSEARCH_PASS             optional, basic auth password
#   OPENSEARCH_CACERT           optional, path to CA bundle for TLS
#   OPENSEARCH_INSECURE         optional, set to "1" to skip TLS verification (dev only)
#   RAG_TIMEOUT                 default: 10 (seconds)
#   RAG_REQUIRED                optional, set to "1" to make RAG unavailability a hard error
#
# Exit codes (agents interpret these):
#   0  success, results printed
#   1  usage error / malformed arguments
#   2  OpenSearch unavailable (connect/DNS/timeout) — advisory, agents may proceed
#   3  OpenSearch returned an error response (auth, index missing, bad query)
#   4  auth failed (401/403)

set -euo pipefail

# --- Parse arguments ---
QUERY=""
SOURCE=""
SIZE=5
INDEX="ai-pipeline-rag"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)  SOURCE="$2"; shift 2 ;;
    --size)    SIZE="$2"; shift 2 ;;
    --index)   INDEX="$2"; shift 2 ;;
    --help|-h)
      head -35 "$0" | tail -33
      exit 0
      ;;
    *)
      if [[ -z "$QUERY" ]]; then
        QUERY="$1"
      else
        QUERY="$QUERY $1"
      fi
      shift
      ;;
  esac
done

if [[ -z "$QUERY" ]]; then
  echo "Usage: rag-search.sh \"query text\" [--source SOURCE] [--size N] [--index NAME]" >&2
  echo "Run with --help for full usage." >&2
  exit 1
fi

OPENSEARCH_URL="${OPENSEARCH_URL:-http://localhost:9200}"
RAG_TIMEOUT="${RAG_TIMEOUT:-10}"
RAG_REQUIRED="${RAG_REQUIRED:-0}"

# Build curl flags
CURL_FLAGS=(-s --connect-timeout "${RAG_TIMEOUT}" --max-time "$((RAG_TIMEOUT * 2))")

# Auth
AUTH_FLAG=()
if [[ -n "${OPENSEARCH_USER:-}" && -n "${OPENSEARCH_PASS:-}" ]]; then
  AUTH_FLAG=(-u "${OPENSEARCH_USER}:${OPENSEARCH_PASS}")
fi

# TLS
if [[ -n "${OPENSEARCH_CACERT:-}" ]]; then
  CURL_FLAGS+=(--cacert "${OPENSEARCH_CACERT}")
fi
if [[ "${OPENSEARCH_INSECURE:-0}" == "1" ]]; then
  CURL_FLAGS+=(-k)
fi

warn_unavailable() {
  local msg="$1"
  if [[ "$RAG_REQUIRED" == "1" ]]; then
    echo "ERROR: RAG unavailable — ${msg}" >&2
    echo "RAG_REQUIRED=1 set; failing." >&2
    exit 2
  else
    echo "WARN: RAG unavailable — ${msg}" >&2
    echo "WARN: Continuing without RAG context. Set RAG_REQUIRED=1 to make this fatal." >&2
    exit 2
  fi
}

# --- Preflight: is OpenSearch reachable? ---
PING=$(curl "${CURL_FLAGS[@]}" "${AUTH_FLAG[@]}" -o /dev/null -w "%{http_code}" "${OPENSEARCH_URL}/" 2>/dev/null || true)

case "$PING" in
  200)
    : # reachable
    ;;
  401|403)
    echo "ERROR: OpenSearch auth rejected (HTTP ${PING}) at ${OPENSEARCH_URL}" >&2
    echo "Check OPENSEARCH_USER / OPENSEARCH_PASS." >&2
    exit 4
    ;;
  000|"")
    warn_unavailable "cannot reach ${OPENSEARCH_URL} (connect/DNS/timeout)"
    ;;
  *)
    warn_unavailable "unexpected ping status ${PING} from ${OPENSEARCH_URL}"
    ;;
esac

# Escape double quotes in query for JSON safety
SAFE_QUERY=$(echo "$QUERY" | sed 's/"/\\"/g')

# Build query body — multi_match on title+text, optional source filter
if [[ -n "$SOURCE" ]]; then
  BODY=$(cat <<EOF
{
  "size": ${SIZE},
  "_source": ["id", "source", "source_ref", "title", "text", "updated_at"],
  "query": {
    "bool": {
      "must": {
        "multi_match": {
          "query": "${SAFE_QUERY}",
          "fields": ["title^2", "text"],
          "type": "best_fields"
        }
      },
      "filter": {
        "term": { "source": "${SOURCE}" }
      }
    }
  }
}
EOF
)
else
  BODY=$(cat <<EOF
{
  "size": ${SIZE},
  "_source": ["id", "source", "source_ref", "title", "text", "updated_at"],
  "query": {
    "multi_match": {
      "query": "${SAFE_QUERY}",
      "fields": ["title^2", "text"],
      "type": "best_fields"
    }
  }
}
EOF
)
fi

RESPONSE=$(curl "${CURL_FLAGS[@]}" -X POST \
  "${AUTH_FLAG[@]}" \
  -H "Content-Type: application/json" \
  "${OPENSEARCH_URL}/${INDEX}/_search" \
  -d "${BODY}" 2>&1) || {
    warn_unavailable "query failed: ${RESPONSE}"
  }

# Check for errors
if echo "$RESPONSE" | grep -q '"error"'; then
  echo "--- OpenSearch Error ---" >&2
  echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE" >&2
  exit 3
fi

# Pretty-print hits
echo "$RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
hits = data.get('hits', {}).get('hits', [])
total = data.get('hits', {}).get('total', {}).get('value', 0)
if not hits:
    print('No results found.')
    sys.exit(0)
print(f'Found {len(hits)} of {total} matching document(s):')
print('---')
for i, hit in enumerate(hits, 1):
    src = hit.get('_source', {})
    score = hit.get('_score', 0)
    title = src.get('title', 'untitled')
    source = src.get('source', '')
    source_ref = src.get('source_ref', '')
    text = src.get('text', '')
    if len(text) > 1500:
        text = text[:1500] + '...'
    print(f'[{i}] (score: {score:.4f}) [{source}] {title}')
    if source_ref:
        print(f'    ref: {source_ref}')
    print(text)
    print('---')
" 2>/dev/null || echo "$RESPONSE"
