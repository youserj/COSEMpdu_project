from typing import Self
from .x680.enumerated_type import EnumerationList, EnumerationMember
from .x680.tagged_type import TaggingMode
from .x680.type import NamedType
from .axdr import create_alternatives, TaggedType
from . import axdr


# =============================================================================
# application-reference [0] IMPLICIT ENUMERATED
# =============================================================================

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


class ApplicationReferenceEnum(axdr.EnumeratedType):
    """application-reference"""
    named_members = ApplicationReferenceList()


class ApplicationReference(TaggedType[ApplicationReferenceEnum]):
    """application-reference"""
    tag = 0
    mode = TaggingMode.IMPLICIT
    value: ApplicationReferenceEnum


# =============================================================================
# hardware-resource [1] IMPLICIT ENUMERATED
# =============================================================================

class HardwareResourceList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("memory-unavailable", 1),
        EnumerationMember("processor-resource-unavailable", 2),
        EnumerationMember("mass-storage-unavailable", 3),
        EnumerationMember("other-resource-unavailable", 4)
    )


class HardwareResourceEnum(axdr.EnumeratedType):
    """hardware-resource"""
    named_members = HardwareResourceList()


class HardwareResource(TaggedType[HardwareResourceEnum]):
    """hardware-resource"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: HardwareResourceEnum


# =============================================================================
# vde-state-error [2] IMPLICIT ENUMERATED
# =============================================================================

class VDEStateErrorList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("no-dlms-context", 1),
        EnumerationMember("loading-data-set", 2),
        EnumerationMember("status-nochange", 3),
        EnumerationMember("status-inoperable", 4)
    )


class VDEStateErrorEnum(axdr.EnumeratedType):
    """vde-state-error"""
    named_members = VDEStateErrorList()


class VDEStateError(TaggedType[VDEStateErrorEnum]):
    """vde-state-error"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: VDEStateErrorEnum


# =============================================================================
# service [3] IMPLICIT ENUMERATED
# =============================================================================

class ServiceList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("pdu-size", 1),
        EnumerationMember("service-unsupported", 2)
    )


class ServiceEnum(axdr.EnumeratedType):
    """service"""
    named_members = ServiceList()


class Service(TaggedType[ServiceEnum]):
    """service"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: ServiceEnum


# =============================================================================
# definition [4] IMPLICIT ENUMERATED
# =============================================================================


class DefinitionList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("object-undefined", 1),
        EnumerationMember("object-class-inconsistent", 2),
        EnumerationMember("object-attribute-inconsistent", 3)
    )


class DefinitionEnum(axdr.EnumeratedType):
    """definition"""
    named_members = DefinitionList()


class Definition(TaggedType[DefinitionEnum]):
    """definition"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: DefinitionEnum


# =============================================================================
# access [5] IMPLICIT ENUMERATED
# =============================================================================


class AccessList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("scope-of-access-violated", 1),
        EnumerationMember("object-access-violated", 2),
        EnumerationMember("hardware-fault", 3),
        EnumerationMember("object-unavailable", 4)
    )


class AccessEnum(axdr.EnumeratedType):
    """access"""
    named_members = AccessList()


class Access(TaggedType[AccessEnum]):
    """access"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: AccessEnum


# =============================================================================
# initiate [6] IMPLICIT ENUMERATED
# =============================================================================


class InitiateList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("dlms-version-too-low", 1),
        EnumerationMember("incompatible-conformance", 2),
        EnumerationMember("pdu-size-too-short", 3),
        EnumerationMember("refused-by-the-vde-handler", 4)
    )


class InitiateEnum(axdr.EnumeratedType):
    """initiate"""
    named_members = InitiateList()


class Initiate(TaggedType[InitiateEnum]):
    """initiate"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    value: InitiateEnum


# =============================================================================
# load-data-set [7] IMPLICIT ENUMERATED
# =============================================================================


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


class LoadDataSetEnum(axdr.EnumeratedType):
    """load-data-set"""
    named_members = LoadDataSetList()


class LoadDataSet(TaggedType[LoadDataSetEnum]):
    """load-data-set"""
    tag = 7
    mode = TaggingMode.IMPLICIT
    value: LoadDataSetEnum


# =============================================================================
# task [9] IMPLICIT ENUMERATED
# =============================================================================


class TaskList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("no-remote-control", 1),
        EnumerationMember("ti-stopped", 2),
        EnumerationMember("ti-running", 3),
        EnumerationMember("ti-unusable", 4)
    )


class TaskEnum(axdr.EnumeratedType):
    """task"""
    named_members = TaskList()


class Task(TaggedType[TaskEnum]):
    """task"""
    tag = 9
    mode = TaggingMode.IMPLICIT
    value: TaskEnum


class ChangeScopeEnum(axdr.EnumeratedType): ...


class Changescope(TaggedType[ChangeScopeEnum]):
    """change-scope"""
    tag = 8
    mode = TaggingMode.IMPLICIT
    value: ChangeScopeEnum


class OtherEnum(axdr.EnumeratedType): ...


class Other(TaggedType[OtherEnum]):
    """Other"""
    tag = 10
    mode = TaggingMode.IMPLICIT
    value: OtherEnum


# =============================================================================
# ServiceError CHOICE
# =============================================================================


class ServiceError(axdr.ChoiceType):
    """ServiceError"""
    alternatives = create_alternatives(
        NamedType("application-reference", ApplicationReference),
        NamedType("hardware-resource", HardwareResource),
        NamedType("vde-state-error", VDEStateError),
        NamedType("service", Service),
        NamedType("definition", Definition),
        NamedType("access", Access),
        NamedType("initiate", Initiate),
        NamedType("load-data-set", LoadDataSet),
        NamedType("change-scope", Changescope),
        NamedType("task", Task),
        NamedType("other", Other),
    )

    @classmethod
    def access(cls, value: AccessEnum) -> Self:
        return cls(Access(value))


class InitiateError(TaggedType[ServiceError]):
    """[1] ServiceError"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class GetStatus(TaggedType[ServiceError]):
    """[2] ServiceError"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class GetNameList(TaggedType[ServiceError]):
    """[3] ServiceError"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class GetVariableAttribute(TaggedType[ServiceError]):
    """[4] ServiceError"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class Read(TaggedType[ServiceError]):
    """[5] ServiceError"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class Write(TaggedType[ServiceError]):
    """[6] ServiceError"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class GetDataSetAttribute(TaggedType[ServiceError]):
    """[7] ServiceError"""
    tag = 7
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class GetTIAttribute(TaggedType[ServiceError]):
    """[8] ServiceError"""
    tag = 8
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class ChangeScope(TaggedType[ServiceError]):
    """[9] ServiceError"""
    tag = 9
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class Start(TaggedType[ServiceError]):
    """[10] ServiceError"""
    tag = 10
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class Stop(TaggedType[ServiceError]):
    """[11] ServiceError"""
    tag = 11
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class Resume(TaggedType[ServiceError]):
    """[12] ServiceError"""
    tag = 12
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class MakeUsable(TaggedType[ServiceError]):
    """[13] ServiceError"""
    tag = 13
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class InitiateLoad(TaggedType[ServiceError]):
    """[14] ServiceError"""
    tag = 14
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class LoadSegment(TaggedType[ServiceError]):
    """[15] ServiceError"""
    tag = 15
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class TerminateLoad(TaggedType[ServiceError]):
    """[16] ServiceError"""
    tag = 16
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class InitiateUpLoad(TaggedType[ServiceError]):
    """[17] ServiceError"""
    tag = 17
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class UpLoadSegment(TaggedType[ServiceError]):
    """[18] ServiceError"""
    tag = 18
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class TerminateUpLoad(TaggedType[ServiceError]):
    """[19] ServiceError"""
    tag = 19
    mode = TaggingMode.IMPLICIT
    value: ServiceError


class ConfirmedServiceError(axdr.ChoiceType):
    """ConfirmedServiceError"""
    alternatives = create_alternatives(
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
    )

    @classmethod
    def initiate(cls, value: ServiceError) -> Self:
        return cls(InitiateError(value))

    @classmethod
    def read(cls, value: ServiceError) -> Self:
        return cls(Read(value))

    @classmethod
    def write(cls, value: ServiceError) -> Self:
        return cls(Write(value))
