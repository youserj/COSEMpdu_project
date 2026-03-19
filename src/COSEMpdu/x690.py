from dataclasses import dataclass, field
from typing import ClassVar, Self
from . import x680
from .x680.type import EDTLV
from .byte_buffer import ByteBuffer


@dataclass
class Length(EDTLV):
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
    def get(cls, buf: ByteBuffer) -> Self:
        """
        Decode length per X.690 §8.1.3
        Returns:
            Length(n) for definite form (n >= 0)
            Length(-1) for indefinite form
        """
        first = buf.get_uint8()
        if not (first & 0x80):  # Short form: bits 7-1 = length
            return cls(first)
        length_of_length = first & 0x7F
        if length_of_length == 0:  # Indefinite form marker (0x80)
            return cls(-1)
        # Long definite form: read 'length_of_length' bytes as big-endian integer
        value = buf.get_uint(length_of_length)
        return cls(value)

    def put(self, buf: ByteBuffer) -> int:
        """Encode length per X.690 §8.1.3 (minimal octets required)"""
        if self.value == -1:  # Indefinite form
            return buf.put_uint8(0x80)
        if self.value < 0x80:  # Short definite form
            return buf.put_uint8(self.value)
        # Long definite form: minimal octets for value
        num_bytes = (self.value.bit_length() + 7) // 8
        written = buf.put_uint8(0x80 | num_bytes)
        value_bytes = self.value.to_bytes(num_bytes, byteorder='big')
        return written + buf.write(value_bytes)

    def __str__(self) -> str:
        return "indefinite" if self.value == -1 else str(self.value)


@dataclass
class Tag(EDTLV, x680.Tag):
    """
    Tag component with BER-specific constructed flag (X.690 §8.1.2)
    Extends x680.Tag with encoding-time metadata
    """
    # class_number: int
    constructed: bool = False  # Bit 6 per X.690 §8.1.2.5
    _hash_cache: int = field(init=False, repr=False, default=0)

    def __post_init__(self) -> None:
        # Вычисляем хэш один раз при создании
        object.__setattr__(self, '_hash_cache', 
            hash((self.class_, self.class_number, self.constructed)))
        object.__setattr__(self, '_hash_computed', True)

    def validate(self, buf: ByteBuffer) -> None:
        pos = buf.get_pos()
        tag = self.get(buf)
        if tag.class_number != self.class_number:
            buf.set_pos(pos)
            raise ValueError(f"Expected tag {self.class_number}, got {tag.class_number}")
        if tag.class_ != self.class_:
            buf.set_pos(pos)
            raise ValueError(f"Expected class {self.class_.name}, got {tag.class_.name}")

    @classmethod
    def get(cls, buf: ByteBuffer) -> Self:
        """Decode tag per X.690 §8.1.2 (advances buffer position)"""
        first = buf.get_uint8()
        tag_class = x680.Class(first & x680.Class.PRIVATE)  # Bits 8-7
        constructed = bool(first & 0x20)      # Bit 6
        tag_number = first & 0x1F             # Bits 5-1
        
        # High-tag-number form (X.690 §8.1.2.4)
        if tag_number == 0x1F:
            tag_number = 0
            while True:
                byte = buf.get_uint8()
                tag_number = (tag_number << 7) | (byte & 0x7F)
                if not (byte & 0x80):  # Last octet has bit 8 = 0
                    break
        return cls(class_number=tag_number, class_=tag_class, constructed=constructed)

    def put(self, buf: ByteBuffer) -> int:
        """Encode tag per X.690 §8.1.2 (minimal octets, sets constructed bit)"""
        # Initial octet components
        initial = self.class_
        if self.constructed:
            initial |= 0x20
        
        if self.class_number < 0x1F:
            # Low-tag-number form (X.690 §8.1.2.2)
            return buf.put_uint8(initial | self.class_number)
        
        # High-tag-number form (X.690 §8.1.2.4)
        written = buf.put_uint8(initial | 0x1F)
        
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
            written += buf.put_uint8(chunk)
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

    def __hash__(self) -> int:
        """
        Efficient hash for Choice alternative lookup.
        Combines class (2 bits), constructed flag (1 bit), and number.
        """
        return self._hash_cache