from typing import Self, Union, TypeAlias
from . import asn1, a_xdr, ber, x690
from .byte_buffer import ByteBuffer as Buf

_value = a_xdr._value


class Integer8(a_xdr.SizedCoder, asn1.IntegerType):
    """ INTEGER(-127…128) """
    Size = 1
    __slots__ = _value

    @classmethod
    def SIGNED(cls) -> bool:
        return True


class Integer16(a_xdr.SizedCoder, asn1.IntegerType):
    """ INTEGER(-32 768...32 767) """
    Size = 2
    __slots__ = _value

    @classmethod
    def SIGNED(cls) -> bool:
        return True


class Integer32(a_xdr.SizedCoder, asn1.IntegerType):
    """ INTEGER(-2 147 483 648...2 147 483 647) """
    Size = 4
    __slots__ = _value

    @classmethod
    def SIGNED(cls) -> bool:
        return True


class Integer64(a_xdr.SizedCoder, asn1.IntegerType):
    """ INTEGER(-2^63...2^63-1) """
    Size = 8
    __slots__ = _value

    @classmethod
    def SIGNED(cls) -> bool:
        return True


class Unsigned8(a_xdr.SizedCoder, asn1.IntegerType):
    """ INTEGER(0...255) """
    Size = 1
    __slots__ = _value

    @classmethod
    def SIGNED(cls) -> bool:
        return False


class Unsigned16(a_xdr.SizedCoder, asn1.IntegerType):
    """ INTEGER(0...65 535) """
    Size = 2
    __slots__ = _value

    @classmethod
    def SIGNED(cls) -> bool:
        return False


class Unsigned32(a_xdr.SizedCoder, asn1.IntegerType):
    """ INTEGER(0...4 294 967 295) """
    Size = 4
    __slots__ = _value

    @classmethod
    def SIGNED(cls) -> bool:
        return False


class Unsigned64(a_xdr.SizedCoder, asn1.IntegerType):
    """ INTEGER(0...264-1) """
    Size = 8
    __slots__ = _value

    @classmethod
    def SIGNED(cls) -> bool:
        return False


class OctetString4(a_xdr.SizedCoder, asn1.OctetStringType):
    Size = 4
    __slots__ = _value


class OctetString5(a_xdr.SizedCoder, asn1.OctetStringType):
    Size = 5
    __slots__ = _value


class OctetString6(a_xdr.SizedCoder, asn1.OctetStringType):
    Size = 6
    __slots__ = _value


class OctetString8(a_xdr.SizedCoder, asn1.OctetStringType):
    Size = 8
    __slots__ = _value


class OctetString12(a_xdr.SizedCoder, asn1.OctetStringType):
    Size = 12
    __slots__ = _value


class NullData(a_xdr.Implicit, asn1.NamedType, a_xdr.NullType):
    Tag = a_xdr.Tag(0)

    @classmethod
    def default(cls) -> Self:
        return NULL_DATA


NULL_DATA = NullData(b'')


class Boolean(a_xdr.Implicit, asn1.NamedType, a_xdr.BooleanType):
    Tag = a_xdr.Tag(3)
    __slots__ = _value


class BitString(a_xdr.Implicit, asn1.NamedType, a_xdr.BitStringType):
    Tag = a_xdr.Tag(4)
    __slots__ = _value


class DoubleLong(a_xdr.Implicit, asn1.NamedType, Integer32):
    Tag = a_xdr.Tag(5)
    __slots__ = _value


class DoubleLongUnsigned(a_xdr.Implicit, asn1.NamedType, Unsigned32):
    Tag = a_xdr.Tag(6)
    __slots__ = _value


class OctetString(a_xdr.Implicit, asn1.NamedType, a_xdr.OctetStringType):
    Tag = a_xdr.Tag(9)
    __slots__ = _value


class Visiblestring(a_xdr.Implicit, asn1.NamedType, a_xdr.OctetStringType):
    Tag = a_xdr.Tag(10)
    __slots__ = _value


class UTF8string(a_xdr.Implicit, asn1.NamedType, a_xdr.UTF8String):
    Tag = a_xdr.Tag(12)


class BCD(a_xdr.Implicit, asn1.NamedType, Integer8):
    Tag = a_xdr.Tag(13)


class Integer(a_xdr.Implicit, asn1.NamedType, Integer8):
    Tag = a_xdr.Tag(15)


class Long(a_xdr.Implicit, asn1.NamedType, Integer16):
    Tag = a_xdr.Tag(16)


class Unsigned(a_xdr.Implicit, asn1.NamedType, Unsigned8):
    Tag = a_xdr.Tag(17)


class LongUnsigned(a_xdr.Implicit, asn1.NamedType, Unsigned16):
    Tag = a_xdr.Tag(18)


class Long64(a_xdr.Implicit, asn1.NamedType, Integer64):
    Tag = a_xdr.Tag(20)


class Long64Unsigned(a_xdr.Implicit, asn1.NamedType, Unsigned64):
    Tag = a_xdr.Tag(21)


class Enum(a_xdr.Implicit, asn1.NamedType, Unsigned8):
    Tag = a_xdr.Tag(22)


class Float32(a_xdr.Implicit, asn1.NamedType, OctetString4):
    Tag = a_xdr.Tag(23)


class Float64(a_xdr.Implicit, asn1.NamedType, OctetString8):
    Tag = a_xdr.Tag(24)


class DateTime(a_xdr.Implicit, asn1.NamedType, OctetString12):
    Tag = a_xdr.Tag(25)


class Date(a_xdr.Implicit, asn1.NamedType, OctetString5):
    Tag = a_xdr.Tag(26)


class Time(a_xdr.Implicit, asn1.NamedType, OctetString4):
    Tag = a_xdr.Tag(27)


class DontCare(a_xdr.Implicit, asn1.NamedType, a_xdr.NullType):
    Tag = a_xdr.Tag(255)


class Data(a_xdr.Choice):
    """Data"""
    def __init__(self, value):
        """reinit after for typing value"""


class SequenceOfData(a_xdr.SequenceOfType):
    Type = Data

    def __init__(self, value):
        """reinit after for typing value"""


class Array(a_xdr.Implicit, SequenceOfData):
    Tag = a_xdr.Tag(1)


def get_array_of(t: type[asn1.Type]) -> type[Array]:
    class ArrayOf(Array):
        Type = t

    return ArrayOf


class AnnotationSequenceOfData(asn1.AnnotationGetterMixin, SequenceOfData):
    @classmethod
    def get(cls, buf: Buf) -> Self:
        if (length := len(cls.__annotations__)) == 0:
            return super().get(buf)
        elif length != (l := x690.Length.get(buf).value):
            raise ValueError(F"got {cls.__name__} length={l}, expected {len(cls.__annotations__)}")
        else:
            ret = list()
            for el in cls.__annotations__.values():
                # el: CDT
                ret.append(el.get(buf))
            return cls(tuple(ret))


class Structure(a_xdr.Implicit, AnnotationSequenceOfData):
    Tag = a_xdr.Tag(2)


CDT: TypeAlias = Union[
    NullData,
    Array,
    Structure,
    Boolean,
    BitString,
    DoubleLong,
    DoubleLongUnsigned,
    OctetString,
    Visiblestring,
    UTF8string,
    BCD,
    Integer,
    Long,
    Unsigned,
    LongUnsigned,
    # compact-array                      [19]  IMPLICIT   SEQUENCE
    #     {
    #         contents-description                [0]              TypeDescription,
    #         array-contents                      [1]   IMPLICIT   OCTET STRING
    #     },
    Long64,
    Long64Unsigned,
    Enum,
    Float32,
    Float64,
    DateTime,
    Date,
    Time,
    DontCare]


def reinit_Data(self, value: CDT):
    self.value = value


def reinit_SequenceOfData(self, value: tuple[CDT, ...]):
    self.value = value


setattr(Data, "__init__", reinit_Data)
setattr(SequenceOfData, "__init__", reinit_Data)


class ProposedQualityOfService(a_xdr.Implicit, Integer8):
    Tag = a_xdr.Tag(0)


class OptionalProposedQualityOfService(a_xdr.Optional, ProposedQualityOfService):
    __slots__ = _value


# todo: wrong realization
class Conformance(ber.BitStringType, asn1.IMPLICIT):
    __slots__ = _value
    Tag = x690.Tag(31, asn1.Class.APPLICATION)
    # {
    #     -- the bit is set when the corresponding service or functionality is available
    #     reserved-zero                      (0),
    #     -- The actual list of general protection services depends on the security suite
    #     general-protection                 (1),
    #     general-block-transfer             (2),
    #     read                               (3),
    #     write                              (4),
    #     unconfirmed-write                  (5),
    #     reserved-six                       (6),
    #     reserved-seven                     (7),
    #     attribute0-supported-with-set      (8),
    #     priority-mgmt-supported            (9),
    #     attribute0-supported-with-get      (10),
    #     block-transfer-with-get-or-read    (11),
    #     block-transfer-with-set-or-write   (12),
    #     block-transfer-with-action         (13),
    #     multiple-references                (14),
    #     information-report                 (15),
    #     data-notification                  (16),
    #     access                             (17),
    #     parameterized-access               (18),
    #     get                                (19),
    #     set                                (20),
    #     selective-access                   (21),
    #     event-notification                 (22),
    #     action                             (23)
    # }


class ObjectName(Integer16):
    """ObjectName COSEMpdu"""


class InitiateRequest(a_xdr.SequenceType):
    __slots__ = _value
    dedicated_key:                a_xdr.OptionalOctetStringType
    response_allowed:             a_xdr.BooleanType   # todo: make BOOLEAN DEFAULT TRUE,
    proposed_quality_of_service:  OptionalProposedQualityOfService   # [0] asn1.IMPLICIT Integer8 OPTIONAL,
    proposed_dlms_version_number: Unsigned8
    proposed_conformance:         Conformance  # -- Shall be encoded in BER
    client_max_receive_pdu_size:  Unsigned16

    def __init__(self, value: tuple[a_xdr.OptionalOctetStringType, a_xdr.BooleanType, OptionalProposedQualityOfService, Unsigned8, Conformance, Unsigned16]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      dedicated_key:                a_xdr.OptionalOctetStringType,
                      response_allowed:             a_xdr.BooleanType,
                      proposed_quality_of_service:  OptionalProposedQualityOfService,
                      proposed_dlms_version_number: Unsigned8,
                      proposed_conformance:         Conformance,
                      client_max_receive_pdu_size:  Unsigned16):
        return cls((dedicated_key, response_allowed, proposed_quality_of_service, proposed_dlms_version_number, proposed_conformance, client_max_receive_pdu_size))


class initiateRequest(a_xdr.Implicit, asn1.NamedType, InitiateRequest):
    Tag = a_xdr.Tag(1)
    __annotations__ = InitiateRequest.__annotations__


class variableName(a_xdr.Implicit, asn1.NamedType, ObjectName):
    Tag = a_xdr.Tag(2)
    __annotations__ = ObjectName.__annotations__


class ParameterizedAccess(a_xdr.SequenceType):
    """Parameterized-Access"""
    __slots__ = _value
    variable_name: ObjectName
    selector:      Unsigned8
    parameter:     Data

    def __init__(self, value: tuple[ObjectName, Unsigned8, Data]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      variable_name: ObjectName,
                      selector:      Unsigned8,
                      parameter:     Data):
        return cls((variable_name, selector, parameter))


class parameterizedAccess(a_xdr.Implicit, asn1.NamedType, ParameterizedAccess):
    Tag = a_xdr.Tag(4)
    __annotations__ = ParameterizedAccess.__annotations__


class BlockNumberAccess(a_xdr.SequenceType):
    """Block-Number-Access"""
    __slots__ = _value
    block_number: Unsigned16

    def __init__(self, value: tuple[Unsigned16]):
        super().__init__(value)

    @classmethod
    def from_elements(cls, block_number: Unsigned16):
        return cls((block_number,))


class blockNumberAccess(a_xdr.Implicit, asn1.NamedType, BlockNumberAccess):
    Tag = a_xdr.Tag(5)
    __annotations__ = BlockNumberAccess.__annotations__


class ReadDataBlockAccess(a_xdr.SequenceType):
    """Read-Data-Block-Access"""
    last_block:   a_xdr.BooleanType
    block_number: Unsigned16
    raw_data:     a_xdr.OctetStringType

    def __init__(self, value: tuple[a_xdr.BooleanType, Unsigned16, a_xdr.OctetStringType]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      last_block: a_xdr.BooleanType,
                      block_number: Unsigned16,
                      raw_data: a_xdr.OctetStringType):
        return cls((last_block, block_number, raw_data))


class readDataBlockAccess(a_xdr.Implicit, asn1.NamedType, ReadDataBlockAccess):
    Tag = a_xdr.Tag(6)
    __annotations__ = ReadDataBlockAccess.__annotations__


class WriteDataBlockAccess(a_xdr.SequenceType):
    """Write-Data-Block-Access"""
    last_block:   a_xdr.BooleanType
    block_number: Unsigned16

    def __init__(self, value: tuple[a_xdr.BooleanType, Unsigned16]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      last_block:   a_xdr.BooleanType,
                      block_number: Unsigned16):
        return cls((last_block, block_number))


class writeDataBlockAccess(a_xdr.Implicit, asn1.NamedType, WriteDataBlockAccess):
    Tag = a_xdr.Tag(7)
    __annotations__ = WriteDataBlockAccess.__annotations__


VariableAccessSpecification_t: TypeAlias = Union[
    variableName,
    # -- detailed-access[3] is not used in DLMS / COSEM
    parameterizedAccess,
    blockNumberAccess,
    readDataBlockAccess]


class VariableAccessSpecification(a_xdr.Choice):
    """Variable-Access-Specification"""

    def __init__(self, value: VariableAccessSpecification_t):
        super().__init__(value)


class ReadRequest(a_xdr.SequenceOfType):
    Type = VariableAccessSpecification

    def __init__(self, value: tuple[VariableAccessSpecification, ...]):
        super().__init__(value)


class readRequest(a_xdr.Implicit, asn1.NamedType, ReadRequest):
    Tag = a_xdr.Tag(5)
    __annotations__ = InitiateRequest.__annotations__


class NegotiatedQualityOfService(a_xdr.Implicit, Integer8):
    Tag = a_xdr.Tag(0)


class OptionalNegotiatedQualityOfService(a_xdr.Optional, NegotiatedQualityOfService):
    __slots__ = _value


class InitiateResponse(a_xdr.SequenceType):
    __slots__ = _value
    negotiated_quality_of_service:     OptionalNegotiatedQualityOfService  # [0] IMPLICIT Integer8 OPTIONAL,
    negotiated_dlms_version_number:    Unsigned8
    negotiated_conformance:            Conformance
    server_max_receive_pdu_size:       Unsigned16
    vaa_name:                          ObjectName

    def __init__(self, value: tuple[OptionalNegotiatedQualityOfService, Unsigned8, Conformance, Unsigned16, ObjectName]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      negotiated_quality_of_service:     OptionalNegotiatedQualityOfService,
                      negotiated_dlms_version_number:    Unsigned8,
                      negotiated_conformance:            Conformance,
                      server_max_receive_pdu_size:       Unsigned16,
                      vaa_name:                          ObjectName):
        return cls((negotiated_quality_of_service, negotiated_dlms_version_number, negotiated_conformance, server_max_receive_pdu_size, vaa_name))


class initiateResponse(a_xdr.Implicit, asn1.NamedType, InitiateResponse):
    Tag = a_xdr.Tag(8)
    __annotations__ = InitiateResponse.__annotations__


class InvokeIdAndPriority(Unsigned8):
    """Invoke-Id-And-Priority"""


class LongInvokeIdAndPriority(Unsigned32):
    """Long-Invoke-Id-And-Priority"""


class CosemClassId(Unsigned16):
    """Cosem-Class-Id"""


class CosemObjectInstanceId(OctetString6):
    """Cosem-Object-Instance-Id"""


class CosemObjectMethodId(Integer8):
    """Cosem-Object-Method-Id"""


class CosemObjectAttributeId(Integer8):
    """Cosem-Object-Attribute-Id"""


class CosemAttributeDescriptor(a_xdr.SequenceType):
    """Cosem-Attribute-Descriptor"""
    __slots__ = _value
    class_id:     CosemClassId
    instance_id:  CosemObjectInstanceId
    attribute_id: CosemObjectAttributeId

    def __init__(self, value: tuple[CosemClassId, CosemObjectInstanceId, CosemObjectAttributeId]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      class_id: CosemClassId,
                      instance_id: CosemObjectInstanceId,
                      attribute_id: CosemObjectAttributeId):
        return cls((class_id, instance_id, attribute_id))


class CosemMethodDescriptor(a_xdr.SequenceType):
    """Cosem-Method-Descriptor"""
    __slots__ = _value
    class_id:    CosemClassId
    instance_id: CosemObjectInstanceId
    method_id:   CosemObjectMethodId

    def __init__(self, value: tuple[CosemClassId, CosemObjectInstanceId, CosemObjectMethodId]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      class_id: CosemClassId,
                      instance_id: CosemObjectInstanceId,
                      method_id: CosemObjectMethodId):
        return cls((class_id, instance_id, method_id))


class SelectiveAccessDescriptor(a_xdr.SequenceType):
    """Selective-Access-Descriptor"""
    __slots__ = _value
    access_selector:   Unsigned8
    access_parameters: Data

    def __init__(self, value: tuple[Unsigned8, Data]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      access_selector: Unsigned8,
                      access_parameters: Data):
        return cls((access_selector, access_parameters))


class SelectiveAccessDescriptorOptional(a_xdr.Optional, SelectiveAccessDescriptor):
    __annotations__ = SelectiveAccessDescriptor.__annotations__
    __slots__ = _value


class CosemAttributeDescriptorWithList(a_xdr.SequenceType):
    """Cosem-Attribute-Descriptor"""
    __slots__ = _value
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection:           SelectiveAccessDescriptorOptional

    def __init__(self, value: tuple[CosemAttributeDescriptor, SelectiveAccessDescriptorOptional]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      cosem_attribute_descriptor: CosemAttributeDescriptor,
                      access_selection: SelectiveAccessDescriptorOptional):
        return cls((cosem_attribute_descriptor, access_selection))


class GetRequestNormal(a_xdr.SequenceType):
    __slots__ = _value
    invoke_id_and_priority:     InvokeIdAndPriority
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection:           SelectiveAccessDescriptorOptional

    def __init__(self, value: tuple[InvokeIdAndPriority, CosemAttributeDescriptor, SelectiveAccessDescriptorOptional]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      cosem_attribute_descriptor: CosemAttributeDescriptor,
                      access_selection: SelectiveAccessDescriptorOptional):
        return cls((invoke_id_and_priority, cosem_attribute_descriptor, access_selection))


class getRequestNormal(a_xdr.Implicit, asn1.NamedType, GetRequestNormal):
    Tag = a_xdr.Tag(1)
    __annotations__ = GetRequestNormal.__annotations__


class GetRequestNext(a_xdr.SequenceType):
    __slots__ = _value
    invoke_id_and_priority:     InvokeIdAndPriority
    block_number:               Unsigned32

    def __init__(self, value: tuple[InvokeIdAndPriority, Unsigned32]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      block_number: Unsigned32):
        return cls((invoke_id_and_priority, block_number))


class getRequestNext(a_xdr.Implicit, asn1.NamedType, GetRequestNext):
    Tag = a_xdr.Tag(2)
    __annotations__ = GetRequestNext.__annotations__


class SequenceOfCosemAttributeDescriptorWithList(a_xdr.SequenceOfType):
    Type = CosemAttributeDescriptorWithList

    def __init__(self, value: tuple[CosemAttributeDescriptorWithList, ...]):
        super().__init__(value)


class GetRequestWithList(a_xdr.SequenceType):
    __slots__ = _value
    invoke_id_and_priority:     InvokeIdAndPriority
    attribute_descriptor_list:  SequenceOfCosemAttributeDescriptorWithList

    def __init__(self, value: tuple[InvokeIdAndPriority, SequenceOfCosemAttributeDescriptorWithList]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      attribute_descriptor_list: SequenceOfCosemAttributeDescriptorWithList):
        return cls((invoke_id_and_priority, attribute_descriptor_list))


class getRequestWithList(a_xdr.Implicit, asn1.NamedType, GetRequestWithList):
    Tag = a_xdr.Tag(3)
    __annotations__ = GetRequestWithList.__annotations__


class GetRequest(a_xdr.Choice):
    """Get-Request"""
    def __init__(self, value: Union[
        getRequestNormal,
        getRequestNext,
        getRequestWithList]
    ):
        super().__init__(value)


class getRequest(a_xdr.Implicit, asn1.NamedType, GetRequest):
    Tag = a_xdr.Tag(192)


class data(a_xdr.Implicit, asn1.NamedType, Data):
    Tag = a_xdr.Tag(0)
    __annotations__ = GetRequestNext.__annotations__


class DataAccessResult(a_xdr.EnumeratedType):
    """Data-Access-Result"""
    ENUMERATIONS = (
        asn1.NamedNumber("success", 0),
        asn1.NamedNumber("hardware-fault", 1),
        asn1.NamedNumber("temporary-failure", 2),
        asn1.NamedNumber("read-write-denied", 3),
        asn1.NamedNumber("object-undefined", 4),
        asn1.NamedNumber("object-class-inconsistent", 9),
        asn1.NamedNumber("object-unavailable", 11),
        asn1.NamedNumber("type-unmatched", 12),
        asn1.NamedNumber("scope-of-access-violated", 13),
        asn1.NamedNumber("data-block-unavailable", 14),
        asn1.NamedNumber("long-get-aborted", 15),
        asn1.NamedNumber("no-long-get-in-progress", 16),
        asn1.NamedNumber("long-set-aborted", 17),
        asn1.NamedNumber("no-long-set-in-progress", 18),
        asn1.NamedNumber("data-block-number-invalid", 19),
        asn1.NamedNumber("other-reason", 250),
    )


class GetDataResult(a_xdr.Choice):
    """Get-Data-Result"""
    def __init__(self, value: Union[
        data,
        DataAccessResult]
    ):
        super().__init__(value)


class GetResponseNormal(a_xdr.SequenceType):
    __slots__ = _value
    invoke_id_and_priority:     InvokeIdAndPriority
    result:                     GetDataResult

    def __init__(self, value: tuple[InvokeIdAndPriority, GetDataResult]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      result:                 GetDataResult):
        return cls((invoke_id_and_priority, result))


class getResponseNormal(a_xdr.Implicit, asn1.NamedType, GetResponseNormal):
    Tag = a_xdr.Tag(1)
    __annotations__ = GetResponseNormal.__annotations__


class RawData(a_xdr.Implicit, asn1.NamedType, a_xdr.OctetStringType):
    Tag = a_xdr.Tag(0)


class DataAccessResult_IMP(a_xdr.Implicit, asn1.NamedType, DataAccessResult):
    Tag = a_xdr.Tag(1)


class Result(a_xdr.Choice):
    """result of DataBlock-G"""
    def __init__(self, value: Union[
        RawData,
        DataAccessResult_IMP]
    ):
        super().__init__(value)


class DataBlockG(a_xdr.SequenceType):
    __slots__ = _value
    last_block:   a_xdr.BooleanType
    block_number: Unsigned32
    result:       Result


class GetResponseWithDatablock(a_xdr.SequenceType):
    __slots__ = _value
    invoke_id_and_priority: InvokeIdAndPriority
    result:                 GetDataResult

    def __init__(self, value: tuple[InvokeIdAndPriority, GetDataResult]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      result: GetDataResult):
        return cls((invoke_id_and_priority, result))


class getResponseWithDatablock(a_xdr.Implicit, asn1.NamedType, GetResponseWithDatablock):
    Tag = a_xdr.Tag(2)
    __annotations__ = GetResponseWithDatablock.__annotations__


class SequenceOfGetDataResult(a_xdr.SequenceOfType):
    Type = GetDataResult

    def __init__(self, value: tuple[GetDataResult, ...]):
        super().__init__(value)


class GetResponseWithList(a_xdr.SequenceType):
    invoke_id_and_priority: InvokeIdAndPriority
    result: SequenceOfGetDataResult

    def __init__(self, value: tuple[InvokeIdAndPriority, SequenceOfGetDataResult]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      result: SequenceOfGetDataResult):
        return cls((invoke_id_and_priority, result))


class getResponseWithList(a_xdr.Implicit, asn1.NamedType, GetResponseWithList):
    Tag = a_xdr.Tag(3)
    __annotations__ = GetResponseWithList.__annotations__


class GetResponse(a_xdr.Choice):
    """ Get-Request"""
    def __init__(self, value: Union[
        getResponseNormal,
        getResponseWithDatablock,
        getResponseWithList]
    ):
        super().__init__(value)


class ApplicationReference(a_xdr.Implicit, asn1.NamedType, a_xdr.EnumeratedType):
    """application-reference"""
    Tag = a_xdr.Tag(0)
    ENUMERATIONS = (
        asn1.NamedNumber("other", 0),
        asn1.NamedNumber("time-elapsed", 1),
        asn1.NamedNumber("application-unreachable", 2),
        asn1.NamedNumber("application-reference-invalid", 3),
        asn1.NamedNumber("application-context-unsupported", 4),
        asn1.NamedNumber("provider-communication-error", 5),
        asn1.NamedNumber("deciphering-error", 6)
    )


class HardwareResource(a_xdr.Implicit, asn1.NamedType, a_xdr.EnumeratedType):
    """hardware-resource"""
    Tag = a_xdr.Tag(1)
    ENUMERATIONS = (
        asn1.NamedNumber("other", 0),
        asn1.NamedNumber("memory-unavailable", 1),
        asn1.NamedNumber("processor-resource-unavailable", 2),
        asn1.NamedNumber("mass-storage-unavailable", 3),
        asn1.NamedNumber("other-resource-unavailable", 4),
    )


class VdeStateError(a_xdr.Implicit, asn1.NamedType, a_xdr.EnumeratedType):
    """vde-state-error"""
    Tag = a_xdr.Tag(2)
    ENUMERATIONS = (
        asn1.NamedNumber("other", 0),
        asn1.NamedNumber("no-dlms-context", 1),
        asn1.NamedNumber("loading-data-set", 2),
        asn1.NamedNumber("status-nochange", 3),
        asn1.NamedNumber("status-inoperable", 4),
    )


class Service(a_xdr.Implicit, asn1.NamedType, a_xdr.EnumeratedType):
    """service"""
    Tag = a_xdr.Tag(3)
    ENUMERATIONS = (
        asn1.NamedNumber("other", 0),
        asn1.NamedNumber("pdu-size", 1),
        asn1.NamedNumber("service-unsupported", 2),
    )


class Definition(a_xdr.Implicit, asn1.NamedType, a_xdr.EnumeratedType):
    """definition"""
    Tag = a_xdr.Tag(4)
    ENUMERATIONS = (
        asn1.NamedNumber("other", 0),
        asn1.NamedNumber("object-undefined", 1),
        asn1.NamedNumber("object-class-inconsistent", 2),
        asn1.NamedNumber("object-attribute-inconsistent", 3),
    )


class Access(a_xdr.Implicit, asn1.NamedType, a_xdr.EnumeratedType):
    """access"""
    Tag = a_xdr.Tag(5)
    ENUMERATIONS = (
        asn1.NamedNumber("other", 0),
        asn1.NamedNumber("scope-of-access-violated", 1),
        asn1.NamedNumber("object-access-violated", 2),
        asn1.NamedNumber("hardware-fault", 3),
        asn1.NamedNumber("object-unavailable", 4),
    )


class Initiate(a_xdr.Implicit, asn1.NamedType, a_xdr.EnumeratedType):
    """initiate"""
    Tag = a_xdr.Tag(6)
    ENUMERATIONS = (
        asn1.NamedNumber("other", 0),
        asn1.NamedNumber("dlms-version-too-low", 1),
        asn1.NamedNumber("incompatible-conformance", 2),
        asn1.NamedNumber("pdu-size-too-short", 3),
        asn1.NamedNumber("refused-by-the-VDE-Handler", 4),
    )


class LoadDataSet(a_xdr.Implicit, asn1.NamedType, a_xdr.EnumeratedType):
    """load-data-set"""
    Tag = a_xdr.Tag(7)
    ENUMERATIONS = (
        asn1.NamedNumber("other", 0),
        asn1.NamedNumber("primitive-out-of-sequence", 1),
        asn1.NamedNumber("not-loadable", 2),
        asn1.NamedNumber("dataset-size-too-large", 3),
        asn1.NamedNumber("not-awaited-segment", 4),
        asn1.NamedNumber("interpretation-failure", 5),
        asn1.NamedNumber("storage-failure", 6),
        asn1.NamedNumber("data-set-not-ready", 7),
    )


class ChangeScope(a_xdr.Implicit, asn1.NamedType, a_xdr.EnumeratedType):
    """load-data-set"""
    Tag = a_xdr.Tag(8)
    ENUMERATIONS = tuple()


class Task(a_xdr.Implicit, asn1.NamedType, a_xdr.EnumeratedType):
    """task"""
    Tag = a_xdr.Tag(9)
    ENUMERATIONS = (
        asn1.NamedNumber("other", 0),
        asn1.NamedNumber("no-remote-control", 1),
        asn1.NamedNumber("ti-stopped", 2),
        asn1.NamedNumber("ti-running", 3),
        asn1.NamedNumber("ti-unusable", 4),
    )


class Other(a_xdr.Implicit, asn1.NamedType, a_xdr.EnumeratedType):
    """other"""
    Tag = a_xdr.Tag(10)
    ENUMERATIONS = tuple()


class ServiceError(a_xdr.Choice):
    """ServiceError"""
    def __init__(self, value: Union[
        ApplicationReference,
        HardwareResource,
        VdeStateError,
        Service,
        Definition,
        Access,
        Initiate,
        LoadDataSet,
        ChangeScope,
        Task,
        Other]
    ):
        super().__init__(value)


class InitiateError(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """initiateError"""
    Tag = a_xdr.Tag(1)


class GetStatus(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """getStatus"""
    Tag = a_xdr.Tag(2)


class GetNameList(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """getNameList"""
    Tag = a_xdr.Tag(3)


class GetVariableAttribute(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """getVariableAttribute"""
    Tag = a_xdr.Tag(4)


class Read(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """read"""
    Tag = a_xdr.Tag(5)


class Write(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """write"""
    Tag = a_xdr.Tag(6)


class GetDataSetAttribute(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """getDataSetAttribute"""
    Tag = a_xdr.Tag(7)


class GetTIAttribute(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """getTIAttribute"""
    Tag = a_xdr.Tag(8)


class changeScope(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """changeScope"""
    Tag = a_xdr.Tag(9)


class Start(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """start"""
    Tag = a_xdr.Tag(10)


class Stop(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """stop"""
    Tag = a_xdr.Tag(11)


class Resume(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """resume"""
    Tag = a_xdr.Tag(12)


class MakeUsable(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """makeUsable"""
    Tag = a_xdr.Tag(13)


class InitiateLoad(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """initiateLoad"""
    Tag = a_xdr.Tag(14)


class LoadSegment(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """loadSegment"""
    Tag = a_xdr.Tag(15)


class TerminateLoad(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """terminatedLoad"""
    Tag = a_xdr.Tag(16)


class InitiateUpLoad(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """initiateUpLoad"""
    Tag = a_xdr.Tag(17)


class UpLoadSegment(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """upLoadSegment"""
    Tag = a_xdr.Tag(18)


class TerminateUpLoad(a_xdr.Implicit, asn1.NamedType, ServiceError):
    """terminateUpLoad"""
    Tag = a_xdr.Tag(19)


class ConfirmedServiceError(a_xdr.Choice):
    """ConfirmedServiceError"""
    def __init__(self, value: Union[
        InitiateError,
        GetStatus,
        GetNameList,
        GetVariableAttribute,
        Read,
        Write,
        GetDataSetAttribute,
        GetTIAttribute,
        changeScope,
        Start,
        Stop,
        Resume,
        MakeUsable,
        InitiateLoad,
        LoadSegment,
        TerminateLoad,
        InitiateUpLoad,
        UpLoadSegment,
        TerminateUpLoad]
    ):
        super().__init__(value)


class confirmedServiceError(a_xdr.Implicit, asn1.NamedType, ConfirmedServiceError):
    """confirmedServiceError"""
    Tag = a_xdr.Tag(14)


class getResponse(a_xdr.Implicit, asn1.NamedType, GetResponse):
    Tag = a_xdr.Tag(196)


class ActionResult(a_xdr.EnumeratedType):
    """Action-Result"""
    ENUMERATIONS = (
        asn1.NamedNumber("success", 0),
        asn1.NamedNumber("hardware-fault", 1),
        asn1.NamedNumber("temporary-failure", 2),
        asn1.NamedNumber("read-write-denied", 3),
        asn1.NamedNumber("object-undefined", 4),
        asn1.NamedNumber("object-class-inconsistent", 9),
        asn1.NamedNumber("object-unavailable", 11),
        asn1.NamedNumber("type-unmatched", 12),
        asn1.NamedNumber("scope-of-access-violated", 13),
        asn1.NamedNumber("data-block-unavailable", 14),
        asn1.NamedNumber("long-action-aborted", 15),
        asn1.NamedNumber("no-long-action-in-progress", 16),
        asn1.NamedNumber("other-reason", 250)
    )


class DataOptional(a_xdr.Optional, Data):
    """"""
    def __init__(self, value: Union[CDT, b'']):
        super().__init__(value)


class ActionRequestNormal(a_xdr.SequenceType):
    """Action-Request-Normal"""
    __slots__ = _value
    invoke_id_and_priority:       InvokeIdAndPriority
    cosem_method_descriptor:      CosemMethodDescriptor
    method_invocation_parameters: DataOptional

    def __init__(self, value: tuple[InvokeIdAndPriority, CosemMethodDescriptor, DataOptional]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      cosem_method_descriptor: CosemMethodDescriptor,
                      method_invocation_parameters: DataOptional):
        return cls((invoke_id_and_priority, cosem_method_descriptor, method_invocation_parameters))


class actionRequestNormal(a_xdr.Implicit, asn1.NamedType, ActionRequestNormal):
    Tag = a_xdr.Tag(1)
    __annotations__ = ActionRequestNormal.__annotations__


class ActionRequestNextPblock(a_xdr.SequenceType):
    """Action-Request-Next-Pblock"""
    __slots__ = _value
    invoke_id_and_priority: InvokeIdAndPriority
    block_number:           Unsigned32

    def __init__(self, value: tuple[InvokeIdAndPriority, Unsigned32]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      block_number: Unsigned32):
        return cls((invoke_id_and_priority, block_number))


class actionRequestNextPblock(a_xdr.Implicit, asn1.NamedType, ActionRequestNextPblock):
    Tag = a_xdr.Tag(2)
    __annotations__ = ActionRequestNextPblock.__annotations__


class SequenceOfCosemMethodDescriptor(a_xdr.SequenceOfType):
    Type = CosemMethodDescriptor

    def __init__(self, value: tuple[CosemMethodDescriptor, ...]):
        super().__init__(value)


class ActionRequestWithList(a_xdr.SequenceType):
    """Action-Request-With-List"""
    __slots__ = _value
    invoke_id_and_priority:       InvokeIdAndPriority
    cosem_method_descriptor_list: SequenceOfCosemMethodDescriptor
    method_invocation_parameters: SequenceOfData

    def __init__(self, value: tuple[InvokeIdAndPriority, SequenceOfCosemMethodDescriptor, SequenceOfData]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      cosem_method_descriptor_list: SequenceOfCosemMethodDescriptor,
                      method_invocation_parameters: SequenceOfData):
        return cls((invoke_id_and_priority, cosem_method_descriptor_list, method_invocation_parameters))


class actionRequestWithList(a_xdr.Implicit, asn1.NamedType, ActionRequestWithList):
    Tag = a_xdr.Tag(3)
    __annotations__ = ActionRequestWithList.__annotations__


class DataBlockSA(a_xdr.SequenceType):
    """DataBlock-SA"""
    __slots__ = _value
    last_block:   a_xdr.BooleanType
    block_number: Unsigned32
    raw_data:     a_xdr.OctetStringType

    def __init__(self, value: tuple[a_xdr.BooleanType, Unsigned32, a_xdr.OctetStringType]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      last_block: a_xdr.BooleanType,
                      block_number: Unsigned32,
                      raw_data: a_xdr.OctetStringType):
        return cls((last_block, block_number, raw_data))


class ActionRequestWithFirstPblock(a_xdr.SequenceType):
    """Action-Request-With-First-Pblock"""
    __slots__ = _value
    invoke_id_and_priority:       InvokeIdAndPriority
    cosem_method_descriptor:      CosemMethodDescriptor
    pblock:                       DataBlockSA

    def __init__(self, value: tuple[InvokeIdAndPriority, CosemMethodDescriptor, DataBlockSA]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      cosem_method_descriptor: CosemMethodDescriptor,
                      pblock: DataBlockSA):
        return cls((invoke_id_and_priority, cosem_method_descriptor, pblock))


class actionRequestWithFirstPblock(a_xdr.Implicit, asn1.NamedType, ActionRequestWithFirstPblock):
    Tag = a_xdr.Tag(4)
    __annotations__ = ActionRequestWithFirstPblock.__annotations__


class ActionRequestWithListAndFirstPblock(a_xdr.SequenceType):
    """Action-Request-With-List-And-First-Pblock"""
    __slots__ = _value
    invoke_id_and_priority:       InvokeIdAndPriority
    cosem_method_descriptor_list: SequenceOfCosemMethodDescriptor
    pblock:                       DataBlockSA

    def __init__(self, value: tuple[InvokeIdAndPriority, SequenceOfCosemMethodDescriptor, DataBlockSA]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      cosem_method_descriptor_list: SequenceOfCosemMethodDescriptor,
                      pblock: DataBlockSA):
        return cls((invoke_id_and_priority, cosem_method_descriptor_list, pblock))


class actionRequestWithListAndFirstPblock(a_xdr.Implicit, asn1.NamedType, ActionRequestWithListAndFirstPblock):
    Tag = a_xdr.Tag(5)
    __annotations__ = ActionRequestWithListAndFirstPblock.__annotations__


class ActionRequestWithPblock(a_xdr.SequenceType):
    """Action-Request-With-Pblock"""
    __slots__ = _value
    invoke_id_and_priority:       InvokeIdAndPriority
    pblock:                       DataBlockSA

    def __init__(self, value: tuple[InvokeIdAndPriority, DataBlockSA]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      pblock: DataBlockSA):
        return cls((invoke_id_and_priority, pblock))


class actionRequestWithPblock(a_xdr.Implicit, asn1.NamedType, ActionRequestWithPblock):
    Tag = a_xdr.Tag(6)
    __annotations__ = ActionRequestWithPblock.__annotations__


class ActionRequest(a_xdr.Choice):
    """Action-Request"""
    def __init__(self, value: Union[
        actionRequestNormal,
        actionRequestNextPblock,
        actionRequestWithList,
        actionRequestWithFirstPblock,
        actionRequestWithListAndFirstPblock,
        actionRequestWithPblock]
    ):
        super().__init__(value)


class actionRequest(a_xdr.Implicit, asn1.NamedType, ActionRequest):
    Tag = a_xdr.Tag(195)


class Data_(a_xdr.Implicit, asn1.NamedType, Data):
    Tag = a_xdr.Tag(0)


class DataAccessResult_(a_xdr.Implicit, asn1.NamedType, DataAccessResult):
    Tag = a_xdr.Tag(1)
    __annotations__ = DataAccessResult.__annotations__


class DataBlockResult(a_xdr.SequenceType):
    """Data-Block-Result"""
    __slots__ = _value
    last_block:   a_xdr.BooleanType
    block_number: Unsigned16
    raw_data:     a_xdr.OctetStringType

    def __init__(self, value: tuple[a_xdr.BooleanType, Unsigned16, a_xdr.OctetStringType]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      last_block: a_xdr.BooleanType,
                      block_number: Unsigned16,
                      raw_data: a_xdr.OctetStringType):
        return cls((last_block, block_number, raw_data))


class DataBlockResult_(a_xdr.Implicit, asn1.NamedType, DataBlockResult):
    """Implicit DataBlockResult"""
    Tag = a_xdr.Tag(2)
    __annotations__ = DataBlockResult.__annotations__


class Unsigned16_(a_xdr.Implicit, asn1.NamedType, Unsigned16):
    Tag = a_xdr.Tag(3)


ReadResponseElement_t: TypeAlias = Union[
    Data_,
    DataAccessResult_,
    DataBlockResult_,
    Unsigned16_]


class ReadResponseElement(a_xdr.Choice):
    """Element of ReadResponse"""
    def __init__(self, value: ReadResponseElement_t):
        super().__init__(value)


class ReadResponse(a_xdr.SequenceOfType):
    """ReadResponse"""
    Type = ReadResponseElement

    def __init__(self, value: tuple[ReadResponseElement_t, ...]):
        super().__init__(value)


class ReadResponse_(a_xdr.Implicit, asn1.NamedType, ReadResponse):
    """[12] IMPLICIT ReadResponse"""
    Tag = a_xdr.Tag(12)


class SequenceOfVariableAccessSpecification(a_xdr.SequenceOfType):
    Type = VariableAccessSpecification

    def __init__(self, value: tuple[VariableAccessSpecification_t, ...]):
        super().__init__(value)


class WriteRequest(a_xdr.SequenceType):
    """WriteRequest"""
    __slots__ = _value
    variable_access_specification:  SequenceOfVariableAccessSpecification
    list_of_data:                   SequenceOfData

    def __init__(self, value: tuple[SequenceOfVariableAccessSpecification, SequenceOfData]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      variable_access_specification: SequenceOfVariableAccessSpecification,
                      list_of_data: SequenceOfData):
        return cls((variable_access_specification, list_of_data))


class WriteRequest_(a_xdr.Implicit, asn1.NamedType, WriteRequest):
    """Implicit WriteRequest"""
    __annotations__ = WriteRequest.__annotations__
    Tag = a_xdr.Tag(6)


class Success(a_xdr.Implicit, asn1.NamedType, a_xdr.NullType):
    """Implicit Null"""
    Tag = a_xdr.Tag(0)


class BlockNumber(a_xdr.Implicit, asn1.NamedType, Unsigned16):
    """IMPLICIT Unsigned16"""
    Tag = a_xdr.Tag(2)


class WriteResponseElement(a_xdr.Choice):
    def __init__(self, value: Union[
        Success,
        DataAccessResult_IMP,
        BlockNumber]
    ):
        super().__init__(value)


class WriteResponse(a_xdr.SequenceOfType):
    Type = WriteResponseElement

    def __init__(self, value: tuple[WriteResponseElement, ...]):
        super().__init__(value)


class WriteResponse_IMP(a_xdr.Implicit, asn1.NamedType, WriteResponse):
    """Implicit WriteResponse"""
    Tag = a_xdr.Tag(13)


class SetRequestNormal(a_xdr.SequenceType):
    """Set-Request-Normal"""
    __slots__ = _value
    invoke_id_and_priority:     InvokeIdAndPriority
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection:           SelectiveAccessDescriptorOptional
    value_:                      Data

    def __init__(self, value: tuple[InvokeIdAndPriority, CosemAttributeDescriptor, SelectiveAccessDescriptorOptional, Data]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      cosem_attribute_descriptor: CosemAttributeDescriptor,
                      access_selection: SelectiveAccessDescriptorOptional,
                      value_: Data):
        return cls((invoke_id_and_priority, cosem_attribute_descriptor, access_selection, value_))
    
    
class SelectiveAccessDescriptorOptionalImplicit(a_xdr.Implicit, asn1.NamedType, SelectiveAccessDescriptorOptional):
    Tag = a_xdr.Tag(0)


class SetRequestWithFirstDatablock(a_xdr.SequenceType):
    """Set-Request-With-First-Datablock"""
    __slots__ = _value
    invoke_id_and_priority:     InvokeIdAndPriority
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection:           SelectiveAccessDescriptorOptionalImplicit
    datablock:                  DataBlockSA
    
    def __init__(self, value: tuple[InvokeIdAndPriority, CosemAttributeDescriptor, SelectiveAccessDescriptorOptionalImplicit, DataBlockSA]):
        super().__init__(value)
        
    @classmethod
    def from_elements(cls, 
                      invoke_id_and_priority:     InvokeIdAndPriority,
                      cosem_attribute_descriptor: CosemAttributeDescriptor,
                      access_selection:           SelectiveAccessDescriptorOptionalImplicit,
                      datablock:                  DataBlockSA):
        return cls((invoke_id_and_priority, cosem_attribute_descriptor, access_selection, datablock))
    
    
class SetRequestWithDatablock(a_xdr.SequenceType):
    """Set-Request-With-Datablock"""
    __slots__ = _value
    invoke_id_and_priority: InvokeIdAndPriority
    datablock: DataBlockSA

    def __init__(self, value: tuple[InvokeIdAndPriority, DataBlockSA]):
        super().__init__(value)
    
    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      datablock: DataBlockSA):
        return cls((invoke_id_and_priority, datablock))


class CosemAttributeDescriptorWithSelection(a_xdr.SequenceType):
    """Cosem-Attribute-Descriptor-With-Selection"""
    __slots__ = _value
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection:           SelectiveAccessDescriptorOptional

    def __init__(self, value: tuple[CosemAttributeDescriptor, SelectiveAccessDescriptorOptional]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      cosem_attribute_descriptor: CosemAttributeDescriptor,
                      access_selection:           SelectiveAccessDescriptorOptional):
        return cls((cosem_attribute_descriptor, access_selection))


class SequenceOfCosemAttributeDescriptorWithSelection(a_xdr.SequenceOfType):
    Type = CosemAttributeDescriptorWithSelection

    def __init__(self, value: tuple[CosemAttributeDescriptorWithSelection, ...]):
        super().__init__(value)


class SetRequestWithList(a_xdr.SequenceType):
    """Set-Request-With-List"""
    __slots__ = _value
    invoke_id_and_priority:    InvokeIdAndPriority
    attribute_descriptor_list: SequenceOfCosemAttributeDescriptorWithSelection
    value_list:                SequenceOfData

    def __init__(self, value: tuple[InvokeIdAndPriority, SequenceOfCosemAttributeDescriptorWithSelection, SequenceOfData]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      attribute_descriptor_list: SequenceOfCosemAttributeDescriptorWithSelection,
                      value_list: SequenceOfData):
        return cls((invoke_id_and_priority, attribute_descriptor_list, value_list))


class SetRequestWithListAndFirstDatablock(a_xdr.SequenceType):
    """Set-Request-With-List-And-First-Datablock"""
    __slots__ = _value
    invoke_id_and_priority:    InvokeIdAndPriority
    attribute_descriptor_list: SequenceOfCosemAttributeDescriptorWithSelection
    datablock:                 DataBlockSA

    def __init__(self, value: tuple[InvokeIdAndPriority, SequenceOfCosemAttributeDescriptorWithSelection, DataBlockSA]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      attribute_descriptor_list: SequenceOfCosemAttributeDescriptorWithSelection,
                      datablock:                 DataBlockSA):
        return cls((invoke_id_and_priority, attribute_descriptor_list, datablock))


class setRequestNormal(a_xdr.Implicit, asn1.NamedType, SetRequestNormal):
    """[1] IMPLICIT Set-Request-Normal"""
    Tag = a_xdr.Tag(1)
    __annotations__ = SetRequestNormal.__annotations__


class setRequestWithFirstDatablock(a_xdr.Implicit, asn1.NamedType, SetRequestWithFirstDatablock):
    """[2] IMPLICIT  Set-Request-With-First-Datablock"""
    Tag = a_xdr.Tag(2)
    __annotations__ = SetRequestWithFirstDatablock.__annotations__


class setRequestWithDatablock(a_xdr.Implicit, asn1.NamedType, SetRequestWithDatablock):
    """[3] IMPLICIT  Set-Request-With-Datablock"""
    Tag = a_xdr.Tag(3)
    __annotations__ = SetRequestWithDatablock.__annotations__


class setRequestWithList(a_xdr.Implicit, asn1.NamedType, SetRequestWithList):
    """[4] IMPLICIT  Set-Request-With-List"""
    Tag = a_xdr.Tag(4)
    __annotations__ = SetRequestWithList.__annotations__


class setRequestWithListAndFirstDatablock(a_xdr.Implicit, asn1.NamedType, SetRequestWithListAndFirstDatablock):
    """[5] IMPLICIT  Set-Request-With-List-And-First-Datablock"""
    Tag = a_xdr.Tag(5)
    __annotations__ = SetRequestWithListAndFirstDatablock.__annotations__


class SetRequest(a_xdr.Choice):
    """Set-Request"""
    def __init__(self, value: Union[
        setRequestNormal,
        setRequestWithFirstDatablock,
        setRequestWithDatablock,
        setRequestWithList,
        setRequestWithListAndFirstDatablock
    ]):
        super().__init__(value)


class setRequest(a_xdr.Implicit, asn1.NamedType, SetRequest):
    """[193] IMPLICIT      Set-Request"""
    Tag = a_xdr.Tag(193)


class SetResponseNormal(a_xdr.SequenceType):
    """Set-Response-Normal"""
    __slots__ = _value
    invoke_id_and_priority:    InvokeIdAndPriority
    result:                    DataAccessResult

    def __init__(self, value: tuple[InvokeIdAndPriority, DataAccessResult]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      result: DataAccessResult):
        return cls((invoke_id_and_priority, result))


class SetResponseDatablock(a_xdr.SequenceType):
    """Set-Response-Datablock"""
    __slots__ = _value
    invoke_id_and_priority: InvokeIdAndPriority
    block_number:           Unsigned32

    def __init__(self, value: tuple[InvokeIdAndPriority, Unsigned32]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      block_number:           Unsigned32):
        return cls((invoke_id_and_priority, block_number))


class SetResponseLastDatablock(a_xdr.SequenceType):
    """Set-Response-Last-Datablock"""
    __slots__ = _value
    invoke_id_and_priority: InvokeIdAndPriority
    result: DataAccessResult
    block_number: Unsigned32

    def __init__(self, value: tuple[InvokeIdAndPriority, DataAccessResult, Unsigned32]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      result: DataAccessResult,
                      block_number: Unsigned32):
        return cls((invoke_id_and_priority, result, block_number))


class SequenceOfDataAccessResult(a_xdr.SequenceOfType):
    Type = DataAccessResult

    def __init__(self, value: tuple[DataAccessResult, ...]):
        super().__init__(value)


class SetResponseLastDatablockWithList(a_xdr.SequenceType):
    """Set-Response-Last-Datablock-With-List"""
    __slots__ = _value
    invoke_id_and_priority: InvokeIdAndPriority
    result:                 SequenceOfDataAccessResult
    block_number: Unsigned32

    def __init__(self, value: tuple[InvokeIdAndPriority, SequenceOfDataAccessResult, Unsigned32]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      result: SequenceOfDataAccessResult,
                      block_number: Unsigned32):
        return cls((invoke_id_and_priority, result, block_number))


class SetResponseWithList(a_xdr.SequenceType):
    """Set-Response-With-List"""
    __slots__ = _value
    invoke_id_and_priority: InvokeIdAndPriority
    result:                 SequenceOfDataAccessResult

    def __init__(self, value: tuple[InvokeIdAndPriority, SequenceOfDataAccessResult]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      invoke_id_and_priority: InvokeIdAndPriority,
                      result: SequenceOfDataAccessResult):
        return cls((invoke_id_and_priority, result))


class setResponseNormal(a_xdr.Implicit, asn1.NamedType, SetResponseNormal):
    """[1] IMPLICIT Set-Response-Normal"""
    Tag = a_xdr.Tag(1)
    __annotations__ = SetResponseNormal.__annotations__


class setResponseDatablock(a_xdr.Implicit, asn1.NamedType, SetResponseDatablock):
    """[2] IMPLICIT Set-Response-Datablock"""
    Tag = a_xdr.Tag(2)
    __annotations__ = SetResponseDatablock.__annotations__


class setResponseLastDatablock(a_xdr.Implicit, asn1.NamedType, SetResponseLastDatablock):
    """[3] IMPLICIT   Set-Response-Last-Datablock"""
    Tag = a_xdr.Tag(3)
    __annotations__ = SetResponseLastDatablock.__annotations__


class setResponseLastDatablockWithList(a_xdr.Implicit, asn1.NamedType, SetResponseLastDatablockWithList):
    """[4] IMPLICIT   Set-Response-Last-Datablock-With-List"""
    Tag = a_xdr.Tag(4)
    __annotations__ = SetResponseLastDatablockWithList.__annotations__


class setResponseWithList(a_xdr.Implicit, asn1.NamedType, SetResponseWithList):
    """[5] IMPLICIT   Set-Response-With-List"""
    Tag = a_xdr.Tag(5)
    __annotations__ = SetResponseWithList.__annotations__


class SetResponse(a_xdr.Choice):
    """Set-Response"""
    def __init__(self, value: Union[
        setResponseNormal,
        setResponseDatablock,
        setResponseLastDatablock,
        setResponseLastDatablockWithList,
        setResponseWithList
    ]):
        super().__init__(value)


class setResponse(a_xdr.Implicit, asn1.NamedType, SetResponse):
    """[197] IMPLICIT      Set-Response"""
    Tag = a_xdr.Tag(197)


class AccessRequestGet(a_xdr.SequenceType):
    """Access-Request-Get"""
    __slots__ = _value
    cosem_attribute_descriptor: CosemAttributeDescriptor

    def __init__(self, value: tuple[CosemAttributeDescriptor,]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      cosem_attribute_descriptor: CosemAttributeDescriptor):
        return cls((cosem_attribute_descriptor,))


class AccessRequestGetWithSelection(a_xdr.SequenceType):
    """Access-Request-Get-With-Selection"""
    __slots__ = _value
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection:           SelectiveAccessDescriptor

    def __init__(self, value: tuple[CosemAttributeDescriptor, SelectiveAccessDescriptor]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      cosem_attribute_descriptor: CosemAttributeDescriptor,
                      access_selection: SelectiveAccessDescriptor):
        return cls((cosem_attribute_descriptor, access_selection))


class AccessRequestSet(a_xdr.SequenceType):
    """Access-Request-Set"""
    __slots__ = _value
    cosem_attribute_descriptor: CosemAttributeDescriptor

    def __init__(self, value: tuple[CosemAttributeDescriptor,]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      cosem_attribute_descriptor: CosemAttributeDescriptor):
        return cls((cosem_attribute_descriptor,))


class AccessRequestSetWithSelection(a_xdr.SequenceType):
    """Access-Request-Set-With-Selection"""
    __slots__ = _value
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection:           SelectiveAccessDescriptor

    def __init__(self, value: tuple[CosemAttributeDescriptor, SelectiveAccessDescriptor]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      cosem_attribute_descriptor: CosemAttributeDescriptor,
                      access_selection: SelectiveAccessDescriptor):
        return cls((cosem_attribute_descriptor, access_selection))


class AccessRequestAction(a_xdr.SequenceType):
    """Access-Request-Action"""
    __slots__ = _value
    cosem_method_descriptor: CosemMethodDescriptor

    def __init__(self, value: tuple[CosemMethodDescriptor,]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      cosem_method_descriptor: CosemMethodDescriptor):
        return cls((cosem_method_descriptor,))


class accessRequestGet(a_xdr.Implicit, asn1.NamedType, AccessRequestGet):
    """[1] Access-Request-Get"""
    Tag = a_xdr.Tag(1)
    __annotations__ = AccessRequestGet.__annotations__


class accessRequestSet(a_xdr.Implicit, asn1.NamedType, AccessRequestSet):
    """[2] Access-Request-Set"""
    Tag = a_xdr.Tag(2)
    __annotations__ = AccessRequestSet.__annotations__


class accessRequestAction(a_xdr.Implicit, asn1.NamedType, AccessRequestAction):
    """[3] Access-Request-Action"""
    Tag = a_xdr.Tag(3)
    __annotations__ = AccessRequestAction.__annotations__


class accessRequestGetWithSelection(a_xdr.Implicit, asn1.NamedType, AccessRequestGetWithSelection):
    """[4] Access-Request-Get-With-Selection"""
    Tag = a_xdr.Tag(4)
    __annotations__ = AccessRequestGetWithSelection.__annotations__


class accessRequestSetWithSelection(a_xdr.Implicit, asn1.NamedType, AccessRequestSetWithSelection):
    """[5] Access-Request-Set-With-Selection"""
    Tag = a_xdr.Tag(5)
    __annotations__ = AccessRequestSetWithSelection.__annotations__


class AccessRequestSpecification(a_xdr.Choice):
    """Access-Request-Specification"""
    def __init__(self, value: Union[
        accessRequestGet,
        accessRequestSet,
        accessRequestAction,
        accessRequestGetWithSelection,
        accessRequestSetWithSelection
    ]):
        super().__init__(value)


class ListOfAccessRequestSpecification(a_xdr.SequenceOfType):
    """List-Of-Access-Request-Specification"""
    Type = AccessRequestSpecification

    def __init__(self, value: tuple[AccessRequestSpecification, ...]):
        super().__init__(value)


class ListOfData(a_xdr.SequenceOfType):
    """List-Of-Data"""
    Type = Data

    def __init__(self, value: tuple[Data, ...]):
        super().__init__(value)


class AccessRequestBody(a_xdr.SequenceType):
    """Access-Request-Body"""
    __slots__ = _value
    access_request_specification:        ListOfAccessRequestSpecification
    access_request_list_of_data:         ListOfData

    def __init__(self, value: tuple[ListOfAccessRequestSpecification, ListOfData]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      access_request_specification: ListOfAccessRequestSpecification,
                      access_request_list_of_data: ListOfData):
        return cls((access_request_specification,access_request_list_of_data))


class AccessRequest(a_xdr.SequenceType):
    """Access-Request"""
    __slots__ = _value
    long_invoke_id_and_priority: LongInvokeIdAndPriority
    date_time:                   a_xdr.OctetStringType
    access_request_body:         AccessRequestBody

    def __init__(self, value: tuple[LongInvokeIdAndPriority, a_xdr.OctetStringType, AccessRequestBody]):
        super().__init__(value)

    @classmethod
    def from_elements(cls,
                      long_invoke_id_and_priority: LongInvokeIdAndPriority,
                      date_time: a_xdr.OctetStringType,
                      access_request_body: AccessRequestBody):
        return cls((long_invoke_id_and_priority, date_time, access_request_body))


class accessRequest(a_xdr.Implicit, asn1.NamedType, AccessRequest):
    """[217] IMPLICIT Access-Request"""
    Tag = a_xdr.Tag(217)
    __annotations__ = AccessRequest.__annotations__


class XDLMSAPDU(a_xdr.Choice):
    def __init__(self, value: Union[
        initiateRequest,
        readRequest,
        WriteRequest_,
        initiateResponse,
        ReadResponse_,
        WriteResponse_IMP,
        confirmedServiceError,
        # data-notification                  [15] IMPLICIT       Data-Notification,
        # unconfirmedWriteRequest            [22] IMPLICIT       UnconfirmedWriteRequest,
        # informationReportRequest           [24] IMPLICIT       InformationReportRequest,
        # glo-initiateRequest                [33]  IMPLICIT      OCTET STRING,
        # glo-readRequest                    [37]  IMPLICIT      OCTET STRING,
        # glo-writeRequest                   [38]  IMPLICIT      OCTET STRING,
        # glo-initiateResponse               [40]  IMPLICIT      OCTET STRING,
        # glo-readResponse                   [44]  IMPLICIT      OCTET STRING,
        # glo-writeResponse                  [45]  IMPLICIT      OCTET STRING,
        # glo-confirmedServiceError          [46]  IMPLICIT      OCTET STRING,
        # glo-unconfirmedWriteRequest        [54]  IMPLICIT      OCTET STRING,
        # glo-informationReportRequest       [56]  IMPLICIT      OCTET STRING,
        # ded-initiateRequest                [65]  IMPLICIT      OCTET STRING,
        # ded-readRequest                    [69]  IMPLICIT      OCTET STRING,
        # ded-writeRequest                   [70]  IMPLICIT      OCTET STRING,
        # ded-initiateResponse               [72]  IMPLICIT      OCTET STRING,
        # ded-readResponse                   [76]  IMPLICIT      OCTET STRING,
        # ded-writeResponse                  [77]  IMPLICIT      OCTET STRING,
        # ded-confirmedServiceError          [78]  IMPLICIT      OCTET STRING,
        # ded-unconfirmedWriteRequest        [86]  IMPLICIT      OCTET STRING,
        # ded-informationReportRequest       [88]  IMPLICIT      OCTET STRING,
        getRequest,
        setRequest,
        # event-notification-request         [194] IMPLICIT      EventNotificationRequest,
        actionRequest,
        getResponse,
        setResponse,
        # action-response                    [199] IMPLICIT      Action-Response,
        # glo-get-request                    [200] IMPLICIT      OCTET STRING,
        # glo-set-request                    [201] IMPLICIT      OCTET STRING,
        # glo-event-notification-request     [202] IMPLICIT      OCTET STRING,
        # glo-action-request                 [203] IMPLICIT      OCTET STRING,
        # glo-get-response                   [204] IMPLICIT      OCTET STRING,
        # glo-set-response                   [205] IMPLICIT      OCTET STRING,
        # glo-action-response                [207] IMPLICIT      OCTET STRING,
        # ded-get-request                    [208] IMPLICIT      OCTET STRING,
        # ded-set-request                    [209] IMPLICIT      OCTET STRING,
        # ded-event-notification-request     [210] IMPLICIT      OCTET STRING,
        # ded-actionRequest                  [211] IMPLICIT      OCTET STRING,
        # ded-get-response                   [212] IMPLICIT      OCTET STRING,
        # ded-set-response                   [213] IMPLICIT      OCTET STRING,
        # ded-action-response                [215] IMPLICIT      OCTET STRING,
        # exception-response                 [216] IMPLICIT      ExceptionResponse,
        accessRequest,
        # access-response                    [218] IMPLICIT      Access-Response,
        # general-glo-ciphering              [219] IMPLICIT      General-Glo-Ciphering,
        # general-ded-ciphering              [220] IMPLICIT      General-Ded-Ciphering,
        # general-ciphering                  [221] IMPLICIT      General-Ciphering,
        # general-signing                    [223] IMPLICIT      General-Signing,
        # general-block-transfer             [224] IMPLICIT      General-Block-Transfer
        # -- reserved                            [230]
        # -- reserved                            [231]
    ]):
        super().__init__(value)


class APTitle(a_xdr.OctetStringType):
    """AP-title"""


class AEQualifier(a_xdr.OctetStringType):
    """AE-qualifier"""


class APInvocationIdentifier(a_xdr.IntegerType):
    """AP-invocation-identifier"""


class AEInvocationIdentifier(a_xdr.IntegerType):
    """AE-invocation-identifier"""


class AssociationInformation(a_xdr.OctetStringType):
    """Association-information"""


# Application-context-name ::=           OBJECT IDENTIFIER
# ACSE-requirements ::=                  BIT STRING {authentication(0)}
# Mechanism-name ::=                     OBJECT IDENTIFIER

# Authentication-value ::= CHOICE
# {
#     charstring                         [0] IMPLICIT    GraphicString,
#     bitstring                          [1] IMPLICIT    BIT STRING
# }
#
# Implementation-data ::=                GraphicString
# Association-result ::=                 INTEGER
# {
#     accepted                           (0),
#     rejected-permanent                 (1),
#     rejected-transient                 (2)
# }

# Associate-source-diagnostic ::= CHOICE
# {
#     acse-service-user                  [1] INTEGER
#     {
#          null                                             (0),
#          no-reason-given                                  (1),
#          application-context-name-not-supported           (2),
#          calling-AP-title-not-recognized                  (3),
#          calling-AP-invocation-identifier-not-recognized  (4),
#          calling-AE-qualifier-not-recognized              (5),
#          calling-AE-invocation-identifier-not-recognized  (6),
#          called-AP-title-not-recognized                   (7),
#          called-AP-invocation-identifier-not-recognized   (8),
#          called-AE-qualifier-not-recognized               (9),
#          called-AE-invocation-identifier-not-recognized   (10),
#          authentication-mechanism-name-not-recognised     (11),
#          authentication-mechanism-name-required           (12),
#          authentication-failure                           (13),
#          authentication-required                          (14)
#     },
#     acse-service-provider              [2] INTEGER
#     {
#          null                               (0),
#          no-reason-given                    (1),
#          no-common-acse-version             (2)
#     }
# }
#
# Release-request-reason ::= INTEGER
# {
#     normal                             (0),
#     urgent                             (1),
#     user-defined                       (30)
# }
#
# Release-response-reason ::= INTEGER
# {
#     normal                             (0),
#     not-finished                       (1),
#     user-defined                       (30)
# }

# UnconfirmedWriteRequest ::= SEQUENCE
# {
#     variable-access-specification      SEQUENCE OF Variable-Access-Specification,
#     list-of-data                       SEQUENCE OF Data
# }
#
# InformationReportRequest ::= SEQUENCE
# {
#     current-time                       GeneralizedTime OPTIONAL,
#     variable-access-specification      SEQUENCE OF Variable-Access-Specification,
#     list-of-data                       SEQUENCE OF Data
# }




# Action-Response ::= CHOICE
# {
#     action-response-normal             [1] IMPLICIT    Action-Response-Normal,
#     action-response-with-pblock        [2] IMPLICIT    Action-Response-With-Pblock,
#     action-response-with-list          [3] IMPLICIT    Action-Response-With-List,
#     action-response-next-pblock        [4] IMPLICIT    Action-Response-Next-Pblock
# }
#
# Action-Response-Normal ::= SEQUENCE
# {
#     invoke-id-and-priority             Invoke-Id-And-Priority,
#     single-response                    Action-Response-With-Optional-Data
# }
#
# Action-Response-With-Pblock ::= SEQUENCE
# {
#     invoke-id-and-priority             Invoke-Id-And-Priority,
#     pblock                             DataBlock-SA
# }
#
# Action-Response-With-List ::= SEQUENCE
# {
#     invoke-id-and-priority             Invoke-Id-And-Priority,
#     list-of-responses                  SEQUENCE OF Action-Response-With-Optional-Data
# }
#
# Action-Response-Next-Pblock ::= SEQUENCE
# {
#     invoke-id-and-priority             Invoke-Id-And-Priority,
#     block-number                       Unsigned32
# }
#
# EventNotificationRequest ::= SEQUENCE
# {
#     time                               OCTET STRING  OPTIONAL,
#     cosem-attribute-descriptor         Cosem-Attribute-Descriptor,
#     attribute-value                    Data
# }
#
# ExceptionResponse ::= SEQUENCE
# {
#     state-error                        [0] IMPLICIT ENUMERATED
#     {
#         service-not-allowed                 (1),
#         service-unknown                     (2)
#     },
#     service-error                      [1] CHOICE
#     {
#         operation-not-possible              [1] IMPLICIT NULL,
#         service-not-supported               [2] IMPLICIT NULL,
#         other-reason                        [3] IMPLICIT NULL,
#         pdu-too-long                        [4] IMPLICIT NULL,
#         deciphering-error                   [5] IMPLICIT NULL,
#         invocation-counter-error            [6] IMPLICIT Unsigned32
#     }
# }
#
#
# Access-Response ::= SEQUENCE
# {
# 	long-invoke-id-and-priority        Long-Invoke-Id-And-Priority,
# 	date-time                          OCTET STRING,
# 	access-response-body               Access-Response-Body
# }
#
#
# -- 	 Data-Notification
#
# Data-Notification ::= SEQUENCE
# {
#    long-invoke-id-and-priority         Long-Invoke-Id-And-Priority,
#    date-time                           OCTET STRING,
#    notification-body                   Notification-Body
# }
#
#
# -- General APDUs
#
# General-Ded-Ciphering ::= SEQUENCE
# {
#    system-title                        OCTET STRING,
#    ciphered-content                    OCTET STRING
# }
#
# General-Glo-Ciphering ::= SEQUENCE
# {
#    system-title                        OCTET STRING,
#    ciphered-content                    OCTET STRING
# }
#
# General-Ciphering ::= SEQUENCE
# {
#    transaction-id                      OCTET STRING,
#    originator-system-title             OCTET STRING,
#    recipient-system-title              OCTET STRING,
#    date-time                           OCTET STRING,
#    other-information                   OCTET STRING,
#    key-info                            Key-Info OPTIONAL,
#    ciphered-content                    OCTET STRING
# }
#
# General-Signing ::= SEQUENCE
# {
#    transaction-id                      OCTET STRING,
#    originator-system-title             OCTET STRING,
#    recipient-system-title              OCTET STRING,
#    date-time                           OCTET STRING,
#    other-information                   OCTET STRING,
#    content                             OCTET STRING,
#    signature                           OCTET STRING
# }
#
# General-Block-Transfer ::= SEQUENCE
# {
#    block-control                       Block-Control,
#    block-number                        Unsigned16,
#    block-number-ack                    Unsigned16,
#    block-data                          OCTET STRING
# }

# TypeDescription ::= CHOICE
# {
#     null-data                          [0]   IMPLICIT  NULL,
#     array                              [1]   IMPLICIT  SEQUENCE
#     {
#         number-of-elements        Unsigned16,
#         type-description          TypeDescription
#     },
#     structure                          [2]   IMPLICIT  SEQUENCE OF TypeDescription,
#     boolean                            [3]   IMPLICIT  NULL,
#     bit-string                         [4]   IMPLICIT  NULL,
#     double-long                        [5]   IMPLICIT  NULL,
#     double-long-unsigned               [6]   IMPLICIT  NULL,
#     octet-string                       [9]   IMPLICIT  NULL,
#     visible-string                     [10]  IMPLICIT  NULL,
#     utf8-string                        [12]  IMPLICIT  NULL,
#     bcd                                [13]  IMPLICIT  NULL,
#     integer                            [15]  IMPLICIT  NULL,
#     long                               [16]  IMPLICIT  NULL,
#     unsigned                           [17]  IMPLICIT  NULL,
#     long-unsigned                      [18]  IMPLICIT  NULL,
#     long64                             [20]  IMPLICIT  NULL,
#     long64-unsigned                    [21]  IMPLICIT  NULL,
#     enum                               [22]  IMPLICIT  NULL,
#     float32                            [23]  IMPLICIT  NULL,
#     float64                            [24]  IMPLICIT  NULL,
#     date-time                          [25]  IMPLICIT  NULL,
#     date                               [26]  IMPLICIT  NULL,
#     time                               [27]  IMPLICIT  NULL,
#     dont-care                          [255] IMPLICIT  NULL
# }

# Cosem-Attribute-Descriptor-With-Selection ::= SEQUENCE
# {
#     cosem-attribute-descriptor         Cosem-Attribute-Descriptor,
#     access-selection                   Selective-Access-Descriptor OPTIONAL
# }

# Get-Data-Result ::= CHOICE
# {
#    data                                [0] Data,
#    data-access-result                  [1] IMPLICIT Data-Access-Result
# }
#
# DataBlock-G ::= SEQUENCE     -- G == DataBlock for the GET-response
# {
#     last-block                         BOOLEAN,
#     block-number                       Unsigned32,
#     result  CHOICE
#     {
#         raw-data                       [0] IMPLICIT OCTET STRING,
#         data-access-result             [1] IMPLICIT Data-Access-Result
#     }
# }
#
#
# Action-Response-With-Optional-Data ::= SEQUENCE
# {
#     result                             Action-Result,
#     return-parameters                  Get-Data-Result  OPTIONAL
# }
#
# Notification-Body ::= SEQUENCE
# {
#    data-value                          Data
# }
#
#
#
#
#
# Access-Response-Get ::= SEQUENCE
# {
#    result                              Data-Access-Result
# }
#
# Access-Response-Set ::= SEQUENCE
# {
#    result                              Data-Access-Result
# }
#
# Access-Response-Action ::= SEQUENCE
# {
#    result                              Action-Result
# }
#
# Access-Response-Specification ::= CHOICE
# {
#    access-response-get                 [1] Access-Response-Get,
#    access-response-set                 [2] Access-Response-Set,
#    access-response-action              [3] Access-Response-Action
# }
#
# List-Of-Access-Response-Specification ::= SEQUENCE OF Access-Response-Specification
#
# Access-Response-Body ::= SEQUENCE
# {
#    access-request-specification        [0] List-Of-Access-Request-Specification OPTIONAL,
#    access-response-list-of-data        List-Of-Data,
#    access-response-specification       List-Of-Access-Response-Specification
# }
#
# -- Key-info
#
# Key-Id ::= ENUMERATED
# {
# 	global-unicast-encryption-key      (0),
# 	global-broadcast-encryption-key    (1)
# }
#
# Kek-Id ::= ENUMERATED
# {
# 	master-key                         (0)
# }
#
#
# Identified-Key ::= SEQUENCE
# {
# 	key-id                             Key-Id
# }
#
# Wrapped-Key ::= SEQUENCE
# {
#     kek-id                             Kek-Id,
#     key-ciphered-data                  OCTET STRING
# }
#
# Agreed-Key ::= SEQUENCE
# {
#     key-parameters                     OCTET STRING,
#     key-ciphered-data                  OCTET STRING
# }
#
# Key-Info ::= CHOICE
# {
#     identified-key                     [0] Identified-Key,
#     wrapped-key                        [1] Wrapped-Key,
#     agreed-key                         [2] Agreed-Key
# }
#
# -- Use of Block-Control
# --    window                   bits 0-5      window advertise
# --    streaming                bit  6        0 = No Streaming active, 1 = Streaming active
# --    last-block               bit  7        0 = Not Last Block, 1 = Last Block
# Block-Control ::=                      Unsigned8


# AARQ-apdu ::= [APPLICATION 0] IMPLICIT SEQUENCE
# {
# -- [APPLICATION 0] == [ 60H ] = [ 96 ]
#
#     protocol-version                   [0] IMPLICIT        BIT STRING {version1 (0)} DEFAULT {version1},
#     application-context-name           [1]                 Application-context-name,
#     called-AP-title                    [2]                 AP-title OPTIONAL,
#     called-AE-qualifier                [3]                 AE-qualifier OPTIONAL,
#     called-AP-invocation-id            [4]                 AP-invocation-identifier OPTIONAL,
#     called-AE-invocation-id            [5]                 AE-invocation-identifier OPTIONAL,
#     calling-AP-title                   [6]                 AP-title OPTIONAL,
#     calling-AE-qualifier               [7]                 AE-qualifier OPTIONAL,
#     calling-AP-invocation-id           [8]                 AP-invocation-identifier OPTIONAL,
#     calling-AE-invocation-id           [9]                 AE-invocation-identifier OPTIONAL,
#
# -- The following field shall not be present if only the kernel is used.
#     sender-acse-requirements           [10] IMPLICIT      ACSE-requirements OPTIONAL,
#
# -- The following field shall only be present if the authentication functional unit is selected.
#     mechanism-name                     [11] IMPLICIT      Mechanism-name OPTIONAL,
#
# -- The following field shall only be present if the authentication functional unit is selected.
#
#     calling-authentication-value       [12] EXPLICIT      Authentication-value OPTIONAL,
#     implementation-information         [29] IMPLICIT      Implementation-data OPTIONAL,
#     user-information                   [30] EXPLICIT      Association-information OPTIONAL
# }

# AARE-apdu ::= [APPLICATION 1] IMPLICIT SEQUENCE
# {
# -- [APPLICATION 1] == [ 61H ] = [ 97 ]
#
#     protocol-version                   [0] IMPLICIT        BIT STRING {version1 (0)} DEFAULT {version1},
#     application-context-name           [1]                 Application-context-name,
#     result                             [2]                 Association-result,
#     result-source-diagnostic           [3]                 Associate-source-diagnostic,
#     responding-AP-title                [4]                 AP-title OPTIONAL,
#     responding-AE-qualifier            [5]                 AE-qualifier OPTIONAL,
#     responding-AP-invocation-id        [6]                 AP-invocation-identifier OPTIONAL,
#     responding-AE-invocation-id        [7]                 AE-invocation-identifier OPTIONAL,
#
# -- The following field shall not be present if only the kernel is used.
#     responder-acse-requirements        [8] IMPLICIT        ACSE-requirements OPTIONAL,
#
# -- The following field shall only be present if the authentication functional unit is selected.
#     mechanism-name                     [9] IMPLICIT        Mechanism-name OPTIONAL,
#
# -- The following field shall only be present if the authentication functional unit is selected.
#     responding-authentication-value    [10] EXPLICIT       Authentication-value OPTIONAL,
#     implementation-information         [29] IMPLICIT       Implementation-data OPTIONAL,
#     user-information                   [30] EXPLICIT       Association-information OPTIONAL
# }
#
# -- The user-information field shall carry either an InitiateResponse (or, when the proposed xDLMS
# -- context is not accepted by the server, a ConfirmedServiceError) APDU encoded in A-XDR, and then
# -- encoding the resulting OCTET STRING in BER.
#
# RLRQ-apdu ::= [APPLICATION 2] IMPLICIT SEQUENCE
# {
# -- [APPLICATION 2] == [ 62H ] = [ 98 ]
#
#     reason                             [0] IMPLICIT        Release-request-reason OPTIONAL,
#     user-information                   [30] EXPLICIT       Association-information OPTIONAL
# }
#
# RLRE-apdu ::= [APPLICATION 3] IMPLICIT SEQUENCE
# {
# -- [APPLICATION 3] == [ 63H ] = [ 99 ]
#
#     reason                             [0] IMPLICIT        Release-response-reason OPTIONAL,
#     user-information                   [30] EXPLICIT       Association-information OPTIONAL
# }

# ACSE-XDLMSAPDU ::= CHOICE
# {
#     aarq                               AARQ-apdu,
#     aare                               AARE-apdu,
#     rlrq                               RLRQ-apdu,          -- OPTIONAL
#     rlre                               RLRE-apdu           -- OPTIONAL
# }

