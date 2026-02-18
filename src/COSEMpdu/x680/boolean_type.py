from dataclasses import dataclass
from typing import Protocol
from .type import BuiltinType


@dataclass
class BooleanType(BuiltinType, Protocol):
    """
    BOOLEAN type (X.680 §17)
    NATIVE REPRESENTATION: bool
    """
    value: bool

    def __bool__(self) -> bool:
        """Прямое преобразование в Python bool"""
        return self.value

    def __str__(self) -> str:
        """ASN.1 textual representation: TRUE / FALSE"""
        return "TRUE" if self.value else "FALSE"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"