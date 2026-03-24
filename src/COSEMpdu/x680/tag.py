from dataclasses import dataclass
from enum import IntEnum


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
