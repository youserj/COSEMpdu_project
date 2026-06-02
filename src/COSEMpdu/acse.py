"""
COSEM PDU Types Implementation
Based on COSEMpdu_GB83.txt (Green Book 8.3)
Implements A-XDR encoding/decoding according to IEC 61334-6 ACSE APDU Types (COSEMpdu_GB83
"""
from dataclasses import dataclass
from typing import ClassVar, Optional
from . import x690
from .x680 import (
    NamedType,
    TaggingMode,
    NamedBitList,
    NamedBit,
    NamedNumberList,
    NamedNumber
)
from . import ber
from .x680.tag import Class
from .ber import create_alternatives, ImplicitTaggedType, GraphicString, BitStringType, IntegerType, SequenceType


class ApplicationContextName(ber.ObjectIdentifierType):
    """Application-context-name"""


class ApplicationContextName1(ber.TaggedType[ApplicationContextName]):
    """[1] Application-context-name"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=1)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class APTitle(ber.OctetStringType):
    """AP-title"""


class AEQualifier(ber.OctetStringType):
    """AE-qualifier"""


class APInvocationIdentifier(ber.IntegerType):
    """AP-invocation-identifier"""


class AEInvocationIdentifier(ber.IntegerType):
    """AE-invocation-identifier"""


class ACSERequirements(BitStringType):
    """ACSE-requirements"""
    named_bits = NamedBitList((NamedBit("authentication", 0),))


class MechanismName(ber.ObjectIdentifierType):
    """Mechanism-name"""


class Charstring(ImplicitTaggedType, GraphicString):
    """charstring [0] IMPLICIT GraphicString"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=0)


class BitString(ImplicitTaggedType, BitStringType):
    """bitstring [1] IMPLICIT BIT STRING"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=1)


class AuthenticationValue(ber.ChoiceType):
    """Authentication-value"""
    alternatives = ber.create_alternatives(
        NamedType("charstring", Charstring),
        NamedType("bitstring", BitString)
    )
    value: Charstring | BitString


class ImplementationInformation(ImplicitTaggedType, GraphicString):
    """implementation-information [29] IMPLICIT Implementation-data"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=29)


class AssociationInformation(ber.OctetStringType):
    """Association-information"""


class UserInformation(ber.TaggedType[AssociationInformation]):
    """[30] EXPLICIT Association-information"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=30)
    mode: ClassVar[TaggingMode] = TaggingMode.EXPLICIT


class AssociationResult(ber.IntegerType):
    """Association-result"""
    named_numbers = NamedNumberList((
        NamedNumber("accepted", 0),
        NamedNumber("rejected-permanent", 1),
        NamedNumber("rejected-transient", 2),
    ))


class Result(ber.TaggedType[AssociationResult]):
    """[2] Association-result"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=2)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


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


class ServiceUser(ber.TaggedType[AcseServiceUser]):
    """[1] acse-service-user"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=1)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class AcseServiceProvider(ber.IntegerType):
    """acse-service-provider"""
    named_numbers = NamedNumberList((
        NamedNumber("null", 0),
        NamedNumber("no-reason-given", 1),
        NamedNumber("no-common-acse-version", 2),
    ))


class Provider(ber.TaggedType[AcseServiceProvider]):
    """[2] acse-service-provider"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=2)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class AssociateSourceDiagnostic(ber.ChoiceType):
    """Associate-source-diagnostic"""
    alternatives = create_alternatives(
        NamedType("acse-service-user", ServiceUser),
        NamedType("acse-service-provider", Provider)
    )


class ResultSourceDiagnostic(ber.TaggedType[AssociateSourceDiagnostic]):
    """[3] Associate-source-diagnostic"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=3)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class RequestReason(ImplicitTaggedType, IntegerType):
    """reason [0] IMPLICIT Release-request-reason"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=0)
    named_numbers = NamedNumberList((
        NamedNumber("normal", 0),
        NamedNumber("urgent", 1),
        NamedNumber("user-defined", 30),
    ))


class ResponseReason(ImplicitTaggedType, IntegerType):
    """reason [0] IMPLICIT Release-response-reason"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=0)
    named_numbers = NamedNumberList((
        NamedNumber("normal", 0),
        NamedNumber("not-finished", 1),
        NamedNumber("user-defined", 30),
    ))


class ProtocolVersion(ImplicitTaggedType, BitStringType):
    """protocol-version [0] IMPLICIT BIT STRING {version1 (0)}"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=0)
    named_bits = NamedBitList((NamedBit("version1", 0),))


DEFAULT_PROTOCOL_VERSION = ProtocolVersion((0,))


class CalledAPTitle(ber.TaggedType[APTitle]):
    """[2] AP-title"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=2)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class CallingAPTitle(ber.TaggedType[APTitle]):
    """[6] AP-title"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=6)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class CalledAEQualifier(ber.TaggedType[AEQualifier]):
    """[3] AE-qualifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=3)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class CallingAEQualifier(ber.TaggedType[AEQualifier]):
    """[7] AE-qualifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=7)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class CalledAPInvocationIdentifier(ber.TaggedType[APInvocationIdentifier]):
    """[4] AP-invocation-identifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=4)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class CallingAPInvocationIdentifier(ber.TaggedType[APInvocationIdentifier]):
    """[8] AP-invocation-identifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=8)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class CalledAEInvocationIdentifier(ber.TaggedType[AEInvocationIdentifier]):
    """[5] AE-invocation-identifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=5)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class CallingAEInvocationIdentifier(ber.TaggedType[AEInvocationIdentifier]):
    """[9] AE-invocation-identifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=9)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class SenderACSERequirements(ImplicitTaggedType, ACSERequirements):
    """sender-acse-requirements [10] IMPLICIT ACSE-requirements"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=10)


class RequestMechanismName(ImplicitTaggedType, MechanismName):
    """mechanism-name [11] IMPLICIT Mechanism-name"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=11)


class CallingAuthenticationValue(ber.TaggedType[AuthenticationValue]):
    """[12] EXPLICIT Authentication-value"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=12)
    mode: ClassVar[TaggingMode] = TaggingMode.EXPLICIT


class AARQapdu(ImplicitTaggedType, SequenceType):
    """AARQ-apdu ::= [APPLICATION 0] IMPLICIT SEQUENCE"""
    tag: ClassVar[x690.Tag] = x690.Tag(
        class_=Class.APPLICATION,
        class_number=0,
        constructed=True)
    protocol_version: ProtocolVersion = DEFAULT_PROTOCOL_VERSION
    application_context_name: ApplicationContextName1
    called_ap_title: Optional[CalledAPTitle]
    called_ae_qualifier: Optional[CalledAEQualifier]
    called_ap_invocation_id: Optional[CalledAPInvocationIdentifier]
    called_ae_invocation_id: Optional[CalledAEInvocationIdentifier]
    calling_ap_title: Optional[CallingAPTitle]
    calling_ae_qualifier: Optional[CallingAEQualifier]
    calling_ap_invocation_id: Optional[CallingAPInvocationIdentifier]
    calling_ae_invocation_id: Optional[CallingAEInvocationIdentifier]
    sender_acse_requirements: Optional[SenderACSERequirements]
    mechanism_name: Optional[RequestMechanismName]
    calling_authentication_value: Optional[CallingAuthenticationValue]
    implementation_information: Optional[ImplementationInformation]
    user_information: Optional[UserInformation]

    def __init__(
        self,
        *,
        protocol_version: ProtocolVersion = DEFAULT_PROTOCOL_VERSION,
        application_context_name: ApplicationContextName1,
        called_ap_title: Optional[CalledAPTitle] = None,
        called_ae_qualifier: Optional[CalledAEQualifier] = None,
        called_ap_invocation_id: Optional[CalledAPInvocationIdentifier] = None,
        called_ae_invocation_id: Optional[CalledAEInvocationIdentifier] = None,
        calling_ap_title: Optional[CallingAPTitle] = None,
        calling_ae_qualifier: Optional[CallingAEQualifier] = None,
        calling_ap_invocation_id: Optional[CallingAPInvocationIdentifier] = None,
        calling_ae_invocation_id: Optional[CallingAEInvocationIdentifier] = None,
        sender_acse_requirements: Optional[SenderACSERequirements] = None,
        mechanism_name: Optional[RequestMechanismName] = None,
        calling_authentication_value: Optional[CallingAuthenticationValue] = None,
        implementation_information: Optional[ImplementationInformation] = None,
        user_information: Optional[UserInformation] = None,
    ) -> None:
        self.protocol_version = protocol_version
        self.application_context_name = application_context_name
        self.called_ap_title = called_ap_title
        self.called_ae_qualifier = called_ae_qualifier
        self.called_ap_invocation_id = called_ap_invocation_id
        self.called_ae_invocation_id = called_ae_invocation_id
        self.calling_ap_title = calling_ap_title
        self.calling_ae_qualifier = calling_ae_qualifier
        self.calling_ap_invocation_id = calling_ap_invocation_id
        self.calling_ae_invocation_id = calling_ae_invocation_id
        self.sender_acse_requirements = sender_acse_requirements
        self.mechanism_name = mechanism_name
        self.calling_authentication_value = calling_authentication_value
        self.implementation_information = implementation_information
        self.user_information = user_information


class RespondingAPTitle(ber.TaggedType[APTitle]):
    """[4] AP-title"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=4)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class RespondingAEQualifier(ber.TaggedType[AEQualifier]):
    """[5] AE-qualifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=5)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class RespondingAPInvocationIdentifier(ber.TaggedType[APInvocationIdentifier]):
    """[6] AP-invocation-identifier tagged"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=6)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class RespondingAEInvocationIdentifier(ber.TaggedType[AEInvocationIdentifier]):
    """[7] AE-invocation-identifier"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=7)
    mode: ClassVar[TaggingMode] = TaggingMode.DEFAULT


class ResponderACSERequirements(ImplicitTaggedType, ACSERequirements):
    """responder-acse-requirements [8] IMPLICIT ACSE-requirements tagged"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=8)


class ResponseMechanismName(ImplicitTaggedType, MechanismName):
    """mechanism-name [9] IMPLICIT Mechanism-name"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=9)


class RespondingAuthenticationValue(ber.TaggedType[AuthenticationValue]):
    """[11] EXPLICIT Authentication-value"""
    tag: ClassVar[x690.Tag] = x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=11)
    mode: ClassVar[TaggingMode] = TaggingMode.EXPLICIT


class AAREapdu(ImplicitTaggedType, SequenceType):
    """AARE-apdu ::= [APPLICATION 1] IMPLICIT SEQUENCE"""
    tag: ClassVar[x690.Tag] = x690.Tag(
        class_=Class.APPLICATION,
        class_number=1,
        constructed=True)
    protocol_version: ProtocolVersion = DEFAULT_PROTOCOL_VERSION
    application_context_name: ApplicationContextName1
    result: Result
    result_source_diagnostic: ResultSourceDiagnostic
    responding_ap_title: Optional[RespondingAPTitle]
    responding_ae_qualifier: Optional[RespondingAEQualifier]
    responding_ap_invocation_id: Optional[RespondingAPInvocationIdentifier]
    responding_ae_invocation_id: Optional[RespondingAEInvocationIdentifier]
    responder_acse_requirements: Optional[ResponderACSERequirements]
    mechanism_name: Optional[ResponseMechanismName]
    responding_authentication_value: Optional[RespondingAuthenticationValue]
    implementation_information: Optional[ImplementationInformation]
    user_information: Optional[UserInformation]

    def __init__(
        self,
        *,
        protocol_version: ProtocolVersion = DEFAULT_PROTOCOL_VERSION,
        application_context_name: ApplicationContextName1,
        result: Result,
        result_source_diagnostic: ResultSourceDiagnostic,
        responding_ap_title: Optional[RespondingAPTitle] = None,
        responding_ae_qualifier: Optional[RespondingAEQualifier] = None,
        responding_ap_invocation_id: Optional[RespondingAPInvocationIdentifier] = None,
        responding_ae_invocation_id: Optional[RespondingAEInvocationIdentifier] = None,
        responder_acse_requirements: Optional[ResponderACSERequirements] = None,
        mechanism_name: Optional[ResponseMechanismName] = None,
        responding_authentication_value: Optional[RespondingAuthenticationValue] = None,
        implementation_information: Optional[ImplementationInformation] = None,
        user_information: Optional[UserInformation] = None,
    ) -> None:
        self.protocol_version = protocol_version
        self.application_context_name = application_context_name
        self.result = result
        self.result_source_diagnostic = result_source_diagnostic
        self.responding_ap_title = responding_ap_title
        self.responding_ae_qualifier = responding_ae_qualifier
        self.responding_ap_invocation_id = responding_ap_invocation_id
        self.responding_ae_invocation_id = responding_ae_invocation_id
        self.responder_acse_requirements = responder_acse_requirements
        self.mechanism_name = mechanism_name
        self.responding_authentication_value = responding_authentication_value
        self.implementation_information = implementation_information
        self.user_information = user_information


@dataclass
class RLRQapdu(ImplicitTaggedType, SequenceType):
    """RLRQ-apdu ::= [APPLICATION 2] IMPLICIT SEQUENCE"""
    tag: ClassVar[x690.Tag] = x690.Tag(
        class_=Class.APPLICATION,
        class_number=2,
        constructed=True)
    reason: Optional[RequestReason] = None
    user_information: Optional[UserInformation] = None


@dataclass
class RLREapdu(ImplicitTaggedType, SequenceType):
    """RLRE-apdu ::= [APPLICATION 3] IMPLICIT SEQUENCE"""
    tag: ClassVar[x690.Tag] = x690.Tag(
        class_=Class.APPLICATION,
        class_number=3,
        constructed=True)
    reason: Optional[ResponseReason] = None
    user_information: Optional[UserInformation] = None


class ACSEApdu(ber.ChoiceType):
    """ACSE-APDU"""
    alternatives = create_alternatives(
        NamedType("aarq", AARQapdu),
        NamedType("aare", AAREapdu),
        NamedType("rlrq", RLRQapdu),
        NamedType("rlre", RLREapdu)
    )
