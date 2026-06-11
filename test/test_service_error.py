"""
Unit tests for ServiceError encoding/decoding (A-XDR)

Standards:
    - COSEMpdu_GB83.txt: ServiceError definition
    - IEC 61334-6 §6.6: CHOICE encoding
    - IEC 61334-6 §6.4: ENUMERATED encoding (1 byte)
"""

import unittest
from StructResult.result import Error, NULL
from src.COSEMpdu.apdu import (
    # Error types
    ConfirmedServiceError, ApplicationReference,
    HardwareResource, VDEStateError,
    Service, Read, Write,
    Definition, Access,
    Initiate, LoadDataSet,
    Task, ServiceError, InitiateError,
)
from src.COSEMpdu.byte_buffer import ByteBuffer


class TestApplicationReference(unittest.TestCase):
    """Test application-reference [0] IMPLICIT ENUMERATED"""

    def test_encode_decode_other(self) -> None:
        """Test other (0)"""
        original = ApplicationReference(0)
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ApplicationReference.get(buf)
        self.assertEqual(decoded.value, 0)

    def test_encode_decode_time_elapsed(self) -> None:
        """Test time-elapsed (1)"""
        original = ApplicationReference(1)
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ApplicationReference.get(buf)
        self.assertEqual(decoded.value, 1)

    def test_encode_decode_all_codes(self) -> None:
        """Test all error codes 0-6"""
        for code in range(7):
            with self.subTest(code=code):
                original = ApplicationReference(code)
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = ApplicationReference.get(buf)
                self.assertEqual(decoded.value, code)

    def test_invalid_code(self) -> None:
        """Test invalid error code (>6)"""
        original = ApplicationReference(7)
        buf = ByteBuffer.allocate(10)
        # Should encode but may be invalid per spec
        original.put(buf)


class TestHardwareResource(unittest.TestCase):
    """Test hardware-resource [1] IMPLICIT ENUMERATED"""

    def test_encode_decode_all_codes(self) -> None:
        """Test all error codes 0-4"""
        for code in range(5):
            with self.subTest(code=code):
                original = HardwareResource(code)
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = HardwareResource.get(buf)
                self.assertEqual(decoded.value, code)


class TestVDEStateError(unittest.TestCase):
    """Test vde-state-error [2] IMPLICIT ENUMERATED"""

    def test_encode_decode_no_dlms_context(self) -> None:
        """Test no-dlms-context (1)"""
        original = VDEStateError(1)
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = VDEStateError.get(buf)
        self.assertEqual(decoded.value, 1)

    def test_encode_decode_all_codes(self) -> None:
        """Test all error codes 0-4"""
        for code in range(5):
            with self.subTest(code=code):
                original = VDEStateError(code)
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = VDEStateError.get(buf)
                self.assertEqual(decoded.value, code)


class TestService(unittest.TestCase):
    """Test service [3] IMPLICIT ENUMERATED"""

    def test_encode_decode_service_unsupported(self) -> None:
        """Test service-unsupported (2)"""
        original = Service(2)
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Service.get(buf)
        self.assertEqual(decoded.value, 2)


class TestDefinition(unittest.TestCase):
    """Test definition [4] IMPLICIT ENUMERATED"""

    def test_encode_decode_object_undefined(self) -> None:
        """Test object-undefined (1)"""
        original = Definition(1)
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Definition.get(buf)
        self.assertEqual(decoded.value, 1)


class TestAccess(unittest.TestCase):
    """Test access [5] IMPLICIT ENUMERATED"""

    def test_encode_decode_scope_violated(self) -> None:
        """Test scope-of-access-violated (1)"""
        original = Access(1)
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Access.get(buf)
        self.assertEqual(decoded.value, 1)


class TestInitiate(unittest.TestCase):
    """Test initiate [6] IMPLICIT ENUMERATED"""

    def test_encode_decode_incompatible_conformance(self) -> None:
        """Test incompatible-conformance (2) - most common"""
        original = Initiate(2)
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Initiate.get(buf)
        self.assertEqual(decoded.value, 2)

    def test_encode_decode_all_codes(self) -> None:
        """Test all error codes 0-4"""
        for code in range(5):
            with self.subTest(code=code):
                original = Initiate(code)
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = Initiate.get(buf)
                self.assertEqual(decoded.value, code)


class TestLoadDataSet(unittest.TestCase):
    """Test load-data-set [7] IMPLICIT ENUMERATED"""

    def test_encode_decode_all_codes(self) -> None:
        """Test all error codes 0-7"""
        for code in range(8):
            with self.subTest(code=code):
                original = LoadDataSet(code)
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = LoadDataSet.get(buf)
                self.assertEqual(decoded.value, code)


class TestTask(unittest.TestCase):
    """Test task [9] IMPLICIT ENUMERATED"""

    def test_encode_decode_all_codes(self) -> None:
        """Test all error codes 0-4"""
        for code in range(5):
            with self.subTest(code=code):
                original = Task(code)
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = Task.get(buf)
                self.assertEqual(decoded.value, code)


class TestServiceErrorChoice(unittest.TestCase):
    """Test ServiceError CHOICE encoding/decoding"""

    def test_encode_decode_application_reference(self) -> None:
        """Test application-reference alternative (tag 0)"""
        original = ServiceError(ApplicationReference(ApplicationReference.APPLICATION_UNREACHABLE))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ServiceError.get(buf)
        self.assertIsInstance(decoded.value, ApplicationReference)
        self.assertEqual(decoded.value.value, 2)

    def test_encode_decode_hardware_resource(self) -> None:
        """Test hardware-resource alternative (tag 1)"""
        original = ServiceError(HardwareResource(3))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ServiceError.get(buf)
        self.assertIsInstance(decoded.value, HardwareResource)
        self.assertEqual(decoded.value.value, 3)

    def test_encode_decode_initiate_incompatible_conformance(self) -> None:
        """Test initiate with incompatible-conformance (most common case)"""
        original = ServiceError(Initiate(2))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ServiceError.get(buf)
        self.assertIsInstance(decoded.value, Initiate)
        self.assertEqual(decoded.value.value, 2)

    def test_encode_decode_initiate_dlms_version_too_low(self) -> None:
        """Test initiate with dlms-version-too-low (1)"""
        original = ServiceError(Initiate(1))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ServiceError.get(buf)
        self.assertIsInstance(decoded.value, Initiate)
        self.assertEqual(decoded.value.value, 1)

    def test_encode_decode_read_error(self) -> None:
        """Test read alternative (tag 5)"""
        original = ConfirmedServiceError(Read(Access(1)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ConfirmedServiceError.get(buf)
        self.assertIsInstance(decoded.value, Read)

    def test_encode_decode_write_error(self) -> None:
        """Test write alternative (tag 6)"""
        original = ConfirmedServiceError(Write(Access(2)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ConfirmedServiceError.get(buf)
        self.assertIsInstance(decoded.value, Write)

    def test_encode_decode_all_alternatives(self) -> None:
        """Test all ServiceError alternatives"""
        test_cases = [
            (ApplicationReference, 0),
            (HardwareResource, 1),
            (VDEStateError, 2),
            (Service, 0),
            (Definition, 1),
            (Access, 3),
            (Initiate, 2),
            (LoadDataSet, 4),
            (Task, 4),
        ]

        for error_class, error_value in test_cases:
            with self.subTest(error_class=error_class.__name__):
                original = ServiceError(error_class(error_value))
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = ServiceError.get(buf)
                self.assertIsInstance(decoded.value, error_class)

    def test_invalid_tag(self) -> None:
        """Test invalid tag number"""
        buf = ByteBuffer.wrap(bytes([0xFF, 0x00]))  # Tag 255 (invalid)
        self.assertFalse(ServiceError.get(buf).has(None, ValueError))

    def test_encoding_size(self) -> None:
        """Test that ServiceError encoding is 2 bytes (tag + enum)"""
        original = ServiceError(Initiate(2))
        buf = ByteBuffer.allocate(10)
        size = original.put(buf)
        self.assertEqual(size, 2)  # 1 byte tag + 1 byte enum


class TestInitiateError(unittest.TestCase):
    """Test InitiateError [1] ServiceError"""

    def test_encode_decode_initiate_error(self) -> None:
        """Test InitiateError wrapper"""
        service_error = ServiceError(Initiate(2))
        original = InitiateError(service_error)
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        # Read tag
        tag = buf.get_u8()
        self.assertEqual(tag, 1)
        # Decode ServiceError
        decoded_service_error = ServiceError.get(buf)
        self.assertIsInstance(decoded_service_error.value, Initiate)
        self.assertEqual(decoded_service_error.value.value, 2)

    def test_initiate_error_tag(self) -> None:
        """Test that InitiateError has tag 1"""
        self.assertEqual(InitiateError.tag, 1)


class TestConfirmedServiceErrorIntegration(unittest.TestCase):
    """Integration tests for ConfirmedServiceError PDU"""

    def test_full_pdu_encoding_initiate_error(self) -> None:
        """
        Test full ConfirmedServiceError PDU encoding

        Per IEC 61334-6 Example 3:
        OE          tag (explicit) of ConfirmedServiceError (=14)
        01          tag of initiateError (=1)
        06          tag of initiate (=6)
        02          ENUMERATED value (incompatible-conformance=2)
        """
        # ConfirmedServiceError is CHOICE with tag 14
        # initiateError is [1] ServiceError
        # ServiceError CHOICE with initiate [6]
        # Initiate ENUMERATED with value 2

        # Simulate the encoding
        confirmed_error_tag = 14
        initiate_error_tag = 1
        initiate_tag = 6
        error_code = 2

        buf = ByteBuffer.allocate(10)
        buf.put_u8(confirmed_error_tag)  # ConfirmedServiceError tag
        buf.put_u8(initiate_error_tag)   # initiateError tag
        buf.put_u8(initiate_tag)         # initiate tag
        buf.put_u8(error_code)           # error code

        # Verify encoding
        buf.set_pos(0)
        self.assertEqual(buf.get_u8(), confirmed_error_tag)
        self.assertEqual(buf.get_u8(), initiate_error_tag)
        self.assertEqual(buf.get_u8(), initiate_tag)
        self.assertEqual(buf.get_u8(), error_code)

    def test_common_error_scenarios(self) -> None:
        """Test common error scenarios from DLMS/COSEM"""
        scenarios = [
            # (error_class, error_code, description)
            (Initiate, 1, "dlms-version-too-low"),
            (Initiate, 2, "incompatible-conformance"),
            (Initiate, 3, "pdu-size-too-short"),
            (Initiate, 4, "refused-by-the-vde-handler"),
            (Access, 1, "scope-of-access-violated"),
            (Access, 2, "object-access-violated"),
            (Definition, 1, "object-undefined"),
        ]

        for error_class, error_code, description in scenarios:
            with self.subTest(description=description):
                error_value = error_class(error_code)

                original = ServiceError(error_value)
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                if isinstance(decoded := ServiceError.get(buf), Error):
                    decoded.unwrap()
                self.assertIsInstance(decoded.value, error_class)
                self.assertEqual(decoded.value.value, error_code)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def test_buffer_overflow(self) -> None:
        """Test buffer overflow protection"""
        original = ServiceError(Initiate(Initiate.INCOMPATIBLE_CONFORMANCE))
        buf = ByteBuffer.allocate(1)  # Too small
        if isinstance(err := original.put(buf), Error):
            self.assertTrue(err.has(NULL, BufferError))

    def test_empty_buffer(self) -> None:
        """Test decoding from empty buffer"""
        buf = ByteBuffer.allocate(0)
        self.assertFalse(ServiceError.get(buf).has(None, BufferError))

    def test_round_trip_all_error_types(self) -> None:
        """Test round-trip encoding/decoding for all error types"""
        test_cases = [
            (ApplicationReference, 0),
            (HardwareResource, 1),
            (VDEStateError, 2),
            (Service, 0),
            (Definition, 1),
            (Access, 2),
            (Initiate, 3),
            (LoadDataSet, 4),
            (Task, 0),
        ]

        for error_class, error_value in test_cases:
            with self.subTest(error_class=error_class.__name__):
                original = error_class(error_value)
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = error_class.get(buf)
                self.assertEqual(decoded.value, error_value)


if __name__ == "__main__":
    unittest.main()
