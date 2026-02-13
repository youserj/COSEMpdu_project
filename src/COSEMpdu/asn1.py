"""Rec. ITU-T X.680 (02/2021)"""
from functools import lru_cache
from inspect import getfullargspec
from typing import Never, Self, TypeAlias, Literal, Any, Union, get_args, ClassVar, Protocol, runtime_checkable
from dataclasses import dataclass
from .byte_buffer import ByteBuffer as Buf


ByteString: TypeAlias = bytes | memoryview

def get_values(value: str) -> list[str]:
    """parsing sequence string"""
    ret: list[str] = []
    el: str = ""
    nested: int = 0
    for c in value:
        match c:
            case "," if nested == 0:
                ret.append(el)
                el = ""
            case "(":
                if nested != 0:
                    el += c
                nested += 1
            case ")":
                nested -= 1
                if nested != 0:
                    el += c
            case _:
                el += c
    ret.append(el)
    return ret


Transcript: TypeAlias = str | list["Transcript"]


@runtime_checkable
class Type(Protocol):
    """"""
    Tag: ClassVar["Tag"]
    """8 Tags. Universal class tag. -1 is absense"""

    @classmethod
    def parse(cls, value: Transcript) -> Self: ...

    def __str__(self) -> str: ...

    def __len__(self) -> int:
        """necessary length of encode in octets"""
        ...

    @classmethod
    def get(cls, buf: Buf) -> Self:
        """constructor decoded value from buffer, for concrete coders"""
        ...

    def put(self, buf: Buf) -> int:
        """put encode definite length value to buffer, for concrete coders"""
        ...


class BuiltinType(Type, Protocol):
    """16.2"""

class Simple(Type, Protocol):
    """Contract. contents and initiating by ByteString"""
    value: ByteString


@dataclass
class SimpleType(Simple, Protocol):
    """Contract. contents and initiating by ByteString"""


class Digital(SimpleType, Protocol):
    """Contract. abstract's for digital types"""

    def __int__(self) -> int:
        return int.from_bytes(self.value, signed=self.SIGNED())

    @classmethod
    def from_int(cls, value: int) -> Self:
        """constructor by builtin int"""
        return cls(value.to_bytes(
            length=((value.bit_length() >> 3) + 1) if cls.Size == -1 else cls.Size,
            byteorder="big",
            signed=cls.SIGNED()))

    @classmethod
    def SIGNED(cls) -> bool:
        """return signed flag"""
        ...


Unused = Literal[0, 1, 2, 3, 4, 5, 6, 7]
"""itu-t Rec. X.209 11.2.2"""


class BitStringType(BuiltinType, Protocol):
    Tag: ClassVar["Tag"] = Tag(UniversalClassTagAssignments.BitString)
    value: ByteString

    @classmethod
    def from_list(cls, value: list[int]) -> Self:
        return cls.parse("".join(map(str, value)))

    def __setitem__(self, key: int, value: int | bool) -> None:
        tmp: list[int] = self.to_list()
        tmp[key] = int(value)
        new: BitStringType = self.from_list(tmp)
        self.value = new.value

    def inverse(self, index: int) -> None:
        """ inverse one bit by index"""
        self[index] = self.to_list()[index] ^ 0b1

    def __lshift__(self, other: int) -> None:
        for _ in range(other):
            tmp: list[int] = self.to_list()
            tmp.append(tmp.pop(0))
            self.value = self.from_list(tmp).value

    def __rshift__(self, other: int) -> None:
        for _ in range(other):
            tmp: list[int] = self.to_list()
            tmp.insert(0, tmp.pop())
            self.value = self.from_list(tmp).value

    @classmethod
    def default(cls) -> Self:
        """return sequence with zero length"""
        raise ValueError("not implement")

    def __str__(self) -> str:
        """ TODO: copypast cdt FlagMixin"""
        return "".join(map(str, self.to_list()))

    def __getitem__(self, item: int) -> int:
        """ get integer(0, 1) from contents by index """
        return self.to_list()[item]

    def to_list(self) -> list[int]:
        """cast to python builtin list"""

    def clear(self) -> None:
        """set all bits as 0"""
        for i in range(len(self)):
            self[i] = 0


class BooleanType(Digital, BuiltinType, Protocol):
    Size: ClassVar[int] = 1
    Tag: ClassVar["Tag"] = Tag(UniversalClassTagAssignments.Boolean)

    @classmethod
    def parse(cls, value: str) -> Self:
        match value:
            case "0" | "False":
                return cls(b"\x00")
            case "1" | "True":
                return cls(b"\x01")
            case _:
                raise ValueError(F"for {cls.__name__}.from_str got unknown {value=}")

    def __str__(self) -> str:
        return str(bool(self))

    def __bool__(self) -> bool:
        return bool(int(self))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__) and self.value == other.value:
            return True
        else:
            return False

    @classmethod
    def default(cls) -> Self:
        return cls(b"\x01")

    @classmethod
    def from_int(cls, value: int) -> Self:
        return cls(b"\x00") if value == 0 else cls(b"\x01")

    @classmethod
    def SIGNED(cls) -> bool:
        return False


class CharacterStringType(SimpleType, BuiltinType, Protocol):
    """40.1"""


class UTF8String(CharacterStringType, Protocol):
    """41 Definition of restricted character string types"""
    Tag: ClassVar["Tag"] = Tag(UniversalClassTagAssignments.UTF8String)

    def __str__(self) -> str:
        return bytes(self.value).decode("utf-8", errors="strict")

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(value.encode("utf-8"))


class VisibleString(CharacterStringType, Protocol):
    """41 Definition of restricted character string types"""
    Tag: ClassVar["Tag"] = Tag(UniversalClassTagAssignments.VisibleString)

    def __str__(self) -> str:
        return bytes(self.value).decode("ascii", errors="strict")

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(value.encode("ascii", errors="ignore"))


Identifier: TypeAlias = str

# NamedType: tuple[identifier, type[Type]]


class NamedType(Type, Protocol):
    """"""
    def __str__(self) -> str:
        return F"{self.__class__.__name__}"


AlternativeTypeList: TypeAlias = Union[NamedType]


class ChoiceType(BuiltinType, Protocol):
    """CHOICE"""
    Tag: ClassVar["Tag"] = Tag(UniversalClassTagAssignments.Reserved)
    value: Type
    ELEMENTS: AlternativeTypeList

    def __init__(self, value: AlternativeTypeList):
        self.value = value

    def validation(self) -> bool:
        for el in self.get_elements():
            if isinstance(self.value, el):
                return True
        else:
            raise RuntimeError(F"element {self.value} not for {self.__class__.__name__}")

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def parse(cls, value: str) -> Self:
        tag, value2 = value.split(sep=":", maxsplit=1)
        if not tag.isdigit():
            raise ValueError(F"in {value=}, got {tag=}, expected is digit")
        return cls(cls.get_named_type(int(tag)).parse(value2))

    @classmethod
    def get_type(cls) -> Union:
        return getfullargspec(cls.__init__).annotations["value"]

    @classmethod
    def get_elements(cls) -> tuple[type[NamedType], ...]:
        return get_args(cls.get_type())

    @classmethod
    @lru_cache(maxsize=20)
    def get_named_type(cls, tag: int) -> type[NamedType]:
        for n_t in cls.get_elements():
            if int(n_t.Tag) == tag:
                return n_t
        else:
            raise ValueError(f"in {cls.__name__} got unknown {tag=}, expected {", ".join(str(n_t.Tag) for n_t in cls.get_elements())}")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Type):
            if (
                self.value.Tag == other.value.Tag 
                and self.value == other.value
            ):
                return True
            else:
                return False
        else:
            raise NotImplementedError

    @classmethod
    def default(cls) -> Self:
        """choice 0 tag parameter"""
        return cls(cls.get_elements()[0].default())


@runtime_checkable
class IntegerType(Digital, SimpleType, BuiltinType, Protocol):
    """ Default value is 0 """
    Tag: ClassVar["Tag"] = Tag(UniversalClassTagAssignments.Integer)

    @classmethod
    def default(cls) -> Self:
        """return empty string"""
        return cls(b"\x00")

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls.from_int(int(value))

    def __str__(self) -> str:
        return str(int(self))

    @classmethod
    def SIGNED(cls) -> bool:
        return True

    def __gt__(self, other: Self) -> bool:
        match other:
            case IntegerType():
                return int(self) > int(other)
            case _:
                raise TypeError(F"Compare type is {other.__class__}, expected {self.__class__.__name__}")

    def __hash__(self) -> int:
        return int(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, IntegerType):
            return int(self) == int(other)
        else:
            raise NotImplementedError


@dataclass
class NamedNumber:
    """ITU-T Rec. X.680 19.1"""
    identifier: Identifier
    number: int


@runtime_checkable
class EnumeratedType(SimpleType, BuiltinType, Protocol):  # todo: make common with Digital
    """Default value is 0"""
    Tag: ClassVar["Tag"] = Tag(UniversalClassTagAssignments.Enumerated)
    ENUMERATIONS: tuple[NamedNumber]

    def __int__(self) -> int:
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
        return cls(b"\x00")

    @classmethod
    def parse(cls, value: str) -> str:
        return cls.from_int(int(value))

    def __str__(self) -> str:
        n = int(self)
        for n_n in self.ENUMERATIONS:
            if n == n_n.number:
                return F"({n}){n_n.identifier}"
        else:
            return str(n)

    def __gt__(self, other: Self) -> bool:
        match other:
            case EnumeratedType():
                return int(self) > int(other)
            case _:
                raise TypeError(F"Compare type is {other.__class__}, expected {self.__class__.__name__}")

    def __hash__(self) -> int:
        return int(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EnumeratedType):
            return int(self) == int(other)
        else:
            raise NotImplementedError


class NullType(BuiltinType, Protocol):
    Size = 0
    Tag: ClassVar["Tag"] = Tag(UniversalClassTagAssignments.Null)

    def __init__(self, value: ByteString | None = None) -> None:
        """nothing do it"""

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls()

    def __str__(self) -> str:
        return self.__class__.__name__


class OctetStringType(SimpleType, BuiltinType, Protocol):
    """ An ordered sequence of octets (8 bit bytes) """
    Tag: ClassVar["Tag"] = Tag(UniversalClassTagAssignments.OctetString)

    @classmethod
    def parse(cls, value: str) -> Self:
        """ input as hex code """
        return cls(bytes.fromhex(value))

    def __str__(self) -> str:
        return self.value.hex(" ")


class ComponentType(Type, Protocol):
    """"""


class Optional(ComponentType, Protocol):
    """OPTIONAL"""

    def __init__(self, value: ByteString) -> None:
        self.value = value

    def __str__(self) -> str:
        if self.value == b"":
            return "OPTIONAL"
        else:
            return super().__str__()

    @classmethod
    def default(cls) -> Self:
        return cls(b"")

    @classmethod
    def parse(cls, value: str) -> Self:
        if value == "":
            return cls(b"")
        else:
            return super().parse(value)


ComponentTypeList: TypeAlias = tuple[Type | ComponentType, ...]


class AnnotationGetterMixin(Protocol):
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


class SequenceType(AnnotationGetterMixin, BuiltinType, Protocol):
    """use annotation for init elements of sequence"""
    Tag: ClassVar["Tag"] = Tag(UniversalClassTagAssignments.Sequence)
    value: ComponentTypeList

    def __init__(self, value: ComponentTypeList):
        self.value = value

    def __str__(self):
        return F"{SequenceType.__name__}[{len(self.__annotations__)}]"

    @classmethod
    def from_elements(cls, **kwargs) -> Self:
        """create instance by elements"""


class SequenceOfType(BuiltinType, Protocol):
    """SEQUENCE OF"""
    Type: type[Type]
    Tag: ClassVar["Tag"] = Tag(UniversalClassTagAssignments.SequenceOf)
    value: tuple[Type, ...]

    def __init__(self, value: tuple[Type, ...]) -> None:
        self.value = value

    def __str__(self) -> str:
        return F"{self.Type.__name__}[{len(self.value)}]"

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(tuple(cls.Type.parse(val) for val in value.replace(" ", "").split(";")))
    @classmethod
    def default(cls) -> Self:
        """return sequence with zero length"""
        return cls(tuple())


class PrefixedType(BuiltinType, Protocol):
    ...


class TaggedType(PrefixedType, Protocol):
    Tag: ClassVar["Tag"]



class IMPLICIT(TaggedType, Protocol):
    """Simple change Tag to new. see 31.2.1"""
    Tag: ClassVar["Tag"]


class EXPLICIT(TaggedType, Protocol):
    """see 31.2.1"""
    Type: type["Type"]  # consist Type into

    def __init__(self, value: "Type") -> None:
        self.value = value

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(cls.Type.parse(value))

    def __str__(self) -> str:
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


class ConstrainedType(Type, Protocol):
    """49 Constrained types"""
    constraint: Constraint
    type: type[Type]
    value: Type

    def __init__(self, value: Type):
        self.value = value
