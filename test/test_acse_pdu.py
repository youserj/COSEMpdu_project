"""
Unit tests for ACSE APDU types
Based on COSEMpdu_GB83.txt (Green Book 8.3)
"""
import unittest
from COSEMpdu.acse import (
    # Base types
    AARE,
    ApplicationContextName,
    APTitle,
    AEQualifier,
    APInvocationIdentifier,
    AEInvocationIdentifier,
    ACSERequirements,
    MechanismName,
    AuthenticationValue,
    ImplementationData,
    AssociationInformation,
    AssociationResult,
    AssociateSourceDiagnostic,
    ReleaseRequestReason,
    ReleaseResponseReason,
    ProtocolVersion,
    # Tagged types
    ApplicationContextName1,
   MechanismName9,
    CallingAuthenticationValue,
    ImplementationData29,
    AssociationInformation30,
    Result,
    ResultSourceDiagnostic,
    RequestReason,
    ResponseReason,
    ProtocolVersion0,
    # APDU types
    AARQApdu,
    AAREApdu,
    RLRQApdu,
    RLREApdu,
    ACSEApdu,
)
from COSEMpdu import x690
from COSEMpdu.x680.tagged_type import TaggingMode
from COSEMpdu.x680.tag import Class
from COSEMpdu.byte_buffer import ByteBuffer


class TestACSEBaseTypes(unittest.TestCase):
    """Test basic ACSE types"""

    def test_application_context_name(self) -> None:
        """Test ApplicationContextName (OBJECT IDENTIFIER)"""
        oid = ApplicationContextName((1, 2, 840, 10008, 1, 1))
        self.assertIsNotNone(oid)

    def test_ap_title(self) -> None:
        """Test APTitle (OCTET STRING)"""
        title = APTitle(b"\x01\x02\x03\x04")
        self.assertEqual(len(title), 4)

    def test_ae_qualifier(self) -> None:
        """Test AEQualifier (OCTET STRING)"""
        qualifier = AEQualifier(b"\x00\x01")
        self.assertEqual(len(qualifier), 2)

    def test_ap_invocation_identifier(self) -> None:
        """Test APInvocationIdentifier (INTEGER)"""
        identifier = APInvocationIdentifier(42)
        self.assertEqual(identifier.value, 42)

    def test_protocol_version(self) -> None:
        """Test ProtocolVersion (BIT STRING)"""
        version = ProtocolVersion((0,))  # version1
        self.assertEqual(version.value, (0,))

    def test_acse_requirements(self) -> None:
        """Test ACSERequirements (BIT STRING with named bits)"""
        requirements = ACSERequirements((1,))  # authentication bit set
        self.assertEqual(requirements.value, (1,))

    def test_association_result(self) -> None:
        """Test AssociationResult (ENUMERATED)"""
        accepted = AssociationResult(0)  # accepted
        rejected_permanent = AssociationResult(1)  # rejected-permanent
        rejected_transient = AssociationResult(2)  # rejected-transient
        self.assertEqual(accepted.value, 0)
        self.assertEqual(rejected_permanent.value, 1)
        self.assertEqual(rejected_transient.value, 2)


class TestTaggedTypes(unittest.TestCase):
    """Test TaggedType classes for ACSE fields"""

    def test_application_context_name_tagged(self) -> None:
        """Test ApplicationContextNameTagged configuration"""
        self.assertEqual(
            ApplicationContextName1.tag,
            x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=1)
        )
        self.assertEqual(
            ApplicationContextName1.mode,
            TaggingMode.DEFAULT
        )
        self.assertEqual(
            ApplicationContextName1.type_,
            ApplicationContextName
        )

    def test_ap_title_tagged(self) -> None:
        """Test APTitleTagged configuration"""
        self.assertEqual(
            APTitleTagged.tag,
            x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=2)
        )
        self.assertEqual(APTitleTagged.mode, TaggingMode.DEFAULT)
        self.assertEqual(APTitleTagged.type_, APTitle)

    def test_ae_qualifier_tagged(self) -> None:
        """Test AEQualifierTagged configuration"""
        self.assertEqual(
            AEQualifierTagged.tag,
            x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=3)
        )
        self.assertEqual(AEQualifierTagged.mode, TaggingMode.DEFAULT)
        self.assertEqual(AEQualifierTagged.type_, AEQualifier)

    def test_protocol_version_tagged(self) -> None:
        """Test ProtocolVersionTagged configuration"""
        self.assertEqual(
            ProtocolVersion0.tag,
            x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=0)
        )
        self.assertEqual(ProtocolVersion0.mode, TaggingMode.IMPLICIT)
        self.assertEqual(ProtocolVersion0.type_, ProtocolVersion)

    def test_acse_requirements_tagged(self) -> None:
        """Test ACSERequirementsTagged configuration"""
        self.assertEqual(
            ACSERequirementsTagged.tag,
            x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=10)
        )
        self.assertEqual(ACSERequirementsTagged.mode, TaggingMode.IMPLICIT)
        self.assertEqual(ACSERequirementsTagged.type_, ACSERequirements)

    def test_authentication_value_tagged(self) -> None:
        """Test AuthenticationValueTagged configuration"""
        self.assertEqual(
            CallingAuthenticationValue.tag,
            x690.Tag(class_=Class.CONTEXT_SPECIFIC, class_number=12)
        )
        self.assertEqual(CallingAuthenticationValue.mode, TaggingMode.EXPLICIT)
        self.assertEqual(CallingAuthenticationValue.type_, AuthenticationValue)


class TestAARQApdu(unittest.TestCase):
    """Test AARQ-apdu (Association Request)"""

    def test_from_components_minimal(self) -> None:
        """Test AARQApdu.from_components with minimal required fields"""
        app_context = ApplicationContextName1(ApplicationContextName((1, 2, 840, 10008, 1, 1)))

        aarq = AARQApdu.from_components(
            application_context_name=app_context
        )

        self.assertIsNotNone(aarq)
        # Check default protocol version is set
        self.assertEqual(aarq.value[0].value, ProtocolVersion((0,)))

    def test_from_components_with_optional_fields(self) -> None:
        """Test AARQApdu.from_components with optional fields"""
        app_context = ApplicationContextName1(ApplicationContextName((1, 2, 840, 10008, 1, 1)))
        called_title = APTitleTagged(APTitle(b"\x01\x02\x03\x04"))
        calling_title = APTitleTagged(APTitle(b"\x05\x06\x07\x08"))

        aarq = AARQApdu.from_components(
            application_context_name=app_context,
            called_ap_title=called_title,
            calling_ap_title=calling_title,
        )

        self.assertIsNotNone(aarq)
        self.assertEqual(aarq.value[1], app_context)
        self.assertEqual(aarq.value[2], called_title)
        self.assertEqual(aarq.value[6], calling_title)

    def test_from_components_with_custom_protocol_version(self) -> None:
        """Test AARQApdu.from_components with custom protocol version"""
        app_context = ApplicationContextName1(ApplicationContextName((1, 2, 840, 10008, 1, 1)))
        custom_version = ProtocolVersion0(ProtocolVersion((0, 1)))

        aarq = AARQApdu.from_components(
            protocol_version=custom_version,
            application_context_name=app_context
        )

        self.assertEqual(aarq.value[0], custom_version)

    def test_from_components_all_fields(self) -> None:
        """Test AARQApdu.from_components with all fields"""
        aarq = AARQApdu.from_components(
            protocol_version=ProtocolVersion0(ProtocolVersion((0,))),
            application_context_name=ApplicationContextName1(
                ApplicationContextName((1, 2, 840, 10008, 1, 1))
            ),
            called_ap_title=APTitleTagged(APTitle(b"\x01\x02")),
            called_ae_qualifier=AEQualifierTagged(AEQualifier(b"\x03\x04")),
            called_ap_invocation_id=APInvocationIdentifierTagged(APInvocationIdentifier(1)),
            called_ae_invocation_id=AEInvocationIdentifierTagged(AEInvocationIdentifier(2)),
            calling_ap_title=APTitleTagged(APTitle(b"\x05\x06")),
            calling_ae_qualifier=AEQualifierTagged(AEQualifier(b"\x07\x08")),
            calling_ap_invocation_id=APInvocationIdentifierTagged(APInvocationIdentifier(3)),
            calling_ae_invocation_id=AEInvocationIdentifierTagged(AEInvocationIdentifier(4)),
            sender_acse_requirements=ACSERequirementsTagged(ACSERequirements((1,))),
            mechanism_name=MechanismName9(MechanismName((1, 2, 3))),
            calling_authentication_value=CallingAuthenticationValue(AuthenticationValue()),
            implementation_information=ImplementationData29(ImplementationData("test")),
            user_information=AssociationInformation30(AssociationInformation(b"\x00\x01")),
        )

        self.assertIsNotNone(aarq)
        self.assertEqual(len(aarq.value), 15)  # All 15 components

    def test_aarq_tagged_type_config(self) -> None:
        """Test AARQApdu TaggedType configuration"""
        self.assertEqual(
            AARQApdu.tag,
            x690.Tag(class_=Class.APPLICATION, class_number=0, constructed=True)
        )
        self.assertEqual(AARQApdu.mode, TaggingMode.IMPLICIT)


class TestAAREApdu(unittest.TestCase):
    """Test AARE-apdu (Association Response)"""

    def test_from_components_minimal(self) -> None:
        """Test AAREApdu.from_components with minimal required fields"""
        app_context = ApplicationContextName1(ApplicationContextName((1, 2, 840, 10008, 1, 1)))
        result = Result(AssociationResult(0))  # accepted
        diagnostic = ResultSourceDiagnostic(
            AssociateSourceDiagnostic()
        )

        aare = AAREApdu.from_components(
            application_context_name=app_context,
            result=result,
            result_source_diagnostic=diagnostic
        )

        self.assertIsNotNone(aare)
        self.assertEqual(aare.value[0], ProtocolVersion((0,)))  # default
        self.assertEqual(aare.value[1], app_context)
        self.assertEqual(aare.value[2], result)
        self.assertEqual(aare.value[3], diagnostic)

    def test_from_components_with_result_accepted(self) -> None:
        """Test AAREApdu with accepted result"""
        aare = AAREApdu.from_components(
            application_context_name=ApplicationContextName1(
                ApplicationContextName((1, 2, 840, 10008, 1, 1))
            ),
            result=Result(AssociationResult(0)),  # accepted
            result_source_diagnostic=ResultSourceDiagnostic(
                AssociateSourceDiagnostic()
            )
        )

        self.assertIsNotNone(aare)

    def test_from_components_with_result_rejected(self) -> None:
        """Test AAREApdu with rejected result"""
        aare = AAREApdu.from_components(
            application_context_name=ApplicationContextName1(
                ApplicationContextName((1, 2, 840, 10008, 1, 1))
            ),
            result=Result(AssociationResult(1)),  # rejected-permanent
            result_source_diagnostic=ResultSourceDiagnostic(
                AssociateSourceDiagnostic()
            )
        )

        self.assertIsNotNone(aare)

    def test_from_components_with_optional_fields(self) -> None:
        """Test AAREApdu with optional responding fields"""
        aare = AAREApdu.from_components(
            application_context_name=ApplicationContextName1(
                ApplicationContextName((1, 2, 840, 10008, 1, 1))
            ),
            result=Result(AssociationResult(0)),
            result_source_diagnostic=ResultSourceDiagnostic(
                AssociateSourceDiagnostic()
            ),
            responding_ap_title=APTitleTagged(APTitle(b"\x01\x02\x03")),
            responding_ae_qualifier=AEQualifierTagged(AEQualifier(b"\x04\x05")),
        )

        self.assertIsNotNone(aare)
        self.assertEqual(aare.value[4], APTitleTagged(APTitle(b"\x01\x02\x03")))
        self.assertEqual(aare.value[5], AEQualifierTagged(AEQualifier(b"\x04\x05")))

    def test_aare_tagged_type_config(self) -> None:
        """Test AAREApdu TaggedType configuration"""
        self.assertEqual(
            AAREApdu.tag,
            x690.Tag(class_=Class.APPLICATION, class_number=1, constructed=True)
        )
        self.assertEqual(AAREApdu.mode, TaggingMode.IMPLICIT)


class TestRLRQApdu(unittest.TestCase):
    """Test RLRQ-apdu (Release Request)"""

    def test_from_components_minimal(self) -> None:
        """Test RLRQApdu.from_components with no fields (all optional)"""
        rlrq = RLRQApdu.from_components()

        self.assertIsNotNone(rlrq)
        self.assertEqual(rlrq.value[0], None)  # reason is optional
        self.assertEqual(rlrq.value[1], None)  # user-information is optional

    def test_from_components_with_reason(self) -> None:
        """Test RLRQApdu with release reason"""
        rlrq = RLRQApdu.from_components(
            reason=RequestReason(ReleaseRequestReason(0))  # normal
        )

        self.assertIsNotNone(rlrq)
        self.assertEqual(rlrq.value[0], RequestReason(ReleaseRequestReason(0)))

    def test_from_components_with_user_info(self) -> None:
        """Test RLRQApdu with user information"""
        rlrq = RLRQApdu.from_components(
            user_information=AssociationInformation30(
                AssociationInformation(b"\x00\x01\x02")
            )
        )

        self.assertIsNotNone(rlrq)
        self.assertEqual(rlrq.value[1], AssociationInformation30(AssociationInformation(b"\x00\x01\x02")))


class TestRLREApdu(unittest.TestCase):
    """Test RLRE-apdu (Release Response)"""

    def test_from_components_minimal(self) -> None:
        """Test RLREApdu.from_components with no fields (all optional)"""
        rlre = RLREApdu.from_components()

        self.assertIsNotNone(rlre)
        self.assertEqual(rlre.value[0], None)  # reason is optional
        self.assertEqual(rlre.value[1], None)  # user-information is optional

    def test_from_components_with_reason(self) -> None:
        """Test RLREApdu with release reason"""
        rlre = RLREApdu.from_components(
            reason=ResponseReason(ReleaseResponseReason(0))  # normal
        )

        self.assertIsNotNone(rlre)
        self.assertEqual(rlre.value[0], ResponseReason(ReleaseResponseReason(0)))

    def test_from_components_with_not_finished(self) -> None:
        """Test RLREApdu with not-finished reason"""
        rlre = RLREApdu.from_components(
            reason=ResponseReason(ReleaseResponseReason(1))  # not-finished
        )

        self.assertIsNotNone(rlre)
        self.assertEqual(rlre.value[0], ResponseReason(ReleaseResponseReason(1)))


class TestACSEApdu(unittest.TestCase):
    """Test ACSE-APDU Choice type"""

    def test_acse_apdu_aarq(self) -> None:
        """Test ACSEApdu with AARQ alternative"""
        aarq = AARQApdu.from_components(
            application_context_name=ApplicationContextName1(
                ApplicationContextName((1, 2, 840, 10008, 1, 1))
            )
        )
        acse = ACSEApdu(aarq)
        self.assertIsNotNone(acse)

    def test_acse_apdu_aare(self) -> None:
        """Test ACSEApdu with AARE alternative"""
        aare = AAREApdu.from_components(
            application_context_name=ApplicationContextName1(
                ApplicationContextName((1, 2, 840, 10008, 1, 1))
            ),
            result=Result(AssociationResult(0)),
            result_source_diagnostic=ResultSourceDiagnostic(
                AssociateSourceDiagnostic()
            )
        )
        acse = ACSEApdu(aare)
        self.assertIsNotNone(acse)

    def test_acse_apdu_rlrq(self) -> None:
        """Test ACSEApdu with RLRQ alternative"""
        rlrq = RLRQApdu.from_components()
        acse = ACSEApdu(rlrq)
        self.assertIsNotNone(acse)

    def test_acse_apdu_rlre(self) -> None:
        """Test ACSEApdu with RLRE alternative"""
        rlre = RLREApdu.from_components()
        acse = ACSEApdu(rlre)
        self.assertIsNotNone(acse)


class TestEncodingDecoding(unittest.TestCase):
    """Test encoding and decoding of ACSE APDUs"""

    def test_aarq_encode_decode(self) -> None:
        """Test AARQApdu encoding and decoding"""
        # Create AARQ with minimal fields
        aarq = AARQApdu.from_components(
            application_context_name=ApplicationContextName1(
                ApplicationContextName((1, 2, 840, 10008, 1, 1))
            )
        )

        # Encode
        buffer = ByteBuffer.allocate(1024)
        encoded = aarq.encode(buffer)
        self.assertGreater(len(encoded), 0)

        # Decode
        decoded_buffer = ByteBuffer.wrap(encoded)
        decoded = AARQApdu.decode(decoded_buffer)
        self.assertIsNotNone(decoded)

    def test_aare_encode_decode(self) -> None:
        """Test AAREApdu encoding and decoding"""
        aare = AAREApdu.from_components(
            application_context_name=ApplicationContextName1(
                ApplicationContextName((1, 2, 840, 10008, 1, 1))
            ),
            result=Result(AssociationResult(0)),
            result_source_diagnostic=ResultSourceDiagnostic(
                AssociateSourceDiagnostic()
            )
        )

        # Encode
        buffer = ByteBuffer.allocate(1024)
        encoded = aare.encode(buffer)
        self.assertGreater(len(encoded), 0)

        # Decode
        decoded_buffer = ByteBuffer.wrap(encoded)
        decoded = AAREApdu.decode(decoded_buffer)
        self.assertIsNotNone(decoded)

    def test_rlrq_encode_decode(self) -> None:
        """Test RLRQApdu encoding and decoding"""
        rlrq = RLRQApdu.from_components(
            reason=RequestReason(ReleaseRequestReason(0))
        )

        # Encode
        buffer = ByteBuffer.allocate(512)
        encoded = rlrq.encode(buffer)
        self.assertGreater(len(encoded), 0)

        # Decode
        decoded_buffer = ByteBuffer.wrap(encoded)
        decoded = RLRQApdu.decode(decoded_buffer)
        self.assertIsNotNone(decoded)

    def test_rlre_encode_decode(self) -> None:
        """Test RLREApdu encoding and decoding"""
        rlre = RLREApdu.from_components(
            reason=ResponseReason(ReleaseResponseReason(0))
        )

        # Encode
        buffer = ByteBuffer.allocate(512)
        encoded = rlre.encode(buffer)
        self.assertGreater(len(encoded), 0)

        # Decode
        decoded_buffer = ByteBuffer.wrap(encoded)
        decoded = RLREApdu.decode(decoded_buffer)
        self.assertIsNotNone(decoded)


class TestTaggedTypeFields(unittest.TestCase):
    """Test that all SequenceType components use TaggedType fields"""

    def test_aarq_components_are_tagged(self) -> None:
        """Verify all AARQApdu components are TaggedType instances"""
        for component in AARQApdu.type_.components:
            # Each component type should be a TaggedType
            self.assertTrue(
                hasattr(component.type, "tag"),
                f"Component {component.identifier} should have tag attribute"
            )
            self.assertTrue(
                hasattr(component.type, "mode"),
                f"Component {component.identifier} should have mode attribute"
            )
            self.assertTrue(
                hasattr(component.type, "type_"),
                f"Component {component.identifier} should have type_ attribute"
            )

    def test_aare_components_are_tagged(self) -> None:
        """Verify all AAREApdu components are TaggedType instances"""
        for component in AARE.type_.components:
            self.assertTrue(hasattr(component.type, "tag"))
            self.assertTrue(hasattr(component.type, "mode"))
            self.assertTrue(hasattr(component.type, "type_"))

    def test_rlrq_components_are_tagged(self) -> None:
        """Verify all RLRQApdu components are TaggedType instances"""
        for component in RLRQApdu.type_.components:
            self.assertTrue(hasattr(component.type, "tag"))
            self.assertTrue(hasattr(component.type, "mode"))
            self.assertTrue(hasattr(component.type, "type_"))

    def test_rlre_components_are_tagged(self) -> None:
        """Verify all RLREApdu components are TaggedType instances"""
        for component in RLREApdu.type_.components:
            self.assertTrue(hasattr(component.type, "tag"))
            self.assertTrue(hasattr(component.type, "mode"))
            self.assertTrue(hasattr(component.type, "type_"))


class TestFromComponentsTypeAnnotations(unittest.TestCase):
    """Test from_components method type annotations"""

    def test_aarq_from_components_signature(self) -> None:
        """Test AARQApdu.from_components has correct signature"""
        import inspect
        sig = inspect.signature(AARQApdu.from_components)
        params = sig.parameters

        # Check required parameter
        self.assertIn("application_context_name", params)

        # Check optional parameters
        self.assertIn("protocol_version", params)
        self.assertIn("called_ap_title", params)
        self.assertIn("calling_ap_title", params)

    def test_aare_from_components_signature(self) -> None:
        """Test AAREApdu.from_components has correct signature"""
        import inspect
        sig = inspect.signature(AAREApdu.from_components)
        params = sig.parameters

        # Check required parameters
        self.assertIn("application_context_name", params)
        self.assertIn("result", params)
        self.assertIn("result_source_diagnostic", params)

    def test_rlrq_from_components_signature(self) -> None:
        """Test RLRQApdu.from_components has correct signature"""
        import inspect
        sig = inspect.signature(RLRQApdu.from_components)
        params = sig.parameters

        # All parameters should be optional
        self.assertIn("reason", params)
        self.assertIn("user_information", params)

    def test_rlre_from_components_signature(self) -> None:
        """Test RLREApdu.from_components has correct signature"""
        import inspect
        sig = inspect.signature(RLREApdu.from_components)
        params = sig.parameters

        # All parameters should be optional
        self.assertIn("reason", params)
        self.assertIn("user_information", params)


if __name__ == "__main__":
    unittest.main()
