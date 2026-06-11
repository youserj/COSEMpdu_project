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