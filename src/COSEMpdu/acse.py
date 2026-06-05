"""
COSEM PDU Types Implementation
Based on COSEMpdu_GB83.txt (Green Book 8.3)
Implements A-XDR encoding/decoding according to IEC 61334-6 ACSE APDU Types (COSEMpdu_GB83
"""
from dataclasses import dataclass
from typing import ClassVar, Optional
from . import x690
from .x680 import NamedBitList, NamedBit, NamedNumberList, NamedNumber
from .x680.tag import Class
from .ber import ImplicitTaggedType, GraphicString, BitStringType, IntegerType, SequenceType, ExplicitTaggedType, OctetStringType, ChoiceType, ObjectIdentifierType


class ApplicationContextName(ExplicitTaggedType, ObjectIdentifierType):
    """application-context-name [1] Application-context-name"""
    tag2: ClassVar[x690.Tag] = x690.Tag(1, Class.CONTEXT_SPECIFIC, True)


class APTitle(OctetStringType):
    """AP-title"""


class AEQualifier(OctetStringType):
    """AE-qualifier"""


class APInvocationIdentifier(IntegerType):
    """AP-invocation-identifier"""


class AEInvocationIdentifier(IntegerType):
    """AE-invocation-identifier"""


class ACSERequirements(BitStringType):
    """ACSE-requirements"""
    named_bits = NamedBitList((NamedBit("authentication", 0),))


class MechanismName(ObjectIdentifierType):
    """Mechanism-name"""


class Charstring(ImplicitTaggedType, GraphicString):
    """charstring [0] IMPLICIT GraphicString"""
    tag: ClassVar[x690.Tag] = x690.Tag(0, Class.CONTEXT_SPECIFIC)


class BitString(ImplicitTaggedType, BitStringType):
    """bitstring [1] IMPLICIT BIT STRING"""
    tag: ClassVar[x690.Tag] = x690.Tag(1, Class.CONTEXT_SPECIFIC)


class AuthenticationValue(ChoiceType):
    """Authentication-value"""
    value: Charstring | BitString


class ImplementationInformation(ImplicitTaggedType, GraphicString):
    """implementation-information [29] IMPLICIT Implementation-data"""
    tag: ClassVar[x690.Tag] = x690.Tag(29, Class.CONTEXT_SPECIFIC)


class UserInformation(ExplicitTaggedType, OctetStringType):
    """user-information [30] EXPLICIT Association-information"""
    tag2: ClassVar[x690.Tag] = x690.Tag(30, Class.CONTEXT_SPECIFIC, True)


class Result(ExplicitTaggedType, IntegerType):
    """result [2] Association-result"""
    tag2: ClassVar[x690.Tag] = x690.Tag(2, Class.CONTEXT_SPECIFIC, True)
    named_numbers = NamedNumberList((
        NamedNumber("accepted", 0),
        NamedNumber("rejected-permanent", 1),
        NamedNumber("rejected-transient", 2),
    ))


class ACSEServiceUser(ExplicitTaggedType, IntegerType):
    """acse-service-user [1] INTEGER"""
    tag2: ClassVar[x690.Tag] = x690.Tag(1, Class.CONTEXT_SPECIFIC, True)
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


class ACSEServiceProvider(ExplicitTaggedType, IntegerType):
    """acse-service-provider [2] INTEGER"""
    tag2: ClassVar[x690.Tag] = x690.Tag(2, Class.CONTEXT_SPECIFIC, True)
    named_numbers = NamedNumberList((
        NamedNumber("null", 0),
        NamedNumber("no-reason-given", 1),
        NamedNumber("no-common-acse-version", 2),
    ))


class ResultSourceDiagnostic(ExplicitTaggedType, ChoiceType):
    """result-source-diagnostic [3] Associate-source-diagnostic"""
    tag2: ClassVar[x690.Tag] = x690.Tag(3, Class.CONTEXT_SPECIFIC, True)
    value: ACSEServiceUser | ACSEServiceProvider


class RequestReason(ImplicitTaggedType, IntegerType):
    """reason [0] IMPLICIT Release-request-reason"""
    tag: ClassVar[x690.Tag] = x690.Tag(0, Class.CONTEXT_SPECIFIC)
    named_numbers = NamedNumberList((
        NamedNumber("normal", 0),
        NamedNumber("urgent", 1),
        NamedNumber("user-defined", 30),
    ))


class ResponseReason(ImplicitTaggedType, IntegerType):
    """reason [0] IMPLICIT Release-response-reason"""
    tag: ClassVar[x690.Tag] = x690.Tag(0, Class.CONTEXT_SPECIFIC)
    named_numbers = NamedNumberList((
        NamedNumber("normal", 0),
        NamedNumber("not-finished", 1),
        NamedNumber("user-defined", 30),
    ))


class ProtocolVersion(ImplicitTaggedType, BitStringType):
    """protocol-version [0] IMPLICIT BIT STRING {version1 (0)}"""
    tag: ClassVar[x690.Tag] = x690.Tag(0, Class.CONTEXT_SPECIFIC)
    named_bits = NamedBitList((NamedBit("version1", 0),))


DEFAULT_PROTOCOL_VERSION = ProtocolVersion((0,))


class CalledAPTitle(ExplicitTaggedType, APTitle):
    """called-AP-title [2] AP-title"""
    tag2: ClassVar[x690.Tag] = x690.Tag(2, Class.CONTEXT_SPECIFIC, True)


class CallingAPTitle(ExplicitTaggedType, APTitle):
    """calling-AP-title [6] AP-title"""
    tag2: ClassVar[x690.Tag] = x690.Tag(6, Class.CONTEXT_SPECIFIC, True)


class CalledAEQualifier(ExplicitTaggedType, AEQualifier):
    """called-AE-qualifier [3] AE-qualifier"""
    tag2: ClassVar[x690.Tag] = x690.Tag(3, Class.CONTEXT_SPECIFIC, True)


class CallingAEQualifier(ExplicitTaggedType, AEQualifier):
    """calling-AE-qualifier [7] AE-qualifier"""
    tag2: ClassVar[x690.Tag] = x690.Tag(7, Class.CONTEXT_SPECIFIC, True)


class CalledAPInvocationId(ExplicitTaggedType, APInvocationIdentifier):
    """called-AP-invocation-id [4] AP-invocation-identifier"""
    tag2: ClassVar[x690.Tag] = x690.Tag(4, Class.CONTEXT_SPECIFIC, True)


class CallingAPInvocationId(ExplicitTaggedType, APInvocationIdentifier):
    """calling-AP-invocation-id [8] AP-invocation-identifier"""
    tag2: ClassVar[x690.Tag] = x690.Tag(8, Class.CONTEXT_SPECIFIC, True)


class CalledAEInvocationId(ExplicitTaggedType, AEInvocationIdentifier):
    """called-AE-invocation-id [5] AE-invocation-identifier"""
    tag2: ClassVar[x690.Tag] = x690.Tag(5, Class.CONTEXT_SPECIFIC, True)


class CallingAEInvocationId(ExplicitTaggedType, AEInvocationIdentifier):
    """calling-AE-invocation-id [9] AE-invocation-identifier"""
    tag2: ClassVar[x690.Tag] = x690.Tag(9, Class.CONTEXT_SPECIFIC, True)


class SenderACSERequirements(ImplicitTaggedType, ACSERequirements):
    """sender-acse-requirements [10] IMPLICIT ACSE-requirements"""
    tag: ClassVar[x690.Tag] = x690.Tag(10, Class.CONTEXT_SPECIFIC)


class RequestMechanismName(ImplicitTaggedType, MechanismName):
    """mechanism-name [11] IMPLICIT Mechanism-name"""
    tag: ClassVar[x690.Tag] = x690.Tag(11, Class.CONTEXT_SPECIFIC)


class CallingAuthenticationValue(ExplicitTaggedType, AuthenticationValue):
    """calling-authentication-value [12] EXPLICIT Authentication-value"""
    tag2: ClassVar[x690.Tag] = x690.Tag(12, Class.CONTEXT_SPECIFIC, True)


class AARQapdu(ImplicitTaggedType, SequenceType):
    """AARQ-apdu ::= [APPLICATION 0] IMPLICIT SEQUENCE"""
    tag: ClassVar[x690.Tag] = x690.Tag(0, Class.APPLICATION, constructed=True)
    protocol_version: ProtocolVersion = DEFAULT_PROTOCOL_VERSION
    application_context_name: ApplicationContextName
    called_ap_title: Optional[CalledAPTitle]
    called_ae_qualifier: Optional[CalledAEQualifier]
    called_ap_invocation_id: Optional[CalledAPInvocationId]
    called_ae_invocation_id: Optional[CalledAEInvocationId]
    calling_ap_title: Optional[CallingAPTitle]
    calling_ae_qualifier: Optional[CallingAEQualifier]
    calling_ap_invocation_id: Optional[CallingAPInvocationId]
    calling_ae_invocation_id: Optional[CallingAEInvocationId]
    sender_acse_requirements: Optional[SenderACSERequirements]
    mechanism_name: Optional[RequestMechanismName]
    calling_authentication_value: Optional[CallingAuthenticationValue]
    implementation_information: Optional[ImplementationInformation]
    user_information: Optional[UserInformation]

    def __init__(
        self,
        *,
        protocol_version: ProtocolVersion = DEFAULT_PROTOCOL_VERSION,
        application_context_name: ApplicationContextName,
        called_ap_title: Optional[CalledAPTitle] = None,
        called_ae_qualifier: Optional[CalledAEQualifier] = None,
        called_ap_invocation_id: Optional[CalledAPInvocationId] = None,
        called_ae_invocation_id: Optional[CalledAEInvocationId] = None,
        calling_ap_title: Optional[CallingAPTitle] = None,
        calling_ae_qualifier: Optional[CallingAEQualifier] = None,
        calling_ap_invocation_id: Optional[CallingAPInvocationId] = None,
        calling_ae_invocation_id: Optional[CallingAEInvocationId] = None,
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


class RespondingAPTitle(ExplicitTaggedType, APTitle):
    """responding-AP-title [4] AP-title"""
    tag2: ClassVar[x690.Tag] = x690.Tag(4, Class.CONTEXT_SPECIFIC, True)


class RespondingAEQualifier(ExplicitTaggedType, AEQualifier):
    """responding-AE-qualifier [5] AE-qualifier"""
    tag2: ClassVar[x690.Tag] = x690.Tag(5, Class.CONTEXT_SPECIFIC, True)


class RespondingAPInvocationId(ExplicitTaggedType, APInvocationIdentifier):
    """responding-AP-invocation-id [6] AP-invocation-identifier tagged"""
    tag2: ClassVar[x690.Tag] = x690.Tag(6, Class.CONTEXT_SPECIFIC, True)


class RespondingAEInvocationId(ExplicitTaggedType, AEInvocationIdentifier):
    """responding-AE-invocation-id [7] AE-invocation-identifier"""
    tag2: ClassVar[x690.Tag] = x690.Tag(7, Class.CONTEXT_SPECIFIC, True)


class ResponderACSERequirements(ImplicitTaggedType, ACSERequirements):
    """responder-acse-requirements [8] IMPLICIT ACSE-requirements tagged"""
    tag: ClassVar[x690.Tag] = x690.Tag(8, Class.CONTEXT_SPECIFIC)


class ResponseMechanismName(ImplicitTaggedType, MechanismName):
    """mechanism-name [9] IMPLICIT Mechanism-name"""
    tag: ClassVar[x690.Tag] = x690.Tag(9, Class.CONTEXT_SPECIFIC)


class RespondingAuthenticationValue(ExplicitTaggedType, AuthenticationValue):
    """responding-authentication-value [10] EXPLICIT Authentication-value"""
    tag2: ClassVar[x690.Tag] = x690.Tag(10, Class.CONTEXT_SPECIFIC, True)


class AAREapdu(ImplicitTaggedType, SequenceType):
    """AARE-apdu ::= [APPLICATION 1] IMPLICIT SEQUENCE"""
    tag: ClassVar[x690.Tag] = x690.Tag(1, Class.APPLICATION, True)
    protocol_version: ProtocolVersion = DEFAULT_PROTOCOL_VERSION
    application_context_name: ApplicationContextName
    result: Result
    result_source_diagnostic: ResultSourceDiagnostic
    responding_ap_title: Optional[RespondingAPTitle]
    responding_ae_qualifier: Optional[RespondingAEQualifier]
    responding_ap_invocation_id: Optional[RespondingAPInvocationId]
    responding_ae_invocation_id: Optional[RespondingAEInvocationId]
    responder_acse_requirements: Optional[ResponderACSERequirements]
    mechanism_name: Optional[ResponseMechanismName]
    responding_authentication_value: Optional[RespondingAuthenticationValue]
    implementation_information: Optional[ImplementationInformation]
    user_information: Optional[UserInformation]

    def __init__(
        self,
        *,
        protocol_version: ProtocolVersion = DEFAULT_PROTOCOL_VERSION,
        application_context_name: ApplicationContextName,
        result: Result,
        result_source_diagnostic: ResultSourceDiagnostic,
        responding_ap_title: Optional[RespondingAPTitle] = None,
        responding_ae_qualifier: Optional[RespondingAEQualifier] = None,
        responding_ap_invocation_id: Optional[RespondingAPInvocationId] = None,
        responding_ae_invocation_id: Optional[RespondingAEInvocationId] = None,
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
    tag: ClassVar[x690.Tag] = x690.Tag(2, Class.APPLICATION, True)
    reason: Optional[RequestReason] = None
    user_information: Optional[UserInformation] = None


@dataclass
class RLREapdu(ImplicitTaggedType, SequenceType):
    """RLRE-apdu ::= [APPLICATION 3] IMPLICIT SEQUENCE"""
    tag: ClassVar[x690.Tag] = x690.Tag(3, Class.APPLICATION, True)
    reason: Optional[ResponseReason] = None
    user_information: Optional[UserInformation] = None


class ACSEApdu(ChoiceType):
    """ACSE-APDU"""
    value: AARQapdu | AAREapdu | RLRQapdu | RLREapdu
