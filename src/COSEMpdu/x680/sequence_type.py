# src/COSEMpdu/x680/sequence_type.py
from dataclasses import dataclass
from typing import ClassVar, Protocol
from .tag import Tag, UniversalClassTagAssignments
from .type import BuiltinType, UType


@dataclass(frozen=True)
class SequenceType(BuiltinType, Protocol):
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
    components: ClassVar[dict[str, type[UType]]]

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