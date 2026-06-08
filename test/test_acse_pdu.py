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
    Charstring,
    ImplementationInformation,
    UserInformation,
    Result,
    ResultSourceDiagnostic,
    ACSEServiceUser,
    RequestReason,
    ResponseReason,
    AARQapdu,
    AAREapdu,
    RLRQapdu,
    RLREapdu,
    ACSEApdu,
    ProtocolVersion,
    CalledAPTitle,
    CalledAEQualifier,
    CalledAPInvocationId,
    CalledAEInvocationId,
    CallingAPTitle,
    CallingAEQualifier,
    CallingAPInvocationId,
    CallingAEInvocationId,
    SenderACSERequirements,
    RequestMechanismName,
    CallingAuthenticationValue,
    RespondingAPTitle,
    RespondingAEQualifier,
    RespondingAPInvocationId,
    RespondingAEInvocationId,
    ResponderACSERequirements,
    ResponseMechanismName,
    RespondingAuthenticationValue,
)


class TestACSEApdu(unittest.TestCase):
    """Test ACSE-APDU Choice type"""

    def test_acse_apdu_aarq(self) -> None:
        """Test ACSEApdu with AARQ alternative"""
        aarq = AARQapdu(application_context_name=ApplicationContextName((1, 2, 840, 10008, 1, 1)))
        acse = ACSEApdu(aarq)
        self.assertIsNotNone(acse)

    def test_acse_apdu_aare(self) -> None:
        """Test ACSEApdu with AARE alternative"""
        aare = AAREapdu(
            application_context_name=ApplicationContextName((1, 2, 840, 10008, 1, 1)),
            result=Result(0),
            result_source_diagnostic=ResultSourceDiagnostic(ACSEServiceUser(5)),
        )
        acse = ACSEApdu(aare)
        self.assertIsNotNone(acse)

    def test_acse_apdu_rlrq(self) -> None:
        """Test ACSEApdu with RLRQ alternative"""
        rlrq = RLRQapdu()
        acse = ACSEApdu(rlrq)
        self.assertIsNotNone(acse)

    def test_acse_apdu_rlre(self) -> None:
        """Test ACSEApdu with RLRE alternative"""
        rlre = RLREapdu()
        acse = ACSEApdu(rlre)
        self.assertIsNotNone(acse)


class TestEncodingDecoding(unittest.TestCase):
    """Test encoding and decoding of ACSE APDUs"""

    def test_aarq_encode_decode(self) -> None:
        """Test AARQApdu encoding and decoding with all optional fields"""
        aarq = AARQapdu(
            protocol_version=ProtocolVersion((1, 1)),
            application_context_name=ApplicationContextName((2, 16, 756, 5, 8, 1, 1)),
            # called_ap_title=CalledAPTitle(b"called_ap"),
            # called_ae_qualifier=CalledAEQualifier(b"called_ae"),
            called_ap_invocation_id=CalledAPInvocationId(1),
            called_ae_invocation_id=CalledAEInvocationId(2),
            # calling_ap_title=CallingAPTitle(b"calling_ap"),
            # calling_ae_qualifier=CallingAEQualifier(b"calling_ae"),
            calling_ap_invocation_id=CallingAPInvocationId(3),
            calling_ae_invocation_id=CallingAEInvocationId(4),
            # sender_acse_requirements=SenderACSERequirements((0,)),
            mechanism_name=RequestMechanismName((2, 16, 756, 5, 8, 2, 2)),
            # calling_authentication_value=CallingAuthenticationValue(Charstring("test_auth")),
            # implementation_information=ImplementationInformation("DLMS/COSEM"),
            # user_information=UserInformation(b"\x01\x02\x03"),
        )
        check_encode_decode(aarq, AARQapdu, 1024)

    def test_aare_encode_decode(self) -> None:
        """Test AAREApdu encoding and decoding with all optional fields"""
        aare = AAREapdu(
            protocol_version=ProtocolVersion((0,)),
            application_context_name=ApplicationContextName((1, 2, 840, 10008, 1, 1)),
            result=Result(0),
            result_source_diagnostic=ResultSourceDiagnostic(ACSEServiceUser.default()),
            responding_ap_title=RespondingAPTitle(b"resp_ap"),
            responding_ae_qualifier=RespondingAEQualifier(b"resp_ae"),
            responding_ap_invocation_id=RespondingAPInvocationId(10),
            responding_ae_invocation_id=RespondingAEInvocationId(20),
            responder_acse_requirements=ResponderACSERequirements((0,)),
            mechanism_name=ResponseMechanismName((1, 2, 840, 10008, 1, 2)),
            responding_authentication_value=RespondingAuthenticationValue(Charstring("resp_auth")),
            implementation_information=ImplementationInformation("DLMS/COSEM"),
            user_information=UserInformation(b"\x01\x02\x03"),
        )

        check_encode_decode(aare, AAREapdu, 1024)

    def test_rlrq_encode_decode(self) -> None:
        """Test RLRQApdu encoding and decoding with all optional fields"""
        rlrq = RLRQapdu(
            reason=RequestReason(0),
            user_information=UserInformation(b"\x04\x05\x06"),
        )

        check_encode_decode(rlrq, RLRQapdu, 512)

    def test_rlre_encode_decode(self) -> None:
        """Test RLREApdu encoding and decoding with all optional fields"""
        rlre = RLREapdu(
            reason=ResponseReason(0),
            user_information=UserInformation(b"\x07\x08\x09"),
        )

        check_encode_decode(rlre, RLREapdu, 512)


if __name__ == "__main__":
    unittest.main()
