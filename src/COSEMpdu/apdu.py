"""
COSEM PDU Types Implementation
Based on COSEMpdu_GB83.txt (Green Book 8.3)
Implements A-XDR encoding/decoding according to IEC 61334-6
"""
from typing import ClassVar, Final, Optional, TypeAlias, Union
from dataclasses import dataclass
from .data import Data, SequenceOfData, ObjectName, Unsigned16, Unsigned8, Unsigned32, Integer8
from .axdr import (
    EnumeratedType, OctetStringType, SequenceType, SequenceOfType,
    ChoiceType, NullType, GeneralizedTime, NullType0, ImplicitTaggedType, BooleanType
)
from .types_used import (
    TaggedData,
    CosemAttributeDescriptor,
    CosemAttributeDescriptorWithSelection,
    CosemMethodDescriptor,
    InvokeIdAndPriority,
    SelectiveAccessDescriptor,
    VariableAccessSpecification,
    dataAccessResult,
    DataBlockResult,
    LongInvokeIdAndPriority,
    GetDataResult,
    DataBlockG,
    DataBlockSA,
    DataAccessResult,
    ActionResponseWithOptionalData,
    AccessRequestBody,
    AccessResponseBody
)
from .service_error import ConfirmedServiceError
from . import ber
from . import x690
from .x680 import tag, ConstraintSpec
from .x680.bit_string import NamedBitList, NamedBit
from .x680.constrained_type import SizeConstraint


class Conformance(ber.ImplicitTaggedType, ber.ConstrainedBitStringType):
    """Conformance ::= [APPLICATION 31] IMPLICIT BIT STRING"""
    tag = x690.Tag(
        class_number=31,
        class_=tag.Class.APPLICATION
    )
    constraint_spec: ClassVar[ConstraintSpec] = SizeConstraint(24)
    named_bits: ClassVar[Optional[NamedBitList]] = NamedBitList((
        NamedBit("reserved-zero", 0),
        NamedBit("general-protection", 1),
        NamedBit("general-block-transfer", 2),
        NamedBit("read", 3),
        NamedBit("write", 4),
        NamedBit("unconfirmed-write", 5),
        NamedBit("delta-value-encoding", 6),
        NamedBit("reserved-seven", 7),
        NamedBit("attribute0-supported-with-set", 8),
        NamedBit("priority-mgmt-supported", 9),
        NamedBit("attribute0-supported-with-get", 10),
        NamedBit("block-transfer-with-get-or-read", 11),
        NamedBit("block-transfer-with-set-or-write", 12),
        NamedBit("block-transfer-with-action", 13),
        NamedBit("multiple-references", 14),
        NamedBit("information-report", 15),
        NamedBit("data-notification", 16),
        NamedBit("access", 17),
        NamedBit("parameterized-access", 18),
        NamedBit("get", 19),
        NamedBit("set", 20),
        NamedBit("selective-access", 21),
        NamedBit("event-notification", 22),
        NamedBit("action", 23),
    ))


class InitialRequest(ImplicitTaggedType, SequenceType):
    """initiateRequest [1] IMPLICIT InitiateRequest"""
    tag: ClassVar[int] = 1
    dedicated_key: Optional[OctetStringType] = None
    response_allowed: BooleanType = BooleanType(True)
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
        response_allowed: BooleanType = BooleanType(True),
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
        return self.value.value & 0x3F

    def is_streaming(self) -> bool:
        """Check if streaming bit (6) is set"""
        return bool(self.value.value & 0x40)

    def is_last_block(self) -> bool:
        """Check if last-block bit (7) is set"""
        return bool(self.value.value & 0x80)


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
