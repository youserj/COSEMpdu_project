from typing import Self, TypeAlias, ClassVar, Protocol, runtime_checkable
from ..byte_buffer import ByteBuffer as Buf
from .tag import Tag


Transcript: TypeAlias = str | list["Transcript"]


@runtime_checkable
class Type(Protocol):
    """"""
    tag: ClassVar[Tag]
    """8 Tags. Universal class tag. -1 is absense"""

    @classmethod
    def parse(cls, value: Transcript) -> Self: ...

    def to_transcript(self) -> Transcript: ...

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


class ReferencedType(Type, Protocol):
    """16.3"""


class ConstrainedType(Type, Protocol):
    """45"""
