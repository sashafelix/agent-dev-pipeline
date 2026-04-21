# Backend Conventions — Security

**Scope: backend stacks.** Examples below target Spring Security (filter chain, `@PreAuthorize`, `SecurityContextHolder`). The *principles* — token-based auth, explicit endpoint authorization, fail-closed defaults, CORS allowlist, log sanitization, secret externalization, secure XML parsing — apply to any backend. Translate to the stack's mechanism (Express middleware, NestJS guards, FastAPI dependencies, Go middleware, ASP.NET authorization policies).

Applies to: `ai-pipeline-security`, `ai-pipeline-api`, `ai-pipeline-integration`, `ai-pipeline-observability`.

## AuthN/AuthZ
- Token-based auth flow (Bearer token).
- Explicit endpoint role checks with `@PreAuthorize`.
- Fail closed by default.

### Role-Based Authorization
```java
@PreAuthorize("hasAuthority('User')")
@GetMapping("/import")
public String importData() { ... }
```

## Security Filter Chain

### Profile-Based Configuration
```java
@Bean
@Profile("!local")
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http.cors(Customizer.withDefaults())
        .csrf(AbstractHttpConfigurer::disable)
        .authorizeHttpRequests(authorize ->
            authorize.requestMatchers(
                    antMatcher("/swagger-ui/**"),
                    antMatcher("/v3/**"),
                    antMatcher("/actuator/**")).permitAll()
                .anyRequest().authenticated())
        .addFilterBefore(customFilter, UsernamePasswordAuthenticationFilter.class);
    return http.build();
}

@Bean
@Profile("local")
public SecurityFilterChain securityFilterChainLocal(HttpSecurity http) throws Exception {
    http.cors(Customizer.withDefaults())
        .csrf(AbstractHttpConfigurer::disable)
        .authorizeHttpRequests(authorize ->
            authorize.requestMatchers(antMatcher("/**")).permitAll());
    return http.build();
}
```

### Permitted Endpoints
- `/swagger-ui/**` - API documentation
- `/v3/**` - OpenAPI spec
- `/actuator/**` - Health/metrics endpoints

### Role Prefix Removal
```java
@Bean
GrantedAuthorityDefaults grantedAuthorityDefaults() {
    return new GrantedAuthorityDefaults("");  // Remove 'ROLE_' prefix
}
```

## Custom Authentication Filter
```java
public class CustomFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest request, 
            HttpServletResponse response, FilterChain filterChain) {
        // Skip non-API paths
        if (!request.getRequestURI().startsWith("/api")) {
            filterChain.doFilter(request, response);
            return;
        }
        
        try {
            String tokenHeader = request.getHeader(HttpHeaders.AUTHORIZATION);
            if (tokenHeader != null && tokenHeader.startsWith("Bearer ")) {
                String token = tokenHeader.substring(7);
                Authentication auth = authManager.authenticate(;...);
                SecurityContextHolder.getContext().setAuthentication(auth);
            }
        } catch (Exception e) {
            SecurityContextHolder.clearContext();
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED, e.getMessage());
            return;
        }
        filterChain.doFilter(request, response);
    }
}
```

## UserContextHolder Pattern
Static utility for accessing current user context:
```java
public class UserContextHolder {
    public static UserDetails getUserInfo() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth.getPrincipal() instanceof UserDetails) {
            return (UserDetails) auth.getPrincipal();
        }
        return null;
    }

    public static String getUsername() {
        return getUserInfo() != null ? getUserInfo().getUsername() : "System";
    }

    public static boolean hasUserRole(String role) {
        UserDetails user = getUserInfo();
        return user != null && user.getAuthorities().stream()
            .anyMatch(a -> a.getAuthority().equals(role));
    }
}
```

## JPA Audit Integration
Use `@PrePersist` and `@PreUpdate` lifecycle callbacks:
```java
@PrePersist
public void prePersist() {
    setUserCreated(UserContextHolder.getUsername());
    setUserChanged(UserContextHolder.getUsername());
}

@PreUpdate
public void preUpdate() {
    setUserChanged(UserContextHolder.getUsername());
}
```

## CORS Configuration
```java
@Bean
public UrlBasedCorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(properties.getCors());
    config.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    config.setAllowedHeaders(Arrays.asList("Authorization", "Cache-Control", "Content-Type"));
    config.setAllowCredentials(true);

    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);
    return source;
}
```

## Secure Coding
- Sanitize user-controlled strings in logs using `LogSanitizer`.
- Never hardcode secrets.
- Keep secret/config resolution externalized via environment variables.
- Configure secure XML parsing (disable external DTD loading).

```java
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
```

## Error Handling
- Unauthorized/forbidden behavior must be deterministic and test-covered.
- Do not expose sensitive internals in auth errors.
- Use dedicated exceptions: `RpaAuthenticationException`, `AccessDeniedException`.

## Security Tests
- Include role-based access tests for changed endpoints.
- Include negative-path auth tests where relevant.
- Test both `@WithMockUser` and `@WithAnonymousUser` scenarios.


