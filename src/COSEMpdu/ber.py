from typing import Self
from abc import ABC
from . import asn1, x690
from .byte_buffer import ByteBuffer as Buf, ByteBuffer

_value = ("value",)
_empty = asn1._empty


class BitStringType(asn1.BitStringType):
    __slots__ = _value
    Tag = x690.Tag(asn1.UniversalClassTagAssignments.BitString)

    def __len__(self):
        return 1 + len(x690.Length(len(self.value))) + len(self.value)

    @classmethod
    def get(cls, buf: Buf) -> Self:
        if (tag := x690.Tag.get(buf)) == cls.Tag:
            return cls(buf.read(x690.Length.get(buf).value))
        else:
            raise ValueError(F"for {cls.__name__} got {tag}, expected {cls.Tag}")

    def put(self, buf: Buf) -> int:
        return self.Tag.put(buf) + x690.Length(len(self.value)).put(buf) + buf.write(self.value)

    @classmethod
    def from_str(cls, value: str) -> Self:
        l: int = len(value)
        unused: asn1.Unused = (8 - l) % 8
        value = value + '0' * unused
        return cls(unused.to_bytes(1, "big") + bytes((int(value[count:(count + 8)], base=2) for count in range(0, l, 8))))

    def to_list(self) -> list[int]:
        ret = list()
        for byte_ in self.value[1:]:
            ret.extend([(byte_ >> it) & 0b00000001 for it in range(7, -1, -1)])
        return ret if self.unused == 0 else ret[:-self.unused]

    @property
    def unused(self) -> int:
        return self.value[0]


# class TaggedType(asn1.TaggedType):
#     def put(self, buf: ByteBuffer) -> int:
#         ret = buf.put_uint8(self.Tag.ClassNumber)
#         ret += x690.Length.put_int(buf, len(self.value))  # PROBLEM: decide len value each time
#         ret += self.value.put(buf)
#         return ret


class Implicit(asn1.IMPLICIT, ABC):
    Tag: x690.Tag
    __slots__ = _empty
