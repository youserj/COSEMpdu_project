from abc import ABC, abstractmethod
from typing import Self, ByteString
from struct import pack, Struct
from math import log, ceil
from . import asn1, x690, byte_buffer, ber
from .byte_buffer import ByteBuffer as Buf

_empty = asn1.NullType.__slots__
_value = asn1._value


def create_buf(value: asn1.Type) -> Buf:
    buf: Buf = Buf.allocate(len(value))
    value.put(buf)
    buf.set_pos(0)
    return buf


class Tag(x690.ComponentEDV, asn1.Tag):
    """IEC 61334-6 2000 6.7 Tagged types"""
    def __len__(self):
        return 1

    @classmethod
    def get(cls, buf: Buf) -> Self:
        """todo: add constructed handle"""
        return cls(class_number=buf.get_uint8())

    def put(self, buf: Buf) -> int:
        return buf.put_uint8(self.ClassNumber)

    def __eq__(self, other: Self):
        if self.ClassNumber == other.ClassNumber:
            return True
        else:
            return False


class _StringCoder(asn1.SimpleType, ABC):
    def __len__(self) -> int:
        return len(x690.Length(len(self.value))) + len(self.value)

    @classmethod
    def get(cls, buf: Buf) -> Self:
        return cls(buf.read(x690.Length.get(buf).value))

    def put(self, buf: Buf) -> int:
        ret: int = x690.Length(len(self.value)).put(buf)
        return ret + buf.write(self.value)


class BitStringType(asn1.BitStringType):
    __slots__ = _value
    value: tuple[x690.Length, ByteString]

    def __init__(self, value: tuple[x690.Length, ByteString]):
        self.value = value

    def __len__(self) -> int:
        return sum(map(len, self.value))

    @classmethod
    def from_str(cls, value: str) -> Self:
        """override asn.1"""
        l = x690.Length(len(value))
        value = value + '0' * ((8 - l.value) % 8)
        return cls((l, bytes((int(value[count:(count + 8)], base=2) for count in range(0, l.value, 8)))))

    @classmethod
    def get(cls, buf: Buf) -> Self:
        l: x690.Length = x690.Length.get(buf)
        return cls((l, buf.read(ceil(l.value / 8))))

    def put(self, buf: Buf) -> int:
        return self.value[0].put(buf) + buf.write(self.value[1])

    def to_list(self) -> list[int]:
        ret = list()
        for byte_ in self.content:
            ret.extend([(byte_ >> it) & 0b00000001 for it in range(7, -1, -1)])
        return ret[:self.length.value]

    @property
    def length(self) -> x690.Length:
        return self.value[0]

    @property
    def content(self) -> ByteString:
        return self.value[1]


class BooleanType(asn1.BooleanType):
    __slots__ = _value

    def __len__(self) -> int:
        return 1

    @classmethod
    def get(cls, buf: Buf) -> Self:
        return cls(buf.read(cls.Size))

    def put(self, buf: Buf) -> int:
        return buf.write(self.value)


FALSE = BooleanType(b'\x00')
"""allocated FALSE"""
TRUE = BooleanType(b'\x01')
"""allocated TRUE"""


class UTF8String(_StringCoder, asn1.UTF8String):
    __slots__ = _value


class VisibleString(_StringCoder, asn1.VisibleString):
    __slots__ = _value


class Choice(asn1.Choice, ABC):
    ELEMENTS: asn1.AlternativeTypeList
    __slots__ = _value

    def __len__(self):
        if self.Tag.ClassNumber == asn1.UniversalClassTagAssignments.Reserved:
            return len(self.value)
        else:
            return 1 + len(self.value)

    @classmethod
    def get(cls, buf: Buf) -> asn1.Type:  # todo: make more restricted annotation
        n_t = cls.get_named_type(buf.get_uint8())
        buf.set_pos(buf.get_pos() - 1)  # todo: make better - one more read buffer tag
        # return cls(n_t.get(buf))
        return n_t.get(buf)

    def put(self, buf: Buf) -> int:
        return self.value.put(buf)

    # def __bytes__(self):
    #     buf = Buf.allocate(len(self))
    #     self.put(buf)
    #     return bytes(buf)


class IntegerType(_StringCoder, asn1.IntegerType):
    __slots__ = _value


class NullType(asn1.NullType):
    __slots__ = _empty

    def __len__(self):
        return 0

    @classmethod
    def from_str(cls, value: str):
        return cls()

    @classmethod
    def get(cls, buf: Buf) -> Self:
        return cls()

    def put(self, buf: Buf) -> int:
        """not carry info"""
        return 0

    @classmethod
    def default(cls) -> Self:
        return cls()


class OctetStringType(_StringCoder, asn1.OctetStringType):
    __slots__ = _value


class Optional(asn1.Optional):
    __slots__ = _empty

    def __len__(self):
        return 1 + super().__len__()

    @classmethod
    def get(cls, buf: Buf) -> asn1.Type:
        if BooleanType.get(buf) == FALSE:
            return cls(b'')
        else:
            return super().get(buf)

    def put(self, buf: Buf) -> int:
        if self.value == b'':
            return FALSE.put(buf)
        else:
            return TRUE.put(buf) + super().put(buf)


def get_optional(t: type[asn1.Type]) -> type[Optional]:
    class Optional_(Optional, t):
        """"""

    return Optional_


class SequenceType(asn1.SequenceType, ABC):
    __slots__ = _empty
    value: asn1.ComponentTypeList

    def __len__(self) -> int:
        return sum((len(it) for it in self.value))

    @classmethod
    def get(cls, buf: Buf) -> Self:
        ret = list()
        for el in cls.__annotations__.values():
            el: asn1.Type
            ret.append(el.get(buf))
        return cls(tuple(ret))

    def put(self, buf: Buf) -> int:
        """put to buffer"""
        return sum(val.put(buf) for val in self.value)


class SequenceOfType(asn1.SequenceOfType, ABC):
    Type: type[asn1.Type]
    __slots__ = _value

    def __len__(self):
        return len(x690.Length(len(self.value))) + sum(map(len, self.value))

    @classmethod
    def get(cls, buf: Buf) -> Self:
        return cls(tuple(cls.Type.get(buf) for _ in range(x690.Length.get(buf).value)))

    def put(self, buf: Buf) -> int:
        ret: int = x690.Length(len(self.value)).put(buf)
        return ret + sum((el.put(buf) for el in self.value))


def get_sequence_of(t: type[asn1.Type]) -> type[SequenceOfType]:
    class SequenceOf(SequenceOfType):
        Type = t

        def __init__(self, value: tuple[t, ...]):
            super().__init__(value)

    return SequenceOf


class SizedCoder(asn1.SimpleType, ABC):
    """coder for Types with Size != -1 """
    __slots__ = _empty

    def validate(self):
        if self.Size != len(self.value):
            raise ValueError(F"{self.__class__.__name__} has value with length {len(self.value)}, expected {self.Size}")

    def __len__(self) -> int:
        return self.Size

    @classmethod
    def get(cls, buf: Buf) -> Self:
        return cls(buf.read(cls.Size))

    def put(self, buf: Buf) -> int:
        return buf.write(self.value)


class EnumeratedType(SizedCoder, asn1.EnumeratedType):
    Size = 1
    __slots__ = _value


_tag2_buf = byte_buffer.ByteBuffer.allocate(1000)
"""used as temp buffer for putting value with EXPLICIT TaggedType"""


class EXPLICIT(asn1.EXPLICIT, ABC):  # todo: make ALL
    __slots__ = _empty

    def put(self, buf: Buf) -> int:
        """override put"""
        ret = buf.put_uint8(self.Tag.ClassNumber)

        # variant(use additional buffer)
        # _tag2_buf.set_pos(0)
        # l1 = self.value.put(_tag2_buf)
        # ret += buf.put_len(l1)
        # ret += buf.write(_tag2_buf.buf[:l1], l1)

        # variant 2(readable and slow)
        ret += x690.Length(len(self.value)).put(buf)  # PROBLEM: decide len value each time
        ret += self.value.put(buf)

        # variant 3(right shift buffer)
        # ...

        return ret


class Implicit(asn1.IMPLICIT, ABC):
    """IEC 61334-6 5.1 The Identifier field"""
    Tag: Tag

    def __str__(self):
        return F"[{self.Tag.ClassNumber}]{super().__str__()}"

    def __len__(self):
        return len(self.Tag) + super().__len__()

    @classmethod
    def get(cls, buf: Buf) -> Self:
        if (tag := cls.Tag.get(buf)) != cls.Tag:
            raise ValueError(F"got {tag}, expected: {cls.Tag}")
        else:
            return super().get(buf)

    def put(self, buf: Buf) -> int:
        return self.Tag.put(buf) + super().put(buf)


# todo: now only for EnumeratedType
def get_implicit(tag: int, t: type[asn1.BuiltinType]) -> type[Implicit]:
    class Implicit_(asn1.NamedType, Implicit, t):
        Tag = Tag(tag)

    return Implicit_


# class IMPLICIT(asn1.IMPLICIT, ABC):
#     Tag: asn1.Tag
#     Type = asn1.Type
#     __slots__ = _empty
#
#     def __len__(self):
#         return 1 + len(self.value)
#
#     def put(self, buf: Buf) -> int:
#         ret = buf.put_uint8(self.Tag.ClassNumber)
#         return ret + self.value.put(buf)
#
#     @classmethod
#     def get(cls, buf: Buf) -> Self:
#         if (tag := buf.get_uint8())==cls.Tag.ClassNumber:
#             return cls(cls.Type.get(buf))
#         else:
#             raise ValueError(F"for {cls.__name__} got {tag=}, expected {cls.Tag.ClassNumber}")


class OptionalOctetStringType(Optional, OctetStringType):
    __slots__ = _value
