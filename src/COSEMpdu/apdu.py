"""
COSEM PDU Types Implementation
Based on COSEMpdu_GB83.txt (Green Book 8.3)
Implements A-XDR encoding/decoding according to IEC 61334-6
"""
from typing import ClassVar, Optional, TypeAlias
from dataclasses import dataclass
from .data import Data, SequenceOfData
from .x680.tagged_type import TaggingMode
from .x680.enumerated_type import EnumerationList, EnumerationMember
from .axdr import (
    EnumeratedType, OctetStringType, SequenceType, SequenceOfType, create_alternatives,
    ChoiceType, TaggedType, NullType, GeneralizedTime, NullType0
)
from .x680.type import NamedType
from .useful_types import Unsigned16, Unsigned8, Unsigned32
from .types_used import (
    CosemAttributeDescriptor,
    CosemAttributeDescriptorWithSelection,
    CosemMethodDescriptor,
    InvokeIdAndPriority,
    SelectiveAccessDescriptor,
    VariableAccessSpecification,
    Data0,
    DataAccessResult1,
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
from .user_information import InitiateRequest, InitiateResponse
from .key_info import KeyInfo


class initialRequest(TaggedType[InitiateRequest]):
    """initialRequest"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: InitiateRequest


class initialResponse(TaggedType[InitiateResponse]):
    """initialResponse"""
    tag = 8
    mode = TaggingMode.IMPLICIT
    value: InitiateResponse


# ============================================================================
# -- Read/Write Request/Response (COSEMpdu_GB83.txt)
# ============================================================================


ReadRequest: TypeAlias = SequenceOfType[VariableAccessSpecification]
"""ReadRequest"""


class readRequest(TaggedType[ReadRequest]):
    """readRequest"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: ReadRequest


class dataBlockResult(TaggedType[DataBlockResult]):
    """[2] IMPLICIT Data-Block-Result"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: DataBlockResult


class BlockNumber3(TaggedType[Unsigned16]):
    """[3] IMPLICIT Unsigned16"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: Unsigned16


class ReadResponseChoice(ChoiceType):
    """CHOICE {
        data              [0] Data,
        data-access-error [1] IMPLICIT Data-Access-Result,
        data-block-result [2] IMPLICIT Data-Block-Result,
        block-number      [3] IMPLICIT Unsigned16
    }
    """
    alternatives = create_alternatives(
        NamedType("data", Data0),
        NamedType("data-access-error", DataAccessResult1),
        NamedType("data-block-result", dataBlockResult),
        NamedType("block-number", BlockNumber3),
    )
    value: dataBlockResult | DataAccessResult1 | dataBlockResult | BlockNumber3


ReadResponse: TypeAlias = SequenceOfType[ReadResponseChoice]
"""ReadResponse"""


class readResponse(TaggedType[ReadResponse]):
    """readResponse"""
    tag = 12
    mode = TaggingMode.IMPLICIT
    value: ReadResponse


SequenceOfVariableAccessSpecification: TypeAlias = SequenceOfType[VariableAccessSpecification]
"""SEQUENCE OF VariableAccessSpecification"""

@dataclass
class WriteRequest(SequenceType):
    """WriteRequest"""
    variable_access_specification: SequenceOfVariableAccessSpecification
    list_of_data: SequenceOfData


class writeRequest(TaggedType[WriteRequest]):
    """writeRequest"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    value: WriteRequest


class BlockNumber2(TaggedType[Unsigned16]):
    """[2] Unsigned16"""
    tag = 2
    mode = TaggingMode.DEFAULT
    value: Unsigned16


class WriteResponseChoice(ChoiceType):
    """CHOICE {
        success           [0] IMPLICIT NULL,
        data-access-error [1] IMPLICIT Data-Access-Result,
        block-number      [2] Unsigned16
    }
    """
    alternatives = {
        0: NamedType("success", NullType0),
        1: NamedType("data-access-error", DataAccessResult1),
        2: NamedType("block-number", BlockNumber2),
    }
    value: NullType0 | DataAccessResult1 | BlockNumber2
    SUCCESS: ClassVar["WriteResponseChoice"]


WriteResponseChoice.SUCCESS = WriteResponseChoice(NullType0(NullType(None)))


WriteResponse: TypeAlias = SequenceOfType[WriteResponseChoice]
"""WriteResponse"""


class writeResponse(TaggedType[WriteResponse]):
    """writeResponse"""
    tag = 13
    mode = TaggingMode.IMPLICIT
    value: WriteResponse


class confirmedServiceError(TaggedType[ConfirmedServiceError]):
    """confirmedServiceError"""
    tag = 14
    mode = TaggingMode.IMPLICIT
    value: ConfirmedServiceError


@dataclass
class NotificationBody(SequenceType):
    """NotificationBody"""
    data_value: Data


@dataclass
class DataNotification(SequenceType):
    """DataNotification"""
    long_invoke_id_and_priority: LongInvokeIdAndPriority
    date_time: OctetStringType
    notification_body: NotificationBody


class dataNotification(TaggedType[DataNotification]):
    """data-notification"""
    tag = 15
    mode = TaggingMode.IMPLICIT
    value: DataNotification


@dataclass
class DataNotificationConfirm(SequenceType):
    """DataNotificationConfirm"""
    long_invoke_id_and_priority: LongInvokeIdAndPriority
    date_time: OctetStringType


class dataNotificationConfirm(TaggedType[DataNotificationConfirm]):
    """data-notification-confirm"""
    tag = 16
    mode = TaggingMode.IMPLICIT
    value: DataNotificationConfirm


@dataclass
class UnconfirmedWriteRequest(SequenceType):
    """UnconfirmedWriteRequest"""
    variable_access_specification: SequenceOfVariableAccessSpecification
    list_of_data: SequenceOfData


class unconfirmedWriteRequest(TaggedType[UnconfirmedWriteRequest]):
    """unconfirmedWriteRequest"""
    tag = 22
    mode = TaggingMode.IMPLICIT
    value: UnconfirmedWriteRequest


class InformationReportRequest(SequenceType):
    """InformationReportRequest"""
    current_time: Optional[GeneralizedTime] = None  # OPTIONAL — before mandatory
    variable_access_specification: SequenceOfVariableAccessSpecification
    list_of_data: SequenceOfData

    def __init__(self, variable_access_specification: SequenceOfVariableAccessSpecification,
                 list_of_data: SequenceOfData,
                 current_time: Optional[GeneralizedTime] = None) -> None:
        self.variable_access_specification = variable_access_specification
        self.list_of_data = list_of_data
        self.current_time = current_time


class informationReportRequest(TaggedType[InformationReportRequest]):
    """informationReportRequest"""
    tag = 24
    mode = TaggingMode.IMPLICIT
    value: InformationReportRequest


class GloInitiateRequest(TaggedType[OctetStringType]):
    """glo-initiateRequest"""
    tag = 33
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class GloReadRequest(TaggedType[OctetStringType]):
    """glo-readRequest"""
    tag = 37
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class GloWriteRequest(TaggedType[OctetStringType]):
    """glo-writeRequest"""
    tag = 38
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class GloInitiateResponse(TaggedType[OctetStringType]):
    """glo-initiateResponse"""
    tag = 40
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class GloReadResponse(TaggedType[OctetStringType]):
    """glo-readResponse"""
    tag = 44
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class GloWriteResponse(TaggedType[OctetStringType]):
    """glo-writeResponse"""
    tag = 45
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class GloConfirmedServiceError(TaggedType[OctetStringType]):
    """glo-confirmedServiceError"""
    tag = 46
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class GloUnconfirmedWriteRequest(TaggedType[OctetStringType]):
    """glo-unconfirmedWriteRequest"""
    tag = 54
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class GloInformationReportRequest(TaggedType[OctetStringType]):
    """glo-informationReportRequest"""
    tag = 56
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class DedInitiateRequest(TaggedType[OctetStringType]):
    """ded-initiateRequest"""
    tag = 65
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class DedReadRequest(TaggedType[OctetStringType]):
    """ded-readRequest"""
    tag = 69
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class DedWriteRequest(TaggedType[OctetStringType]):
    """ded-writeRequest"""
    tag = 70
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class DedInitiateResponse(TaggedType[OctetStringType]):
    """ded-initiateResponse"""
    tag = 72
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class DedReadResponse(TaggedType[OctetStringType]):
    """ded-readResponse"""
    tag = 76
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class DedWriteResponse(TaggedType[OctetStringType]):
    """ded-writeResponse"""
    tag = 77
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class DedConfirmedServiceError(TaggedType[OctetStringType]):
    """ded-confirmedServiceError"""
    tag = 78
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class DedUnconfirmedWriteRequest(TaggedType[OctetStringType]):
    """ded-unconfirmedWriteRequest"""
    tag = 86
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class DedInformationReportRequest(TaggedType[OctetStringType]):
    """ded-informationReportRequest"""
    tag = 88
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class GetRequestNormal(SequenceType):
    """Get-Request-Normal"""
    invoke_id_and_priority: InvokeIdAndPriority
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection: Optional[SelectiveAccessDescriptor] = None


class GetRequestNormal1(TaggedType[GetRequestNormal]):
    """[1] IMPLICIT Get-Request-Normal"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: GetRequestNormal


@dataclass
class GetRequestNext(SequenceType):
    """Get-Request-Next"""
    invoke_id_and_priority: InvokeIdAndPriority
    block_number: Unsigned32


class GetRequestNext2(TaggedType[GetRequestNext]):
    """[2] IMPLICIT Get-Request-Next"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: GetRequestNext


SequenceOfCosemAttributeDescriptorWithSelection: TypeAlias = SequenceOfType[CosemAttributeDescriptorWithSelection]
"""SEQUENCE OF CosemAttributeDescriptorWithSelection"""


@dataclass
class GetRequestWithList(SequenceType):
    """Get-Request-With-List"""
    invoke_id_and_priority: InvokeIdAndPriority
    attribute_descriptor_list: SequenceOfCosemAttributeDescriptorWithSelection


class GetRequestWithList3(TaggedType[GetRequestWithList]):
    """[3] IMPLICIT Get-Request-With-List"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: GetRequestWithList


class GetRequest(ChoiceType):
    """Get-Request"""
    alternatives = {
        1: NamedType("get-request-normal", GetRequestNormal1),
        2: NamedType("get-request-next", GetRequestNext2),
        3: NamedType("get-request-with-list", GetRequestWithList3),
    }


class getRequest(TaggedType[GetRequest]):
    """[192] IMPLICIT Get-Request"""
    tag = 192
    mode = TaggingMode.IMPLICIT
    value: GetRequest


@dataclass
class GetResponseNormal(SequenceType):
    """Get-Response-Normal"""
    invoke_id_and_priority: InvokeIdAndPriority
    result: GetDataResult


class GetResponseNormal1(TaggedType[GetResponseNormal]):
    """[1] IMPLICIT Get-Response-Normal"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: GetResponseNormal


@dataclass
class GetResponseWithDatablock(SequenceType):
    """Get-Response-With-Datablock ::= SEQUENCE {invoke-id-and-priority, result}"""
    invoke_id_and_priority: InvokeIdAndPriority
    result: DataBlockG


class GetResponseWithDatablock2(TaggedType[GetResponseWithDatablock]):
    """[2] IMPLICIT Get-Response-With-Datablock"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: GetResponseWithDatablock


SequenceOfGetDataResult: TypeAlias = SequenceOfType[GetDataResult]
"""SEQUENCE OF GetDataResult"""


@dataclass
class GetResponseWithList(SequenceType):
    """Get-Response-With-List ::= SEQUENCE {invoke-id-and-priority, result}"""
    invoke_id_and_priority: InvokeIdAndPriority
    result: SequenceOfGetDataResult


class GetResponseWithList3(TaggedType[GetResponseWithList]):
    """[3] IMPLICIT Get-Response-With-List"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: GetResponseWithList


class GetResponse(ChoiceType):
    """Get-Response"""
    alternatives = {
        1: NamedType("get-response-normal", GetResponseNormal1),
        2: NamedType("get-response-with-datablock", GetResponseWithDatablock2),
        3: NamedType("get-response-with-list", GetResponseWithList3),
    }


class getResponse(TaggedType[GetResponse]):
    """[196] IMPLICIT Get-Response"""
    tag = 196
    mode = TaggingMode.IMPLICIT
    value: GetResponse


class SetRequestNormal(SequenceType):
    """Set-Request-Normal"""
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


class SetRequestNormal1(TaggedType[SetRequestNormal]):
    """[1] IMPLICIT Set-Request-Normal"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: SetRequestNormal


class SetRequestWithFirstDatablock(SequenceType):
    """Set-Request-With-First-Datablock"""
    invoke_id_and_priority: InvokeIdAndPriority
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection: Optional[SelectiveAccessDescriptor] = None  # OPTIONAL — между mandatory
    datablock: DataBlockSA

    def __init__(self, invoke_id_and_priority: InvokeIdAndPriority,
                 cosem_attribute_descriptor: CosemAttributeDescriptor,
                 datablock: DataBlockSA,
                 access_selection: Optional[SelectiveAccessDescriptor] = None):
        self.invoke_id_and_priority = invoke_id_and_priority
        self.cosem_attribute_descriptor = cosem_attribute_descriptor
        self.datablock = datablock
        self.access_selection = access_selection


class SetRequestWithFirstDatablock2(TaggedType[SetRequestWithFirstDatablock]):
    """[2] IMPLICIT Set-Request-With-First-Datablock"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: SetRequestWithFirstDatablock


class SetRequestWithDatablock(SequenceType):
    """Set-Request-With-Datablock"""
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


class SetRequestWithDatablock3(TaggedType[SetRequestWithDatablock]):
    """[3] IMPLICIT Set-Request-With-Datablock"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: SetRequestWithDatablock


SequenceOfCosemAttributeDescriptorWithSelection: TypeAlias = SequenceOfType[CosemAttributeDescriptorWithSelection]
"""SEQUENCE OF CosemAttributeDescriptorWithSelection"""


@dataclass
class SetRequestWithList(SequenceType):
    """Set-Request-With-List"""
    invoke_id_and_priority: InvokeIdAndPriority
    attribute_descriptor_list: SequenceOfCosemAttributeDescriptorWithSelection
    value_list: SequenceOfData


class SetRequestWithList4(TaggedType[SetRequestWithList]):
    """[4] IMPLICIT Set-Request-With-List"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: SetRequestWithList


@dataclass
class SetRequestWithListAndFirstDatablock(SequenceType):
    """Set-Request-With-List-And-First-Datablock"""
    invoke_id_and_priority: InvokeIdAndPriority
    attribute_descriptor_list: SequenceOfCosemAttributeDescriptorWithSelection
    datablock: DataBlockSA


class SetRequestWithListAndFirstDatablock5(TaggedType[SetRequestWithListAndFirstDatablock]):
    """[5] IMPLICIT Set-Request-With-List-And-First-Datablock"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: SetRequestWithListAndFirstDatablock


class SetRequest(ChoiceType):
    """Set-Request"""
    alternatives = {
        1: NamedType("set-request-normal", SetRequestNormal1),
        2: NamedType("set-request-with-first-datablock", SetRequestWithFirstDatablock2),
        3: NamedType("set-request-with-datablock", SetRequestWithDatablock3),
        4: NamedType("set-request-with-list", SetRequestWithList4),
        5: NamedType("set-request-with-list-and-first-datablock", SetRequestWithListAndFirstDatablock5),
    }


class setRequest(TaggedType[SetRequest]):
    """[193] IMPLICIT Set-Request"""
    tag = 193
    mode = TaggingMode.IMPLICIT
    value: SetRequest


@dataclass
class SetResponseNormal(SequenceType):
    """Set-Response-Normal"""
    invoke_id_and_priority: InvokeIdAndPriority
    result: GetDataResult


class SetResponseNormal1(TaggedType[SetResponseNormal]):
    """[1] IMPLICIT Set-Response-Normal"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: SetResponseNormal


@dataclass
class SetResponseDatablock(SequenceType):
    """Set-Response-Datablock"""
    invoke_id_and_priority: InvokeIdAndPriority
    block_number: Unsigned32


class SetResponseDatablock2(TaggedType[SetResponseDatablock]):
    """[2] IMPLICIT Set-Response-Datablock"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: SetResponseDatablock


@dataclass
class SetResponseLastDatablock(SequenceType):
    """Set-Response-Last-Datablock"""
    invoke_id_and_priority: InvokeIdAndPriority
    result: DataAccessResult
    block_number: Unsigned32


class SetResponseLastDatablock3(TaggedType[SetResponseLastDatablock]):
    """[3] IMPLICIT Set-Response-Last-Datablock"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: SetResponseLastDatablock


SequenceOfDataAccessResult: TypeAlias = SequenceOfType[DataAccessResult]
"""SEQUENCE OF DataAccessResult"""


@dataclass
class SetResponseLastDatablockWithList(SequenceType):
    """Set-Response-Last-Datablock-With-List"""
    invoke_id_and_priority: InvokeIdAndPriority
    result: SequenceOfDataAccessResult
    block_number: Unsigned32


class SetResponseLastDatablockWithList4(TaggedType[SetResponseLastDatablockWithList]):
    """[4] IMPLICIT Set-Response-Last-Datablock-With-List"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: SetResponseLastDatablockWithList


@dataclass
class SetResponseWithList(SequenceType):
    """Set-Response-With-List"""
    invoke_id_and_priority: InvokeIdAndPriority
    result: SequenceOfDataAccessResult


class SetResponseWithList5(TaggedType[SetResponseWithList]):
    """[5] IMPLICIT Set-Response-With-List"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: SetResponseWithList


class SetResponse(ChoiceType):
    """Set-Response"""
    alternatives = {
        1: NamedType("set-response-normal", SetResponseNormal1),
        2: NamedType("set-response-datablock", SetResponseDatablock2),
        3: NamedType("set-response-last-datablock", SetResponseLastDatablock3),
        4: NamedType("set-response-last-datablock-with-list", SetResponseLastDatablockWithList4),
        5: NamedType("set-response-with-list", SetResponseWithList5)
    }


class setResponse(TaggedType[SetResponse]):
    """[197] IMPLICIT Set-Response"""
    tag = 197
    mode = TaggingMode.IMPLICIT
    value: SetResponse


@dataclass
class ActionRequestNormal(SequenceType):
    """Action-Request-Normal"""
    invoke_id_and_priority: InvokeIdAndPriority
    cosem_method_descriptor: CosemMethodDescriptor
    method_invocation_parameters: Optional[Data] = None


class actionRequestNormal(TaggedType[ActionRequestNormal]):
    """[1] IMPLICIT Action-Request-Normal"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: ActionRequestNormal


@dataclass
class ActionRequestNextPblock(SequenceType):
    """Action-Request-Next-Pblock"""
    invoke_id_and_priority: InvokeIdAndPriority
    block_number: Unsigned32


class actionRequestNextPblock(TaggedType[ActionRequestNextPblock]):
    """[2] IMPLICIT Action-Request-Next-Pblock"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: ActionRequestNextPblock


SequenceOfCosemMethodDescriptor: TypeAlias = SequenceOfType[CosemMethodDescriptor]
"""SEQUENCE OF CosemMethodDescriptor"""


@dataclass
class ActionRequestWithList(SequenceType):
    """Action-Request-With-List"""
    invoke_id_and_priority: InvokeIdAndPriority
    cosem_method_descriptor_list: SequenceOfCosemMethodDescriptor
    method_invocation_parameters: SequenceOfData


class actionRequestWithList(TaggedType[ActionRequestWithList]):
    """[3] IMPLICIT Action-Request-With-List"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: ActionRequestWithList


@dataclass
class ActionRequestWithFirstPblock(SequenceType):
    """Action-Request-With-First-Pblock"""
    invoke_id_and_priority: InvokeIdAndPriority
    cosem_method_descriptor: CosemMethodDescriptor
    pblock: DataBlockSA


class actionRequestWithFirstPblock(TaggedType[ActionRequestWithFirstPblock]):
    """[4] IMPLICIT Action-Request-With-First-Pblock"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: ActionRequestWithFirstPblock


@dataclass
class ActionRequestWithListAndFirstPblock(SequenceType):
    """Action-Request-With-List-And-First-Pblock"""
    invoke_id_and_priority: InvokeIdAndPriority
    cosem_method_descriptor_list: SequenceOfCosemMethodDescriptor
    pblock: DataBlockSA


class actionRequestWithListAndFirstPblock(TaggedType[ActionRequestWithListAndFirstPblock]):
    """[5] IMPLICIT Action-Request-With-List-And-First-Pblock"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: ActionRequestWithListAndFirstPblock


@dataclass
class ActionRequestWithPblock(SequenceType):
    """Action-Request-With-Pblock"""
    invoke_id_and_priority: InvokeIdAndPriority
    pblock: DataBlockSA


class actionRequestWithPblock(TaggedType[ActionRequestWithPblock]):
    """[6] IMPLICIT Action-Request-With-Pblock"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    value: ActionRequestWithPblock


class ActionRequest(ChoiceType):
    """Action-Request"""
    alternatives = {
        1: NamedType("action-request-normal", actionRequestNormal),
        2: NamedType("action-request-next-pblock", actionRequestNextPblock),
        3: NamedType("action-request-with-list", actionRequestWithList),
        4: NamedType("action-request-with-first-pblock", actionRequestWithFirstPblock),
        5: NamedType("action-request-with-list-and-first-pblock", actionRequestWithListAndFirstPblock),
        6: NamedType("action-request-with-pblock", actionRequestWithPblock)
    }


class actionRequest(TaggedType[ActionRequest]):
    """[195] IMPLICIT Action-Request"""
    tag = 195
    mode = TaggingMode.IMPLICIT
    value: ActionRequest


@dataclass
class ActionResponseNormal(SequenceType):
    """Action-Response-Normal"""
    invoke_id_and_priority: InvokeIdAndPriority
    single_response: ActionResponseWithOptionalData


class actionResponseNormal(TaggedType[ActionResponseNormal]):
    """action-response-normal"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: ActionResponseNormal


@dataclass
class ActionResponseWithPblock(SequenceType):
    """Action-Response-With-Pblock"""
    invoke_id_and_priority: InvokeIdAndPriority
    pblock: DataBlockSA


class actionResponseWithPblock(TaggedType[ActionResponseWithPblock]):
    """action-response-with-pblock"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: ActionResponseWithPblock


SequenceOfActionResponseWithOptionalData: TypeAlias = SequenceOfType[ActionResponseWithOptionalData]
"""SEQUENCE OF ActionResponseWithOptionalData"""


@dataclass
class ActionResponseWithList(SequenceType):
    """Action-Response-With-List"""
    invoke_id_and_priority: InvokeIdAndPriority
    list_of_responses: SequenceOfActionResponseWithOptionalData


class actionResponseWithList(TaggedType[ActionResponseWithList]):
    """action-response-with-list"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: ActionResponseWithList


@dataclass
class ActionResponseNextPblock(SequenceType):
    """Action-Response-Next-Pblock"""
    invoke_id_and_priority: InvokeIdAndPriority
    block_number: Unsigned32


class actionResponseNextPblock(TaggedType[ActionResponseNextPblock]):
    """action-response-next-pblock"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: ActionResponseNextPblock


class ActionResponse(ChoiceType):
    """Action-Response"""
    alternatives = {
        1: NamedType("action-response-normal", actionResponseNormal),
        2: NamedType("action-response-with-pblock", actionResponseWithPblock),
        3: NamedType("action-response-with-list", actionResponseWithList),
        4: NamedType("action-response-next-pblock", actionResponseNextPblock)
    }


class actionResponse(TaggedType[ActionResponse]):
    """[199] IMPLICIT Action-Response"""
    tag = 199
    mode = TaggingMode.IMPLICIT
    value: ActionResponse


class EventNotificationRequest(SequenceType):
    """EventNotificationRequest"""
    time: Optional[OctetStringType] = None  # OPTIONAL — before mandatory
    cosem_attribute_descriptor: CosemAttributeDescriptor
    attribute_value: Data

    def __init__(self, cosem_attribute_descriptor: CosemAttributeDescriptor,
                 attribute_value: Data,
                 time: Optional[OctetStringType] = None) -> None:
        self.cosem_attribute_descriptor = cosem_attribute_descriptor
        self.attribute_value = attribute_value
        self.time = time


class eventNotificationRequest(TaggedType[EventNotificationRequest]):
    """[194] IMPLICIT EventNotificationRequest"""
    tag = 194
    mode = TaggingMode.IMPLICIT
    value: EventNotificationRequest


class gloGetRequest(TaggedType[OctetStringType]):
    """[200] IMPLICIT glo-get-request"""
    tag = 200
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class gloSetRequest(TaggedType[OctetStringType]):
    """[201] IMPLICIT glo-set-request"""
    tag = 201
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class gloEventNotificationRequest(TaggedType[OctetStringType]):
    """[202] IMPLICIT glo-event-notification-request"""
    tag = 202
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class gloActionRequest(TaggedType[OctetStringType]):
    """[203] IMPLICIT glo-action-request"""
    tag = 203
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class gloGetResponse(TaggedType[OctetStringType]):
    """[204] IMPLICIT glo-get-response"""
    tag = 204
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class gloSetResponse(TaggedType[OctetStringType]):
    """[205] IMPLICIT glo-set-response"""
    tag = 205
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class gloActionResponse(TaggedType[OctetStringType]):
    """[207] IMPLICIT glo-action-response"""
    tag = 207
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class dedGetRequest(TaggedType[OctetStringType]):
    """[208] IMPLICIT ded-get-request"""
    tag = 208
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class dedSetRequest(TaggedType[OctetStringType]):
    """[209] IMPLICIT ded-set-request"""
    tag = 209
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class dedEventNotificationRequest(TaggedType[OctetStringType]):
    """[210] IMPLICIT ded-event-notification-request"""
    tag = 210
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class dedActionRequest(TaggedType[OctetStringType]):
    """[211] IMPLICIT ded-action-request"""
    tag = 211
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class dedGetResponse(TaggedType[OctetStringType]):
    """[212] IMPLICIT ded-get-response"""
    tag = 212
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class dedSetResponse(TaggedType[OctetStringType]):
    """[213] IMPLICIT ded-set-response"""
    tag = 213
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class dedActionResponse(TaggedType[OctetStringType]):
    """[215] IMPLICIT ded-action-response"""
    tag = 215
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


class StateErrorList(EnumerationList):
    members = (
        EnumerationMember("service-not-allowed", 1),
        EnumerationMember("service-unknown", 2)
    )


class StateErrorEnum(EnumeratedType):
    named_members = StateErrorList()


class StateError(TaggedType[StateErrorEnum]):
    """[0] IMPLICIT state-error"""
    tag = 0
    mode = TaggingMode.IMPLICIT
    value: StateErrorEnum
    SERVICE_NOT_ALLOWED: ClassVar["StateError"]
    SERVICE_UNKNOWN: ClassVar["StateError"]


StateError.SERVICE_NOT_ALLOWED = StateError(StateErrorEnum(1))
StateError.SERVICE_UNKNOWN = StateError(StateErrorEnum(2))


class OperationNotPossible(TaggedType[NullType]):
    """operation-not-possible"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: NullType


class ServiceNotSupported(TaggedType[NullType]):
    """service-not-supported"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: NullType


class OtherReason(TaggedType[NullType]):
    """other-reason"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: NullType


class PduTooLong(TaggedType[NullType]):
    """pdu-too-long"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: NullType


class DecipheringError(TaggedType[NullType]):
    """deciphering-error"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: NullType


class InvocationCounterError(TaggedType[Unsigned32]):
    """invocation-counter-error"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    value: Unsigned32


class ServiceErrorChoice(ChoiceType):
    """ CHOICE
    {
    operation-not-possible [1] IMPLICIT NULL,
    service-not-supported [2] IMPLICIT NULL,
    other-reason [3] IMPLICIT NULL,
    pdu-too-long [4] IMPLICIT NULL,
    deciphering-error [5] IMPLICIT NULL,
    invocation-counter-error [6] IMPLICIT Unsigned32
    }"""
    alternatives = {
        1: NamedType("operation-not-possible", OperationNotPossible),
        2: NamedType("service-not-supported", ServiceNotSupported),
        3: NamedType("other-reason", OtherReason),
        4: NamedType("pdu-too-long", PduTooLong),
        5: NamedType("deciphering-error", DecipheringError),
        6: NamedType("invocation-counter-error", InvocationCounterError)
    }


class serviceError(TaggedType[ServiceErrorChoice]):
    """service-error"""
    tag = 1
    mode = TaggingMode.DEFAULT
    value: ServiceErrorChoice
    OPERATION_NOT_POSSIBLE: ClassVar["serviceError"]
    SERVICE_NOT_SUPPORTED: ClassVar["serviceError"]
    OTHER_REASON: ClassVar["serviceError"]
    PDU_TOO_LONG: ClassVar["serviceError"]
    DECIPHERING_ERROR: ClassVar["serviceError"]


serviceError.OPERATION_NOT_POSSIBLE = serviceError(ServiceErrorChoice(OperationNotPossible(NullType(None))))
serviceError.SERVICE_NOT_SUPPORTED = serviceError(ServiceErrorChoice(ServiceNotSupported(NullType(None))))
serviceError.OTHER_REASON = serviceError(ServiceErrorChoice(OtherReason(NullType(None))))
serviceError.PDU_TOO_LONG = serviceError(ServiceErrorChoice(PduTooLong(NullType(None))))
serviceError.DECIPHERING_ERROR = serviceError(ServiceErrorChoice(DecipheringError(NullType(None))))


@dataclass
class ExceptionResponse(SequenceType):
    """ExceptionResponse"""
    state_error: StateError
    service_error: serviceError


class exceptionResponse(TaggedType[ExceptionResponse]):
    """[216] IMPLICIT exception-response"""
    tag = 216
    mode = TaggingMode.IMPLICIT
    value: ExceptionResponse


@dataclass
class AccessRequest(SequenceType):
    """Access-Request"""
    long_invoke_id_and_priority: LongInvokeIdAndPriority
    date_time: OctetStringType
    access_request_body: AccessRequestBody


class accessRequest(TaggedType[AccessRequest]):
    """[217] IMPLICIT Access-Request"""
    tag = 217
    mode = TaggingMode.IMPLICIT
    value: AccessRequest


@dataclass
class AccessResponse(SequenceType):
    """Access-Response"""
    long_invoke_id_and_priority: LongInvokeIdAndPriority
    date_time: OctetStringType
    access_response_body: AccessResponseBody


class accessResponse(TaggedType[AccessResponse]):
    """[218] IMPLICIT Access-Response"""
    tag = 218
    mode = TaggingMode.IMPLICIT
    value: AccessResponse


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
class GeneralDedCiphering(SequenceType):
    """General-Ded-Ciphering"""
    system_title: OctetStringType
    ciphered_content: OctetStringType


class generalDedCiphering(TaggedType[GeneralDedCiphering]):
    """[220] IMPLICIT generalDedCiphering"""
    tag = 220
    mode = TaggingMode.IMPLICIT
    value: GeneralDedCiphering


@dataclass
class GeneralGloCiphering(SequenceType):
    """General-Glo-Ciphering"""
    system_title: OctetStringType
    ciphered_content: OctetStringType


class generalGloCiphering(TaggedType[GeneralGloCiphering]):
    """[219] IMPLICIT generalGloCiphering"""
    tag = 219
    mode = TaggingMode.IMPLICIT
    value: GeneralGloCiphering


@dataclass
class GeneralCiphering(SequenceType):
    """General-Ciphering"""
    transaction_id: OctetStringType
    originator_system_title: OctetStringType
    recipient_system_title: OctetStringType
    date_time: OctetStringType
    other_information: OctetStringType
    key_info: KeyInfo
    ciphered_content: OctetStringType


class generalCiphering(TaggedType[GeneralCiphering]):
    """[221] IMPLICIT generalCiphering"""
    tag = 221
    mode = TaggingMode.IMPLICIT
    value: GeneralCiphering


@dataclass
class GeneralSigning(SequenceType):
    """General-Signing"""
    transaction_id: OctetStringType
    originator_system_title: OctetStringType
    recipient_system_title: OctetStringType
    date_time: OctetStringType
    other_information: OctetStringType
    content: OctetStringType
    signature: OctetStringType


class generalSigning(TaggedType[GeneralSigning]):
    """[223] IMPLICIT generalSigning"""
    tag = 223
    mode = TaggingMode.IMPLICIT
    value: GeneralSigning


@dataclass
class GeneralBlockTransfer(SequenceType):
    """General-Block-Transfer"""
    block_control: BlockControl
    block_number: Unsigned16
    block_number_ack: Unsigned16
    block_data: OctetStringType


class generalBlockTransfer(TaggedType[GeneralBlockTransfer]):
    """[224] IMPLICIT generalBlockTransfer"""
    tag = 224
    mode = TaggingMode.IMPLICIT
    value: GeneralBlockTransfer


# ============================================================================
# -- XDLMS-APDU Top-Level Choice (COSEMpdu_GB83.txt)
# ============================================================================


class XDLMS_APDU(ChoiceType):
    """XDLMS-APDU"""
    alternatives = {
        1: NamedType("initiateRequest", initialRequest),
        5: NamedType("readRequest", readRequest),
        6: NamedType("writeRequest", writeRequest),
        8: NamedType("initiateResponse", initialResponse),
        12: NamedType("readResponse", readResponse),
        13: NamedType("writeResponse", writeResponse),
        14: NamedType("confirmedServiceError", confirmedServiceError),
        15: NamedType("data-notification", dataNotification),
        16: NamedType("data-notification-confirm", dataNotificationConfirm),
        22: NamedType("unconfirmedWriteRequest", unconfirmedWriteRequest),
        24: NamedType("informationReportRequest", informationReportRequest),
        # -- with global ciphering (OCTET STRING)
        33: NamedType("glo-initiateRequest", GloInitiateRequest),
        37: NamedType("glo-readRequest", GloReadRequest),
        38: NamedType("glo-writeRequest", GloWriteRequest),
        40: NamedType("glo-initiateResponse", GloInitiateResponse),
        44: NamedType("glo-readResponse", GloReadResponse),
        45: NamedType("glo-writeResponse", GloWriteResponse),
        46: NamedType("glo-confirmedServiceError", GloConfirmedServiceError),
        54: NamedType("glo-unconfirmedWriteRequest", GloUnconfirmedWriteRequest),
        56: NamedType("glo-informationReportRequest", GloInformationReportRequest),
        # -- with dedicated ciphering (OCTET STRING)
        65: NamedType("ded-initiateRequest", DedInitiateRequest),
        69: NamedType("ded-readRequest", DedReadRequest),
        70: NamedType("ded-writeRequest", DedWriteRequest),
        72: NamedType("ded-initiateResponse", DedInitiateResponse),
        76: NamedType("ded-readResponse", DedReadResponse),
        77: NamedType("ded-writeResponse", DedWriteResponse),
        78: NamedType("ded-confirmedServiceError", DedConfirmedServiceError),
        86: NamedType("ded-unconfirmedWriteRequest", DedUnconfirmedWriteRequest),
        88: NamedType("ded-informationReportRequest", DedInformationReportRequest),
        # -- xDLMS APDUs used with LN referencing -- with no ciphering
        192: NamedType("get-request", getRequest),
        193: NamedType("set-request", setRequest),
        194: NamedType("event-notification-request", eventNotificationRequest),
        195: NamedType("action-request", actionRequest),
        196: NamedType("get-response", getResponse),
        197: NamedType("set-response", setResponse),
        199: NamedType("action-response", actionResponse),
        # -- with global ciphering (LN)
        200: NamedType("glo-get-request", gloGetRequest),
        201: NamedType("glo-set-request", gloSetRequest),
        202: NamedType("glo-event-notification-request", gloEventNotificationRequest),
        203: NamedType("glo-action-request", gloActionRequest),
        204: NamedType("glo-get-response", gloGetResponse),
        205: NamedType("glo-set-response", gloSetResponse),
        207: NamedType("glo-action-response", gloActionResponse),
        # -- with dedicated ciphering (LN)
        208: NamedType("ded-get-request", dedGetRequest),
        209: NamedType("ded-set-request", dedSetRequest),
        210: NamedType("ded-event-notification-request", dedEventNotificationRequest),
        211: NamedType("ded-actionRequest", dedActionRequest),
        212: NamedType("ded-get-response", dedGetResponse),
        213: NamedType("ded-set-response", dedSetResponse),
        215: NamedType("ded-action-response", dedActionResponse),
        # -- the exception response pdu
        216: NamedType("exception-response", exceptionResponse),
        # -- access
        217: NamedType("access-request", accessRequest),
        218: NamedType("access-response", accessResponse),
        # -- general APDUs
        219: NamedType("general-glo-ciphering", generalGloCiphering),
        220: NamedType("general-ded-ciphering", generalDedCiphering),
        221: NamedType("general-ciphering", generalCiphering),
        223: NamedType("general-signing", generalSigning),
        224: NamedType("general-block-transfer", generalBlockTransfer),
        # -- The tags 230 and 231 are reserved for DLMS Gateway
    }
