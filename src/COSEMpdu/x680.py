"""
ASN.1 X.680 Type Definitions

Unified module containing all ASN.1 type definitions from:
- type.py: Base types, protocols, and helper classes
- tag.py: ASN.1 tag definitions
- integer_type.py: INTEGER type
- bit_string.py: BIT STRING type
- boolean_type.py: BOOLEAN type
- null_type.py: NULL type
- octet_string_type.py: OCTET STRING type
- enumerated_type.py: ENUMERATED type
- generalized_time.py: GeneralizedTime type
- object_identifier_type.py: OBJECT IDENTIFIER type
- choice_type.py: CHOICE type
- sequence_of_type.py: SEQUENCE OF type
- sequence_type.py: SEQUENCE type
- constrained_type.py: Constrained type definitions

Standards:
    - X.680: Abstract Syntax Notation One (ASN.1)
    - X.690: BER encoding rules
    - IEC 61334-6: DLMS/COSEM A-XDR encoding
"""

# =============================================================================
# Combined external imports
# =============================================================================

from dataclasses import dataclass
from enum import IntEnum
from types import UnionType
from typing import (Self, Protocol, Optional, Any, runtime_checkable, cast,
                    ClassVar, get_origin, Iterator, overload, Union,
                    get_args)
from StructResult.result import ValueOrError, Error

# =============================================================================
# 1. type.py — Base types, protocols, and helper classes
# =============================================================================


@dataclass(frozen=True)
class NamedValue:
    """
    NamedValue ::= identifier "(" SignedNumber ")" | identifier "(" DefinedValue ")" |
                   identifier "(" number ")"  -- NamedBit (BIT STRING)

    Unified representation for:
    - INTEGER NamedNumberList (X.680 §18.1, §18.3-18.6) — value is the integer constant
    - ENUMERATED EnumerationItem (X.680 §19.1, §19.3-19.6) — value is the enum index
    - BIT STRING NamedBit (X.680 §22.4) — value is the bit position (LSB0)

    Notes:
    - Values may be negative for INTEGER (SignedNumber); non-negative for ENUMERATED/BIT STRING
    - Used solely in value notation (X.680 §18.3: "not significant in type definition")
    - Identifiers and values must be unique within their list (X.680 §18.5, §18.6)
    """
    identifier: str
    value: int  # Signed integer for INTEGER; non-negative for ENUMERATED/BIT STRING

    def __str__(self) -> str:
        sign = "-" if self.value < 0 else ""
        abs_val = abs(self.value)
        return f"{self.identifier}({sign}{abs_val})"

    def __int__(self) -> int:
        """Bit mask interpretation (1 << value) for BIT STRING usage."""
        return 1 << self.value


type INTEGER = int
type REAL = float
type STRING = str
type BIT_STRING = tuple[int, ...]
type BOOLEAN = int
type NULL = None
type OCTET_STRING = bytes
type OBJECT_IDENTIFIER = tuple[int, ...]
type SIMPLE = INTEGER | STRING | BIT_STRING | BOOLEAN | OCTET_STRING | OBJECT_IDENTIFIER | NULL


class InitError(Exception):
    """marked Type init error"""


@runtime_checkable
class Type(Protocol):
    """
    Encoding Data Value component per X.690 §8.1.2

    Base protocol for ASN.1 types with A-XDR/BER encoding support.

    IMPORTANT DESIGN NOTES:

    1. TAG SEMANTICS (IEC 61334-6:2000 §5.1, §6.6, §6.7):
       - tag attribute represents the ASN.1 universal tag (e.g., INTEGER=2)
       - A-XDR does NOT systematically encode tags:
         * CHOICE alternatives: ALWAYS encode raw tag number (1 byte)
         * ASN.1 explicit tags ([APPLICATION x]): encode in BER format
         * SEQUENCE components: NEVER encode tags (even if explicitly tagged)
         * Base constrained types (INTEGER(0..255)): NEVER encode tags

    2. BER ENCODING:
       - Systematically encodes tags (TLV structure)
       - Used for EXTERNAL, EMBEDDED PDV, ASN.1 explicit tags

    3. TRANSCRIPT USAGE:
       - Used ONLY for human-readable value representation/parsing
       - Contains pure data values (str/list[str]), NO structural metadata
       - Field names and type context are handled by container types (SEQUENCE, etc.)
    """

    @classmethod
    def default(cls) -> Self:
        """Return default value instance for this type, if defined."""
        ...

    def __eq__(self, value: object) -> bool: ...


class Simple[T: SIMPLE](Type):
    value: T

    def __init__(self, value: T) -> None:
        self.value = value

    @classmethod
    def new(cls, value: T) -> ValueOrError[Self]:
        return cls(value)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Simple):
            raise TypeError(f"unknown value type: {object.__class__}")
        return (
            self.__class__ == value.__class__
            and self.value == value.value
        )


type SEQUENCE_OF[U: Type] = list[U]


class BuiltinType(Type, Protocol):
    """Built-in ASN.1 types per X.680 §16.2 (BOOLEAN, INTEGER, etc.)"""


@dataclass
class ReferencedType(Type, Protocol):
    """Referenced types per X.680 §16.3"""


class UsefulType(Simple[STRING], ReferencedType):
    """16.3"""


@dataclass
class NamedType[T: Type]:
    """
    Named component type for SEQUENCE/SET (X.680 §24.2).

    Represents a single component in a structured type with:
    - Identifier (field name)
    - Type (ASN.1 type)

    Example ASN.1:
        MySequence ::= SEQUENCE {
            id        INTEGER,                    -- REQUIRED
            name      VisibleString OPTIONAL,     -- OPTIONAL
            timeout   INTEGER DEFAULT 30          -- DEFAULT
        }

    Attributes:
        identifier: Field name (X.680 §24.2)
        type: ASN.1 type for this component

    Note:
        In CHOICE context, the component identifier is used in ChoiceValue notation:
        ChoiceValue ::= identifier ":" Value (X.680 Clause 28.10)
    """
    identifier: str
    type_: type[T]


@dataclass
class OptionalNamedType(NamedType[Type]):
    """
    OPTIONAL component type for SEQUENCE/SET (X.680 §24.2).

    Represents an optional component that may be absent from encoding.

    Example ASN.1:
        MySequence ::= SEQUENCE {
            name      VisibleString OPTIONAL
        }

    Note:
        - A-XDR: Preceded by BOOLEAN presence flag (§6.8)
        - BER: Absence detected by end-of-contents or tag mismatch (§8.9.3)
    """
    def __str__(self) -> str:
        return f"OPTIONAL {self.type_.__name__}"


@dataclass
class DefaultNamedType[T: Type](NamedType[T]):
    """
    DEFAULT component type for SEQUENCE/SET (X.680 §24.2).

    Represents a component with a default value that may be absent from encoding.

    Example ASN.1:
        MySequence ::= SEQUENCE {
            timeout   INTEGER DEFAULT 30
        }

    Attributes:
        default: Default value instance

    Note:
        - A-XDR: Preceded by BOOLEAN presence flag (§6.8)
        - BER: Omit encoding if value equals default (§8.9.3)
        - DEFAULT without value uses type's intrinsic default
    """
    default: T

    def __str__(self) -> str:
        return f"DEFAULT {self.type_.__name__} {self.default}"


class CharacterStringType(Type, Protocol):
    """"""


@dataclass
class RestrictedCharacterStringType(Simple[STRING], CharacterStringType):
    value: STRING

    @classmethod
    def default(cls) -> Self:
        """Default to empty string"""
        return cls("")


@dataclass
class GraphicString(RestrictedCharacterStringType):
    ...


@dataclass
class VisibleString(RestrictedCharacterStringType):
    ...


@dataclass
class Utf8String(RestrictedCharacterStringType):
    ...


def is_classvar(type_: Type) -> bool:
    """Check if annotation is ClassVar[X]."""
    return get_origin(type_) is ClassVar


# =============================================================================
# 2. tag.py — ASN.1 Tag definitions
# =============================================================================


@dataclass(frozen=True)
class UniversalClassTagAssignments:
    """ISO/IEC 8824-1:2021 table 1"""
    Reserved = 0
    Boolean = 1
    Integer = 2
    BitString = 3
    OctetString = 4
    Null = 5
    ObjectIdentifier = 6
    ObjectDescriptor = 7
    InstanceOf = 8
    External = 8
    Real = 9
    Enumerated = 10
    EmbeddedPdv = 11
    UTF8String = 12
    RelativeOID = 13
    Sequence = 16
    SequenceOf = 16
    Set = 17
    SetOf = 17
    NumericString = 18
    PrintableString = 19
    TeletexString = 20
    T61String = 20
    VideotexString = 21
    IA5String = 22
    UTCTime = 23
    GeneralizedTime = 24
    GraphicString = 25
    VisibleString = 26
    ISO646String = 26
    GeneralString = 27
    UniversalString = 28
    CharacterString = 29
    BMPString = 30


class Class(IntEnum):
    UNIVERSAL = 0
    APPLICATION = 0b01_000000
    CONTEXT_SPECIFIC = 0b10_000000
    PRIVATE = 0b11_000000


@dataclass
class Tag:
    """
    ASN.1 tag (X.680 31.2)
    A tag consists of:
    - Class: UNIVERSAL, APPLICATION, CONTEXT-SPECIFIC, PRIVATE
    - Tag number: non-negative integer
    """
    class_number: int
    class_: Class = Class.UNIVERSAL

    def __str__(self) -> str:
        """ASN.1 notation: [UNIVERSAL 2], [APPLICATION 5], [0] etc."""
        if self.class_ == Class.CONTEXT_SPECIFIC:
            return f"[{self.class_number}]"
        return f"[{self.class_} {self.class_number}]"

    def __repr__(self) -> str:
        args = f"{self.class_number}, {self.class_}"
        return f"Tag({args})"

    def is_universal(self) -> bool:
        return self.class_ == Class.UNIVERSAL

    def is_application(self) -> bool:
        return self.class_ == Class.APPLICATION

    def is_context_specific(self) -> bool:
        return self.class_ == Class.CONTEXT_SPECIFIC

    def is_private(self) -> bool:
        return self.class_ == Class.PRIVATE

    @classmethod
    def universal(cls, number: int) -> "Tag":
        """Create UNIVERSAL class tag"""
        return cls(number, Class.UNIVERSAL)

    @classmethod
    def application(cls, number: int) -> "Tag":
        """Create APPLICATION class tag"""
        return cls(number, Class.APPLICATION)

    @classmethod
    def context(cls, number: int) -> "Tag":
        """Create CONTEXT-SPECIFIC class tag"""
        return cls(number, Class.CONTEXT_SPECIFIC)

    @classmethod
    def private(cls, number: int) -> "Tag":
        """Create PRIVATE class tag"""
        return cls(number, Class.PRIVATE)

    def __int__(self) -> int:
        return self.class_number


class Members(Protocol):
    members: ClassVar[tuple[NamedValue, ...]] = ()

    @classmethod
    def build_members(cls, inherit: bool = False) -> None:
        """
        Build <members> ClassVar from int class annotations.

        Scans cls.__annotations__ for int-valued attributes (skipping ClassVar),
        creates NamedValue entries, and assigns them to cls.members.

        If inherit=True, existing cls.members are preserved and extended.

        Used by IntegerType, EnumeratedType, and BitStringType __init_subclass__.
        """
        members: list[NamedValue] = []
        if inherit and hasattr(cls, "members"):
            members.extend(cls.members)
        for identifier, type_ in cls.__annotations__.items():
            if is_classvar(type_):
                continue
            if (
                hasattr(cls, identifier)
                and isinstance(value := cls.__dict__[identifier], int)
            ):
                members.append(NamedValue(identifier, value))
        cls.members = tuple(members)


# =============================================================================
# 3. integer_type.py — INTEGER type
# =============================================================================


class IntegerType(Members, Simple[INTEGER], BuiltinType):
    """
    INTEGER type (X.680 §18)
    NATIVE REPRESENTATION: int (arbitrary precision)

    Subclassing pattern — declare members as `int` annotations:
        class AccessResult(IntegerType):
            SUCCESS: int = 0
            OBJECT_UNDEFINED: int = 1
            ACCESS_VIOLATED: int = -5  # negative allowed

    Note:
    - members is NamedNumberList ::= NamedNumber | NamedNumberList "," NamedNumber (X.680 §18.1)

    Standards compliance:
    - Tag: UNIVERSAL 2 (X.680 §18.8)
    - Values: arbitrary precision integers (X.680 §3.6.41, §6.3.34)
    - NamedNumberList used ONLY in value notation (X.680 §18.3)
    - Supports negative values and non-contiguous ranges
    - A-XDR constraint: 0..255 for ENUMERATED (IEC 61334-6 §6.77), NOT for INTEGER
    """

    def __init_subclass__(cls) -> None:
        cls.build_members()

    @classmethod
    def default(cls) -> Self:
        """Default value: 0"""
        return cls(0)

    def __str__(self) -> str:
        """
        ASN.1 value notation per X.680 §18.9-18.10:
        - Returns identifier if defined in members (e.g., "Success")
        - Falls back to signed integer string otherwise (e.g., "-5", "42")
        """
        if ident := self._get_identifier(self.value):
            return ident
        return str(self.value)

    def __int__(self) -> int:
        """Native integer conversion (required for codec implementations)."""
        return self.value

    def __repr__(self) -> str:
        if (
            len(self.__class__.members) != 0
            and (name := self._get_identifier(self.value))
        ):
            return f"{self.__class__.__name__}.{name}"
        return f"{self.__class__.__name__}({self.value})"

    def _get_identifier(self, value: int) -> Optional[str]:
        """Get identifier for integer value from members."""
        for m in self.__class__.members:
            if m.value == value:
                return m.identifier
        return None

    def __lt__(self, other: Self) -> bool:
        return self.value < other.value

# =============================================================================
# 4. bit_string.py — BIT STRING type
# =============================================================================


class BitStringType(Members, Simple[BIT_STRING], BuiltinType):
    """
    BIT STRING type (X.680 22)

    Native representation:
    - value: tuple[int, ...] of bits (0/1) in LSB0 order
    - members: ClassVar[tuple[NamedValue, ...]] — bit names defined for this type.
        Automatically populated in __init_subclass__ by scanning Final[int] class annotations.

    ASN.1 examples:
        Status ::= BIT STRING { read(0), write(1), execute(2) }
        Bits ::= BIT STRING { flag0(0), flag1(1), flag2(2) } (SIZE(4))

    Usage:
        class Status(BitStringType):
            read: Final[int] = 0
            write: Final[int] = 1
            execute: Final[int] = 2
    """
    value: BIT_STRING

    def __init_subclass__(cls) -> None:
        cls.build_members()

    @classmethod
    def default(cls) -> Self:
        """Default value: all bits 0"""
        if len(cls.members) != 0:
            return cls((0,) * (cls.members[-1].value + 1))
        return cls(())

    @classmethod
    def from_bin(cls, bin_str: str) -> Self:
        """
        Create from binary string: '101' -> (1,0,1)
        ASN.1 notation: '101'B
        """
        # Remove ASN.1 quotes and B suffix
        if bin_str.startswith("'") and bin_str.endswith("'B"):
            bin_str = bin_str[1:-2]
        elif bin_str.endswith("'B"):
            bin_str = bin_str[:-2]
        # Validate
        if not all(c in "01" for c in bin_str):
            raise ValueError(f"Invalid binary string: {bin_str}")
        bits = tuple(int(c) for c in bin_str)
        return cls(bits)

    @classmethod
    def from_hex(cls, hex_str: str, bit_length: Optional[int] = None) -> Self:
        """
        Create from hex string: 'A5' -> (1,0,1,0,0,1,0,1)
        ASN.1 notation: 'A5'H
        """
        if hex_str.startswith("'") and hex_str.endswith("'H"):
            hex_str = hex_str[1:-2]
        elif hex_str.endswith("'H"):
            hex_str = hex_str[:-2]
        data = bytes.fromhex(hex_str)
        bits: list[int] = []
        for byte in data:
            bits.extend([(byte >> i) & 1 for i in range(7, -1, -1)])
        if bit_length is not None:
            bits = bits[:bit_length]
        return cls(tuple(bits))

    @classmethod
    def from_int(cls, value: int, length: int) -> Self:
        """
        Create from integer with given length:
        42, 6 -> 101010 (6 bits)
        """
        bits: list[int] = []
        for i in range(length - 1, -1, -1):
            bits.append((value >> i) & 1)
        return cls(tuple(bits))

    @classmethod
    def from_bytes(cls, data: bytes, bit_length: Optional[int] = None) -> Self:
        """
        Create from bytes (big-endian, MSB first)
        """
        bits: list[int] = []
        for byte in data:
            bits.extend([(byte >> i) & 1 for i in range(7, -1, -1)])
        if bit_length is not None:
            bits = bits[:bit_length]
        return cls(tuple(bits))

    @classmethod
    def from_bits(cls, *bits: int) -> Self:
        """Create with bits set at given positions: (0, 3, 5) -> bits 0,3,5 = 1, rest 0"""
        if not bits:
            return cls.default()
        max_pos = max(bits)
        result = [0] * (max_pos + 1)
        for pos in bits:
            result[pos] = 1
        return cls(tuple(result))

    @classmethod
    def empty(cls) -> Self:
        """Empty bit string"""
        return cls(())

    @classmethod
    def zeros(cls, length: int) -> Self:
        """Bit string of all zeros of given length"""
        return cls(tuple([0] * length))

    @classmethod
    def ones(cls, length: int) -> Self:
        """Bit string of all ones of given length"""
        return cls(tuple([1] * length))

    @property
    def bit_length(self) -> int:
        """Length in bits"""
        return len(self.value)

    @property
    def octet_length(self) -> int:
        """Length in octets (rounded up)"""
        return (len(self.value) + 7) // 8

    @overload
    def __getitem__(self, key: int) -> int: ...

    @overload
    def __getitem__(self, key: slice) -> Self: ...

    def __getitem__(self, key: int | slice) -> int | Self:
        """
        Bit access:
        - int: bits[0] -> first bit (LSB0), returns int (0/1)
        - slice: bits[1:4] -> slice, returns new BitStringType
        """
        if isinstance(key, int):
            # Index access
            if key < 0:
                raise IndexError(f"Bit index {key} out of range [0, ...]")
            if key >= len(self.value):
                # If there is a named_bit with position == key, return 0
                named_bits = self.members
                if named_bits and any(nb.value == key for nb in named_bits):
                    return 0
                raise IndexError(f"Bit index {key} out of range [0, {len(self.value) - 1}]")
            return self.value[key]
        if isinstance(key, slice):
            # Bit string slice
            sliced = self.value[key]
            return self.__class__(sliced)
        raise TypeError(f"Expected int, str or slice, got {type(key)}")

    def __setitem__(self, key: int | slice, value: int | bool | Self) -> None:
        """
        Bit assignment:
        - int: bits[0] = 1 -> set a single bit
        - slice: bits[1:4] = (1,0,1) -> set a slice
        """
        if isinstance(key, int):
            # Set by index
            if key < 0:
                raise IndexError(f"Bit index {key} out of range [0, ...]")
            named_bits = self.__class__.members
            if key >= len(self.value):
                # Auto-expand if key matches a named_bit position
                if named_bits and any(nb.value == key for nb in named_bits):
                    bits = list(self.value)
                    bits.extend([0] * (key - len(self.value) + 1))
                    bits[key] = int(value)
                    self.value = tuple(bits)
                    return
                raise IndexError(f"Bit index {key} out of range [0, {len(self.value) - 1}]")
            bits = list(self.value)
            bits[key] = int(value)
            self.value = tuple(bits)
        elif isinstance(key, slice):
            # Set a slice
            if isinstance(value, (tuple, list)):
                # Value as a sequence of bits
                new_bits = list(self.value)
                new_bits[key] = list(int(v) for v in value)
                self.value = tuple(new_bits)
            elif isinstance(value, self.__class__):
                # Value as another BitStringType
                new_bits = list(self.value)
                new_bits[key] = list(value.value)
                self.value = tuple(new_bits)
            else:
                raise TypeError(f"Expected tuple, list or BitStringType for slice assignment, got {type(value)}")

        else:
            raise TypeError(f"Expected int, str or slice, got {type(key)}")

    def get_value(self, identifier: int, default: int = 0) -> int:
        """Safely get a named bit value"""
        try:
            return self[identifier]
        except KeyError:
            return default

    def set(self, identifier: int, value: int = 1) -> None:
        """Set a named bit"""
        self[identifier] = value

    def clear(self, identifier: int) -> None:
        """Clear a named bit to 0"""
        self[identifier] = 0

    def toggle(self, identifier: int) -> None:
        """Toggle a named bit"""
        self[identifier] = 1 - self[identifier]

    def has_bit(self, identifier: int) -> bool:
        """Check if a named bit is set"""
        return bool(self.get_value(identifier, 0))

    def has_any(self, *identifiers: int) -> bool:
        """Check if at least one of the specified bits is set"""
        return any(self.has_bit(ident) for ident in identifiers)

    def has_all(self, *identifiers: int) -> bool:
        """Check if all specified bits are set"""
        return all(self.has_bit(ident) for ident in identifiers)

    def to_bin(self) -> str:
        """Binary representation: '1011'"""
        return "".join(map(str, self.value))

    def hex(self) -> str:
        """Hexadecimal representation: 'A5'"""
        if not self.value:
            return ""
        # Pad to octet boundary
        padded = list(self.value)
        while len(padded) % 8 != 0:
            padded.append(0)
        # Convert to bytes
        data: list[int] = []
        for i in range(0, len(padded), 8):
            byte = 0
            for j in range(8):
                byte |= (padded[i + j] << (7 - j))
            data.append(byte)
        return bytes(data).hex().upper()

    def __int__(self) -> int:
        """Integer representation (big-endian)"""
        result = 0
        for bit in self.value:
            result = (result << 1) | bit
        return result

    def __bytes__(self) -> bytes:
        """Byte representation with octet-aligned padding"""
        return bytes.fromhex(self.hex())

    def __str__(self) -> str:
        """ASN.1 notation: '101'B or '{read, write}'"""
        named_bits = self.__class__.members
        if named_bits:
            # Show set bit names
            set_bits: list[str] = []
            for named_bit in named_bits:
                if named_bit.value < len(self.value) and self.value[named_bit.value]:
                    set_bits.append(named_bit.identifier)
            if set_bits:
                return "{" + ", ".join(set_bits) + "}"
            return "{}"
        return f"'{self.to_bin()}'B"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_bin()!r})"

    def __and__(self, other: Self) -> Self:
        """Bitwise AND"""
        min_len = min(len(self.value), len(other.value))
        result = tuple(self.value[i] & other.value[i] for i in range(min_len))
        return self.__class__(result)

    def __or__(self, other: Self) -> Self:
        """Bitwise OR"""
        max_len = max(len(self.value), len(other.value))
        result = [0] * max_len
        for i, bit in enumerate(self.value):
            result[i] = bit
        for i, bit in enumerate(other.value):
            result[i] |= bit
        return self.__class__(tuple(result))

    def __xor__(self, other: Self) -> Self:
        """Bitwise XOR"""
        min_len = min(len(self.value), len(other.value))
        result = tuple(self.value[i] ^ other.value[i] for i in range(min_len))
        return self.__class__(tuple(result))

    def __invert__(self) -> Self:
        """Bitwise NOT"""
        result = tuple(1 - b for b in self.value)
        return self.__class__(result)

    def __lshift__(self, shift: int) -> Self:
        """Left shift (append zeros on the right)"""
        if shift < 0:
            return self.__rshift__(-shift)
        bits = list(self.value)
        bits.extend([0] * shift)
        return self.__class__(tuple(bits))

    def __rshift__(self, shift: int) -> Self:
        """Right shift (discard bits from the right)"""
        if shift < 0:
            return self.__lshift__(-shift)
        if shift >= len(self.value):
            return self.__class__(())
        return self.__class__(self.value[:-shift])

    def __add__(self, other: Self) -> Self:
        """Concatenation of bit strings"""
        result = self.value + other.value
        return self.__class__(result)

    def __bool__(self) -> bool:
        """True if at least one bit is set (non-zero)"""
        return any(b == 1 for b in self.value)

    def __contains__(self, item: int) -> bool:
        return bool(self.value[item])


# =============================================================================
# 5. boolean_type.py — BOOLEAN type
# =============================================================================


class BooleanType(Simple[BOOLEAN], BuiltinType):
    """
    BOOLEAN type (X.680 §17)
    NATIVE REPRESENTATION: int
    """
    value: BOOLEAN

    @classmethod
    def default(cls) -> Self:
        """Default value: FALSE"""
        return cls(False)  # noqa: FBT003

    def __bool__(self) -> bool:
        return bool(self.value)

    def __str__(self) -> str:
        return "TRUE" if self.value else "FALSE"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    def __int__(self) -> int:
        return int(self.value)


# =============================================================================
# 6. null_type.py — NULL type
# =============================================================================


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


# =============================================================================
# 7. octet_string_type.py — OCTET STRING type
# =============================================================================


class OctetStringType(Simple[OCTET_STRING], BuiltinType):
    """
    OCTET STRING type (X.680 §22, X.690 §8.7)
    NATIVE REPRESENTATION: bytes

    ASN.1 examples:
        ImageData ::= OCTET STRING
        'A5'H, '10100101'B (converted to bytes internally)

    Standards compliance:
    - Tag: UNIVERSAL 4 (X.680 §22.2)
    - Values: arbitrary sequence of octets (X.680 §6.3.49)
    - XML notation: <OCTET_STRING>hex</OCTET_STRING> (X.680 Table 4)
    """
    value: OCTET_STRING

    @classmethod
    def default(cls) -> Self:
        """Default to empty OCTET STRING"""
        return cls(b"")

    def __len__(self) -> int:
        """Length in octets (X.680 §22.6)"""
        return len(self.value)

    def __bytes__(self) -> bytes:
        """Direct access to native bytes representation"""
        return self.value

    def hex(self) -> str:
        """Hexadecimal string representation (uppercase, no prefix/suffix)"""
        return self.value.hex().upper()

    def __str__(self) -> str:
        """ASN.1 value notation: 'A5'H (X.680 §22.3)"""
        return self.value.hex(" ")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"

    @classmethod
    def empty(cls) -> Self:
        return cls(b"")


# =============================================================================
# 8. enumerated_type.py — ENUMERATED type
# =============================================================================


class EnumeratedType(Members, Simple[INTEGER], BuiltinType):
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

    Note:
    - members is EnumerationItem ::=  identifier | NamedNumber (X.680 §19.1)

    Standards compliance:
    - Values: non-negative integers (X.680 §19.3, §19.6)
    - Tag: UNIVERSAL 10 (X.680 §19.7)
    - XML notation: <identifier/> (X.680 §19.8)
    - A-XDR constraint: 0..255 (IEC 61334-6 §6.77) — enforced in codecs
    - Supports NamedNumber syntax (identifier "(" number ")") and implicit numbering
    """
    value: INTEGER

    def __init_subclass__(cls) -> None:
        cls.build_members()

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


# =============================================================================
# 9. generalized_time.py — GeneralizedTime type
# =============================================================================


class GeneralizedTime(UsefulType):
    """
    ASN.1 GeneralizedTime type (X.680 §42).

    GeneralizedTime represents a calendar date and time of day with
    optional fractional seconds and time zone information.

    Example ASN.1:
        CreationTime ::= GeneralizedTime
        ExpiryTime ::= GeneralizedTime

    Attributes:
        value: String representation in ASN.1 format
               Format: YYYYMMDDHHMMSS[.fff][Z|±HHMM]
               - YYYY: 4-digit year (0000-9999)
               - MM: 2-digit month (01-12)
               - DD: 2-digit day (01-31)
               - HH: 2-digit hour (00-23)
               - MM: 2-digit minute (00-59)
               - SS: 2-digit second (00-60, 60 for leap second)
               - .fff: Optional fractional seconds (1+ digits)
               - Z: UTC time, or ±HHMM: local time offset

    Note:
        - More flexible than UTCTime (supports 4-digit years)
        - Supports fractional seconds precision
        - Supports explicit time zone offsets
        - BER encoding: VisibleString with UNIVERSAL tag 24
        - For DLMS/COSEM, typically used without fractional seconds

    References:
        - X.680 §42: GeneralizedTime notation
        - X.680 Table 1: UNIVERSAL tag 24
        - X.690 §8.23: GeneralizedTime BER encoding
        - IEC 61334-6 §6.12: DLMS GeneralizedTime usage

    Usage pattern:
        # Create from string
        time = GeneralizedTimeType("20240115120000Z")

        # Create with fractional seconds
        time = GeneralizedTimeType("20240115120000.5Z")

        # Create with time zone offset
        time = GeneralizedTimeType("20240115120000+0300")

        # Convert to transcript
        transcript = time.to_transcript()  # "20240115120000Z"

    GeneralizedTime value in ASN.1 string format.

    Valid formats:
    - Basic: YYYYMMDDHHMMSSZ (UTC time)
    - With offset: YYYYMMDDHHMMSS±HHMM (local time)
    - With fractions: YYYYMMDDHHMMSS.fffZ (fractional seconds)

    Note:
        - No separators between components (except optional decimal point)
        - Must terminate with Z or ±HHMM
        - Fractional seconds optional but must have at least one digit
    """

    @classmethod
    def new(cls, value: STRING) -> ValueOrError[Self]:
        """
            Validate GeneralizedTime string format.

            Checks:
            - Minimum length (14 chars + timezone)
            - Numeric components
            - Valid ranges for each component
            - Timezone format (Z or ±HHMM)
            - Fractional seconds format (if present)

            Raises:
                ValueError: If validation fails
        """
        # Minimum length: YYYYMMDDHHMMSS + timezone = 15 chars
        if len(value) < 15:
            return Error.from_e(ValueError(
                f"GeneralizedTime too short: {len(value)} chars, "
                f"minimum 15 (YYYYMMDDHHMMSS+timezone)"
            ))
        # Extract components
        try:
            year = int(value[0:4])
            month = int(value[4:6])
            day = int(value[6:8])
            hour = int(value[8:10])
            minute = int(value[10:12])
            second = int(value[12:14])
        except ValueError as e:
            return Error.from_e(ValueError(f"GeneralizedTime contains non-numeric components: {e}"))
        # Validate ranges
        if not (0 <= year <= 9999):
            return Error.from_e(ValueError(f"Year out of range (0-9999): {year}"))
        if not (1 <= month <= 12):
            return Error.from_e(ValueError(f"Month out of range (1-12): {month}"))
        if not (1 <= day <= 31):
            return Error.from_e(ValueError(f"Day out of range (1-31): {day}"))
        if not (0 <= hour <= 23):
            return Error.from_e(ValueError(f"Hour out of range (0-23): {hour}"))
        if not (0 <= minute <= 59):
            return Error.from_e(ValueError(f"Minute out of range (0-59): {minute}"))
        if not (0 <= second <= 60):  # 60 for leap second
            return Error.from_e(ValueError(f"Second out of range (0-60): {second}"))

        # Validate timezone
        remainder = value[14:]
        if remainder.endswith("Z"):
            # UTC time - check for fractional seconds before Z
            frac_part = remainder[:-1]
            if frac_part and not frac_part.startswith("."):
                return Error.from_e(ValueError(f"Invalid fractional seconds format: {frac_part}, must start with '.'"))
            if frac_part:
                frac = frac_part[1:]
                if not frac:
                    return Error.from_e(ValueError("Fractional seconds must have at least one digit"))
                if not frac.isdigit():
                    return Error.from_e(ValueError(f"Fractional seconds must be numeric: {frac}"))
        elif remainder[0] in ("+", "-"):
            # Timezone offset ±HHMM
            if len(remainder) != 5:
                return Error.from_e(ValueError(f"Invalid timezone offset format: {remainder}, must be ±HHMM (5 chars)"))
            try:
                tz_hour = int(remainder[1:3])
                tz_min = int(remainder[3:5])
                if not (0 <= tz_hour <= 23):
                    return Error.from_e(ValueError(f"Timezone hour out of range (0-23): {tz_hour}"))
                if not (0 <= tz_min <= 59):
                    return Error.from_e(ValueError(f"Timezone minute out of range (0-59): {tz_min}"))
            except ValueError as e:
                return Error.from_e(ValueError(f"Invalid timezone offset: {e}"))
        else:
            return Error.from_e(ValueError(f"GeneralizedTime must end with 'Z' or ±HHMM, got: {remainder}"))
        return cls(value)

    @classmethod
    def default(cls) -> Self:
        return cls("00000101000000Z")  # Default to 0000-01-01T00:00:00Z, though this may be invalid

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns:
            GeneralizedTime value string

        Example:
            >>> str(GeneralizedTimeType("20240115120000Z"))
            '20240115120000Z'
        """
        return self.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value!r})"

    def __eq__(self, other: object) -> bool:
        """
        Compare GeneralizedTime values for equality.

        Two GeneralizedTime values are equal if their string
        representations are identical

        Args:
            other: Another GeneralizedTimeType instance

        Returns:
            True if string values match exactly
        """
        if not isinstance(other, GeneralizedTime):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __lt__(self, other: "GeneralizedTime") -> bool:
        """
        Compare GeneralizedTime values lexicographically.

        Note: This is a string comparison, not a temporal comparison.
        For accurate temporal comparison, convert to datetime first.

        Args:
            other: Another GeneralizedTimeType instance

        Returns:
            True if self.value < other.value (string comparison)
        """
        if not isinstance(other, GeneralizedTime):
            return NotImplemented
        return self.value < other.value

    @property
    def year(self) -> int:
        """Return 4-digit year (0000-9999)."""
        return int(self.value[0:4])

    @property
    def month(self) -> int:
        """Return month (01-12)."""
        return int(self.value[4:6])

    @property
    def day(self) -> int:
        """Return day (01-31)."""
        return int(self.value[6:8])

    @property
    def hour(self) -> int:
        """Return hour (00-23)."""
        return int(self.value[8:10])

    @property
    def minute(self) -> int:
        """Return minute (00-59)."""
        return int(self.value[10:12])

    @property
    def second(self) -> int:
        """Return second (00-60)."""
        return int(self.value[12:14])

    @property
    def has_fractional_seconds(self) -> bool:
        """Check if fractional seconds are present."""
        remainder = self.value[14:]
        if remainder.endswith("Z"):
            return "." in remainder
        if remainder[0] in ("+", "-"):
            frac_part = remainder[1:]
            return "." in frac_part
        return False

    @property
    def fractional_seconds(self) -> Optional[str]:
        """
        Return fractional seconds string (without decimal point).

        Returns:
            Fractional seconds digits or None if not present

        Example:
            >>> GeneralizedTimeType("20240115120000.5Z").fractional_seconds
            '5'
            >>> GeneralizedTimeType("20240115120000Z").fractional_seconds
            None
        """
        remainder = self.value[14:]
        if remainder.endswith("Z"):
            frac_part = remainder[:-1]
            if "." in frac_part:
                return frac_part.split(".")[1]
        elif remainder[0] in ("+", "-"):
            tz_start = remainder[0:5]
            frac_part = remainder[5:]
            if frac_part and frac_part.startswith("."):
                return frac_part[1:]
        return None

    @property
    def is_utc(self) -> bool:
        """Check if time is in UTC (ends with 'Z')."""
        return self.value.endswith("Z")

    @property
    def timezone_offset(self) -> Optional[str]:
        """
        Return timezone offset string (±HHMM) or None if UTC.

        Returns:
            Timezone offset like "+0300" or None for UTC

        Example:
            >>> GeneralizedTimeType("20240115120000+0300").timezone_offset
            '+0300'
            >>> GeneralizedTimeType("20240115120000Z").timezone_offset
            None
        """
        if self.is_utc:
            return None
        remainder = self.value[14:]
        if remainder[0] in ("+", "-"):
            # Check for fractional seconds before timezone
            if "." in remainder:
                frac_end = remainder.index(".")
                # Find timezone after fractional seconds
                tz_start = remainder[frac_end:]
                for i, c in enumerate(tz_start):
                    if c in ("+", "-") and i > 0:
                        return tz_start[i:i + 5]
            else:
                return remainder[0:5]
        return None

    def to_utc(self) -> "GeneralizedTime":
        """
        Convert to UTC representation (requires timezone offset).

        Note: This is a string manipulation only. For accurate
        timezone conversion, use Python's datetime module.

        Returns:
            New GeneralizedTimeType with 'Z' suffix

        Raises:
            ValueError: If no timezone offset present (already UTC)
        """
        if self.is_utc:
            return self

        # For proper timezone conversion, external library needed
        # This is a placeholder that just changes the suffix
        raise NotImplementedError(
            "Timezone conversion requires datetime library. "
            "Use .value property and convert externally."
        )

    def truncate_to(self, precision: str) -> "GeneralizedTime":
        """
        Truncate GeneralizedTime to specified precision.

        Args:
            precision: One of 'year', 'month', 'day', 'hour', 'minute', 'second'

        Returns:
            New GeneralizedTimeType truncated to precision

        Raises:
            ValueError: If precision is invalid

        Example:
            >>> time = GeneralizedTimeType("20240115120000Z")
            >>> time.truncate_to('minute')
            GeneralizedTimeType(value='202401151200Z')
        """
        valid_precisions = ("year", "month", "day", "hour", "minute", "second")
        if precision not in valid_precisions:
            raise ValueError(f"Invalid precision: {precision}, must be one of {valid_precisions}")

        # Determine cutoff position
        cutoffs = {
            "year": 4,
            "month": 6,
            "day": 8,
            "hour": 10,
            "minute": 12,
            "second": 14,
        }

        cutoff = cutoffs[precision]
        base = self.value[:cutoff]

        # Add timezone (preserve original)
        remainder = self.value[14:]
        if remainder.endswith("Z"):
            # Handle fractional seconds
            if "." in remainder:
                tz = "Z"
            else:
                tz = "Z"
        elif remainder[0] in ("+", "-"):
            tz = remainder[0:5]
        else:
            tz = "Z"  # Default to UTC if malformed

        return type(self)(base + tz)


# =============================================================================
# 10. object_identifier_type.py — OBJECT IDENTIFIER type
# =============================================================================


class ObjectIdentifierType(Simple[OBJECT_IDENTIFIER], BuiltinType):
    """
    ASN.1 OBJECT IDENTIFIER type (X.680 §31).

    An OBJECT IDENTIFIER is a globally unique identifier assigned to objects
    using a hierarchical tree structure. Each node in the tree is assigned
    by a registration authority.
    Example ASN.1:
        iso OBJECT IDENTIFIER ::= {1}
        standard OBJECT IDENTIFIER ::= {iso 0}
        asn1 OBJECT IDENTIFIER ::= {standard 1}

        -- Full OID: {iso standard asn1} = {1 0 1}

    Attributes:
        value: Tuple of non-negative integers representing OID arcs
               First arc: 0 (itu-t), 1 (iso), 2 (joint-iso-itu-t)
               Second arc: 0-39 (if first arc is 0 or 1), 0+ (if first arc is 2)
               Subsequent arcs: 0+ (unlimited)

    Note:
        - Minimum 2 arcs required (X.680 §31.10)
        - Encoding/decoding is handled in x690 module (BER)
        - This class only describes the abstract syntax structure

    References:
        - X.680 §31: Notation for the object identifier type
        - X.680 Table 1: UNIVERSAL tag 6
        - ITU-T X.660 | ISO/IEC 9834-1: OID registration procedures
    """
    value: OBJECT_IDENTIFIER

    @classmethod
    def new(cls, value: OBJECT_IDENTIFIER) -> ValueOrError[Self]:
        """
        Validate OBJECT IDENTIFIER structure per X.680 §31.10.
        Raises:
            ValueError: If OID has less than 2 arcs or invalid arc values
        """
        if len(value) < 2:
            return Error.from_e(ConstraintError(f"OBJECT IDENTIFIER must have at least 2 arcs, got {len(value)}"))
        # Validate first arc (0, 1, or 2)
        if value[0] not in (0, 1, 2):
            return Error.from_e(ConstraintError(f"First arc must be 0, 1, or 2, got {value[0]}"))
        # Validate second arc (0-39 if first arc is 0 or 1)
        if value[0] in (0, 1) and value[1] > 39:
            return Error.from_e(ConstraintError(f"Second arc must be 0-39 when first arc is {value[0]}, got {value[1]}"))
        # Validate all arcs are non-negative
        for i, arc in enumerate(value):
            if arc < 0:
                return Error.from_e(ConstraintError(f"Arc {i} must be non-negative, got {arc}"))
        return cls(value)

    def __iter__(self) -> Iterator[int]:
        return iter(self.value)

    def __getitem__(self, key: int) -> int:
        return self.value[key]

    @classmethod
    def default(cls) -> Self:
        return cls((0, 0))  # Default to {0 0}, though this may be invalid

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns:
            Dotted decimal notation

        Example:
            >>> str(ObjectIdentifierType((1, 0, 1)))
            '1.0.1'
        """
        return ".".join(str(arc) for arc in self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"

    def __eq__(self, other: object) -> bool:
        """
        Compare OBJECT IDENTIFIERs for equality.

        Two OIDs are equal if and only if all arcs are identical.
        """
        if not isinstance(other, ObjectIdentifierType):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __lt__(self, other: object) -> bool:
        """
        Compare OBJECT IDENTIFIERs lexicographically.

        Used for sorting OIDs in canonical order.
        """
        if not isinstance(other, ObjectIdentifierType):
            return NotImplemented
        return self.value < other.value

    @property
    def root_arc(self) -> int:
        """Return the root arc (first component)."""
        return self.value[0]

    @property
    def is_iso(self) -> bool:
        """Check if OID is under ISO root {1}."""
        return self.root_arc == 1

    @property
    def is_itu_t(self) -> bool:
        """Check if OID is under ITU-T root {0}."""
        return self.root_arc == 0

    @property
    def is_joint(self) -> bool:
        """Check if OID is under joint-iso-itu-t root {2}."""
        return self.root_arc == 2

    def startswith(self, prefix: "ObjectIdentifierType") -> bool:
        """
        Check if this OID starts with the given prefix.

        Example:
            >>> oid = ObjectIdentifierType((1, 0, 1, 5, 1))
            >>> prefix = ObjectIdentifierType((1, 0, 1))
            >>> oid.startswith(prefix)
            True
        """
        if not isinstance(prefix, ObjectIdentifierType):
            raise TypeError("Prefix must be ObjectIdentifierType")
        return self.value[:len(prefix.value)] == prefix.value

    def parent(self) -> ValueOrError[Self]:
        """
        Return parent OID (all arcs except last).

        Returns:
            Parent OID or Error if this is a root arc

        Example:
            >>> ObjectIdentifierType((1, 0, 1)).parent()
            ObjectIdentifierType(value=(1, 0))
        """
        if len(self.value) <= 2:
            return Error.from_e(ValueError("parent must be at least with 2 values"))
        return self.__class__(self.value[:-1])

    def child(self, arc: int) -> Self:
        """
        Return child OID with additional arc.

        Args:
            arc: Non-negative integer arc to append

        Returns:
            New ObjectIdentifierType with appended arc

        Example:
            >>> ObjectIdentifierType((1, 0)).child(1)
            ObjectIdentifierType(value=(1, 0, 1))
        """
        if arc < 0:
            raise ValueError(f"Arc must be non-negative, got {arc}")
        return self.__class__(self.value + (arc,))


# =============================================================================
# 11. choice_type.py — CHOICE type
# =============================================================================


@runtime_checkable
class ChoiceType[T: Type](BuiltinType, Protocol):
    """
    ASN.1 CHOICE type protocol (X.680 §28).

    Defines the abstract structure for CHOICE types — a discriminated union
    where exactly one alternative is present.  Encoding/decoding logic is
    provided by concrete implementations that subclass this protocol:

    * ``ber.ChoiceType`` — BER encoding (X.690 §8.13), used in ACSE layer
    * ``axdr.ChoiceType`` — A-XDR encoding (IEC 61334-6 §6.6), used in DLMS/COSEM

    **Typical usage**

    .. code-block:: python

        class MyChoice(axdr.ChoiceType):                # use A-XDR for COSEM
            value: FooType | BarType                     # union annotation → auto-generates alternatives

    ``alternatives`` (``dict[int, Type]``) is automatically derived from
    the ``value`` annotation by the concrete subclass constructor
    (see ``ber.ChoiceType`` / ``axdr.ChoiceType``).  Tag numbers are taken
    from the ``tag`` attribute of each type class in the union.  You may
    also override the mapping manually:

    .. code-block:: python

        class MyChoice(axdr.ChoiceType):
            alternatives = {1: FooType, 2: BarType}      # explicit tag → type mapping
            value: FooType | BarType

    **Attributes:**

    ``alternatives``
        ClassVar mapping tag numbers (``int``) directly to Python type
        classes (``Type``).  Each type class must provide a ``tag``
        attribute for automatic generation; manual overrides may use
        arbitrary tag numbers.

    ``value``
        Instance of the currently selected alternative.  The annotation
        should be a union of all possible alternative types so that
        type-checkers and the auto-generation of ``alternatives`` work
        correctly.

    **Methods** (no encoding — see ``ber.ChoiceType`` / ``axdr.ChoiceType``)

    ``validate(value)``
        Check that *value* is an instance of one of the alternatives.

    ``default()``
        Return an instance with the first alternative set to its default.

        Conversion from/to the ``CHOICE`` helper type (see ``x680.type``).
    """

    # Class variable: defines available alternatives for this CHOICE type
    alternatives: ClassVar[dict[int, type[Type]]]
    value: T

    def __init__(self, value: T) -> None:
        self.value = value

    @classmethod
    def new(cls, value: ValueOrError[T]) -> ValueOrError[Self]:
        if isinstance(value, Error):
            return value
        for t_ in cls.alternatives.values():
            if isinstance(value, t_):
                break
        else:
            return Error.from_e(TypeError(f"got {value=}, expected {", ".join((it.__name__ for it in cls.alternatives.values()))}"))  # TODO: make better
        return cls(value)

    @classmethod
    def default(cls) -> Self:
        return cls(cls.alternatives[next(iter(cls.alternatives))].default())  # type: ignore

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"value={self.value!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ChoiceType):
            return False
        return self.value == other.value

    def __str__(self) -> str:
        return f"{self.__class__.__name__}.{self.value}"


# =============================================================================
# 12. sequence_of_type.py — SEQUENCE OF type
# =============================================================================


class SequenceOfType[T: Type](BuiltinType):
    """ASN.1 SEQUENCE OF type."""
    _T: type[T]
    value: SEQUENCE_OF[T]

    def __init__(self, value: SEQUENCE_OF[T] = []) -> None:
        self.value = value

    @classmethod
    def new(cls, value: SEQUENCE_OF[T]) -> ValueOrError[Self]:
        return cls(value)

    def __class_getitem__(cls, item: type[T]) -> type["SequenceOfType[T]"]:
        """Supports SequenceOfType[int] at class level."""
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
        if len(other) != len(self):
            return False
        return all(v1 == v2 for v1, v2 in zip(self, other))


# =============================================================================
# 13. sequence_type.py — SEQUENCE type
# =============================================================================


def get_optional(type_: Any) -> Optional[type]:
    """Extract inner type from Optional[X] annotation."""
    origin = get_origin(type_)
    if origin in (Union, UnionType):
        args = get_args(type_)
        non_none_types = [arg for arg in args if arg is not type(None)]
        if len(non_none_types) == 1:
            return non_none_types[0]
    return None


class SequenceType(BuiltinType):
    """
    Base class for SEQUENCE types (X.680 §24)
    NATIVE REPRESENTATION: dataclass instance with fields corresponding to components

    ASN.1 semantics:
    - Ordered collection of named components (X.680 §3.6.60)
    - Components may be OPTIONAL or DEFAULT (X.680 §24.3)
    - Tag: UNIVERSAL 16 (X.680 §24.16)
    - XML notation: <SEQUENCE>...</SEQUENCE> (X.680 Table 4)

    A-XDR encoding note (IEC 61334-6 §6.9):
    - Components encoded in definition order
    - OPTIONAL/DEFAULT components omitted when absent/default
    - Explicit tags NOT encoded (redundant information)

    Usage pattern with @dataclass (simple case — all OPTIONAL/DEFAULT after mandatory):
        @dataclass
        class Credentials(SequenceType):
            userName: VisibleStringType
            password: VisibleStringType
            accountNumber: Optional[IntegerType] = None  # OPTIONAL component
            status: BooleanType = BooleanType(True)  # DEFAULT

    Usage pattern without @dataclass (when OPTIONAL/DEFAULT fields are mixed among mandatory):
        class MixedSequence(SequenceType):
            optionalField: Optional[IntegerType] = None   # OPTIONAL — before mandatory
            mandatoryField: VisibleStringType             # MANDATORY
            flag: BooleanType = BooleanType(False)        # DEFAULT — after mandatory

            def __init__(self, mandatoryField: VisibleStringType,
                         optionalField: Optional[IntegerType] = None,
                         flag: BooleanType = BooleanType(False)):
                self.mandatoryField = mandatoryField
                self.optionalField = optionalField
                self.flag = flag

    Component access:
        cred = Credentials(userName=..., password=...)
        cred.userName  # Direct attribute access
        cred.accountNumber  # None if absent (OPTIONAL)

    Note:
        - Encoding is concatenation of component encodings
        - Component order is fixed by ASN.1 definition
        - For DLMS/COSEM, component tags are omitted (unlike BER)
        - OPTIONAL/DEFAULT indicated by presence flag in A-XDR
        - Subclass components are created from __annotations__ (via __init_subclass__)
        - If all OPTIONAL/DEFAULT components are absent or appear only after mandatory
          fields, the class should be decorated with @dataclass
        - Otherwise, __init__ must reorder parameters: mandatory fields first,
          followed by Optional/Default fields in their original order
        - The order of __annotations__ matters, just like in ASN.1.
          The order of the components determines the encoding/decoding order.
        - When using @dataclass, do NOT use field() for DEFAULT components —
          it prevents proper DEFAULT detection.
    """
    components: ClassVar[tuple[NamedType[Type], ...]]

    @classmethod
    def new(cls, **kwargs: Any) -> ValueOrError[Self]:
        return cls(**kwargs)

    @classmethod
    def default(cls) -> Self:
        return cls(**{component.identifier: component.type_.default() for component in cls.components})

    def __str__(self) -> str:
        """
        ASN.1 value notation per X.680 §24.17:
        { identifier1 value1, identifier2 value2, ... }
        Omits components with value None (absent OPTIONAL components).
        DEFAULT values are ALWAYS included (cannot distinguish explicit vs default assignment in native representation).
        """
        return f"{self.__class__.__name__}[{len(self.components)}]"

    def __iter__(self) -> Iterator[Type]:
        for comp in self.components:
            yield getattr(self, comp.identifier)

    def __getitem__(self, key: int | str) -> Optional[Type]:
        if isinstance(key, int):
            key = self.components[key].identifier
        if hasattr(self, key):
            return cast("Type", getattr(self, key))
        raise KeyError(f"not find component with name: {key}")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SequenceType):
            return False
        return all(v1 == v2 for v1, v2 in zip(self, other))

    @classmethod
    def _init_sequence_components(cls) -> None:
        """
        Build <components> tuple from class annotations.
        Should be called from SequenceType.__init_subclass__ in encoding modules (ber/axdr).
        """
        elements: list[NamedType[Type] | OptionalNamedType | DefaultNamedType[Type]] = []
        if hasattr(cls, "components"):
            elements.extend(cls.components)
        for identifier, type_ in cls.__annotations__.items():
            if is_classvar(type_):
                continue
            for i, e in enumerate(elements):
                if e.identifier == identifier:
                    del elements[i]
                    break
            if (
                hasattr(cls, identifier)
                and (value := cls.__dict__[identifier]) is not None
            ):
                elements.append(DefaultNamedType(identifier, type_, value))
            elif in_type := get_optional(type_):
                elements.append(OptionalNamedType(identifier, in_type))
            else:
                elements.append(NamedType(identifier, type_))
        cls.components = tuple(elements)


# =============================================================================
# 14. constrained_type.py — Constrained type definitions
# =============================================================================


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
        if (
            isinstance(value, str)
            and len(value) != 1
        ):
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


class SizeConstraint(SubtypeElements):
    max_size: int
    min_size: int

    def __init__(self, max_size: int, min_size: Optional[int] = None) -> None:
        self.max_size = max_size
        self.min_size = max_size if min_size is None else min_size

    def contains(self, value: int) -> bool:
        if value < self.min_size:
            return False
        return not value > self.max_size

    def __str__(self) -> str:
        if self.min_size == self.max_size:
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


class ConstrainedType(Type):
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


class ConstrainedIntegerType(ConstrainedType, IntegerType):
    """Integer type bounded by a :class:`ValueRange` constraint.

    Automatically derives ``signed`` and ``fixed_length`` from the
    constraint at class‑creation time via :meth:`_init_subclass`.
    """
    fixed_length: ClassVar[Optional[int]] = None
    signed: ClassVar[bool] = True

    @classmethod
    def new(cls, value: INTEGER) -> ValueOrError[Self]:
        if (
            isinstance(v_r := cls.constraint_spec, ValueRange)
            and not v_r.contains(value)
        ):
            return Error.from_e(ConstraintError(f"{value=} outside range [{v_r.lower_endpoint}..{v_r.upper_endpoint}]"))
        return cls(value)

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
            and cls.constraint_spec.min_size == cls.constraint_spec.max_size
        ):
            cls.fixed_length = cls.constraint_spec.max_size

    @classmethod
    def new(cls, value: BIT_STRING) -> ValueOrError[Self]:
        if (
            isinstance(cls.constraint_spec, SizeConstraint)
            and not cls.constraint_spec.contains(len(value))
        ):
            return Error.from_e(ConstraintError(f"got {len(value)}, expected {cls.constraint_spec}"))
        return cls(value)


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
            and cls.constraint_spec.min_size == cls.constraint_spec.max_size
        ):
            cls.fixed_length = cls.constraint_spec.max_size

    @classmethod
    def new(cls, value: SEQUENCE_OF[T]) -> ValueOrError[Self]:
        """Validate the number of elements against ``fixed_length``."""
        if (
            isinstance(length := cls.fixed_length, int)
            and length != len(value)
        ):
            return Error.from_e(ConstraintError(f"got {len(value)}, expected {cls.constraint_spec}"))
        return cls(value)


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
            hasattr(cls, "constraint_spec")
            and isinstance(cls.constraint_spec, SizeConstraint)
            and cls.constraint_spec.min_size == cls.constraint_spec.max_size
        ):
            cls.fixed_length = cls.constraint_spec.max_size

    @classmethod
    def new(cls, value: OCTET_STRING) -> ValueOrError[Self]:
        if (
            isinstance(length := cls.fixed_length, int)
            and length != len(value)
        ):
            return Error.from_e(ConstraintError(f"{cls.__name__} got size={len(value)}, expected {cls.constraint_spec}"))
        return cls(value)

    @classmethod
    def default(cls) -> Self:
        """Return a default value — all‑zeroes for fixed‑length strings."""
        if cls.fixed_length is not None:
            return cls(b"\x00" * cls.fixed_length)
        return super().default()


# =============================================================================
# __all__ — public API
# =============================================================================

__all__ = [
    # type.py
    "INTEGER",
    "REAL",
    "STRING",
    "BIT_STRING",
    "BOOLEAN",
    "NULL",
    "OCTET_STRING",
    "OBJECT_IDENTIFIER",
    "SIMPLE",
    "SEQUENCE_OF",
]
