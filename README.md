# COSEMpdu

DLMS/COSEM PDU encoder/decoder for smart metering protocols. Implements ASN.1 types (X.680), A-XDR encoding rules (IEC 61334-6), and BER encoding rules (X.690).

## Overview

COSEMpdu provides a Python library for working with DLMS/COSEM Protocol Data Units (PDUs) used in smart metering and energy management systems. It implements the full COSEM PDU specification from the Green Book (IEC 62056 / EN 13757-1), including:

- **ASN.1 Type System (X.680)** — BOOLEAN, INTEGER, ENUMERATED, OCTET STRING, BIT STRING, SEQUENCE, SEQUENCE OF, CHOICE, NULL, OBJECT IDENTIFIER, GeneralizedTime, constrained types, and tagging
- **A-XDR Encoding (IEC 61334-6:2000)** — Size-optimized encoding for COSEM APDU (Application Protocol Data Unit)
- **BER Encoding (X.690)** — Basic Encoding Rules for COSEM ACSE (Association Control Service Element)
- **COSEM APDU Types** — All PDU types defined in the Green Book: xDLMS services, COSEM services, and all response types
- **COSEM ACSE Types** — Application association, authentication, and release PDUs

## Installation

```bash
pip install COSEMpdu
```

Requires Python ≥ 3.12.

## Quick Start

```python
from COSEMpdu.apdu import (
    GetRequest, InvokeIdAndPriority,
    CosemAttributeDescriptor,
    CosemClassId, CosemObjectInstanceId, CosemObjectAttributeId,
)
from COSEMpdu.byte_buffer import ByteBuffer
from StructResult.result import Error

# Create a GET-Request PDU
get = GetRequest(
    invoke_id_and_priority=InvokeIdAndPriority(0x13),  # invoke_id=1, confirmed, priority high
    cosem_attribute_descriptor=CosemAttributeDescriptor(
        class_id=CosemClassId(8),                        # Clock object
        instance_id=CosemObjectInstanceId(b"\x00\x00\x01\x00\x00\xff"),  # logical name
        attribute_id=CosemObjectAttributeId(2)           # attribute #2 (time)
    )
)

# Encode to A-XDR bytes
buf = ByteBuffer(bytearray(100))
get.put(buf)
print(bytes(buf.extract()).hex())  # => encoded PDU bytes

# Decode from bytes
result = GetRequest.get(buf.extract())
match result:
    case Error():
        print("Decode failed:", result.err)
    case _:
        decoded: GetRequest = result
        print(decoded.cosem_attribute_descriptor.class_id)
```

### ACSE (BER) Example

```python
from COSEMpdu.acse import (
    AARQapdu, ProtocolVersion, ApplicationContextName,
    CalledAPInvocationId, CalledAEInvocationId,
    CallingAPInvocationId, CallingAEInvocationId,
    RequestMechanismName,
)
from COSEMpdu.byte_buffer import ByteBuffer
from StructResult.result import Error

# Create an AARQ (Application Association Request) — BER encoding
aarq = AARQapdu(
    protocol_version=ProtocolVersion((1, 1)),
    application_context_name=ApplicationContextName(
        (2, 16, 756, 5, 8, 1, 1)  # LN referencing
    ),
    called_ap_invocation_id=CalledAPInvocationId(1),
    called_ae_invocation_id=CalledAEInvocationId(2),
    calling_ap_invocation_id=CallingAPInvocationId(3),
    calling_ae_invocation_id=CallingAEInvocationId(4),
    mechanism_name=RequestMechanismName(
        (2, 16, 756, 5, 8, 2, 2)  # LLS authentication
    ),
)

# Encode using BER rules
buf = ByteBuffer(bytearray(512))
aarq.put(buf)
print(bytes(buf.extract()).hex())

# Decode back
result = AARQapdu.get(buf.extract())
match result:
    case Error():
        print("Decode failed:", result.err)
    case _:
        decoded = result
        print(decoded.application_context_name)  # (2, 16, 756, 5, 8, 1, 1)
```

### Basic BER Types (X.690)

Create and encode/decode individual ASN.1 types using Basic Encoding Rules.

```python
from COSEMpdu.ber import (
    IntegerType, BooleanType, OctetStringType, NullType,
    BitStringType, EnumeratedType, ObjectIdentifierType,
    SequenceType, SequenceOfType, ChoiceType,
    ExplicitTaggedType, ImplicitTaggedType,
)
from COSEMpdu.x680 import Class, UniversalClassTagAssignments, NamedType, OptionalNamedType, DefaultNamedType, NamedValue
from COSEMpdu.x690 import Tag
from COSEMpdu.byte_buffer import ByteBuffer
from StructResult.result import Error

# --- INTEGER ---
i = IntegerType(42)
buf = ByteBuffer.allocate(16)
i.put(buf)
print(bytes(buf.extract()).hex())  # 02012a  (tag=02, len=01, value=2a)
result = IntegerType.get(ByteBuffer.wrap(bytes.fromhex("02012a")))
match result:
    case Error(): pass
    case _: print(result.value)  # 42

# --- BOOLEAN ---
b = BooleanType(True)
buf = ByteBuffer.allocate(8)
b.put(buf)
print(bytes(buf.extract()).hex())  # 0101ff

# --- OCTET STRING ---
o = OctetStringType(b"hello")
buf = ByteBuffer.allocate(16)
o.put(buf)
print(bytes(buf.extract()).hex())  # 040568656c6c6f

# --- NULL ---
n = NullType()
buf = ByteBuffer.allocate(4)
n.put(buf)
print(bytes(buf.extract()).hex())  # 0500

# --- BIT STRING (primitive) ---
bs = BitStringType((1, 0, 1, 0, 0, 0, 0, 0))  # 8 bits
buf = ByteBuffer.allocate(16)
bs.put(buf)
print(bytes(buf.extract()).hex())  # 030200a0  (tag=03, len=02, unused=00, data=a0)

# --- ENUMERATED ---
class MyEnum(EnumeratedType):
    OFF: Final[int] = 0
    ON: Final[int] = 1
e = MyEnum(1)
buf = ByteBuffer.allocate(8)
e.put(buf)
print(bytes(buf.extract()).hex())  # 0a0101

# --- OBJECT IDENTIFIER ---
oid = ObjectIdentifierType((1, 2, 840, 10045, 2, 1))
buf = ByteBuffer.allocate(16)
oid.put(buf)
print(bytes(buf.extract()).hex())  # 06082a8648ce3d0201

# --- SEQUENCE (subclass with components) ---
class MySequence(SequenceType):
    name: OctetStringType
    age: IntegerType

seq = MySequence(name=OctetStringType(b"Vasily"), age=IntegerType(35))
buf = ByteBuffer.allocate(64)
seq.put(buf)
print(bytes(buf.extract()).hex())  # 300a0406566173696c79020123

# --- SEQUENCE OF ---
Strings = SequenceOfType[OctetStringType]
sof = Strings([OctetStringType(b"one"), OctetStringType(b"two")])
buf = ByteBuffer.allocate(32)
sof.put(buf)
print(bytes(buf.extract()).hex())

# --- CHOICE ---
class Integer2(IntegerType):
    tag = Tag(2, class_=Class.CONTEXT_SPECIFIC)


class OctetString4(OctetStringType):
    tag = Tag(4, class_=Class.CONTEXT_SPECIFIC)


class MyChoice(ChoiceType):
    value: IntegerType2 | OctetStringType4

ch = MyChoice(Integer2(99))
buf = ByteBuffer.allocate(16)
ch.put(buf)
print(bytes(buf.extract()).hex())  # 020163

# --- EXPLICIT tagged ---
class MyExplicitInteger(ExplicitTaggedType, IntegerType):
    tag2 = Tag(class_number=0, class_=Class.Context, constructed=True)
x = MyExplicitInteger(5)
buf = ByteBuffer.allocate(16)
x.put(buf)
print(bytes(buf.extract()).hex())  # a003020105

# --- IMPLICIT tagged ---
class MyImplicitInteger(ImplicitTaggedType, IntegerType):
    tag = Tag(class_number=1, class_=Class.Context)

y = MyImplicitInteger(10)
buf = ByteBuffer.allocate(8)
y.put(buf)
print(bytes(buf.extract()).hex())  # 81010a
```

### Basic A-XDR Types (IEC 61334-6)

Create and encode/decode individual DLMS/COSEM types using A-XDR encoding.

```python
from COSEMpdu.axdr import (
    BooleanType, IntegerType, OctetStringType, BitStringType,
    EnumeratedType, VisibleString, Utf8String,
    SequenceType, ChoiceType, ImplicitTaggedType,
)
from COSEMpdu.x680 import NamedType, OptionalNamedType
from COSEMpdu.byte_buffer import ByteBuffer
from StructResult.result import Error

# --- INTEGER (variable-length) ---
i = IntegerType(100)
buf = ByteBuffer.allocate(8)
i.put(buf)
print(bytes(buf.extract()).hex())  # 64  (short form, 0-127)

j = IntegerType(300)
buf = ByteBuffer.allocate(8)
j.put(buf)
print(bytes(buf.extract()).hex())  # 82012c  (long form: len=2, value=012c)

# --- BOOLEAN ---
b = BooleanType(1)
buf = ByteBuffer.allocate(4)
b.put(buf)
print(bytes(buf.extract()).hex())  # ff

# --- OCTET STRING ---
o = OctetStringType(b"axdr")
buf = ByteBuffer.allocate(16)
o.put(buf)
print(bytes(buf.extract()).hex())  # 0461786472  (len=4, data)

# --- BIT STRING ---
bs = BitStringType((1, 0, 1))
buf = ByteBuffer.allocate(8)
bs.put(buf)
print(bytes(buf.extract()).hex())  # 03a0  (length=3 bits, data=a0)

# --- ENUMERATED ---
e = EnumeratedType(2)
buf = ByteBuffer.allocate(4)
e.put(buf)
print(bytes(buf.extract()).hex())  # 02

# --- VisibleString ---
vs = VisibleString("meter")
buf = ByteBuffer.allocate(16)
vs.put(buf)
print(bytes(buf.extract()).hex())  # 056d65746572

# --- SEQUENCE ---
class MySeq(SequenceType):
    name: OctetStringType
    count: IntegerType

seq = MySeq(name=OctetStringType(b"dev1"), count=IntegerType(5))
buf = ByteBuffer.allocate(32)
seq.put(buf)
print(bytes(buf.extract()).hex())  # 046465763105

# --- CHOICE ---
class Integer2(IntegerType):
    tag = 2


class Boolean1(OctetStringType):
    tag = 1



class MyAxdrChoice(ChoiceType):
    value: Boolean1 | Integer2

ch = MyAxdrChoice(Integer2(42))
buf = ByteBuffer.allocate(8)
ch.put(buf)
print(bytes(buf.extract()).hex())  # 022a
```

## Supported Standards

| Standard | Description |
|----------|-------------|
| **IEC 61334-6:2000** | DLMS/COSEM A-XDR encoding rules |
| **X.680** | ASN.1 notation and type definitions |
| **X.690** | BER (Basic Encoding Rules) |
| **IEC 62056 / EN 13757-1** | DLMS/COSEM application layer |

## Modules

| Module | Purpose |
|--------|---------|
| `COSEMpdu.x680` | ASN.1 type system: base types, tags, constraints |
| `COSEMpdu.axdr` | A-XDR encoding/decoding for DLMS/COSEM |
| `COSEMpdu.x690` | BER Tag and Length encoding primitives |
| `COSEMpdu.ber` | BER encoding/decoding for ASN.1 types |
| `COSEMpdu.data` | COSEM data types (Integer8..Unsigned64, Data, COSEM specific types) |
| `COSEMpdu.apdu` | All COSEM APDU types and services (GET, SET, ACTION, etc.) |
| `COSEMpdu.acse` | ACSE APDU types (AARQ, AARE, RLRQ, RLRE) |
| `COSEMpdu.byte_buffer` | Byte-level read/write buffer |

## Project Links

- **Source code:** [GitHub](https://github.com/youserj/COSEMpdu_project)
- **Issues:** [GitHub Issues](https://github.com/youserj/COSEMpdu_project/issues)

## License

MIT License — see the source repository for details.