# AXDR — A-XDR Encoding (IEC 61334-6)

## Overview

The `axdr` module implements A-XDR (Adapted eXtended Data Representation) encoding/decoding according to the IEC 61334-6 standard. A-XDR is a simplified ASN.1 type encoding format used in DLMS/COSEM protocols for data transfer between meters and data collection systems.

Unlike BER, A-XDR:
- **Does not encode tags** for most types (only for CHOICE and explicit tags)
- **Does not encode length** for simple fixed-size types
- Uses **compact representation** to save bandwidth

The module is used by:
- **COSEM APDU** (`apdu.py`) — all APDU messages are encoded in A-XDR
- **Data** (`data.py`) — COSEM Data types

- [X.680](x680.md)
- [X690](x690.md)
- [BER](ber.md)
- [Data](data.md)
- [APDU](apdu.md)

## Module Contents

### Base A-XDR Types

| Class | ASN.1 Type | Encoding Format |
|-------|------------|-----------------|
| `NullType` | NULL | 1 byte (0x00) |
| `NullType0` | NULL with tag [0] | 1 byte (0x00) |
| `BooleanType` | BOOLEAN | 1 byte (0x00/0xFF) |
| `Integer8` | INTEGER (-128..127) | 1 byte |
| `Integer16` | INTEGER (-32768..32767) | 2 bytes |
| `Integer32` | INTEGER (-2³¹..2³¹-1) | 4 bytes |
| `Integer64` | INTEGER (-2⁶³..2⁶³-1) | 8 bytes |
| `Unsigned8` | INTEGER (0..255) | 1 byte |
| `Unsigned16` | INTEGER (0..65535) | 2 bytes |
| `Unsigned32` | INTEGER (0..2³²-1) | 4 bytes |
| `Unsigned64` | INTEGER (0..2⁶⁴-1) | 8 bytes |
| `Float32` | REAL (IEEE 754) | 4 bytes |
| `Float64` | REAL (IEEE 754) | 8 bytes |
| `OctetStringType` | OCTET STRING | length (1 byte) + data |
| `VisibleString` | VisibleString | length (1 byte) + ASCII data |
| `GeneralizedTime` | GeneralizedTime | length + 12 bytes ISO 8601 |
| `EnumeratedType` | ENUMERATED | 1 byte |

### Structured Types

| Class | Description |
|-------|-------------|
| `SequenceType` | SEQUENCE — fields encoded sequentially without tags |
| `SequenceOfType[T]` | SEQUENCE OF — length (1 byte) + elements |
| `ChoiceType` | CHOICE — tag (1 byte) + value |
| `ImplicitTaggedType` | Implicit tagging — no tag in encoding |
| `ExplicitTaggedType` | Explicit tagging — BER TLV format |

### Constrained Types

| Class | Description |
|-------|-------------|
| `ConstrainedOctetStringType` | OCTET STRING with fixed length (no length byte) |
| `ConstrainedSequenceOfType` | SEQUENCE OF with fixed element count |

### Helper Functions

| Function | Description |
|----------|-------------|
| `encode_length(buf, value)` | Encode length in A-XDR (1 byte) |
| `decode_length(buf)` | Decode length from A-XDR |
| `encode_tag(buf, tag)` | Encode CHOICE tag (1 byte) |
| `decode_tag(buf)` | Decode CHOICE tag |

## Usage

### Encoding a Simple Type

```python
from COSEMpdu.axdr import Unsigned8, Integer16
from COSEMpdu.byte_buffer import ByteBuffer

buf = ByteBuffer()
u8 = Unsigned8(42)
u8.put(buf)  # writes 1 byte

i16 = Integer16(-1000)
i16.put(buf)  # writes 2 bytes
```

### Decoding a SEQUENCE

```python
from COSEMpdu.axdr import SequenceType, Unsigned8
from COSEMpdu.byte_buffer import ByteBuffer
from dataclasses import dataclass

@dataclass
class MySequence(SequenceType):
    id: Unsigned8
    value: Unsigned8

buf = ByteBuffer(b'\x01\x2A')
result = MySequence.get(buf)  # -> MySequence(id=Unsigned8(1), value=Unsigned8(42))
```

### Encoding a CHOICE

```python
from COSEMpdu.axdr import ChoiceType
from COSEMpdu.byte_buffer import ByteBuffer

class MyChoice(ChoiceType):
    value: Unsigned8 | OctetStringType

buf = ByteBuffer()
choice = MyChoice(Unsigned8(5))
choice.put(buf)  # 1 tag byte + 1 value byte
```

## Related Links

- [X.680](x680.md) — base ASN.1 types
- [BER](ber.md) — BER type implementations
- [X690](x690.md) — low-level TLV encoding
- [Data](data.md) — COSEM Data types
- [APDU](apdu.md) — COSEM APDU
- [ByteBuffer](byte_buffer.md) — helper class for working with bytes