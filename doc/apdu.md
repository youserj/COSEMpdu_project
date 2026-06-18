# APDU — COSEM APDU (IEC 62056-5-3)

## Overview

The `apdu` module implements all COSEM APDU (Application Protocol Data Unit) types according to the IEC 62056-5-3 standard and the DLMS/COSEM Green Book 8.3 specification. This is the central module for data exchange in the DLMS/COSEM protocol — all requests and responses are encoded in A-XDR.

APDU messages are embedded in ACSE `UserInformation` and transmitted over a BER session. The module uses A-XDR encoding (`axdr.py`) and COSEM Data types (`data.py`).

- [X.680](x680.md)
- [AXDR](axdr.md)
- [Data](data.md)
- [ACSE](acse.md)

## Module Contents

### Enumerated Types

| Class | Purpose | Primary Codes |
|-------|---------|---------------|
| `DataAccessResult` | Data access result | SUCCESS(0), HARDWARE_FAULT(1), READ_WRITE_DENIED(3), OBJECT_UNDEFINED(4), … (17 codes) |
| `dataAccessResult` | [1] IMPLICIT Data-Access-Result | — |
| `ActionResult` | Action execution result | SUCCESS(0), HARDWARE_FAULT(1), READ_WRITE_DENIED(3), … (12 codes) |

### Base COSEM Types

| Class | Type | Description |
|-------|------|-------------|
| `CosemClassId` | Unsigned16 | COSEM object class identifier |
| `CosemObjectInstanceId` | OCTET STRING SIZE(6) | Instance identifier (OBIS code) |
| `CosemObjectAttributeId` | Integer8 | Attribute identifier |
| `CosemObjectMethodId` | Integer8 | Method identifier |
| `InvokeIdAndPriority` | Unsigned8 | Invoke ID + priority (bit field) |

### Descriptors (SEQUENCE)

| Class | Description | Fields |
|-------|-------------|--------|
| `CosemAttributeDescriptor` | Attribute descriptor | class_id, instance_id, attribute_id |
| `CosemMethodDescriptor` | Method descriptor | class_id, instance_id, method_id |
| `SelectiveAccessDescriptor` | Selective access descriptor | access_selector, access_parameters |
| `CosemAttributeDescriptorWithSelection` | Descriptor with selection | attribute_descriptor, access_selection |

### Access Specification (CHOICE)

| Class | Tag | Description |
|-------|-----|-------------|
| `VariableName` | [2] | Access by name (ObjectName) |
| `ParameterizedAccess` | [4] | Parameterized access |
| `BlockNumberAccess` | [5] | Block number access |
| `ReadDataBlockAccess` | [6] | Read data block access |
| `WriteDataBlockAccess` | [7] | Write data block access |
| `VariableAccessSpecification` | — | CHOICE of all access types |

### xDLMS Services (APDU Messages)

| Service | Purpose |
|---------|---------|
| `GET-Request` | Read attributes |
| `GET-Response` | Read response |
| `SET-Request` | Write attributes |
| `SET-Response` | Write response |
| `ACTION-Request` | Method call |
| `ACTION-Response` | Method call response |
| `Get-Data-Block` | Data block request |
| `Set-Data-Block` | Data block set |

### Information Blocks

| Class | Description |
|-------|-------------|
| `GetRequestBlock` | GET request block (with normal and next) |
| `GetResponseBlock` | GET response block (with normal/next and with data block) |
| `SetRequestBlock` | SET request block (with normal, with block, and with last block) |
| `ActionRequestBlock` | ACTION request block (with normal, with block, and with last block) |

### Conformance and Capabilities

| Class | Description |
|-------|-------------|
| `Conformance` | Client/server capabilities (bit mask) |
| `ConformanceBit` | Conformance bits (GET, SET, ACTION, multiple_references, etc.) |

### Full APDU Messages

| Class | Tag | Purpose |
|-------|-----|---------|
| `GetRequest` | [192] | GET request |
| `GetResponse` | [196] | GET response |
| `SetRequest` | [193] | SET request |
| `SetResponse` | [197] | SET response |
| `ActionRequest` | [195] | ACTION request |
| `ActionResponse` | [199] | ACTION response |

## InvokeIdAndPriority Structure

1-byte bit field:

```
Bits:  7  6  5  4  3  2  1  0
      [ invoke_id  ] [S] [P] [0]
       
invoke_id  (4 bits): Invoke identifier (0-15)
S (1 bit):  Service class (1=confirmed, 0=unconfirmed)
P (1 bit):  Priority (1=high, 0=normal)
```

```python
from COSEMpdu.apdu import InvokeIdAndPriority

idp = InvokeIdAndPriority.from_bits(
    invoke_id=1,
    service_class="confirmed",
    priority="high"
)
```

## Usage

### Building a GET Request

```python
from COSEMpdu.apdu import (
    GetRequest, CosemAttributeDescriptor, 
    CosemClassId, CosemObjectInstanceId, CosemObjectAttributeId,
    InvokeIdAndPriority
)
from COSEMpdu.byte_buffer import ByteBuffer

descriptor = CosemAttributeDescriptor(
    class_id=CosemClassId(7),    # Register
    instance_id=CosemObjectInstanceId(b'\x01\x00\x01\x08\x00\xFF'),
    attribute_id=CosemObjectAttributeId(2)  # value
)

request = GetRequest(
    invoke_id_and_priority=InvokeIdAndPriority.from_bits(1, "confirmed", "normal"),
    attribute_descriptor=descriptor
)

buf = ByteBuffer()
request.put(buf)
print(buf.hex())
```

### Handling a GET Response

```python
from COSEMpdu.apdu import GetResponse
from COSEMpdu.data import Data, DoubleLongUnsigned
from COSEMpdu.byte_buffer import ByteBuffer

buf = ByteBuffer(received_bytes)
response = GetResponse.get(buf)

if isinstance(response.result.value, DataAccessResult):
    if int(response.result) == 0:  # SUCCESS
        value = response.data.value  # DoubleLongUnsigned or another Data type
```

### Working with Conformance

```python
from COSEMpdu.apdu import Conformance, ConformanceBit

conf = Conformance()
conf.set(ConformanceBit.GET)
conf.set(ConformanceBit.SET)
conf.set(ConformanceBit.ACTION)

buf = ByteBuffer()
conf.put(buf)
```

### DataAccessResult Codes

```python
from COSEMpdu.apdu import DataAccessResult

# Primary error codes
DataAccessResult.SUCCESS                  # 0
DataAccessResult.HARDWARE_FAULT           # 1
DataAccessResult.TEMPORARY_FAILURE        # 2
DataAccessResult.READ_WRITE_DENIED        # 3
DataAccessResult.OBJECT_UNDEFINED         # 4
DataAccessResult.TYPE_UNMATCHED           # 12
DataAccessResult.SCOPE_OF_ACCESS_VIOLATED # 13
```

## APDU Exchange Diagram

```
Client                                        Server
  |                                             |
  |--- GET-Request [192] ---------------------->|
  |   + CosemAttributeDescriptor                |
  |     + class_id: 7 (Register)                |
  |     + instance_id: OBIS                     |
  |     + attribute_id: 2 (value)               |
  |                                             |
  |<--- GET-Response [196] ---------------------|
  |   + result: SUCCESS                         |
  |   + data: DoubleLongUnsigned(230000)        |
  |                                             |
  |--- SET-Request [193] ---------------------->|
  |   + attribute_descriptor                    |
  |   + data: DoubleLongUnsigned(231000)        |
  |                                             |
  |<--- SET-Response [197] ---------------------|
  |   + result: SUCCESS                         |
```

## Related Links

- [X.680](x680.md) — base ASN.1 types
- [AXDR](axdr.md) — A-XDR type implementations
- [Data](data.md) — COSEM Data types
- [ACSE](acse.md) — ACSE APDU (transport layer)
- [BER](ber.md) — BER type implementations (used for Conformance)
- [ByteBuffer](byte_buffer.md) — helper class for working with bytes