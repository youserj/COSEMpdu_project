from dataclasses import dataclass
from typing import Self, Protocol
from StructResult.result import ValueOrError, Error, Fallible, OK
from . import x680
from .byte_buffer import ByteBuffer, ReadableByteBuffer


class TagError(Exception): ...


class ED(Protocol):
    """
    Generic protocol interface for encoding/decoding (Encode/Decode).

    Not tied to any specific wire format — implementations may or may not
    use TLV structure.

    Implementations MUST:
    - In `get()`: decode from buffer and return the decoded instance.
    - In `put()`: encode to buffer and return the number of bytes written.
    """
    @classmethod
    def get(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode from buffer and return the decoded instance.
        """
        ...

    def put(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode to buffer and return the number of bytes written.
        """
        ...


class EDTLV(ED, Protocol):
    """
    Protocol interface for BER/X.690 TLV (Tag-Length-Value) encoding/decoding.

    Adds Length+Contents (LC) methods for cases where the tag is already
    known/validated and only Length + Contents need to be processed.

    - `get()` / `put()`: inherited from `ED`, operate on full TLV.
    - `get_lc()` / `put_lc()`: decode/encode Length + Contents without the tag.
    """

    def put(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode with full TLV (Tag + Length + Contents).
        Returns number of bytes written.
        """
        ...

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode Length + Contents without the tag.
        Use when the tag is already known/validated.
        """
        ...

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode Length + Contents without the tag.
        Use when the tag is already known/validated.
        """
        ...


@dataclass
class Length(ED):
    """
    Length component (X.690 §8.1.3)
    value:
        - >=0: definite length (octets)
        - -1: indefinite form (EOC terminated)
    """
    value: int  # -1 = indefinite form

    def __post_init__(self) -> None:
        if self.value < -1:
            raise ValueError(f"Invalid length value: {self.value}")

    def __len__(self) -> int:
        """Octets required for encoding (X.690 §8.1.3.4, §8.1.3.6)"""
        if self.value == -1:  # Indefinite form
            return 1
        if self.value < 0x80:  # Short definite form
            return 1
        # Long definite form: 1 (length-of-length) + minimal value bytes
        num_value_bytes = (self.value.bit_length() + 7) // 8
        return 1 + num_value_bytes

    @classmethod
    def get(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode length per X.690 §8.1.3
        Returns:
            Length(n) for definite form (n >= 0)
            Length(-1) for indefinite form
        """
        if isinstance(first := buf.get_u8(), Error):
            return first
        if not (first & 0x80):  # Short form: bits 7-1 = length
            return cls(first)
        length = first & 0x7F
        if length == 0:  # Indefinite form marker (0x80)
            return cls(-1)
        # Long definite form: read "length_of_length" bytes as big-endian integer
        if isinstance(value := buf.get_uint(length), Error):
            return value
        return cls(value)

    def put(self, buf: ByteBuffer) -> ValueOrError[int]:
        """Encode length per X.690 §8.1.3 (minimal octets required)"""
        if self.value == -1:  # Indefinite form
            return buf.put_u8(0x80)
        if self.value < 0x80:  # Short definite form
            return buf.put_u8(self.value)
        # Long definite form: minimal octets for value
        num_bytes = (self.value.bit_length() + 7) // 8
        if isinstance(ret := buf.put_u8(0x80 | num_bytes), Error):
            return ret
        value_bytes = self.value.to_bytes(num_bytes, byteorder="big")
        if isinstance(ret2 := buf.write(value_bytes), Error):
            return ret2
        return ret + ret2

    def __str__(self) -> str:
        return "indefinite" if self.value == -1 else str(self.value)


def put_length(buf: ByteBuffer, value: int) -> ValueOrError[int]:
    """Encode length per X.690 §8.1.3 (minimal octets required)"""
    if value == -1:  # Indefinite form
        return buf.put_u8(0x80)
    if value < 0x80:  # Short definite form
        return buf.put_u8(value)
    # Long definite form: minimal octets for value
    num_bytes = (value.bit_length() + 7) // 8
    if isinstance(ret := buf.put_u8(0x80 | num_bytes), Error):
        return ret
    value_bytes = value.to_bytes(num_bytes, byteorder="big")
    if isinstance(ret2 := buf.write(value_bytes), Error):
        return ret2
    return ret + ret2


@dataclass
class Tag(ED, x680.Tag):
    """
    Tag component with BER-specific constructed flag (X.690 §8.1.2)
    Extends x680.Tag with encoding-time metadata
    """
    # class_number: int
    constructed: bool = False  # Bit 6 per X.690 §8.1.2.5

    def validate(self, buf: ReadableByteBuffer) -> Fallible:
        pos = buf.get_pos()
        if isinstance(tag := self.get(buf), Error):
            return tag
        if tag.class_number != self.class_number:
            if isinstance(err_pos := buf.set_pos(pos), Error):
                return err_pos
            return Error.from_e(TagError(f"Expected tag {self.class_number}, got {tag.class_number}"))
        if tag.class_ != self.class_:
            if isinstance(err_pos := buf.set_pos(pos), Error):
                return err_pos
            return Error.from_e(TagError(f"Expected class {self.class_.name}, got {tag.class_.name}"))
        return OK

    @classmethod
    def get(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """Decode tag per X.690 §8.1.2 (advances buffer position)"""
        if isinstance(first := buf.get_u8(), Error):
            return first
        tag_class = x680.Class(first & x680.Class.PRIVATE)  # Bits 8-7
        constructed = bool(first & 0x20)      # Bit 6
        tag_number = first & 0x1F             # Bits 5-1
        # High-tag-number form (X.690 §8.1.2.4)
        if tag_number == 0x1F:
            tag_number = 0
            while True:
                if isinstance(byte := buf.get_u8(), Error):
                    return byte
                tag_number = (tag_number << 7) | (byte & 0x7F)
                if not (byte & 0x80):  # Last octet has bit 8 = 0
                    break
        return cls(class_number=tag_number, class_=tag_class, constructed=constructed)

    def put(self, buf: ByteBuffer) -> ValueOrError[int]:
        """Encode tag per X.690 §8.1.2 (minimal octets, sets constructed bit)"""
        # Initial octet components
        initial = int(self.class_)
        if self.constructed:
            initial |= 0x20
        if self.class_number < 0x1F:
            # Low-tag-number form (X.690 §8.1.2.2)
            return buf.put_u8(initial | self.class_number)
        # High-tag-number form (X.690 §8.1.2.4)
        if isinstance(written := buf.put_u8(initial | 0x1F), Error):
            return written
        # Encode tag number in 7-bit chunks (MSB first, last chunk has bit 8=0)
        chunks: list[int] = []
        n = self.class_number
        while n:
            chunks.append(n & 0x7F)
            n >>= 7
        # Reverse to get MSB first, set bit 8 on all but last chunk
        chunks.reverse()
        for i in range(len(chunks) - 1):
            chunks[i] |= 0x80
        # Write chunks
        for chunk in chunks:
            if isinstance(tmp := buf.put_u8(chunk), Error):
                return tmp
            written += tmp
        return written

    def __str__(self) -> str:
        form = "constructed" if self.constructed else "primitive"
        return f"Tag(class={self.class_.name}, number={self.class_number}, {form})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tag):
            return NotImplemented
        return (
            self.class_number == other.class_number
            and self.class_ == other.class_
            and self.constructed == other.constructed
        )
