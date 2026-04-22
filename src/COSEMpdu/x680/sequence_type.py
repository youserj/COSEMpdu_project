# src/COSEMpdu/x680/sequence_type.py
from typing import ClassVar, Optional, Self
from .type import BuiltinType, NamedType, Type, SEQUENCE, TYPE_VALUE


class SequenceType[T: SEQUENCE](BuiltinType):
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
    value: T

    def __init__(self, value: T) -> None:
        self.value = value

    @classmethod
    def parse[U: TYPE_VALUE](cls, value: tuple[U]) -> Self:
        return cls(tuple(None if val is None else comp.type_.parse(val) for comp, val in zip(cls.components, value, strict=True)))

    def normalize(self) -> tuple[TYPE_VALUE, ...]:
        return tuple(None if val is None else val.normalize() for val in self.value)

    @classmethod
    def default(cls) -> Self:
        return cls(tuple(component.type_.default() for component in cls.components))

    def __str__(self) -> str:
        """
        ASN.1 value notation per X.680 §24.17:
        { identifier1 value1, identifier2 value2, ... }
        Omits components with value None (absent OPTIONAL components).
        DEFAULT values are ALWAYS included (cannot distinguish explicit vs default assignment in native representation).
        """
        return f"{self.__class__.__name__}[{len(self.value)}]"

    def __getitem__(self, key: int | str) -> Optional[Type]:
        if isinstance(key, int):
            return self.value[key]
        for i, component in enumerate(self.components):
            if component.identifier == key:
                return self.value[i]
        else:
            raise KeyError(f"not find component with name: {key}")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SequenceType):
            return False
        return self.normalize() == other.normalize()
