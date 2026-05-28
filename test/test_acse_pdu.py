"""
Unit tests for ACSE APDU types (Green Book 8.3).

Testing is based on the principle: encode/decode is the only
reliable way to verify the correctness of the entire chain:
    value -> packing in TaggedType -> BER encoding
    -> BER decoding -> TaggedType -> value.

This approach covers:
- correctness of context tags (class, number, constructed);
- tagging mode (IMPLICIT / EXPLICIT / DEFAULT);
- structure of SEQUENCE/CHOICE types (order of fields, optionality);
- correct coding of nested types.

Additionally, the CHOICE type ACSEApdu is checked — that all four
alternatives (AARQ, AARE, RLRQ, RLRE) are constructed without errors.

What is NOT tested here:
- static TaggedType attributes (tag, mode, class_number) — these are
  constants from acse.py, checking them duplicates the declaration;
- bare construction of base types (APTitle, AEQualifier, ...) — they
  are building blocks for APDU and are tested implicitly through
  encode/decode; separate tests for their instantiation are redundant
  because any defect in them will surface during the full cycle;
- meta-checks for the presence of attributes on components — redundant
  in the presence of encode/decode.
"""
import sys
sys.path.insert(0, "src")

import unittest
from test._utils import check_encode_decode

from COSEMpdu.acse import (
    ApplicationContextName,
    ApplicationContextName1,
    APTitle,
    AEQualifier,
    APInvocationIdentifier,
    AEInvocationIdentifier,
    ACSERequirements,
    MechanismName,
    Charstring,
    AuthenticationValue,
    ImplementationData,
    ImplementationData29,
    AssociationResult,
    AssociationInformation,
    AssociationInformation30,
    AssociateSourceDiagnostic,
    Result,
    ResultSourceDiagnostic,
    ServiceUser,
    ReleaseRequestReason,
    RequestReason,
    ReleaseResponseReason,
    ResponseReason,
    AARQApdu,
    AARQ,
    AAREApdu,
    AARE,
    RLRQApdu,
    RLRQ,
    RLREApdu,
    RLRE,
    ACSEApdu,
    ProtocolVersion,
    ProtocolVersion0,
    CalledAPTitle,
    CalledAEQualifier,
    CalledAPInvocationIdentifier,
    CalledAEInvocationIdentifier,
    CallingAPTitle,
    CallingAEQualifier,
    CallingAPInvocationIdentifier,
    CallingAEInvocationIdentifier,
    SenderACSERequirements,
    MechanismName11,
    CallingAuthenticationValue,
    RespondingAPTitle,
    RespondingAEQualifier,
    RespondingAPInvocationIdentifier,
    RespondingAEInvocationIdentifier,
    ResponderACSERequirements,
    MechanismName9,
    RespondingAuthenticationValue,
)
from COSEMpdu.ber import GraphicString


class TestACSEApdu(unittest.TestCase):
    """Test ACSE-APDU Choice type"""

    def test_acse_apdu_aarq(self) -> None:
        """Test ACSEApdu with AARQ alternative"""
        aarq = AARQApdu(
            application_context_name=ApplicationContextName1(
                ApplicationContextName((1, 2, 840, 10008, 1, 1))
            )
        )
        aarq_tagged = AARQ(aarq)
        acse = ACSEApdu(aarq_tagged)
        self.assertIsNotNone(acse)

    def test_acse_apdu_aare(self) -> None:
        """Test ACSEApdu with AARE alternative"""
        aare = AAREApdu(
            application_context_name=ApplicationContextName1(
                ApplicationContextName((1, 2, 840, 10008, 1, 1))
            ),
            result=Result(AssociationResult(0)),
            result_source_diagnostic=ResultSourceDiagnostic(
                AssociateSourceDiagnostic(ServiceUser.parse(5))
            ),
        )
        aare_tagged = AARE(aare)
        acse = ACSEApdu(aare_tagged)
        self.assertIsNotNone(acse)

    def test_acse_apdu_rlrq(self) -> None:
        """Test ACSEApdu with RLRQ alternative"""
        rlrq = RLRQApdu()
        rlrq_tagged = RLRQ(rlrq)
        acse = ACSEApdu(rlrq_tagged)
        self.assertIsNotNone(acse)

    def test_acse_apdu_rlre(self) -> None:
        """Test ACSEApdu with RLRE alternative"""
        rlre = RLREApdu()
        rlre_tagged = RLRE(rlre)
        acse = ACSEApdu(rlre_tagged)
        self.assertIsNotNone(acse)


class TestEncodingDecoding(unittest.TestCase):
    """Test encoding and decoding of ACSE APDUs"""

    def test_aarq_encode_decode(self) -> None:
        """Test AARQApdu encoding and decoding with all optional fields"""
        aarq = AARQApdu(
            protocol_version=ProtocolVersion0(ProtocolVersion((0,))),
            application_context_name=ApplicationContextName1(
                ApplicationContextName((1, 2, 840, 10008, 1, 1))
            ),
            called_ap_title=CalledAPTitle(APTitle(b"called_ap")),
            called_ae_qualifier=CalledAEQualifier(AEQualifier(b"called_ae")),
            called_ap_invocation_id=CalledAPInvocationIdentifier(APInvocationIdentifier(1)),
            called_ae_invocation_id=CalledAEInvocationIdentifier(AEInvocationIdentifier(2)),
            calling_ap_title=CallingAPTitle(APTitle(b"calling_ap")),
            calling_ae_qualifier=CallingAEQualifier(AEQualifier(b"calling_ae")),
            calling_ap_invocation_id=CallingAPInvocationIdentifier(APInvocationIdentifier(3)),
            calling_ae_invocation_id=CallingAEInvocationIdentifier(AEInvocationIdentifier(4)),
            sender_acse_requirements=SenderACSERequirements(ACSERequirements((0,))),
            mechanism_name=MechanismName11(MechanismName((1, 2, 840, 10008, 1, 2))),
            calling_authentication_value=CallingAuthenticationValue(
                AuthenticationValue(Charstring(GraphicString("test_auth")))
            ),
            implementation_information=ImplementationData29(ImplementationData("DLMS/COSEM")),
            user_information=AssociationInformation30(AssociationInformation(b"\x01\x02\x03")),
        )

        check_encode_decode(aarq, AARQApdu, 1024)

    def test_aare_encode_decode(self) -> None:
        """Test AAREApdu encoding and decoding with all optional fields"""
        aare = AAREApdu(
            protocol_version=ProtocolVersion0(ProtocolVersion((0,))),
            application_context_name=ApplicationContextName1(
                ApplicationContextName((1, 2, 840, 10008, 1, 1))
            ),
            result=Result(AssociationResult(0)),
            result_source_diagnostic=ResultSourceDiagnostic(
                AssociateSourceDiagnostic(ServiceUser.default())
            ),
            responding_ap_title=RespondingAPTitle(APTitle(b"resp_ap")),
            responding_ae_qualifier=RespondingAEQualifier(AEQualifier(b"resp_ae")),
            responding_ap_invocation_id=RespondingAPInvocationIdentifier(APInvocationIdentifier(10)),
            responding_ae_invocation_id=RespondingAEInvocationIdentifier(AEInvocationIdentifier(20)),
            responder_acse_requirements=ResponderACSERequirements(ACSERequirements((0,))),
            mechanism_name=MechanismName9(MechanismName((1, 2, 840, 10008, 1, 2))),
            responding_authentication_value=RespondingAuthenticationValue(
                AuthenticationValue(Charstring(GraphicString("resp_auth")))
            ),
            implementation_information=ImplementationData29(ImplementationData("DLMS/COSEM")),
            user_information=AssociationInformation30(AssociationInformation(b"\x01\x02\x03")),
        )

        check_encode_decode(aare, AAREApdu, 1024)

    def test_rlrq_encode_decode(self) -> None:
        """Test RLRQApdu encoding and decoding with all optional fields"""
        rlrq = RLRQApdu(
            reason=RequestReason(ReleaseRequestReason(0)),
            user_information=AssociationInformation30(AssociationInformation(b"\x04\x05\x06")),
        )

        check_encode_decode(rlrq, RLRQApdu, 512)

    def test_rlre_encode_decode(self) -> None:
        """Test RLREApdu encoding and decoding with all optional fields"""
        rlre = RLREApdu(
            reason=ResponseReason(ReleaseResponseReason(0)),
            user_information=AssociationInformation30(AssociationInformation(b"\x07\x08\x09")),
        )

        check_encode_decode(rlre, RLREApdu, 512)


if __name__ == "__main__":
    unittest.main()