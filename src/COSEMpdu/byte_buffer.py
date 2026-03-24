from typing import Self, Optional, Protocol


class _ByteBuffer[T: (bytearray, bytes)](Protocol):
    """Object class wrapping a byte array and allowing manipulation"""
    buf: T
    _pos: int
    __slots__ = ("buf", "_pos")

    def __init__(self, buffer: T) -> None:
        self.buf = buffer
        """ the data buffer """
        self._pos = 0
        """ current position """

    @classmethod
    def wrap(cls, data: T) -> Self: ...

    def remaining(self, pos: Optional[int] = None) -> int:
        """remaining bytes"""
        if pos is None:
            pos = self._pos
        return len(self.buf) - pos

    def _check_space(self, space: int, pos: Optional[int] = None) -> None:
        """check whether this buffer has enough `space` left for r/w op"""
        if pos is None:
            pos = self._pos
        if self.remaining(pos) < space:
            raise BufferError(F"{self} not enough more {space=}")

    def read(self, length: int = 1) -> T:
        """return view to position, increase position"""
        ret = self.read_pos(self._pos, length)
        self._pos += length
        return ret

    def read_pos(self,
                 pos: int,
                 length: int = 1) -> T:
        """return view to position"""
        self._check_space(length, pos)
        return self.buf[pos: pos + length]

    def get_uint(self, length: int) -> int:
        """get INTEGER, increase position"""
        return int.from_bytes(self.read(length), "big")

    def get_uint_pos(self,
                     pos: int,
                     length: int) -> int:
        """get INTEGER"""
        return int.from_bytes(self.read_pos(pos, length), "big")

    def get_uint8(self) -> int:
        """get integer8, increase position"""
        return self.read(1)[0]

    def get(self) -> bytes:
        """get one byte, increase position"""
        return bytes(self.read(1))

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

    def set_pos(self, index: int) -> None:
        """set new position, with check"""
        if (len_ := len(self)) == 0:
            """skip NullTypes"""
        elif 0 <= index < len_:
            self._pos = index
        else:
            raise BufferError(f"overflow, {self} can't set {index=}")

    def shift_pos(self, value: int) -> int:
        """shift and return old position"""
        self.set_pos((ret := self._pos) + value)
        return ret

    def peek(self, length: int = 1) -> T:
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

    def write(self,
              value: memoryview | bytes) -> int:
        """keep data to position, increase position"""
        self._pos += (length := self.write_pos(value, self._pos))
        return length

    def write_pos(self,
                  value: bytes,
                  pos: int) -> int:
        """keep data to position, return length data"""
        length = len(value)
        self._check_space(length, pos)
        self.buf[pos: pos + length] = value
        return length

    def put_uint8(self, value: int) -> int:
        """put builtin int, increase position"""
        self._check_space(1)
        self.buf[self._pos] = value
        self._pos += 1
        return 1

    def frozen(self) -> ByteBufferFrozen:
        """Allocate a new ByteBuffer with a zero-initialized buffer of given size"""
        return ByteBufferFrozen(bytes(self))

    def shift_right(self, pos: int, length: int, step: int) -> int:
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
            raise ValueError(f"Step must be non-negative, got {step}")
        if length < 0:
            raise ValueError(f"Length must be non-negative, got {length}")
        if pos < 0 or pos > len(self.buf):
            raise ValueError(f"Position {pos} out of range [0, {len(self.buf)}]")
        # Nothing to shift or zero shift - just return next position
        if length == 0 or step == 0:
            return pos + length
        # Check if shifted data fits in buffer
        if pos + length + step > len(self.buf):
            raise BufferError(f"Not enough space: need {pos + length + step}, have {len(self.buf)}")
        # Write data to new position
        for i in range(length - 1, -1, -1):
            self.buf[pos + step + i] = self.buf[pos + i]
        # Return next position after shifted data
        return pos + length + step
