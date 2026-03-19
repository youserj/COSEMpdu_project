# src/COSEMpdu/x680/sequence_type.py
from dataclasses import dataclass
from typing import ClassVar, Optional, Self, Any
from .type import BuiltinType, NamedType, Type, SEQUENCE, DefaultNamedType, OptionalNamedType, SEQUENCE_OF, Constraint, TYPE_VALUE


@dataclass
class SequenceType(BuiltinType):
    """
    Base class for SEQUENCE types (X.680 §24)
    NATIVE REPRESENTATION: dataclass instance with fields corresponding to components

    ASN.1 semantics:
    - Ordered collection of named components (X.680 §3.6.60)
    - Components may be OPTIONAL or DEFAULT (X.680 §24.3)
    - Tag: UNIVERSAL 16 (X.680 §24.16)
    - XML notation: <SEQUENCE>...</SEQUENCE> (X.680 Table 4)

    A-XDR encoding note (IEC 61334-6 §6.9):
    - Components encoded in definition order
    - OPTIONAL/DEFAULT components omitted when absent/default
    - Explicit tags NOT encoded (redundant information)

    Usage pattern (concrete SEQUENCE definition):
        @dataclass(frozen=True)
        class Credentials(SequenceType):
            userName: VisibleStringType
            password: VisibleStringType
            accountNumber: Optional[IntegerType] = None  # OPTIONAL component
            status: BooleanType = field(default_factory=lambda: BooleanType(True))  # DEFAULT

    Component access:
        cred = Credentials(userName=..., password=...)
        cred.userName  # Direct attribute access
        cred.accountNumber  # None if absent (OPTIONAL)
    """
    components: ClassVar[tuple[NamedType[Type], ...]]
    value: SEQUENCE

    def check_constraint(self, constraint: Constraint[Any]) -> None:
        raise NotImplementedError(f"Validation not implemented for {type(constraint.constraint_spec)}")

    def __str__(self) -> str:
        """
        ASN.1 value notation per X.680 §24.17:
        { identifier1 value1, identifier2 value2, ... }
        Omits components with value None (absent OPTIONAL components).
        DEFAULT values are ALWAYS included (cannot distinguish explicit vs default assignment in native representation).
        """
        components: list[str] = []
        # Preserve field definition order (critical for SEQUENCE semantics)
        for field_name in self.__dataclass_fields__:
            if field_name == "tag":  # Skip ClassVar metadata
                continue
            value = getattr(self, field_name)
            if value is not None:  # Skip absent OPTIONAL components
                components.append(f"{field_name} {value}")
        return "{" + ", ".join(components) + "}"

    def __getitem__(self, key: int | str) -> Optional[Type]:
        if isinstance(key, int):
            return self.value[key]
        for i, component in enumerate(self.components):
            if component.identifier == key:
                return self.value[i]
        else:
            raise KeyError(f"not find component with name: {key}")

    @classmethod
    def _from_components(cls, **kwargs: Optional[Type]) -> Self:
        """
        Create SequenceType instance from named component values.

        Maps keyword arguments to component positions based on 
        cls.components definition (X.680 §24.2).

        Args:
            **kwargs: Field name → Type value mappings.
                    OPTIONAL fields can be None (absent).
                    DEFAULT fields omitted → default value used.

        Returns:
            Self: New SequenceType instance with ordered value tuple.

        Raises:
            ValueError: Unknown field name or missing REQUIRED component.
            TypeError: Value type doesn't match component type.

        Example:
            >>> cred = Credentials.from_components(
            ...     userName=VisibleString("admin"),
            ...     password=VisibleString("secret"),
            ...     accountNumber=Integer(123)  # OPTIONAL
            ... )
            >>> cred.value  # Tuple in definition order
            (VisibleString("admin"), VisibleString("secret"), Integer(123))
        """
        values: list[Optional[Type]] = []
        used_fields: set[str] = set()
        for component in cls.components:
            field_name = component.identifier
            field_value = kwargs.get(field_name)
            # Track which fields were provided
            if field_name in kwargs:
                used_fields.add(field_name)
            # Handle component based on type
            if isinstance(component, DefaultNamedType):
                # DEFAULT: use provided value or default
                if field_value is None:
                    if field_name in kwargs:
                        # Explicitly set to None → use default
                        values.append(component.default)
                    else:
                        # Not provided → use default
                        values.append(component.default)
                else:
                    values.append(field_value)
            elif isinstance(component, OptionalNamedType):
                # OPTIONAL: None means absent
                values.append(field_value)  # Can be None
            else:
                # REQUIRED: must be provided
                if field_value is None:
                    if field_name not in kwargs:
                        raise ValueError(f"Missing required component '{field_name}' in {cls.__name__}")
                if isinstance(field_value, component.type_):
                    values.append(field_value)
                else:
                    raise TypeError(f"got Required component '{field_name}' type: {field_value.__class__.__name__}, expected {component.type_}")
        # Check for unknown fields
        expected_fields = {c.identifier for c in cls.components}
        unknown_fields = used_fields - expected_fields
        if unknown_fields:
            raise ValueError(f"Unknown component(s): {unknown_fields} in {cls.__name__}. Expected: {expected_fields}")
        return cls(value=tuple(values))