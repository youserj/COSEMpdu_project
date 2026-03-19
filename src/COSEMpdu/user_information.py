from dataclasses import dataclass
from typing import Optional, Self, ClassVar, Any
from .x680 import tag, TaggingMode
from .x680.type import (
    Constraint,
    SizeConstraint,
    OptionalNamedType,
    DefaultNamedType,
    NamedType
)
from .x680.bit_string import NamedBitList, NamedBit
from . import ber
from . import axdr
from .cosem_pdu import Integer8, Unsigned16, Unsigned8, ObjectName


@dataclass
class Conformance_(ber.BitStringType):
    """Conformance"""
    named_bits: ClassVar[Optional[NamedBitList]] = NamedBitList((
        NamedBit("reserved-zero", 0),
        NamedBit("general-protection", 1),
        NamedBit("general-block-transfer", 2),
        NamedBit("read", 3),
        NamedBit("write", 4),
        NamedBit("unconfirmed-write", 5),
        NamedBit("reserved-six", 6),
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
    constraint: ClassVar[Optional[Constraint[Any]]] = Constraint(SizeConstraint(24))


@dataclass
class Conformance(ber.TaggedType):
    tag = ber.Tag(
        class_number=31,
        class_=tag.Class.APPLICATION
    )
    mode = TaggingMode.IMPLICIT
    type_ = Conformance_


LN_REFERENCE = ObjectName(0x0007)
SN_REFERENCE = ObjectName(0xFA00)


@dataclass
class InitiateRequest(axdr.SequenceType):
    """InitiateRequest"""
    components = (
        OptionalNamedType("dedicated-key", axdr.OctetStringType),
        DefaultNamedType("response-allowed", axdr.BooleanType, axdr.BooleanType(True)),
        OptionalNamedType("proposed-quality-of-service", Integer8),
        NamedType("proposed-dlms-version-number", Unsigned8),
        NamedType("proposed-conformance", Conformance),
        NamedType("client-max-receive-pdu-size", Unsigned16),
    )

    @classmethod
    def from_components(cls, *,
        dedicated_key: Optional[axdr.OctetStringType],
        response_allowed: Optional[axdr.BooleanType],
        proposed_quality_of_service: Optional[Integer8],
        proposed_dlms_version_number: Unsigned8,
        proposed_conformance: Conformance,
        client_max_receive_pdu_size: Unsigned16
    ) -> Self:
        return cls((
            dedicated_key,
            axdr.BooleanType(True) if response_allowed is None else response_allowed,
            proposed_quality_of_service,
            proposed_dlms_version_number,
            proposed_conformance,
            client_max_receive_pdu_size
        ))


@dataclass
class InitiateResponse(axdr.SequenceType):
    """InitiateResponse"""
    components = (
        OptionalNamedType("negotiated-quality-of-service", Integer8),
        NamedType("negotiated-dlms-version-number", Unsigned8),
        NamedType("negotiated-conformance", Conformance),
        NamedType("server-max-receive-pdu-size", Unsigned16),
        NamedType("vaa-name", ObjectName),
    )

    @classmethod
    def from_components(cls, *,
        negotiated_quality_of_service: Optional[Integer8],
        negotiated_dlms_version_number: Unsigned8,
        negotiated_conformance: Conformance,
        server_max_receive_pdu_size: Unsigned16,
        vaa_name: ObjectName
    ) -> Self:
        """
        Create InitiateResponse from components.

        Args:
            negotiated_quality_of_service: QoS parameter (optional, not used in DLMS/COSEM)
            negotiated_dlms_version_number: DLMS version (typically 1)
            negotiated_conformance: Conformance block (BER encoded)
            server_max_receive_pdu_size: Maximum PDU size server can receive
            vaa_name: Virtual Association Entity name (ObjectName)

        Returns:
            InitiateResponse instance
        """
        return cls((
            negotiated_quality_of_service,
            negotiated_dlms_version_number,
            negotiated_conformance,
            server_max_receive_pdu_size,
            vaa_name
        ))
