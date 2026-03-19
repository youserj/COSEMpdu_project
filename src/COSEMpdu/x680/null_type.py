from dataclasses import dataclass
from typing import Any
from COSEMpdu.x680.type import Constraint, Type
from .type import BuiltinType, NULL, TYPE_VALUE, SEQUENCE_OF


@dataclass
class NullType(BuiltinType):
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
    value: NULL
    def __post_init__(self) -> None:
        if self.value is not None:
            raise ValueError("NullType must have value=None")

    def check_constraint(self, constraint: Constraint[Any]) -> None:
        raise NotImplementedError(f"Validation not implemented for {type(constraint.constraint_spec)}")

    def __str__(self) -> str:
        """ASN.1 value notation: NULL (X.680 §23.3)"""
        return "NULL"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __bool__(self) -> bool:
        """Always False (semantic convention for NULL)"""
        return False
