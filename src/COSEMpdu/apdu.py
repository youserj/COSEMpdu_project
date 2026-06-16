"""
COSEM PDU Types Implementation
Based on COSEMpdu_GB83.txt (Green Book 8.3)
Implements A-XDR encoding/decoding according to IEC 61334-6
"""
from typing import Final, Optional, Self, Literal, ClassVar, TypeAlias, Union
from dataclasses import dataclass
from StructResult.result import Error
from .x680 import InitError
from .data import Data, SequenceOfData, ObjectName, Unsigned16, Unsigned8, Unsigned32, Integer8
from .axdr import (
    ConstrainedOctetStringType, OctetStringType, SequenceOfType, EnumeratedType, SequenceType,
    BooleanType, ChoiceType, NullType, GeneralizedTime, NullType0, ImplicitTaggedType
)
from . import ber
from . import x690
from .x680 import Class, ConstraintSpec, SizeConstraint


# =============================================================================
# ENUMERATED Types (A-XDR: encoded as fixed-length unsigned integer in 1 byte)
# =============================================================================


class DataAccessResult(EnumeratedType):
    """Data-Access-Result"""
    SUCCESS: Final[int] = 0
    HARDWARE_FAULT: Final[int] = 1
    TEMPORARY_FAILURE: Final[int] = 2
    READ_WRITE_DENIED: Final[int] = 3
    OBJECT_UNDEFINED: Final[int] = 4
    OBJECT_CLASS_INCONSISTENT: Final[int] = 9
    OBJECT_UNAVAILABLE: Final[int] = 11
    TYPE_UNMATCHED: Final[int] = 12
    SCOPE_OF_ACCESS_VIOLATED: Final[int] = 13
    DATA_BLOCK_UNAVAILABLE: Final[int] = 14
    LONG_GET_ABORTED: Final[int] = 15
    NO_LONG_GET_IN_PROGRESS: Final[int] = 16
    LONG_SET_ABORTED: Final[int] = 17
    NO_LONG_SET_IN_PROGRESS: Final[int] = 18
    DATA_BLOCK_NUMBER_INVALID: Final[int] = 19
    OTHER_REASON: Final[int] = 250


class dataAccessResult(ImplicitTaggedType, DataAccessResult):
    """data-access-result [1] IMPLICIT Data-Access-Result"""
    tag: ClassVar[int] = 1


class ActionResult(EnumeratedType):
    """Action-Result"""
    SUCCESS: Final[int] = 0
    HARDWARE_FAULT: Final[int] = 1
    TEMPORARY_FAILURE: Final[int] = 2
    READ_WRITE_DENIED: Final[int] = 3
    OBJECT_UNDEFINED: Final[int] = 4
    OBJECT_CLASS_INCONSISTENT: Final[int] = 9
    OBJECT_UNAVAILABLE: Final[int] = 11
    TYPE_UNMATCHED: Final[int] = 12
    SCOPE_OF_ACCESS_VIOLATED: Final[int] = 13
    DATA_BLOCK_UNAVAILABLE: Final[int] = 14
    LONG_ACTION_ABORTED: Final[int] = 15
    NO_LONG_ACTION_IN_PROGRESS: Final[int] = 16
    OTHER_REASON: Final[int] = 250


# =============================================================================
# Basic Types (from COSEMpdu_GB83.txt)
# =============================================================================


class CosemClassId(Unsigned16):
    """Cosem-Class-Id"""


class CosemObjectInstanceId(ConstrainedOctetStringType):
    """Cosem-Object-Instance-Id"""
    constraint_spec = SizeConstraint(6)


class CosemObjectAttributeId(Integer8):
    """Cosem-Object-Attribute-Id"""


class CosemObjectMethodId(Integer8):
    """Cosem-Object-Method-Id"""


# =============================================================================
# SEQUENCE Types for xDLMS Data Transfer Services
# =============================================================================


@dataclass
class CosemAttributeDescriptor(SequenceType):
    """Cosem-Attribute-Descriptor"""
    class_id: CosemClassId
    instance_id: CosemObjectInstanceId
    attribute_id: CosemObjectAttributeId


@dataclass
class CosemMethodDescriptor(SequenceType):
    """Cosem-Method-Descriptor"""
    class_id: CosemClassId
    instance_id: CosemObjectInstanceId
    method_id: CosemObjectMethodId


@dataclass
class SelectiveAccessDescriptor(SequenceType):
    """Selective-Access-Descriptor"""
    access_selector: Unsigned8
    access_parameters: Data
    selector_parameters: ClassVar[dict[int, type[ImplicitTaggedType]]] = {}

    @classmethod
    def new(cls, access_selector: Unsigned8, access_parameters: Data) -> Self | Error:
        if (expected_type := cls.selector_parameters.get(int(access_selector))) is None:
            return Error.from_e(InitError(f"Unknown access-selector value: {access_selector}"))
        if not isinstance(access_parameters.value, expected_type):
            return Error.from_e(InitError(f"Expected access-parameters type {expected_type.__name__} for selector {access_selector}, got {type(access_parameters).__name__}"))
        return cls(access_selector, access_parameters)


@dataclass
class CosemAttributeDescriptorWithSelection(SequenceType):
    """Cosem-Attribute-Descriptor-With-Selection"""
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection: Optional[SelectiveAccessDescriptor] = None


# =============================================================================
# Variable-Access-Specification CHOICE
# =============================================================================


class VariableName(ImplicitTaggedType, ObjectName):
    """variable-name [2] IMPLICIT ObjectName"""
    tag = 2


@dataclass
class ParameterizedAccess(ImplicitTaggedType, SequenceType):
    """parameterized-access [4] IMPLICIT Parameterized-Access"""
    tag: ClassVar[int] = 4
    variable_name: ObjectName
    selector: Unsigned8
    parameter: Data


@dataclass
class BlockNumberAccess(ImplicitTaggedType, SequenceType):
    """block-number-access [5] IMPLICIT Block-Number-Access"""
    tag: ClassVar[int] = 5
    block_number: Unsigned16


@dataclass
class ReadDataBlockAccess(ImplicitTaggedType, SequenceType):
    """read-data-block-access [6] IMPLICIT Read-Data-Block-Access"""
    tag: ClassVar[int] = 6
    last_block: BooleanType
    block_number: Unsigned16
    raw_data: OctetStringType


@dataclass
class WriteDataBlockAccess(ImplicitTaggedType, SequenceType):
    """write-data-block-access [7] IMPLICIT Write-Data-Block-Access"""
    tag: ClassVar[int] = 7
    last_block: BooleanType
    block_number: Unsigned16


class VariableAccessSpecification(ChoiceType):
    """Variable-Access-Specification"""
    value: VariableName | ParameterizedAccess | BlockNumberAccess | ReadDataBlockAccess | WriteDataBlockAccess


# =============================================================================
# Invoke-Id-And-Priority Types
# =============================================================================


class InvokeIdAndPriority(Unsigned8):
    """Invoke-Id-And-Priority"""

    @classmethod
    def from_bits(
        cls,
        invoke_id: int,
        service_class: Literal["confirmed", "unconfirmed"] = "confirmed",
        priority: Literal["high", "normal"] = "normal"
    ) -> Self:
        """Create from individual bit fields"""
        if not (0 <= invoke_id <= 15):
            raise ValueError(f"invoke_id must be 0-15, got {invoke_id}")
        value = (invoke_id << 4) | (1 if service_class == "confirmed" else 0) << 1 | (1 if priority == "high" else 0)
        return cls(value & 0xFF)

    @property
    def invoke_id(self) -> int:
        """Extract invoke-id (bits 0-3)"""
        return (self.value >> 4) & 0x0F

    def is_confirmed(self) -> bool:
        """Check service-class bit (bit 6)"""
        return bool((self.value >> 1) & 0x01)

    def is_high_priority(self) -> bool:
        """Check priority bit (bit 7)"""
        return bool(self.value & 0x01)


class LongInvokeIdAndPriority(Unsigned32):
    """Long-Invoke-Id-And-Priority"""

    @classmethod
    def from_bits(
        cls,
        long_invoke_id: int,
        self_descriptive: Literal["Not-Self", "Self"] = "Not-Self",
        processing_option: Literal["Continue", "Break"] = "Continue",
        service_class: Literal["confirmed", "unconfirmed"] = "confirmed",
        priority: Literal["high", "normal"] = "normal"
    ) -> Self:
        """Create from individual bit fields"""
        if not (0 <= long_invoke_id <= 0xFFFFFF):
            raise ValueError(f"long_invoke_id must be 0-0xFFFFFF, got {long_invoke_id}")
        value = (
            (long_invoke_id << 8) |
            (1 if self_descriptive == "Self" else 0) << 3 |
            (1 if processing_option == "Break" else 0) << 2 |
            (1 if service_class == "confirmed" else 0) << 1 |
            (1 if priority == "high" else 0)
        )
        return cls(value & 0xFFFFFFFF)

    @property
    def long_invoke_id(self) -> int:
        """Extract long-invoke-id (bits 0-23)"""
        return (self.value >> 8) & 0xFFFFFF

    def is_self_descriptive(self) -> bool:
        """Check self-descriptive bit (bit 28)"""
        return bool((self.value >> 3) & 0x01)

    def is_break_on_error(self) -> bool:
        """Check processing-option bit (bit 29)"""
        return bool((self.value >> 2) & 0x01)

    def is_confirmed(self) -> bool:
        """Check service-class bit (bit 30)"""
        return bool((self.value >> 1) & 0x01)

    def is_high_priority(self) -> bool:
        """Check priority bit (bit 31)"""
        return bool(self.value & 0x01)


# =============================================================================
# Get-Data-Result CHOICE
# =============================================================================


class TaggedData(ImplicitTaggedType, Data):
    """data [0] Data"""
    tag = 0


class GetDataResult(ChoiceType):
    """Get-Data-Result"""
    value: TaggedData | dataAccessResult


# =============================================================================
# Data Block Types
# =============================================================================


@dataclass
class DataBlockResult(SequenceType):
    """Data-Block-Result"""
    last_block: BooleanType
    block_number: Unsigned16
    raw_data: OctetStringType


class RawData(ImplicitTaggedType, OctetStringType):
    """raw-data [0] IMPLICIT OCTET STRING"""
    tag = 0


class DataBlockGResult(ChoiceType):
    """
    DataBlock-G.result CHOICE:
    {
        raw-data                       [0] IMPLICIT OCTET STRING,
        data-access-result             [1] IMPLICIT Data-Access-Result
    }
    """
    value: RawData | dataAccessResult


@dataclass
class DataBlockG(SequenceType):
    """DataBlock-G"""
    last_block: BooleanType
    block_number: Unsigned32
    result: DataBlockGResult


@dataclass
class DataBlockSA(SequenceType):
    """DataBlock-SA"""
    last_block: BooleanType
    block_number: Unsigned32
    raw_data: OctetStringType


# =============================================================================
# Action Response Types
# =============================================================================


@dataclass
class ActionResponseWithOptionalData(SequenceType):
    """Action-Response-With-Optional-Data"""
    result: ActionResult
    return_parameters: Optional[GetDataResult] = None


# =============================================================================
# Notification Types
# =============================================================================


@dataclass
class NotificationBody(SequenceType):
    """Notification-Body"""
    data_value: Data


# =============================================================================
# List Types (SEQUENCE OF)
# =============================================================================


ListOfData: TypeAlias = SequenceOfType[Data]
"""List-Of-Data"""


# =============================================================================
# Access Request Types
# =============================================================================

@dataclass
class AccessRequestGet(ImplicitTaggedType, SequenceType):
    """access-request-get"""
    tag: ClassVar[int] = 1
    cosem_attribute_descriptor: CosemAttributeDescriptor


@dataclass
class AccessRequestSet(ImplicitTaggedType, SequenceType):
    """access-request-set"""
    tag: ClassVar[int] = 2
    cosem_attribute_descriptor: CosemAttributeDescriptor


@dataclass
class AccessRequestAction(ImplicitTaggedType, SequenceType):
    """access-request-action"""
    tag: ClassVar[int] = 3
    cosem_method_descriptor: CosemMethodDescriptor


@dataclass
class AccessRequestGetWithSelection(ImplicitTaggedType, SequenceType):
    """access-request-get-with-selection"""
    tag: ClassVar[int] = 4
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection: SelectiveAccessDescriptor


@dataclass
class AccessRequestSetWithSelection(ImplicitTaggedType, SequenceType):
    """access-request-set-with-selection"""
    tag: ClassVar[int] = 5
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection: SelectiveAccessDescriptor


class AccessRequestSpecification(ChoiceType):
    """Access-Request-Specification"""
    value: AccessRequestGet | AccessRequestSet | AccessRequestAction | AccessRequestGetWithSelection | AccessRequestSetWithSelection


ListOfAccessRequestSpecification = SequenceOfType[AccessRequestSpecification]
"""List-Of-Access-Request-Specification"""


class accessRequestSpecification(ImplicitTaggedType, ListOfAccessRequestSpecification):
    """access-request-specification"""
    tag: ClassVar[int] = 0


@dataclass
class AccessRequestBody(SequenceType):
    """Access-Request-Body"""
    access_request_specification: ListOfAccessRequestSpecification
    access_request_list_of_data: ListOfData


# =============================================================================
# Access Response Types
# =============================================================================


@dataclass
class AccessResponseGet(ImplicitTaggedType, SequenceType):
    """access-response-get"""
    tag: ClassVar[int] = 1
    result: dataAccessResult


@dataclass
class AccessResponseSet(ImplicitTaggedType, SequenceType):
    """access-response-set"""
    tag: ClassVar[int] = 2
    result: dataAccessResult


@dataclass
class AccessResponseAction(ImplicitTaggedType, SequenceType):
    """access-response-action"""
    tag: ClassVar[int] = 3
    result: ActionResult


class AccessResponseSpecification(ChoiceType):
    """Access-Response-Specification"""
    value: AccessResponseGet | AccessResponseSet | AccessResponseAction


ListOfAccessResponseSpecification = SequenceOfType[AccessResponseSpecification]
"""List-Of-Access-Response-Specification"""


class AccessResponseBody(SequenceType):
    """Access-Response-Body"""
    access_request_specification: Optional[accessRequestSpecification] = None  # OPTIONAL — before mandatory
    access_response_list_of_data: ListOfData
    access_response_specification: ListOfAccessResponseSpecification

    def __init__(self, access_response_list_of_data: ListOfData,
                 access_response_specification: ListOfAccessResponseSpecification,
                 access_request_specification: Optional[accessRequestSpecification] = None) -> None:
        self.access_response_list_of_data = access_response_list_of_data
        self.access_response_specification = access_response_specification
        self.access_request_specification = access_request_specification


class Conformance(ber.ConstrainedBitStringType):
    """Conformance ::= [APPLICATION 31] IMPLICIT BIT STRING"""
    tag: ClassVar[x690.Tag] = x690.Tag(
        class_number=31,
        class_=Class.APPLICATION
    )
    constraint_spec: ClassVar[ConstraintSpec] = SizeConstraint(24)
    RESERVED_ZERO: Final[int] = 0
    GENERAL_PROTECTION: Final[int] = 1
    GENERAL_BLOCK_TRANSFER: Final[int] = 2
    READ: Final[int] = 3
    WRITE: Final[int] = 4
    UNCONFIRMED_WRITE: Final[int] = 5
    DELTA_VALUE_ENCODING: Final[int] = 6
    RESERVED_SEVEN: Final[int] = 7
    ATTRIBUTE0_SUPPORTED_WITH_SET: Final[int] = 8
    PRIORITY_MGMT_SUPPORTED: Final[int] = 9
    ATTRIBUTE0_SUPPORTED_WITH_GET: Final[int] = 10
    BLOCK_TRANSFER_WITH_GET_OR_READ: Final[int] = 11
    BLOCK_TRANSFER_WITH_SET_OR_WRITE: Final[int] = 12
    BLOCK_TRANSFER_WITH_ACTION: Final[int] = 13
    MULTIPLE_REFERENCES: Final[int] = 14
    INFORMATION_REPORT: Final[int] = 15
    DATA_NOTIFICATION: Final[int] = 16
    ACCESS: Final[int] = 17
    PARAMETERIZED_ACCESS: Final[int] = 18
    GET: Final[int] = 19
    SET: Final[int] = 20
    SELECTIVE_ACCESS: Final[int] = 21
    EVENT_NOTIFICATION: Final[int] = 22
    ACTION: Final[int] = 23


class InitialRequest(ImplicitTaggedType, SequenceType):
    """initiateRequest [1] IMPLICIT InitiateRequest"""
    tag: ClassVar[int] = 1
    dedicated_key: Optional[OctetStringType] = None
    response_allowed: BooleanType = BooleanType(1)
    proposed_quality_of_service: Optional[Integer8] = None
    proposed_dlms_version_number: Unsigned8
    proposed_conformance: Conformance
    client_max_receive_pdu_size: Unsigned16

    def __init__(
        self,
        *,
        proposed_dlms_version_number: Unsigned8,
        proposed_conformance: Conformance,
        client_max_receive_pdu_size: Unsigned16,
        dedicated_key: Optional[OctetStringType] = None,
        response_allowed: BooleanType = BooleanType(1),
        proposed_quality_of_service: Optional[Integer8] = None,
    ) -> None:
        self.dedicated_key = dedicated_key
        self.response_allowed = response_allowed
        self.proposed_quality_of_service = proposed_quality_of_service
        self.proposed_dlms_version_number = proposed_dlms_version_number
        self.proposed_conformance = proposed_conformance
        self.client_max_receive_pdu_size = client_max_receive_pdu_size


class InitialResponse(ImplicitTaggedType, SequenceType):
    """initiateResponse [8] IMPLICIT InitiateResponse"""
    tag: ClassVar[int] = 8
    negotiated_quality_of_service: Optional[Integer8] = None
    negotiated_dlms_version_number: Unsigned8
    negotiated_conformance: Conformance
    server_max_receive_pdu_size: Unsigned16
    vaa_name: ObjectName

    def __init__(
        self,
        *,
        negotiated_dlms_version_number: Unsigned8,
        negotiated_conformance: Conformance,
        server_max_receive_pdu_size: Unsigned16,
        vaa_name: ObjectName,
        negotiated_quality_of_service: Optional[Integer8] = None,
    ) -> None:
        self.negotiated_quality_of_service = negotiated_quality_of_service
        self.negotiated_dlms_version_number = negotiated_dlms_version_number
        self.negotiated_conformance = negotiated_conformance
        self.server_max_receive_pdu_size = server_max_receive_pdu_size
        self.vaa_name = vaa_name


class ReadRequest(ImplicitTaggedType, SequenceOfType[VariableAccessSpecification]):
    """readRequest [5] IMPLICIT ReadRequest"""
    tag = 5


class dataBlockResult(ImplicitTaggedType, DataBlockResult):
    """data-block-result [2] IMPLICIT Data-Block-Result"""
    tag = 2


class BlockNumber3(ImplicitTaggedType, Unsigned16):
    """block-number [3] IMPLICIT Unsigned16"""
    tag = 3


class ReadResponseChoice(ChoiceType):
    """CHOICE {
        data              [0] Data,
        data-access-error [1] IMPLICIT Data-Access-Result,
        data-block-result [2] IMPLICIT Data-Block-Result,
        block-number      [3] IMPLICIT Unsigned16
    }
    """
    value: TaggedData | dataAccessResult | dataBlockResult | BlockNumber3


class ReadResponse(ImplicitTaggedType, SequenceOfType[ReadResponseChoice]):
    """readResponse"""
    tag = 12


SequenceOfVariableAccessSpecification: TypeAlias = SequenceOfType[VariableAccessSpecification]
"""SEQUENCE OF VariableAccessSpecification"""


@dataclass
class WriteRequest(ImplicitTaggedType, SequenceType):
    """writeRequest"""
    tag: ClassVar[int] = 6
    variable_access_specification: SequenceOfVariableAccessSpecification
    list_of_data: SequenceOfData


class BlockNumber2(ImplicitTaggedType, Unsigned16):
    """[2] Unsigned16"""
    tag = 2


class WriteResponseChoice(ChoiceType):
    """CHOICE {
        success           [0] IMPLICIT NULL,
        data-access-error [1] IMPLICIT Data-Access-Result,
        block-number      [2] Unsigned16
    }
    """
    value: NullType0 | dataAccessResult | BlockNumber2
    SUCCESS: ClassVar["WriteResponseChoice"]


WriteResponseChoice.SUCCESS = WriteResponseChoice(NullType0(None))


class WriteResponse(ImplicitTaggedType, SequenceOfType[WriteResponseChoice]):
    """writeResponse [13] IMPLICIT WriteResponse"""
    tag = 13


class ApplicationReference(ImplicitTaggedType, EnumeratedType):
    """application-reference [0] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 0
    OTHER: Final[int] = 0
    TIME_ELAPSED: Final[int] = 1
    APPLICATION_UNREACHABLE: Final[int] = 2
    APPLICATION_REFERENCE_INVALID: Final[int] = 3
    APPLICATION_CONTEXT_UNSUPPORTED: Final[int] = 4
    PROVIDER_COMMUNICATION_ERROR: Final[int] = 5
    DECIPHERING_ERROR: Final[int] = 6


class HardwareResource(ImplicitTaggedType, EnumeratedType):
    """hardware-resource [1] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 1
    OTHER: Final[int] = 0
    MEMORY_UNAVAILABLE: Final[int] = 1
    PROCESSOR_RESOURCE_UNAVAILABLE: Final[int] = 2
    MASS_STORAGE_UNAVAILABLE: Final[int] = 3
    OTHER_RESOURCE_UNAVAILABLE: Final[int] = 4


class VDEStateError(ImplicitTaggedType, EnumeratedType):
    """vde-state-error [2] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 2
    OTHER: Final[int] = 0
    NO_DLMS_CONTEXT: Final[int] = 1
    LOADING_DATA_SET: Final[int] = 2
    STATUS_NOCHANGE: Final[int] = 3
    STATUS_INOPERABLE: Final[int] = 4


class Service(ImplicitTaggedType, EnumeratedType):
    """service [3] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 3
    OTHER: Final[int] = 0
    PDU_SIZE: Final[int] = 1
    SERVICE_UNSUPPORTED: Final[int] = 2


class Definition(ImplicitTaggedType, EnumeratedType):
    """definition [4] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 4
    OTHER: Final[int] = 0
    OBJECT_UNDEFINED: Final[int] = 1
    OBJECT_CLASS_INCONSISTENT: Final[int] = 2
    OBJECT_ATTRIBUTE_INCONSISTENT: Final[int] = 3


class Access(ImplicitTaggedType, EnumeratedType):
    """access [5] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 5
    OTHER: Final[int] = 0
    SCOPE_OF_ACCESS_VIOLATED: Final[int] = 1
    OBJECT_ACCESS_VIOLATED: Final[int] = 2
    HARDWARE_FAULT: Final[int] = 3
    OBJECT_UNAVAILABLE: Final[int] = 4


class Initiate(ImplicitTaggedType, EnumeratedType):
    """initiate [6] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 6
    OTHER: Final[int] = 0
    DLMS_VERSION_TOO_LOW: Final[int] = 1
    INCOMPATIBLE_CONFORMANCE: Final[int] = 2
    PDU_SIZE_TOO_SHORT: Final[int] = 3
    REFUSED_BY_THE_VDE_HANDLER: Final[int] = 4


class LoadDataSet(ImplicitTaggedType, EnumeratedType):
    """load-data-set [7] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 7
    OTHER: Final[int] = 0
    PRIMITIVE_OUT_OF_SEQUENCE: Final[int] = 1
    NOT_LOADABLE: Final[int] = 2
    DATASET_SIZE_TOO_LARGE: Final[int] = 3
    NOT_AWAITED_SEGMENT: Final[int] = 4
    INTERPRETATION_FAILURE: Final[int] = 5
    STORAGE_FAILURE: Final[int] = 6
    DATA_SET_NOT_READY: Final[int] = 7


class Task(ImplicitTaggedType, EnumeratedType):
    """task [9] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 9
    OTHER: Final[int] = 0
    NO_REMOTE_CONTROL: Final[int] = 1
    TI_STOPPED: Final[int] = 2
    TI_RUNNING: Final[int] = 3
    TI_UNUSABLE: Final[int] = 4


class Changescope(ImplicitTaggedType, EnumeratedType):
    """change-scope [8] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 8


class Other(ImplicitTaggedType, EnumeratedType):
    """other [10] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 10


class ServiceError(ChoiceType):
    """ServiceError"""
    value: Union[
        ApplicationReference, HardwareResource, VDEStateError, Service, Definition,
        Access, Initiate, LoadDataSet, Changescope, Task, Other]


class InitiateError(ImplicitTaggedType, ServiceError):
    """[1] ServiceError"""
    tag: ClassVar[int] = 1


class GetStatus(ImplicitTaggedType, ServiceError):
    """[2] ServiceError"""
    tag: ClassVar[int] = 2


class GetNameList(ImplicitTaggedType, ServiceError):
    """[3] ServiceError"""
    tag: ClassVar[int] = 3


class GetVariableAttribute(ImplicitTaggedType, ServiceError):
    """[4] ServiceError"""
    tag: ClassVar[int] = 4


class Read(ImplicitTaggedType, ServiceError):
    """[5] ServiceError"""
    tag: ClassVar[int] = 5


class Write(ImplicitTaggedType, ServiceError):
    """[6] ServiceError"""
    tag: ClassVar[int] = 6


class GetDataSetAttribute(ImplicitTaggedType, ServiceError):
    """[7] ServiceError"""
    tag: ClassVar[int] = 7


class GetTIAttribute(ImplicitTaggedType, ServiceError):
    """[8] ServiceError"""
    tag: ClassVar[int] = 8


class ChangeScope(ImplicitTaggedType, ServiceError):
    """[9] ServiceError"""
    tag: ClassVar[int] = 9


class Start(ImplicitTaggedType, ServiceError):
    """[10] ServiceError"""
    tag: ClassVar[int] = 10


class Stop(ImplicitTaggedType, ServiceError):
    """[11] ServiceError"""
    tag: ClassVar[int] = 11


class Resume(ImplicitTaggedType, ServiceError):
    """[12] ServiceError"""
    tag: ClassVar[int] = 12


class MakeUsable(ImplicitTaggedType, ServiceError):
    """[13] ServiceError"""
    tag: ClassVar[int] = 13


class InitiateLoad(ImplicitTaggedType, ServiceError):
    """[14] ServiceError"""
    tag: ClassVar[int] = 14


class LoadSegment(ImplicitTaggedType, ServiceError):
    """[15] ServiceError"""
    tag: ClassVar[int] = 15


class TerminateLoad(ImplicitTaggedType, ServiceError):
    """[16] ServiceError"""
    tag: ClassVar[int] = 16


class InitiateUpLoad(ImplicitTaggedType, ServiceError):
    """[17] ServiceError"""
    tag: ClassVar[int] = 17


class UpLoadSegment(ImplicitTaggedType, ServiceError):
    """[18] ServiceError"""
    tag: ClassVar[int] = 18


class TerminateUpLoad(ImplicitTaggedType, ServiceError):
    """[19] ServiceError"""
    tag: ClassVar[int] = 19


class ConfirmedServiceError(ChoiceType):
    """ConfirmedServiceError"""
    value: Union[
        InitiateError, GetStatus, GetNameList, GetVariableAttribute, Read, Write,
        GetDataSetAttribute, GetTIAttribute, ChangeScope, Start, Stop, Resume,
        MakeUsable, InitiateLoad, LoadSegment, TerminateLoad, InitiateUpLoad,
        UpLoadSegment, TerminateUpLoad
    ]


class confirmedServiceError(ImplicitTaggedType, ConfirmedServiceError):
    """confirmedServiceError [14] ConfirmedServiceError"""
    tag = 14


@dataclass
class DataNotification(ImplicitTaggedType, SequenceType):
    """data-notification [15] IMPLICIT Data-Notification"""
    tag: ClassVar[int] = 15
    long_invoke_id_and_priority: LongInvokeIdAndPriority
    date_time: OctetStringType
    data_value: Data


@dataclass
class DataNotificationConfirm(ImplicitTaggedType, SequenceType):
    """data-notification-confirm"""
    tag: ClassVar[int] = 16
    long_invoke_id_and_priority: LongInvokeIdAndPriority
    date_time: OctetStringType


@dataclass
class UnconfirmedWriteRequest(ImplicitTaggedType, SequenceType):
    """unconfirmedWriteRequest [22] IMPLICIT UnconfirmedWriteRequest"""
    tag: ClassVar[int] = 22
    variable_access_specification: SequenceOfVariableAccessSpecification
    list_of_data: SequenceOfData


class informationReportRequest(ImplicitTaggedType, SequenceType):
    """informationReportRequest [24] IMPLICIT InformationReportRequest,"""
    tag: ClassVar[int] = 24
    current_time: Optional[GeneralizedTime] = None  # OPTIONAL — before mandatory
    variable_access_specification: SequenceOfVariableAccessSpecification
    list_of_data: SequenceOfData

    def __init__(self, variable_access_specification: SequenceOfVariableAccessSpecification,
                 list_of_data: SequenceOfData,
                 current_time: Optional[GeneralizedTime] = None) -> None:
        self.variable_access_specification = variable_access_specification
        self.list_of_data = list_of_data
        self.current_time = current_time


class GloInitiateRequest(ImplicitTaggedType, OctetStringType):
    """glo-initiateRequest [33] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 33


class GloReadRequest(ImplicitTaggedType, OctetStringType):
    """glo-readRequest [37] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 37


class GloWriteRequest(ImplicitTaggedType, OctetStringType):
    """glo-writeRequest [38] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 38


class GloInitiateResponse(ImplicitTaggedType, OctetStringType):
    """glo-initiateResponse [40] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 40


class GloReadResponse(ImplicitTaggedType, OctetStringType):
    """glo-readResponse [44] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 44


class GloWriteResponse(ImplicitTaggedType, OctetStringType):
    """glo-writeResponse [45] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 45


class GloConfirmedServiceError(ImplicitTaggedType, OctetStringType):
    """glo-confirmedServiceError [46] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 46


class GloUnconfirmedWriteRequest(ImplicitTaggedType, OctetStringType):
    """glo-unconfirmedWriteRequest [54] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 54


class GloInformationReportRequest(ImplicitTaggedType, OctetStringType):
    """glo-informationReportRequest [56] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 56


class DedInitiateRequest(ImplicitTaggedType, OctetStringType):
    """ded-initiateRequest [65] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 65


class DedReadRequest(ImplicitTaggedType, OctetStringType):
    """ded-readRequest [69] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 69


class DedWriteRequest(ImplicitTaggedType, OctetStringType):
    """ded-writeRequest [70] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 70


class DedInitiateResponse(ImplicitTaggedType, OctetStringType):
    """ded-initiateResponse [72] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 72


class DedReadResponse(ImplicitTaggedType, OctetStringType):
    """ded-readResponse [76] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 76


class DedWriteResponse(ImplicitTaggedType, OctetStringType):
    """ded-writeResponse [77] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 77


class DedConfirmedServiceError(ImplicitTaggedType, OctetStringType):
    """ded-confirmedServiceError [78] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 78


class DedUnconfirmedWriteRequest(ImplicitTaggedType, OctetStringType):
    """ded-unconfirmedWriteRequest [86] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 86


class DedInformationReportRequest(ImplicitTaggedType, OctetStringType):
    """ded-informationReportRequest [88] IMPLICIT OCTET STRING"""
    tag: ClassVar[int] = 88


@dataclass
class GetRequestNormal(ImplicitTaggedType, SequenceType):
    """get-request-normal [1] IMPLICIT Get-Request-Normal"""
    tag: ClassVar[int] = 1
    invoke_id_and_priority: InvokeIdAndPriority
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection: Optional[SelectiveAccessDescriptor] = None


@dataclass
class GetRequestNext(ImplicitTaggedType, SequenceType):
    """get-request-next [2] IMPLICIT Get-Request-Next"""
    tag: ClassVar[int] = 2
    invoke_id_and_priority: InvokeIdAndPriority
    block_number: Unsigned32


SequenceOfCosemAttributeDescriptorWithSelection: TypeAlias = SequenceOfType[CosemAttributeDescriptorWithSelection]
"""SEQUENCE OF CosemAttributeDescriptorWithSelection"""


@dataclass
class GetRequestWithList(ImplicitTaggedType, SequenceType):
    """get-request-with-list [3] IMPLICIT Get-Request-With-List"""
    tag: ClassVar[int] = 3
    invoke_id_and_priority: InvokeIdAndPriority
    attribute_descriptor_list: SequenceOfCosemAttributeDescriptorWithSelection


class GetRequest(ImplicitTaggedType, ChoiceType):
    """get-request"""
    tag: ClassVar[int] = 192
    value: GetRequestNormal | GetRequestNext | GetRequestWithList


@dataclass
class GetResponseNormal(ImplicitTaggedType, SequenceType):
    """get-response-normal [1] IMPLICIT Get-Response-Normal"""
    tag: ClassVar[int] = 1
    invoke_id_and_priority: InvokeIdAndPriority
    result: GetDataResult


@dataclass
class GetResponseWithDatablock(ImplicitTaggedType, SequenceType):
    """get-response-with-datablock [2] IMPLICIT Get-Response-With-Datablock"""
    tag: ClassVar[int] = 2
    invoke_id_and_priority: InvokeIdAndPriority
    result: DataBlockG


SequenceOfGetDataResult: TypeAlias = SequenceOfType[GetDataResult]
"""SEQUENCE OF GetDataResult"""


@dataclass
class GetResponseWithList(ImplicitTaggedType, SequenceType):
    """get-response-with-list [3] IMPLICIT Get-Response-With-List"""
    tag: ClassVar[int] = 3
    invoke_id_and_priority: InvokeIdAndPriority
    result: SequenceOfGetDataResult


class GetResponse(ImplicitTaggedType, ChoiceType):
    """get-response"""
    tag: ClassVar[int] = 196
    value: GetResponseNormal | GetResponseWithDatablock | GetResponseWithList


class SetRequestNormal(ImplicitTaggedType, SequenceType):
    """[1] IMPLICIT Set-Request-Normal"""
    tag: ClassVar[int] = 1
    invoke_id_and_priority: InvokeIdAndPriority
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection: Optional[SelectiveAccessDescriptor] = None  # OPTIONAL — между mandatory
    value: Data

    def __init__(self, invoke_id_and_priority: InvokeIdAndPriority,
                 cosem_attribute_descriptor: CosemAttributeDescriptor,
                 value: Data,
                 access_selection: Optional[SelectiveAccessDescriptor] = None) -> None:
        self.invoke_id_and_priority = invoke_id_and_priority
        self.cosem_attribute_descriptor = cosem_attribute_descriptor
        self.value = value
        self.access_selection = access_selection


class SetRequestWithFirstDatablock(ImplicitTaggedType, SequenceType):
    """[2] IMPLICIT Set-Request-With-First-Datablock"""
    tag: ClassVar[int] = 2
    invoke_id_and_priority: InvokeIdAndPriority
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection: Optional[SelectiveAccessDescriptor] = None  # OPTIONAL — между mandatory
    datablock: DataBlockSA

    def __init__(self, invoke_id_and_priority: InvokeIdAndPriority,
                 cosem_attribute_descriptor: CosemAttributeDescriptor,
                 datablock: DataBlockSA,
                 access_selection: Optional[SelectiveAccessDescriptor] = None) -> None:
        self.invoke_id_and_priority = invoke_id_and_priority
        self.cosem_attribute_descriptor = cosem_attribute_descriptor
        self.datablock = datablock
        self.access_selection = access_selection


class SetRequestWithDatablock(ImplicitTaggedType, SequenceType):
    """[3] IMPLICIT Set-Request-With-Datablock"""
    tag: ClassVar[int] = 3
    invoke_id_and_priority: InvokeIdAndPriority
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection: Optional[SelectiveAccessDescriptor] = None  # OPTIONAL — между mandatory
    datablock: DataBlockSA

    def __init__(self, invoke_id_and_priority: InvokeIdAndPriority,
                 cosem_attribute_descriptor: CosemAttributeDescriptor,
                 datablock: DataBlockSA,
                 access_selection: Optional[SelectiveAccessDescriptor] = None) -> None:
        self.invoke_id_and_priority = invoke_id_and_priority
        self.cosem_attribute_descriptor = cosem_attribute_descriptor
        self.datablock = datablock
        self.access_selection = access_selection


@dataclass
class SetRequestWithList(ImplicitTaggedType, SequenceType):
    """[4] IMPLICIT Set-Request-With-List"""
    tag: ClassVar[int] = 4
    invoke_id_and_priority: InvokeIdAndPriority
    attribute_descriptor_list: SequenceOfCosemAttributeDescriptorWithSelection
    value_list: SequenceOfData


@dataclass
class SetRequestWithListAndFirstDatablock(ImplicitTaggedType, SequenceType):
    """[5] IMPLICIT Set-Request-With-List-And-First-Datablock"""
    tag: ClassVar[int] = 5
    invoke_id_and_priority: InvokeIdAndPriority
    attribute_descriptor_list: SequenceOfCosemAttributeDescriptorWithSelection
    datablock: DataBlockSA


class SetRequest(ImplicitTaggedType, ChoiceType):
    """set-request"""
    tag: ClassVar[int] = 193
    value: SetRequestNormal | SetRequestWithFirstDatablock | SetRequestWithDatablock | SetRequestWithList | SetRequestWithListAndFirstDatablock


@dataclass
class SetResponseNormal(ImplicitTaggedType, SequenceType):
    """set-response-normal [1] IMPLICIT Set-Response-Normal"""
    tag: ClassVar[int] = 1
    invoke_id_and_priority: InvokeIdAndPriority
    result: GetDataResult


@dataclass
class SetResponseDatablock(ImplicitTaggedType, SequenceType):
    """set-response-datablock [2] IMPLICIT Set-Response-Datablock"""
    tag: ClassVar[int] = 2
    invoke_id_and_priority: InvokeIdAndPriority
    block_number: Unsigned32


@dataclass
class SetResponseLastDatablock(ImplicitTaggedType, SequenceType):
    """set-response-last-datablock [3] IMPLICIT Set-Response-Last-Datablock"""
    tag: ClassVar[int] = 3
    invoke_id_and_priority: InvokeIdAndPriority
    result: DataAccessResult
    block_number: Unsigned32


SequenceOfDataAccessResult: TypeAlias = SequenceOfType[DataAccessResult]
"""SEQUENCE OF DataAccessResult"""


@dataclass
class SetResponseLastDatablockWithList(ImplicitTaggedType, SequenceType):
    """set-response-last-datablock-with-list [4] IMPLICIT Set-Response-Last-Datablock-With-List"""
    tag: ClassVar[int] = 4
    invoke_id_and_priority: InvokeIdAndPriority
    result: SequenceOfDataAccessResult
    block_number: Unsigned32


@dataclass
class SetResponseWithList(ImplicitTaggedType, SequenceType):
    """set-response-with-list [5] IMPLICIT Set-Response-With-List"""
    tag: ClassVar[int] = 5
    invoke_id_and_priority: InvokeIdAndPriority
    result: SequenceOfDataAccessResult


class SetResponse(ImplicitTaggedType, ChoiceType):
    """set-response [197] IMPLICIT Set-Response"""
    tag: ClassVar[int] = 197
    value: SetResponseNormal | SetResponseDatablock | SetResponseLastDatablock | SetResponseLastDatablockWithList | SetResponseWithList


@dataclass
class ActionRequestNormal(ImplicitTaggedType, SequenceType):
    """action-request-normal [1] IMPLICIT Action-Request-Normal"""
    tag: ClassVar[int] = 1
    invoke_id_and_priority: InvokeIdAndPriority
    cosem_method_descriptor: CosemMethodDescriptor
    method_invocation_parameters: Optional[Data] = None


@dataclass
class ActionRequestNextPblock(ImplicitTaggedType, SequenceType):
    """action-request-next-pblock [2] IMPLICIT Action-Request-Next-Pblock"""
    tag: ClassVar[int] = 2
    invoke_id_and_priority: InvokeIdAndPriority
    block_number: Unsigned32


SequenceOfCosemMethodDescriptor: TypeAlias = SequenceOfType[CosemMethodDescriptor]
"""SEQUENCE OF CosemMethodDescriptor"""


@dataclass
class ActionRequestWithList(ImplicitTaggedType, SequenceType):
    """action-request-with-list [3] IMPLICIT Action-Request-With-List"""
    tag: ClassVar[int] = 3
    invoke_id_and_priority: InvokeIdAndPriority
    cosem_method_descriptor_list: SequenceOfCosemMethodDescriptor
    method_invocation_parameters: SequenceOfData


@dataclass
class ActionRequestWithFirstPblock(ImplicitTaggedType, SequenceType):
    """action-request-with-first-pblock [4] IMPLICIT Action-Request-With-First-Pblock"""
    tag: ClassVar[int] = 4
    invoke_id_and_priority: InvokeIdAndPriority
    cosem_method_descriptor: CosemMethodDescriptor
    pblock: DataBlockSA


@dataclass
class ActionRequestWithListAndFirstPblock(ImplicitTaggedType, SequenceType):
    """action-request-with-list-and-first-pblock [5] IMPLICIT Action-Request-With-List-And-First-Pblock"""
    tag: ClassVar[int] = 5
    invoke_id_and_priority: InvokeIdAndPriority
    cosem_method_descriptor_list: SequenceOfCosemMethodDescriptor
    pblock: DataBlockSA


@dataclass
class ActionRequestWithPblock(ImplicitTaggedType, SequenceType):
    """action-request-with-pblock [6] IMPLICIT Action-Request-With-Pblock"""
    tag: ClassVar[int] = 6
    invoke_id_and_priority: InvokeIdAndPriority
    pblock: DataBlockSA


class ActionRequest(ImplicitTaggedType, ChoiceType):
    """action-request"""
    tag: ClassVar[int] = 195
    value: ActionRequestNormal | ActionRequestNextPblock | ActionRequestWithList | ActionRequestWithFirstPblock | ActionRequestWithListAndFirstPblock | ActionRequestWithPblock


@dataclass
class ActionResponseNormal(ImplicitTaggedType, SequenceType):
    """action-response-normal"""
    tag: ClassVar[int] = 1
    invoke_id_and_priority: InvokeIdAndPriority
    single_response: ActionResponseWithOptionalData


@dataclass
class ActionResponseWithPblock(ImplicitTaggedType, SequenceType):
    """action-response-with-pblock"""
    tag: ClassVar[int] = 2
    invoke_id_and_priority: InvokeIdAndPriority
    pblock: DataBlockSA


SequenceOfActionResponseWithOptionalData: TypeAlias = SequenceOfType[ActionResponseWithOptionalData]
"""SEQUENCE OF ActionResponseWithOptionalData"""


@dataclass
class ActionResponseWithList(ImplicitTaggedType, SequenceType):
    """action-response-with-list"""
    tag: ClassVar[int] = 3
    invoke_id_and_priority: InvokeIdAndPriority
    list_of_responses: SequenceOfActionResponseWithOptionalData


@dataclass
class ActionResponseNextPblock(ImplicitTaggedType, SequenceType):
    """action-response-next-pblock"""
    tag: ClassVar[int] = 4
    invoke_id_and_priority: InvokeIdAndPriority
    block_number: Unsigned32


class ActionResponse(ImplicitTaggedType, ChoiceType):
    """action-Response"""
    tag: ClassVar[int] = 199
    value: ActionResponseNormal | ActionResponseWithPblock | ActionResponseWithList | ActionResponseNextPblock


class EventNotificationRequest(ImplicitTaggedType, SequenceType):
    """[194] IMPLICIT EventNotificationRequest"""
    tag: ClassVar[int] = 194
    time: Optional[OctetStringType] = None  # OPTIONAL — before mandatory
    cosem_attribute_descriptor: CosemAttributeDescriptor
    attribute_value: Data

    def __init__(self, cosem_attribute_descriptor: CosemAttributeDescriptor,
                 attribute_value: Data,
                 time: Optional[OctetStringType] = None) -> None:
        self.cosem_attribute_descriptor = cosem_attribute_descriptor
        self.attribute_value = attribute_value
        self.time = time


class GloGetRequest(ImplicitTaggedType, OctetStringType):
    """[200] IMPLICIT glo-get-request"""
    tag: ClassVar[int] = 200


class GloSetRequest(ImplicitTaggedType, OctetStringType):
    """[201] IMPLICIT glo-set-request"""
    tag: ClassVar[int] = 201


class GloEventNotificationRequest(ImplicitTaggedType, OctetStringType):
    """[202] IMPLICIT glo-event-notification-request"""
    tag: ClassVar[int] = 202


class GloActionRequest(ImplicitTaggedType, OctetStringType):
    """[203] IMPLICIT glo-action-request"""
    tag: ClassVar[int] = 203


class GloGetResponse(ImplicitTaggedType, OctetStringType):
    """[204] IMPLICIT glo-get-response"""
    tag: ClassVar[int] = 204


class GloSetResponse(ImplicitTaggedType, OctetStringType):
    """[205] IMPLICIT glo-set-response"""
    tag: ClassVar[int] = 205


class GloActionResponse(ImplicitTaggedType, OctetStringType):
    """[207] IMPLICIT glo-action-response"""
    tag: ClassVar[int] = 207


class DedGetRequest(ImplicitTaggedType, OctetStringType):
    """[208] IMPLICIT ded-get-request"""
    tag: ClassVar[int] = 208


class DedSetRequest(ImplicitTaggedType, OctetStringType):
    """[209] IMPLICIT ded-set-request"""
    tag: ClassVar[int] = 209


class DedEventNotificationRequest(ImplicitTaggedType, OctetStringType):
    """[210] IMPLICIT ded-event-notification-request"""
    tag: ClassVar[int] = 210


class DedActionRequest(ImplicitTaggedType, OctetStringType):
    """[211] IMPLICIT ded-action-request"""
    tag: ClassVar[int] = 211


class DedGetResponse(ImplicitTaggedType, OctetStringType):
    """[212] IMPLICIT ded-get-response"""
    tag: ClassVar[int] = 212


class DedSetResponse(ImplicitTaggedType, OctetStringType):
    """[213] IMPLICIT ded-set-response"""
    tag: ClassVar[int] = 213


class DedActionResponse(ImplicitTaggedType, OctetStringType):
    """[215] IMPLICIT ded-action-response"""
    tag: ClassVar[int] = 215


class StateError(ImplicitTaggedType, EnumeratedType):
    """state-error [0] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 0
    SERVICE_NOT_ALLOWED: Final[int] = 1
    SERVICE_UNKNOWN: Final[int] = 2


class OperationNotPossible(ImplicitTaggedType, NullType):
    """operation-not-possible"""
    tag: ClassVar[int] = 1


class ServiceNotSupported(ImplicitTaggedType, NullType):
    """service-not-supported"""
    tag: ClassVar[int] = 2


class OtherReason(ImplicitTaggedType, NullType):
    """other-reason"""
    tag: ClassVar[int] = 3


class PduTooLong(ImplicitTaggedType, NullType):
    """pdu-too-long"""
    tag: ClassVar[int] = 4


class DecipheringError(ImplicitTaggedType, NullType):
    """deciphering-error"""
    tag: ClassVar[int] = 5


class InvocationCounterError(ImplicitTaggedType, Unsigned32):
    """invocation-counter-error"""
    tag: ClassVar[int] = 6


class serviceError(ImplicitTaggedType, ChoiceType):
    """service-error"""
    tag: ClassVar[int] = 1
    value: OperationNotPossible | ServiceNotSupported | OtherReason | PduTooLong | DecipheringError | InvocationCounterError


@dataclass
class ExceptionResponse(ImplicitTaggedType, SequenceType):
    """exception-response"""
    tag: ClassVar[int] = 216
    state_error: StateError
    service_error: serviceError


@dataclass
class AccessRequest(ImplicitTaggedType, SequenceType):
    """access-request"""
    tag: ClassVar[int] = 217
    long_invoke_id_and_priority: LongInvokeIdAndPriority
    date_time: OctetStringType
    access_request_body: AccessRequestBody


@dataclass
class AccessResponse(ImplicitTaggedType, SequenceType):
    """access-response"""
    tag: ClassVar[int] = 218
    long_invoke_id_and_priority: LongInvokeIdAndPriority
    date_time: OctetStringType
    access_response_body: AccessResponseBody


class BlockControl(Unsigned8):
    """Block-Control"""

    def window_bits(self) -> int:
        """Extract window bits (0-5)"""
        return self.value & 0x3F

    def is_streaming(self) -> bool:
        """Check if streaming bit (6) is set"""
        return bool(self.value & 0x40)

    def is_last_block(self) -> bool:
        """Check if last-block bit (7) is set"""
        return bool(self.value & 0x80)


@dataclass
class GeneralDedCiphering(ImplicitTaggedType, SequenceType):
    """[220] IMPLICIT generalDedCiphering"""
    tag: ClassVar[int] = 220
    system_title: OctetStringType
    ciphered_content: OctetStringType


@dataclass
class GeneralGloCiphering(ImplicitTaggedType, SequenceType):
    """[219] IMPLICIT generalGloCiphering"""
    tag: ClassVar[int] = 219
    system_title: OctetStringType
    ciphered_content: OctetStringType


class KeyId(EnumeratedType):
    """Key-Id"""
    GLOBAL_UNICAST_ENCRYPTION_KEY: Final[int] = 0
    GLOBAL_BROADCAST_ENCRYPTION_KEY: Final[int] = 1


class KekId(EnumeratedType):
    """Kek-Id"""
    MASTER_KEY: Final[int] = 0


@dataclass
class IdentifiedKey(ImplicitTaggedType, SequenceType):
    """identified-key"""
    tag: ClassVar[int] = 0
    key_id: KeyId


@dataclass
class WrappedKey(ImplicitTaggedType, SequenceType):
    """wrapped-key"""
    tag: ClassVar[int] = 1
    kek_id: KekId
    key_ciphered_data: OctetStringType


@dataclass
class AgreedKey(ImplicitTaggedType, SequenceType):
    """agreed-key"""
    tag: ClassVar[int] = 2
    key_parameters: OctetStringType
    key_ciphered_data: OctetStringType


class KeyInfo(ChoiceType):
    """Key-Info"""
    value: IdentifiedKey | WrappedKey | AgreedKey


@dataclass
class GeneralCiphering(ImplicitTaggedType, SequenceType):
    """[221] IMPLICIT generalCiphering"""
    tag: ClassVar[int] = 221
    transaction_id: OctetStringType
    originator_system_title: OctetStringType
    recipient_system_title: OctetStringType
    date_time: OctetStringType
    other_information: OctetStringType
    key_info: KeyInfo
    ciphered_content: OctetStringType


@dataclass
class GeneralSigning(ImplicitTaggedType, SequenceType):
    """[223] IMPLICIT generalSigning"""
    tag: ClassVar[int] = 223
    transaction_id: OctetStringType
    originator_system_title: OctetStringType
    recipient_system_title: OctetStringType
    date_time: OctetStringType
    other_information: OctetStringType
    content: OctetStringType
    signature: OctetStringType


@dataclass
class GeneralBlockTransfer(ImplicitTaggedType, SequenceType):
    """[224] IMPLICIT generalBlockTransfer"""
    tag: ClassVar[int] = 224
    block_control: BlockControl
    block_number: Unsigned16
    block_number_ack: Unsigned16
    block_data: OctetStringType


class XDLMS_APDU(ChoiceType):
    """XDLMS-APDU"""
    value: Union[
        InitialRequest, ReadRequest, WriteRequest, InitialResponse,
        ReadResponse, WriteResponse, confirmedServiceError,
        DataNotification, DataNotificationConfirm, UnconfirmedWriteRequest,
        informationReportRequest, GloInitiateRequest, GloReadRequest,
        GloWriteRequest, GloInitiateResponse, GloReadResponse, GloWriteResponse,
        GloConfirmedServiceError, GloUnconfirmedWriteRequest, GloInformationReportRequest,
        DedInitiateRequest, DedReadRequest, DedWriteRequest,
        DedInitiateResponse, DedReadResponse, DedWriteResponse,
        DedConfirmedServiceError, DedUnconfirmedWriteRequest, DedInformationReportRequest,
        GetRequest, SetRequest, EventNotificationRequest, ActionRequest,
        GetResponse, SetResponse, ActionResponse,
        GloGetRequest, GloSetRequest, GloEventNotificationRequest, GloActionRequest,
        GloGetResponse, GloSetResponse, GloActionResponse,
        DedGetRequest, DedSetRequest, DedEventNotificationRequest, DedActionRequest,
        DedGetResponse, DedSetResponse, DedActionResponse,
        ExceptionResponse, AccessRequest, AccessResponse,
        GeneralGloCiphering, GeneralDedCiphering, GeneralCiphering,
        GeneralSigning, GeneralBlockTransfer,
    ]
