from dataclasses import dataclass
from typing import Self
from .x680.enumerated_type import EnumerationList, EnumerationMember
from .x680.tagged_type import TaggingMode
from .x680.type import NamedType
from .axdr import create_alternatives
from . import axdr


# =============================================================================
# application-reference [0] IMPLICIT ENUMERATED
# =============================================================================

@dataclass
class ApplicationReferenceList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("time-elapsed", 1),
        EnumerationMember("application-unreachable", 2),
        EnumerationMember("application-reference-invalid", 3),
        EnumerationMember("application-context-unsupported", 4),
        EnumerationMember("provider-communication-error", 5),
        EnumerationMember("deciphering-error", 6)
    )


@dataclass
class ApplicationReferenceEnum(axdr.EnumeratedType):
    """application-reference"""
    named_members = ApplicationReferenceList()


@dataclass
class ApplicationReference(axdr.TaggedType):
    """application-reference"""
    tag = 0
    mode = TaggingMode.IMPLICIT
    type_ = ApplicationReferenceEnum


# =============================================================================
# hardware-resource [1] IMPLICIT ENUMERATED
# =============================================================================

@dataclass
class HardwareResourceList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("memory-unavailable", 1),
        EnumerationMember("processor-resource-unavailable", 2),
        EnumerationMember("mass-storage-unavailable", 3),
        EnumerationMember("other-resource-unavailable", 4)
    )


@dataclass
class HardwareResourceEnum(axdr.EnumeratedType):
    """hardware-resource"""
    named_members = HardwareResourceList()


@dataclass
class HardwareResource(axdr.TaggedType):
    """hardware-resource"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    type_ = HardwareResourceEnum


# =============================================================================
# vde-state-error [2] IMPLICIT ENUMERATED
# =============================================================================

@dataclass
class VDEStateErrorList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("no-dlms-context", 1),
        EnumerationMember("loading-data-set", 2),
        EnumerationMember("status-nochange", 3),
        EnumerationMember("status-inoperable", 4)
    )


@dataclass
class VDEStateErrorEnum(axdr.EnumeratedType):
    """vde-state-error"""
    named_members = VDEStateErrorList()


@dataclass
class VDEStateError(axdr.TaggedType):
    """vde-state-error"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    type_ = VDEStateErrorEnum


# =============================================================================
# service [3] IMPLICIT ENUMERATED
# =============================================================================

@dataclass
class ServiceList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("pdu-size", 1),
        EnumerationMember("service-unsupported", 2)
    )


@dataclass
class ServiceEnum(axdr.EnumeratedType):
    """service"""
    named_members = ServiceList()


@dataclass
class Service(axdr.TaggedType):
    """service"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    type_ = ServiceEnum


# =============================================================================
# definition [4] IMPLICIT ENUMERATED
# =============================================================================

@dataclass
class DefinitionList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("object-undefined", 1),
        EnumerationMember("object-class-inconsistent", 2),
        EnumerationMember("object-attribute-inconsistent", 3)
    )


@dataclass
class DefinitionEnum(axdr.EnumeratedType):
    """definition"""
    named_members = DefinitionList()


@dataclass
class Definition(axdr.TaggedType):
    """definition"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    type_ = DefinitionEnum


# =============================================================================
# access [5] IMPLICIT ENUMERATED
# =============================================================================

@dataclass
class AccessList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("scope-of-access-violated", 1),
        EnumerationMember("object-access-violated", 2),
        EnumerationMember("hardware-fault", 3),
        EnumerationMember("object-unavailable", 4)
    )


@dataclass
class AccessEnum(axdr.EnumeratedType):
    """access"""
    named_members = AccessList()


@dataclass
class Access(axdr.TaggedType):
    """access"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    type_ = AccessEnum


# =============================================================================
# initiate [6] IMPLICIT ENUMERATED
# =============================================================================

@dataclass
class InitiateList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("dlms-version-too-low", 1),
        EnumerationMember("incompatible-conformance", 2),
        EnumerationMember("pdu-size-too-short", 3),
        EnumerationMember("refused-by-the-vde-handler", 4)
    )


@dataclass
class InitiateEnum(axdr.EnumeratedType):
    """initiate"""
    named_members = InitiateList()


@dataclass
class Initiate(axdr.TaggedType):
    """initiate"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    type_ = InitiateEnum


# =============================================================================
# load-data-set [7] IMPLICIT ENUMERATED
# =============================================================================

@dataclass
class LoadDataSetList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("primitive-out-of-sequence", 1),
        EnumerationMember("not-loadable", 2),
        EnumerationMember("dataset-size-too-large", 3),
        EnumerationMember("not-awaited-segment", 4),
        EnumerationMember("interpretation-failure", 5),
        EnumerationMember("storage-failure", 6),
        EnumerationMember("data-set-not-ready", 7)
    )


@dataclass
class LoadDataSetEnum(axdr.EnumeratedType):
    """load-data-set"""
    named_members = LoadDataSetList()


@dataclass
class LoadDataSet(axdr.TaggedType):
    """load-data-set"""
    tag = 7
    mode = TaggingMode.IMPLICIT
    type_ = LoadDataSetEnum


# =============================================================================
# task [9] IMPLICIT ENUMERATED
# =============================================================================

@dataclass
class TaskList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("no-remote-control", 1),
        EnumerationMember("ti-stopped", 2),
        EnumerationMember("ti-running", 3),
        EnumerationMember("ti-unusable", 4)
    )


@dataclass
class TaskEnum(axdr.EnumeratedType):
    """task"""
    named_members = TaskList()


@dataclass
class Task(axdr.TaggedType):
    """task"""
    tag = 9
    mode = TaggingMode.IMPLICIT
    type_ = TaskEnum


@dataclass
class ChangeScopeEnum(axdr.EnumeratedType): ...


@dataclass
class ChangeScope(axdr.TaggedType):
    """change-scope"""
    tag = 8
    mode = TaggingMode.IMPLICIT
    type_ = ChangeScopeEnum


@dataclass
class OtherEnum(axdr.EnumeratedType): ...


@dataclass
class Other(axdr.TaggedType):
    """Other"""
    tag = 10
    mode = TaggingMode.IMPLICIT
    type_ = OtherEnum


# =============================================================================
# ServiceError CHOICE
# =============================================================================

@dataclass
class ServiceError(axdr.ChoiceType):
    """ServiceError"""
    alternatives = create_alternatives((
        NamedType("application-reference", ApplicationReference),
        NamedType("hardware-resource", HardwareResource),
        NamedType("vde-state-error", VDEStateError),
        NamedType("service", Service),
        NamedType("definition", Definition),
        NamedType("access", Access),
        NamedType("initiate", Initiate),
        NamedType("load-data-set", LoadDataSet),
        NamedType("change-scope", ChangeScope),
        NamedType("task", Task),
        NamedType("other", Other),
    ))

    @classmethod
    def access(cls, value: AccessEnum) -> Self:
        return cls(Access(value))


@dataclass
class InitiateError(axdr.TaggedType):
    """[1] ServiceError"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class GetStatus(axdr.TaggedType):
    """[2] ServiceError"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class GetNameList(axdr.TaggedType):
    """[3] ServiceError"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class GetVariableAttribute(axdr.TaggedType):
    """[4] ServiceError"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class Read(axdr.TaggedType):
    """[5] ServiceError"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class Write(axdr.TaggedType):
    """[6] ServiceError"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class GetDataSetAttribute(axdr.TaggedType):
    """[7] ServiceError"""
    tag = 7
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class GetTIAttribute(axdr.TaggedType):
    """[8] ServiceError"""
    tag = 8
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class ChangeScope(axdr.TaggedType):
    """[9] ServiceError"""
    tag = 9
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class Start(axdr.TaggedType):
    """[10] ServiceError"""
    tag = 10
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class Stop(axdr.TaggedType):
    """[11] ServiceError"""
    tag = 11
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class Resume(axdr.TaggedType):
    """[12] ServiceError"""
    tag = 12
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class MakeUsable(axdr.TaggedType):
    """[13] ServiceError"""
    tag = 13
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class InitiateLoad(axdr.TaggedType):
    """[14] ServiceError"""
    tag = 14
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class LoadSegment(axdr.TaggedType):
    """[15] ServiceError"""
    tag = 15
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class TerminateLoad(axdr.TaggedType):
    """[16] ServiceError"""
    tag = 16
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class InitiateUpLoad(axdr.TaggedType):
    """[17] ServiceError"""
    tag = 17
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class UpLoadSegment(axdr.TaggedType):
    """[18] ServiceError"""
    tag = 18
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class TerminateUpLoad(axdr.TaggedType):
    """[19] ServiceError"""
    tag = 19
    mode = TaggingMode.IMPLICIT
    type_ = ServiceError


@dataclass
class ConfirmedServiceError(axdr.ChoiceType):
    """ConfirmedServiceError"""
    alternatives = create_alternatives((
        NamedType("initiate-error", InitiateError),
        NamedType("get-status", GetStatus),
        NamedType("get-name-list", GetNameList),
        NamedType("get-variable-attribute", GetVariableAttribute),
        NamedType("read", Read),
        NamedType("write", Write),
        NamedType("get-data-set-attribute", GetDataSetAttribute),
        NamedType("get-ti-attribute", GetTIAttribute),
        NamedType("change-scope", ChangeScope),
        NamedType("start", Start),
        NamedType("stop", Stop),
        NamedType("resume", Resume),
        NamedType("make-usable", MakeUsable),
        NamedType("initiate-load", InitiateLoad),
        NamedType("load-segment", LoadSegment),
        NamedType("terminate-load", TerminateLoad),
        NamedType("initiate-upload", InitiateUpLoad),
        NamedType("upload-segment", UpLoadSegment),
        NamedType("terminate-upload", TerminateUpLoad),
    ))

    @classmethod
    def initiate(cls, value: ServiceError) -> Self:
        return cls(InitiateError(value))

    @classmethod
    def read(cls, value: ServiceError) -> Self:
        return cls(Read(value))

    @classmethod
    def write(cls, value: ServiceError) -> Self:
        return cls(Write(value))
