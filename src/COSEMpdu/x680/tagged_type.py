from enum import IntEnum, auto
from typing import ClassVar, Self, overload
from .type import Simple, Type, BuiltinType, TYPE_VALUE, OCTET_STRING
from .octet_string_type import OctetStringType


class TaggingMode(IntEnum):
    """
    Tagging mode per ITU-T X.680 §30.6 and IEC 61334-6 §6.7

    IMPLICIT: Tag replaces base type's tag (A-XDR: keyword ignored)
    EXPLICIT: Tag wraps base type's encoding (constructed)
    DEFAULT: Depends on module's TagDefault (treated as EXPLICIT)
    """
    IMPLICIT = auto()
    EXPLICIT = auto()
    DEFAULT = auto()


class TaggedType[T: Type](BuiltinType):
    """
    ASN.1 TaggedType per ITU-T X.680 §30 and IEC 61334-6 §6.7

    TaggedType ::=
        Tag Type |
        Tag IMPLICIT Type |
        Tag EXPLICIT Type

    A-XDR specific rules (§6.7):
    - IMPLICIT keyword is ignored (treated as EXPLICIT for tagging)
    - CHOICE alternatives: encode raw tag number (1 byte)
    - ASN.1 explicit tags ([APPLICATION x]): encode in BER format
    - SEQUENCE components: NEVER encode tags

    BER encoding rules (X.690 §8.14):
    - IMPLICIT: contents = base encoding's contents (primitive/constructed preserved)
    - EXPLICIT: constructed, contents = complete base encoding (TLV)
    """
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    _T: type[T]
    value: T

    def __init__(self, value: T) -> None:
        self.value = value

    def __class_getitem__(cls, item: type[T]) -> type["TaggedType[T]"]:
        name = f"{cls.__name__}[{item.__name__}]"
        return type(name, (cls,), {
            "_T": item,
        })

    def normalize(self) -> TYPE_VALUE:
        return self.value.normalize()

    @classmethod
    def default(cls) -> Self:
        return cls(cls._T.default())

    @classmethod
    def parse(cls, value: TYPE_VALUE) -> Self:
        """constuctor from type value"""
        return cls(cls._T.parse(value))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TaggedType):
            return False
        return self.normalize() == other.normalize()
