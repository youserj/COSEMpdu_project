# src/COSEMpdu/x680/integer_type.py
from dataclasses import dataclass
from typing import ClassVar, Iterator, Optional, Self, Any, Protocol
from .type import BuiltinType, ValueRange, Constraint, INTEGER, TYPE_VALUE, Type, SEQUENCE_OF


@dataclass(frozen=True)
class NamedNumber:
    """
    NamedNumber ::= identifier "(" SignedNumber ")" | identifier "(" DefinedValue ")"
    Represents a named integer constant (X.680 §18.1, §18.3-18.6).
    
    Notes:
    - Values may be negative (SignedNumber)
    - Used solely in value notation (X.680 §18.3: "not significant in type definition")
    - Identifiers and values must be unique within NamedNumberList (X.680 §18.5, §18.6)
    """
    identifier: str
    value: int  # Signed integer (may be negative)

    def __str__(self) -> str:
        sign = "-" if self.value < 0 else ""
        abs_val = abs(self.value)
        return f"{self.identifier}({sign}{abs_val})"


@dataclass
class NamedNumberList:
    """
    NamedNumberList ::= NamedNumber | NamedNumberList "," NamedNumber
    Container for named integer constants (X.680 §18.1).
    
    Supports:
    - Lookup by identifier → value
    - Lookup by value → identifier
    - Membership checks
    """
    members: tuple[NamedNumber, ...]

    def get_value(self, identifier: str) -> Optional[int]:
        """Get integer value for identifier (X.680 §18.10)."""
        for nn in self.members:
            if nn.identifier == identifier:
                return nn.value
        return None

    def get_identifier(self, value: int) -> Optional[str]:
        """Get identifier for integer value."""
        for nn in self.members:
            if nn.value == value:
                return nn.identifier
        return None

    def __contains__(self, item: str | int) -> bool:
        """Check membership: 'success' in list or 0 in list"""
        return (isinstance(item, str) and self.get_value(item) is not None) or \
               (isinstance(item, int) and self.get_identifier(item) is not None)

    def __iter__(self) -> Iterator[NamedNumber]:
        return iter(self.members)

    def __len__(self) -> int:
        return len(self.members)

    def __str__(self) -> str:
        return "{" + ", ".join(str(nn) for nn in self.members) + "}"


@dataclass
class IntegerType(BuiltinType, Protocol):
    """
    INTEGER type (X.680 §18)
    NATIVE REPRESENTATION: int (arbitrary precision)

    Subclassing pattern (matches EnumeratedType.named_members):
        class AccessResultNumbers(NamedNumberList):
            members: ClassVar[tuple[NamedNumber, ...]] = (
                NamedNumber("success", 0),
                NamedNumber("object-undefined", 1),
                NamedNumber("access-violated", -5),  # negative allowed
            )

        class AccessResult(IntegerType):
            named_numbers: ClassVar[NamedNumberList] = AccessResultNumbers()

    Standards compliance:
    - Tag: UNIVERSAL 2 (X.680 §18.8)
    - Values: arbitrary precision integers (X.680 §3.6.41, §6.3.34)
    - NamedNumberList used ONLY in value notation (X.680 §18.3)
    - Supports negative values and non-contiguous ranges
    - A-XDR constraint: 0..255 for ENUMERATED (IEC 61334-6 §6.77), NOT for INTEGER
    """
    named_numbers: ClassVar[Optional[NamedNumberList]] = None
    value: INTEGER

    def check_constraint(self, constraint: Constraint[Any]) -> None:
        if isinstance(v_r := constraint.constraint_spec, ValueRange):
            if not v_r.contains(self.value):
                raise ValueError(f"Value {self.value!r} outside range [{v_r.lower_endpoint}..{v_r.upper_endpoint}]")
            return
        raise NotImplementedError(f"Validation not implemented for {type(constraint.constraint_spec)}")

    def __str__(self) -> str:
        """
        ASN.1 value notation per X.680 §18.9-18.10:
        - Returns identifier if defined in named_numbers (e.g., "success")
        - Falls back to signed integer string otherwise (e.g., "-5", "42")
        """
        if self.named_numbers and (ident := self.named_numbers.get_identifier(self.value)):
            return ident
        return str(self.value)

    def __int__(self) -> int:
        """Native integer conversion (required for codec implementations)."""
        return self.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    @property
    def identifier(self) -> Optional[str]:
        """Get identifier string for current value if defined, else None."""
        return self.named_numbers.get_identifier(self.value) if self.named_numbers else None

    @classmethod
    def from_identifier(cls, identifier: str) -> Self:
        """
        Create instance from named identifier (X.680 §18.10).
        Raises KeyError if identifier not found in named_numbers.
        """
        if cls.named_numbers is None:
            raise KeyError(f"Type {cls.__name__} has no named numbers defined")
        if (val := cls.named_numbers.get_value(identifier)) is None:
            raise KeyError(f"Identifier '{identifier}' not found in {cls.__name__}")
        return cls(val)
