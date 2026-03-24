from dataclasses import dataclass
from typing import Self, Literal
from struct import pack, unpack
from .byte_buffer import ByteBuffer
from .x680.constrained_type import SizeConstraint
from .x680.type import (
    NamedType,
    BIT_STRING, BOOLEAN, OCTET_STRING, INTEGER, STRING
    )
from .x680.tagged_type import TaggingMode
from . import axdr
from .useful_types import (
    Integer8, Integer16, Integer32, Integer64,
    Unsigned8, Unsigned16, Unsigned32, Unsigned64
)
from .axdr import ConstrainedOctetStringType, IntegerType, OctetStringType, NullType, BooleanType, BitStringType, SequenceOfType, ChoiceType, TaggedType, NullType0

# =============================================================================
# TypeDescription CHOICE
# =============================================================================
# TypeDescription ::= CHOICE { ... }
# Most alternatives are NULL (type indicator only)
# Some have structure (array, structure)
# =============================================================================

@dataclass
class TypeDescriptionNullData(TaggedType[NullType]):
    """[0] IMPLICIT NULL"""
    tag = 0
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionArrayContent(axdr.SequenceType):
    """array content: SEQUENCE { number-of-elements Unsigned16, type-description TypeDescription }"""


@dataclass
class TypeDescriptionArray(TaggedType[TypeDescriptionArrayContent]):
    """[1] IMPLICIT SEQUENCE { number-of-elements Unsigned16, type-description TypeDescription }"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: TypeDescriptionArrayContent


@dataclass
class TypeDescriptionStructure(TaggedType["TypeDescriptionSequenceOf"]):
    """[2] IMPLICIT SEQUENCE OF TypeDescription"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: "TypeDescriptionSequenceOf"  # Forward reference


@dataclass
class TypeDescriptionBoolean(TaggedType[NullType]):
    """[3] IMPLICIT NULL"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionBitString(TaggedType[NullType]):
    """[4] IMPLICIT NULL"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionDoubleLong(TaggedType[NullType]):
    """[5] IMPLICIT NULL"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionDoubleLongUnsigned(TaggedType[NullType]):
    """[6] IMPLICIT NULL"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionOctetString(TaggedType[NullType]):
    """[9] IMPLICIT NULL"""
    tag = 9
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionVisibleString(TaggedType[NullType]):
    """[10] IMPLICIT NULL"""
    tag = 10
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionUtf8String(TaggedType[NullType]):
    """[12] IMPLICIT NULL"""
    tag = 12
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionBcd(TaggedType[NullType]):
    """[13] IMPLICIT NULL"""
    tag = 13
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionInteger(TaggedType[NullType]):
    """[15] IMPLICIT NULL"""
    tag = 15
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionLong(TaggedType[NullType]):
    """[16] IMPLICIT NULL"""
    tag = 16
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionUnsigned(TaggedType[NullType]):
    """[17] IMPLICIT NULL"""
    tag = 17
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionLongUnsigned(TaggedType[NullType]):
    """[18] IMPLICIT NULL"""
    tag = 18
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionLong64(TaggedType[NullType]):
    """[20] IMPLICIT NULL"""
    tag = 20
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionLong64Unsigned(TaggedType[NullType]):
    """[21] IMPLICIT NULL"""
    tag = 21
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionEnum(TaggedType[NullType]):
    """[22] IMPLICIT NULL"""
    tag = 22
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionFloat32(TaggedType[NullType]):
    """[23] IMPLICIT NULL"""
    tag = 23
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionFloat64(TaggedType[NullType]):
    """[24] IMPLICIT NULL"""
    tag = 24
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionDateTime(TaggedType[NullType]):
    """[25] IMPLICIT NULL"""
    tag = 25
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionDate(TaggedType[NullType]):
    """[26] IMPLICIT NULL"""
    tag = 26
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionTime(TaggedType[NullType]):
    """[27] IMPLICIT NULL"""
    tag = 27
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescriptionDontCare(TaggedType[NullType]):
    """[255] IMPLICIT NULL"""
    tag = 255
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class TypeDescription(axdr.ChoiceType):
    """TypeDescription"""
    alternatives = {
        0: NamedType("null-data", TypeDescriptionNullData),
        1: NamedType("array", TypeDescriptionArray),
        2: NamedType("structure", TypeDescriptionStructure),
        3: NamedType("boolean", TypeDescriptionBoolean),
        4: NamedType("bit-string", TypeDescriptionBitString),
        5: NamedType("double-long", TypeDescriptionDoubleLong),
        6: NamedType("double-long-unsigned", TypeDescriptionDoubleLongUnsigned),
        9: NamedType("octet-string", TypeDescriptionOctetString),
        10: NamedType("visible-string", TypeDescriptionVisibleString),
        12: NamedType("utf8-string", TypeDescriptionUtf8String),
        13: NamedType("bcd", TypeDescriptionBcd),
        15: NamedType("integer", TypeDescriptionInteger),
        16: NamedType("long", TypeDescriptionLong),
        17: NamedType("unsigned", TypeDescriptionUnsigned),
        18: NamedType("long-unsigned", TypeDescriptionLongUnsigned),
        20: NamedType("long64", TypeDescriptionLong64),
        21: NamedType("long64-unsigned", TypeDescriptionLong64Unsigned),
        22: NamedType("enum", TypeDescriptionEnum),
        23: NamedType("float32", TypeDescriptionFloat32),
        24: NamedType("float64", TypeDescriptionFloat64),
        25: NamedType("date-time", TypeDescriptionDateTime),
        26: NamedType("date", TypeDescriptionDate),
        2: NamedType("time", TypeDescriptionTime),
        255: NamedType("dont-care", TypeDescriptionDontCare)
    }

    # Convenience constructors
    @classmethod
    def null_data(cls) -> Self:
        return cls(TypeDescriptionNullData(NullType(None)))

    @classmethod
    def array(cls, number_of_elements: Unsigned16, type_description: "TypeDescription") -> Self:
        return cls(TypeDescriptionArray(TypeDescriptionArrayContent((number_of_elements, type_description))))

    @classmethod
    def structure(cls, elements: list["TypeDescription"]) -> Self:
        return cls(TypeDescriptionStructure(TypeDescriptionSequenceOf(elements)))

    @classmethod
    def boolean(cls) -> Self:
        return cls(TypeDescriptionBoolean(NullType(None)))

    @classmethod
    def octet_string(cls) -> Self:
        return cls(TypeDescriptionOctetString(NullType(None)))

    @classmethod
    def visible_string(cls) -> Self:
        return cls(TypeDescriptionVisibleString(NullType(None)))

    @classmethod
    def integer(cls) -> Self:
        return cls(TypeDescriptionInteger(NullType(None)))

    @classmethod
    def unsigned(cls) -> Self:
        return cls(TypeDescriptionUnsigned(NullType(None)))

    @classmethod
    def long(cls) -> Self:
        return cls(TypeDescriptionLong(NullType(None)))

    @classmethod
    def long_unsigned(cls) -> Self:
        return cls(TypeDescriptionLongUnsigned(NullType(None)))

    @classmethod
    def dont_care(cls) -> Self:
        return cls(TypeDescriptionDontCare(NullType(None)))


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


NullData = NullType0


@dataclass
class SequenceOfData(axdr.SequenceOfType[axdr.Type]): ...  # Forward declaration for recursive types


@dataclass
class Array(TaggedType["SequenceOfData"]):
    """[1] IMPLICIT SEQUENCE OF Data"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: SequenceOfData


@dataclass
class Structure(TaggedType["SequenceOfData"]):
    """[2] IMPLICIT SEQUENCE OF Data"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: SequenceOfData


@dataclass
class Boolean(TaggedType[BooleanType]):
    """[3] IMPLICIT BOOLEAN"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: BooleanType


@dataclass
class BitString(TaggedType[axdr.BitStringType]):
    """[4] IMPLICIT BIT STRING"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: axdr.BitStringType


@dataclass
class DoubleLong(TaggedType[Integer32]):
    """[5] IMPLICIT Integer32"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: Integer32


@dataclass
class DoubleLongUnsigned(TaggedType[Unsigned32]):
    """[6] IMPLICIT Unsigned32"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    value: Unsigned32


@dataclass
class OctetString(TaggedType[OctetStringType]):
    """[9] IMPLICIT OCTET STRING"""
    tag = 9
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class VisibleString(TaggedType[axdr.VisibleString]):
    """[10] IMPLICIT VisibleString"""
    tag = 10
    mode = TaggingMode.IMPLICIT
    value: axdr.VisibleString


@dataclass
class Utf8String(TaggedType[axdr.Utf8String]):
    """[12] IMPLICIT UTF8String"""
    tag = 12
    mode = TaggingMode.IMPLICIT
    value: axdr.Utf8String


@dataclass
class Bcd(TaggedType[Integer8]):
    """[13] IMPLICIT Integer8"""
    tag = 13
    mode = TaggingMode.IMPLICIT
    value: Integer8


@dataclass
class Integer(TaggedType[Integer8]):
    """[15] IMPLICIT Integer8"""
    tag = 15
    mode = TaggingMode.IMPLICIT
    value: Integer8


@dataclass
class Long(TaggedType[Integer16]):
    """[16] IMPLICIT Integer16"""
    tag = 16
    mode = TaggingMode.IMPLICIT
    value: Integer16


@dataclass
class Unsigned(TaggedType[Unsigned8]):
    """[17] IMPLICIT Unsigned8"""
    tag = 17
    mode = TaggingMode.IMPLICIT
    value: Unsigned8


@dataclass
class LongUnsigned(TaggedType[Unsigned16]):
    """[18] IMPLICIT Unsigned16"""
    tag = 18
    mode = TaggingMode.IMPLICIT
    value: Unsigned16


@dataclass
class ContentsDescription(TaggedType[TypeDescription]):
    """[0] TypeDescription"""
    tag = 0
    mode = TaggingMode.DEFAULT
    value: TypeDescription


@dataclass
class ArrayContents(TaggedType[OctetStringType]):
    """[1] IMPLICIT   OCTET STRING"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


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
            data = data_class.get_lc(buf)
            result.append(data)
        return result

    @classmethod
    def from_array[T: "Data"](cls, contents: ContentsDescription, array: list[T], buf_size: int = 65535) -> Self:
        buf = ByteBuffer.allocate(buf_size)
        for el in array:
            el.put_lc(buf)
        array_contents = ArrayContents(OctetStringType(bytes(buf.extract())))
        return cls((contents, array_contents))


@dataclass
class CompactArray(TaggedType[CompactArrayContent]):
    """[19] IMPLICIT SEQUENCE { contents-description TypeDescription, array-contents OCTET STRING }"""
    tag = 19
    mode = TaggingMode.IMPLICIT
    value: CompactArrayContent


@dataclass
class Long64(TaggedType[Integer64]):
    """[20] IMPLICIT Integer64"""
    tag = 20
    mode = TaggingMode.IMPLICIT
    value: Integer64


@dataclass
class Long64Unsigned(TaggedType[Unsigned64]):
    """[21] IMPLICIT Unsigned64"""
    tag = 21
    mode = TaggingMode.IMPLICIT
    value: Unsigned64


@dataclass
class Enum(TaggedType[Unsigned8]):
    """[22] IMPLICIT Unsigned8"""
    tag = 22
    mode = TaggingMode.IMPLICIT
    value: Unsigned8


class OctetStringTypeSize4(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(4)
    value: OctetStringType


class OctetStringTypeSize8(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(8)
    value: OctetStringType


class OctetStringTypeSize12(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(12)
    value: OctetStringType


class OctetStringTypeSize5(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(5)
    value: OctetStringType


def float2OctetString[T: (OctetStringTypeSize4, OctetStringTypeSize8)](type_: type[T], fmt: str, value: float) -> T:
    """ Input float: <sign><integer>.<fraction>[e[-+]power] example: 1.0, -0.003, 1e+12, 4.5e-7 """
    if "inf" in str(value):
        raise OverflowError("float overflow error")
    return type_(pack(fmt, value))


def octetString2Float(data: OCTET_STRING, fmt: Literal[">f", ">d"]) -> float:
    """return the build in float type IEEE 60559"""
    return unpack(fmt, data)[0]


@dataclass
class Float32(TaggedType[OctetStringTypeSize4]):
    """[23] IMPLICIT OCTET STRING (SIZE(4))"""
    tag = 23
    mode = TaggingMode.IMPLICIT
    value: OctetStringTypeSize4

    @classmethod
    def from_float(cls, value: float) -> Self:
        return cls(float2OctetString(cls.get_type(), ">f", value))

    def __float__(self) -> float:
        return octetString2Float(self.value.value, ">f")


@dataclass
class Float64(TaggedType[OctetStringTypeSize8]):
    """[24] IMPLICIT OCTET STRING (SIZE(8))"""
    tag = 24
    mode = TaggingMode.IMPLICIT
    value: OctetStringTypeSize8

    @classmethod
    def from_float(cls, value: float) -> Self:
        return cls(float2OctetString(cls.get_type(), ">d", value))

    def __float__(self) -> float:
        return octetString2Float(self.value.value, ">d")


@dataclass
class DateTime(TaggedType[OctetStringTypeSize12]):
    """[25] IMPLICIT OCTET STRING (SIZE(12))"""
    tag = 25
    mode = TaggingMode.IMPLICIT
    value: OctetStringTypeSize12


@dataclass
class Date(TaggedType[OctetStringTypeSize5]):
    """[26] IMPLICIT OCTET STRING (SIZE(5))"""
    tag = 26
    mode = TaggingMode.IMPLICIT
    value: OctetStringTypeSize5


@dataclass
class Time(TaggedType[OctetStringTypeSize4]):
    """[27] IMPLICIT OCTET STRING (SIZE(4))"""
    tag = 27
    mode = TaggingMode.IMPLICIT
    value: OctetStringTypeSize4


@dataclass
class DontCare(TaggedType[axdr.NullType]):
    """[255] IMPLICIT NULL"""
    tag = 255
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class Data(axdr.ChoiceType):
    """Data"""
    alternatives = axdr.create_alternatives(
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
    )
    value: NullData | Array | Structure | Boolean | BitString | DoubleLong | DoubleLongUnsigned | OctetString | VisibleString | Utf8String | Bcd | Integer | Long | Unsigned \
          | LongUnsigned | CompactArray | Long64 | Long64Unsigned | Enum | Float32 | Float64 | DateTime | Date | Time | DontCare

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
        return cls(DoubleLong(Integer32(IntegerType(value))))

    @classmethod
    def double_long_unsigned(cls, value: INTEGER) -> Self:
        """Create double-long-unsigned [6] Unsigned32"""
        return cls(DoubleLongUnsigned(Unsigned32(IntegerType(value))))

    @classmethod
    def octet_string(cls, value: OCTET_STRING) -> Self:
        """Create octet-string [9]"""
        return cls(OctetString(OctetStringType(value)))

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
        return cls(Bcd(Integer8(IntegerType(value))))

    @classmethod
    def integer(cls, value: INTEGER) -> Self:
        """Create integer [15] Integer8"""
        return cls(Integer(Integer8(IntegerType(value))))

    @classmethod
    def long(cls, value: INTEGER) -> Self:
        """Create long [16] Integer16"""
        return cls(Long(Integer16(IntegerType(value))))

    @classmethod
    def unsigned(cls, value: INTEGER) -> Self:
        """Create unsigned [17] Unsigned8"""
        return cls(Unsigned(Unsigned8(IntegerType(value))))

    @classmethod
    def long_unsigned(cls, value: INTEGER) -> Self:
        """Create long-unsigned [18] Unsigned16"""
        return cls(LongUnsigned(Unsigned16(IntegerType(value))))

    @classmethod
    def compact_array(cls, contents_description: ContentsDescription, array_contents: ArrayContents) -> Self:
        """Create compact-array [19]"""
        return cls(CompactArray(CompactArrayContent((contents_description, array_contents))))

    @classmethod
    def long64(cls, value: INTEGER) -> Self:
        """Create long64 [20] Integer64"""
        return cls(Long64(Integer64(IntegerType(value))))

    @classmethod
    def long64_unsigned(cls, value: INTEGER) -> Self:
        """Create long64-unsigned [21] Unsigned64"""
        return cls(Long64Unsigned(Unsigned64(IntegerType(value))))

    @classmethod
    def enum(cls, value: INTEGER) -> Self:
        """Create enum [22] Unsigned8"""
        return cls(Enum(Unsigned8(IntegerType(value))))

    @classmethod
    def float32(cls, value: OCTET_STRING) -> Self:
        """Create float32 [23] OCTET STRING (SIZE(4))"""
        return cls(Float32(OctetStringTypeSize4(OctetStringType(value))))

    @classmethod
    def float64(cls, value: OCTET_STRING) -> Self:
        """Create float64 [24] OCTET STRING (SIZE(8))"""
        return cls(Float64(OctetStringTypeSize8(OctetStringType(value))))

    @classmethod
    def date_time(cls, value: OCTET_STRING) -> Self:
        """Create date-time [25] OCTET STRING (SIZE(12))"""
        return cls(DateTime(OctetStringTypeSize12(OctetStringType(value))))

    @classmethod
    def date(cls, value: OCTET_STRING) -> Self:
        """Create date [26] OCTET STRING (SIZE(5))"""
        return cls(Date(OctetStringTypeSize5(OctetStringType(value))))

    @classmethod
    def time(cls, value: bytes) -> Self:
        """Create time [27] OCTET STRING (SIZE(4))"""
        if len(value) != 4:
            raise ValueError("time must be 4 bytes")
        return cls(Time(OctetStringTypeSize4(OctetStringType(value))))

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


setattr(SequenceOfData, "component_type", Data)
setattr(TypeDescriptionArrayContent, "components", (
        NamedType("number-of-elements", Unsigned16),
        NamedType("type-description", TypeDescription),
    ))
