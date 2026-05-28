import datetime
from dataclasses import dataclass
from types import UnionType
from typing import Self, ClassVar, TypeAlias, Optional, Union, Protocol, get_args, Any, cast, Iterator, TypeVar
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
from .axdr import ConstrainedOctetStringType, IntegerType, OctetStringType, NullType, BooleanType, NullType0, Type, get_length, ImplicitTaggedType, ObjectIdentifierType


class TaggedNullType(ImplicitTaggedType[NullType]): ...


TD: TypeAlias = """Union[
    TypeDescriptionNullData, TypeDescriptionArray, TypeDescriptionStructure, TypeDescriptionBoolean,
    TypeDescriptionOctetString, TypeDescriptionVisibleString, TypeDescriptionInteger,
    TypeDescriptionUnsigned, TypeDescriptionLong, TypeDescriptionLongUnsigned, TypeDescriptionLong64,
    TypeDescriptionLong64Unsigned, TypeDescriptionEnum, TypeDescriptionFloat32, TypeDescriptionFloat64,
    TypeDescriptionDateTime, TypeDescriptionDate, TypeDescriptionTime, TypeDescriptionDontCare
]"""


class TypeDescription(axdr.ChoiceType):  # Forward declaration
    """TypeDescription"""

    # Convenience constructors
    @classmethod
    def null_data(cls) -> Self:
        return cls(TypeDescriptionNullData(NullType(None)))

    @classmethod
    def array(cls, number_of_elements: Unsigned16, type_description: "TypeDescription") -> Self:
        return cls(TypeDescriptionArray(TypeDescriptionArrayContent((number_of_elements, type_description))))

    @classmethod
    def structure(cls, elements: list["TypeDescription"]) -> Self:
        return cls(TypeDescriptionStructure(SequenceOfTypeDescription(elements)))

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


class TypeDescriptionNullData(TaggedNullType):
    """[0] IMPLICIT NULL"""
    tag = 0


@dataclass
class TypeDescriptionArrayContent(axdr.SequenceType):
    """array content: SEQUENCE { number-of-elements Unsigned16, type-description TypeDescription }"""
    number_of_elements: Unsigned16
    type_description: TypeDescription


class TypeDescriptionArray(ImplicitTaggedType[TypeDescriptionArrayContent]):
    """[1] IMPLICIT SEQUENCE { number-of-elements Unsigned16, type-description TypeDescription }"""
    tag = 1


class SequenceOfTypeDescription(axdr.SequenceOfType[TypeDescription]): ...  # Forward declaration


class TypeDescriptionStructure(ImplicitTaggedType[SequenceOfTypeDescription]):
    """[2] IMPLICIT SEQUENCE OF TypeDescription"""
    tag = 2


class TypeDescriptionBoolean(TaggedNullType):
    """[3] IMPLICIT NULL"""
    tag = 3


class TypeDescriptionBitString(TaggedNullType):
    """[4] IMPLICIT NULL"""
    tag = 4


class TypeDescriptionDoubleLong(TaggedNullType):
    """[5] IMPLICIT NULL"""
    tag = 5


class TypeDescriptionDoubleLongUnsigned(TaggedNullType):
    """[6] IMPLICIT NULL"""
    tag = 6


class TypeDescriptionOctetString(TaggedNullType):
    """[9] IMPLICIT NULL"""
    tag = 9


class TypeDescriptionVisibleString(TaggedNullType):
    """[10] IMPLICIT NULL"""
    tag = 10


class TypeDescriptionUtf8String(TaggedNullType):
    """[12] IMPLICIT NULL"""
    tag = 12


class TypeDescriptionBcd(TaggedNullType):
    """[13] IMPLICIT NULL"""
    tag = 13


class TypeDescriptionInteger(TaggedNullType):
    """[15] IMPLICIT NULL"""
    tag = 15


class TypeDescriptionLong(TaggedNullType):
    """[16] IMPLICIT NULL"""
    tag = 16


class TypeDescriptionUnsigned(TaggedNullType):
    """[17] IMPLICIT NULL"""
    tag = 17


class TypeDescriptionLongUnsigned(TaggedNullType):
    """[18] IMPLICIT NULL"""
    tag = 18


class TypeDescriptionLong64(TaggedNullType):
    """[20] IMPLICIT NULL"""
    tag = 20


class TypeDescriptionLong64Unsigned(TaggedNullType):
    """[21] IMPLICIT NULL"""
    tag = 21


class TypeDescriptionEnum(TaggedNullType):
    """[22] IMPLICIT NULL"""
    tag = 22


class TypeDescriptionFloat32(TaggedNullType):
    """[23] IMPLICIT NULL"""
    tag = 23


class TypeDescriptionFloat64(TaggedNullType):
    """[24] IMPLICIT NULL"""
    tag = 24


class TypeDescriptionDateTime(TaggedNullType):
    """[25] IMPLICIT NULL"""
    tag = 25


class TypeDescriptionDate(TaggedNullType):
    """[26] IMPLICIT NULL"""
    tag = 26


class TypeDescriptionTime(TaggedNullType):
    """[27] IMPLICIT NULL"""
    tag = 27


class TypeDescriptionDontCare(TaggedNullType):
    """[255] IMPLICIT NULL"""
    tag = 255


setattr(TypeDescription, "alternatives", {
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
})
setattr(TypeDescriptionStructure, "type_", SequenceOfTypeDescription)
setattr(SequenceOfTypeDescription, "component_type", TypeDescription)


NullData = NullType0


class SequenceOfData[T: ImplicitTaggedType[Any]](axdr.SequenceOfType[T]): ...  # Forward declaration for recursive types


class Array[T: ImplicitTaggedType[Any]](ImplicitTaggedType[SequenceOfData[T]]):
    """[1] IMPLICIT SEQUENCE OF Data"""
    tag = 1

    def __class_getitem__(cls, item: type[T]) -> type["Array[T]"]:
        name = f"{cls.__name__}[{item.__name__}]"
        return type(name, (cls,), {
            "_T": SequenceOfData[item],
        })

    def __iter__(self) -> Iterator[T]:
        for val in self.value:
            yield val


class Structure(ImplicitTaggedType[SequenceOfData[ImplicitTaggedType[Any]]]):
    """[2] IMPLICIT SEQUENCE OF Data"""
    tag = 2
    components: ClassVar[Optional[tuple[NamedType[Type], ...]]] = None  # 4.1.5 Common data types Table 2

    @classmethod
    def default(cls) -> Self:
        return cls(SequenceOfData([component.type_.default() for component in cls.components]))

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
        if cls.components is not None:
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
            if isinstance(value := n_t.type_.get(buf), Error):
                return value
            components_data.append(value)
        return cls(SequenceOfData(components_data))


class DigitalMixin[T: Unsigned8 | Unsigned16 | Unsigned32 | Unsigned64 | Integer8 | Integer16 | Integer32 | Integer64]:
    value: T

    def __int__(self) -> int:
        return self.value.value.value

    def normalize(self) -> INTEGER:
        return self.value.normalize()


class Boolean(ImplicitTaggedType[BooleanType]):
    """[3] IMPLICIT BOOLEAN"""
    tag = 3


class BitString(ImplicitTaggedType[axdr.BitStringType]):
    """[4] IMPLICIT BIT STRING"""
    tag = 4


class DoubleLong(DigitalMixin[Integer32], ImplicitTaggedType[Integer32]):
    """[5] IMPLICIT Integer32"""
    tag = 5


class DoubleLongUnsigned(DigitalMixin[Unsigned32], ImplicitTaggedType[Unsigned32]):
    """[6] IMPLICIT Unsigned32"""
    tag = 6


class OctetString(ImplicitTaggedType[OctetStringType]):
    """[9] IMPLICIT OCTET STRING"""
    tag = 9

    def normalize(self) -> OCTET_STRING:
        return super().normalize()


class VisibleString(ImplicitTaggedType[axdr.VisibleString]):
    """[10] IMPLICIT VisibleString"""
    tag = 10


class Utf8String(ImplicitTaggedType[axdr.Utf8String]):
    """[12] IMPLICIT UTF8String"""
    tag = 12


class Bcd(ImplicitTaggedType[Integer8]):
    """[13] IMPLICIT Integer8"""
    tag = 13


class Integer(DigitalMixin[Integer8], ImplicitTaggedType[Integer8]):
    """[15] IMPLICIT Integer8"""
    tag = 15


class Long(DigitalMixin[Integer16], ImplicitTaggedType[Integer16]):
    """[16] IMPLICIT Integer16"""
    tag = 16


class Unsigned(DigitalMixin[Unsigned8], ImplicitTaggedType[Unsigned8]):
    """[17] IMPLICIT Unsigned8"""
    tag = 17


class LongUnsigned(DigitalMixin[Unsigned16], ImplicitTaggedType[Unsigned16]):
    """[18] IMPLICIT Unsigned16"""
    tag = 18


class ContentsDescription(ImplicitTaggedType[TypeDescription]):
    """[0] TypeDescription"""
    tag = 0
    mode = TaggingMode.DEFAULT


class ArrayContents(ImplicitTaggedType[OctetStringType]):
    """[1] IMPLICIT   OCTET STRING"""
    tag = 1


@dataclass
class CompactArraySequenceType(axdr.SequenceType):
    """compact-array content: SEQUENCE { contents-description TypeDescription, array-contents OCTET STRING }"""
    contents_description: ContentsDescription
    array_contents: ArrayContents

    def get_array(self) -> list["CommonDataType[CDT]"]:
        if (type_ := Data.alternatives.get(self.contents_description.value.value.tag)) is None:
            raise ValueError(f"Unknown TypeDescription tag: {self.contents_description}")
        data_class = type_.type_
        contents_bytes = bytes(self.array_contents.value)
        if not contents_bytes:
            return []
        result: list["Data"] = []
        buf = ByteBuffer.wrap(contents_bytes)
        pos: int = 0
        while buf.remaining() > 0:
            data = data_class.get_lc(buf)
            if pos == buf.get_pos():
                raise ValueError("infinity <array-contents>")
            pos = buf.get_pos()
            result.append(data)
        return result

    @classmethod
    def from_array[T: "Data[CDT]"](cls, contents: ContentsDescription, array: list[T], buf_size: int = 65535) -> Self:
        buf = ByteBuffer.allocate(buf_size)
        for el in array:
            el.put_lc(buf)
        array_contents = ArrayContents(OctetStringType(bytes(buf.extract())))
        return cls((contents, array_contents))


class CompactArray(ImplicitTaggedType[CompactArraySequenceType]):
    """[19] IMPLICIT SEQUENCE { contents-description TypeDescription, array-contents OCTET STRING }"""
    tag = 19


class Long64(DigitalMixin[Integer64], ImplicitTaggedType[Integer64]):
    """[20] IMPLICIT Integer64"""
    tag = 20


class Long64Unsigned(DigitalMixin[Unsigned64], ImplicitTaggedType[Unsigned64]):
    """[21] IMPLICIT Unsigned64"""
    tag = 21


class EnumMixin:
    enumeration_item: ClassVar[dict[int, str]]
    value: Unsigned8

    def normalize(self) -> INTEGER:
        return self.value.normalize()

    def __init_subclass__(cls) -> None:
        ret = {}
        for name in cls.__annotations__:
            if name.isupper():
                ret[cls.__dict__[name]] = name
        cls.enumeration_item = ret

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int):
            return self.normalize() == other
        if isinstance(other, self.__class__):
            return self.normalize() == other.normalize()
        return False

    def __str__(self) -> str:
        value = self.normalize()
        return f"({value}){self.enumeration_item.get(value, "")}"


class BitMixin:
    enumeration_item: ClassVar[dict[int, str]]
    value: Unsigned8

    def normalize(self) -> INTEGER:
        return self.value.normalize()

    def __str__(self) -> str:
        value = self.normalize()
        values: list[str] = []
        for (k, v) in self.enumeration_item.items():
            if k & value:
                values.append(v)
        return f"({value}){" | ".join(values)}"

    def __contains__(self, item: INTEGER) -> bool:
        return bool(item & self.normalize())


class Enum(EnumMixin, ImplicitTaggedType[Unsigned8]):
    """[22] IMPLICIT Unsigned8"""
    tag = 22

    def __int__(self) -> int:
        return self.value.value.value


class OctetStringTypeSize4(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(4)


class OctetStringTypeSize8(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(8)


class OctetStringTypeSize12(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(12)


class OctetStringTypeSize5(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(5)


class _Float[T: (OctetStringTypeSize4, OctetStringTypeSize8)](ImplicitTaggedType[T]):
    fmt: ClassVar[str]

    @classmethod
    def from_float(cls, value: float) -> Self:
        return cls(cls._T(OctetStringType(pack(cls.fmt, value))))

    def __float__(self) -> float:
        return unpack(self.fmt, bytes(self.value.value))[0]


class Float32(_Float[OctetStringTypeSize4]):
    """[23] IMPLICIT OCTET STRING (SIZE(4))"""
    tag = 23
    fmt = ">f"


class Float64(_Float[OctetStringTypeSize8]):
    """[24] IMPLICIT OCTET STRING (SIZE(8))"""
    tag = 24
    fmt = ">d"


class DateTime(ImplicitTaggedType[OctetStringTypeSize12]):
    """[25] IMPLICIT OCTET STRING (SIZE(12))"""
    tag = 25


class Date(ImplicitTaggedType[OctetStringTypeSize5]):
    """[26] IMPLICIT OCTET STRING (SIZE(5))"""
    tag = 26


class TimeMixin[T: (OctetStringTypeSize4, OctetStringType)](Protocol):
    value: T

    @classmethod
    def parse(cls, value: OCTET_STRING) -> Self: ...

    def normalize(self) -> OCTET_STRING: ...

    @classmethod
    def fromisoformat(cls, value: str) -> Self:
        """Construct a time from a string in one of the ISO 8601 formats."""
        data = datetime.time.fromisoformat(value)
        return cls.parse(bytes((data.hour, data.minute, data.second, data.microsecond // 10_000)))

    def to_time(self) -> datetime.time:
        """ return python time. Used 00 instead 'NOT SPECIFIED'  """
        hour, minute, second, hundredths = self.normalize()
        return datetime.time(
            hour=hour if hour != 0xff else 0,
            minute=minute if minute != 0xff else 0,
            second=second if second != 0xff else 0,
            microsecond=hundredths * 10000 if hundredths != 0xff else 0)

    def isoformat(self) -> str:
        """Return the time formatted according to ISO."""
        return self.to_time().isoformat()


class Time(ImplicitTaggedType[OctetStringTypeSize4], TimeMixin[OctetStringTypeSize4]):
    """[27] IMPLICIT OCTET STRING (SIZE(4))"""
    tag = 27


class DeltaInteger(Integer):
    """[28] IMPLICIT Integer8"""
    tag = 28


class DeltaLong(Long):
    """[29] IMPLICIT Integer16"""
    tag = 29


class DeltaDoubleLong(DoubleLong):
    """[30] IMPLICIT Integer32"""
    tag = 30


class DeltaUnsigned(Unsigned):
    """[31] IMPLICIT Unsigned8"""
    tag = 31


class DeltaLongUnsigned(LongUnsigned):
    """[32] IMPLICIT Unsigned16"""
    tag = 32


class DeltaDoubleLongUnsigned(DoubleLongUnsigned):
    """[33] IMPLICIT Unsigned32"""
    tag = 33


class DontCare(ImplicitTaggedType[axdr.NullType]):
    """[255] IMPLICIT NULL"""
    tag = 255


SimpleDataType = Union[NullData | Boolean | BitString | DoubleLong | DoubleLongUnsigned | OctetString | VisibleString | \
                Utf8String | Bcd | Integer | Long | Unsigned | LongUnsigned | Long64 | Long64Unsigned | Enum | Float32 | \
                Float64 | DateTime | Date | Time | DeltaInteger | DeltaLong | DeltaDoubleLong | DeltaUnsigned | DeltaLongUnsigned | \
                DeltaDoubleLongUnsigned]
ComplexDataType = Union[Array[ImplicitTaggedType[Any]] | Structure | CompactArray]
CDT = Union[SimpleDataType | ComplexDataType]


Alternatives: TypeAlias = dict[int, NamedType[CDT | ImplicitTaggedType[Any]]]


data_alternatives: Alternatives = {
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


class CommonDataType[T: ImplicitTaggedType[Any]](axdr.ChoiceType, Protocol):
    """Data"""
    alternatives: Alternatives
    value: T

    # =========================================================================
    # Convenience constructors for common data types
    # =========================================================================

    # def __class_getitem__(cls, item: UnionType | TypeVar) -> type["Data[T]"]:
    #     if isinstance(item, UnionType):
    #         name = f"{cls.__name__}"  #[{item.__name__}]"
    #         new = {}
    #         args = cast("tuple[ImplicitTaggedType[Any]]", get_args(item))
    #         if not args:
    #             args = item,
    #         for type_ in args:
    #             for id, n_t in Data.alternatives.items():
    #                 if type_.tag == n_t.type_.tag:
    #                     new[id] = NamedType(n_t.identifier, type_)
    #                     break
    #         return type(name, (cls,), {
    #             "alternatives": new,
    #         })

    @classmethod
    def null_data(cls) -> "Data[NullData]":
        """Create null-data [0]"""
        return cls(NullData(axdr.null))

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
        return cls(CompactArray(CompactArraySequenceType((contents_description, array_contents))))

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


class Data(CommonDataType[CDT]):
    alternatives = data_alternatives


data_alternatives[1] = NamedType("array", Array[Data])


def union2alternatives(item: UnionType) -> Alternatives:
    new = {}
    args = cast("tuple[ImplicitTaggedType[Any], ...]", get_args(item))
    if not args:
        args = item,
    for type_ in args:
        for id, n_t in data_alternatives.items():
            if type_.tag == n_t.type_.tag:
                new[id] = NamedType(n_t.identifier, type_)
                break
    return new


def include_alternatives(type_alias: TypeAlias) -> dict[int, NamedType[CDT]]:
    new = {}
    for type_ in get_args(type_alias):
        for id, n_t in Data.alternatives.items():
            if issubclass(type_, n_t.type_):
                new[id] = type_
    return new


setattr(SequenceOfData, "component_type", Data)


class ExternallyData[T: ImplicitTaggedType[Any]](CommonDataType[T]):

    @property
    def selected(self) -> str:
        for n_t in self.alternatives.values():
            if isinstance(self.value, n_t.type_):
                return n_t.identifier
        raise ValueError(f"Value {self.value} not in alternatives: {", ".join(map(str, (n_t.identifier for n_t in self.alternatives.values())))}")

    @classmethod
    def get(cls, buf: ByteBuffer) -> Self | Error:
        return Error.from_e(RuntimeError(f"can't get {cls.__name__} separately"))


class DiscriminatedUnion(Structure):
    """implementation Choice CommonDataType, ex.:
        key_info_element ::= structure
        {
        key_info_type: enum:
        (0) identified_key,d        -- used with identified_key_info_options
        (1) wrapped_key,            -- used with wrapped_key_info_options
        (2) agreed_key              -- used with agreed_key_info_options
        key_info_options: CHOICE
        {
        identified_key_info_options,
        wrapped_key_info_options,
        agreed_key_info_options
        }
        }
        """
    components: ClassVar[tuple[NamedType[Enum], NamedType[ExternallyData[Any]]]]

    def __init_subclass__(cls) -> None:
        """create <components> from annotations"""
        elements: list[NamedType[Type]] = []
        for (identifier, type_), f in zip(cls.__annotations__.items(), (Structure.get_el0, Structure.get_el1)):
            elements.append((NamedType(identifier, type_)))
            setattr(cls, identifier, f)
        cls.components = tuple(elements)

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        if isinstance(length := get_length(buf), Error):
            return length
        if length != 2:
            return Error.from_e(ValueError(f"Invalid length for {cls.__name__}: expected 2, got {length}"))
        selector_t, value_t = cls.components
        if isinstance(selector := selector_t.type_.get(buf), Error):
            return selector
        if (alt := value_t.type_.alternatives.get(int(selector))) is None:
            return Error.from_e(ValueError(f"got {selector=}, expected {list(value_t.type_.alternatives.keys())}"))
        if isinstance(value := alt.type_.get(buf), Error):
            return value
        return cls(SequenceOfData([selector, value_t.type_(value)]))
