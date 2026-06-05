from dataclasses import dataclass
from StructResult.result import Error
from typing import ClassVar, Optional, Self, Any
from .type import BuiltinType, INTEGER, Simple, is_classvar, InitError


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


class EnumeratedType(Simple[INTEGER], BuiltinType):
    """
    ENUMERATED type (X.680 §19)
    NATIVE REPRESENTATION: int (non-negative enumeration index)

    Subclassing pattern — declare members as `Final[int]` annotations:
        class AccessResult(EnumeratedType):
            SUCCESS: Final[int] = 0
            OBJECT_UNDEFINED: Final[int] = 1
            ACCESS_VIOLATED: Final[int] = 5  # non-contiguous allowed

    Implicitly tagged subtypes follow the same pattern:
        class ApplicationReference(ImplicitTaggedType, EnumeratedType):
            tag: ClassVar[int] = 0
            OTHER: Final[int] = 0
            TIME_ELAPSED: Final[int] = 1

    Standards compliance:
    - Values: non-negative integers (X.680 §19.3, §19.6)
    - Tag: UNIVERSAL 10 (X.680 §19.7)
    - XML notation: <identifier/> (X.680 §19.8)
    - A-XDR constraint: 0..255 (IEC 61334-6 §6.77) — enforced in codecs
    - Supports NamedNumber syntax (identifier "(" number ")") and implicit numbering
    """
    members: ClassVar[tuple[EnumerationMember, ...]] = ()
    value: INTEGER

    @classmethod
    def validate(cls, value: Any) -> None | Error:
        if isinstance(value, int):
            return None
        return Error.from_e(InitError(f"got {value=}, expected ENUM"))

    def __init_subclass__(cls) -> None:
        """
        Build <members> tuple from `Final[int]` class annotations.
        Ignores ClassVar members.
        """
        members: list[EnumerationMember] = []
        if hasattr(cls, "members"):
            members.extend(cls.members)
        for identifier, type_ in cls.__annotations__.items():
            if is_classvar(type_):
                continue
            if (
                hasattr(cls, identifier)
                and isinstance(value := cls.__dict__[identifier], int)
            ):
                members.append(EnumerationMember(identifier, value))
        cls.members = tuple(members)

    @classmethod
    def default(cls) -> Self:
        """Default value: first member in the list."""
        if len(cls.members) == 0:
            return cls(0)  # Default to 0 if no members defined, though this may be invalid
        return cls(cls.members[0].value)

    def __str__(self) -> str:
        """
        ASN.1 value notation per X.680 §19.8:
        - Returns identifier if defined (e.g., "success")
        - Falls back to integer string otherwise (e.g., "42")
        """
        if ident := self._get_identifier(self.value):
            return ident
        return str(self.value)

    def __repr__(self) -> str:
        if (
            len(self.members) != 0
            and (name := self._get_identifier(self.value))
        ):
            return f"{self.__class__.__name__}.{name.upper()}"
        return f"{self.__class__.__name__}({self.value})"

    @property
    def identifier(self) -> Optional[str]:
        """Get identifier string for current value if defined, else None."""
        return self._get_identifier(self.value)

    def __int__(self) -> int:
        """Native integer conversion (required for codec implementations)."""
        return self.value

    def __eq__(self, value: object) -> bool:
        if isinstance(value, int):
            return self.value == value
        if isinstance(value, EnumeratedType):
            return self.value == value.value
        raise NotImplementedError

    def _get_identifier(self, value: int) -> Optional[str]:
        """Get identifier for integer value."""
        for m in self.members:
            if m.value == value:
                return m.identifier
        return None
