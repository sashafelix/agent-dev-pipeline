# Backend Conventions — External Integrations

**Scope: backend stacks calling external systems.** Examples below target Java + Spring `RestTemplate` / JAX-RS / JAXB. The *principles* — adapter boundary per dependency, explicit retry/idempotency, distinguish transient vs terminal, structured logging for external calls, secrets via env — generalize to any HTTP / message-broker / streaming integration in any stack (`fetch` + `undici` in Node, `httpx` in Python, `net/http` in Go, `HttpClient` in .NET).

Applies to: `ai-pipeline-integration`, `ai-pipeline-green-code`, `ai-pipeline-observability`.

## Adapter Design
- Encapsulate each external dependency behind a service/adapter boundary.
- Keep mapping between external and internal models explicit.
- Name external API services: `{Service}ApiService` (e.g., `HstApiService`, `TnsGoApiService`).

## RestTemplate Configuration

### Multiple Named Beans
```java
@Bean
@Primary
public RestTemplate restTemplate() {
    return new RestTemplate();
}

@Bean
public RestTemplate tnsRestTemplate() {
    SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
    BufferingClientHttpRequestFactory buffering = new BufferingClientHttpRequestFactory(factory);
    RestTemplate restTemplate = new RestTemplate(buffering);
    restTemplate.getInterceptors().add(new TnsGoInterceptor(objectMapper()));
    return restTemplate;
}
```

### HTTP Interceptor Pattern
```java
public class TnsGoInterceptor implements ClientHttpRequestInterceptor {
    @Override
    public ClientHttpResponse intercept(HttpRequest request, byte[] body, 
            ClientHttpRequestExecution execution) throws IOException {
        // Add headers, logging, etc.
        return execution.execute(request, body);
    }
}
```

### JAX-RS ClientRequestFilter
```java
@Slf4j
public class ApiLoggingFilter implements ClientRequestFilter {
    @Override
    public void filter(ClientRequestContext ctx) throws IOException {
        log.debug("Request URI: {}", ctx.getUri());
        log.debug("Request Method: {}", ctx.getMethod());
        log.debug("Request Headers: {}", ctx.getHeaders());
    }
}
```

## Custom Deserializers
For complex API responses:
```java
public class TnsBranchResponseDeserializer extends JsonDeserializer<TnsBranchResponse> {
    @Override
    public TnsBranchResponse deserialize(JsonParser p, DeserializationContext ctx) {
        // Custom deserialization logic
    }
}

// Registration
ObjectMapper objectMapper = new ObjectMapper();
SimpleModule module = new SimpleModule();
module.addDeserializer(TnsBranchResponse.class, new TnsBranchResponseDeserializer());
objectMapper.registerModule(module);
```

## XML/JAXB Processing

### Secure DocumentBuilder
```java
@Bean
public DocumentBuilder secureDocumentBuilder() throws ParserConfigurationException {
    DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
    dbf.setValidating(false);
    dbf.setNamespaceAware(true);
    dbf.setFeature("http://xml.org/sax/features/namespaces", false);
    dbf.setFeature("http://xml.org/sax/features/validation", false);
    dbf.setFeature("http://apache.org/xml/features/nonvalidating/load-dtd-grammar", false);
    dbf.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
    return dbf.newDocumentBuilder();
}
```

### Secure JAXB Unmarshalling
```java
JAXBContext context = JAXBContext.newInstance(HstAllData.class);
Unmarshaller unmarshaller = context.createUnmarshaller();
try { unmarshaller.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, ""); } catch (Exception ignored) {}
try { unmarshaller.setProperty(XMLConstants.ACCESS_EXTERNAL_SCHEMA, ""); } catch (Exception ignored) {}
```

### XML Model Classes
```java
@Data
@XmlAccessorType(XmlAccessType.FIELD)
@XmlRootElement(name = "dataRecord")
public class DataRecord implements Serializable {
    @XmlAttribute
    private String dpNumber;

    @XmlElement(name = "owner")
    private XmlOwner xmlOwner;

    @XmlElementWrapper(name = "addresses")
    @XmlElement(name = "address")
    private List<XmlAddress> addresses = new ArrayList<>();
}
```

## ZIP Stream Processing
```java
@Transactional
public Boolean importData() throws IOException {
    try (CustomZipInputStream zis = new CustomZipInputStream(apiService.requestData())) {
        ZipEntry entry;
        while ((entry = zis.getNextEntry()) != null) {
            if (entry.getName().endsWith(".xml")) {
                Document xml = documentBuilder.parse(new InputSource(zis));
                processXml(xml);
            }
        }
        return true;
    } catch (Exception e) {
        log.error("RPA-ERROR-IMPORT: {}", e.getLocalizedMessage(), e);
        return false;
    }
}
```

## Reliability
- Handle retries/idempotency explicitly where needed.
- Distinguish transient vs terminal failures.
- Emit actionable errors and metrics.
- Use structured logging for external calls.

```java
log.info("TNS check existing of outlet: {} with response: {}",
    outlet, LogSanitizer.getSanitizedStringForLogging(response.toString()));
```

## Configuration
- Endpoint URLs and credentials via environment/config only.
- No environment-specific constants in business code.

```yaml
tnsgo:
  baseUrl: ${TNS_BASE_URL}
  apiKey: ${TNS_API_KEY}

hst:
  baseUrl: ${HST_BASE_URL}
```

## History/Audit Tracking
Track import/sync operations:
```java
historyService.updateTnsHistory(totalProcessed, totalUpdated, totalAdded);
log.info("Sync complete, total: {}, created: {}, updated: {}",
    total, added, updated);
```

## Testing
- Mock external systems in unit/slice tests.
- Cover failure modes and timeout behavior.
- Use test configuration with mock endpoints.


