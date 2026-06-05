from typing import Self, Any
from StructResult.result import Error
from .type import BuiltinType, NULL, Simple


class NullType(Simple[NULL], BuiltinType):
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

    def __init__(self, value: NULL = None) -> None:
        self.value = value

    @classmethod
    def validate(cls, value: Any) -> None | Error:
        return None

    @classmethod
    def default(cls) -> Self:
        return cls(None)  # NULL has no value, but we use None to represent it in Python

    def __str__(self) -> str:
        """ASN.1 value notation: NULL (X.680 §23.3)"""
        return "NULL"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __bool__(self) -> bool:
        """Always False (semantic convention for NULL)"""
        return False

    def __eq__(self, value: object) -> bool:
        if isinstance(value, self.__class__):
            return True
        return super().__eq__(value)
