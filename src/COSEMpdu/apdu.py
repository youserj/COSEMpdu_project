"""
COSEM PDU Types Implementation
Based on COSEMpdu_GB83.txt (Green Book 8.3)
Implements A-XDR encoding/decoding according to IEC 61334-6
"""
from dataclasses import dataclass
from typing import ClassVar, Optional, Self
from .data import Data, NullData
from .x680.tagged_type import TaggingMode
from .x680.enumerated_type import EnumerationList, EnumerationMember
from .axdr import (
    ConstrainedIntegerType, EnumeratedType, IntegerType, ConstrainedOctetStringType,
    OctetStringType, BitStringType, SequenceType, SequenceOfType, create_alternatives,
    ChoiceType, TaggedType, NullType, BooleanType, VisibleString, Utf8String, GeneralizedTime, NullType0
)
from .x680.type import STRING, NamedType, OptionalNamedType
from .useful_types import Integer8, Unsigned16, Unsigned8, ObjectName, Unsigned32
from .byte_buffer import ByteBuffer
from .types_used import (
    CosemAttributeDescriptor,
    CosemAttributeDescriptorWithSelection,
    CosemMethodDescriptor,
    InvokeIdAndPriority,
    SelectiveAccessDescriptor,
    VariableAccessSpecification,
    Data0,
    DataAccesResult1,
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


@dataclass
class InitialRequest1(TaggedType[InitiateRequest]):
    """initialRequest"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: InitiateRequest


@dataclass
class InitialResponse8(TaggedType[InitiateResponse]):
    """initialResponse"""
    tag = 8
    mode = TaggingMode.IMPLICIT
    value: InitiateResponse


# ============================================================================
# -- Read/Write Request/Response (COSEMpdu_GB83.txt)
# ============================================================================

@dataclass
class ReadRequest(SequenceOfType[VariableAccessSpecification]):
    """ReadRequest"""
    component_type = VariableAccessSpecification


@dataclass
class ReadRequest5(TaggedType[ReadRequest]):
    """readRequest"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: ReadRequest


@dataclass
class DataBlockResult2(TaggedType[DataBlockResult]):
    """[2] IMPLICIT Data-Block-Result"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: DataBlockResult


@dataclass
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
        NamedType("data-access-error", DataAccesResult1),
        NamedType("data-block-result", DataBlockResult2),
        NamedType("block-number", BlockNumber3),
    )
    value: DataBlockResult2 | DataAccesResult1 | DataBlockResult2 | BlockNumber3


@dataclass
class ReadResponse(SequenceOfType[ReadResponseChoice]):
    """ReadResponse"""
    component_type = ReadResponseChoice


@dataclass
class ReadResponse12(TaggedType[ReadResponse]):
    """[12] IMPLICIT ReadResponse"""
    tag = 12
    mode = TaggingMode.IMPLICIT
    value: ReadResponse


@dataclass
class WriteRequest(SequenceType):
    """WriteRequest"""
    components = (
        NamedType("variable-access-specification", SequenceOfType[VariableAccessSpecification]),
        NamedType("list-of-data", SequenceOfType[Data]),
    )


@dataclass
class WriteRequest6(TaggedType[WriteRequest]):
    """writeRequest"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    value: WriteRequest


@dataclass
class BlockNumber2(TaggedType[Unsigned16]):
    """[2] Unsigned16"""
    tag = 2
    mode = TaggingMode.DEFAULT
    value: Unsigned16


@dataclass
class WriteResponseChoice(ChoiceType):
    """CHOICE {
        success           [0] IMPLICIT NULL,
        data-access-error [1] IMPLICIT Data-Access-Result,
        block-number      [2] Unsigned16
    }
    """
    alternatives = {
        0: NamedType("success", NullType0),
        1: NamedType("data-access-error", DataAccesResult1),
        2: NamedType("block-number", BlockNumber2),
    }
    value: NullType0 | DataAccesResult1 | BlockNumber2
    SUCCESS: ClassVar["WriteResponseChoice"]


WriteResponseChoice.SUCCESS = WriteResponseChoice(NullType0(NullType(None)))


@dataclass
class WriteResponse(SequenceOfType[WriteResponseChoice]):
    """WriteResponse"""
    component_type = WriteResponseChoice


@dataclass
class writeResponse(TaggedType[WriteResponse]):
    """writeResponse"""
    tag = 13
    mode = TaggingMode.IMPLICIT
    value: WriteResponse


@dataclass
class confirmedServiceError(TaggedType[ConfirmedServiceError]):
    """confirmedServiceError"""
    tag = 14
    mode = TaggingMode.IMPLICIT
    value: ConfirmedServiceError


@dataclass
class NotificationBody(SequenceType):
    """NotificationBody"""
    components = (
        NamedType("data-value", Data),
    )


@dataclass
class DataNotification(SequenceType):
    """DataNotification"""
    components = (
        NamedType("long-invoke-id-and-priority", LongInvokeIdAndPriority),
        NamedType("date-time", OctetStringType),
        NamedType("notification-body", NotificationBody),
    )


@dataclass
class DataNotification15(TaggedType[DataNotification]):
    """data-notification"""
    tag = 15
    mode = TaggingMode.IMPLICIT
    value: DataNotification


@dataclass
class DataNotificationConfirm(SequenceType):
    """DataNotificationConfirm"""
    components = (
        NamedType("long-invoke-id-and-priority", LongInvokeIdAndPriority),
        NamedType("date-time", OctetStringType),
    )


@dataclass
class DataNotificationConfirm16(TaggedType[DataNotificationConfirm]):
    """data-notification-confirm"""
    tag = 16
    mode = TaggingMode.IMPLICIT
    value: DataNotificationConfirm


@dataclass
class UnconfirmedWriteRequest(SequenceType):
    """UnconfirmedWriteRequest"""
    components = (
        NamedType("variable-access-specification", SequenceOfType[VariableAccessSpecification]),
        NamedType("list-of-data", SequenceOfType[Data]),
    )


@dataclass
class UnconfirmedWriteRequest22(TaggedType[UnconfirmedWriteRequest]):
    """unconfirmedWriteRequest"""
    tag = 22
    mode = TaggingMode.IMPLICIT
    value: UnconfirmedWriteRequest


@dataclass
class InformationReportRequest(SequenceType):
    """InformationReportRequest"""
    components = (
        OptionalNamedType("current-time", GeneralizedTime),
        NamedType("variable-access-specification", SequenceOfType[VariableAccessSpecification]),
        NamedType("list-of-data", SequenceOfType[Data]),
    )


@dataclass
class InformationReportRequest24(TaggedType[InformationReportRequest]):
    """informationReportRequest"""
    tag = 24
    mode = TaggingMode.IMPLICIT
    value: InformationReportRequest


@dataclass
class GloInitiateRequest(TaggedType[OctetStringType]):
    """glo-initiateRequest"""
    tag = 33
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class GloReadRequest(TaggedType[OctetStringType]):
    """glo-readRequest"""
    tag = 37
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class GloWriteRequest(TaggedType[OctetStringType]):
    """glo-writeRequest"""
    tag = 38
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class GloInitiateResponse(TaggedType[OctetStringType]):
    """glo-initiateResponse"""
    tag = 40
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class GloReadResponse(TaggedType[OctetStringType]):
    """glo-readResponse"""
    tag = 44
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class GloWriteResponse(TaggedType[OctetStringType]):
    """glo-writeResponse"""
    tag = 45
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class GloConfirmedServiceError(TaggedType[OctetStringType]):
    """glo-confirmedServiceError"""
    tag = 46
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class GloUnconfirmedWriteRequest(TaggedType[OctetStringType]):
    """glo-unconfirmedWriteRequest"""
    tag = 54
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class GloInformationReportRequest(TaggedType[OctetStringType]):
    """glo-informationReportRequest"""
    tag = 56
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class DedInitiateRequest(TaggedType[OctetStringType]):
    """ded-initiateRequest"""
    tag = 65
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class DedReadRequest(TaggedType[OctetStringType]):
    """ded-readRequest"""
    tag = 69
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class DedWriteRequest(TaggedType[OctetStringType]):
    """ded-writeRequest"""
    tag = 70
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class DedInitiateResponse(TaggedType[OctetStringType]):
    """ded-initiateResponse"""
    tag = 72
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class DedReadResponse(TaggedType[OctetStringType]):
    """ded-readResponse"""
    tag = 76
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class DedWriteResponse(TaggedType[OctetStringType]):
    """ded-writeResponse"""
    tag = 77
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class DedConfirmedServiceError(TaggedType[OctetStringType]):
    """ded-confirmedServiceError"""
    tag = 78
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class DedUnconfirmedWriteRequest(TaggedType[OctetStringType]):
    """ded-unconfirmedWriteRequest"""
    tag = 86
    mode = TaggingMode.IMPLICIT
    value: OctetStringType

@dataclass
class DedInformationReportRequest(TaggedType[OctetStringType]):
    """ded-informationReportRequest"""
    tag = 88
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class GetRequestNormal(SequenceType):
    """Get-Request-Normal"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("cosem-attribute-descriptor", CosemAttributeDescriptor),
        OptionalNamedType("access-selection", SelectiveAccessDescriptor),
    )


@dataclass
class GetRequestNormal1(TaggedType[GetRequestNormal]):
    """[1] IMPLICIT Get-Request-Normal"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: GetRequestNormal


@dataclass
class GetRequestNext(SequenceType):
    """Get-Request-Next"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("block-number", Unsigned32),
    )


@dataclass
class GetRequestNext2(TaggedType[GetRequestNext]):
    """[2] IMPLICIT Get-Request-Next"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: GetRequestNext


@dataclass
class GetRequestWithList(SequenceType):
    """Get-Request-With-List"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("attribute-descriptor-list", SequenceOfType[CosemAttributeDescriptorWithSelection]),
    )


@dataclass
class GetRequestWithList3(TaggedType[GetRequestWithList]):
    """[3] IMPLICIT Get-Request-With-List"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: GetRequestWithList


@dataclass
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
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("result", GetDataResult),
    )


@dataclass
class GetResponseNormal1(TaggedType[GetResponseNormal]):
    """[1] IMPLICIT Get-Response-Normal"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: GetResponseNormal


@dataclass
class GetResponseWithDatablock(SequenceType):
    """Get-Response-With-Datablock ::= SEQUENCE {invoke-id-and-priority, result}"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("result", DataBlockG),
    )


@dataclass
class GetResponseWithDatablock2(TaggedType[GetResponseWithDatablock]):
    """[2] IMPLICIT Get-Response-With-Datablock"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: GetResponseWithDatablock


@dataclass
class GetResponseWithList(SequenceType):
    """Get-Response-With-List ::= SEQUENCE {invoke-id-and-priority, result}"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("result", SequenceOfType[GetDataResult]),
    )


@dataclass
class GetResponseWithList3(TaggedType[GetResponseWithList]):
    """[3] IMPLICIT Get-Response-With-List"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: GetResponseWithList


@dataclass
class GetResponse(ChoiceType):
    """Get-Response"""
    alternatives = {
        1: NamedType("get-response-normal", GetResponseNormal1),
        2: NamedType("get-response-with-datablock", GetResponseWithDatablock2),
        3: NamedType("get-response-with-list", GetResponseWithList3),
    }


@dataclass
class getResponse(TaggedType[GetResponse]):
    """[196] IMPLICIT Get-Response"""
    tag = 196
    mode = TaggingMode.IMPLICIT
    value: GetResponse


@dataclass
class SetRequestNormal(SequenceType):
    """Set-Request-Normal"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("cosem-attribute-descriptor", CosemAttributeDescriptor),
        OptionalNamedType("access-selection", SelectiveAccessDescriptor),
        NamedType("value", Data),
    )


@dataclass
class SetRequestNormal1(TaggedType[SetRequestNormal]):
    """[1] IMPLICIT Set-Request-Normal"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: SetRequestNormal


@dataclass
class SetRequestWithFirstDatablock(SequenceType):
    """Set-Request-With-First-Datablock"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("cosem-attribute-descriptor", CosemAttributeDescriptor),
        OptionalNamedType("access-selection", SelectiveAccessDescriptor),
        NamedType("datablock", DataBlockSA),
    )


@dataclass
class SetRequestWithFirstDatablock2(TaggedType[SetRequestWithFirstDatablock]):
    """[2] IMPLICIT Set-Request-With-First-Datablock"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: SetRequestWithFirstDatablock


@dataclass
class SetRequestWithDatablock(SequenceType):
    """Set-Request-With-Datablock"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("cosem-attribute-descriptor", CosemAttributeDescriptor),
        OptionalNamedType("access-selection", SelectiveAccessDescriptor),
        NamedType("datablock", DataBlockSA)
    )


@dataclass
class SetRequestWithDatablock3(TaggedType[SetRequestWithDatablock]):
    """[3] IMPLICIT Set-Request-With-Datablock"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: SetRequestWithDatablock


@dataclass
class SetRequestWithList(SequenceType):
    """Set-Request-With-List"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("attribute-descriptor-list", SequenceOfType[CosemAttributeDescriptorWithSelection]),
        NamedType("value-list", SequenceOfType[Data])
    )


@dataclass
class SetRequestWithList4(TaggedType[SetRequestWithList]):
    """[4] IMPLICIT Set-Request-With-List"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: SetRequestWithList


@dataclass
class SetRequestWithListAndFirstDatablock(SequenceType):
    """Set-Request-With-List-And-First-Datablock"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("attribute-descriptor-list", SequenceOfType[CosemAttributeDescriptorWithSelection]),
        NamedType("datablock", DataBlockSA)
    )


@dataclass
class SetRequestWithListAndFirstDatablock5(TaggedType[SetRequestWithListAndFirstDatablock]):
    """[5] IMPLICIT Set-Request-With-List-And-First-Datablock"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: SetRequestWithListAndFirstDatablock


@dataclass
class SetRequest(ChoiceType):
    """Set-Request"""
    alternatives = {
        1: NamedType("set-request-normal", SetRequestNormal1),
        2: NamedType("set-request-with-first-datablock", SetRequestWithFirstDatablock2),
        3: NamedType("set-request-with-datablock", SetRequestWithDatablock3),
        4: NamedType("set-request-with-list", SetRequestWithList4),
        5: NamedType("set-request-with-list-and-first-datablock", SetRequestWithListAndFirstDatablock5),
    }


@dataclass
class setRequest(TaggedType[SetRequest]):
    """[193] IMPLICIT Set-Request"""
    tag = 193
    mode = TaggingMode.IMPLICIT
    value: SetRequest


@dataclass
class SetResponseNormal(SequenceType):
    """Set-Response-Normal"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("result", GetDataResult),
    )


@dataclass
class SetResponseNormal1(TaggedType[SetResponseNormal]):
    """[1] IMPLICIT Set-Response-Normal"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: SetResponseNormal


@dataclass
class SetResponseDatablock(SequenceType):
    """Set-Response-Datablock"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("block-number", Unsigned32)
    )


@dataclass
class SetResponseDatablock2(TaggedType[SetResponseDatablock]):
    """[2] IMPLICIT Set-Response-Datablock"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: SetResponseDatablock


@dataclass
class SetResponseLastDatablock(SequenceType):
    """Set-Response-Last-Datablock"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("result", DataAccessResult),
        NamedType("block-number", Unsigned32)
    )


@dataclass
class SetResponseLastDatablock3(TaggedType[SetResponseLastDatablock]):
    """[3] IMPLICIT Set-Response-Last-Datablock"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: SetResponseLastDatablock


@dataclass
class SetResponseLastDatablockWithList(SequenceType):
    """Set-Response-Last-Datablock-With-List"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("result", SequenceOfType[DataAccessResult]),
        NamedType("block-number", Unsigned32)
    )


@dataclass
class SetResponseLastDatablockWithList4(TaggedType[SetResponseLastDatablockWithList]):
    """[4] IMPLICIT Set-Response-Last-Datablock-With-List"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: SetResponseLastDatablockWithList


@dataclass
class SetResponseWithList(SequenceType):
    """Set-Response-With-List"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("result", SequenceOfType[DataAccessResult]),
    )


@dataclass
class SetResponseWithList5(TaggedType[SetResponseWithList]):
    """[5] IMPLICIT Set-Response-With-List"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: SetResponseWithList


@dataclass
class SetResponse(ChoiceType):
    """Set-Response"""
    alternatives = {
        1: NamedType("set-response-normal", SetResponseNormal1),
        2: NamedType("set-response-datablock", SetResponseDatablock2),
        3: NamedType("set-response-last-datablock", SetResponseLastDatablock3),
        4: NamedType("set-response-last-datablock-with-list", SetResponseLastDatablockWithList4),
        5: NamedType("set-response-with-list", SetResponseWithList5)
    }


@dataclass
class setResponse(TaggedType[SetResponse]):
    """[197] IMPLICIT Set-Response"""
    tag = 197
    mode = TaggingMode.IMPLICIT
    value: SetResponse


@dataclass
class ActionRequestNormal(SequenceType):
    """Action-Request-Normal"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("cosem-method-descriptor", CosemMethodDescriptor),
        OptionalNamedType("method-invocation-parameters", Data)
    )


@dataclass
class ActionRequestNormal1(TaggedType[ActionRequestNormal]):
    """[1] IMPLICIT Action-Request-Normal"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: ActionRequestNormal


@dataclass
class ActionRequestNextPblock(SequenceType):
    """Action-Request-Next-Pblock"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("block-number", Unsigned32)
    )

@dataclass
class ActionRequestNextPblock2(TaggedType[ActionRequestNextPblock]):
    """[2] IMPLICIT Action-Request-Next-Pblock"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: ActionRequestNextPblock


@dataclass
class ActionRequestWithList(SequenceType):
    """Action-Request-With-List"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("cosem-method-descriptor-list", SequenceOfType[CosemMethodDescriptor]),
        NamedType("method-invocation-parameters", SequenceOfType[Data])
    )

@dataclass
class ActionRequestWithList3(TaggedType[ActionRequestWithList]):
    """[3] IMPLICIT Action-Request-With-List"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: ActionRequestWithList


@dataclass
class ActionRequestWithFirstPblock(SequenceType):
    """Action-Request-With-First-Pblock"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("cosem-method-descriptor", CosemMethodDescriptor),
        NamedType("pblock", DataBlockSA)
    )

@dataclass
class ActionRequestWithFirstPblock4(TaggedType[ActionRequestWithFirstPblock]):
    """[4] IMPLICIT Action-Request-With-First-Pblock"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: ActionRequestWithFirstPblock


@dataclass
class ActionRequestWithListAndFirstPblock(SequenceType):
    """Action-Request-With-List-And-First-Pblock"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("cosem-method-descriptor-list", SequenceOfType[CosemMethodDescriptor]),
        NamedType("pblock", DataBlockSA)
    )

@dataclass
class ActionRequestWithListAndFirstPblock5(TaggedType[ActionRequestWithListAndFirstPblock]):
    """[5] IMPLICIT Action-Request-With-List-And-First-Pblock"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: ActionRequestWithListAndFirstPblock


@dataclass
class ActionRequestWithPblock(SequenceType):
    """Action-Request-With-Pblock"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("pblock", DataBlockSA)
    )

@dataclass
class ActionRequestWithPblock6(TaggedType[ActionRequestWithPblock]):
    """[6] IMPLICIT Action-Request-With-Pblock"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    value: ActionRequestWithPblock


@dataclass
class ActionRequest(ChoiceType):
    """Action-Request"""
    alternatives = {
        1: NamedType("action-request-normal", ActionRequestNormal1),
        2: NamedType("action-request-next-pblock", ActionRequestNextPblock2),
        3: NamedType("action-request-with-list", ActionRequestWithList3),
        4: NamedType("action-request-with-first-pblock", ActionRequestWithFirstPblock4),
        5: NamedType("action-request-with-list-and-first-pblock", ActionRequestWithListAndFirstPblock5),
        6: NamedType("action-request-with-pblock", ActionRequestWithPblock6)
    }


@dataclass
class actionRequest(TaggedType[ActionRequest]):
    """[195] IMPLICIT Action-Request"""
    tag = 195
    mode = TaggingMode.IMPLICIT
    value: ActionRequest


@dataclass
class ActionResponseNormal(SequenceType):
    """Action-Response-Normal"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("single-response", ActionResponseWithOptionalData)
    )


@dataclass
class ActionResponseNormal1(TaggedType[ActionResponseNormal]):
    """[1] IMPLICIT Action-Response-Normal"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: ActionResponseNormal


@dataclass
class ActionResponseWithPblock(SequenceType):
    """Action-Response-With-Pblock"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("pblock", DataBlockSA)
    )

@dataclass
class ActionResponseWithPblock2(TaggedType[ActionResponseWithPblock]):
    """[2] IMPLICIT Action-Response-With-Pblock"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: ActionResponseWithPblock


@dataclass
class ActionResponseWithList(SequenceType):
    """Action-Response-With-List"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("list-of-responses", SequenceOfType[ActionResponseWithOptionalData])
    )

@dataclass
class ActionResponseWithList3(TaggedType[ActionResponseWithList]):
    """[3] IMPLICIT Action-Response-With-List"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: ActionResponseWithList


@dataclass
class ActionResponseNextPblock(SequenceType):
    """Action-Response-Next-Pblock"""
    components = (
        NamedType("invoke-id-and-priority", InvokeIdAndPriority),
        NamedType("block-number", Unsigned32)
    )

@dataclass
class ActionResponseNextPblock4(TaggedType[ActionResponseNextPblock]):
    """[4] IMPLICIT Action-Response-Next-Pblock"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: ActionResponseNextPblock


@dataclass
class ActionResponse(ChoiceType):
    """Action-Response"""
    alternatives = {
        1: NamedType("action-response-normal", ActionResponseNormal1),
        2: NamedType("action-response-with-pblock", ActionResponseWithPblock2),
        3: NamedType("action-response-with-list", ActionResponseWithList3),
        4: NamedType("action-response-next-pblock", ActionResponseNextPblock4)
    }


@dataclass
class actionResponse(TaggedType[ActionResponse]):
    """[199] IMPLICIT Action-Response"""
    tag = 199
    mode = TaggingMode.IMPLICIT
    value: ActionResponse


@dataclass
class EventNotificationRequest(SequenceType):
    """EventNotificationRequest"""
    components = (
        OptionalNamedType("time", OctetStringType),
        NamedType("cosem-attribute-descriptor", CosemAttributeDescriptor),
        NamedType("attribute-value", Data)
    )


@dataclass
class eventNotificationRequest(TaggedType[EventNotificationRequest]):
    """[194] IMPLICIT EventNotificationRequest"""
    tag = 194
    mode = TaggingMode.IMPLICIT
    value: EventNotificationRequest


@dataclass
class gloGetRequest(TaggedType[OctetStringType]):
    """[200] IMPLICIT glo-get-request"""
    tag = 200
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class gloSetRequest(TaggedType[OctetStringType]):
    """[201] IMPLICIT glo-set-request"""
    tag = 201
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class gloEventNotificationRequest(TaggedType[OctetStringType]):
    """[202] IMPLICIT glo-event-notification-request"""
    tag = 202
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class gloActionRequest(TaggedType[OctetStringType]):
    """[203] IMPLICIT glo-action-request"""
    tag = 203
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class gloGetResponse(TaggedType[OctetStringType]):
    """[204] IMPLICIT glo-get-response"""
    tag = 204
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class gloSetResponse(TaggedType[OctetStringType]):
    """[205] IMPLICIT glo-set-response"""
    tag = 205
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class gloActionResponse(TaggedType[OctetStringType]):
    """[207] IMPLICIT glo-action-response"""
    tag = 207
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class dedGetRequest(TaggedType[OctetStringType]):
    """[208] IMPLICIT ded-get-request"""
    tag = 208
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class dedSetRequest(TaggedType[OctetStringType]):
    """[209] IMPLICIT ded-set-request"""
    tag = 209
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class dedEventNotificationRequest(TaggedType[OctetStringType]):
    """[210] IMPLICIT ded-event-notification-request"""
    tag = 210
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class dedActionRequest(TaggedType[OctetStringType]):
    """[211] IMPLICIT ded-action-request"""
    tag = 211
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class dedGetResponse(TaggedType[OctetStringType]):
    """[212] IMPLICIT ded-get-response"""
    tag = 212
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class dedSetResponse(TaggedType[OctetStringType]):
    """[213] IMPLICIT ded-set-response"""
    tag = 213
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class dedActionResponse(TaggedType[OctetStringType]):
    """[215] IMPLICIT ded-action-response"""
    tag = 215
    mode = TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class StateErrorList(EnumerationList):
    members = (
        EnumerationMember("service-not-allowed", 1),
        EnumerationMember("service-unknown", 2)
    )


@dataclass(frozen=True)
class StateErrorEnum(EnumeratedType):
    named_members = StateErrorList()


@dataclass
class StateError(TaggedType[StateErrorEnum]):
    """[0] IMPLICIT state-error"""
    tag = 0
    mode = TaggingMode.IMPLICIT
    value: StateErrorEnum
    SERVICE_NOT_ALLOWED: ClassVar["StateError"]
    SERVICE_UNKNOWN: ClassVar["StateError"]


StateError.SERVICE_NOT_ALLOWED = StateError(StateErrorEnum(1))
StateError.SERVICE_UNKNOWN = StateError(StateErrorEnum(2))


@dataclass
class OperationNotPossible(TaggedType[NullType]):
    """operation-not-possible"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class ServiceNotSupported(TaggedType[NullType]):
    """service-not-supported"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class OtherReason(TaggedType[NullType]):
    """other-reason"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class PduTooLong(TaggedType[NullType]):
    """pdu-too-long"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class DecipheringError(TaggedType[NullType]):
    """deciphering-error"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: NullType


@dataclass
class InvocationCounterError(TaggedType[Unsigned32]):
    """invocation-counter-error"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    value: Unsigned32


@dataclass
class ServiceErrorChoice(ChoiceType):
    """service-error"""
    alternatives = {
        1: NamedType("operation-not-possible", OperationNotPossible),
        2: NamedType("service-not-supported", ServiceNotSupported),
        3: NamedType("other-reason", OtherReason),
        4: NamedType("pdu-too-long", PduTooLong),
        5: NamedType("deciphering-error", DecipheringError),
        6: NamedType("invocation-counter-error", InvocationCounterError)
    }


@dataclass
class ServiceError(TaggedType[ServiceErrorChoice]):
    """[1] IMPLICIT service-error"""
    tag = 1
    mode = TaggingMode.DEFAULT
    value: ServiceErrorChoice
    OPERATION_NOT_POSSIBLE: ClassVar["ServiceError"]
    SERVICE_NOT_SUPPORTED: ClassVar["ServiceError"]
    OTHER_REASON: ClassVar["ServiceError"]
    PDU_TOO_LONG: ClassVar["ServiceError"]
    DECIPHERING_ERROR: ClassVar["ServiceError"]


ServiceError.OPERATION_NOT_POSSIBLE = ServiceError(ServiceErrorChoice(OperationNotPossible(NullType(None))))
ServiceError.SERVICE_NOT_SUPPORTED = ServiceError(ServiceErrorChoice(ServiceNotSupported(NullType(None))))
ServiceError.OTHER_REASON = ServiceError(ServiceErrorChoice(OtherReason(NullType(None))))
ServiceError.PDU_TOO_LONG = ServiceError(ServiceErrorChoice(PduTooLong(NullType(None))))
ServiceError.DECIPHERING_ERROR = ServiceError(ServiceErrorChoice(DecipheringError(NullType(None))))


@dataclass
class ExceptionResponse(SequenceType):
    """ExceptionResponse"""
    components = (
        NamedType("state-error", StateError),
        NamedType("service-error", ServiceError)
    )


@dataclass
class exceptionResponse(TaggedType[ExceptionResponse]):
    """[216] IMPLICIT exception-response"""
    tag = 216
    mode = TaggingMode.IMPLICIT
    value: ExceptionResponse


@dataclass
class AccessRequest(SequenceType):
    """Access-Request"""
    components = (
        NamedType("long-invoke-id-and-priority", LongInvokeIdAndPriority),
        NamedType("date-time", OctetStringType),
        NamedType("access-request-body", AccessRequestBody)
    )


@dataclass
class accessRequest(TaggedType[AccessRequest]):
    """[217] IMPLICIT Access-Request"""
    tag = 217
    mode = TaggingMode.IMPLICIT
    value: AccessRequest


@dataclass
class AccessResponse(SequenceType):
    """Access-Response"""
    components = (
        NamedType("long-invoke-id-and-priority", LongInvokeIdAndPriority),
        NamedType("date-time", OctetStringType),
        NamedType("access-response-body", AccessResponseBody)
    )


@dataclass
class accessResponse(TaggedType[AccessResponse]):
    """[218] IMPLICIT Access-Response"""
    tag = 218
    mode = TaggingMode.IMPLICIT
    value: AccessResponse


@dataclass
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
    components = (
        NamedType("system-title", OctetStringType),
        NamedType("ciphered-content", OctetStringType)
    )


@dataclass
class generalDedCiphering(TaggedType[GeneralDedCiphering]):
    """[220] IMPLICIT generalDedCiphering"""
    tag = 220
    mode = TaggingMode.IMPLICIT
    value: GeneralDedCiphering


@dataclass
class GeneralGloCiphering(SequenceType):
    """General-Glo-Ciphering"""
    components = (
        NamedType("system-title", OctetStringType),
        NamedType("ciphered-content", OctetStringType)
    )

@dataclass
class generalGloCiphering(TaggedType[GeneralGloCiphering]):
    """[219] IMPLICIT generalGloCiphering"""
    tag = 219
    mode = TaggingMode.IMPLICIT
    value: GeneralGloCiphering


@dataclass
class GeneralCiphering(SequenceType):
    """General-Ciphering"""
    components = (
        NamedType("transaction-id", OctetStringType),
        NamedType("originator-system-title", OctetStringType),
        NamedType("recipient-system-title", OctetStringType),
        NamedType("date-time", OctetStringType),
        NamedType("other-information", OctetStringType),
        NamedType("key-info", KeyInfo),
        NamedType("ciphered-content", OctetStringType)
    )


@dataclass
class generalCiphering(TaggedType[GeneralCiphering]):
    """[221] IMPLICIT generalCiphering"""
    tag = 221
    mode = TaggingMode.IMPLICIT
    value: GeneralCiphering


@dataclass
class GeneralSigning(SequenceType):
    """General-Signing"""
    components = (
        NamedType("transaction-id", OctetStringType),
        NamedType("originator-system-title", OctetStringType),
        NamedType("recipient-system-title", OctetStringType),
        NamedType("date-time", OctetStringType),
        NamedType("other-information", OctetStringType),
        NamedType("content", OctetStringType),
        NamedType("signature", OctetStringType)
    )


class generalSigning(TaggedType[GeneralSigning]):
    """[223] IMPLICIT generalSigning"""
    tag = 223
    mode = TaggingMode.IMPLICIT
    value: GeneralSigning


@dataclass
class GeneralBlockTransfer(SequenceType):
    """General-Block-Transfer"""
    components = (
        NamedType("block-control", BlockControl),
        NamedType("block-number", Unsigned16),
        NamedType("block-number-ack", Unsigned16),
        NamedType("block-data", OctetStringType)
    )


@dataclass
class generalBlockTransfer(TaggedType[GeneralBlockTransfer]):
    """[224] IMPLICIT generalBlockTransfer"""
    tag = 224
    mode = TaggingMode.IMPLICIT
    value: GeneralBlockTransfer


# ============================================================================
# -- XDLMS-APDU Top-Level Choice (COSEMpdu_GB83.txt)
# ============================================================================


@dataclass
class XDLMS_APDU(ChoiceType):
    """XDLMS-APDU"""
    alternatives = {
        1: NamedType("initiateRequest", InitialRequest1),
        5: NamedType("readRequest", ReadRequest5),
        6: NamedType("writeRequest", WriteRequest6),
        8: NamedType("initiateResponse", InitialResponse8),
        12: NamedType("readResponse", ReadResponse12),
        13: NamedType("writeResponse", writeResponse),
        14: NamedType("confirmedServiceError", confirmedServiceError),
        15: NamedType("data-notification", DataNotification15),
        16: NamedType("data-notification-confirm", DataNotificationConfirm16),
        22: NamedType("unconfirmedWriteRequest", UnconfirmedWriteRequest22),
        24: NamedType("informationReportRequest", InformationReportRequest24),
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
