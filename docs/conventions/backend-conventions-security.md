# Backend Conventions — Security

**Scope: applicable backend services.** Spring examples are reference patterns, not a security configuration installed by the pipeline. Follow the target project's approved authentication, authorization and deployment design. Relevant helpers inherit their calling stage's role and write limits; VERIFY inspects and reports only.

## Authentication and authorization

- Use the project's maintained authentication integration and validate credentials before establishing a security context.
- Require authentication by default; define and test role/permission checks for each protected operation.
- In Spring, `@PreAuthorize` requires method security to be enabled. It is authorization, not a replacement for authentication. See [method security](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html).
- Distinguish unauthenticated and forbidden requests using the configured API error contract. Never expose raw authentication exceptions to clients.
- Prefer the framework's supported bearer-token/resource-server integration to an incomplete custom filter. A username helper must handle absent/anonymous authentication; a fallback audit label must never grant authorization.

## HTTP security configuration

A minimal authorization fragment keeps every route authenticated:

```java
http.cors(Customizer.withDefaults())
    .authorizeHttpRequests(auth -> auth.anyRequest().authenticated());
```

This fragment assumes the application separately configures its authentication mechanism, CORS and applicable method security. It intentionally leaves CSRF protection enabled. Disable or narrow CSRF protection only for a reviewed authentication/client model; being stateless alone does not establish that a browser-facing service is safe from CSRF. See [Spring Security CSRF](https://docs.spring.io/spring-security/reference/features/exploits/csrf.html).

Do not make `/actuator/**`, `/v3/**` or `/swagger-ui/**` public by default. If unauthenticated infrastructure probes are required, allow only the exact probe paths under the deployment's network restrictions and suppress sensitive health details. Keep documentation, metrics and other management endpoints subject to explicit policy.

Local development should use test identities or a mock authentication provider. Any deliberate authentication bypass must be isolated from shared environments and production; a profile name alone is not isolation.

## CORS

- Configure explicit approved origins, methods and headers.
- Permit credentials only when required by the client/authentication model.
- Do not use a wildcard origin for credentialed browser access.
- CORS is not authentication and does not constrain server-to-server clients.

## Logging and sensitive data

Choose non-sensitive fields before logging. Omit or explicitly mask credentials, tokens, personal identifiers and raw request/response bodies. Test the actual output for representative sensitive values.

The `LogSanitizer` helper replaces newline, carriage-return and tab characters to limit log injection. It does **not** mask secrets or PII. Parameterized logging also does not redact values automatically.

## XML and external input

Use a hardened parser for untrusted XML: disallow unnecessary DTDs and external entity/schema access, disable XInclude where applicable, and enforce size/depth/expansion limits. Do not silently ignore failures to apply required parser protections. JAXB must receive an appropriately hardened XML source; setting unsupported properties and continuing after failure is not protection.

Validate external archive entry paths and bound entry count, decompressed bytes and expansion ratios before processing. Keep credentials/configuration external to tracked source.

## Verification

- Test allowed and denied roles plus unauthenticated requests using the real security configuration.
- Include CSRF cases when the application uses browser/session authentication.
- Verify management endpoint exposure and error-response content.
- Assert sensitive values are absent from telemetry and responses.
- Record exact commands/results in canonical stage evidence. A helper checklist is not proof by itself.
