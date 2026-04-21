# Skill: skill-compliance

## Purpose
Capture traceable evidence for security, quality, and release controls. Every compliance claim must link to a specific file, test, commit, or contract.

## When invoked
- By `ai-pipeline-quality-gate` during the final VERIFY stage.
- By `ai-pipeline-green-code` when a story touches a regulated concern (auth, PII, audit logging, cryptography, financial data).

## Reads
- `docs/conventions/backend-conventions-general.md`
- `docs/conventions/backend-conventions-quality-ops.md`
- `docs/conventions/backend-conventions-security.md`
- `docs/agent/learnings.md` (filter by `compliance:*`, `security:*`, `audit:*`)
- Run folder: `handoff.md`, `quality-gates.md`, `decision-log.md`, `brainstorm.md`
- RAG: `--source standards_it_security`, `--source standards_it_iam`, `--source standards_it_ai`

## Writes
- Compliance notes in `docs/agent/runs/{story_id}/decision-log.md`
- Evidence summary block inserted into `quality-gates.md` by the calling agent

## Evidence Checklist

Every entry below must have a concrete link (file path, test name, commit, migration ID, RAG `source_ref`). No hand-wavy "we follow the standard" claims.

### 1. Security controls
- [ ] Authentication required on new endpoints? Proof: `@PreAuthorize` on controller, security test asserting 401/403.
- [ ] Authorization correct per role? Proof: positive + negative test per role.
- [ ] Input validation? Proof: `@Valid` annotation + negative test for invalid payload.
- [ ] Output sanitization for sensitive data? Proof: `LogSanitizer` usage + log assertion.
- [ ] Secrets handling? Proof: env-var reference, no literal in config.

### 2. Audit + traceability
- [ ] Audit log entry for regulated operations? Proof: logger call + test asserting log output.
- [ ] Correlation ID propagated? Proof: `skill-observability` configuration + integration test.
- [ ] Created/updated columns on new entities per `backend-conventions-entity-mapping`? Proof: migration DDL.

### 3. Data handling
- [ ] PII/PHI fields identified? Proof: list in decision-log.
- [ ] PII not logged? Proof: `LogSanitizer` usage + negative log test.
- [ ] PII not returned in public-facing DTOs? Proof: DTO shape review + contract test.
- [ ] Data retention rule considered? Proof: cleanup job, TTL, or explicit decision-log entry "not applicable because ...".

### 4. Contract compatibility
- [ ] OpenAPI diff checked? Proof: `skill-contract-guard` output in handoff.
- [ ] DB migration backward-compatible? Proof: migration type in `skill-database` safety matrix.
- [ ] Event schema (Kafka) backward-compatible? Proof: schema registry diff.

### 5. Test evidence (mandatory matrix)
- [ ] Unit tests cover changed business logic.
- [ ] Integration test if external systems involved.
- [ ] Security test if authz touched.
- [ ] Coverage ≥ 80% on touched modules (no regression).

### 6. Release-readiness
- [ ] Feature flag required? Documented + test asserts both states.
- [ ] Rollback plan? Documented in `skill-devops` evidence or decision-log.
- [ ] Dependencies on other services/stories? Documented with story IDs.

## Evidence Summary Block

The calling agent inserts this into `quality-gates.md`:

```markdown
## Compliance Evidence

| Control | Status | Evidence |
| --- | --- | --- |
| AuthN on endpoint | ✓ | `OrderControllerTest#create_unauthenticated_returns401` |
| AuthZ per role | ✓ | `OrderControllerTest#create_asClerk_returns403` |
| Input validation | ✓ | `OrderControllerTest#create_invalidPayload_returns400` |
| Audit log | ✓ | `OrderServiceTest#create_logsAuditEntry` |
| PII sanitization | ✓ | `LogSanitizerTest#sanitize_maskCustomerId` |
| OpenAPI compatible | ✓ | `skill-contract-guard` output → `handoff.md` |
| Coverage ≥ 80% | ✓ | JaCoCo report → `target/site/jacoco/` |
```

Every row with `✗` or `WARN` must be accompanied by an explicit justification in decision-log and an approval note.

## Guardrails
- Evidence must be traceable to a file, test, or commit. "We followed the standard" is not evidence.
- No PASS claim without specific proof.
- No skipping an item; if inapplicable, explicitly state "N/A because {reason}" in decision-log.
- If a control conflicts with the story scope (e.g., PII rule blocks a feature), halt and escalate — do not silently downgrade.
