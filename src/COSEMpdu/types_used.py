from typing import Self, Literal, ClassVar
from .x680.type import (
    NamedType, INTEGER, OCTET_STRING, OptionalNamedType, BOOLEAN
)
from .x680.enumerated_type import EnumerationList, EnumerationMember
from .x680.constrained_type import SizeConstraint
from .x680.tagged_type import TaggingMode
from . import axdr
from .data import Data
from .useful_types import (
    Integer8, Unsigned8, Unsigned16, Unsigned32, ObjectName
)
from .axdr import ConstrainedOctetStringType, TaggedType, IntegerType, OctetStringType, SequenceOfType


# =============================================================================
# ENUMERATED Types (A-XDR: encoded as fixed-length unsigned integer in 1 byte)
# Using EnumerationList pattern from service_error.py
# =============================================================================


class DataAccessResultList(EnumerationList):
    """Data-Access-Result enumeration members"""
    members = (
        EnumerationMember("success", 0),
        EnumerationMember("hardware-fault", 1),
        EnumerationMember("temporary-failure", 2),
        EnumerationMember("read-write-denied", 3),
        EnumerationMember("object-undefined", 4),
        EnumerationMember("object-class-inconsistent", 9),
        EnumerationMember("object-unavailable", 11),
        EnumerationMember("type-unmatched", 12),
        EnumerationMember("scope-of-access-violated", 13),
        EnumerationMember("data-block-unavailable", 14),
        EnumerationMember("long-get-aborted", 15),
        EnumerationMember("no-long-get-in-progress", 16),
        EnumerationMember("long-set-aborted", 17),
        EnumerationMember("no-long-set-in-progress", 18),
        EnumerationMember("data-block-number-invalid", 19),
        EnumerationMember("other-reason", 250),
    )


class DataAccessResult(axdr.EnumeratedType):
    """Data-Access-Result"""
    named_members = DataAccessResultList()
    SUCCESS: ClassVar[Self]


DataAccessResult.SUCCESS = DataAccessResult(0)


class DataAccessResult1(TaggedType[DataAccessResult]):
    """ [1] IMPLICIT Data-Access-Result"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: DataAccessResult


class ActionResultList(EnumerationList):
    """Action-Result enumeration members"""
    members = (
        EnumerationMember("success", 0),
        EnumerationMember("hardware-fault", 1),
        EnumerationMember("temporary-failure", 2),
        EnumerationMember("read-write-denied", 3),
        EnumerationMember("object-undefined", 4),
        EnumerationMember("object-class-inconsistent", 9),
        EnumerationMember("object-unavailable", 11),
        EnumerationMember("type-unmatched", 12),
        EnumerationMember("scope-of-access-violated", 13),
        EnumerationMember("data-block-unavailable", 14),
        EnumerationMember("long-action-aborted", 15),
        EnumerationMember("no-long-action-in-progress", 16),
        EnumerationMember("other-reason", 250),
    )


class ActionResult(axdr.EnumeratedType):
    """Action-Result"""
    named_members = ActionResultList()


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


class CosemAttributeDescriptor(axdr.SequenceType):
    """Cosem-Attribute-Descriptor"""
    components = (
        NamedType("class-id", CosemClassId),
        NamedType("instance-id", CosemObjectInstanceId),
        NamedType("attribute-id", CosemObjectAttributeId),
    )

    @classmethod
    def from_components(
        cls,
        class_id: INTEGER,
        instance_id: OCTET_STRING,
        attribute_id: INTEGER
    ) -> Self:
        return cls((
            CosemClassId(IntegerType(class_id)),
            CosemObjectInstanceId(OctetStringType(instance_id)),
            CosemObjectAttributeId(IntegerType(attribute_id))
        ))


class CosemMethodDescriptor(axdr.SequenceType):
    """Cosem-Method-Descriptor"""
    components = (
        NamedType("class-id", CosemClassId),
        NamedType("instance-id", CosemObjectInstanceId),
        NamedType("method-id", CosemObjectMethodId),
    )

    @classmethod
    def from_components(
        cls,
        class_id: INTEGER,
        instance_id: OCTET_STRING,
        method_id: INTEGER
    ) -> Self:
        return cls((
            CosemClassId(IntegerType(class_id)),
            CosemObjectInstanceId(OctetStringType(instance_id)),
            CosemObjectMethodId(IntegerType(method_id))
        ))


class SelectiveAccessDescriptor(axdr.SequenceType):
    """Selective-Access-Descriptor"""
    components = (
        NamedType("access-selector", Unsigned8),
        NamedType("access-parameters", Data),
    )

    @classmethod
    def from_components(
        cls,
        access_selector: INTEGER,
        access_parameters: Data
    ) -> Self:
        return cls((
            Unsigned8(IntegerType(access_selector)),
            access_parameters
        ))


class CosemAttributeDescriptorWithSelection(axdr.SequenceType):
    """Cosem-Attribute-Descriptor-With-Selection"""
    components = (
        NamedType("cosem-attribute-descriptor", CosemAttributeDescriptor),
        OptionalNamedType("access-selection", SelectiveAccessDescriptor),
    )


# =============================================================================
# Variable-Access-Specification CHOICE
# =============================================================================


class VariableName2(TaggedType[ObjectName]):
    """variable-name [2] IMPLICIT ObjectName"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: ObjectName


class ParameterizedAccess(axdr.SequenceType):
    """Parameterized-Access"""
    components = (
        NamedType("variable-name", ObjectName),
        NamedType("selector", Unsigned8),
        NamedType("parameter", Data),
    )


class ParameterizedAccess4(TaggedType[ParameterizedAccess]):
    """[4] IMPLICIT Parameterized-Access"""
    tag = 4
    mode = TaggingMode.IMPLICIT
    value: ParameterizedAccess


class BlockNumberAccess(axdr.SequenceType):
    """Block-Number-Access"""
    components = (
        NamedType("block-number", Unsigned16),
    )


class BlockNumberAccess5(TaggedType[BlockNumberAccess]):
    """[5] IMPLICIT Block-Number-Access"""
    tag = 5
    mode = TaggingMode.IMPLICIT
    value: BlockNumberAccess


class ReadDataBlockAccess(axdr.SequenceType):
    """Read-Data-Block-Access"""
    components = (
        NamedType("last-block", axdr.BooleanType),
        NamedType("block-number", Unsigned16),
        NamedType("raw-data", axdr.OctetStringType),
    )


class ReadDataBlockAccess6(TaggedType[ReadDataBlockAccess]):
    """[6] IMPLICIT Read-Data-Block-Access"""
    tag = 6
    mode = TaggingMode.IMPLICIT
    value: ReadDataBlockAccess


class WriteDataBlockAccess(axdr.SequenceType):
    """Write-Data-Block-Access"""
    components = (
        NamedType("last-block", axdr.BooleanType),
        NamedType("block-number", Unsigned16),
    )


class WriteDataBlockAccess7(TaggedType[WriteDataBlockAccess]):
    """[7] IMPLICIT Write-Data-Block-Access"""
    tag = 7
    mode = TaggingMode.IMPLICIT
    value: WriteDataBlockAccess


class VariableAccessSpecification(axdr.ChoiceType):
    """Variable-Access-Specification"""
    alternatives = {
        2: NamedType("variable-name", VariableName2),
        4: NamedType("parameterized-access", ParameterizedAccess4),
        5: NamedType("block-number-access", BlockNumberAccess5),
        6: NamedType("read-data-block-access", ReadDataBlockAccess6),
        7: NamedType("write-data-block-access", WriteDataBlockAccess7),
    }

    # Convenience constructors
    @classmethod
    def variable_name(cls, object_name: INTEGER) -> Self:
        return cls(VariableName2(ObjectName(IntegerType(object_name))))

    @classmethod
    def parameterized_access(
        cls,
        variable_name: Unsigned16,
        selector: Unsigned8,
        parameter: Data
    ) -> Self:
        return cls(ParameterizedAccess4(ParameterizedAccess((
            variable_name, selector, parameter
        ))))

    @classmethod
    def block_number(cls, block_number: Unsigned16) -> Self:
        return cls(BlockNumberAccess5(BlockNumberAccess((block_number,))))

    @classmethod
    def read_data_block(
        cls,
        last_block: BOOLEAN,
        block_number: INTEGER,
        raw_data: OCTET_STRING
    ) -> Self:
        return cls(ReadDataBlockAccess6(ReadDataBlockAccess((
            axdr.BooleanType(last_block),
            Unsigned16(IntegerType(block_number)),
            axdr.OctetStringType(raw_data)
        ))))

    @classmethod
    def from_write_data_block(
        cls,
        last_block: BOOLEAN,
        block_number: INTEGER
    ) -> Self:
        return cls(WriteDataBlockAccess7(WriteDataBlockAccess((
            axdr.BooleanType(last_block),
            Unsigned16(IntegerType(block_number))
        ))))


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
        return cls(IntegerType(value & 0xFF))

    @property
    def invoke_id(self) -> int:
        """Extract invoke-id (bits 0-3)"""
        return (self.value.value >> 4) & 0x0F

    def is_confirmed(self) -> bool:
        """Check service-class bit (bit 6)"""
        return bool((self.value.value >> 1) & 0x01)

    def is_high_priority(self) -> bool:
        """Check priority bit (bit 7)"""
        return bool(self.value.value & 0x01)


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
        return cls(IntegerType(value & 0xFFFFFFFF))

    @property
    def long_invoke_id(self) -> int:
        """Extract long-invoke-id (bits 0-23)"""
        return (self.value.value >> 8) & 0xFFFFFF

    def is_self_descriptive(self) -> bool:
        """Check self-descriptive bit (bit 28)"""
        return bool((self.value.value >> 3) & 0x01)

    def is_break_on_error(self) -> bool:
        """Check processing-option bit (bit 29)"""
        return bool((self.value.value >> 2) & 0x01)

    def is_confirmed(self) -> bool:
        """Check service-class bit (bit 30)"""
        return bool((self.value.value >> 1) & 0x01)

    def is_high_priority(self) -> bool:
        """Check priority bit (bit 31)"""
        return bool(self.value.value & 0x01)


# =============================================================================
# Get-Data-Result CHOICE
# =============================================================================


class Data0(TaggedType[Data]):
    """[0] Data"""
    tag = 0
    mode = TaggingMode.DEFAULT
    value: Data


class DataAccesResult1(TaggedType[DataAccessResult1]):
    """[1] IMPLICIT Data-Access-Result"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: DataAccessResult1


class GetDataResult(axdr.ChoiceType):
    """Get-Data-Result"""
    alternatives = {
        0: NamedType("data", Data0),
        1: NamedType("data-access-result", DataAccesResult1)
    }

    @classmethod
    def data(cls, data: Data) -> Self:
        return cls(Data0(data))

    @classmethod
    def data_access_result(cls, result: DataAccessResult1) -> Self:
        return cls(DataAccesResult1(result))


# =============================================================================
# Data Block Types
# =============================================================================


class DataBlockResult(axdr.SequenceType):
    """Data-Block-Result"""
    components = (
        NamedType("last-block", axdr.BooleanType),
        NamedType("block-number", Unsigned16),
        NamedType("raw-data", axdr.OctetStringType),
    )


class RawData(TaggedType[axdr.OctetStringType]):
    """[0] IMPLICIT OCTET STRING"""
    tag = 0
    mode = TaggingMode.IMPLICIT
    value: axdr.OctetStringType


class DataBlockGResult(axdr.ChoiceType):
    """
    DataBlock-G result CHOICE:
    {
        raw-data                       [0] IMPLICIT OCTET STRING,
        data-access-result             [1] IMPLICIT Data-Access-Result
    }
    """
    alternatives = axdr.create_alternatives(
        NamedType("raw-data", RawData),
        NamedType("data-access-result", DataAccessResult1),
    )


class DataBlockG(axdr.SequenceType):
    """DataBlock-G"""
    components = (
        NamedType("last-block", axdr.BooleanType),
        NamedType("block-number", Unsigned32),
        NamedType("result", DataBlockGResult),
    )


class DataBlockSA(axdr.SequenceType):
    """DataBlock-SA"""
    components = (
        NamedType("last-block", axdr.BooleanType),
        NamedType("block-number", Unsigned32),
        NamedType("raw-data", axdr.OctetStringType),
    )


# =============================================================================
# Action Response Types
# =============================================================================


class ActionResponseWithOptionalData(axdr.SequenceType):
    """Action-Response-With-Optional-Data"""
    components = (
        NamedType("result", ActionResult),
        NamedType("return-parameters", GetDataResult),
    )


# =============================================================================
# Notification Types
# =============================================================================


class NotificationBody(axdr.SequenceType):
    """Notification-Body"""
    components = (
        NamedType("data-value", Data),
    )


# =============================================================================
# List Types (SEQUENCE OF)
# =============================================================================


class ListOfData(SequenceOfType[Data]):
    """List-Of-Data"""
    component_type = Data


# =============================================================================
# Access Request Types
# =============================================================================


class AccessRequestGet(axdr.SequenceType):
    """Access-Request-Get"""
    components = (
        NamedType("cosem-attribute-descriptor", CosemAttributeDescriptor),
    )


class AccessRequestGet1(TaggedType[AccessRequestGet]):
    """[1] Access-Request-Get"""
    tag = 1
    mode = TaggingMode.DEFAULT
    value: AccessRequestGet


class AccessRequestGetWithSelection(axdr.SequenceType):
    """Access-Request-Get-With-Selection"""
    components = (
        NamedType("cosem-attribute-descriptor", CosemAttributeDescriptor),
        NamedType("access-selection", SelectiveAccessDescriptor),
    )


class AccessRequestGetWithSelection4(TaggedType[AccessRequestGetWithSelection]):
    """[4] Access-Request-Get-With-Selection"""
    tag = 4
    mode = TaggingMode.DEFAULT
    value: AccessRequestGetWithSelection


class AccessRequestSet(axdr.SequenceType):
    """Access-Request-Set"""
    components = (
        NamedType("cosem-attribute-descriptor", CosemAttributeDescriptor),
    )


class AccessRequestSet2(TaggedType[AccessRequestSet]):
    """[2] Access-Request-Set"""
    tag = 2
    mode = TaggingMode.DEFAULT
    value: AccessRequestSet


class AccessRequestSetWithSelection(axdr.SequenceType):
    """Access-Request-Set-With-Selection"""
    components = (
        NamedType("cosem-attribute-descriptor", CosemAttributeDescriptor),
        NamedType("access-selection", SelectiveAccessDescriptor),
    )


class AccessRequestSetWithSelection5(TaggedType[AccessRequestSetWithSelection]):
    """[5] Access-Request-Set-With-Selection"""
    tag = 5
    mode = TaggingMode.DEFAULT
    value: AccessRequestSetWithSelection


class AccessRequestAction(axdr.SequenceType):
    """Access-Request-Action"""
    components = (
        NamedType("cosem-method-descriptor", CosemMethodDescriptor),
    )


class AccessRequestAction3(TaggedType[AccessRequestAction]):
    """[3] Access-Request-Action"""
    tag = 3
    mode = TaggingMode.DEFAULT
    value: AccessRequestAction


class AccessRequestSpecification(axdr.ChoiceType):
    """Access-Request-Specification"""
    alternatives = {
        1: NamedType("access-request-get", AccessRequestGet1),
        2: NamedType("access-request-set", AccessRequestSet2),
        3: NamedType("access-request-action", AccessRequestAction3),
        4: NamedType("access-request-get-with-selection", AccessRequestGetWithSelection4),
        5: NamedType("access-request-set-with-selection", AccessRequestSetWithSelection5),
    }


class ListOfAccessRequestSpecification(SequenceOfType[AccessRequestSpecification]):
    """List-Of-Access-Request-Specification"""
    component_type = AccessRequestSpecification


class ListOfAccessRequestSpecification0(TaggedType[ListOfAccessRequestSpecification]):
    tag = 0
    mode = TaggingMode.DEFAULT
    value: ListOfAccessRequestSpecification


class AccessRequestBody(axdr.SequenceType):
    """Access-Request-Body"""
    components = (
        NamedType("access-request-specification", ListOfAccessRequestSpecification),
        NamedType("access-request-list-of-data", ListOfData),
    )


# =============================================================================
# Access Response Types
# =============================================================================


class AccessResponseGet(axdr.SequenceType):
    """Access-Response-Get"""
    components = (
        NamedType("result", DataAccessResult1),
    )


class AccessResponseGet1(TaggedType[AccessResponseGet]):
    """[1] Access-Response-Get"""
    tag = 1
    mode = TaggingMode.DEFAULT
    value: AccessResponseGet


class AccessResponseSet(axdr.SequenceType):
    """Access-Response-Set"""
    components = (
        NamedType("result", DataAccessResult1),
    )


class AccessResponseSet2(axdr.TaggedType[AccessResponseSet]):
    """[2] Access-Response-Set"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: AccessResponseSet


class AccessResponseAction(axdr.SequenceType):
    """Access-Response-Action"""
    components = (
        NamedType("result", ActionResult),
    )


class AccessResponseAction3(TaggedType[AccessResponseAction]):
    """[3] Access-Response-Action"""
    tag = 3
    mode = TaggingMode.IMPLICIT
    value: AccessResponseAction


class AccessResponseSpecification(axdr.ChoiceType):
    """Access-Response-Specification"""
    alternatives = {
        1: NamedType("access-response-get", AccessResponseGet1),
        2: NamedType("access-response-set", AccessResponseSet2),
        3: NamedType("access-response-action", AccessResponseAction3),
    }


class ListOfAccessResponseSpecification(SequenceOfType[AccessResponseSpecification]):
    """List-Of-Access-Response-Specification"""
    component_type = AccessResponseSpecification


class AccessResponseBody(axdr.SequenceType):
    """Access-Response-Body"""
    components = (
        OptionalNamedType("access-request-specification", ListOfAccessRequestSpecification0),
        NamedType("access-response-list-of-data", ListOfData),
        NamedType("access-response-specification", ListOfAccessResponseSpecification),
    )
