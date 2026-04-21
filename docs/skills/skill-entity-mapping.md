# Skill: skill-entity-mapping

## Purpose
Implement domain entities, repositories, DTO boundaries, and mappers.

## Reads
- `docs/conventions/backend-conventions-general.md`
- `docs/conventions/backend-conventions-java-style.md`
- `docs/conventions/backend-conventions-entity-mapping.md`
- migration and contract context

## Writes
- entity/repository/mapper/DTO files in backend module scope
- decision notes in `docs/agent/runs/{story_id}/decision-log.md`

## Entity Conventions

### Base Entity Pattern
All entities extend `AbstractBaseEntity`:
```java
@Data
@MappedSuperclass
public abstract class AbstractBaseEntity implements Serializable {
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

### Entity Annotations
```java
@Entity
@Data
@Table(name = "my_table", schema = "ai_pipeline")
@EqualsAndHashCode(onlyExplicitlyIncluded = true, callSuper = false)
public class MyEntity extends AbstractBaseEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "my_seq")
    @SequenceGenerator(name = "my_seq", sequenceName = "my_seq", allocationSize = 1)
    private Long id;

    @EqualsAndHashCode.Include
    @Column(nullable = false)
    private String businessKey;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_fk")
    @ToString.Exclude
    private ParentEntity parent;

    @OneToMany(mappedBy = "parent", cascade = CascadeType.ALL, orphanRemoval = true)
    @ToString.Exclude
    private List<ChildEntity> children = new ArrayList<>();
}
```

### View Entity Pattern (Read-Only Projections)
For database views:
```java
@Entity
@Immutable
@Table(name = "my_view", schema = "ai_pipeline")
@Data
public class MyView {
    @Id
    private Long id;
    // read-only fields
}
```
Repository:
```java
@Repository
public interface MyViewRepository extends JpaRepository<MyView, Long> {
    List<MyView> findAllByStatusTrue();
}
```

## Mapper Conventions

### Base Interface
```java
public interface EntityMapper<D, E> {
    D toDto(E entity);
    E toEntity(D dto);
    List<D> toDto(List<E> entities);
    List<E> toEntity(List<D> dtos);
}
```

### Standard Mapper
```java
@Mapper(componentModel = "spring")
public interface MyMapper extends EntityMapper<MyDto, MyEntity> {
    @Mapping(target = "fieldA", source = "entityFieldA")
    @Mapping(target = "computed", expression = "java(entity.getComputed())")
    MyDto toDto(MyEntity entity);
}
```

### Decorator Pattern (Complex Mapping)
When mapping requires service calls or complex logic:
```java
@Mapper(componentModel = "spring")
@DecoratedWith(MyMapperDecorator.class)
public interface MyMapper {
    @Mapping(target = "relatedEntity", ignore = true)
    MyEntity toEntity(MyDto dto);
}

public abstract class MyMapperDecorator implements MyMapper {
    @Autowired
    @Qualifier("delegate")
    private MyMapper delegate;

    @Autowired
    private RelatedRepository relatedRepository;

    @Override
    public MyEntity toEntity(MyDto dto) {
        MyEntity entity = delegate.toEntity(dto);
        entity.setRelatedEntity(relatedRepository.findById(dto.getRelatedId()).orElse(null));
        return entity;
    }
}
```

## Enum Conventions
```java
public enum Status {
    ACTIVE("A"),
    INACTIVE("I");

    private final String code;

    Status(String code) { this.code = code; }

    public String getCode() { return code; }

    public static Status fromCode(String code) {
        return Arrays.stream(values())
            .filter(s -> s.code.equals(code))
            .findFirst()
            .orElse(null);
    }
}
```

For XML/JAXB (when needed):
```java
@XmlType
@XmlEnum(String.class)
public enum PortfolioCode {
    @XmlEnumValue("B1") P_B1("B1");
    // ...
}
```

## Guardrails
- Do not leak JPA entities into API contracts.
- Keep mapping explicit and testable.
- Use `@ToString.Exclude` on all relationship fields.
- Use `@EqualsAndHashCode.Include` on business keys, not IDs.
- Prefer LAZY fetch for collections; EAGER only with justification.



