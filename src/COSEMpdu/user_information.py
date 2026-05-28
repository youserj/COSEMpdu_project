from typing import Optional, Self, ClassVar, Literal
from .x680 import tag, TaggingMode
from .x680.type import (
    INTEGER
)
from .x680.bit_string import NamedBitList, NamedBit
from .x680.constrained_type import SizeConstraint
from . import x690
from . import ber
from . import axdr
from .useful_types import Integer8, Unsigned16, Unsigned8, ObjectName


class BitStringConformance(ber.BitStringType):
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


class Conformance_(ber.ConstrainedType[BitStringConformance]):
    """Conformance"""
    constraint_spec = SizeConstraint(24)
    value: BitStringConformance


NamedBitLiteral = Literal[
    "reserved-zero",
    "general-protection",
    "general-block-transfer",
    "read",
    "write",
    "unconfirmed-write",
    "delta-value-encoding",
    "reserved-seven",
    "attribute0-supported-with-set",
    "priority-mgmt-supported",
    "attribute0-supported-with-get",
    "block-transfer-with-get-or-read",
    "block-transfer-with-set-or-write",
    "block-transfer-with-action",
    "multiple-references",
    "information-report",
    "data-notification",
    "access",
    "parameterized-access",
    "get",
    "set",
    "selective-access",
    "event-notification",
    "action"
]


class Conformance(ber.TaggedType[Conformance_]):
    tag = x690.Tag(
        class_number=31,
        class_=tag.Class.APPLICATION
    )
    mode = TaggingMode.IMPLICIT
    value: Conformance_

    def __getitem__(self, key: NamedBitLiteral) -> INTEGER:
        return self.value.value[key]


LN_REFERENCE = ObjectName(axdr.IntegerType(0x0007))
SN_REFERENCE = ObjectName(axdr.IntegerType(-1536))  # 0xFA00


class InitiateRequest(axdr.SequenceType):
    """InitiateRequest"""
    dedicated_key: Optional[axdr.OctetStringType] = None
    response_allowed: axdr.BooleanType = axdr.BooleanType(True)
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
        dedicated_key: Optional[axdr.OctetStringType] = None,
        response_allowed: axdr.BooleanType = axdr.BooleanType(True),
        proposed_quality_of_service: Optional[Integer8] = None,
    ) -> None:
        self.dedicated_key = dedicated_key
        self.response_allowed = response_allowed
        self.proposed_quality_of_service = proposed_quality_of_service
        self.proposed_dlms_version_number = proposed_dlms_version_number
        self.proposed_conformance = proposed_conformance
        self.client_max_receive_pdu_size = client_max_receive_pdu_size


class InitiateResponse(axdr.SequenceType):
    """InitiateResponse"""
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
