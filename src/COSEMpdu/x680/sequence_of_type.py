# src/COSEMpdu/x680/sequence_of_type.py
"""
ASN.1 SEQUENCE OF Type Definition (X.680 §25)
This module defines the abstract syntax for SEQUENCE OF types.

Standards:
    - X.680 §25: SEQUENCE OF type definition
    - IEC 61334-6 §6.10: DLMS/COSEM SEQUENCE OF A-XDR encoding

Note:
    - SEQUENCE OF is a BUILTIN type per X.680 §16.2
"""
from dataclasses import dataclass
from typing import ClassVar, Iterator, Any
from .type import BuiltinType, SEQUENCE_OF, Type, Constraint


@dataclass
class SequenceOfType[T: Type](BuiltinType):
    """ASN.1 SEQUENCE OF type."""
    component_type: ClassVar[type[Type]]
    value: SEQUENCE_OF[T]

    def __class_getitem__(cls, item: type[T]) -> type["SequenceOfType[T]"]:
        """Поддерживает SequenceOfType[int] на уровне класса."""
        name = f"{cls.__name__}[{item.__name__}]"
        return type(name, (cls,), {
            "component_type": item,
        })

    def check_constraint(self, constraint: Constraint[Any]) -> None:
        raise NotImplementedError(f"Validation not implemented for {type(constraint.constraint_spec)}")

    def __getitem__(self, index: int) -> T:
        """
        Get component by index.

        Args:
            index: Zero-based index into the sequence

        Returns:
            Component at specified index

        Raises:
            IndexError: If index is out of range
        """
        return self.value[index]

    def __iter__(self) -> Iterator[T]:
        """Iterate over components in order."""
        return iter(self.value)

    def __repr__(self) -> str:
        """
        Return developer-friendly string representation.

        Returns:
            String showing component count
        """
        return f"{self.__class__.__name__}(count={len(self.value)})"

    def __len__(self) -> int:
        """Return number of components"""
        return len(self.value)

    @property
    def is_empty(self) -> bool:
        """Check if sequence contains no components"""
        return len(self.value) == 0

    @property
    def first(self) -> T | None:
        """Get first component if present"""
        return self.value[0] if self.value else None

    @property
    def last(self) -> T | None:
        """Get last component if present"""
        return self.value[-1] if self.value else None
