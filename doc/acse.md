# ACSE — ACSE APDU (ISO/IEC 10035-1)

## Overview

The `acse` module implements ACSE (Association Control Service Element) APDU types according to the ISO/IEC 10035-1 standard and the DLMS/COSEM specification (Green Book 8.3). ACSE messages are used to establish, confirm, and release a logical connection (association) between a DLMS/COSEM client and server.

All ACSE types use BER encoding (X.690) and are built on types from `x680` and `ber`.

- [X.680](x680.md)
- [X690](x690.md)
- [BER](ber.md)
- [AXDR](axdr.md)
- [APDU](apdu.md)

## Module Contents

### Base ACSE Types

| Class | ASN.1 Type | Encoding |
|-------|------------|----------|
| `ApplicationContextName` | ObjectIdentifier | EXPLICIT [1] |
| `APTitle` | OCTET STRING | — |
| `AEQualifier` | OCTET STRING | — |
| `APInvocationIdentifier` | INTEGER | — |
| `AEInvocationIdentifier` | INTEGER | — |
| `ACSERequirements` | BIT STRING | Authentication (bit 0) |
| `MechanismName` | OBJECT IDENTIFIER | — |
| `Charstring` | GraphicString | IMPLICIT [0] |
| `BitString` | BIT STRING | IMPLICIT [1] |
| `AuthenticationValue` | CHOICE | Charstring / BitString |
| `ImplementationInformation` | GraphicString | IMPLICIT [29] |
| `UserInformation` | OCTET STRING | EXPLICIT [30] |

### Association Results

| Class | Description |
|-------|-------------|
| `Result` | EXPLICIT [2] — association result |
| `ACSEServiceUser` | EXPLICIT [1] — service user diagnostics (14 codes) |
| `ACSEServiceProvider` | EXPLICIT [2] — service provider diagnostics (2 codes) |
| `ResultSourceDiagnostic` | EXPLICIT [3] CHOICE — final diagnostic |

### Association Release Types

| Class | Description |
|-------|-------------|
| `RequestReason` | IMPLICIT [0] — release request reason |
| `ResponseReason` | IMPLICIT [0] — release response reason |
| `ProtocolVersion` | IMPLICIT [0] BIT STRING — protocol version |

### AARQ Fields (Association Request)

| Class | Tag | Type |
|-------|-----|------|
| `CalledAPTitle` | EXPLICIT [2] | Called AP-title |
| `CallingAPTitle` | EXPLICIT [6] | Calling AP-title |
| `CalledAEQualifier` | EXPLICIT [3] | Called AE-qualifier |
| `CallingAEQualifier` | EXPLICIT [7] | Calling AE-qualifier |
| `CalledAPInvocationId` | EXPLICIT [4] | Called AP-invocation-id |
| `CallingAPInvocationId` | EXPLICIT [8] | Calling AP-invocation-id |
| `CalledAEInvocationId` | EXPLICIT [5] | Called AE-invocation-id |
| `CallingAEInvocationId` | EXPLICIT [9] | Calling AE-invocation-id |
| `SenderACSERequirements` | IMPLICIT [10] | Sender ACSE-requirements |
| `RequestMechanismName` | IMPLICIT [11] | Mechanism-name |
| `CallingAuthenticationValue` | EXPLICIT [12] | Authentication-value |

### APDU Messages

| Class | ASN.1 Type | Purpose |
|-------|------------|---------|
| `AARQapdu` | [APPLICATION 0] SEQUENCE | Association request |
| `AAREapdu` | [APPLICATION 1] SEQUENCE | Association response |
| `RLRQapdu` | [APPLICATION 2] SEQUENCE | Release request |
| `RLREapdu` | [APPLICATION 3] SEQUENCE | Release response |

### Result Error Codes

| Constant | Code | Description |
|----------|------|-------------|
| `ACCEPTED` | 0 | Accepted |
| `REJECTED_PERMANENT` | 1 | Rejected (permanent) |
| `REJECTED_TRANSIENT` | 2 | Rejected (transient) |

### ACSEServiceUser Codes

| Code | Constant |
|------|----------|
| 0 | NULL |
| 1 | NO_REASON_GIVEN |
| 2 | APPLICATION_CONTEXT_NAME_NOT_SUPPORTED |
| 3 | CALLING_AP_TITLE_NOT_RECOGNIZED |
| 4 | CALLING_AP_INVOCATION_IDENTIFIER_NOT_RECOGNIZED |
| 5 | CALLING_AE_QUALIFIER_NOT_RECOGNIZED |
| 6 | CALLING_AE_INVOCATION_IDENTIFIER_NOT_RECOGNIZED |
| 7 | CALLED_AP_TITLE_NOT_RECOGNIZED |
| 8 | CALLED_AP_INVOCATION_IDENTIFIER_NOT_RECOGNIZED |
| 9 | CALLED_AE_QUALIFIER_NOT_RECOGNIZED |
| 10 | CALLED_AE_INVOCATION_IDENTIFIER_NOT_RECOGNIZED |
| 11 | AUTHENTICATION_MECHANISM_NAME_NOT_RECOGNISED |
| 12 | AUTHENTICATION_MECHANISM_NAME_REQUIRED |
| 13 | AUTHENTICATION_FAILURE |
| 14 | AUTHENTICATION_REQUIRED |

### ACSEServiceProvider Codes

| Code | Constant |
|------|----------|
| 0 | NULL |
| 1 | NO_REASON_GIVEN |
| 2 | NO_COMMON_ACSE_VERSION |

## How It Works

### Association Establishment Flow

```
Client                        Server
  |                             |
  |--- AARQapdu (request) ----->|
  |                             |
  |<--- AAREapdu (response) ----|
  |                             |
  |--- COSEM APDU exchange ---->|
  |                             |
  |--- RLRQapdu (release) ----->|
  |                             |
  |<--- RLREapdu (confirm) -----|
```

### ACSE Message Encoding

All ACSE messages are encoded in BER (X.690). Example AARQ structure:

```
[APPLICATION 0, CONSTRUCTED]  (AARQ tag)
  Length (entire message)
  +-- protocol_version [0] BIT STRING
  +-- application_context_name [1] EXPLICIT OID
  +-- called_ap_title [2] EXPLICIT OCTET STRING (optional)
  +-- ... (other fields)
  +-- user_information [30] EXPLICIT OCTET STRING
       Contains COSEM APDU in A-XDR
```

## Usage

### Encoding an AARQ Request

```python
from COSEMpdu.acse import AARQapdu, ApplicationContextName, ProtocolVersion
from COSEMpdu.byte_buffer import ByteBuffer

aarq = AARQapdu(
    application_context_name=ApplicationContextName("2.16.1.1.0.0.1.2"),
    protocol_version=ProtocolVersion((0,)),
)

buf = ByteBuffer()
aarq.put(buf)
print(buf.hex())
```

### Decoding an AARE Response

```python
from COSEMpdu.acse import AAREapdu
from COSEMpdu.byte_buffer import ByteBuffer

buf = ByteBuffer(received_bytes)
aare = AAREapdu.get(buf)
print(aare.result)  # Result.ACCEPTED or error code
```

## Related Links

- [X.680](x680.md) — base ASN.1 types
- [X690](x690.md) — low-level TLV encoding
- [BER](ber.md) — BER type implementations
- [APDU](apdu.md) — COSEM APDU (nested in UserInformation)
- [ByteBuffer](byte_buffer.md) — helper class for working with bytes