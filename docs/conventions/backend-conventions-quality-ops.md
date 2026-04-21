# Backend Conventions — Quality, Observability, DevOps, Compliance

**Scope: backend stacks.** Examples below target Java + Maven + Spring Boot (JaCoCo, Sleuth, Logback, Spring Actuator). The *principles* — coverage target with exclusions for trivial classes, structured logging with traceable prefixes, profile-based config, externalized secrets, traceability from requirement → code → test → release — apply to any stack. Translate the mechanisms:
- Coverage: JaCoCo → c8 / Istanbul (Node), coverage.py (Python), `go test -cover`, Coverlet (.NET)
- Tracing: Sleuth → OpenTelemetry SDK (any stack)
- Logging: Logback → pino/winston (Node), structlog (Python), zap/zerolog (Go), Serilog (.NET)
- Profiles: Spring profiles → `NODE_ENV`/dotenv, `APP_ENV`, Go build tags, ASP.NET environments

Applies to: `ai-pipeline-contract-guard`, `ai-pipeline-observability`, `ai-pipeline-devops`, `ai-pipeline-compliance`, `ai-pipeline-architecture-decisions`.

## Contract Guard
- Validate API and schema compatibility.
- Explicitly label breaking vs non-breaking changes.

## Code Coverage (JaCoCo)

### Maven Configuration
```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.12</version>
    <executions>
        <execution>
            <goals><goal>report</goal></goals>
        </execution>
        <execution>
            <id>jacoco-check</id>
            <phase>test</phase>
            <goals><goal>check</goal></goals>
            <configuration>
                <excludes>
                    <exclude>com/example/*/model/**/*.class</exclude>
                </excludes>
                <rules>
                    <rule>
                        <element>BUNDLE</element>
                        <limits>
                            <limit>
                                <counter>LINE</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.80</minimum>
                            </limit>
                        </limits>
                    </rule>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

### Coverage Exclusions
Exclude model/DTO packages from coverage requirements:
- `com/*/model/**/*.class`
- Generated mapper implementations

## Maven Profiles
```xml
<profiles>
    <profile>
        <id>local</id>
        <activation><activeByDefault>true</activeByDefault></activation>
        <properties><active-profiles>local</active-profiles></properties>
    </profile>
    <profile>
        <id>test</id>
        <properties><active-profiles>test</active-profiles></properties>
    </profile>
    <profile>
        <id>int</id>
        <properties><active-profiles>int</active-profiles></properties>
    </profile>
    <profile>
        <id>prod</id>
        <properties><active-profiles>prod</active-profiles></properties>
    </profile>
</profiles>
```

## Observability

### Structured Logging (Logstash)
```xml
<dependency>
    <groupId>net.logstash.logback</groupId>
    <artifactId>logstash-logback-encoder</artifactId>
    <version>7.0.1</version>
</dependency>
```

### Distributed Tracing (Spring Cloud Sleuth)
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-sleuth</artifactId>
</dependency>
```

### Log Prefixes for Traceability
- `RPA-API-REQUEST-*`: API request logging
- `RPA-ERROR-*`: Error conditions
- `RPA-TNS-GO-*`: External integration

### Actuator Configuration
```yaml
management:
  endpoints:
    web:
      exposure:
        include: '*'
  endpoint:
    health:
      probes:
        enabled: true
      show-details: always
```

### Observability Rules
- Add meaningful structured logs for key business flow transitions.
- Add metrics/traces for critical paths and failure points.
- Avoid sensitive data in logs (use `LogSanitizer`).

## Caching
```java
@SpringBootApplication
@EnableCaching
public class Application { ... }

@Bean
public Caffeine caffeineConfig() {
    return Caffeine.newBuilder()
        .expireAfterWrite(60, TimeUnit.MINUTES);
}
```

## Scheduling
```java
@SpringBootApplication
@EnableScheduling
public class Application { ... }
```

## DevOps

### Docker Configuration
```dockerfile
FROM openjdk:21
ARG JAR_FILE=target/app*.jar
WORKDIR /opt/app
COPY ${JAR_FILE} app.jar
RUN mkdir /opt/app/tmp
ENTRYPOINT ["java", "-Djava.io.tmpdir=/opt/app/tmp", "-jar", "app.jar"]
VOLUME /opt/app/tmp
```

### CI/CD Rules
- CI/CD must enforce tests and quality gates.
- Keep environment configs separated.
- Keep secrets external to repo.

## Application Configuration

### Profile-Based Config Files
| Profile | File | Purpose |
|---------|------|---------|
| default | `application.yml` | Base configuration |
| local | `application-local.yml` | Local development |
| int | `application-int.yml` | Integration environment |
| test | `application-test.yml` | Test environment |
| prod | `application-prod.yml` | Production |

### Configuration Properties Class
```java
@Configuration
@ConfigurationProperties(prefix = "app-name")
public class AppProperties {
    private List<String> cors;
    // getters/setters
}
```

## Compliance
- Maintain traceability from requirement -> code -> test -> release artifact.
- Keep release evidence concise and linked.

## Decision Management
- Story-level decisions are append-only in `decision-log.md`.
- Global index updated with links/summaries only.


