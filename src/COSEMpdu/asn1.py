"""Rec. ITU-T X.680 (02/2021)"""
from abc import ABC, abstractmethod
from functools import lru_cache
from inspect import getfullargspec
from typing import Self, ByteString, TypeAlias, Literal, Any, Union, get_args
from dataclasses import dataclass
from enum import IntEnum
from .byte_buffer import ByteBuffer as Buf


_value = ("value",)


def get_values(value: str) -> list[str]:
    """parsing sequence string"""
    ret = list()
    el = ''
    nested: int = 0
    for c in value:
        match c:
            case ',' if nested == 0:
                ret.append(el)
                el = ''
            case '(':
                if nested != 0:
                    el += c
                nested += 1
            case ')':
                nested -= 1
                if nested != 0:
                    el += c
            case _:
                el += c
    ret.append(el)
    return ret


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


_empty = tuple()


class Class(IntEnum):
    UNIVERSAL = 0
    APPLICATION = 0b01_000000
    CONTEXT_SPECIFIC = 0b10_000000
    PRIVATE = 0b11_000000


class Tag:
    ClassNumber: int
    Class: Class
    EncodingReference: None  # implement in future if will need

    def __init__(self,
                 class_number: int,
                 class_: Class = Class.UNIVERSAL,
                 encoding_reference=None):
        self.ClassNumber = class_number
        self.Class = class_

    def __int__(self):
        return self.ClassNumber

    def __str__(self):
        return F"ClassNumber: {self.ClassNumber}"


class Type(ABC):
    """"""
    __slots__ = _empty
    Tag: Tag(UniversalClassTagAssignments.Reserved)
    """8 Tags. Universal class tag. -1 is absense"""
    Size: int = -1
    """length of value in octets. -1 is unrestricted size"""

    @abstractmethod
    def __init__(self, value):
        """"""

    @classmethod
    @abstractmethod
    def from_str(cls, value: str) -> Self:
        """constructor from python string"""

    @abstractmethod
    def __str__(self):
        """string representation"""

    @abstractmethod
    def __len__(self):
        """necessary length of encode in octets"""

    @classmethod
    @abstractmethod
    def get(cls, buf: Buf) -> Self:
        """constructor decoded value from buffer"""

    @abstractmethod
    def put(self, buf: Buf) -> int:
        """put encode definite length value to buffer"""

    @classmethod
    @abstractmethod
    def default(cls) -> Self:
        """default value constructor"""

    def __eq__(self, other):
        """todo: not for all Type maybe"""
        if self.Tag == other.Tag and self.value == other.value:
            return True
        else:
            return False


class WithoutCoding(ABC):
    """for using Types without coding"""
    __slots__ = _empty

    def __len__(self):
        raise RuntimeError(F"no implement <len> in {self.__class__.__name__}")

    @classmethod
    def get(cls, buf: Buf) -> Self:
        raise RuntimeError(F"no implement <get> in {cls.__name__}")

    def put(self, buf: Buf) -> int:
        raise RuntimeError(F"no implement <put> in {self.__class__.__name__}")


class BuiltinType(Type, ABC):
    """17.2"""
    __slots__ = _empty


class UniversalTag(ABC):
    """Rec. ITU-T X.680 (02/2021) Table 1 for consisted Tags"""
    __slots__ = _empty
    Tag: Tag  # todo: why it here


class Simple:
    """Contract. contents and initiating by ByteString"""
    value: ByteString
    __slots__ = _empty

    def __init__(self, value: ByteString):
        self.value = value


class SimpleType(Simple, Type, ABC):
    """Contract. contents and initiating by ByteString"""


class StringDefault(SimpleType, ABC):
    """Mixin for simple string"""
    __slots__ = _empty

    @classmethod
    def default(cls) -> Self:
        return cls(b"")


class Digital(SimpleType, ABC):
    """Contract. abstract's for digital types"""
    __slots__ = _empty

    def __int__(self):
        return int.from_bytes(self.value, signed=self.SIGNED())

    @classmethod
    def from_int(cls, value: int) -> Self:
        """constructor by builtin int"""
        return cls(value.to_bytes(
            length=((value.bit_length() >> 3) + 1) if cls.Size == -1 else cls.Size,
            byteorder="big",
            signed=cls.SIGNED()))

    @classmethod
    @abstractmethod
    def SIGNED(cls) -> bool:
        """return signed flag"""


class Sized(ABC):
    """Contract. """
    __slots__ = _empty
    SIZE: int


Unused = Literal[0, 1, 2, 3, 4, 5, 6, 7]
"""itu-t Rec. X.209 11.2.2"""


class BitStringType(BuiltinType, ABC):
    __slots__ = _empty
    Tag = UniversalClassTagAssignments.BitString

    def __init__(self, value: ByteString):
        self.value = value

    @classmethod
    def from_list(cls, value: list[int]) -> Self:
        return cls.from_str("".join(map(str, value)))

    def __setitem__(self, key: int, value: int | bool):
        tmp: list[int] = self.to_list()
        tmp[key] = int(value)
        new: Self = self.from_list(tmp)
        self.value = new.value

    def inverse(self, index: int):
        """ inverse one bit by index"""
        self[index] = self.to_list()[index] ^ 0b1

    def __lshift__(self, other):
        for i in range(other):
            tmp: list[int] = self.to_list()
            tmp.append(tmp.pop(0))
            self.value = self.from_list(tmp)

    def __rshift__(self, other):
        for i in range(other):
            tmp: list[int] = self.to_list()
            tmp.insert(0, tmp.pop())
            self.value = self.from_list(tmp)

    @classmethod
    def default(cls) -> Self:
        """return sequence with zero length"""
        raise ValueError("not implement")

    def __str__(self):
        """ TODO: copypast cdt FlagMixin"""
        return ''.join(map(str, self.to_list()))

    def __getitem__(self, item) -> int:
        """ get integer(0, 1) from contents by index """
        return self.to_list()[item]

    @abstractmethod
    def to_list(self) -> list[int]:
        """cast to python builtin list"""

    def clear(self):
        """set all bits as 0"""
        for i in range(len(self)):
            self[i] = 0


class BooleanType(Digital, BuiltinType, ABC):
    __slots__ = ("value", )
    Size = 1
    Tag = Tag(UniversalClassTagAssignments.Boolean)

    @classmethod
    def from_str(cls, value: str):
        match value:
            case "0" | "False":
                return cls(b'\x00')
            case "1" | "True":
                return cls(b'\x01')
            case _:
                raise ValueError(F"for {cls.__name__}.from_str got unknown {value=}")

    def __str__(self):
        return str(bool(self))

    def __bool__(self):
        return bool(int(self))

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.value == other.value:
            return True
        else:
            return False

    @classmethod
    def default(cls) -> Self:
        return cls(b'\x01')

    @classmethod
    def from_int(cls, value: int):
        return cls(b'\x00') if value == 0 else cls(b'\x01')

    @classmethod
    def SIGNED(cls) -> bool:
        return False


class CharacterStringType(SimpleType, BuiltinType, ABC):
    """40.1"""


class UTF8String(StringDefault, CharacterStringType, ABC):
    """41 Definition of restricted character string types"""
    Tag = Tag(UniversalClassTagAssignments.UTF8String)
    __slots__ = ("value", )

    def __str__(self):
        self.value.decode("utf-8", errors="strict")

    @classmethod
    def from_str(cls, value: str) -> Self:
        return cls(value.encode("utf-8"))


class VisibleString(StringDefault, CharacterStringType, ABC):
    """41 Definition of restricted character string types"""
    Tag = Tag(UniversalClassTagAssignments.VisibleString)
    __slots__ = ("value", )

    def __str__(self):
        self.value.decode("ascii", errors="strict")

    @classmethod
    def from_str(cls, value: str) -> Self:
        return cls(value.encode("ascii", errors="ignore"))


Identifier: TypeAlias = str

# NamedType: tuple[identifier, type[Type]]


class NamedType(Type, ABC):
    """"""
    def __str__(self):
        return F"{self.__class__.__name__}: {super().__str__()}"


AlternativeTypeList: TypeAlias = Union[NamedType]


class Choice(BuiltinType, ABC):
    """CHOICE"""
    Tag = Tag(UniversalClassTagAssignments.Reserved)
    value: Type
    ELEMENTS: AlternativeTypeList
    __slots__ = _empty

    @abstractmethod
    def __init__(self, value: AlternativeTypeList):
        self.value = value

    def validation(self):
        for el in self.get_elements():
            if isinstance(self.value, el):
                return True
        else:
            raise RuntimeError(F"element {self.value} not for {self.__class__.__name__}")

    def __str__(self):
        return str(self.value)

    @classmethod
    def from_str(cls, value: str) -> Self:
        tag, value2 = value.split(sep=":", maxsplit=1)
        tag: str
        if not tag.isdigit():
            raise ValueError(F"in {value=}, got {tag=}, expected is digit")
        return cls(cls.get_named_type(int(tag)).from_str(value2))

    @classmethod
    def get_type(cls) -> Union:
        return getfullargspec(cls.__init__).annotations["value"]

    @classmethod
    def get_elements(cls) -> tuple[type[Type]]:
        return get_args(cls.get_type())

    @classmethod
    @lru_cache(maxsize=20)
    def get_named_type(cls, tag: int) -> NamedType:
        for n_t in cls.get_elements():
            n_t: NamedType
            if int(n_t.Tag) == tag:
                return n_t
        else:
            raise ValueError(F"in {cls.__name__} got unknown {tag=}, expected {', '.join(str(n_t.Tag) for n_t in cls.get_elements())}")

    def __eq__(self, other: Self):
        if self.value.Tag == other.value.Tag and self.value == other.value:
            return True
        else:
            return False

    @classmethod
    def default(cls) -> Self:
        """choice 0 tag parameter"""
        return cls(cls.get_elements()[0].default())


class IntegerType(Digital, SimpleType, BuiltinType, ABC):
    """ Default value is 0 """
    Tag = Tag(UniversalClassTagAssignments.Integer)
    __slots__ = ("value",)

    @classmethod
    def default(cls) -> Self:
        """return empty string"""
        return cls(b'\x00')

    @classmethod
    def from_str(cls, value: str):
        return cls.from_int(int(value))

    def __str__(self):
        return str(int(self))

    @classmethod
    def SIGNED(cls) -> bool:
        return True

    def __gt__(self, other: Self):
        match other:
            case IntegerType():
                return int(self) > int(other)
            case _:
                raise TypeError(F'Compare type is {other.__class__}, expected {self.__class__.__name__}')

    def __hash__(self):
        return int(self)

    def __eq__(self, other: Self):
        return int(self) == int(other)


@dataclass
class NamedNumber:
    """ITU-T Rec. X.680 19.1"""
    identifier: Identifier
    number: int


class EnumeratedType(SimpleType, BuiltinType, ABC):  # todo: make common with Digital
    """Default value is 0"""
    Tag = Tag(UniversalClassTagAssignments.Enumerated)
    __slots__ = ("value",)
    ENUMERATIONS: tuple[NamedNumber]

    def __int__(self):
        return int.from_bytes(self.value)

    @classmethod
    def from_int(cls, value: int) -> Self:
        """constructor by builtin int"""
        return cls(value.to_bytes(
            length=((value.bit_length() >> 3) + 1) if cls.Size == -1 else cls.Size,
            byteorder="big"))

    @classmethod
    def default(cls) -> Self:
        """return empty string"""
        return cls(b'\x00')

    @classmethod
    def from_str(cls, value: str):
        return cls.from_int(int(value))

    def __str__(self):
        n = int(self)
        for n_n in self.ENUMERATIONS:
            if n == n_n.number:
                return F"({n}){n_n.identifier}"
        else:
            return str(n)

    def __gt__(self, other: Self):
        match other:
            case EnumeratedType():
                return int(self) > int(other)
            case _:
                raise TypeError(F'Compare type is {other.__class__}, expected {self.__class__.__name__}')

    def __hash__(self):
        return int(self)

    def __eq__(self, other: Self):
        return int(self) == int(other)


class NullType(BuiltinType, ABC):
    Size = 0
    Tag = Tag(UniversalClassTagAssignments.Null)
    __slots__ = _empty

    def __init__(self, value: ByteString | None = None):
        """nothing do it"""

    @classmethod
    def from_str(cls, value: str):
        return cls()

    def __str__(self):
        return self.__class__.__name__


class OctetStringType(StringDefault, SimpleType, BuiltinType, ABC):
    """ An ordered sequence of octets (8 bit bytes) """
    Tag = Tag(UniversalClassTagAssignments.OctetString)
    __slots__ = ("value",)

    @classmethod
    def from_str(cls, value: str) -> Self:
        """ input as hex code """
        return cls(bytes.fromhex(value))

    def __str__(self):
        return self.value.hex(' ')


class ComponentType(Type, ABC):
    """"""


class Optional(ComponentType, ABC):
    """OPTIONAL"""
    __slots__ = _empty

    def __init__(self, value: ByteString):
        self.value = value

    def __str__(self):
        if self.value == b'':
            return "OPTIONAL"
        else:
            return super().__str__()

    @classmethod
    def default(cls) -> Self:
        return cls(b'')

    @classmethod
    def from_str(cls, value: str) -> Self:
        if value == "":
            return cls(b'')
        else:
            return super().from_str(value)


ComponentTypeList: TypeAlias = tuple[Type | ComponentType, ...]


class AnnotationGetterMixin(ABC):
    """use annotation for init elements"""
    value: Any
    @property
    def _get0(self):
        return self.value[0]

    @property
    def _get1(self):
        return self.value[1]

    @property
    def _get2(self):
        return self.value[2]

    @property
    def _get3(self):
        return self.value[3]

    @property
    def _get4(self):
        return self.value[4]

    @property
    def _get5(self):
        return self.value[5]

    @property
    def _get6(self):
        return self.value[6]

    @property
    def _get7(self):
        return self.value[7]

    @property
    def _get8(self):
        return self.value[8]

    @property
    def _get9(self):
        return self.value[9]

    def __init_subclass__(cls, **kwargs):
        """link attributes with functions"""
        if len(cls.__annotations__) != 0:
            for (name, type_), f in zip(cls.__annotations__.items(),
                                        (cls._get0, cls._get1, cls._get2, cls._get3, cls._get4, cls._get5, cls._get6, cls._get7, cls._get8, cls._get9)):
                setattr(cls, name, f)

    @classmethod
    def default(cls) -> Self:
        return cls(tuple(el.default() for el in cls.__annotations__.values()))

    @classmethod
    def from_str(cls, value: str) -> Self:
        values = get_values(value)
        if len(values) == len(cls.__annotations__):
            return cls(tuple(el.from_str(val) for el, val in zip(cls.__annotations__.values(), values)))
        else:
            raise ValueError(F"{cls} from {value=} got {len(values)} elements, expected {len(cls.__annotations__)}")


class SequenceType(AnnotationGetterMixin, BuiltinType, ABC):
    """use annotation for init elements of sequence"""
    Tag = Tag(UniversalClassTagAssignments.Sequence)
    __slots__ = _empty
    value: ComponentTypeList

    @abstractmethod
    def __init__(self, value: ComponentTypeList):
        self.value = value

    def __str__(self):
        return F"{SequenceType.__name__}[{len(self.__annotations__)}]"

    @classmethod
    @abstractmethod
    def from_elements(cls, **kwargs) -> Self:
        """create instance by elements"""


class SequenceOfType(BuiltinType, ABC):
    """SEQUENCE OF"""
    Type: type[Type]
    Tag = Tag(UniversalClassTagAssignments.SequenceOf)
    __slots__ = ("value",)
    value: tuple[Type, ...]

    @abstractmethod
    def __init__(self, value: tuple[Type, ...]):
        self.value = value

    def __str__(self):
        return F"{self.Type.__name__}[{len(self.value)}]"

    @classmethod
    def from_str(cls, value: str) -> Self:
        return cls(tuple(cls.Type.from_str(val) for val in value.replace(' ', '').split(";")))

    @classmethod
    def default(cls) -> Self:
        """return sequence with zero length"""
        return cls(tuple())


class PrefixedType(BuiltinType, ABC):
    __slots__ = tuple()


class TaggedType(PrefixedType, ABC):
    Tag: Tag
    __slots__ = _empty



class IMPLICIT(TaggedType, ABC):
    """Simple change Tag to new. see 31.2.1"""
    Tag: Tag
    __slots__ = _empty  # set slots


class EXPLICIT(TaggedType, ABC):
    """see 31.2.1"""
    Type: type[Type]  # consist Type into
    __slots__ = ("value", )

    def __init__(self, value: Type):
        self.value = value

    @classmethod
    def from_str(cls, value: str) -> Self:
        return cls(cls.Type.from_str(value))

    def __str__(self):
        return str(self.value)

    @classmethod
    def default(cls) -> Self:
        return cls(cls.Type.default())


class NotImplement:
    """special class for todo in future"""


class ElementSetSpecs:
    """50.1"""


SubtypeConstraint = ElementSetSpecs
"""49.7"""


GeneralConstraint = NotImplement


ConstraintSpec: TypeAlias = SubtypeConstraint | GeneralConstraint


@dataclass
class Constraint:
    """49.6"""
    constraint_spec: ConstraintSpec
    ExceptionSpec: None


class ConstrainedType(Type, ABC):
    """49 Constrained types"""
    constraint: Constraint
    type: type[Type]
    __slots__ = _empty
    value: Type

    def __init__(self, value: Type):
        self.value = value
