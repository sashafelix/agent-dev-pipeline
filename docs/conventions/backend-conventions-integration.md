# Backend Conventions — External Integrations

**Scope: code that calls external services, brokers, object stores or file-transfer systems.** Apply the target stack's supported client libraries and existing project conventions. Integration helpers inherit the calling stage's authority; verification roles do not edit story code.

## Adapter boundary

- Place each external dependency behind a small application-owned adapter.
- Keep transport models separate from domain/API models; validate and map fields explicitly.
- Reuse existing client configuration, authentication and tracing rather than creating an unconfigured client per call.
- Declare base URLs, credentials, TLS policy, connection/read timeouts and response-size limits in project configuration. Never disable certificate verification as a connectivity fix.
- For Spring projects, use the project's supported configured client builder; bare client construction may bypass trace propagation and project interceptors.

## Reliability

- Bound timeouts and total retry budgets; classify transient and deterministic failures.
- Retry a write only when its idempotency contract makes that safe.
- Preserve cancellation and propagate terminal failures; returning a success-shaped value after catching an exception hides failed work.
- Record enough non-sensitive context to diagnose the failed operation.
- Keep remote I/O outside database transactions; validate/fetch first, then perform a bounded local write unit. Define partial-failure and replay behaviour explicitly.

## Logging

Log operation, outcome, duration and an approved correlation identifier. Do not dump request headers, full URLs with query values, payloads, tokens or raw responses. An allowlist of safe fields is preferable to attempting to sanitize entire objects. Newline sanitization is not secret redaction.

```java
log.info("External lookup completed, outcome: {}, durationMs: {}", outcome, durationMs);
```

## XML and archives

Follow `backend-conventions-security.md` for hardened XML parsing. Feed JAXB from a hardened parser/source; do not catch and ignore failed security settings. Reject unsafe archive paths and enforce entry/expanded-size limits before processing. Close streams deterministically and keep download/decompression outside database transactions.

## Configuration

Use project-specific service names and approved environment/secret references, for example:

```yaml
external-service:
  base-url: ${EXTERNAL_SERVICE_BASE_URL}
  api-key: ${EXTERNAL_SERVICE_API_KEY}
```

These names are illustrative; they are not environment variables required by the pipeline.

## Verification and evidence

- Mock application-owned adapters in focused unit tests.
- Use controlled HTTP/broker/database test infrastructure to verify actual serialization, authentication headers, timeouts, cancellation and error mapping.
- Cover negative responses, malformed/oversized input, rate limits and retry/idempotency behaviour.
- Record command results, contract impact and any unresolved issue in canonical stage evidence and the append-only decision log.
