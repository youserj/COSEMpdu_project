import datetime
from dataclasses import dataclass
from types import UnionType
from typing import Self, ClassVar, TypeAlias, Optional, Union, get_args, cast
from struct import pack, unpack
from StructResult.result import Error, ValueOrError
from .byte_buffer import ByteBuffer, put_chain
from .x680.constrained_type import SizeConstraint, ValueRange
from .x680.type import NamedType, INTEGER
from . import x680
from . import axdr
from .axdr import ConstrainedIntegerType, ConstrainedOctetStringType, OctetStringType, NullType, BooleanType, get_length, ImplicitTaggedType, NullType0


class Integer8(ConstrainedIntegerType):
    constraint_spec = ValueRange(-128, 127)


class Integer16(ConstrainedIntegerType):
    constraint_spec = ValueRange(-32768, 32767)


class Integer32(ConstrainedIntegerType):
    constraint_spec = ValueRange(-2147483648, 2147483647)


class Integer64(ConstrainedIntegerType):
    constraint_spec = ValueRange(-9223372036854775808, 9223372036854775807)


class Unsigned8(ConstrainedIntegerType):
    constraint_spec = ValueRange(0, 255)


class Unsigned16(ConstrainedIntegerType):
    constraint_spec = ValueRange(0, 65535)


class Unsigned32(ConstrainedIntegerType):
    constraint_spec = ValueRange(0, 4294967295)


class Unsigned64(ConstrainedIntegerType):
    constraint_spec = ValueRange(0, 18446744073709551615)


class ObjectName(Integer16):
    """ObjectName"""


LN_REFERENCE = ObjectName(0x0007)
SN_REFERENCE = ObjectName(-1536)  # 0xFA00


class TypeDescription(axdr.ChoiceType):  # Forward declaration
    """TypeDescription"""


NullData = NullType0
"""null-data [0] IMPLICIT NULL"""


@dataclass
class TypeDescriptionArray(ImplicitTaggedType, axdr.SequenceType):
    """array [1] IMPLICIT SEQUENCE
    {
        number-of-elements Unsigned16,
        type-description TypeDescription
    }"""
    tag: ClassVar[int] = 1
    number_of_elements: Unsigned16
    type_description: TypeDescription


SequenceOfTypeDescription: TypeAlias = axdr.SequenceOfType[TypeDescription]
"""SEQUENCE OF TypeDescription"""


class TypeDescriptionStructure(ImplicitTaggedType, SequenceOfTypeDescription):
    """structure [2] IMPLICIT SEQUENCE OF TypeDescription"""
    tag = 2


class TypeDescriptionBoolean(ImplicitTaggedType, NullType):
    """boolean [3] IMPLICIT NULL"""
    tag = 3


class TypeDescriptionBitString(ImplicitTaggedType, NullType):
    """bit-string [4] IMPLICIT NULL"""
    tag = 4


class TypeDescriptionDoubleLong(ImplicitTaggedType, NullType):
    """double-long [5] IMPLICIT NULL"""
    tag = 5


class TypeDescriptionDoubleLongUnsigned(ImplicitTaggedType, NullType):
    """double-long-unsigned [6] IMPLICIT NULL"""
    tag = 6


class TypeDescriptionOctetString(ImplicitTaggedType, NullType):
    """octet-string [9] IMPLICIT NULL"""
    tag = 9


class TypeDescriptionVisibleString(ImplicitTaggedType, NullType):
    """visible-string [10] IMPLICIT NULL"""
    tag = 10


class TypeDescriptionUtf8String(ImplicitTaggedType, NullType):
    """utf8-string [12] IMPLICIT NULL"""
    tag = 12


class TypeDescriptionBcd(ImplicitTaggedType, NullType):
    """bcd [13] IMPLICIT NULL"""
    tag = 13


class TypeDescriptionInteger(ImplicitTaggedType, NullType):
    """integer [15] IMPLICIT NULL"""
    tag = 15


class TypeDescriptionLong(ImplicitTaggedType, NullType):
    """long [16] IMPLICIT NULL"""
    tag = 16


class TypeDescriptionUnsigned(ImplicitTaggedType, NullType):
    """unsigned [17] IMPLICIT NULL"""
    tag = 17


class TypeDescriptionLongUnsigned(ImplicitTaggedType, NullType):
    """long-unsigned [18] IMPLICIT NULL"""
    tag = 18


class TypeDescriptionLong64(ImplicitTaggedType, NullType):
    """long64 [20] IMPLICIT NULL"""
    tag = 20


class TypeDescriptionLong64Unsigned(ImplicitTaggedType, NullType):
    """long64-unsigned [21] IMPLICIT NULL"""
    tag = 21


class TypeDescriptionEnum(ImplicitTaggedType, NullType):
    """enum [22] IMPLICIT NULL"""
    tag = 22


class TypeDescriptionFloat32(ImplicitTaggedType, NullType):
    """float32 [23] IMPLICIT NULL"""
    tag = 23


class TypeDescriptionFloat64(ImplicitTaggedType, NullType):
    """float64 [24] IMPLICIT NULL"""
    tag = 24


class TypeDescriptionDateTime(ImplicitTaggedType, NullType):
    """date-time [25] IMPLICIT NULL"""
    tag = 25


class TypeDescriptionDate(ImplicitTaggedType, NullType):
    """date [26] IMPLICIT NULL"""
    tag = 26


class TypeDescriptionTime(ImplicitTaggedType, NullType):
    """time [27] IMPLICIT NULL"""
    tag = 27


class TypeDescriptionDontCare(ImplicitTaggedType, NullType):
    """dont-care [255] IMPLICIT NULL"""
    tag = 255


setattr(TypeDescription, "alternatives", {
    0: NamedType("null-data", NullData),
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


class SequenceOfData[T: ImplicitTaggedType | axdr.ChoiceType](axdr.SequenceOfType[T]): ...  # Forward declaration for recursive types


class Array[T: ImplicitTaggedType | axdr.ChoiceType](ImplicitTaggedType, SequenceOfData[T]):
    """array [1] IMPLICIT SEQUENCE OF Data"""
    tag = 1


class Structure(ImplicitTaggedType, x680.SequenceType):
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
    def from_data(cls, *args: ImplicitTaggedType) -> Self:
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


class Boolean(ImplicitTaggedType, BooleanType):
    """boolean [3] IMPLICIT BOOLEAN"""
    tag = 3


class BitString(ImplicitTaggedType, axdr.BitStringType):
    """bit-string [4] IMPLICIT BIT STRING"""
    tag = 4


class DoubleLong(ImplicitTaggedType, Integer32):
    """double-long [5] IMPLICIT Integer32"""
    tag = 5


class DoubleLongUnsigned(ImplicitTaggedType, Unsigned32):
    """double-long-unsigned [6] IMPLICIT Unsigned32"""
    tag = 6


class OctetString(ImplicitTaggedType, OctetStringType):
    """octet-string [9] IMPLICIT OCTET STRING"""
    tag = 9


class VisibleString(ImplicitTaggedType, axdr.VisibleString):
    """visible-string [10] IMPLICIT VisibleString"""
    tag = 10


class Utf8String(ImplicitTaggedType, axdr.Utf8String):
    """utf8-string [12] IMPLICIT UTF8String"""
    tag = 12


class Bcd(ImplicitTaggedType, Integer8):
    """bcd [13] IMPLICIT Integer8"""
    tag = 13


class Integer(ImplicitTaggedType, Integer8):
    """integer [15] IMPLICIT Integer8"""
    tag = 15


class Long(ImplicitTaggedType, Integer16):
    """long [16] IMPLICIT Integer16"""
    tag = 16


class Unsigned(ImplicitTaggedType, Unsigned8):
    """unsigned [17] IMPLICIT Unsigned8"""
    tag = 17


class LongUnsigned(ImplicitTaggedType, Unsigned16):
    """long-unsigned [18] IMPLICIT Unsigned16"""
    tag = 18


class ContentsDescription(ImplicitTaggedType, TypeDescription):
    """contents-description [0] TypeDescription"""
    tag = 0


class ArrayContents(ImplicitTaggedType, OctetStringType):
    """array-contents [1] IMPLICIT   OCTET STRING"""
    tag = 1


@dataclass
class CompactArray(ImplicitTaggedType, axdr.SequenceType):
    """compact-array [19] IMPLICIT SEQUENCE
    {
        contents-description TypeDescription,
        array-contents OCTET STRING
    }"""
    tag: ClassVar[int] = 19
    contents_description: ContentsDescription
    array_contents: ArrayContents

    def get_array(self) -> list[ImplicitTaggedType]:
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
    def from_array[T: "Data"](cls, array: list[T], contents: Optional[ContentsDescription] = None, buf_size: int = 65535) -> Self:
        if contents is None:
            if len(array) == 0:
                raise ValueError("expected <contents> for empty array")
            contents = TypeDescription(TypeDescription.alternatives[array[0].tag].type_(None))
        buf = ByteBuffer.allocate(buf_size)
        for el in array:
            el.put_lc(buf)
        array_contents = ArrayContents(OctetStringType(bytes(buf.extract())))
        return cls(contents, array_contents)


class Long64(ImplicitTaggedType, Integer64):
    """long64 [20] IMPLICIT Integer64"""
    tag = 20


class Long64Unsigned(ImplicitTaggedType, Unsigned64):
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


class Enum(ImplicitTaggedType, Unsigned8):
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
        return cls(pack(cls.fmt, value))

    def __float__(self) -> float:
        return unpack(self.fmt, bytes(self.value))[0]


class Float32(ImplicitTaggedType, OctetStringTypeSize4, _Float):
    """float32 [23] IMPLICIT OCTET STRING (SIZE(4))"""
    tag = 23
    fmt = ">f"

    # @classmethod
    # def from_float(cls, value: float) -> Self:
    #     return cls(OctetStringType(pack(cls.fmt, value)))

    # def __float__(self) -> float:
    #     return unpack(self.fmt, bytes(self.value.value))[0]


class Float64(ImplicitTaggedType, OctetStringTypeSize8, _Float):
    """float64 [24] IMPLICIT OCTET STRING (SIZE(8))"""
    tag = 24
    fmt = ">d"

    # @classmethod
    # def from_float(cls, value: float) -> Self:
    #     return cls(OctetStringType(pack(cls.fmt, value)))

    # def __float__(self) -> float:
    #     return unpack(self.fmt, bytes(self.value.value))[0]


class DateTime(ImplicitTaggedType, OctetStringTypeSize12):
    """date-time [25] IMPLICIT OCTET STRING (SIZE(12))"""
    tag = 25


class Date(ImplicitTaggedType, OctetStringTypeSize5):
    """date [26] IMPLICIT OCTET STRING (SIZE(5))"""
    tag = 26


class Time(ImplicitTaggedType, OctetStringTypeSize4):
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


class DontCare(ImplicitTaggedType, axdr.NullType):
    """dont-care [255] IMPLICIT NULL"""
    tag = 255


SimpleDataType = Union[NullData | Boolean | BitString | DoubleLong | DoubleLongUnsigned | OctetString | VisibleString | \
                Utf8String | Bcd | Integer | Long | Unsigned | LongUnsigned | Long64 | Long64Unsigned | Enum | Float32 | \
                Float64 | DateTime | Date | Time | DeltaInteger | DeltaLong | DeltaDoubleLong | DeltaUnsigned | DeltaLongUnsigned | \
                DeltaDoubleLongUnsigned]
ComplexDataType = Union[Array[ImplicitTaggedType] | Structure | CompactArray]
CDT = Union[SimpleDataType | ComplexDataType]


class Data(axdr.ChoiceType):
    alternatives: axdr.Alternatives = {
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
    value: CDT


Data.alternatives[1] = NamedType("array", Array[Data])


def union2alternatives(item: UnionType) -> axdr.Alternatives:
    new = {}
    args: tuple[ImplicitTaggedType, ...] = cast("tuple[ImplicitTagged, ...]", get_args(item))
    if not args:
        args = item,
    for type_ in args:
        for id, n_t in Data.alternatives.items():
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


class ExternallyData(axdr.ChoiceType):

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
    components: ClassVar[tuple[NamedType[Enum], NamedType[axdr.ChoiceType]]]

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
