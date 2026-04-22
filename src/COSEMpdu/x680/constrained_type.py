from dataclasses import dataclass
from typing import ClassVar, Optional, Protocol, Any, Self, get_type_hints, override
from StructResult.result import ValueOrError
from .type import Type, TYPE_VALUE, OCTET_STRING
from .integer_type import IntegerType
from .bit_string import BitStringType
from .octet_string_type import OctetStringType
from .sequence_of_type import SequenceOfType
from .enumerated_type import EnumeratedType


class ConstraintSpec(Protocol):
    ...


class ExceptionSpec:
    """not realized"""


class Elements(ConstraintSpec, Protocol):
    """46.5"""


class SubtypeElements(Elements, Protocol):
    """47.1 General SubtypeElements"""
    def contains(self, value: Any) -> bool: ...


@dataclass
class SingleValue[T: (int, str)](SubtypeElements):
    """47.2"""
    value: T

    def contains(self, value: T) -> bool:
        return value == self.value

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class ValueRange(SubtypeElements):
    """47.4 Value range

    Represents a range of values in ASN.1, e.g. (0..100) or ("A".."Z")

    Type Parameters:
        T: Type of endpoints - must be int or str
    """
    lower_endpoint: int
    upper_endpoint: int
    lower_inclusive: bool = True
    upper_inclusive: bool = True

    def contains(self, value: int) -> bool:
        """
        Check if a value is within the constrained range.

        Args:
            value: Value to check (must be same type as endpoints)

        Returns:
            True if value is in range, False otherwise

        Examples:
            >>> ValueRange(0, 100).contains(50)
            True
            >>> ValueRange(0, 100).contains(150)
            False
            >>> ValueRange("A", "Z").contains("M")
            True
            >>> ValueRange("A", "Z").contains("a")
            False
        """
        if isinstance(value, str):
            if len(value) != 1:
                raise ValueError("Value must be a single character")
        lower_ok = value >= self.lower_endpoint if self.lower_inclusive else value > self.lower_endpoint
        upper_ok = value <= self.upper_endpoint if self.upper_inclusive else value < self.upper_endpoint
        return lower_ok and upper_ok

    def __str__(self) -> str:
        """ASN.1 notation for value range."""
        lower = str(self.lower_endpoint)
        upper = str(self.upper_endpoint)
        if isinstance(self.lower_endpoint, str):
            lower = f"{lower}"
            upper = f"{upper}"
        l_mark = "" if self.lower_inclusive else "<"
        u_mark = "" if self.upper_inclusive else "<"
        if l_mark or u_mark:
            return f"({lower}{l_mark}..{u_mark}{upper})"
        return f"({lower}..{upper})"


@dataclass
class SizeConstraint(SubtypeElements):
    max_size: int
    min_size: Optional[int] = None

    def contains(self, value: int) -> bool:
        if self.min_size is None:
            if value != self.max_size:
                raise ValueError(f"Size must be {self.max_size}, got {value}")
        elif value < self.min_size:
            raise ValueError(f"Size must be at least {self.min_size}, got {value}")
        elif value > self.max_size:
            raise ValueError(f"Size must be < {self.max_size}, got {value}")
        return True

    def __str__(self) -> str:
        if self.min_size is None:
            inner = str(self.max_size)
        else:
            inner = f"{self.min_size}..{self.max_size}"
        if inner.startswith("(") and inner.endswith(")"):
            return f"SIZE{inner}"
        return f"SIZE({inner})"


class ConstrainedType[T: Type](Type, Protocol):
    constraint_spec: ClassVar[ConstraintSpec]
    exception_spec: ClassVar[Optional[ExceptionSpec]] = None
    value: T

    def __init__(self, value: T) -> None:
        self.value = value
        if isinstance(self.value, (IntegerType, EnumeratedType)):
            if isinstance(v_r := self.constraint_spec, ValueRange):
                if not v_r.contains(self.value.value):
                    raise ValueError(f"Value {self.value!r} outside range [{v_r.lower_endpoint}..{v_r.upper_endpoint}]")
                return
        elif isinstance(self.value, BitStringType):
            if (
                isinstance(self.constraint_spec, SizeConstraint)
                and not self.constraint_spec.contains(len(self.value.value))
            ):
                raise ValueError(f"got {len(self.value.value)}, expected {self.constraint_spec}")
            return
        elif isinstance(self.value, OctetStringType):
            if (
                isinstance(self.constraint_spec, SizeConstraint)
                and not self.constraint_spec.contains(len(self.value.value))
            ):
                raise ValueError(f"got {len(self.value.value)}, expected {self.constraint_spec}")
            return
        elif isinstance(self.value, SequenceOfType):
            if (
                isinstance(self.constraint_spec, SizeConstraint)
                and not self.constraint_spec.contains(len(self.value.value))
            ):
                raise ValueError(f"got {len(self.value.value)}, expected {self.constraint_spec}")
            return
        raise NotImplementedError(f"Validation {self.get_type().__name__} not implemented for {self.constraint_spec.__class__.__name__}")

    @classmethod
    def parse(cls, value: Any) -> Self:
        return cls(cls.get_type().parse(value))

    # def normalize(self) -> TYPE_VALUE:
    #     return self.value.normalize()

    @classmethod
    def default(cls) -> Self:
        return cls(cls.get_type().default())

    @classmethod
    def get_type(cls) -> type[T]:
        return get_type_hints(cls)["value"]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value


class ConstrainedOctetStringType[T: OctetStringType](ConstrainedType[T], Type):
    fixed_length: ClassVar[Optional[int]] = None
    value: T

    @override
    def normalize(self) -> OCTET_STRING:
        return self.value.normalize()

    @classmethod
    def default(cls) -> Self:
        if cls.fixed_length is not None:
            return cls.parse(b"\x00" * cls.fixed_length)
        return super().default()

    @classmethod
    def __init_subclass__(cls) -> None:
        if hasattr(cls, "constraint_spec"):
            if (  # Fixed-length encoding (§6.5.1)
                isinstance(cls.constraint_spec, SizeConstraint)
                and cls.constraint_spec.min_size is None
            ):
                cls.fixed_length = cls.constraint_spec.max_size
