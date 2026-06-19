from typing import Self, Optional, Protocol, TypeAlias
from StructResult.result import ValueOrError, Fallible, Error, OK


class _ByteBuffer[T: (bytearray, bytes)](Protocol):
    """Object class wrapping a byte array and allowing manipulation"""
    buf: T
    _pos: int
    __slots__ = ("buf", "_pos")

    def __init__(self, buffer: T, pos: int = 0) -> None:
        self.buf = buffer
        """ the data buffer """
        self._pos = pos
        """ current position """

    @classmethod
    def wrap(cls, data: T) -> Self: ...

    def remaining(self, pos: Optional[int] = None) -> int:
        """remaining bytes"""
        if pos is None:
            pos = self._pos
        return len(self.buf) - pos

    def _check_space(self, space: int, pos: Optional[int] = None) -> Fallible:
        """check whether this buffer has enough `space` left for r/w op"""
        if pos is None:
            pos = self._pos
        if self.remaining(pos) < space:
            return Error.from_e(BufferError(F"{self} not enough more {space=}"))
        return OK

    def read(self, length: int = 1) -> ValueOrError[T]:
        """return view to position, increase position"""
        ret = self.read_pos(self._pos, length)
        if not isinstance(ret, Error):
            self._pos += length
        return ret

    def read_pos(self,
                 pos: int,
                 length: int = 1) -> ValueOrError[T]:
        """return view to position"""
        if isinstance(r_check := self._check_space(length, pos), Error):
            return r_check
        return self.buf[pos: pos + length]

    def get_uint(self, length: int) -> ValueOrError[int]:
        """get INTEGER, increase position"""
        if isinstance(r_value := self.read(length), Error):
            return r_value
        return int.from_bytes(r_value, "big")

    def get_uint_pos(self,
                     pos: int,
                     length: int) -> ValueOrError[int]:
        """get INTEGER"""
        if isinstance(r_value := self.read_pos(pos, length), Error):
            return r_value
        return int.from_bytes(r_value, "big")

    def get_u8(self) -> ValueOrError[int]:
        """get integer8, increase position"""
        if isinstance(value := self.read(1), Error):
            return value
        return value[0]

    def get(self) -> ValueOrError[bytes]:
        """get one byte, increase position"""
        if isinstance(r_value := self.read(1), Error):
            return r_value
        return bytes(r_value)

    def __bytes__(self) -> bytes:
        return bytes(self.buf)

    def __getitem__(self, item: int) -> int:
        return self.buf.__getitem__(item)

    def slice(self) -> Self:
        """slice the buffer at current position. return new class"""
        return self.__class__(self.buf[self._pos:])

    def __len__(self) -> int:
        return len(self.buf)

    def __str__(self) -> str:
        return F"{self.__class__.__name__}[{len(self)}]: pos={self._pos}"

    def get_pos(self) -> int:
        return self._pos

    def set_pos(self, index: int) -> ValueOrError[int]:
        """set new position, with check, return delta"""
        if 0 <= index < len(self):
            ret = index - self._pos
            self._pos = index
            return ret
        return Error.from_e(BufferError(f"overflow, {self} can't set {index=}"))

    def shift_pos(self, value: int) -> ValueOrError[int]:
        """shift and return delta"""
        if 0 <= (index := self._pos + value) < len(self):
            self._pos = index
            return value
        return Error.from_e(BufferError(f"overflow, {self} can't set {index=}"))

    def reserve(self, value: int) -> ValueOrError[int]:
        """reserve space to be filled later"""
        if 0 <= (index := self._pos + value) < len(self):
            self._pos = index
            return 0
        return Error.from_e(BufferError(f"overflow, {self} can't set {index=}"))

    def peek(self, length: int = 1) -> ValueOrError[T]:
        return self.read_pos(self._pos, length)

    def extract(self) -> Self:
        """
        Return new ByteBuffer with data from start to current position.

        This is useful for getting the data that has been 'consumed' or 'read'
        from the buffer up to the current position.

        Returns:
            Self: New ByteBuffer instance containing data[0:__pos]

        Example:
            >>> buf = ByteBuffer.allocate(15)
            >>> buf.write(b'Hello World')
            >>> buf.set_pos(5)  # position now at 5
            >>> extracted = buf.extract()  # contains b'Hello'
        """
        return self.__class__(self.buf[:self._pos])


class ByteBufferFrozen(_ByteBuffer[bytes]):
    @classmethod
    def wrap(cls, data: bytes | bytearray) -> Self:
        return cls(bytes(data))

    def unfrozen(self) -> "ByteBuffer":
        return ByteBuffer(bytearray(self.buf))


class ByteBuffer(_ByteBuffer[bytearray]):

    @classmethod
    def allocate(cls, size: int) -> Self:
        """return instance with creating buffer"""
        return cls(bytearray(size))

    @classmethod
    def wrap(cls, data: bytes | bytearray) -> Self:
        return cls(bytearray(data))

    def write(self, value: bytes) -> ValueOrError[int]:
        """keep data to position, increase position"""
        if not isinstance(length := self.write_pos(value, self._pos), Error):
            self._pos += length
        return length

    def write_pos(self,
                  value: bytes,
                  pos: int) -> ValueOrError[int]:
        """keep data to position, return length data"""
        length = len(value)
        if isinstance(err := self._check_space(length, pos), Error):
            return err
        self.buf[pos: pos + length] = value
        return length

    def put_u8(self, value: int) -> ValueOrError[int]:
        """put builtin int, increase position"""
        if isinstance(err := self._check_space(1), Error):
            return err
        self.buf[self._pos] = value
        self._pos += 1
        return 1

    def frozen(self) -> ByteBufferFrozen:
        """Allocate a new ByteBuffer with a zero-initialized buffer of given size"""
        return ByteBufferFrozen(bytes(self))

    def sub_buffer(self, pos: Optional[int] = None) -> "ByteBuffer":
        """Return a new ByteBuffer sharing the same underlying buffer with independent _pos."""
        return ByteBuffer(self.buf, self._pos if pos is None else pos)

    def shift_right(self, pos: int, length: int, step: int) -> ValueOrError[int]:
        """
        Shift data in the buffer right by `step` bytes.

        Args:
            pos: starting position of data to shift
            length: length of data to shift
            step: shift amount (positive integer)

        Returns:
            int: next position after shifted data (pos + length + step)
        Raises:
            ValueError: if parameters are invalid
            BufferError: if there's not enough space in buffer
        """
        # Validate parameters
        if step < 0:
            return Error.from_e(ValueError(f"Step must be non-negative, got {step}"))
        if length < 0:
            return Error.from_e(ValueError(f"Length must be non-negative, got {length}"))
        if pos < 0 or pos > len(self.buf):
            return Error.from_e(ValueError(f"Position {pos} out of range [0, {len(self.buf)}]"))
        # Nothing to shift or zero shift - just return next position
        if length == 0 or step == 0:
            return pos + length
        # Check if shifted data fits in buffer
        if pos + length + step > len(self.buf):
            return Error.from_e(BufferError(f"Not enough space: need {pos + length + step}, have {len(self.buf)}"))
        # Write data to new position
        for i in range(length - 1, -1, -1):
            self.buf[pos + step + i] = self.buf[pos + i]
        # Return next position after shifted data
        return pos + length + step


ReadableByteBuffer: TypeAlias = ByteBuffer | ByteBufferFrozen


def put_chain(*res: ValueOrError[int]) -> ValueOrError[int]:
    count: int = 0
    for r in res:
        if isinstance(r, Error):
            return r
        count += r
    return count
