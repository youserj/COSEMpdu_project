# BER — ASN.1 Basic Encoding Rules

## Overview

The `ber` module contains BER encoding/decoding (X.690) implementations for all base ASN.1 types defined in `x680`. Each class provides `get` and `put` methods for reading/writing in TLV format.

The module is the foundation for:
- **ACSE APDU** (`acse.py`) — all ACSE messages are encoded in BER
- **A-XDR codec** (`axdr.py`) — uses BER for explicit tags
- **COSEM APDU** (`apdu.py`) — types like `Conformance` use BER

- [X.680](x680.md)
- [X690](x690.md)
- [AXDR](axdr.md)
- [ACSE](acse.md)
- [APDU](apdu.md)

## Module Contents

### BER Type Implementations

| Class | ASN.1 Type | Base Type | Methods |
|-------|------------|-----------|---------|
| `BooleanType` | BOOLEAN | `x680.BooleanType` | `get()`, `put()` |
| `IntegerType` | INTEGER | `x680.IntegerType` | `get()`, `put()` |
| `EnumeratedType` | ENUMERATED | `x680.EnumeratedType` | `get()`, `put()` |
| `BitStringType` | BIT STRING | `x680.BitStringType` | `get()`, `put()` |
| `OctetStringType` | OCTET STRING | `x680.OctetStringType` | `get()`, `put()` |
| `NullType` | NULL | `x680.NullType` | `get()`, `put()` |
| `ObjectIdentifierType` | OBJECT IDENTIFIER | `x680.ObjectIdentifierType` | `get()`, `put()` |
| `SequenceType` | SEQUENCE | `x680.SequenceType` | `get()`, `put()` |
| `SequenceOfType` | SEQUENCE OF | `x680.SequenceOfType` | `get()`, `put()` |
| `ChoiceType` | CHOICE | `x680.ChoiceType` | `get()`, `put()` |
| `ExplicitTaggedType` | — (explicit tagging) | `x680.Type` | `get()`, `put()` |
| `ImplicitTaggedType` | — (implicit tagging) | `x680.Type` | `get()`, `put()` |
| `GraphicString` | GraphicString | `x680.GraphicString` | `get()`, `put()` |
| `GeneralizedTime` | GeneralizedTime | `x680.GeneralizedTime` | `get()`, `put()` |
| `ConstrainedBitStringType` | BIT STRING | `x680.ConstrainedBitStringType`, `BitStringType` | `get()`, `put()` |

### Helper Functions

| Function | Description |
|----------|-------------|
| `put_lc(buf, length, data)` | Write Length + Contents to buffer |

## Usage

### INTEGER Encoding/Decoding in BER

```python
from COSEMpdu.ber import IntegerType
from COSEMpdu.byte_buffer import ByteBuffer

# Encoding
buf = ByteBuffer()
value = IntegerType.new(42)
value.put(buf)

# Decoding
decoded = IntegerType.get(buf)  # -> IntegerType(42)
```

### SEQUENCE Encoding in BER

Each type encodes itself via `.put()` — no separate "put_sequence" helper is needed:

```python
from COSEMpdu.ber import SequenceType, IntegerType, OctetStringType
from COSEMpdu.byte_buffer import ByteBuffer

class MySeq(SequenceType):
    a: IntegerType
    b: OctetStringType

buf = ByteBuffer()
seq = MySeq(a=IntegerType.new(1), b=OctetStringType.new(b"hello"))
seq.put(buf)
```

### Creating a BER-Compatible Type

```python
from COSEMpdu.x680 import IntegerType as X680Integer
from COSEMpdu.ber import IntegerType as BERInteger

class MyInt(BERInteger, X680Integer):
    """INTEGER with BER support"""
    pass
```

## Related Links

- [X.680](x680.md) — base ASN.1 types
- [X690](x690.md) — low-level TLV encoding
- [AXDR](axdr.md) — A-XDR type implementations
- [APDU](apdu.md) — COSEM APDU
- [ACSE](acse.md) — ACSE APDU
- [ByteBuffer](byte_buffer.md) — helper class for working with bytes