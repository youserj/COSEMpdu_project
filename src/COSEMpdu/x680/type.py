from dataclasses import dataclass
from typing import Self, TypeAlias, Protocol, Optional, Any, runtime_checkable
from StructResult.result import ValueOrError
from ..byte_buffer import ByteBuffer

# Transcript represents minimal data needed for string parsing/reconstruction.
# Contains ONLY values (str or list of str), NO field names or structural metadata.
# Structural context (field names, types) is maintained by the concrete Type implementation.
Transcript: TypeAlias = str | list["Transcript"]


class EDTLV(Protocol):
    @classmethod
    def get(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        """
        Decode with full TLV (Tag + Length + Contents).
        MUST validate tag before decoding.
        """
        ...

    def put(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode with full TLV (Tag + Length + Contents).
        Returns number of bytes written.
        """
        ...


type INTEGER = int
type REAL = float
type STRING = str
type BIT_STRING = tuple[int, ...]
type BOOLEAN = bool
type NULL = None
type OCTET_STRING = bytes
type OBJECT_IDENTIFIER = tuple[int, ...]
type SIMPLE = INTEGER | STRING | BIT_STRING | BOOLEAN | OCTET_STRING | OBJECT_IDENTIFIER | NULL
type COMPLEX = "SEQUENCE" | "SEQUENCE_OF[Any]"
type TYPE_VALUE = SIMPLE | COMPLEX


@runtime_checkable
class Type(Protocol):
    """
    Encoding Data Value component per X.690 §8.1.2

    Provides two levels of encoding interface:
    1. Full TLV: get()/put() - Tag + Length + Contents
    2. Contents only: get_lc()/put_lc() - Length + Contents only

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
    value: Any

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        """
        Decode with Length + Contents ONLY (no Tag validation).

        Used for:
        - CHOICE alternatives (X.690 §8.13)
        - SEQUENCE components in A-XDR (IEC 61334-6 §6.9)
        - Explicitly tagged types where outer tag already validated
        """
        ...

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode with Length + Contents ONLY (no Tag).

        Used for:
        - CHOICE alternatives (X.690 §8.13)
        - SEQUENCE components in A-XDR (IEC 61334-6 §6.9)
        """
        ...

    @classmethod
    def default(cls) -> Self:
        """Return default value instance for this type, if defined."""
        ...

#     def normalize(self) -> TYPE_VALUE: ...


# class Simple[T: SIMPLE](Type, Protocol):
#     value: T

#     def normalize(self) -> T:
#         return self.value


type SEQUENCE = tuple[Optional[Type], ...]
type SEQUENCE_OF[U: Type] = list[U]


class BuiltinType(Type, Protocol):
    """Built-in ASN.1 types per X.680 §16.2 (BOOLEAN, INTEGER, etc.)"""


@dataclass
class ReferencedType(Type, Protocol):
    """Referenced types per X.680 §16.3"""


@dataclass
class UsefulType(ReferencedType, Protocol):
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
class RestrictedCharacterStringType(CharacterStringType, Protocol):
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


__all__ = [
    "INTEGER",
    "REAL",
    "STRING",
    "BIT_STRING",
    "BOOLEAN",
    "NULL",
    "OCTET_STRING",
    "SIMPLE",
    "COMPLEX",
    "TYPE_VALUE",
    "SEQUENCE"
]
