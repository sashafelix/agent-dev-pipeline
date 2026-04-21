# Skill: skill-observability

## Purpose
Add or validate logs/metrics/traces for key backend business flows.

## Reads
- `docs/conventions/backend-conventions-general.md`
- `docs/conventions/backend-conventions-quality-ops.md`
- `docs/conventions/backend-conventions-security.md`

## Writes
- observability code/config changes in scope
- decision notes in `docs/agent/runs/{story_id}/decision-log.md`

## Conventions

### Correlation ID
- Every request must have a correlation ID (trace ID).
- Use Spring Cloud Sleuth or Micrometer Tracing for automatic propagation.
- Include correlation ID in all log entries and error responses.
- Header: `X-Correlation-ID` or `X-Request-ID`.

### Structured Logging
Use SLF4J with structured key-value pairs:
```java
log.info("Processing order", kv("orderId", orderId), kv("userId", userId));
```

Required log fields for business events:
| Field | Description |
|-------|-------------|
| `correlationId` | Request trace ID |
| `action` | Business action name |
| `entityType` | Entity being acted on |
| `entityId` | Entity identifier |
| `outcome` | success / failure |
| `durationMs` | Processing time (for perf-critical flows) |

### Log Levels
| Level | Use for |
|-------|---------|
| ERROR | Unexpected failures requiring attention |
| WARN | Recoverable issues, degraded behavior |
| INFO | Business events, request summaries |
| DEBUG | Detailed flow for troubleshooting |
| TRACE | Very verbose, usually disabled in prod |

### Sensitive Data Redaction
Use `LogSanitizer` for all user-supplied input:
```java
log.info("Request: {}", LogSanitizer.getSanitizedStringForLogging(input));
```

Never log:
- Passwords, tokens, secrets
- Full credit card numbers
- Personal identifiers (SSN, etc.)
- Raw request bodies containing PII

### Metrics
- Use Micrometer for custom metrics.
- Name pattern: `ai_pipeline.{domain}.{action}` (e.g. `ai_pipeline.order.created`).
- Tag with relevant dimensions (status, type, etc.).

### Error Events
For error logging, always include:
```java
log.error("Failed to process order", kv("orderId", orderId), kv("errorType", e.getClass().getSimpleName()), e);
```

## Guardrails
- No sensitive data in telemetry.
- Keep diagnostics actionable and low-noise.
- Test that correlation IDs propagate through async flows.
- Verify redaction in log output for sensitive fields.





