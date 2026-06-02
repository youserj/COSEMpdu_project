from typing import ClassVar
from .x680.enumerated_type import EnumerationList, EnumerationMember
from .x680.type import NamedType
from .axdr import create_alternatives, ImplicitTaggedType, EnumeratedType
from . import axdr


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


class ApplicationReference(ImplicitTaggedType, EnumeratedType):
    """application-reference [0] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 0
    named_members = ApplicationReferenceList()


class HardwareResourceList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("memory-unavailable", 1),
        EnumerationMember("processor-resource-unavailable", 2),
        EnumerationMember("mass-storage-unavailable", 3),
        EnumerationMember("other-resource-unavailable", 4)
    )


class HardwareResource(ImplicitTaggedType, EnumeratedType):
    """hardware-resource [1] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 1
    named_members = HardwareResourceList()


class VDEStateErrorList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("no-dlms-context", 1),
        EnumerationMember("loading-data-set", 2),
        EnumerationMember("status-nochange", 3),
        EnumerationMember("status-inoperable", 4)
    )


class VDEStateError(ImplicitTaggedType, EnumeratedType):
    """vde-state-error [2] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 2
    named_members = VDEStateErrorList()


class ServiceList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("pdu-size", 1),
        EnumerationMember("service-unsupported", 2)
    )


class Service(ImplicitTaggedType, EnumeratedType):
    """service [3] IMPLICIT ENUMERATED"""
    tag: ClassVar[int] = 3
    named_members = ServiceList()


class DefinitionList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("object-undefined", 1),
        EnumerationMember("object-class-inconsistent", 2),
        EnumerationMember("object-attribute-inconsistent", 3)
    )


class Definition(ImplicitTaggedType, EnumeratedType):
    """definition [4] IMPLICIT ENUMERATED"""
    tag = 4
    named_members = DefinitionList()


class AccessList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("scope-of-access-violated", 1),
        EnumerationMember("object-access-violated", 2),
        EnumerationMember("hardware-fault", 3),
        EnumerationMember("object-unavailable", 4)
    )


class Access(ImplicitTaggedType, EnumeratedType):
    """access [5] IMPLICIT ENUMERATED"""
    tag = 5
    named_members = AccessList()


class InitiateList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("dlms-version-too-low", 1),
        EnumerationMember("incompatible-conformance", 2),
        EnumerationMember("pdu-size-too-short", 3),
        EnumerationMember("refused-by-the-vde-handler", 4)
    )


class Initiate(ImplicitTaggedType, EnumeratedType):
    """initiate [6] IMPLICIT ENUMERATED"""
    tag = 6
    named_members = InitiateList()


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


class LoadDataSet(ImplicitTaggedType, EnumeratedType):
    """load-data-set [7] IMPLICIT ENUMERATED"""
    tag = 7
    named_members = LoadDataSetList()


class TaskList(EnumerationList):
    members = (
        EnumerationMember("other", 0),
        EnumerationMember("no-remote-control", 1),
        EnumerationMember("ti-stopped", 2),
        EnumerationMember("ti-running", 3),
        EnumerationMember("ti-unusable", 4)
    )


class Task(ImplicitTaggedType, EnumeratedType):
    """task [9] IMPLICIT ENUMERATED"""
    tag = 9
    named_members = TaskList()


class Changescope(ImplicitTaggedType, EnumeratedType):
    """change-scope [8] IMPLICIT ENUMERATED"""
    tag = 8


class Other(ImplicitTaggedType, EnumeratedType):
    """other [10] IMPLICIT ENUMERATED"""
    tag = 10


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


class InitiateError(ImplicitTaggedType, ServiceError):
    """[1] ServiceError"""
    tag = 1


class GetStatus(ImplicitTaggedType, ServiceError):
    """[2] ServiceError"""
    tag = 2


class GetNameList(ImplicitTaggedType, ServiceError):
    """[3] ServiceError"""
    tag = 3


class GetVariableAttribute(ImplicitTaggedType, ServiceError):
    """[4] ServiceError"""
    tag = 4


class Read(ImplicitTaggedType, ServiceError):
    """[5] ServiceError"""
    tag = 5


class Write(ImplicitTaggedType, ServiceError):
    """[6] ServiceError"""
    tag = 6


class GetDataSetAttribute(ImplicitTaggedType, ServiceError):
    """[7] ServiceError"""
    tag = 7


class GetTIAttribute(ImplicitTaggedType, ServiceError):
    """[8] ServiceError"""
    tag = 8


class ChangeScope(ImplicitTaggedType, ServiceError):
    """[9] ServiceError"""
    tag = 9


class Start(ImplicitTaggedType, ServiceError):
    """[10] ServiceError"""
    tag = 10


class Stop(ImplicitTaggedType, ServiceError):
    """[11] ServiceError"""
    tag = 11


class Resume(ImplicitTaggedType, ServiceError):
    """[12] ServiceError"""
    tag = 12


class MakeUsable(ImplicitTaggedType, ServiceError):
    """[13] ServiceError"""
    tag = 13


class InitiateLoad(ImplicitTaggedType, ServiceError):
    """[14] ServiceError"""
    tag = 14


class LoadSegment(ImplicitTaggedType, ServiceError):
    """[15] ServiceError"""
    tag = 15


class TerminateLoad(ImplicitTaggedType, ServiceError):
    """[16] ServiceError"""
    tag = 16


class InitiateUpLoad(ImplicitTaggedType, ServiceError):
    """[17] ServiceError"""
    tag = 17


class UpLoadSegment(ImplicitTaggedType, ServiceError):
    """[18] ServiceError"""
    tag = 18


class TerminateUpLoad(ImplicitTaggedType, ServiceError):
    """[19] ServiceError"""
    tag = 19


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
