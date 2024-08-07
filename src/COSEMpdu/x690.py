from math import log
from abc import ABC, abstractmethod
from typing import Self
from . import asn1
from .byte_buffer import ByteBuffer
from struct import Struct

_length1 = Struct("> B B")
_length2 = Struct("> B H")
_length4 = Struct("> B L")


class ComponentEDV(ABC):
    """Encoding data value component"""

    @abstractmethod
    def __len__(self):
        """necessary length of encode in octets"""

    @classmethod
    @abstractmethod
    def get(cls, buf: ByteBuffer) -> Self:
        """constructor decoded value from buffer"""

    @abstractmethod
    def put(self, buf: ByteBuffer) -> int:
        """put encode definite length value to buffer"""


class Length(ComponentEDV):
    __slots__ = ("value",)
    value: int

    def __init__(self, value: int):
        self.value = value

    def __len__(self):
        """return of necessary length for allocating in buffer"""
        if self.value < 0x80:
            return 1
        elif self.value < 0x1_00:
            return 2
        elif self.value < 0x1_00_00:
            return 3
        elif self.value < 0x1_00_00_00_00:
            return 5
        else:
            amount = int(log(self.value, 256)) + 1
            return 1 + amount

    @classmethod
    def get(cls, buf: ByteBuffer) -> Self:
        """
        return common element length from buffer, with increasing by decoding according to 8.1.3 Length octets ITU-T Rec. X.690 (07/2002)
        \n0...: definite mode
        \n-1: indefinite mode
        """
        define_length = buf.get_uint8()
        if define_length & 0b10000000:
            define_length &= 0b0_1111111
            if define_length == 0b0_1111111:
                return cls(-1)
            return cls(buf.get_uint(define_length))
        else:
            return cls(define_length)

    def put(self, buf: ByteBuffer) -> int:
        """ put length to buffer, increase position"""
        if self.value < 0x80:
            return buf.put_uint8(self.value)
        elif self.value < 0x1_00:
            _length1.pack_into(buf.buf, 0,
                               0x81, self.value)
            return 2
        elif self.value < 0x1_00_00:
            _length2.pack_into(buf.buf, 0,
                               0x82, self.value)
            return 3
        elif self.value < 0x1_00_00_00_00:
            _length4.pack_into(buf.buf, 0,
                               0x84, self.value)
            return 5
        else:
            amount = int(log(self.value, 256)) + 1
            ret: int = buf.put_uint8(0x80 + amount)
            length: bytes = self.value.to_bytes(amount, byteorder='big')
            return ret + buf.write(length)

    def __str__(self):
        return str(self.value)


class Tag(ComponentEDV, asn1.Tag):
    def __len__(self):
        if self.ClassNumber < 0b11111:
            return 1
        else:
            ret = 1
            value = self.ClassNumber
            while value:
                value >>= 7
                ret += 1
            return ret

    @classmethod
    def get(cls, buf: ByteBuffer) -> Self:
        """todo: add constructed handle"""
        value = buf.get_uint8()
        class_ = asn1.Class(value & 0b11_000000)
        class_number = value & 0b0001_1111
        if class_number == 0b0001_1111:
            class_number = 0
            while True:
                class_number <<= 7
                value = buf.get_uint8()
                class_number += value & 0b0111_1111
                if (value & 0b1000_0000) == 0:
                    break
        return cls(
            class_number=class_number,
            class_=class_)

    def put(self, buf: ByteBuffer) -> int:
        if self.ClassNumber < 0b0001_1111:
            return buf.put_uint8(self.Class + self.ClassNumber)
        else:
            ret = buf.put_uint8(self.Class | 0b0001_1111)
            value = self.ClassNumber
            tmp = list()
            while value:
                tmp.append(value & 0b0111_1111)
                value >>= 7
            for it in range(len(tmp)-1,0,-1):
                tmp[it] = tmp[it] | 0b1000_0000
            while tmp:
                ret += buf.put_uint8(tmp.pop())
            return ret

    def __str__(self):
        return F"Class: {self.Class}, ClassNumber: {self.ClassNumber}"

    def __eq__(self, other: Self):
        if self.ClassNumber == other.ClassNumber and self.Class == other.Class:
            return True
        else:
            return False
