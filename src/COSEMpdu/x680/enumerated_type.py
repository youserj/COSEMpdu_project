from dataclasses import dataclass
from typing import ClassVar, Iterator, Optional, Self
from .type import BuiltinType, INTEGER, Simple


@dataclass(frozen=True)
class EnumerationMember:
    """
    EnumerationMember ::= identifier | identifier "(" number ")" | identifier "(" DefinedValue ")"
    Represents a single enumeration item with identifier and assigned value (X.680 §19.1, §19.3-19.6).
    """
    identifier: str
    value: int  # non-negative enumeration index per X.680

    def __str__(self) -> str:
        return f"{self.identifier}({self.value})"


class EnumerationList:
    """
    EnumerationList ::= EnumerationItem | EnumerationList "," EnumerationItem
    Base container for enumeration members (X.680 §19). Subclasses define `members` ClassVar.

    Supports:
    - Lookup by identifier (str) → value (int)
    - Lookup by value (int) → identifier (str)
    - Membership checks for both
    """
    members: ClassVar[tuple[EnumerationMember, ...]]

    def get_value(self, identifier: str) -> Optional[int]:
        """Get integer value for identifier (X.680 §19.8)."""
        for m in self.members:
            if m.identifier == identifier:
                return m.value
        return None

    def get_identifier(self, value: int) -> Optional[str]:
        """Get identifier for integer value."""
        for m in self.members:
            if m.value == value:
                return m.identifier
        return None

    def __contains__(self, item: str | int) -> bool:
        """Check membership: 'success' in enum_list or 0 in enum_list"""
        return (isinstance(item, str) and self.get_value(item) is not None) or \
               (isinstance(item, int) and self.get_identifier(item) is not None)

    def __iter__(self) -> Iterator[EnumerationMember]:
        return iter(self.members)

    def __len__(self) -> int:
        return len(self.members)

    def __str__(self) -> str:
        return "{" + ", ".join(str(m) for m in self.members) + "}"


class EnumeratedType(Simple[INTEGER], BuiltinType):
    """
    ENUMERATED type (X.680 §19)
    NATIVE REPRESENTATION: int (non-negative enumeration index)

    Subclassing pattern (matches BitStringType.named_bits pattern):
        class AccessResultMembers(EnumerationList):
            members: ClassVar[tuple[EnumerationMember, ...]] = (
                EnumerationMember("success", 0),
                EnumerationMember("object-undefined", 1),
                EnumerationMember("access-violated", 5),  # non-contiguous allowed
            )

        class AccessResult(EnumeratedType):
            named_members: ClassVar[EnumerationList] = AccessResultMembers()

    Standards compliance:
    - Values: non-negative integers (X.680 §19.3, §19.6)
    - Tag: UNIVERSAL 10 (X.680 §19.7)
    - XML notation: <identifier/> (X.680 §19.8)
    - A-XDR constraint: 0..255 (IEC 61334-6 §6.77) — enforced in codecs
    - Supports NamedNumber syntax (identifier "(" number ")") and implicit numbering
    """
    named_members: ClassVar[Optional[EnumerationList]] = None
    value: INTEGER

    @classmethod
    def default(cls) -> Self:
        """Default value: first member in the list."""
        if cls.named_members is None:
            return cls(0)  # Default to 0 if no members defined, though this may be invalid
        return cls(cls.named_members.members[0].value)

    def __str__(self) -> str:
        """
        ASN.1 value notation per X.680 §19.8:
        - Returns identifier if defined in named_members (e.g., "success")
        - Falls back to integer string otherwise (e.g., "42")
        """
        if self.named_members and (ident := self.named_members.get_identifier(self.value)):
            return ident
        return str(self.value)

    def __repr__(self) -> str:
        if (
            self.named_members
            and (name := self.named_members.get_identifier(self.value))
        ):
            return f"{self.__class__.__name__}.{name.upper()}"
        return f"{self.__class__.__name__}({self.value})"

    @property
    def identifier(self) -> Optional[str]:
        """Get identifier string for current value if defined, else None."""
        return self.named_members.get_identifier(self.value) if self.named_members else None

    @classmethod
    def from_identifier(cls, identifier: str) -> Self:
        """
        Create instance from enumeration identifier (X.680 §19.8).
        Raises KeyError if identifier not found in named_members.
        """
        if cls.named_members is None:
            raise KeyError(f"Type {cls.__name__} has no named members defined")
        if (val := cls.named_members.get_value(identifier)) is None:
            raise KeyError(f"Identifier '{identifier}' not found in {cls.__name__}")
        return cls(val)

    def __int__(self) -> int:
        """Native integer conversion (required for codec implementations)."""
        return self.value
