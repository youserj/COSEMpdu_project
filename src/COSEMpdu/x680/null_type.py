from dataclasses import dataclass
from typing import Optional, Protocol
from .type import BuiltinType


@dataclass(frozen=True)
class NullType(BuiltinType, Protocol):
    """
    NULL type (X.680 §23, X.690 §8.8)
    NATIVE REPRESENTATION: singleton (no value)
    
    ASN.1 example:
        AbsentData ::= NULL
    
    Standards compliance:
    - Tag: UNIVERSAL 5 (X.680 §23.2)
    - Single valid value: NULL (X.680 §23.3)
    - Contents octets: empty (X.690 §8.8.2)
    - XML notation: <NULL/> (X.680 Table 4)
    """
    value: Optional[None] = None  # Explicit None for structural consistency

    def __post_init__(self) -> None:
        if self.value is not None:
            raise ValueError("NullType must have value=None")

    def __str__(self) -> str:
        """ASN.1 value notation: NULL (X.680 §23.3)"""
        return "NULL"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __bool__(self) -> bool:
        """Always False (semantic convention for NULL)"""
        return False


