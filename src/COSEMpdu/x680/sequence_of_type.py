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
from typing import Iterator, Self
from StructResult.result import Error, ValueOrError
from .type import BuiltinType, SEQUENCE_OF, Type, TYPE_VALUE


class SequenceOfType[T: Type](BuiltinType):
    """ASN.1 SEQUENCE OF type."""
    _T: type[T]
    value: SEQUENCE_OF[T]

    def __init__(self, value: SEQUENCE_OF[T] = []) -> None:
        self.value = value

    @classmethod
    def parse[U: TYPE_VALUE](cls, value: tuple[U]) -> Self:
        return cls([cls._T.parse(val) for val in value])

    def normalize(self) -> tuple[TYPE_VALUE]:
        return [val.normalize() for val in self.value]

    def __class_getitem__(cls, item: type[T]) -> type["SequenceOfType[T]"]:
        """Поддерживает SequenceOfType[int] на уровне класса."""
        name = f"{cls.__name__}Of{item.__name__}"
        return type(name, (cls,), {
            "_T": item,
        })

    @classmethod
    def default(cls) -> "SequenceOfType[T]":
        """Return default instance with empty sequence."""
        return cls([])

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
        return f"{self.__class__.__name__}[{len(self.value)}]"

    def __len__(self) -> int:
        """Return number of components"""
        return len(self.value)

    @property
    def is_empty(self) -> bool:
        """Check if sequence contains no components"""
        return len(self.value) == 0

    @property
    def first(self) -> ValueOrError[T]:
        """Get first component if present"""
        if self.value:
            return self.value[0]
        return Error.from_e(IndexError("Sequence is empty"))

    @property
    def last(self) -> ValueOrError[T]:
        """Get last component if present"""
        if self.value:
            return self.value[-1]
        return Error.from_e(IndexError("Sequence is empty"))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SequenceOfType):
            return False
        return (
            self._T == other._T
            and self.normalize() == other.normalize()
        )
