from dataclasses import dataclass
from enum import IntEnum, auto
from typing import ClassVar, Self, Any
from .tag import Tag
from .type import Type, BuiltinType, TYPE_VALUE, SEQUENCE_OF, Constraint


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


@dataclass
class TaggedType(BuiltinType):
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
    type_: ClassVar[type[Type]]
    value: Type

    def check_constraint(self, constraint: Constraint[Any]) -> None:
        value = self.value
        if isinstance(value.constraint, Constraint):
            value.check_constraint(value.constraint)

    @classmethod
    def from_tv(cls, value: Type | TYPE_VALUE) -> Self:
        "constuctor from type value"
        return cls(cls.type_(value))
