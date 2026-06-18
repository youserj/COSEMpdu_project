# Data — COSEM Data Types (IEC 62056-6-2)

## Overview

The `data` module implements COSEM Data types according to the IEC 62056-6-2 (DLMS/COSEM) standard. These types are used to represent attribute values, read and write results in the COSEM protocol. All types are based on A-XDR encoding (`axdr.py`) and inherit base ASN.1 types from `x680`.

The module is central to:
- **COSEM APDU** (`apdu.py`) — all APDU messages use Data types
- **CompactArray** — compact array storage

- [X.680](x680.md)
- [AXDR](axdr.md)
- [APDU](apdu.md)

## Module Contents

### Integer Types

| Class | Range | Size (bytes) |
|-------|-------|--------------|
| `Integer8` | -128..127 | 1 |
| `Integer16` | -32768..32767 | 2 |
| `Integer32` | -2³¹..2³¹-1 | 4 |
| `Integer64` | -2⁶³..2⁶³-1 | 8 |
| `Unsigned8` | 0..255 | 1 |
| `Unsigned16` | 0..65535 | 2 |
| `Unsigned32` | 0..2³²-1 | 4 |
| `Unsigned64` | 0..2⁶⁴-1 | 8 |

### COSEM Data Types (with explicit tags)

| Class | Tag | ASN.1 Type | Size | Description |
|-------|-----|-----------|------|-------------|
| `NullData` | [0] | NULL | 1 | null-data |
| `Array` | [1] | SEQUENCE OF Data | var. | Data array |
| `Structure` | [2] | SEQUENCE OF Data | var. | Structure (fields by name) |
| `Boolean` | [3] | BOOLEAN | 1 | Boolean value |
| `BitString` | [4] | BIT STRING | var. | Bit string |
| `DoubleLong` | [5] | Integer32 | 4 | 32-bit signed |
| `DoubleLongUnsigned` | [6] | Unsigned32 | 4 | 32-bit unsigned |
| `OctetString` | [9] | OCTET STRING | var. | Byte string |
| `VisibleString` | [10] | VisibleString | var. | ASCII string |
| `Utf8String` | [12] | UTF8String | var. | UTF-8 string |
| `Bcd` | [13] | Integer8 | 1 | BCD value |
| `Integer` | [15] | Integer8 | 1 | 8-bit signed |
| `Long` | [16] | Integer16 | 2 | 16-bit signed |
| `Unsigned` | [17] | Unsigned8 | 1 | 8-bit unsigned |
| `LongUnsigned` | [18] | Unsigned16 | 2 | 16-bit unsigned |
| `Long64` | [20] | Integer64 | 8 | 64-bit signed |
| `Long64Unsigned` | [21] | Unsigned64 | 8 | 64-bit unsigned |
| `Enum` | [22] | Unsigned8 | 1 | Enumeration |
| `Float32` | [23] | OCTET STRING SIZE(4) | 4 | 32-bit IEEE 754 |
| `Float64` | [24] | OCTET STRING SIZE(8) | 8 | 64-bit IEEE 754 |
| `DateTime` | [25] | OCTET STRING SIZE(12) | 12 | Date and time |
| `Date` | [26] | OCTET STRING SIZE(5) | 5 | Date |
| `Time` | [27] | OCTET STRING SIZE(4) | 4 | Time |

### Type Description Types (TypeDescription)

| Class | Tag | Describes Type |
|-------|-----|----------------|
| `NullData` | 0 | null-data |
| `TypeDescriptionArray` | 1 | array |
| `TypeDescriptionStructure` | 2 | structure |
| `TypeDescriptionBoolean` | 3 | boolean |
| `TypeDescriptionBitString` | 4 | bit-string |
| `TypeDescriptionDoubleLong` | 5 | double-long |
| `TypeDescriptionDoubleLongUnsigned` | 6 | double-long-unsigned |
| `TypeDescriptionOctetString` | 9 | octet-string |
| `TypeDescriptionVisibleString` | 10 | visible-string |
| `TypeDescriptionUtf8String` | 12 | utf8-string |
| `TypeDescriptionBcd` | 13 | bcd |
| `TypeDescriptionInteger` | 15 | integer |
| `TypeDescriptionLong` | 16 | long |
| `TypeDescriptionUnsigned` | 17 | unsigned |
| `TypeDescriptionLongUnsigned` | 18 | long-unsigned |
| `TypeDescriptionLong64` | 20 | long64 |
| `TypeDescriptionLong64Unsigned` | 21 | long64-unsigned |
| `TypeDescriptionEnum` | 22 | enum |
| `TypeDescriptionFloat32` | 23 | float32 |
| `TypeDescriptionFloat64` | 24 | float64 |
| `TypeDescriptionDateTime` | 25 | date-time |
| `TypeDescriptionDate` | 26 | date |
| `TypeDescriptionTime` | 27 | time |
| `TypeDescriptionDontCare` | 255 | dont-care |

### Structural Types

| Class | Description |
|-------|-------------|
| `CompactArray` | Compact array: [19] SEQUENCE { contents-description, array-contents } |
| `Array[T]` | [1] SEQUENCE OF Data |
| `Structure` | [2] SEQUENCE — fields with name-based access |
| `Data` | CHOICE of all COSEM Data types |

### Helper Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `LN_REFERENCE` | 0x0007 | Logical Name referencing |
| `SN_REFERENCE` | 0xFA00 | Short Name referencing |

## The Data Type (CHOICE)

`Data` is a CHOICE type combining all COSEM Data types. On decoding, the specific type is automatically determined by the tag:

```python
class Data(ChoiceType):
    value: NullData | Array | Structure | Boolean | BitString | DoubleLong
         | DoubleLongUnsigned | OctetString | VisibleString | Utf8String | Bcd
         | Integer | Long | Unsigned | LongUnsigned | Long64 | Long64Unsigned
         | Enum | Float32 | Float64 | DateTime | Date | Time
         | CompactArray | DontCare
```

## The Structure Type

`Structure` supports two operation modes:

### Static (predefined fields)

```python
@dataclass
class MyRecord(Structure):
    voltage: DoubleLongUnsigned
    current: DoubleLongUnsigned
```

### Dynamic (generated fields)

```python
s = Structure.from_data(Unsigned8(42), OctetString(b"hello"))
```

Fields are automatically assigned names `a`, `b`, `c`, …

## Usage

### Reading a COSEM Value

```python
from COSEMpdu.data import Data, Structure, DoubleLongUnsigned
from COSEMpdu.byte_buffer import ByteBuffer

buf = ByteBuffer(apdu_bytes)
data = Data.get(buf)
if isinstance(data.value, Structure):
    print("Structure with fields:", data.value.components)
```

### Creating Values

```python
from COSEMpdu.data import DoubleLongUnsigned, OctetString

voltage = DoubleLongUnsigned(230000)  # 230.000 V
serial = OctetString(b"12345678")
```

### Compact Array

```python
from COSEMpdu.data import CompactArray, Unsigned8, ContentsDescription

data = [Unsigned8(1), Unsigned8(2), Unsigned8(3)]
compact = CompactArray.from_array(data)
restored = compact.get_array()
```

### Float with Conversion

```python
from COSEMpdu.data import Float32

f = Float32.from_float(3.14)
value = float(f)  # -> 3.14
```

## Related Links

- [X.680](x680.md) — base ASN.1 types
- [AXDR](axdr.md) — A-XDR type implementations
- [APDU](apdu.md) — COSEM APDU
- [ByteBuffer](byte_buffer.md) — helper class for working with bytes