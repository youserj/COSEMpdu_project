"""
COSEM PDU Types Implementation
Based on COSEMpdu_GB83.txt (Green Book 8.3)
Implements A-XDR encoding/decoding according to IEC 61334-6 ACSE APDU Types (COSEMpdu_GB83
"""
from dataclasses import dataclass
from re import A, M
from typing import ClassVar, Self, Optional, override
from . import x690
from .x680 import (
    NamedType,
    OptionalNamedType,
    DefaultNamedType,
    Type,
    TaggingMode,
    NamedBitList,
    NamedBit,
    NamedNumberList,
    NamedNumber
)
from . import axdr
from . import ber
from .x680.tag import Class
from .ber import create_alternatives


@dataclass
class ApplicationContextName(ber.ObjectIdentifierType):
    """Application-context-name"""


@dataclass
class ApplicationContextName1(ber.TaggedType[ApplicationContextName]):
    """[1] Application-context-name"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=1)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: ApplicationContextName


@dataclass
class APTitle(ber.OctetStringType):
    """AP-title"""


@dataclass
class AEQualifier(ber.OctetStringType):
    """AE-qualifier"""


@dataclass
class APInvocationIdentifier(ber.IntegerType):
    """AP-invocation-identifier"""


@dataclass
class AEInvocationIdentifier(ber.IntegerType):
    """AE-invocation-identifier"""


@dataclass
class ACSERequirements(ber.BitStringType):
    """ACSE-requirements"""
    named_bits = NamedBitList((NamedBit("authentication", 0),))


@dataclass
class MechanismName(ber.ObjectIdentifierType):
    """Mechanism-name"""


@dataclass
class Charstring(ber.TaggedType[ber.GraphicString]):
    """[0] IMPLICIT GraphicString"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=0)
    mode: ClassVar[TaggingMode] = TaggingMode.IMPLICIT
    value: ber.GraphicString

@dataclass
class BitString1(ber.TaggedType[ber.BitStringType]):
    """ [1] IMPLICIT BIT STRING"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=1)
    mode: ClassVar[TaggingMode] = TaggingMode.IMPLICIT
    value: ber.BitStringType


@dataclass
class AuthenticationValue(ber.ChoiceType):
    """Authentication-value"""
    alternatives = ber.create_alternatives(
        NamedType("charstring", Charstring),
        NamedType("bitstring", BitString1)
    )


@dataclass
class ImplementationData(ber.GraphicString):
    """Implementation-data"""


@dataclass
class ImplementationData29(ber.TaggedType[ImplementationData]):
    """[29] IMPLICIT Implementation-data"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=29)
    mode: ClassVar[TaggingMode] = TaggingMode.IMPLICIT
    value: ImplementationData


@dataclass
class AssociationInformation(ber.OctetStringType):
    """Association-information"""


@dataclass
class AssociationInformation30(ber.TaggedType[AssociationInformation]):
    """[30] EXPLICIT Association-information"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=30)
    mode: ClassVar[TaggingMode] = TaggingMode.EXPLICIT
    value: AssociationInformation


@dataclass
class AssociationResult(ber.IntegerType):
    """Association-result"""
    named_numbers = NamedNumberList((
        NamedNumber("accepted", 0),
        NamedNumber("rejected-permanent", 1),
        NamedNumber("rejected-transient", 2),
    ))


@dataclass
class Result(ber.TaggedType[AssociationResult]):
    """[2] Association-result"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=2)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: AssociationResult


@dataclass
class AcseServiceUser(ber.IntegerType):
    """acse-service-user"""
    named_numbers = NamedNumberList((
        NamedNumber("null", 0),
        NamedNumber("no-reason-given", 1),
        NamedNumber("application-context-name-not-supported", 2),
        NamedNumber("calling-AP-title-not-recognized", 3),
        NamedNumber("calling-AP-invocation-identifier-not-recognized", 4),
        NamedNumber("calling-AE-qualifier-not-recognized", 5),
        NamedNumber("calling-AE-invocation-identifier-not-recognized", 6),
        NamedNumber("called-AP-title-not-recognized", 7),
        NamedNumber("called-AP-invocation-identifier-not-recognized", 8),
        NamedNumber("called-AE-qualifier-not-recognized", 9),
        NamedNumber("called-AE-invocation-identifier-not-recognized", 10),
        NamedNumber("authentication-mechanism-name-not-recognised", 11),
        NamedNumber("authentication-mechanism-name-required", 12),
        NamedNumber("authentication-failure", 13),
        NamedNumber("authentication-required", 14),
    ))


@dataclass
class ServiceUser(ber.TaggedType[AcseServiceUser]):
    """[1] acse-service-user"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=1)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: AcseServiceUser


@dataclass
class AcseServiceProvider(ber.IntegerType):
    """acse-service-provider"""
    named_numbers = NamedNumberList((
        NamedNumber("null", 0),
        NamedNumber("no-reason-given", 1),
        NamedNumber("no-common-acse-version", 2),
    ))


@dataclass
class Provider(ber.TaggedType[AcseServiceProvider]):
    """[2] acse-service-provider"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=2)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: AcseServiceProvider


@dataclass
class AssociateSourceDiagnostic(ber.ChoiceType):
    """Associate-source-diagnostic"""
    alternatives = create_alternatives(
        NamedType("acse-service-user", ServiceUser),
        NamedType("acse-service-provider", Provider)
    )


@dataclass
class ResultSourceDiagnostic(ber.TaggedType[AssociateSourceDiagnostic]):
    """[3] Associate-source-diagnostic"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=3)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: AssociateSourceDiagnostic


@dataclass
class ReleaseRequestReason(ber.IntegerType):
    """Release-request-reason"""
    named_numbers = NamedNumberList((
        NamedNumber("normal", 0),
        NamedNumber("urgent", 1),
        NamedNumber("user-defined", 30),
    ))


@dataclass
class RequestReason(ber.TaggedType[ReleaseRequestReason]):
    """[0] IMPLICIT Release-request-reason"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=0)
    mode: ClassVar[TaggingMode] = TaggingMode.IMPLICIT
    value: ReleaseRequestReason


@dataclass
class ReleaseResponseReason(ber.IntegerType):
    """Release-response-reason"""
    named_numbers = NamedNumberList((
        NamedNumber("normal", 0),
        NamedNumber("not-finished", 1),
        NamedNumber("user-defined", 30),
    ))


@dataclass
class ResponseReason(ber.TaggedType[ReleaseResponseReason]):
    """[0] IMPLICIT Release-response-reason"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=0)
    mode: ClassVar[TaggingMode] = TaggingMode.IMPLICIT
    value: ReleaseResponseReason


@dataclass
class ProtocolVersion(ber.BitStringType):
    """protocol-version"""
    named_bits = NamedBitList((NamedBit("version1", 0),))


@dataclass
class ProtocolVersion0(ber.TaggedType[ProtocolVersion]):
    """[0] IMPLICIT protocol-version"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=0)
    mode: ClassVar[TaggingMode] = TaggingMode.IMPLICIT
    value: ProtocolVersion


DEFAULT_PROTOCOL_VERSION = ProtocolVersion0(ProtocolVersion((0,)))


@dataclass
class CalledAPTitle(ber.TaggedType[APTitle]):
    """[2] AP-title"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=2)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: APTitle


@dataclass
class CallingAPTitle(ber.TaggedType[APTitle]):
    """[6] AP-title"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=6)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: APTitle


@dataclass
class CalledAEQualifier(ber.TaggedType[AEQualifier]):
    """[3] AE-qualifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=3)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: AEQualifier


@dataclass
class CallingAEQualifier(ber.TaggedType[AEQualifier]):
    """[7] AE-qualifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=7)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: AEQualifier


@dataclass
class CalledAPInvocationIdentifier(ber.TaggedType[APInvocationIdentifier]):
    """[4] AP-invocation-identifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=4)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: APInvocationIdentifier


@dataclass
class CallingAPInvocationIdentifier(ber.TaggedType[APInvocationIdentifier]):
    """[8] AP-invocation-identifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=8)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: APInvocationIdentifier


@dataclass
class CalledAEInvocationIdentifier(ber.TaggedType[AEInvocationIdentifier]):
    """[5] AE-invocation-identifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=5)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: AEInvocationIdentifier


@dataclass
class CallingAEInvocationIdentifier(ber.TaggedType[AEInvocationIdentifier]):
    """[9] AE-invocation-identifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=9)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: AEInvocationIdentifier


@dataclass
class SenderACSERequirements(ber.TaggedType[ACSERequirements]):
    """[10] IMPLICIT ACSE-requirements"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=10)
    mode: ClassVar[TaggingMode] = TaggingMode.IMPLICIT
    value: ACSERequirements


@dataclass
class MechanismName11(ber.TaggedType[MechanismName]):
    """[11] IMPLICIT Mechanism-name tagged"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=11)
    mode: ClassVar[TaggingMode] = TaggingMode.IMPLICIT
    value: MechanismName


@dataclass
class CallingAuthenticationValue(ber.TaggedType[AuthenticationValue]):
    """[12] EXPLICIT Authentication-value"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=12)
    mode: ClassVar[TaggingMode] = TaggingMode.EXPLICIT
    value: AuthenticationValue


@dataclass
class AARQApdu(ber.SequenceType):
    """AARQ-apdu"""
    components = (
        DefaultNamedType("protocol-version", ProtocolVersion0, DEFAULT_PROTOCOL_VERSION),
        NamedType("application-context-name", ApplicationContextName1),
        OptionalNamedType("called-AP-title", CalledAPTitle),
        OptionalNamedType("called-AE-qualifier", CalledAEQualifier),
        OptionalNamedType("called-AP-invocation-id", CalledAPInvocationIdentifier),
        OptionalNamedType("called-AE-invocation-id", CalledAEInvocationIdentifier),
        OptionalNamedType("calling-AP-title", CallingAPTitle),
        OptionalNamedType("calling-AE-qualifier", CallingAEQualifier),
        OptionalNamedType("calling-AP-invocation-id", CallingAPInvocationIdentifier),
        OptionalNamedType("calling-AE-invocation-id", CallingAEInvocationIdentifier),
        OptionalNamedType("sender-acse-requirements", SenderACSERequirements),
        OptionalNamedType("mechanism-name", MechanismName11),
        OptionalNamedType("calling-authentication-value", CallingAuthenticationValue),
        OptionalNamedType("implementation-information", ImplementationData29),
        OptionalNamedType("user-information", AssociationInformation30),
    )

    @classmethod
    def from_components(
        cls,
        *,
        protocol_version: Optional[ProtocolVersion0] = None,
        application_context_name: ApplicationContextName1,
        called_ap_title: Optional[CalledAPTitle] = None,
        called_ae_qualifier: Optional[CalledAEQualifier] = None,
        called_ap_invocation_id: Optional[CalledAPInvocationIdentifier] = None,
        called_ae_invocation_id: Optional[CalledAEInvocationIdentifier] = None,
        calling_ap_title: Optional[CallingAPTitle] = None,
        calling_ae_qualifier: Optional[CallingAEQualifier] = None,
        calling_ap_invocation_id: Optional[CallingAPInvocationIdentifier] = None,
        calling_ae_invocation_id: Optional[CalledAEInvocationIdentifier] = None,
        sender_acse_requirements: Optional[SenderACSERequirements] = None,
        mechanism_name: Optional[MechanismName11] = None,
        calling_authentication_value: Optional[CallingAuthenticationValue] = None,
        implementation_information: Optional[ImplementationData29] = None,
        user_information: Optional[AssociationInformation30] = None,
    ) -> Self:
        """
        Create AARQApdu instance from named components.

        Returns:
            Self: New AARQApdu instance with value set to _AARQApdu
        """
        return cls((
            DEFAULT_PROTOCOL_VERSION if protocol_version is None else protocol_version,
            application_context_name,
            called_ap_title,
            called_ae_qualifier,
            called_ap_invocation_id,
            called_ae_invocation_id,
            calling_ap_title,
            calling_ae_qualifier,
            calling_ap_invocation_id,
            calling_ae_invocation_id,
            sender_acse_requirements,
            mechanism_name,
            calling_authentication_value,
            implementation_information,
            user_information
        ))


@dataclass
class AARQ(ber.TaggedType[AARQApdu]):
    """[APPLICATION 0] IMPLICIT AARQ-apdu"""
    tag: ClassVar[x690.Tag] = x690.Tag(
        class_=Class.APPLICATION,
        class_number=0,
        constructed=True
    )
    mode: ClassVar[TaggingMode] = TaggingMode.IMPLICIT
    value: AARQApdu


@dataclass
class RespondingAPTitle(ber.TaggedType[APTitle]):
    """[4] AP-title"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=4)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: APTitle


@dataclass
class RespondingAEQualifier(ber.TaggedType[AEQualifier]):
    """[5] AE-qualifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=5)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: AEQualifier


@dataclass
class RespondingAPInvocationIdentifier(ber.TaggedType[APInvocationIdentifier]):
    """[6] AP-invocation-identifier tagged"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=6)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: APInvocationIdentifier


@dataclass
class RespondingAEInvocationIdentifier(ber.TaggedType[AEInvocationIdentifier]):
    """[7] AE-invocation-identifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=7)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT
    value: AEInvocationIdentifier


@dataclass
class ResponderACSERequirements(ber.TaggedType[ACSERequirements]):
    """[8] IMPLICIT ACSE-requirements tagged"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=8)
    mode: ClassVar[TaggingMode] = TaggingMode.IMPLICIT
    value: ACSERequirements


@dataclass
class MechanismName9(ber.TaggedType[MechanismName]):
    """[9] IMPLICIT Mechanism-name"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=9)
    mode: ClassVar[TaggingMode] = TaggingMode.IMPLICIT
    value: MechanismName



@dataclass
class RespondingAuthenticationValue(ber.TaggedType[AuthenticationValue]):
    """[11] EXPLICIT Authentication-value"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=11)
    mode: ClassVar[TaggingMode] = TaggingMode.EXPLICIT
    value: AuthenticationValue


@dataclass
class AAREApdu(ber.SequenceType):
    """AARE-apdu"""
    components = (
        DefaultNamedType("protocol-version", ProtocolVersion0, DEFAULT_PROTOCOL_VERSION),
        NamedType("application-context-name", ApplicationContextName1),
        NamedType("result", Result),
        NamedType("result-source-diagnostic", ResultSourceDiagnostic),
        OptionalNamedType("responding-AP-title", RespondingAPTitle),
        OptionalNamedType("responding-AE-qualifier", RespondingAEQualifier),
        OptionalNamedType("responding-AP-invocation-id", RespondingAPInvocationIdentifier),
        OptionalNamedType("responding-AE-invocation-id", RespondingAEInvocationIdentifier),
        OptionalNamedType("responder-acse-requirements", ResponderACSERequirements),
        OptionalNamedType("mechanism-name", MechanismName9),
        OptionalNamedType("responding-authentication-value", RespondingAuthenticationValue),
        OptionalNamedType("implementation-information", ImplementationData29),
        OptionalNamedType("user-information", AssociationInformation30),
    )

    @classmethod
    def from_components(
        cls,
        *,
        protocol_version: Optional[ProtocolVersion0] = None,
        application_context_name: ApplicationContextName1,
        result: Result,
        result_source_diagnostic: ResultSourceDiagnostic,
        responding_ap_title: Optional[RespondingAPTitle] = None,
        responding_ae_qualifier: Optional[RespondingAEQualifier] = None,
        responding_ap_invocation_id: Optional[RespondingAPInvocationIdentifier] = None,
        responding_ae_invocation_id: Optional[RespondingAEInvocationIdentifier] = None,
        responder_acse_requirements: Optional[ResponderACSERequirements] = None,
        mechanism_name: Optional[MechanismName9] = None,
        responding_authentication_value: Optional[RespondingAuthenticationValue] = None,
        implementation_information: Optional[ImplementationData29] = None,
        user_information: Optional[AssociationInformation30] = None,
    ) -> Self:
        return cls((
            DEFAULT_PROTOCOL_VERSION if protocol_version is None else protocol_version,
            application_context_name,
            result,
            result_source_diagnostic,
            responding_ap_title,
            responding_ae_qualifier,
            responding_ap_invocation_id,
            responding_ae_invocation_id,
            responder_acse_requirements,
            mechanism_name,
            responding_authentication_value,
            implementation_information,
            user_information
        ))


@dataclass
class AARE(ber.TaggedType[AAREApdu]):
    """[1] AARE-apdu"""
    tag: ClassVar[x690.Tag] = x690.Tag(
        class_=Class.APPLICATION,
        class_number=1,
        constructed=True
    )
    mode: ClassVar[TaggingMode] = TaggingMode.IMPLICIT
    value: AAREApdu


@dataclass
class RLRQApdu(ber.SequenceType):
    """RLRQ-apdu internal sequence"""
    components = (
        OptionalNamedType("reason", RequestReason),
        OptionalNamedType("user-information", AssociationInformation30),
    )
    @classmethod
    def from_components(
        cls,
        *,
        reason: Optional[RequestReason] = None,
        user_information: Optional[AssociationInformation30] = None,
    ) -> Self:
        """
        Create RLREApdu instance from named components.

        Returns:
            Self: New RLREApdu instance
        """
        return cls((
            reason,
            user_information,
        ))


@dataclass
class RLRQ(ber.TaggedType[RLRQApdu]):
    """[2] RLRQ-apdu"""
    tag: ClassVar[x690.Tag] = x690.Tag(
        class_=Class.APPLICATION,
        class_number=2,
        constructed=True
    )
    mode: ClassVar[TaggingMode] = TaggingMode.IMPLICIT
    value: RLRQApdu


@dataclass
class RLREApdu(ber.SequenceType):
    """RLRE-apdu internal sequence"""
    components = (
        OptionalNamedType("reason", ResponseReason),
        OptionalNamedType("user-information", AssociationInformation30),
    )

    @classmethod
    def from_components(
        cls,
        *,
        reason: Optional[ResponseReason] = None,
        user_information: Optional[AssociationInformation30] = None,
    ) -> Self:
        """
        Create RLREApdu instance from named components.

        Returns:
            Self: New RLREApdu instance
        """
        return cls((
            reason,
            user_information,
        ))


@dataclass
class RLRE(ber.TaggedType[RLREApdu]):
    """[3] RLRE-apdu"""
    tag: ClassVar[x690.Tag] = x690.Tag(
        class_=Class.APPLICATION,
        class_number=3,
        constructed=True
    )
    mode: ClassVar[TaggingMode] = TaggingMode.IMPLICIT
    value: RLREApdu


@dataclass
class ACSEApdu(ber.ChoiceType):
    """ACSE-APDU"""
    alternatives = create_alternatives(
        NamedType("aarq", AARQ),
        NamedType("aare", AARE),
        NamedType("rlrq", RLRQ),
        NamedType("rlre", RLRE)
    )
