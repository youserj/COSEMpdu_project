# Byte Buffer API

The `byte_buffer.py` module provides classes for working with byte buffers — both mutable (`ByteBuffer`) and immutable (`ByteBufferFrozen`). The classes are based on the `_ByteBuffer[T]` protocol and use the `ValueOrError` monad (from the `StructResult` library) — most methods return either a value or an error.

---

## `_ByteBuffer[T: (bytearray, bytes)]` (Protocol)

Base protocol class implementing common positional read operations over a byte buffer.

### Attributes

| Attribute | Type  | Description           |
|-----------|-------|-----------------------|
| `buf`     | `T`   | The data buffer       |
| `_pos`    | `int` | Current read position |

### Constructor

```python
def __init__(self, buffer: T, pos: int = 0) -> None
```

| Parameter | Type  | Default | Description                                       |
|-----------|-------|---------|---------------------------------------------------|
| `buffer`  | `T`   | —       | Source byte buffer (`bytes` / `bytearray`)        |
| `pos`     | `int` | `0`     | Initial read position                             |

---

### Methods

#### `wrap(data: T) -> Self` *(classmethod)*

Creates a class instance from the given data.

```python
@classmethod
def wrap(cls, data: T) -> Self
```

#### `remaining(pos: Optional[int] = None) -> int`

Returns the number of bytes remaining from position `pos` to the end of the buffer. If `pos` is not provided, the current `_pos` is used.

| Parameter | Type            | Default | Description                     |
|-----------|-----------------|---------|---------------------------------|
| `pos`     | `Optional[int]` | `None`  | Position to calculate from      |

**Returns:** `int` — number of remaining bytes.

#### `_check_space(space: int, pos: Optional[int] = None) -> Fallible`

Checks whether the buffer has enough `space` bytes available for a read/write operation from position `pos`. Internal method.

| Parameter | Type            | Default | Description                          |
|-----------|-----------------|---------|--------------------------------------|
| `space`   | `int`           | —       | Required number of bytes             |
| `pos`     | `Optional[int]` | `None`  | Position to check from               |

**Returns:** `Fallible` — `OK` on success, `Error` (with `BufferError`) if insufficient space.

#### `read(length: int = 1) -> ValueOrError[T]`

Reads `length` bytes starting at the current position and **increments** `_pos` by `length`.

| Parameter | Type  | Default | Description        |
|-----------|-------|---------|--------------------|
| `length`  | `int` | `1`     | Number of bytes    |

**Returns:** `ValueOrError[T]` — buffer slice or `Error`.

#### `read_pos(pos: int, length: int = 1) -> ValueOrError[T]`

Reads `length` bytes starting at position `pos` **without changing** the current `_pos`.

| Parameter | Type  | Default | Description           |
|-----------|-------|---------|-----------------------|
| `pos`     | `int` | —       | Start position        |
| `length`  | `int` | `1`     | Number of bytes       |

**Returns:** `ValueOrError[T]` — buffer slice or `Error`.

#### `get_uint(length: int) -> ValueOrError[int]`

Reads an unsigned integer of `length` bytes from the current position and **increments** `_pos`.

| Parameter | Type  | Description               |
|-----------|-------|---------------------------|
| `length`  | `int` | Number length in bytes    |

**Returns:** `ValueOrError[int]` — integer value (big-endian) or `Error`.

#### `get_uint_pos(pos: int, length: int) -> ValueOrError[int]`

Reads an unsigned integer from position `pos` **without changing** `_pos`.

| Parameter | Type  | Description               |
|-----------|-------|---------------------------|
| `pos`     | `int` | Start position            |
| `length`  | `int` | Number length in bytes    |

**Returns:** `ValueOrError[int]` — integer value (big-endian) or `Error`.

#### `get_u8() -> ValueOrError[int]`

Reads one byte (`uint8`) from the current position and **increments** `_pos`.

**Returns:** `ValueOrError[int]` — byte value (0–255) or `Error`.

#### `get() -> ValueOrError[bytes]`

Reads one byte from the current position and **increments** `_pos`. Differs from `get_u8()` in return type — returns `bytes`.

**Returns:** `ValueOrError[bytes]` — a single byte as `bytes` or `Error`.

#### `peek(length: int = 1) -> ValueOrError[T]`

Reads `length` bytes at the current position **without changing** `_pos`. Synonym for `read_pos(self._pos, length)`.

| Parameter | Type  | Default | Description        |
|-----------|-------|---------|--------------------|
| `length`  | `int` | `1`     | Number of bytes    |

**Returns:** `ValueOrError[T]` — buffer slice or `Error`.

#### `get_pos() -> int`

Returns the current position `_pos`.

#### `set_pos(index: int) -> ValueOrError[int]`

Sets a new position with bounds checking. Returns the **delta** (difference between new and old position).

| Parameter | Type  | Description       |
|-----------|-------|-------------------|
| `index`   | `int` | New position      |

**Returns:** `ValueOrError[int]` — position delta or `Error` (if `index` is outside `[0, len(self))`).

#### `shift_pos(value: int) -> ValueOrError[int]`

Shifts the position by `value` (adds to current). Returns the old position.

| Parameter | Type  | Description |
|-----------|-------|-------------|
| `value`   | `int` | Offset      |

**Returns:** `ValueOrError[int]` — old position or `Error`.

#### `slice() -> Self`

Returns a **new** instance of the same class with a buffer starting from the current `_pos`.

**Returns:** `Self` — new buffer with data `self.buf[self._pos:]`.

#### `extract() -> Self`

Returns a **new** instance with data from the start of the buffer up to the current position (`self.buf[:self._pos]`). Useful for retrieving data that has already been "consumed" or "read".

**Returns:** `Self` — new buffer with read data.

---

### Dunder methods

| Method                        | Description                                              |
|-------------------------------|----------------------------------------------------------|
| `__bytes__() -> bytes`        | Returns the buffer contents as `bytes`                   |
| `__getitem__(item: int) -> int` | Access to an individual byte by index                  |
| `__len__() -> int`            | Buffer length in bytes                                   |
| `__str__() -> str`            | String representation: `ClassName[len]: pos=N`           |

---

## `ByteBufferFrozen(_ByteBuffer[bytes])`

Immutable (read-only) buffer based on `bytes`. Supports all `_ByteBuffer` methods except write operations.

### Class methods

#### `wrap(data: bytes | bytearray) -> Self`

Creates a `ByteBufferFrozen` from `bytes` or `bytearray` (data is coerced to `bytes`).

### Instance methods

#### `unfrozen() -> ByteBuffer`

Creates a mutable copy (`ByteBuffer`) from this buffer's data.

**Returns:** `ByteBuffer` — mutable buffer with a copy of the data.

---

## `ByteBuffer(_ByteBuffer[bytearray])`

Mutable buffer based on `bytearray`. Supports all `_ByteBuffer` methods plus write operations.

### Class methods

#### `allocate(size: int) -> Self`

Creates a new `ByteBuffer` with a zero-initialized buffer of the given size.

| Parameter | Type  | Description           |
|-----------|-------|-----------------------|
| `size`    | `int` | Buffer size in bytes  |

#### `wrap(data: bytes | bytearray) -> Self`

Creates a `ByteBuffer` from `bytes` or `bytearray` (data is coerced to `bytearray`).

---

### Write methods

#### `write(value: bytes) -> ValueOrError[int]`

Writes `value` to the buffer starting at the current position and **increments** `_pos` by the number of bytes written.

| Parameter | Type    | Description       |
|-----------|---------|-------------------|
| `value`   | `bytes` | Data to write     |

**Returns:** `ValueOrError[int]` — number of bytes written or `Error`.

#### `write_pos(value: bytes, pos: int) -> ValueOrError[int]`

Writes `value` at position `pos` **without changing** `_pos`.

| Parameter | Type    | Description       |
|-----------|---------|-------------------|
| `value`   | `bytes` | Data to write     |
| `pos`     | `int`   | Write position    |

**Returns:** `ValueOrError[int]` — number of bytes written or `Error`.

#### `put_u8(value: int) -> ValueOrError[int]`

Writes a single byte at the current position and **increments** `_pos` by 1.

| Parameter | Type  | Description              |
|-----------|-------|--------------------------|
| `value`   | `int` | Byte value (0–255)       |

**Returns:** `ValueOrError[int]` — `1` on success or `Error`.

---

### Other methods

#### `frozen() -> ByteBufferFrozen`

Creates an immutable copy (`ByteBufferFrozen`) of the current buffer.

**Returns:** `ByteBufferFrozen` — read-only copy.

#### `sub_buffer(pos: Optional[int] = None) -> ByteBuffer`

Creates a **new** `ByteBuffer` sharing the same `bytearray` but with an **independent** `_pos`.

| Parameter | Type            | Default | Description                                      |
|-----------|-----------------|---------|--------------------------------------------------|
| `pos`     | `Optional[int]` | `None`  | Initial position (defaults to `self._pos`)       |

**Returns:** `ByteBuffer` — new buffer sharing the same `bytearray`.

#### `shift_right(pos: int, length: int, step: int) -> ValueOrError[int]`

Shifts `length` bytes starting at position `pos` right by `step` bytes. Data is moved byte-by-byte from end to start (safe for overlapping ranges).

| Parameter | Type  | Description                                      |
|-----------|-------|--------------------------------------------------|
| `pos`     | `int` | Start position of the block to shift             |
| `length`  | `int` | Length of the block to shift                     |
| `step`    | `int` | Right shift amount (non-negative)                |

**Returns:** `ValueOrError[int]` — next position after the shifted block (`pos + length + step`) or `Error`:
- `ValueError` for invalid parameters
- `BufferError` if there is not enough space in the buffer

---

## Utility elements

### `ReadableByteBuffer`

```python
ReadableByteBuffer: TypeAlias = ByteBuffer | ByteBufferFrozen
```

Type alias for any buffer that supports reading (both mutable and immutable).

### `put_chain(*res: ValueOrError[int]) -> ValueOrError[int]`

Utility for chaining write operations. Accepts an arbitrary number of `ValueOrError[int]` results and returns the sum of all successful values or the first encountered error.

| Parameter | Type                 | Description                                          |
|-----------|----------------------|------------------------------------------------------|
| `*res`    | `ValueOrError[int]`  | Results of write operations (each returning a length) |

**Returns:** `ValueOrError[int]` — total number of bytes written or the first `Error`.

---

## Usage examples

```python
from COSEMpdu.byte_buffer import ByteBuffer, ByteBufferFrozen, ReadableByteBuffer, put_chain

# === Buffer creation ===
buf = ByteBuffer.allocate(64)                  # empty 64-byte buffer
buf2 = ByteBuffer.wrap(b"\x01\x02\x03")        # buffer from bytes

frozen = ByteBufferFrozen.wrap(b"\xaa\xbb\xcc")  # immutable buffer

# === Reading ===
val = frozen.get_u8()       # 0xAA, position advanced by 1
val = frozen.get_u8()       # 0xBB
frozen.set_pos(0)           # reset position
data = frozen.read(2)       # b"\xaa\xbb", position = 2
rest = frozen.peek(1)       # b"\xcc", position unchanged

# === Writing to ByteBuffer ===
buf.set_pos(0)
buf.write(b"Hello")         # write 5 bytes, position = 5
buf.put_u8(0x20)            # space, position = 6
buf.write(b"World")         # position = 11

# === Write chain ===
buf.set_pos(0)
result = put_chain(
    buf.write(b"AB"),
    buf.put_u8(0xCD),
    buf.write(b"EF"),
)
# result = OK(5)

# === Freeze / unfreeze ===
frozen_copy = buf.frozen()                  # ByteBufferFrozen
mutable_copy = frozen_copy.unfrozen()       # back to ByteBuffer

# === Extracting consumed data ===
buf.set_pos(0)
buf.read(5)                 # read first 5 bytes
consumed = buf.extract()    # new ByteBuffer with buf[0:5]