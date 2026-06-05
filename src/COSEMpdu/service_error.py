from typing import ClassVar, Final, Union
from .axdr import ImplicitTaggedType, EnumeratedType
from . import axdr


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


class ServiceError(axdr.ChoiceType):
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


class ConfirmedServiceError(axdr.ChoiceType):
    """ConfirmedServiceError"""
    value: Union[
        InitiateError, GetStatus, GetNameList, GetVariableAttribute, Read, Write,
        GetDataSetAttribute, GetTIAttribute, ChangeScope, Start, Stop, Resume,
        MakeUsable, InitiateLoad, LoadSegment, TerminateLoad, InitiateUpLoad,
        UpLoadSegment, TerminateUpLoad
    ]
