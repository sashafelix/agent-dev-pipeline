# Backend Conventions — Testing Style

**Scope: backend stacks** (invoke when `run-context.md > stack` is `backend-*`; the *Mocking Boundaries* and *Test Quality Rules* sections at the bottom are universal).

Examples below target JUnit 5 + Spring's `@WebMvcTest` / `@SpringBootTest` / `@WithMockUser`. The *principles* — behavior-focused naming, Arrange-Act-Assert, one primary assertion per test, negative-path coverage, integration over mocking-what-you-don't-own, deterministic independent tests — apply to any test framework. Translate mechanisms:
- Vitest / Jest (Node/React): `describe/it`, MSW for API mocking, React Testing Library
- PyTest (Python): fixtures + `parametrize`, `pytest-django` or FastAPI `TestClient`
- Go `testing`: table-driven tests, `httptest`
- Playwright / Cypress: e2e over authenticated flows

Applies to: `ai-pipeline-red-test`, `ai-pipeline-green-code`, `ai-pipeline-refactor`, `ai-pipeline-security`, `ai-pipeline-contract-guard`.

## Naming
- Test method format: `method_condition_expectedBehavior`.
- Name should describe observable behavior, not implementation.

### Examples
- `index_withUserRole_shouldReturnAllOverview`
- `import_withoutUserRole_shouldNotAbleToImport`

## Test Structure
- Use Arrange -> Act -> Assert (or Given -> When -> Then) consistently.
- One primary behavior assertion per test; keep tests focused.
- Add negative-path tests for validation/auth/error scenarios.

## Test Types by Change

### Controller Tests (`@WebMvcTest`)
```java
@WebMvcTest(controllers = OutletController.class)
@Import(MethodSecurityConfig.class)
class OutletControllerTest {
    @Autowired
    private MockMvc mvc;
    
    @MockBean
    private OutletService outletService;
    
    @BeforeEach
    void setUp() {
        this.mvc = MockMvcBuilders
            .webAppContextSetup(webApplicationContext)
            .apply(springSecurity())
            .defaultRequest(put("/hst/outlet").with(csrf()))
            .build();
    }
}
```

### Service Tests (Focused)
```java
@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = OutletService.class)
class OutletServiceTest {
    @Autowired
    OutletService outletService;
    
    @MockBean
    private OutletRepository outletRepository;
    
    @MockBean
    private OutletMapper outletMapper;
}
```

### Security Tests
- Test with role: `@WithMockUser(username = "user", authorities = "User")`
- Test without role: `@WithMockUser(username = "user", authorities = "NO_USER_ROLE")`
- Test anonymous: `@WithAnonymousUser`

```java
@Test
@WithMockUser(username = "boo", authorities = "User")
void import_withUserRole_shouldAbleToImport() throws Exception {
    when(importService.importHSTData()).thenReturn(true);
    mvc.perform(get("/hst/import"))
        .andExpect(status().isOk())
        .andExpect(content().string("done"));
    verify(importService, times(1)).importHSTData();
}

@Test
@WithAnonymousUser
void index_withAnonymousUser_shouldReturnUnauthorizedError() throws Exception {
    mvc.perform(get("/hst"))
        .andExpect(status().isUnauthorized());
}
```

## MockMvc Patterns

### Request Building
```java
mvc.perform(get("/hst/outlet/{id}/{buno}", 1, "boo"))
    .andExpect(status().isOk())
    .andExpect(jsonPath("$.id", is(1)))
    .andReturn();

mvc.perform(post("/api/cases")
    .contentType(MediaType.APPLICATION_JSON)
    .content(objectMapper.writeValueAsString(request)))
    .andExpect(status().isCreated());
```

### JSON Assertions
```java
.andExpect(jsonPath("$", hasSize(1)))
.andExpect(jsonPath("$.id", is(1)))
.andExpect(jsonPath("$.name", is("Test")))
```

## Static Utility Mocking
Use `MockedStatic<>` for static methods:
```java
@Test
void it_should_getAll_outlets() {
    try (MockedStatic<UserContextHolder> mockedStatic = mockStatic(UserContextHolder.class)) {
        mockedStatic.when(() -> UserContextHolder.hasUserRole("User")).thenReturn(true);

        // test logic

        var result = outletService.overview();
        assertThat(result.getData()).hasSize(1);
    }
}
```

## Test Data Factory Methods
Create reusable test data builders:
```java
private static OutletOverview mockOutletOverview() {
    OutletOverview outlet = new OutletOverview();
    outlet.setId(1L);
    outlet.setName("Test Outlet");
    outlet.setOutletStatus(true);
    return outlet;
}
```

## RED Stage Rules
- New tests must fail for expected reason before implementation.
- Document failing evidence in `handoff.md`.
- Failure reason must match expected business gap.

## GREEN/REFACTOR Rules
- GREEN: pass tests with minimum implementation.
- REFACTOR: keep all tests green, no behavior change.

## Assertions and Mocks
- Prefer AssertJ assertions: `assertThat(result).isEqualTo(expected)`.
- Use Mockito for mocking: `when(mock.method()).thenReturn(value)`.
- Verify interactions: `verify(mock, times(n)).method()`.

## Test Configuration
```yaml
# src/test/resources/application.yml
spring:
  datasource:
    url: jdbc:h2:mem:testdb;MODE=PostgreSQL
    driver-class-name: org.h2.Driver
  flyway:
    enabled: false
  jpa:
    hibernate:
      ddl-auto: update
    database-platform: org.hibernate.dialect.PostgreSQLDialect
```

## Minimal Test Skeleton
```java
@Test
void createCase_withInvalidPayload_shouldReturnBadRequest() throws Exception {
    // Arrange
    var payload = "{}";

    // Act + Assert
    mvc.perform(post("/api/cases")
        .contentType(MediaType.APPLICATION_JSON)
        .content(payload))
        .andExpect(status().isBadRequest());
}
```

## Mocking Boundaries
- **Mock your own code**, not third-party libraries. Use `@MockBean` for your own services/repositories.
- **Don't mock what you don't own**: for external REST clients, message brokers, or databases, prefer integration tests with `@SpringBootTest`, WireMock, or Testcontainers.
- If mocking an external API is unavoidable, mock at the adapter boundary (your wrapper service), not the HTTP client directly.

## Test Quality Rules
- Tests should test behavior, not implementation details. Refactoring production code should not break tests.
- Avoid testing private methods; test through the public interface.
- Each test should be independently runnable and deterministic (no shared mutable state, no ordering dependencies).


