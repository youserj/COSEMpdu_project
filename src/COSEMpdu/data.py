from typing import Self, ClassVar, TypeAlias, Optional
from struct import pack, unpack
from StructResult.result import Error, ValueOrError
from .byte_buffer import ByteBuffer
from .x680.constrained_type import SizeConstraint
from .x680.type import (
    NamedType, REAL, TYPE_VALUE,
    BIT_STRING, BOOLEAN, OCTET_STRING, INTEGER, STRING
    )
from .x680.tagged_type import TaggingMode
from . import axdr
from .useful_types import (
    Integer8, Integer16, Integer32, Integer64,
    Unsigned8, Unsigned16, Unsigned32, Unsigned64
)
from .axdr import ConstrainedOctetStringType, IntegerType, OctetStringType, NullType, BooleanType, TaggedType, NullType0, Type, get_length

# =============================================================================
# TypeDescription CHOICE
# =============================================================================
# TypeDescription ::= CHOICE { ... }
# Most alternatives are NULL (type indicator only)
# Some have structure (array, structure)
# =============================================================================


class TypeDescriptionNullData(TaggedType[NullType]):
    """[0] IMPLICIT NULL"""
    tag = 0
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionArrayContent(axdr.SequenceType):
    """array content: SEQUENCE { number-of-elements Unsigned16, type-description TypeDescription }"""


class TypeDescriptionArray(TaggedType[TypeDescriptionArrayContent]):
    """[1] IMPLICIT SEQUENCE { number-of-elements Unsigned16, type-description TypeDescription }"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: TypeDescriptionArrayContent


class TypeDescriptionStructure(TaggedType["TypeDescriptionSequenceOf"]):
    """[2] IMPLICIT SEQUENCE OF TypeDescription"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: "TypeDescriptionSequenceOf"  # Forward reference


class TypeDescriptionBoolean(TaggedType[NullType]):
    """[3] IMPLICIT NULL"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionBitString(TaggedType[NullType]):
    """[4] IMPLICIT NULL"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionDoubleLong(TaggedType[NullType]):
    """[5] IMPLICIT NULL"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionDoubleLongUnsigned(TaggedType[NullType]):
    """[6] IMPLICIT NULL"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionOctetString(TaggedType[NullType]):
    """[9] IMPLICIT NULL"""
    tag = 9
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionVisibleString(TaggedType[NullType]):
    """[10] IMPLICIT NULL"""
    tag = 10
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionUtf8String(TaggedType[NullType]):
    """[12] IMPLICIT NULL"""
    tag = 12
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionBcd(TaggedType[NullType]):
    """[13] IMPLICIT NULL"""
    tag = 13
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionInteger(TaggedType[NullType]):
    """[15] IMPLICIT NULL"""
    tag = 15
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionLong(TaggedType[NullType]):
    """[16] IMPLICIT NULL"""
    tag = 16
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionUnsigned(TaggedType[NullType]):
    """[17] IMPLICIT NULL"""
    tag = 17
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionLongUnsigned(TaggedType[NullType]):
    """[18] IMPLICIT NULL"""
    tag = 18
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionLong64(TaggedType[NullType]):
    """[20] IMPLICIT NULL"""
    tag = 20
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionLong64Unsigned(TaggedType[NullType]):
    """[21] IMPLICIT NULL"""
    tag = 21
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionEnum(TaggedType[NullType]):
    """[22] IMPLICIT NULL"""
    tag = 22
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionFloat32(TaggedType[NullType]):
    """[23] IMPLICIT NULL"""
    tag = 23
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionFloat64(TaggedType[NullType]):
    """[24] IMPLICIT NULL"""
    tag = 24
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionDateTime(TaggedType[NullType]):
    """[25] IMPLICIT NULL"""
    tag = 25
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionDate(TaggedType[NullType]):
    """[26] IMPLICIT NULL"""
    tag = 26
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionTime(TaggedType[NullType]):
    """[27] IMPLICIT NULL"""
    tag = 27
    mode = TaggingMode.IMPLICIT
    value: NullType


class TypeDescriptionDontCare(TaggedType[NullType]):
    """[255] IMPLICIT NULL"""
    tag = 255
    mode = TaggingMode.IMPLICIT
    value: NullType


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
        27: NamedType("time", TypeDescriptionTime),
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


class SequenceOfData(axdr.SequenceOfType[axdr.Type]): ...  # Forward declaration for recursive types


class Array(TaggedType["SequenceOfData"]):
    """[1] IMPLICIT SEQUENCE OF Data"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: SequenceOfData


class Structure(TaggedType["SequenceOfData"]):
    """[2] IMPLICIT SEQUENCE OF Data"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: SequenceOfData
    components: ClassVar[Optional[tuple[NamedType[Type], ...]]]  # 4.1.5 Common data types Table 2

    @property
    def get_el0(self):
        return self.value[0]

    @property
    def get_el1(self):
        return self.value[1]

    @property
    def get_el2(self):
        return self.value[2]

    @property
    def get_el3(self):
        return self.value[3]

    @property
    def get_el4(self):
        return self.value[4]

    @property
    def get_el5(self):
        return self.value[5]

    @property
    def get_el6(self):
        return self.value[6]

    @property
    def get_el7(self):
        return self.value[7]

    @property
    def get_el8(self):
        return self.value[8]

    @property
    def get_el9(self):
        return self.value[9]

    def __init_subclass__(cls, **kwargs) -> None:
        """create <components> from annotations"""
        elements: list[NamedType[Type]] = []
        if hasattr(cls, "components"):
            elements.extend(cls.components)
            for identifier, type_ in cls.__annotations__.items():
                for i, el in enumerate(cls.components):
                    if identifier == el.identifier:
                        elements[i] = NamedType(identifier, type_)
                        break
        else:
            for (identifier, type_), f in zip(cls.__annotations__.items(), (
                    Structure.get_el0, Structure.get_el1, Structure.get_el2, Structure.get_el3, Structure.get_el4, Structure.get_el5, Structure.get_el6, Structure.get_el7,
                    Structure.get_el8, Structure.get_el9)):
                elements.append((NamedType(identifier, type_)))
                setattr(cls, identifier, f)
        cls.components = tuple(elements)

    @classmethod
    def parse(cls, value: TYPE_VALUE) -> Self:
        if not isinstance(value, tuple):
            raise ValueError(f"in Structure.parse got {value}, expected <tuple>")
        if cls.components:
            return cls(SequenceOfData([comp.type_.parse(val) for comp, val in zip(cls.components, value, strict=True)]))
        return super().parse(value)

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        if isinstance(length := get_length(buf), Error):
            return length
        return cls.get_c(buf, length)

    @classmethod
    def get_c(cls, buf: ByteBuffer, length: int) -> ValueOrError[Self]:
        if cls.components is None:
            if isinstance(value := SequenceOfData.get_c(buf, length), Error):
                return value
            return cls(value)
        components_data: list[Type] = []
        for n_t in cls.components:
            if isinstance(value := n_t.type_.get_lc(buf), Error):
                return value
            components_data.append(value)
        return cls(SequenceOfData(components_data))


class Boolean(TaggedType[BooleanType]):
    """[3] IMPLICIT BOOLEAN"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: BooleanType


class BitString(TaggedType[axdr.BitStringType]):
    """[4] IMPLICIT BIT STRING"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: axdr.BitStringType


class DoubleLong(TaggedType[Integer32]):
    """[5] IMPLICIT Integer32"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: Integer32


class DoubleLongUnsigned(TaggedType[Unsigned32]):
    """[6] IMPLICIT Unsigned32"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    value: Unsigned32


class OctetString(TaggedType[OctetStringType]):
    """[9] IMPLICIT OCTET STRING"""
    tag = 9
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class VisibleString(TaggedType[axdr.VisibleString]):
    """[10] IMPLICIT VisibleString"""
    tag = 10
    mode = TaggingMode.IMPLICIT
    value: axdr.VisibleString


class Utf8String(TaggedType[axdr.Utf8String]):
    """[12] IMPLICIT UTF8String"""
    tag = 12
    mode = TaggingMode.IMPLICIT
    value: axdr.Utf8String


class Bcd(TaggedType[Integer8]):
    """[13] IMPLICIT Integer8"""
    tag = 13
    mode = TaggingMode.IMPLICIT
    value: Integer8


class Integer(TaggedType[Integer8]):
    """[15] IMPLICIT Integer8"""
    tag = 15
    mode = TaggingMode.IMPLICIT
    value: Integer8


class Long(TaggedType[Integer16]):
    """[16] IMPLICIT Integer16"""
    tag = 16
    mode = TaggingMode.IMPLICIT
    value: Integer16


class Unsigned(TaggedType[Unsigned8]):
    """[17] IMPLICIT Unsigned8"""
    tag = 17
    mode = TaggingMode.IMPLICIT
    value: Unsigned8


class LongUnsigned(TaggedType[Unsigned16]):
    """[18] IMPLICIT Unsigned16"""
    tag = 18
    mode = TaggingMode.IMPLICIT
    value: Unsigned16


class ContentsDescription(TaggedType[TypeDescription]):
    """[0] TypeDescription"""
    tag = 0
    mode = TaggingMode.DEFAULT
    value: TypeDescription


class ArrayContents(TaggedType[OctetStringType]):
    """[1] IMPLICIT   OCTET STRING"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


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


class CompactArray(TaggedType[CompactArrayContent]):
    """[19] IMPLICIT SEQUENCE { contents-description TypeDescription, array-contents OCTET STRING }"""
    tag = 19
    mode = TaggingMode.IMPLICIT
    value: CompactArrayContent


class Long64(TaggedType[Integer64]):
    """[20] IMPLICIT Integer64"""
    tag = 20
    mode = TaggingMode.IMPLICIT
    value: Integer64


class Long64Unsigned(TaggedType[Unsigned64]):
    """[21] IMPLICIT Unsigned64"""
    tag = 21
    mode = TaggingMode.IMPLICIT
    value: Unsigned64


class Enum(TaggedType[Unsigned8]):
    """[22] IMPLICIT Unsigned8"""
    tag = 22
    mode = TaggingMode.IMPLICIT
    value: Unsigned8


class OctetStringTypeSize4(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(4)


class OctetStringTypeSize8(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(8)


class OctetStringTypeSize12(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(12)


class OctetStringTypeSize5(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(5)


class _Float[T: (OctetStringTypeSize4, OctetStringTypeSize8)](TaggedType[T]):
    value: T
    fmt: ClassVar[str]

    @classmethod
    def from_float(cls, value: float) -> Self:
        return cls(cls._T(OctetStringType(pack(cls.fmt, value))))

    def __float__(self) -> float:
        return unpack(self.fmt, bytes(self.value.value))[0]


class Float32(_Float[OctetStringTypeSize4]):
    """[23] IMPLICIT OCTET STRING (SIZE(4))"""
    tag = 23
    mode = TaggingMode.IMPLICIT
    value: OctetStringTypeSize4
    fmt = ">f"


class Float64(_Float[OctetStringTypeSize8]):
    """[24] IMPLICIT OCTET STRING (SIZE(8))"""
    tag = 24
    mode = TaggingMode.IMPLICIT
    value: OctetStringTypeSize8
    fmt = ">d"


class DateTime(TaggedType[OctetStringTypeSize12]):
    """[25] IMPLICIT OCTET STRING (SIZE(12))"""
    tag = 25
    mode = TaggingMode.IMPLICIT
    value: OctetStringTypeSize12


class Date(TaggedType[OctetStringTypeSize5]):
    """[26] IMPLICIT OCTET STRING (SIZE(5))"""
    tag = 26
    mode = TaggingMode.IMPLICIT
    value: OctetStringTypeSize5


class Time(TaggedType[OctetStringTypeSize4]):
    """[27] IMPLICIT OCTET STRING (SIZE(4))"""
    tag = 27
    mode = TaggingMode.IMPLICIT
    value: OctetStringTypeSize4


class DeltaInteger(TaggedType[Integer8]):
    """[28] IMPLICIT Integer8"""
    tag = 28
    mode = TaggingMode.IMPLICIT
    value: Integer8


class DeltaLong(TaggedType[Integer16]):
    """[29] IMPLICIT Integer16"""
    tag = 29
    mode = TaggingMode.IMPLICIT
    value: Integer16


class DeltaDoubleLong(TaggedType[Integer32]):
    """[30] IMPLICIT Integer32"""
    tag = 30
    mode = TaggingMode.IMPLICIT
    value: Integer32


class DeltaUnsigned(TaggedType[Unsigned8]):
    """[31] IMPLICIT Unsigned8"""
    tag = 31
    mode = TaggingMode.IMPLICIT
    value: Unsigned8


class DeltaLongUnsigned(TaggedType[Unsigned16]):
    """[32] IMPLICIT Unsigned16"""
    tag = 32
    mode = TaggingMode.IMPLICIT
    value: Unsigned16


class DeltaDoubleLongUnsigned(TaggedType[Unsigned32]):
    """[33] IMPLICIT Unsigned32"""
    tag = 33
    mode = TaggingMode.IMPLICIT
    value: Unsigned32


class DontCare(TaggedType[axdr.NullType]):
    """[255] IMPLICIT NULL"""
    tag = 255
    mode = TaggingMode.IMPLICIT
    value: NullType


SimpleDataType: TypeAlias = NullData | Boolean | BitString | DoubleLong | DoubleLongUnsigned | OctetString | VisibleString | \
                Utf8String | Bcd | Integer | Long | Unsigned | LongUnsigned | Long64 | Long64Unsigned | Enum | Float32 | \
                Float64 | DateTime | Date | Time | DeltaInteger | DeltaLong | DeltaDoubleLong | DeltaUnsigned | DeltaLongUnsigned | \
                DeltaDoubleLongUnsigned
ComplexDataType: TypeAlias = Array | Structure | CompactArray
CDT: TypeAlias = SimpleDataType | ComplexDataType


class Data[T: CDT](axdr.ChoiceType):
    """Data"""
    alternatives = {
        0: NamedType("null-data", NullData),
        1: NamedType("array", Array),
        2: NamedType("structure", Structure),
        3: NamedType("boolean", Boolean),
        4: NamedType("bit-string", BitString),
        5: NamedType("double-long", DoubleLong),
        6: NamedType("double-long-unsigned", DoubleLongUnsigned),
        9: NamedType("octet-string", OctetString),
        10: NamedType("visible-string", VisibleString),
        12: NamedType("utf8-string", Utf8String),
        13: NamedType("bcd", Bcd),
        15: NamedType("integer", Integer),
        16: NamedType("long", Long),
        17: NamedType("unsigned", Unsigned),
        18: NamedType("long-unsigned", LongUnsigned),
        19: NamedType("compact-array", CompactArray),
        20: NamedType("long64", Long64),
        21: NamedType("long64-unsigned", Long64Unsigned),
        22: NamedType("enum", Enum),
        23: NamedType("float32", Float32),
        24: NamedType("float64", Float64),
        25: NamedType("date-time", DateTime),
        26: NamedType("date", Date),
        27: NamedType("time", Time),
        28: NamedType("delta-integer", DeltaInteger),
        29: NamedType("delta-long", DeltaLong),
        30: NamedType("delta-double-long", DeltaDoubleLong),
        31: NamedType("delta-unsigned", DeltaUnsigned),
        32: NamedType("delta-long-unsigned", DeltaLongUnsigned),
        33: NamedType("delta-double-long-unsigned", DeltaDoubleLongUnsigned),
        255: NamedType("dont-care", DontCare)
    }
    value: T

    # =========================================================================
    # Convenience constructors for common data types
    # =========================================================================

    @classmethod
    def null_data(cls) -> "Data[NullData]":
        """Create null-data [0]"""
        return cls(NullData(axdr.NullType(None)))

    @classmethod
    def array(cls, elements: list["Data[CDT]"]) -> "Data[Array]":
        """Create array [1] SEQUENCE OF Data"""
        return cls(Array(SequenceOfData(elements)))

    @classmethod
    def structure(cls, elements: list["Data[CDT]"]) -> "Data[Structure]":
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
    def float32(cls, value: REAL) -> "Data[Float32]":
        """Create float32 [23] OCTET STRING (SIZE(4))"""
        return cls(Float32.from_float(value))

    @classmethod
    def float64(cls, value: REAL) -> "Data[Float64]":
        """Create float64 [24] OCTET STRING (SIZE(8))"""
        return cls(Float64.from_float(value))

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
    def delta_integer(cls, value: INTEGER) -> Self:
        """Create delta-integer [28] Integer8"""
        return cls(DeltaInteger(Integer8(IntegerType(value))))

    @classmethod
    def delta_long(cls, value: INTEGER) -> Self:
        """Create delta-long [29] Integer16"""
        return cls(DeltaLong(Integer16(IntegerType(value))))

    @classmethod
    def delta_double_long(cls, value: INTEGER) -> Self:
        """Create delta-double-long [30] Integer32"""
        return cls(DeltaDoubleLong(Integer32(IntegerType(value))))

    @classmethod
    def delta_unsigned(cls, value: INTEGER) -> Self:
        """Create delta-unsigned [31] Unsigned8"""
        return cls(DeltaUnsigned(Unsigned8(IntegerType(value))))

    @classmethod
    def delta_long_unsigned(cls, value: INTEGER) -> Self:
        """Create delta-long-unsigned [32] Unsigned16"""
        return cls(DeltaLongUnsigned(Unsigned16(IntegerType(value))))

    @classmethod
    def delta_double_long_unsigned(cls, value: INTEGER) -> Self:
        """Create delta-double-long-unsigned [33] Unsigned32"""
        return cls(DeltaDoubleLongUnsigned(Unsigned32(IntegerType(value))))

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
