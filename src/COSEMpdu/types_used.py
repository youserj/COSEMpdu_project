from typing import Final, Optional, Self, Literal, ClassVar, TypeAlias
from dataclasses import dataclass
from StructResult.result import ValueOrError, Error
from .x680.type import TYPE_VALUE, INTEGER, InitError
from .byte_buffer import ByteBuffer
from .x680.constrained_type import SizeConstraint
from .data import Data, Integer8, Unsigned8, Unsigned16, Unsigned32, ObjectName
from .axdr import (
    ConstrainedOctetStringType, OctetStringType, SequenceOfType, EnumeratedType, SequenceType,
    BooleanType, ChoiceType, ImplicitTaggedType
)


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
    selector_parameters: ClassVar[Optional[dict[int, type[ImplicitTaggedType]]]] = None

    def __post_init__(self) -> None:
        if self.selector_parameters is not None:
            if (expected_type := self.selector_parameters.get(self.access_selector.normalize())) is None:
                raise InitError(f"Unknown access-selector value: {self.access_selector.value}")
            if not isinstance(self.access_parameters, expected_type):
                raise InitError(f"Expected access-parameters type {expected_type.__name__} for selector {self.access_selector.value}, got {type(self.access_parameters).__name__}")

    @classmethod
    def parse(cls, value: tuple[INTEGER, TYPE_VALUE]) -> Self:
        if cls.selector_parameters is None:
            return super().parse(value)
        selector, parameter = value
        if (expected_type := cls.selector_parameters.get(selector)) is None:
            raise InitError(f"Unknown access-selector value: {selector}")
        return cls(Unsigned8.parse(selector), expected_type.parse(parameter))

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        try:
            return super().get_lc(buf)
        except InitError as e:
            return Error.from_e(e)


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
