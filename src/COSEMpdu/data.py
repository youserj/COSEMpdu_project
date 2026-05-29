import datetime
from dataclasses import dataclass
from types import UnionType
from typing import Self, ClassVar, TypeAlias, Optional, Union, Protocol, get_args, Any, cast
from struct import pack, unpack
from StructResult.result import Error, ValueOrError
from .byte_buffer import ByteBuffer, put_chain
from .x680.constrained_type import SizeConstraint
from .x680.type import NamedType, INTEGER
from . import x680
from .x680.tagged_type import TaggingMode
from . import axdr
from .useful_types import Integer8, Integer16, Integer32, Integer64, Unsigned8, Unsigned16, Unsigned32, Unsigned64
from .axdr import ConstrainedOctetStringType, OctetStringType, NullType, BooleanType, get_length, ImplicitTaggedType, TaggedType


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
setattr(SequenceOfTypeDescription, "_T", TypeDescription)


class DataType(x680.Type, Protocol):
    """
    Mixin for COSEM Data types with tag-prefixed A-XDR encoding
    (IEC 61334-6 §6.7).

    Provides ``get`` / ``put`` methods that verify and encode a single
    tag byte, then delegate to the concrete type's ``get_lc`` / ``put_lc``
    for the actual A-XDR content.

    Usage::
        class NullData(DataType, NullType):
            tag = 0

        class Boolean(DataType, BooleanType):
            tag = 3

    In the MRO, ``DataType`` (first parent) handles the tag layer;
    the second parent (e.g. ``BooleanType``, ``NullType``) provides
    ``get_lc`` / ``put_lc`` for content encoding/decoding.
    """
    tag: int

    @classmethod
    def get(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        if isinstance(tag_number := buf.get_u8(), Error):
            return tag_number
        if tag_number != cls.tag:
            return Error.from_e(ValueError(f"expected tag {cls.tag}, got {tag_number}"))
        return cls.get_lc(buf)

    def put(self, buf: ByteBuffer) -> ValueOrError[int]:
        return put_chain(
            buf.put_u8(self.tag),
            self.put_lc(buf)
        )


class NullData(DataType, NullType):
    """null-data [0] IMPLICIT NULL"""
    tag = 0


class SequenceOfData[T: ImplicitTaggedType[Any]](axdr.SequenceOfType[T]): ...  # Forward declaration for recursive types


class Array[T: DataType](DataType, SequenceOfData[T]):
    """array [1] IMPLICIT SEQUENCE OF Data"""
    tag = 1


class Structure(DataType, x680.SequenceType):
    """[2] IMPLICIT SEQUENCE OF Data

    Although the specification defines this as a SEQUENCE OF, the implementation
    uses ``x680.SequenceType`` rather than ``SequenceOfType`` for convenience.
    ``SequenceType`` allows working with components by name (via ``self.components``),
    whereas ``SequenceOfType`` assumes a homogeneous list of identically-typed elements.
    Semantically, a COSEM Structure is a record with arbitrary named fields rather
    than a plain array, so using ``SequenceType`` more accurately reflects the
    actual data model.
    """
    tag: ClassVar[int] = 2

    @classmethod
    def from_data(cls, *args: DataType) -> Self:
        """Dynamically create a Structure subclass from positional arguments.

        Generates single-letter field names (``a``, ``b``, ``c``, …) for each
        positional argument, uses each argument's type as the field annotation,
        builds a new :func:`dataclass` subclass on the fly, and instantiates it
        with the supplied values.

        This allows constructing a typed Structure inline without manually
        defining a subclass::

            s = Structure.from_data(Integer(42), OctetStringType(b"hello"))
        """
        components_data: dict[str, Data] = {}
        for i, value in enumerate(args):
            components_data[chr(i + 97)] = value.__class__
        return dataclass(type(
            f"{cls.__name__}[{len(args)}]",
            (cls,),
            {"__annotations__": components_data}
        ))(*args)

    def __init_subclass__(cls) -> None:
        """create <components> from annotations"""
        cls._init_sequence_components()

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        if isinstance(length := get_length(buf), Error):
            return length
        return cls.get_c(buf, length)

    @classmethod
    def get_c(cls, buf: ByteBuffer, length: int) -> ValueOrError[Self]:
        """Decode SEQUENCE OF content from a buffer.

        Operates in two modes:

        1. **Dynamic** — when ``cls`` has no ``components`` attribute (i.e. decoding
           an externally-defined or runtime-generated Structure). Reads *length*
           elements via ``Data.get()``, assigns them single-letter field names
           (``a``, ``b``, ``c``, …), and returns a dynamically-created dataclass
           subclass.

        2. **Static** — when ``cls`` has ``components`` (i.e. a statically-defined
           Structure subclass). Reads each field by its declared name and type,
           matching the shape of the component definitions.

        :param buf: Buffer containing SEQUENCE content.
        :param length: Number of elements in the SEQUENCE (or number of components
                       for a statically-defined Structure).
        """
        components_data: dict[str, Data] = {}
        values: list[Data] = []
        if not hasattr(cls, "components"):
            for i in range(length):
                if isinstance(value := Data.get(buf), Error):
                    return value
                components_data[chr(i + 97)] = value.value.__class__  # TODO: maybe simple - Data?
                values.append(value)
            return dataclass(type(
                f"{cls.__name__}[{length}]",
                (cls,),
                {"__annotations__": components_data}
            ))(*values)
        for n_t in cls.components:
            if isinstance(value := n_t.type_.get(buf), Error):
                return value
            components_data[n_t.identifier] = value
        return cls(**components_data)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode SEQUENCE OF to A-XDR (IEC 61334-6 §6.10)

        Returns number of bytes written.
        """
        return put_chain(
            axdr.put_length(buf, len(self.components)),  # Variable-length encoding (§6.10.2)
            self.put_c(buf)
        )

    def put_c(self, buf: ByteBuffer) -> ValueOrError[int]:
        return put_chain(*(getattr(self, comp.identifier).put(buf) for comp in self.components))


class DigitalMixin[T: Unsigned8 | Unsigned16 | Unsigned32 | Unsigned64 | Integer8 | Integer16 | Integer32 | Integer64]:
    value: T

    def __int__(self) -> int:
        return self.value.value.value

    def normalize(self) -> INTEGER:
        return self.value.normalize()


class Boolean(DataType, BooleanType):
    """boolean [3] IMPLICIT BOOLEAN"""
    tag = 3


class BitString(DataType, axdr.BitStringType):
    """bit-string [4] IMPLICIT BIT STRING"""
    tag = 4


class DoubleLong(DataType, Integer32):
    """double-long [5] IMPLICIT Integer32"""
    tag = 5


class DoubleLongUnsigned(DataType, Unsigned32):
    """double-long-unsigned [6] IMPLICIT Unsigned32"""
    tag = 6


class OctetString(DataType, OctetStringType):
    """octet-string [9] IMPLICIT OCTET STRING"""
    tag = 9


class VisibleString(DataType, axdr.VisibleString):
    """visible-string [10] IMPLICIT VisibleString"""
    tag = 10


class Utf8String(DataType, axdr.Utf8String):
    """utf8-string [12] IMPLICIT UTF8String"""
    tag = 12


class Bcd(DataType, Integer8):
    """bcd [13] IMPLICIT Integer8"""
    tag = 13


class Integer(DataType, Integer8):
    """integer [15] IMPLICIT Integer8"""
    tag = 15


class Long(DataType, Integer16):
    """long [16] IMPLICIT Integer16"""
    tag = 16


class Unsigned(DataType, Unsigned8):
    """unsigned [17] IMPLICIT Unsigned8"""
    tag = 17


class LongUnsigned(DataType, Unsigned16):
    """long-unsigned [18] IMPLICIT Unsigned16"""
    tag = 18


class ContentsDescription(TaggedType[TypeDescription]):
    """contents-description [0] TypeDescription"""
    tag = 0
    mode = TaggingMode.DEFAULT


class ArrayContents(ImplicitTaggedType[OctetStringType]):
    """array-contents [1] IMPLICIT   OCTET STRING"""
    tag = 1


@dataclass
class CompactArray(DataType, axdr.SequenceType):
    """compact-array [19] IMPLICIT SEQUENCE
    {
        contents-description TypeDescription,
        array-contents OCTET STRING
    }"""
    tag: ClassVar[int] = 19
    contents_description: ContentsDescription
    array_contents: ArrayContents

    def get_array(self) -> list[DataType]:
        if (type_ := Data.alternatives.get(self.contents_description.value.tag)) is None:
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
    def from_array[T: "CommonDataType[CDT]"](cls, array: list[T], contents: Optional[ContentsDescription] = None, buf_size: int = 65535) -> Self:
        if contents is None:
            if len(array) == 0:
                raise ValueError("expected <contents> for empty array")
            contents = TypeDescription(TypeDescription.alternatives[array[0].tag].type_(axdr.null))
        buf = ByteBuffer.allocate(buf_size)
        for el in array:
            el.put_lc(buf)
        array_contents = ArrayContents(OctetStringType(bytes(buf.extract())))
        return cls(contents, array_contents)


class Long64(DataType, Integer64):
    """long64 [20] IMPLICIT Integer64"""
    tag = 20


class Long64Unsigned(DataType, Unsigned64):
    """long64-unsigned [21] IMPLICIT Unsigned64"""
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


class Enum(DataType, Unsigned8):
    """enum [22] IMPLICIT Unsigned8"""
    tag = 22


class OctetStringTypeSize4(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(4)


class OctetStringTypeSize8(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(8)


class OctetStringTypeSize12(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(12)


class OctetStringTypeSize5(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(5)


class _Float(ConstrainedOctetStringType):
    fmt: ClassVar[str]

    @classmethod
    def from_float(cls, value: float) -> Self:
        return cls(OctetStringType(pack(cls.fmt, value)))

    def __float__(self) -> float:
        return unpack(self.fmt, bytes(self.value.value))[0]


class Float32(DataType, OctetStringTypeSize4, _Float):
    """float32 [23] IMPLICIT OCTET STRING (SIZE(4))"""
    tag = 23
    fmt = ">f"

    # @classmethod
    # def from_float(cls, value: float) -> Self:
    #     return cls(OctetStringType(pack(cls.fmt, value)))

    # def __float__(self) -> float:
    #     return unpack(self.fmt, bytes(self.value.value))[0]


class Float64(DataType, OctetStringTypeSize8, _Float):
    """float64 [24] IMPLICIT OCTET STRING (SIZE(8))"""
    tag = 24
    fmt = ">d"

    # @classmethod
    # def from_float(cls, value: float) -> Self:
    #     return cls(OctetStringType(pack(cls.fmt, value)))

    # def __float__(self) -> float:
    #     return unpack(self.fmt, bytes(self.value.value))[0]


class DateTime(DataType, OctetStringTypeSize12):
    """date-time [25] IMPLICIT OCTET STRING (SIZE(12))"""
    tag = 25


class Date(DataType, OctetStringTypeSize5):
    """date [26] IMPLICIT OCTET STRING (SIZE(5))"""
    tag = 26


class Time(DataType, OctetStringTypeSize4):
    """time [27] IMPLICIT OCTET STRING (SIZE(4))"""
    tag = 27

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


class DeltaInteger(Integer):
    """delta-integer [28] IMPLICIT Integer8"""
    tag = 28


class DeltaLong(Long):
    """delta-long [29] IMPLICIT Integer16"""
    tag = 29


class DeltaDoubleLong(DoubleLong):
    """delta-double-long [30] IMPLICIT Integer32"""
    tag = 30


class DeltaUnsigned(Unsigned):
    """delta-unsigned [31] IMPLICIT Unsigned8"""
    tag = 31


class DeltaLongUnsigned(LongUnsigned):
    """delta-long-unsigned [32] IMPLICIT Unsigned16"""
    tag = 32


class DeltaDoubleLongUnsigned(DoubleLongUnsigned):
    """delta-double-long-unsigned[33] IMPLICIT Unsigned32"""
    tag = 33


class DontCare(DataType, axdr.NullType):
    """dont-care [255] IMPLICIT NULL"""
    tag = 255


SimpleDataType = Union[NullData | Boolean | BitString | DoubleLong | DoubleLongUnsigned | OctetString | VisibleString | \
                Utf8String | Bcd | Integer | Long | Unsigned | LongUnsigned | Long64 | Long64Unsigned | Enum | Float32 | \
                Float64 | DateTime | Date | Time | DeltaInteger | DeltaLong | DeltaDoubleLong | DeltaUnsigned | DeltaLongUnsigned | \
                DeltaDoubleLongUnsigned]
ComplexDataType = Union[Array[DataType] | Structure | CompactArray]
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
    def structure(cls, elements: list["Data[CDT]"]) -> "Data[Structure]":
        """Create structure [2] SEQUENCE OF Data"""
        return cls(Structure(SequenceOfData(elements)))

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


setattr(SequenceOfData, "_T", Data)


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
    def __init_subclass__(cls) -> None:
        """create <components> from annotations"""
        super().__init_subclass__()
        if len(cls.components) != 2:
            raise RuntimeError(f"got {len(cls.components)}, expected 2")

    @classmethod
    def get_c(cls, buf: ByteBuffer, length: int) -> ValueOrError[Self]:
        if length != 2:
            return Error.from_e(ValueError(f"Invalid length for {cls.__name__}: expected 2, got {length}"))
        if isinstance(selector := cls.components[0].type_.get(buf), Error):
            return selector
        if (alt := cls.components[1].type_.alternatives.get(int(selector))) is None:
            return Error.from_e(ValueError(f"got {cls.components[0].identifier}={selector}, expected {list(cls.components[1].type_.alternatives.keys())}"))
        if isinstance(value := alt.type_.get(buf), Error):
            return value
        return cls(selector, cls.components[1].type_(value))
