# Skill: skill-security

## Purpose
Apply backend security controls for endpoints, data access, and logging.

## Reads
- `docs/conventions/backend-conventions-general.md`
- `docs/conventions/backend-conventions-security.md`
- `docs/conventions/backend-conventions-testing-style.md`

## Writes
- security config and authorization annotations in scope
- security-focused tests in scope
- decision notes in `docs/agent/runs/{story_id}/decision-log.md`

## Security Configuration

### Filter Chain (Non-Local)
```java
@Bean
@Profile("!local")
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http.cors(Customizer.withDefaults())
        .csrf(AbstractHttpConfigurer::disable)
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/swagger-ui/**", "/v3/**", "/actuator/**").permitAll()
            .anyRequest().authenticated())
        .addFilterBefore(customAuthFilter, UsernamePasswordAuthenticationFilter.class);
    return http.build();
}
```

### Filter Chain (Local Development)
```java
@Bean
@Profile("local")
public SecurityFilterChain securityFilterChainLocal(HttpSecurity http) throws Exception {
    http.cors(Customizer.withDefaults())
        .csrf(AbstractHttpConfigurer::disable)
        .authorizeHttpRequests(auth -> auth.anyRequest().permitAll());
    return http.build();
}
```

### Authorization Annotations
```java
@PreAuthorize("hasAuthority('ADMIN')")
@GetMapping("/admin/users")
public List<UserDto> getUsers() { ... }

@PreAuthorize("hasAnyAuthority('USER', 'ADMIN')")
@GetMapping("/orders")
public List<OrderDto> getOrders() { ... }
```

## Log Sanitization Utility

This skill owns the `LogSanitizer` utility to prevent log injection (CWE-117):

```java
public final class LogSanitizer {
    private LogSanitizer() {}

    public static String getSanitizedStringForLogging(@Nullable String input) {
        if (input == null) return "";
        return input
            .replace('\n', '_')
            .replace('\r', '_')
            .replace('\t', '_');
    }
}
```

Usage (mandatory for user input in logs):
```java
log.info("Request: {}", LogSanitizer.getSanitizedStringForLogging(userInput));
```

## Security Testing

### Controller Security Test Pattern
```java
@WebMvcTest(OrderController.class)
@Import(MethodSecurityConfig.class)
class OrderControllerSecurityTest {
    @Autowired
    private MockMvc mvc;

    @Test
    @WithMockUser(authorities = "ADMIN")
    void adminEndpoint_withAdmin_shouldSucceed() throws Exception {
        mvc.perform(get("/api/admin/orders"))
            .andExpect(status().isOk());
    }

    @Test
    @WithMockUser(authorities = "USER")
    void adminEndpoint_withUser_shouldForbid() throws Exception {
        mvc.perform(get("/api/admin/orders"))
            .andExpect(status().isForbidden());
    }

    @Test
    @WithAnonymousUser
    void protectedEndpoint_anonymous_shouldUnauthorize() throws Exception {
        mvc.perform(get("/api/orders"))
            .andExpect(status().isUnauthorized());
    }
}
```

## Guardrails
- Fail closed: deny by default, permit explicitly.
- No secret exposure in logs, errors, or responses.
- Log safely using `LogSanitizer` for all user-supplied input.
- Test both positive (authorized) and negative (unauthorized) access paths.
- Profile-based security: `local` profile permits all for development only.
