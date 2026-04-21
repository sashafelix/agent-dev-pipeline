# Backend Conventions — Entity, Repository, Mapper

**Scope: backend stacks with an ORM and DTO layer.** Examples below target Java + JPA + Lombok + MapStruct. The *principles* — audit fields on mutable entities, business-key equality, explicit fetch/cascade, DTO↔entity separation via a mapper — generalize to Node + TypeORM/Prisma, Python + SQLAlchemy/Django, Go + GORM, .NET + EF Core. Adapt idioms to the stack.

Applies to: `ai-pipeline-entity`, `ai-pipeline-green-code`, `ai-pipeline-api`.

## Base Entity Pattern

All mutable entities extend `AbstractBaseEntity`:
```java
@Data
@MappedSuperclass
public abstract class AbstractBaseEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @CreationTimestamp
    @Column(name = "date_created", nullable = false, updatable = false)
    private LocalDateTime dateCreated;
    
    @Column(name = "user_created", updatable = false)
    private String userCreated;
    
    @UpdateTimestamp
    @Column(name = "date_changed")
    private LocalDateTime dateChanged;
    
    @Column(name = "user_changed")
    private String userChanged;

    @PrePersist
    public void prePersist() {
        setUserCreated(UserContextHolder.getUsername());
        setUserChanged(UserContextHolder.getUsername());
    }

    @PreUpdate
    public void preUpdate() {
        setUserChanged(UserContextHolder.getUsername());
    }
}
```

## Entity Annotations Pattern
```java
@Entity
@Data
@Table(name = "outlet")
@EqualsAndHashCode(onlyExplicitlyIncluded = true, callSuper = false)
public class Outlet extends AbstractBaseEntity implements Serializable {
    @Serial
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "outlet_generator")
    @SequenceGenerator(name = "outlet_generator", sequenceName = "outlet_seq", allocationSize = 1)
    private Long id;

    @Column(nullable = false)
    @EqualsAndHashCode.Include
    private String outletNumber;  // Business key

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "legal_entity_fk", referencedColumnName = "id")
    @ToString.Exclude
    private LegalEntity legalEntity;

    @OneToMany(fetch = FetchType.LAZY, mappedBy = "outlet", cascade = CascadeType.ALL, orphanRemoval = true)
    @ToString.Exclude
    private List<Address> addresses = new ArrayList<>();
}
```

## Entity Rules
- Extend `AbstractBaseEntity` for audit support.
- Implement `Serializable` with `serialVersionUID`.
- Use `@EqualsAndHashCode(onlyExplicitlyIncluded = true, callSuper = false)`.
- Use `@EqualsAndHashCode.Include` on business key fields (not ID).
- Use `@ToString.Exclude` on relationships to prevent infinite loops.
- Use `allocationSize = 1` for sequence generators (PostgreSQL compatibility).
- Explicit `@Column` constraints: `nullable = false` for required fields.
- Lazy fetch for collections, explicit cascade rules.
- Use `orphanRemoval = true` for owned collections.
- Avoid business-heavy logic in entities (simple derived properties OK).

## Derived Properties in Entities
Entities may contain simple computed/derived properties:
```java
public String getFullName() {
    StringBuilder sb = new StringBuilder(this.getName());
    if (StringUtils.isNotBlank(this.getAdditionalName())) {
        sb.append(" ").append(this.getAdditionalName());
    }
    return sb.toString();
}
```

## View Entity Pattern (Read-Only)
For database views, use immutable entities:
```java
@Entity
@Getter
@Setter
@Immutable
@Table(name = "outlet_overview")
public class OutletOverview {
    @Id
    String buno;
    
    // Manual equals/hashCode on business key
    @Override
    public boolean equals(Object o) { ... }
    @Override
    public int hashCode() { ... }
}
```
- Use `@Immutable` annotation.
- Use `@Getter/@Setter` instead of `@Data`.
- Do **not** extend `AbstractBaseEntity`.
- Manual `equals()`/`hashCode()` on business key.

## Repositories
- Use Spring Data repositories with explicit query intent.
- Annotate with `@Repository`.
- Keep repository methods focused and readable.
- Use query derivation method names.
- Return entities directly (mapping in service/mapper layer).

```java
@Repository
public interface OutletRepository extends JpaRepository<Outlet, Long> {
    Outlet findByOutletNumberAndLegalEntityDpNumber(String outletNumber, String dpNumber);
    Optional<OutletOverview> findByIdAndBunoAndOutletStatusTrueAndOutletHiddenFalse(Long id, String buno);
}
```

## Base DTO Pattern
```java
@Data
public abstract class AbstractAuditingDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    @ReadOnlyProperty
    private LocalDateTime dateCreated;

    @ReadOnlyProperty
    private LocalDateTime dateChanged;
}
```

## DTO Conventions
```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(of = "id", callSuper = false)
public class OutletDto extends AbstractAuditingDTO implements Serializable {
    private Long id;
    private String name;
    
    @Singular
    private List<AddressDto> addresses;  // Use @Singular with @Builder
}
```
- Lombok `@Data`, `@Builder`, `@NoArgsConstructor`, `@AllArgsConstructor`.
- Implement `Serializable`.
- Extend `AbstractAuditingDTO` for audit fields.
- Explicit `@EqualsAndHashCode` based on ID.
- Use `@Singular` for collection fields with `@Builder`.
- Separate request/response DTOs in subpackages.

## EntityMapper Base Interface
```java
public interface EntityMapper<D, E> {
    D toDto(E e);
    E toEntity(D d);
    List<D> toDto(List<E> eList);
    List<E> toEntity(List<D> dList);
}
```

## MapStruct Mapper Conventions
```java
@Mapper(componentModel = "spring")
public interface OutletMapper extends EntityMapper<OutletDto, Outlet> {

    @Mapping(target = "agDealer", expression = "java(outlet.getLegalEntity() != null ? outlet.getLegalEntity().getDpNumber() : null)")
    @Mapping(target = "name", expression = "java(outlet.getFullName())")
    @Mapping(target = "outletType", source = "outletTypeArchitectural")
    OutletDto toDto(Outlet outlet);
}
```

### Composed Mappers
```java
@Mapper(componentModel = "spring", uses = {
    AddressMapper.class,
    CommunicationMapper.class
})
public interface OutletDetailMapper { ... }
```

### Mapper Decorators
```java
@Mapper(componentModel = "spring", uses = {...})
@DecoratedWith(OutletDecorator.class)
public interface XmlOutletMapper {
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "legalEntity", ignore = true)
    Outlet xmlToEntity(DataRecord record);
}
```

## Maven Configuration (MapStruct + Lombok)
```xml
<annotationProcessorPaths>
    <path><groupId>org.mapstruct</groupId><artifactId>mapstruct-processor</artifactId></path>
    <path><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId></path>
    <dependency><groupId>org.projectlombok</groupId><artifactId>lombok-mapstruct-binding</artifactId></dependency>
</annotationProcessorPaths>
<compilerArgs>
    <compilerArg>-Amapstruct.defaultComponentModel=spring</compilerArg>
</compilerArgs>
```

## Guardrails
- No entity leakage in controller responses.
- Ensure mapping updates whenever fields change.
- Use `@Mapping(target = ..., ignore = true)` for unmapped fields.


