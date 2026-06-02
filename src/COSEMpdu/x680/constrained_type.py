"""
Constraint specifications (X.680 §45-47) and validation mixins.

Standards:
    - X.680 §45: Constrained types
    - X.680 §46: Elements
    - X.680 §47: Subtype elements
"""

from dataclasses import dataclass
from typing import ClassVar, Optional, Protocol, Any, Self, cast
from StructResult.result import Error, ValueOrError
from ..byte_buffer import ByteBuffer
from .type import Type, OCTET_STRING, INTEGER, BIT_STRING
from .integer_type import IntegerType
from .bit_string import BitStringType
from .octet_string_type import OctetStringType
from .sequence_of_type import SequenceOfType


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
                raise ConstraintError(f"Size must be {self.max_size}, got {value}")
        elif value < self.min_size:
            raise ConstraintError(f"Size must be at least {self.min_size}, got {value}")
        elif value > self.max_size:
            raise ConstraintError(f"Size must be < {self.max_size}, got {value}")
        return True

    def __str__(self) -> str:
        if self.min_size is None:
            inner = str(self.max_size)
        else:
            inner = f"{self.min_size}..{self.max_size}"
        if inner.startswith("(") and inner.endswith(")"):
            return f"SIZE{inner}"
        return f"SIZE({inner})"


class ConstraintError(Exception):
    """Raised when a constrained-type value fails its constraint check.

    Caught by :meth:`ConstrainedType.get_lc` and converted to a safe
    :class:`~StructResult.result.Error` result instead of propagating
    as an unhandled exception during decoding.
    """


class ConstrainedType(Type, Protocol):
    """Mixin providing constraint validation for ASN.1 constrained types.

    Inherits from :class:`Type` and :class:`~typing.Protocol` so it can
    be combined with any concrete encoding type (A-XDR, BER, …) via
    multiple inheritance without diamond‑protocol conflicts.

    .. rubric:: Class Variables

    ``constraint_spec``
        A :class:`ConstraintSpec` instance (e.g. :class:`ValueRange`,
        :class:`SizeConstraint`) that describes the permitted values.

    ``exception_spec``
        Optional :class:`ExceptionSpec` (currently unused — reserved
        for exception‑spec handling per X.680 §48).

    .. rubric:: Decoding Safety

    :meth:`get_lc` intercepts :class:`ConstraintError` raised during
    decoding and converts it to a safe
    :class:`~StructResult.result.Error`, allowing the caller to handle
    constraint violations gracefully without a hard exception.
    """
    constraint_spec: ClassVar[ConstraintSpec]
    exception_spec: ClassVar[Optional[ExceptionSpec]] = None

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        try:
            return super().get_lc(buf)
        except ConstraintError as e:
            return Error.from_e(e, msg="ConstrainedError")


class ConstrainedIntegerType(ConstrainedType, IntegerType, Protocol):
    """Integer type bounded by a :class:`ValueRange` constraint.

    Automatically derives ``signed`` and ``fixed_length`` from the
    constraint at class‑creation time via :meth:`_init_subclass`.
    """
    fixed_length: ClassVar[Optional[int]] = None
    signed: ClassVar[bool] = True

    @classmethod
    def _init_subclass(cls) -> None:
        """Called on subclass creation — derives ``signed`` and ``fixed_length``.

        If the lower endpoint of the :class:`ValueRange` is >= 0 the
        integer is treated as unsigned.  ``fixed_length`` is computed
        as the minimum number of octets needed to hold the range width.
        """
        if isinstance(v_r := cls.constraint_spec, ValueRange):
            if v_r.lower_endpoint >= 0:
                cls.signed = False
            cls.fixed_length = max(1, ((v_r.upper_endpoint - v_r.lower_endpoint).bit_length() + 7) // 8)

    def __init__(self, value: INTEGER) -> None:
        """Validate ``value`` against the :class:`ValueRange` constraint."""
        if (
            isinstance(v_r := self.constraint_spec, ValueRange)
            and not v_r.contains(value)
        ):
            raise ConstraintError(f"{value=} outside range [{v_r.lower_endpoint}..{v_r.upper_endpoint}]")
        super().__init__(value)


class ConstrainedBitStringType(ConstrainedType, BitStringType):
    """BIT STRING bounded by a :class:`SizeConstraint`.

    .. rubric:: Fixed‑length encoding (IEC 61334‑6 §6.4.1)

    When ``constraint_spec`` is a :class:`SizeConstraint` with only a
    ``max_size`` (i.e. ``min_size is None``) the subclass is treated as
    **fixed‑length** — ``fixed_length`` is set automatically and the
    length field is omitted during encoding.
    """
    fixed_length: ClassVar[Optional[int]] = None

    @classmethod
    def _init_subclass(cls) -> None:
        """Set ``fixed_length`` when the constraint specifies an exact size."""
        if (
            isinstance(cls.constraint_spec, SizeConstraint)
            and cls.constraint_spec.min_size is None
        ):
            cls.fixed_length = cls.constraint_spec.max_size

    def __init__(self, value: BIT_STRING) -> None:
        """Validate ``value`` length against the :class:`SizeConstraint`."""
        if (
            isinstance(self.constraint_spec, SizeConstraint)
            and not self.constraint_spec.contains(len(value))
        ):
            raise ConstraintError(f"got {len(value)}, expected {self.constraint_spec}")
        super().__init__(value)


class ConstrainedSequenceOfType[T: Type](ConstrainedType, SequenceOfType[T]):
    """SEQUENCE OF bounded by a :class:`SizeConstraint`.

    .. rubric:: Fixed‑length encoding (IEC 61334‑6 §6.4.1)

    When ``constraint_spec`` is a :class:`SizeConstraint` with only a
    ``max_size`` (i.e. ``min_size is None``) the sequence is treated as
    **fixed‑length** — ``fixed_length`` is set automatically.
    """
    fixed_length: ClassVar[Optional[int]] = None
    constraint_spec: ClassVar[ConstraintSpec] = None

    @classmethod
    def _init_subclass(cls) -> None:
        """Set ``fixed_length`` when the constraint specifies an exact size."""
        if (
            isinstance(cls.constraint_spec, SizeConstraint)
            and cls.constraint_spec.min_size is None
        ):
            cls.fixed_length = cls.constraint_spec.max_size

    def __init__(self, value: list[T] = []) -> None:
        """Validate the number of elements against ``fixed_length``."""
        if (
            isinstance(length := self.fixed_length, int)
            and length != len(value)
        ):
            raise ConstraintError(f"got {len(value)}, expected {self.constraint_spec}")
        super().__init__(value)


class ConstrainedOctetString(ConstrainedType, OctetStringType):
    """OCTET STRING bounded by a :class:`SizeConstraint`.

    .. rubric:: Fixed‑length encoding (IEC 61334‑6 §6.4.1)

    When ``constraint_spec`` is a :class:`SizeConstraint` with only a
    ``max_size`` (i.e. ``min_size is None``) the octet string is treated
    as **fixed‑length** — ``fixed_length`` is set automatically.
    """
    fixed_length: ClassVar[Optional[int]] = None

    @classmethod
    def _init_subclass(cls) -> None:
        """Set ``fixed_length`` when the constraint specifies an exact size."""
        if (
            isinstance(getattr(cls, "constraint_spec", None), SizeConstraint)
            and cast("SizeConstraint", cls.constraint_spec).min_size is None
        ):
            cls.fixed_length = cast("SizeConstraint", cls.constraint_spec).max_size

    def __init__(self, value: OCTET_STRING) -> None:
        """Validate the octet‑string length against ``fixed_length``."""
        if (
            isinstance(length := self.fixed_length, int)
            and length != len(value)
        ):
            raise ConstraintError(f"got {len(value)}, expected {self.constraint_spec}")
        super().__init__(value)

    @classmethod
    def default(cls) -> Self:
        """Return a default value — all‑zeroes for fixed‑length strings."""
        if cls.fixed_length is not None:
            return cls(b"\x00" * cls.fixed_length)
        return super().default()
