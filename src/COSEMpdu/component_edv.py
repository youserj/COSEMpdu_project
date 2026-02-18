from typing import Self, Protocol
from .byte_buffer import ByteBuffer



class ComponentEDV(Protocol):
    """Encoding data value component"""

    def __len__(self) -> int:
        """necessary length of encode in octets"""
        ...

    @classmethod
    def get(cls, buf: ByteBuffer) -> Self:
        """constructor decoded value from buffer"""
        ...

    def put(self, buf: ByteBuffer) -> int:
        """put encode definite length value to buffer"""
        ...
