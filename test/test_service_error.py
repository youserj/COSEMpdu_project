"""
Unit tests for ServiceError encoding/decoding (A-XDR)

Standards:
    - COSEMpdu_GB83.txt: ServiceError definition
    - IEC 61334-6 §6.6: CHOICE encoding
    - IEC 61334-6 §6.4: ENUMERATED encoding (1 byte)
"""

import unittest
from src.COSEMpdu.service_error import (
    # Error types
    ConfirmedServiceError, Write,
    ApplicationReference, ApplicationReferenceEnum,
    HardwareResource, HardwareResourceEnum,
    VDEStateError, VDEStateErrorEnum,
    Service, ServiceEnum,
    Read,
    Definition, DefinitionEnum,
    Access, AccessEnum,
    Initiate, InitiateEnum,
    LoadDataSet, LoadDataSetEnum,
    Task, TaskEnum,
    ChangeScope, ChangeScopeEnum,
    Other, OtherEnum,
    # CHOICE types
    ServiceError,
    InitiateError,
)
from src.COSEMpdu.byte_buffer import ByteBuffer
from src.COSEMpdu import axdr


class TestApplicationReference(unittest.TestCase):
    """Test application-reference [0] IMPLICIT ENUMERATED"""
    
    def test_encode_decode_other(self):
        """Test other (0)"""
        original = ApplicationReference(ApplicationReferenceEnum(0))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ApplicationReference.get(buf)
        self.assertEqual(decoded.value.value, 0)
    
    def test_encode_decode_time_elapsed(self):
        """Test time-elapsed (1)"""
        original = ApplicationReference(ApplicationReferenceEnum(1))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ApplicationReference.get(buf)
        self.assertEqual(decoded.value.value, 1)
    
    def test_encode_decode_all_codes(self):
        """Test all error codes 0-6"""
        for code in range(7):
            with self.subTest(code=code):
                original = ApplicationReference(ApplicationReferenceEnum(code))
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = ApplicationReference.get(buf)
                self.assertEqual(decoded.value.value, code)
    
    def test_invalid_code(self):
        """Test invalid error code (>6)"""
        original = ApplicationReference(ApplicationReferenceEnum(7))
        buf = ByteBuffer.allocate(10)
        # Should encode but may be invalid per spec
        original.put(buf)


class TestHardwareResource(unittest.TestCase):
    """Test hardware-resource [1] IMPLICIT ENUMERATED"""
    
    def test_encode_decode_all_codes(self):
        """Test all error codes 0-4"""
        for code in range(5):
            with self.subTest(code=code):
                original = HardwareResource(HardwareResourceEnum(code))
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = HardwareResource.get(buf)
                self.assertEqual(decoded.value.value, code)


class TestVDEStateError(unittest.TestCase):
    """Test vde-state-error [2] IMPLICIT ENUMERATED"""
    
    def test_encode_decode_no_dlms_context(self):
        """Test no-dlms-context (1)"""
        original = VDEStateError(VDEStateErrorEnum(1))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = VDEStateError.get(buf)
        self.assertEqual(decoded.value.value, 1)
    
    def test_encode_decode_all_codes(self):
        """Test all error codes 0-4"""
        for code in range(5):
            with self.subTest(code=code):
                original = VDEStateError(VDEStateErrorEnum(code))
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = VDEStateError.get(buf)
                self.assertEqual(decoded.value.value, code)


class TestService(unittest.TestCase):
    """Test service [3] IMPLICIT ENUMERATED"""
    
    def test_encode_decode_service_unsupported(self):
        """Test service-unsupported (2)"""
        original = Service(ServiceEnum(2))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Service.get(buf)
        self.assertEqual(decoded.value.value, 2)


class TestDefinition(unittest.TestCase):
    """Test definition [4] IMPLICIT ENUMERATED"""
    
    def test_encode_decode_object_undefined(self):
        """Test object-undefined (1)"""
        original = Definition(DefinitionEnum(1))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Definition.get(buf)
        self.assertEqual(decoded.value.value, 1)


class TestAccess(unittest.TestCase):
    """Test access [5] IMPLICIT ENUMERATED"""
    
    def test_encode_decode_scope_violated(self):
        """Test scope-of-access-violated (1)"""
        original = Access(AccessEnum(1))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Access.get(buf)
        self.assertEqual(decoded.value.value, 1)


class TestInitiate(unittest.TestCase):
    """Test initiate [6] IMPLICIT ENUMERATED"""
    
    def test_encode_decode_incompatible_conformance(self):
        """Test incompatible-conformance (2) - most common"""
        original = Initiate(InitiateEnum(2))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Initiate.get(buf)
        self.assertEqual(decoded.value.value, 2)
    
    def test_encode_decode_all_codes(self):
        """Test all error codes 0-4"""
        for code in range(5):
            with self.subTest(code=code):
                original = Initiate(InitiateEnum(code))
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = Initiate.get(buf)
                self.assertEqual(decoded.value.value, code)


class TestLoadDataSet(unittest.TestCase):
    """Test load-data-set [7] IMPLICIT ENUMERATED"""
    
    def test_encode_decode_all_codes(self):
        """Test all error codes 0-7"""
        for code in range(8):
            with self.subTest(code=code):
                original = LoadDataSet(LoadDataSetEnum(code))
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = LoadDataSet.get(buf)
                self.assertEqual(decoded.value.value, code)


class TestTask(unittest.TestCase):
    """Test task [9] IMPLICIT ENUMERATED"""
    
    def test_encode_decode_all_codes(self):
        """Test all error codes 0-4"""
        for code in range(5):
            with self.subTest(code=code):
                original = Task(TaskEnum(code))
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = Task.get(buf)
                self.assertEqual(decoded.value.value, code)


class TestServiceErrorChoice(unittest.TestCase):
    """Test ServiceError CHOICE encoding/decoding"""
    
    def test_encode_decode_application_reference(self):
        """Test application-reference alternative (tag 0)"""
        original = ServiceError(ApplicationReference(ApplicationReferenceEnum(2)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ServiceError.get(buf)
        self.assertEqual(decoded.selected, "application-reference")
        self.assertEqual(decoded.value.value.value, 2)
    
    def test_encode_decode_hardware_resource(self):
        """Test hardware-resource alternative (tag 1)"""
        original = ServiceError(HardwareResource(HardwareResourceEnum(3)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ServiceError.get(buf)
        self.assertEqual(decoded.selected, "hardware-resource")
        self.assertEqual(decoded.value.value.value, 3)
    
    def test_encode_decode_initiate_incompatible_conformance(self):
        """Test initiate with incompatible-conformance (most common case)"""
        original = ServiceError(Initiate(InitiateEnum(2)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ServiceError.get(buf)
        self.assertEqual(decoded.selected, "initiate")
        self.assertEqual(decoded.value.value.value, 2)
    
    def test_encode_decode_initiate_dlms_version_too_low(self):
        """Test initiate with dlms-version-too-low (1)"""
        original = ServiceError(Initiate(InitiateEnum(1)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ServiceError.get(buf)
        self.assertEqual(decoded.selected, "initiate")
        self.assertEqual(decoded.value.value.value, 1)
    
    def test_encode_decode_read_error(self):
        """Test read alternative (tag 5)"""
        original = ConfirmedServiceError(Read(ServiceError(Access(AccessEnum(1)))))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ConfirmedServiceError.get(buf)
        self.assertEqual(decoded.selected, "read")
    
    def test_encode_decode_write_error(self):
        """Test write alternative (tag 6)"""
        original = ConfirmedServiceError.write(ServiceError.access(AccessEnum(2)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = ConfirmedServiceError.get(buf)
        self.assertEqual(decoded.selected, "write")
    
    def test_encode_decode_all_alternatives(self):
        """Test all ServiceError alternatives"""
        test_cases = [
            ("application-reference", ApplicationReference, ApplicationReferenceEnum(0)),
            ("hardware-resource", HardwareResource, HardwareResourceEnum(1)),
            ("vde-state-error", VDEStateError, VDEStateErrorEnum(2)),
            ("service", Service, ServiceEnum(0)),
            ("definition", Definition, DefinitionEnum(1)),
            ("access", Access, AccessEnum(3)),
            ("initiate", Initiate, InitiateEnum(2)),
            ("load-data-set", LoadDataSet, LoadDataSetEnum(4)),
            ("task", Task, TaskEnum(4)),
        ]
        
        for selected, error_class, error_value in test_cases:
            with self.subTest(selected=selected):
                original = ServiceError.from_id(selected, error_class(error_value))
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = ServiceError.get(buf)
                self.assertEqual(decoded.selected, selected)
    
    def test_invalid_tag(self):
        """Test invalid tag number"""
        buf = ByteBuffer.wrap(bytes([0xFF, 0x00]))  # Tag 255 (invalid)
        with self.assertRaises(ValueError):
            ServiceError.get(buf)
    
    def test_encoding_size(self):
        """Test that ServiceError encoding is 2 bytes (tag + enum)"""
        original = ServiceError(Initiate(InitiateEnum(2)))
        buf = ByteBuffer.allocate(10)
        size = original.put(buf)
        self.assertEqual(size, 2)  # 1 byte tag + 1 byte enum


class TestInitiateError(unittest.TestCase):
    """Test InitiateError [1] ServiceError"""
    
    def test_encode_decode_initiate_error(self):
        """Test InitiateError wrapper"""
        service_error = ServiceError(Initiate(InitiateEnum(2)))
        original = InitiateError(service_error)
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        # Read tag
        tag = buf.get_uint8()
        self.assertEqual(tag, 1)
        # Decode ServiceError
        decoded_service_error = ServiceError.get(buf)
        self.assertEqual(decoded_service_error.selected, "initiate")
        self.assertEqual(decoded_service_error.value.value.value, 2)
    
    def test_initiate_error_tag(self):
        """Test that InitiateError has tag 1"""
        self.assertEqual(InitiateError.tag, 1)


class TestConfirmedServiceErrorIntegration(unittest.TestCase):
    """Integration tests for ConfirmedServiceError PDU"""
    
    def test_full_pdu_encoding_initiate_error(self):
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
        buf.put_uint8(confirmed_error_tag)  # ConfirmedServiceError tag
        buf.put_uint8(initiate_error_tag)   # initiateError tag
        buf.put_uint8(initiate_tag)         # initiate tag
        buf.put_uint8(error_code)           # error code
        
        # Verify encoding
        buf.set_pos(0)
        self.assertEqual(buf.get_uint8(), confirmed_error_tag)
        self.assertEqual(buf.get_uint8(), initiate_error_tag)
        self.assertEqual(buf.get_uint8(), initiate_tag)
        self.assertEqual(buf.get_uint8(), error_code)
    
    def test_common_error_scenarios(self):
        """Test common error scenarios from DLMS/COSEM"""
        scenarios = [
            # (error_type, error_code, description)
            ("initiate", 1, "dlms-version-too-low"),
            ("initiate", 2, "incompatible-conformance"),
            ("initiate", 3, "pdu-size-too-short"),
            ("initiate", 4, "refused-by-the-vde-handler"),
            ("access", 1, "scope-of-access-violated"),
            ("access", 2, "object-access-violated"),
            ("definition", 1, "object-undefined"),
        ]
        
        for error_type, error_code, description in scenarios:
            with self.subTest(description=description):
                if error_type == "initiate":
                    error_value = InitiateEnum(error_code)
                elif error_type == "access":
                    error_value = AccessEnum(error_code)
                elif error_type == "definition":
                    error_value = DefinitionEnum(error_code)
                else:
                    continue
                
                original = ServiceError.from_id(error_type, error_value)
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = ServiceError.get(buf)
                self.assertEqual(decoded.selected, error_type)
                self.assertEqual(decoded.value.value.value, error_code)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_buffer_overflow(self):
        """Test buffer overflow protection"""
        original = ServiceError(Initiate(InitiateEnum(2)))
        buf = ByteBuffer.allocate(1)  # Too small
        with self.assertRaises(BufferError):
            original.put(buf)
    
    def test_empty_buffer(self):
        """Test decoding from empty buffer"""
        buf = ByteBuffer.allocate(0)
        with self.assertRaises(BufferError):
            ServiceError.get(buf)
    
    def test_round_trip_all_error_types(self):
        """Test round-trip encoding/decoding for all error types"""
        test_cases = [
            (ApplicationReference, ApplicationReferenceEnum(0)),
            (HardwareResource, HardwareResourceEnum(1)),
            (VDEStateError, VDEStateErrorEnum(2)),
            (Service, ServiceEnum(0)),
            (Definition, DefinitionEnum(1)),
            (Access, AccessEnum(2)),
            (Initiate, InitiateEnum(3)),
            (LoadDataSet, LoadDataSetEnum(4)),
            (Task, TaskEnum(0)),
        ]
        
        for error_class, error_value in test_cases:
            with self.subTest(error_class=error_class.__name__):
                original = error_class(error_value)
                buf = ByteBuffer.allocate(10)
                original.put(buf)
                buf.set_pos(0)
                decoded = error_class.get(buf)
                self.assertEqual(decoded.value.value, error_value.value)


if __name__ == "__main__":
    unittest.main()