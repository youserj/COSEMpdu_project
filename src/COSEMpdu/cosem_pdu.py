"""
COSEM PDU Types Implementation
Based on COSEMpdu_GB83.txt (Green Book 8.3)
Implements A-XDR encoding/decoding according to IEC 61334-6
"""

from dataclasses import dataclass
from typing import ClassVar, Self, Optional, Union, Any
from enum import IntEnum
from . import x690
from .x680.tagged_type import TaggingMode
from .x680.type import (
    INTEGER,
    Type,
    TYPE_VALUE,
    SEQUENCE_OF,
    Constraint,
    SizeConstraint,
    NamedType,
    OptionalNamedType,
    DefaultNamedType
    )
from . import x680
from .x680 import (
    Constraint,
    ValueRange,
    NamedBitList,
    NamedBit,
    NamedNumberList,
    NamedNumber
)
from . import axdr
from . import ber
from .byte_buffer import ByteBuffer
from .x680.tag import Class, UniversalClassTagAssignments


# ============================================================================
# -- Useful types
# ============================================================================


@dataclass
class Integer8(axdr.IntegerType):  # approve
    constraint = Constraint(constraint_spec=ValueRange(-128, 127))

@dataclass
class Integer16(axdr.IntegerType):  # approve
    constraint = Constraint(constraint_spec=ValueRange(-32768, 32767))


@dataclass
class Integer32(axdr.IntegerType):  # approve
    constraint = Constraint(constraint_spec=ValueRange(-2147483648, 2147483647))


@dataclass
class Integer64(axdr.IntegerType):  # approve
    constraint = Constraint(constraint_spec=ValueRange(-9223372036854775808, 9223372036854775807))


@dataclass
class Unsigned8(axdr.IntegerType):  # approve
    constraint = Constraint(constraint_spec=ValueRange(0, 255))


@dataclass
class Unsigned16(axdr.IntegerType):  # approve
    constraint = Constraint(constraint_spec=ValueRange(0, 65535))


@dataclass
class Unsigned32(axdr.IntegerType):  # approve
    constraint = Constraint(constraint_spec=ValueRange(0, 4294967295))


@dataclass
class Unsigned64(axdr.IntegerType):  # approve
    constraint = Constraint(constraint_spec=ValueRange(0, 18446744073709551615))

# ============================================================================
# xDLMS APDU Types (COSEMpdu_GB83.txt)
# ============================================================================


@dataclass
class ObjectName(Integer16):
    """ObjectName"""



# @dataclass
# class DataAccessResult(ber.EnumeratedType):
#     """
#     Data-Access-Result ::= ENUMERATED
#     Data access result codes per COSEMpdu_GB83.txt
#     """
#     value: int = 0
    
#     class Result(IntEnum):
#         SUCCESS = 0
#         HARDWARE_FAULT = 1
#         TEMPORARY_FAILURE = 2
#         READ_WRITE_DENIED = 3
#         OBJECT_UNDEFINED = 4
#         OBJECT_CLASS_INCONSISTENT = 9
#         OBJECT_UNAVAILABLE = 11
#         TYPE_UNMATCHED = 12
#         SCOPE_OF_ACCESS_VIOLATED = 13
#         DATA_BLOCK_UNAVAILABLE = 14
#         LONG_GET_ABORTED = 15
#         NO_LONG_GET_IN_PROGRESS = 16
#         LONG_SET_ABORTED = 17
#         NO_LONG_SET_IN_PROGRESS = 18
#         DATA_BLOCK_NUMBER_INVALID = 19
#         OTHER_REASON = 250


# @dataclass
# class Action-Result(ber.EnumeratedType):
#     """
#     Action-Result ::= ENUMERATED
#     Action result codes per COSEMpdu_GB83.txt
#     """
#     value: int = 0
    
#     class Result(IntEnum):
#         SUCCESS = 0
#         HARDWARE_FAULT = 1
#         TEMPORARY_FAILURE = 2
#         READ_WRITE_DENIED = 3
#         OBJECT_UNDEFINED = 4
#         OBJECT_CLASS_INCONSISTENT = 9
#         OBJECT_UNAVAILABLE = 11
#         TYPE_UNMATCHED = 12
#         SCOPE_OF_ACCESS_VIOLATED = 13
#         DATA_BLOCK_UNAVAILABLE = 14
#         LONG_ACTION_ABORTED = 15
#         NO_LONG_ACTION_IN_PROGRESS = 16
#         OTHER_REASON = 250


# # ============================================================================
# # Invoke ID and Priority Types (COSEMpdu_GB83.txt)
# # ============================================================================

# @dataclass
# class Invoke-Id-And-Priority(Unsigned8):
#     """
#     Invoke-Id-And-Priority ::= Unsigned8
#     Bit layout:
#         bits 0-3: invoke-id
#         bits 4-5: reserved
#         bit 6: service-class (0=Unconfirmed, 1=Confirmed)
#         bit 7: priority (0=Normal, 1=High)
#     """
#     value: int = 0
    
#     @property
#     def invoke_id(self) -> int:
#         return self.value & 0x0F
    
#     @property
#     def service_class(self) -> bool:
#         return bool(self.value & 0x40)
    
#     @property
#     def priority(self) -> bool:
#         return bool(self.value & 0x80)
    
#     @classmethod
#     def create(cls, invoke_id: int, confirmed: bool = False, high_priority: bool = False) -> Self:
#         value = (invoke_id & 0x0F)
#         if confirmed:
#             value |= 0x40
#         if high_priority:
#             value |= 0x80
#         return cls(value)


# @dataclass
# class Long-Invoke-Id-And-Priority(Unsigned32):
#     """
#     Long-Invoke-Id-And-Priority ::= Unsigned32
#     Bit layout:
#         bits 0-23: long-invoke-id
#         bits 24-27: reserved
#         bit 28: self-descriptive
#         bit 29: processing-option
#         bit 30: service-class
#         bit 31: priority
#     """
#     value: int = 0
    
#     @property
#     def long_invoke_id(self) -> int:
#         return self.value & 0x00FFFFFF
    
#     @property
#     def self_descriptive(self) -> bool:
#         return bool(self.value & 0x10000000)
    
#     @property
#     def processing_option(self) -> bool:
#         return bool(self.value & 0x20000000)
    
#     @property
#     def service_class(self) -> bool:
#         return bool(self.value & 0x40000000)
    
#     @property
#     def priority(self) -> bool:
#         return bool(self.value & 0x80000000)


# # ============================================================================
# # COSEM Attribute/Method Descriptors (COSEMpdu_GB83.txt)
# # ============================================================================

# @dataclass
# class Cosem-Class-Id(Unsigned16):
#     """COSEM class identifier (e.g., 1=Data, 3=Register, 7=ExtendedRegister, etc.)"""
#     value: int = 0


# @dataclass
# class Cosem-Object-Instance-Id(ber.OctetStringType):
#     """COSEM object instance ID (6 octets for LN, 2 octets for SN)"""
#     value: bytes = b'\x00\x00\x00\x00\x00\x00'
    
#     def __post_init__(self) -> None:
#         if len(self.value) != 6:
#             raise ValueError(f"Cosem-Object-Instance-Id must be 6 octets, got {len(self.value)}")


# @dataclass
# class Cosem-Object-Attribute-Id(Integer8):
#     """COSEM attribute identifier (1-255)"""
#     value: int = 0
    
#     def __post_init__(self) -> None:
#         if not (1 <= self.value <= 255):
#             raise ValueError(f"Cosem-Object-Attribute-Id must be 1..255, got {self.value}")


# @dataclass
# class Cosem-Object-Method-Id(Integer8):
#     """COSEM method identifier (1-255)"""
#     value: int = 0
    
#     def __post_init__(self) -> None:
#         if not (1 <= self.value <= 255):
#             raise ValueError(f"Cosem-Object-Method-Id must be 1..255, got {self.value}")


# @dataclass
# class Cosem-Attribute-Descriptor(axdr.SequenceType):
#     """
#     Cosem-Attribute-Descriptor ::= SEQUENCE {class-id, instance-id, attribute-id}
#     COSEM attribute descriptor for GET/SET services
#     """
#     components = (
#         x680.NamedType('class-id', Cosem-Class-Id),
#         x680.NamedType('instance-id', Cosem-Object-Instance-Id),
#         x680.NamedType('attribute-id', Cosem-Object-Attribute-Id),
#     )
    
#     class_id: Cosem-Class-Id = field(default_factory=Cosem-Class-Id)
#     instance_id: Cosem-Object-Instance-Id = field(default_factory=Cosem-Object-Instance-Id)
#     attribute_id: Cosem-Object-Attribute-Id = field(default_factory=Cosem-Object-Attribute-Id)


# @dataclass
# class Cosem-Method-Descriptor(axdr.SequenceType):
#     """
#     Cosem-Method-Descriptor ::= SEQUENCE {class-id, instance-id, method-id}
#     COSEM method descriptor for ACTION services
#     """
#     components = (
#         x680.NamedType('class-id', Cosem-Class-Id),
#         x680.NamedType('instance-id', Cosem-Object-Instance-Id),
#         x680.NamedType('method-id', Cosem-Object-Method-Id),
#     )
    
#     class_id: Cosem-Class-Id = field(default_factory=Cosem-Class-Id)
#     instance_id: Cosem-Object-Instance-Id = field(default_factory=Cosem-Object-Instance-Id)
#     method_id: Cosem-Object-Method-Id = field(default_factory=Cosem-Object-Method-Id)


# # ============================================================================
# # Read/Write Request/Response (COSEMpdu_GB83.txt)
# # ============================================================================

# @dataclass
# class Variable-Access-Specification(axdr.ChoiceType):
#     """
#     Variable-Access-Specification ::= CHOICE
#     Variable access specification for Read/Write services
#     """
#     alternatives: ClassVar = {
#         2: ObjectName,                    # variable-name
#         4: axdr.SequenceType,             # parameterized-access
#         5: axdr.SequenceType,             # block-number-access
#         6: axdr.SequenceType,             # read-data-block-access
#         7: axdr.SequenceType,             # write-data-block-access
#     }
#     selected_tag: int = 0
#     value: Union[ObjectName, axdr.SequenceType] = field(default_factory=ObjectName)


# @dataclass
# class ReadRequest(axdr.SequenceOfType):
#     """
#     ReadRequest ::= SEQUENCE OF Variable-Access-Specification
#     Read request per COSEMpdu_GB83.txt
#     """
#     value: tuple[Variable-Access-Specification, ...] = ()
#     component_type: ClassVar[type] = Variable-Access-Specification
#     fixed_length: Optional[int] = None


# @dataclass
# class ReadResponse(axdr.SequenceOfType):
#     """
#     ReadResponse ::= SEQUENCE OF CHOICE {data, data-access-error, ...}
#     Read response per COSEMpdu_GB83.txt
#     """
#     value: tuple[axdr.ChoiceType, ...] = ()
#     component_type: ClassVar[type] = axdr.ChoiceType
#     fixed_length: Optional[int] = None


# @dataclass
# class WriteRequest(axdr.SequenceType):
#     """
#     WriteRequest ::= SEQUENCE {variable-access-specification, list-of-data}
#     Write request per COSEMpdu_GB83.txt
#     """
#     components = (
#         x680.NamedType('variable-access-specification', axdr.SequenceOfType),
#         x680.NamedType('list-of-data', axdr.SequenceOfType),
#     )
    
#     variable_access_specification: axdr.SequenceOfType = field(
#         default_factory=lambda: axdr.SequenceOfType(component_type=Variable-Access-Specification)
#     )
#     list_of_ axdr.SequenceOfType = field(
#         default_factory=lambda: axdr.SequenceOfType(component_type=Data)
#     )


# @dataclass
# class WriteResponse(axdr.SequenceOfType):
#     """
#     WriteResponse ::= SEQUENCE OF CHOICE {success, data-access-error, block-number}
#     Write response per COSEMpdu_GB83.txt
#     """
#     value: tuple[axdr.ChoiceType, ...] = ()
#     component_type: ClassVar[type] = axdr.ChoiceType
#     fixed_length: Optional[int] = None


# # ============================================================================
# # XDLMS-APDU Top-Level Choice (COSEMpdu_GB83.txt)
# # ============================================================================

# @dataclass
# class XDLMS-APDU(axdr.ChoiceType):
#     """
#     XDLMS-APDU ::= CHOICE
#     Top-level xDLMS APDU choice per COSEMpdu_GB83.txt
#     Tags are context-specific for A-XDR encoding
#     """
#     alternatives: ClassVar = {
#         # Standardised xDLMS PDUs (no ciphering)
#         1: InitiateRequest,
#         5: ReadRequest,
#         6: WriteRequest,
#         8: InitiateResponse,
#         12: ReadResponse,
#         13: WriteResponse,
#         14: ConfirmedServiceError,
#         15: axdr.SequenceType,  # data-notification
#         22: UnconfirmedWriteRequest,
#         24: InformationReportRequest,
        
#         # With global ciphering (OCTET STRING)
#         33: ber.OctetStringType,  # glo-initiateRequest
#         37: ber.OctetStringType,  # glo-readRequest
#         38: ber.OctetStringType,  # glo-writeRequest
#         40: ber.OctetStringType,  # glo-initiateResponse
#         44: ber.OctetStringType,  # glo-readResponse
#         45: ber.OctetStringType,  # glo-writeResponse
#         46: ber.OctetStringType,  # glo-confirmedServiceError
#         54: ber.OctetStringType,  # glo-unconfirmedWriteRequest
#         56: ber.OctetStringType,  # glo-informationReportRequest
        
#         # With dedicated ciphering (OCTET STRING)
#         65: ber.OctetStringType,  # ded-initiateRequest
#         69: ber.OctetStringType,  # ded-readRequest
#         70: ber.OctetStringType,  # ded-writeRequest
#         72: ber.OctetStringType,  # ded-initiateResponse
#         76: ber.OctetStringType,  # ded-readResponse
#         77: ber.OctetStringType,  # ded-writeResponse
#         78: ber.OctetStringType,  # ded-confirmedServiceError
#         86: ber.OctetStringType,  # ded-unconfirmedWriteRequest
#         88: ber.OctetStringType,  # ded-informationReportRequest,
        
#         # LN referencing (no ciphering)
#         192: axdr.SequenceType,   # get-request
#         193: axdr.SequenceType,   # set-request
#         194: axdr.SequenceType,   # event-notification-request
#         195: axdr.SequenceType,   # action-request
#         196: axdr.SequenceType,   # get-response
#         197: axdr.SequenceType,   # set-response
#         199: axdr.SequenceType,   # action-response,
        
#         # LN referencing (global ciphering)
#         200: ber.OctetStringType,  # glo-get-request
#         201: ber.OctetStringType,  # glo-set-request
#         202: ber.OctetStringType,  # glo-event-notification-request
#         203: ber.OctetStringType,  # glo-action-request
#         204: ber.OctetStringType,  # glo-get-response
#         205: ber.OctetStringType,  # glo-set-response
#         207: ber.OctetStringType,  # glo-action-response,
        
#         # LN referencing (dedicated ciphering)
#         208: ber.OctetStringType,  # ded-get-request
#         209: ber.OctetStringType,  # ded-set-request
#         210: ber.OctetStringType,  # ded-event-notification-request
#         211: ber.OctetStringType,  # ded-actionRequest
#         212: ber.OctetStringType,  # ded-get-response
#         213: ber.OctetStringType,  # ded-set-response
#         215: ber.OctetStringType,  # ded-action-response,
        
#         # Exception and access
#         216: axdr.SequenceType,   # exception-response
#         217: axdr.SequenceType,   # access-request
#         218: axdr.SequenceType,   # access-response,
        
#         # General APDUs
#         219: axdr.SequenceType,   # general-glo-ciphering
#         220: axdr.SequenceType,   # general-ded-ciphering
#         221: axdr.SequenceType,   # general-ciphering
#         223: axdr.SequenceType,   # general-signing
#         224: axdr.SequenceType,   # general-block-transfer
#     }
#     selected_tag: int = 0
#     value: Union[
#         InitiateRequest,
#         ReadRequest,
#         WriteRequest,
#         InitiateResponse,
#         ReadResponse,
#         WriteResponse,
#         ConfirmedServiceError,
#         ber.OctetStringType,
#         axdr.SequenceType,
#     ] = field(default_factory=InitiateRequest)


# # ============================================================================
# # Helper Functions
# # ============================================================================

# def encode_initiate_request_axdr(request: InitiateRequest) -> bytes:
#     """
#     Encode InitiateRequest in A-XDR for user-information field
#     Per COSEMpdu_GB83.txt: "encoded in A-XDR, and then encoding the resulting OCTET STRING in BER"
#     """
#     buf = ByteBuffer.allocate(256)
#     request.put_contents(buf)
#     return bytes(buf.frozen())


# def decode_initiate_request_axdr( bytes) -> InitiateRequest:
#     """Decode InitiateRequest from A-XDR"""
#     buf = ByteBuffer.wrap(data)
#     return InitiateRequest.get_contents(buf)


# def encode_initiate_response_axdr(response: InitiateResponse) -> bytes:
#     """Encode InitiateResponse in A-XDR for user-information field"""
#     buf = ByteBuffer.allocate(256)
#     response.put_contents(buf)
#     return bytes(buf.frozen())


# def decode_initiate_response_axdr( bytes) -> InitiateResponse:
#     """Decode InitiateResponse from A-XDR"""
#     buf = ByteBuffer.wrap(data)
#     return InitiateResponse.get_contents(buf)


# def create_aarq_with_initiate_request(
#     initiate_request: InitiateRequest,
#     application_context: bytes = b'\x60\x85\x74\x05\x08\x01\x01',  # DLMS/COSEM context
# ) -> AARQ-apdu:
#     """
#     Create AARQ APDU with InitiateRequest in user-information field
#     Per COSEMpdu_GB83.txt: user-information carries InitiateRequest encoded in A-XDR, then BER
#     """
#     # Encode InitiateRequest in A-XDR
#     axdr_data = encode_initiate_request_axdr(initiate_request)
    
#     # Create AARQ with A-XDR data in user-information (will be BER-encoded)
#     return AARQ-apdu(
#         application_context_name=Application-context-name(application_context),
#         user_information=Association-information(axdr_data),
#     )


# def create_aare_with_initiate_response(
#     initiate_response: InitiateResponse,
#     result: Association-result.Result = Association-result.Result.ACCEPTED,
#     application_context: bytes = b'\x60\x85\x74\x05\x08\x01\x01',
# ) -> AARE-apdu:
#     """
#     Create AARE APDU with InitiateResponse in user-information field
#     Per COSEMpdu_GB83.txt: user-information carries InitiateResponse or ConfirmedServiceError
#     """
#     # Encode InitiateResponse in A-XDR
#     axdr_data = encode_initiate_response_axdr(initiate_response)
    
#     return AARE-apdu(
#         application_context_name=Application-context-name(application_context),
#         result=Association-result(result.value),
#         result_source_diagnostic=Associate-source-diagnostic(
#             selected_tag=1,
#             value=ber.IntegerType(0)  # null
#         ),
#         user_information=Association-information(axdr_data),
#     )
