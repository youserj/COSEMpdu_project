from dataclasses import dataclass
from typing import Self, Literal
from struct import pack, unpack
from .byte_buffer import ByteBuffer
from .x680.type import (
    Constraint, SizeConstraint, NamedType,
    BIT_STRING, BOOLEAN, OCTET_STRING, INTEGER, STRING
    )
from .x680.tagged_type import TaggingMode
from . import axdr
from .cosem_pdu import (
    Integer8, Integer16, Integer32, Integer64,
    Unsigned8, Unsigned16, Unsigned32, Unsigned64
)


# =============================================================================
# TypeDescription CHOICE
# =============================================================================
# TypeDescription ::= CHOICE { ... }
# Most alternatives are NULL (type indicator only)
# Some have structure (array, structure)
# =============================================================================

@dataclass
class TypeDescriptionNullData(axdr.TaggedType):
    """[0] IMPLICIT NULL"""
    tag = 0
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionArrayContent(axdr.SequenceType):
    """array content: SEQUENCE { number-of-elements Unsigned16, type-description TypeDescription }"""
    components = (
        NamedType("number-of-elements", Unsigned16),
        NamedType("type-description", "TypeDescription"),  # Forward reference
    )


@dataclass
class TypeDescriptionArray(axdr.TaggedType):
    """[1] IMPLICIT SEQUENCE { number-of-elements Unsigned16, type-description TypeDescription }"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    type_ = TypeDescriptionArrayContent


@dataclass
class TypeDescriptionStructure(axdr.TaggedType):
    """[2] IMPLICIT SEQUENCE OF TypeDescription"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    type_ = "TypeDescriptionSequenceOf"  # Forward reference


@dataclass
class TypeDescriptionBoolean(axdr.TaggedType):
    """[3] IMPLICIT NULL"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionBitString(axdr.TaggedType):
    """[4] IMPLICIT NULL"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionDoubleLong(axdr.TaggedType):
    """[5] IMPLICIT NULL"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionDoubleLongUnsigned(axdr.TaggedType):
    """[6] IMPLICIT NULL"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionOctetString(axdr.TaggedType):
    """[9] IMPLICIT NULL"""
    tag = 9
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionVisibleString(axdr.TaggedType):
    """[10] IMPLICIT NULL"""
    tag = 10
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionUtf8String(axdr.TaggedType):
    """[12] IMPLICIT NULL"""
    tag = 12
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionBcd(axdr.TaggedType):
    """[13] IMPLICIT NULL"""
    tag = 13
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionInteger(axdr.TaggedType):
    """[15] IMPLICIT NULL"""
    tag = 15
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionLong(axdr.TaggedType):
    """[16] IMPLICIT NULL"""
    tag = 16
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionUnsigned(axdr.TaggedType):
    """[17] IMPLICIT NULL"""
    tag = 17
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionLongUnsigned(axdr.TaggedType):
    """[18] IMPLICIT NULL"""
    tag = 18
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionLong64(axdr.TaggedType):
    """[20] IMPLICIT NULL"""
    tag = 20
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionLong64Unsigned(axdr.TaggedType):
    """[21] IMPLICIT NULL"""
    tag = 21
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionEnum(axdr.TaggedType):
    """[22] IMPLICIT NULL"""
    tag = 22
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionFloat32(axdr.TaggedType):
    """[23] IMPLICIT NULL"""
    tag = 23
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionFloat64(axdr.TaggedType):
    """[24] IMPLICIT NULL"""
    tag = 24
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionDateTime(axdr.TaggedType):
    """[25] IMPLICIT NULL"""
    tag = 25
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionDate(axdr.TaggedType):
    """[26] IMPLICIT NULL"""
    tag = 26
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionTime(axdr.TaggedType):
    """[27] IMPLICIT NULL"""
    tag = 27
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescriptionDontCare(axdr.TaggedType):
    """[255] IMPLICIT NULL"""
    tag = 255
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class TypeDescription(axdr.ChoiceType):
    """TypeDescription"""
    alternatives = axdr.create_alternatives((
        NamedType("null-data", TypeDescriptionNullData),
        NamedType("array", TypeDescriptionArray),
        NamedType("structure", TypeDescriptionStructure),
        NamedType("boolean", TypeDescriptionBoolean),
        NamedType("bit-string", TypeDescriptionBitString),
        NamedType("double-long", TypeDescriptionDoubleLong),
        NamedType("double-long-unsigned", TypeDescriptionDoubleLongUnsigned),
        NamedType("octet-string", TypeDescriptionOctetString),
        NamedType("visible-string", TypeDescriptionVisibleString),
        NamedType("utf8-string", TypeDescriptionUtf8String),
        NamedType("bcd", TypeDescriptionBcd),
        NamedType("integer", TypeDescriptionInteger),
        NamedType("long", TypeDescriptionLong),
        NamedType("unsigned", TypeDescriptionUnsigned),
        NamedType("long-unsigned", TypeDescriptionLongUnsigned),
        NamedType("long64", TypeDescriptionLong64),
        NamedType("long64-unsigned", TypeDescriptionLong64Unsigned),
        NamedType("enum", TypeDescriptionEnum),
        NamedType("float32", TypeDescriptionFloat32),
        NamedType("float64", TypeDescriptionFloat64),
        NamedType("date-time", TypeDescriptionDateTime),
        NamedType("date", TypeDescriptionDate),
        NamedType("time", TypeDescriptionTime),
        NamedType("dont-care", TypeDescriptionDontCare),
    ))

    # Convenience constructors
    @classmethod
    def null_data(cls) -> Self:
        return cls(TypeDescriptionNullData(axdr.NullType(None)))

    @classmethod
    def array(cls, number_of_elements: Unsigned16, type_description: "TypeDescription") -> Self:
        return cls(TypeDescriptionArray(TypeDescriptionArrayContent((number_of_elements, type_description))))

    @classmethod
    def structure(cls, elements: list["TypeDescription"]) -> Self:
        return cls(TypeDescriptionStructure(TypeDescriptionSequenceOf(elements)))

    @classmethod
    def boolean(cls) -> Self:
        return cls(TypeDescriptionBoolean(axdr.NullType(None)))

    @classmethod
    def octet_string(cls) -> Self:
        return cls(TypeDescriptionOctetString(axdr.NullType(None)))

    @classmethod
    def visible_string(cls) -> Self:
        return cls(TypeDescriptionVisibleString(axdr.NullType(None)))

    @classmethod
    def integer(cls) -> Self:
        return cls(TypeDescriptionInteger(axdr.NullType(None)))

    @classmethod
    def unsigned(cls) -> Self:
        return cls(TypeDescriptionUnsigned(axdr.NullType(None)))

    @classmethod
    def long(cls) -> Self:
        return cls(TypeDescriptionLong(axdr.NullType(None)))

    @classmethod
    def long_unsigned(cls) -> Self:
        return cls(TypeDescriptionLongUnsigned(axdr.NullType(None)))

    @classmethod
    def dont_care(cls) -> Self:
        return cls(TypeDescriptionDontCare(axdr.NullType(None)))


setattr(TypeDescriptionArrayContent, "components",
    (
        NamedType("number-of-elements", Unsigned16),
        NamedType("type-description", TypeDescription)
    )
)


@dataclass
class TypeDescriptionSequenceOf(axdr.SequenceOfType[TypeDescription]):
    component_type = TypeDescription


setattr(TypeDescriptionStructure, "type_", TypeDescriptionSequenceOf)

# =============================================================================
# Data CHOICE
# =============================================================================
# Data ::= CHOICE { ... }
# Contains actual data values (not just type indicators)
# Some types are recursive (array, structure contain Data)
# =============================================================================


@dataclass
class NullData(axdr.TaggedType):
    """[0] IMPLICIT NULL"""
    tag = 0
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


# @dataclass
# class SequenceOfData(axdr.SequenceOfType["Data"]):
#     component_type = "Data"


@dataclass
class Array(axdr.TaggedType):
    """[1] IMPLICIT SEQUENCE OF Data"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    type_ = "SequenceOfData"
    value: "SequenceOfData"


@dataclass
class Structure(axdr.TaggedType):
    """[2] IMPLICIT SEQUENCE OF Data"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    type_ = "SequenceOfData"
    value: "SequenceOfData"


@dataclass
class Boolean(axdr.TaggedType):
    """[3] IMPLICIT BOOLEAN"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    type_ = axdr.BooleanType


@dataclass
class BitString(axdr.TaggedType):
    """[4] IMPLICIT BIT STRING"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    type_ = axdr.BitStringType


@dataclass
class DoubleLong(axdr.TaggedType):
    """[5] IMPLICIT Integer32"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    type_ = Integer32


@dataclass
class DoubleLongUnsigned(axdr.TaggedType):
    """[6] IMPLICIT Unsigned32"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    type_ = Unsigned32


@dataclass
class OctetString(axdr.TaggedType):
    """[9] IMPLICIT OCTET STRING"""
    tag = 9
    mode = TaggingMode.IMPLICIT
    type_ = axdr.OctetStringType


@dataclass
class VisibleString(axdr.TaggedType):
    """[10] IMPLICIT VisibleString"""
    tag = 10
    mode = TaggingMode.IMPLICIT
    type_ = axdr.VisibleString
    value: axdr.VisibleString


@dataclass
class Utf8String(axdr.TaggedType):
    """[12] IMPLICIT UTF8String"""
    tag = 12
    mode = TaggingMode.IMPLICIT
    type_ = axdr.Utf8String


@dataclass
class Bcd(axdr.TaggedType):
    """[13] IMPLICIT Integer8"""
    tag = 13
    mode = TaggingMode.IMPLICIT
    type_ = Integer8


@dataclass
class Integer(axdr.TaggedType):
    """[15] IMPLICIT Integer8"""
    tag = 15
    mode = TaggingMode.IMPLICIT
    type_ = Integer8


@dataclass
class Long(axdr.TaggedType):
    """[16] IMPLICIT Integer16"""
    tag = 16
    mode = TaggingMode.IMPLICIT
    type_ = Integer16


@dataclass
class Unsigned(axdr.TaggedType):
    """[17] IMPLICIT Unsigned8"""
    tag = 17
    mode = TaggingMode.IMPLICIT
    type_ = Unsigned8


@dataclass
class LongUnsigned(axdr.TaggedType):
    """[18] IMPLICIT Unsigned16"""
    tag = 18
    mode = TaggingMode.IMPLICIT
    type_ = Unsigned16


@dataclass
class ContentsDescription(axdr.TaggedType):
    """[0] TypeDescription"""
    tag = 0
    mode = TaggingMode.DEFAULT
    type_ = TypeDescription


@dataclass
class ArrayContents(axdr.TaggedType):
    """[1] IMPLICIT   OCTET STRING"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    type_ = axdr.OctetStringType


@dataclass
class CompactArrayContent(axdr.SequenceType):
    """compact-array content: SEQUENCE { contents-description TypeDescription, array-contents OCTET STRING }"""
    components = (
        NamedType("contents-description", ContentsDescription),
        NamedType("array-contents", ArrayContents),
    )

    def get_array(self) -> list["Data"]:
        if (type_ := Data.alternatives.get(self.value[0].value.value.tag)) is None:
            raise ValueError(f"Unknown TypeDescription tag: {self.value[0]}")
        data_class = type_.type_
        contents_bytes = bytes(self.value[1].value)
        if not contents_bytes:
            return []
        result: list["Data"] = []
        buf = ByteBuffer.wrap(contents_bytes)
        while buf.remaining() > 0:
            data = data_class.get_contents(buf)
            result.append(data)
        return result

    @classmethod
    def from_array[T: "Data"](cls, contents: ContentsDescription, array: list[T], buf_size: int = 65535) -> Self:
        buf = ByteBuffer.allocate(buf_size)
        for el in array:
            el.put_contents(buf)
        array_contents = ArrayContents(axdr.OctetStringType(bytes(buf.extract())))
        return cls((contents, array_contents))


@dataclass
class CompactArray(axdr.TaggedType):
    """[19] IMPLICIT SEQUENCE { contents-description TypeDescription, array-contents OCTET STRING }"""
    tag = 19
    mode = TaggingMode.IMPLICIT
    type_ = CompactArrayContent


@dataclass
class Long64(axdr.TaggedType):
    """[20] IMPLICIT Integer64"""
    tag = 20
    mode = TaggingMode.IMPLICIT
    type_ = Integer64


@dataclass
class Long64Unsigned(axdr.TaggedType):
    """[21] IMPLICIT Unsigned64"""
    tag = 21
    mode = TaggingMode.IMPLICIT
    type_ = Unsigned64


@dataclass
class Enum(axdr.TaggedType):
    """[22] IMPLICIT Unsigned8"""
    tag = 22
    mode = TaggingMode.IMPLICIT
    type_ = Unsigned8


class OctetStringTypeSize4(axdr.OctetStringType):
    constraint = Constraint(SizeConstraint(4))


class OctetStringTypeSize8(axdr.OctetStringType):
    constraint = Constraint(SizeConstraint(8))


class OctetStringTypeSize12(axdr.OctetStringType):
    constraint = Constraint(SizeConstraint(12))


class OctetStringTypeSize5(axdr.OctetStringType):
    constraint = Constraint(SizeConstraint(5))


def float2OctetString[T: (OctetStringTypeSize4, OctetStringTypeSize8)](type_: type[T], fmt: str, value: float) -> T:
    """ Input float: <sign><integer>.<fraction>[e[-+]power] example: 1.0, -0.003, 1e+12, 4.5e-7 """
    if "inf" in str(value):
        raise OverflowError("float overflow error")
    return type_(pack(fmt, value))


def octetString2Float(data: OCTET_STRING, fmt: Literal[">f", ">d"]) -> float:
    """return the build in float type IEEE 60559"""
    return unpack(fmt, data)[0]


@dataclass
class Float32(axdr.TaggedType):
    """[23] IMPLICIT OCTET STRING (SIZE(4))"""
    tag = 23
    mode = TaggingMode.IMPLICIT
    type_ = OctetStringTypeSize4

    @classmethod
    def from_float(cls, value: float) -> Self:
        return cls(float2OctetString(cls.type_, ">f", value))

    def __float__(self) -> float:
        return octetString2Float(self.value.value, ">f")


@dataclass
class Float64(axdr.TaggedType):
    """[24] IMPLICIT OCTET STRING (SIZE(8))"""
    tag = 24
    mode = TaggingMode.IMPLICIT
    type_ = OctetStringTypeSize8

    @classmethod
    def from_float(cls, value: float) -> Self:
        return cls(float2OctetString(cls.type_, ">d", value))

    def __float__(self) -> float:
        return octetString2Float(self.value.value, ">d")


@dataclass
class DateTime(axdr.TaggedType):
    """[25] IMPLICIT OCTET STRING (SIZE(12))"""
    tag = 25
    mode = TaggingMode.IMPLICIT
    type_ = OctetStringTypeSize12


@dataclass
class Date(axdr.TaggedType):
    """[26] IMPLICIT OCTET STRING (SIZE(5))"""
    tag = 26
    mode = TaggingMode.IMPLICIT
    type_ = OctetStringTypeSize5


@dataclass
class Time(axdr.TaggedType):
    """[27] IMPLICIT OCTET STRING (SIZE(4))"""
    tag = 27
    mode = TaggingMode.IMPLICIT
    type_ = OctetStringTypeSize4


@dataclass
class DontCare(axdr.TaggedType):
    """[255] IMPLICIT NULL"""
    tag = 255
    mode = TaggingMode.IMPLICIT
    type_ = axdr.NullType


@dataclass
class Data(axdr.ChoiceType):
    """Data"""
    alternatives = axdr.create_alternatives((
        NamedType("null-data", NullData),
        NamedType("array", Array),
        NamedType("structure", Structure),
        NamedType("boolean", Boolean),
        NamedType("bit-string", BitString),
        NamedType("double-long", DoubleLong),
        NamedType("double-long-unsigned", DoubleLongUnsigned),
        NamedType("octet-string", OctetString),
        NamedType("visible-string", VisibleString),
        NamedType("utf8-string", Utf8String),
        NamedType("bcd", Bcd),
        NamedType("integer", Integer),
        NamedType("long", Long),
        NamedType("unsigned", Unsigned),
        NamedType("long-unsigned", LongUnsigned),
        NamedType("compact-array", CompactArray),
        NamedType("long64", Long64),
        NamedType("long64-unsigned", Long64Unsigned),
        NamedType("enum", Enum),
        NamedType("float32", Float32),
        NamedType("float64", Float64),
        NamedType("date-time", DateTime),
        NamedType("date", Date),
        NamedType("time", Time),
        NamedType("dont-care", DontCare),
    ))

    # =========================================================================
    # Convenience constructors for common data types
    # =========================================================================

    @classmethod
    def null_data(cls) -> Self:
        """Create null-data [0]"""
        return cls(NullData(axdr.NullType(None)))

    @classmethod
    def array(cls, elements: list["Data"]) -> Self:
        """Create array [1] SEQUENCE OF Data"""
        return cls(Array(SequenceOfData(elements)))

    @classmethod
    def structure(cls, elements: list["Data"]) -> Self:
        """Create structure [2] SEQUENCE OF Data"""
        return cls(Structure(SequenceOfData(elements)))

    @classmethod
    def boolean(cls, value: BOOLEAN) -> Self:
        """Create boolean [3]"""
        return cls(Boolean(axdr.BooleanType(value)))

    @classmethod
    def bit_string(cls, value: BIT_STRING) -> Self:
        """Create bit-string [4]"""
        return cls(BitString(axdr.BitStringType(value)))

    @classmethod
    def double_long(cls, value: INTEGER) -> Self:
        """Create double-long [5] Integer32"""
        return cls(DoubleLong(Integer32(value)))

    @classmethod
    def double_long_unsigned(cls, value: INTEGER) -> Self:
        """Create double-long-unsigned [6] Unsigned32"""
        return cls(DoubleLongUnsigned(Unsigned32(value)))

    @classmethod
    def octet_string(cls, value: OCTET_STRING) -> Self:
        """Create octet-string [9]"""
        return cls(OctetString(axdr.OctetStringType(value)))

    @classmethod
    def visible_string(cls, value: STRING) -> Self:
        """Create visible-string [10]"""
        return cls(VisibleString(axdr.VisibleString(value)))

    @classmethod
    def utf8_string(cls, value: STRING) -> Self:
        """Create utf8-string [12]"""
        return cls(Utf8String(axdr.Utf8String(value)))

    @classmethod
    def bcd(cls, value: INTEGER) -> Self:
        """Create bcd [13] Integer8"""
        return cls(Bcd(Integer8(value)))

    @classmethod
    def integer(cls, value: INTEGER) -> Self:
        """Create integer [15] Integer8"""
        return cls(Integer(Integer8(value)))

    @classmethod
    def long(cls, value: INTEGER) -> Self:
        """Create long [16] Integer16"""
        return cls(Long(Integer16(value)))

    @classmethod
    def unsigned(cls, value: INTEGER) -> Self:
        """Create unsigned [17] Unsigned8"""
        return cls(Unsigned(Unsigned8(value)))

    @classmethod
    def long_unsigned(cls, value: INTEGER) -> Self:
        """Create long-unsigned [18] Unsigned16"""
        return cls(LongUnsigned(Unsigned16(value)))

    @classmethod
    def compact_array(cls, contents_description: ContentsDescription, array_contents: ArrayContents) -> Self:
        """Create compact-array [19]"""
        return cls(CompactArray(CompactArrayContent((contents_description, array_contents))))

    @classmethod
    def long64(cls, value: INTEGER) -> Self:
        """Create long64 [20] Integer64"""
        return cls(Long64(Integer64(value)))

    @classmethod
    def long64_unsigned(cls, value: INTEGER) -> Self:
        """Create long64-unsigned [21] Unsigned64"""
        return cls(Long64Unsigned(Unsigned64(value)))

    @classmethod
    def enum(cls, value: INTEGER) -> Self:
        """Create enum [22] Unsigned8"""
        return cls(Enum(Unsigned8(value)))

    @classmethod
    def float32(cls, value: OCTET_STRING) -> Self:
        """Create float32 [23] OCTET STRING (SIZE(4))"""
        return cls(Float32(OctetStringTypeSize4(value)))

    @classmethod
    def float64(cls, value: OCTET_STRING) -> Self:
        """Create float64 [24] OCTET STRING (SIZE(8))"""
        return cls(Float64(OctetStringTypeSize8(value)))

    @classmethod
    def date_time(cls, value: OCTET_STRING) -> Self:
        """Create date-time [25] OCTET STRING (SIZE(12))"""
        return cls(DateTime(OctetStringTypeSize12(value)))

    @classmethod
    def date(cls, value: OCTET_STRING) -> Self:
        """Create date [26] OCTET STRING (SIZE(5))"""
        return cls(Date(OctetStringTypeSize5(value)))

    @classmethod
    def time(cls, value: bytes) -> Self:
        """Create time [27] OCTET STRING (SIZE(4))"""
        if len(value) != 4:
            raise ValueError("time must be 4 bytes")
        return cls(Time(OctetStringTypeSize4(value)))

    @classmethod
    def dont_care(cls) -> Self:
        """Create dont-care [255] NULL"""
        return cls(DontCare(axdr.NullType(None)))

    # =========================================================================
    # Helper methods
    # =========================================================================

    def __repr__(self) -> str:
        """Human-readable representation"""
        return f"Data.{self.value!r}"


@dataclass
class SequenceOfData(axdr.SequenceOfType[Data]):
    component_type = Data


setattr(Array, "type_", SequenceOfData)
setattr(Structure, "type_", SequenceOfData)
