"""
Unit tests for types_used.py - DLMS/COSEM xDLMS Data Transfer Services Types
"""
import unittest
from src.COSEMpdu.types_used import (
    # ENUMERATED Types
    DataAccessResult, DataAccessResult1, DataAccessResultList,
    ActionResult, ActionResultList,
    # Basic Types
    CosemClassId, CosemObjectInstanceId, CosemObjectAttributeId, CosemObjectMethodId,
    # SEQUENCE Types
    CosemAttributeDescriptor, CosemMethodDescriptor, SelectiveAccessDescriptor,
    VariableAccessSpecification, GetDataResult, DataBlockGResult,
    AccessRequestSpecification, AccessResponseSpecification,
    # Invoke-Id-And-Priority Types
    InvokeIdAndPriority, LongInvokeIdAndPriority,
    # Data Block Types
    DataBlockResult, DataBlockG, DataBlockSA,
    # Action Response Types
    ActionResponseWithOptionalData,
    # Notification Types
    NotificationBody,
    # List Types
    ListOfData, ListOfAccessRequestSpecification, ListOfAccessResponseSpecification,
    # Access Request Types
    AccessRequestGet, AccessRequestGet1, AccessRequestGetWithSelection, AccessRequestBody, ListOfAccessRequestSpecification0,
    # Access Response Types
    AccessResponseGet, AccessResponseBodyContent,
)
from src.COSEMpdu.data import Data
from src.COSEMpdu.byte_buffer import ByteBuffer
from src.COSEMpdu import axdr
from src.COSEMpdu.cosem_pdu import (
    Integer8, Unsigned16, Unsigned32
)


class TestDataAccessResult(unittest.TestCase):
    """Test DataAccessResult ENUMERATED type"""

    def test_success_value(self) -> None:
        """Test success (0) value encoding/decoding"""
        result = DataAccessResult.SUCCESS
        repr(result)
        buf = ByteBuffer.allocate(10)
        result.put(buf)

        self.assertEqual(bytes(buf)[:1], b"\x00")

        buf.set_pos(0)
        decoded = DataAccessResult.get(buf)
        self.assertEqual(decoded.value.value, 0)

    def test_hardware_fault_value(self) -> None:
        """Test hardware-fault (1) value encoding/decoding"""
        result = DataAccessResult(DataAccessResultList().members[1])  # hardware-fault = 1
        buf = ByteBuffer.allocate(10)
        result.put(buf)

        self.assertEqual(bytes(buf)[:1], b"\x01")

        buf.set_pos(0)
        decoded = DataAccessResult.get(buf)
        self.assertEqual(decoded.value.value, 1)

    def test_other_reason_value(self) -> None:
        """Test other-reason (250) value encoding/decoding"""
        result = DataAccessResult(DataAccessResultList().members[15])  # other-reason = 250
        buf = ByteBuffer.allocate(10)
        result.put(buf)

        self.assertEqual(bytes(buf)[:1], b"\xfa")

        buf.set_pos(0)
        decoded = DataAccessResult.get(buf)
        self.assertEqual(decoded.value.value, 250)

    def test_tagged_data_access_result(self) -> None:
        """Test [1] IMPLICIT Data-Access-Result tagged type"""
        result = DataAccessResult1(DataAccessResult(DataAccessResultList().members[0]))
        buf = ByteBuffer.allocate(10)
        result.put(buf)

        self.assertEqual(bytes(buf)[:1], b"\x00")

        buf.set_pos(0)
        decoded = DataAccessResult1.get(buf)
        self.assertEqual(decoded.value.value.value, 0)


class TestActionResult(unittest.TestCase):
    """Test ActionResult ENUMERATED type"""

    def test_success_value(self) -> None:
        """Test success (0) value"""
        result = ActionResult(ActionResultList().members[0])
        buf = ByteBuffer.allocate(10)
        result.put(buf)

        self.assertEqual(bytes(buf)[:1], b"\x00")

        buf.set_pos(0)
        decoded = ActionResult.get(buf)
        self.assertEqual(decoded.value.value, 0)

    def test_long_action_aborted_value(self) -> None:
        """Test long-action-aborted (15) value"""
        result = ActionResult(ActionResultList().members[10])
        buf = ByteBuffer.allocate(10)
        result.put(buf)

        self.assertEqual(bytes(buf)[:1], b"\x0f")

        buf.set_pos(0)
        decoded = ActionResult.get(buf)
        self.assertEqual(decoded.value.value, 15)


class TestCosemBasicTypes(unittest.TestCase):
    """Test basic COSEM types"""

    def test_cosem_class_id(self) -> None:
        """Test CosemClassId (Unsigned16)"""
        class_id = CosemClassId(1)  # Data type
        buf = ByteBuffer.allocate(10)
        buf.put_uint8((class_id >> 8) & 0xFF)
        buf.put_uint8(class_id & 0xFF)

        buf.set_pos(0)
        decoded = (buf.get_uint8() << 8) | buf.get_uint8()
        self.assertEqual(decoded, 1)

    def test_cosem_object_instance_id(self) -> None:
        """Test CosemObjectInstanceId (OCTET STRING SIZE(6))"""
        instance_id = CosemObjectInstanceId(b"\x00\x00\x01\x00\x00\xff")
        self.assertEqual(len(instance_id.value), 6)

        buf = ByteBuffer.allocate(10)
        buf.write(instance_id.value)

        self.assertEqual(bytes(buf)[:6], b"\x00\x00\x01\x00\x00\xff")

    def test_cosem_object_attribute_id(self) -> None:
        """Test CosemObjectAttributeId (Integer8)"""
        attr_id = CosemObjectAttributeId(2)
        buf = ByteBuffer.allocate(10)
        buf.put_uint8(attr_id.value & 0xFF)

        buf.set_pos(0)
        decoded = Integer8(buf.get_uint8())
        self.assertEqual(decoded.value, 2)

    def test_cosem_object_method_id(self) -> None:
        """Test CosemObjectMethodId (Integer8)"""
        method_id = CosemObjectMethodId(1)
        buf = ByteBuffer.allocate(10)
        buf.put_uint8(method_id.value & 0xFF)

        buf.set_pos(0)
        decoded = Integer8(buf.get_uint8())
        self.assertEqual(decoded.value, 1)


class TestCosemAttributeDescriptor(unittest.TestCase):
    """Test CosemAttributeDescriptor SEQUENCE type"""

    def test_from_components(self) -> None:
        """Test from_components constructor"""
        descriptor = CosemAttributeDescriptor.from_components(
            class_id=1,
            instance_id=b"\x00\x00\x01\x00\x00\xff",
            attribute_id=2
        )

        self.assertEqual(descriptor.value[0].value, 1)
        self.assertEqual(bytes(descriptor.value[1].value), b"\x00\x00\x01\x00\x00\xff")
        self.assertEqual(descriptor.value[2].value, 2)

    def test_encode_decode(self) -> None:
        """Test encoding and decoding"""
        descriptor = CosemAttributeDescriptor.from_components(
            class_id=1,
            instance_id=b"\x00\x00\x01\x00\x00\xff",
            attribute_id=2
        )

        buf = ByteBuffer.allocate(50)
        descriptor.put(buf)

        buf.set_pos(0)
        decoded = CosemAttributeDescriptor.get(buf)

        self.assertEqual(decoded.value[0].value, 1)
        self.assertEqual(bytes(decoded.value[1].value), b"\x00\x00\x01\x00\x00\xff")
        self.assertEqual(decoded.value[2].value, 2)


class TestCosemMethodDescriptor(unittest.TestCase):
    """Test CosemMethodDescriptor SEQUENCE type"""

    def test_from_components(self) -> None:
        """Test from_components constructor"""
        descriptor = CosemMethodDescriptor.from_components(
            class_id=1,
            instance_id=b"\x00\x00\x01\x00\x00\xff",
            method_id=1
        )

        self.assertEqual(descriptor.value[0].value, 1)
        self.assertEqual(bytes(descriptor.value[1].value), b"\x00\x00\x01\x00\x00\xff")
        self.assertEqual(descriptor.value[2].value, 1)


class TestSelectiveAccessDescriptor(unittest.TestCase):
    """Test SelectiveAccessDescriptor SEQUENCE type"""

    def test_from_components(self) -> None:
        """Test from_components constructor"""
        data = Data.integer(100)
        descriptor = SelectiveAccessDescriptor.from_components(
            access_selector=1,
            access_parameters=data
        )

        self.assertEqual(descriptor.value[0].value, 1)
        self.assertEqual(descriptor.value[1].value.value.value, 100)


class TestInvokeIdAndPriority(unittest.TestCase):
    """Test Invoke-Id-And-Priority types"""

    def test_invoke_id_from_bits_confirmed_high(self) -> None:
        """Test from_bits with confirmed service class and high priority"""
        priority = InvokeIdAndPriority.from_bits(
            invoke_id=5,
            service_class="confirmed",
            priority="high"
        )

        # bits 0-3: invoke_id=5, bit 6: confirmed=1, bit 7: high=1
        # Expected: 0101 00 11 = 0x53
        self.assertEqual(priority.value, 0x53)
        self.assertEqual(priority.invoke_id, 5)
        self.assertTrue(priority.is_confirmed())
        self.assertTrue(priority.is_high_priority())

    def test_invoke_id_from_bits_unconfirmed_normal(self) -> None:
        """Test from_bits with unconfirmed service class and normal priority"""
        priority = InvokeIdAndPriority.from_bits(
            invoke_id=10,
            service_class="unconfirmed",
            priority="normal"
        )

        # bits 0-3: invoke_id=10, bit 6: unconfirmed=0, bit 7: normal=0
        # Expected: 1010 00 00 = 0xA0
        self.assertEqual(priority.value, 0xA0)
        self.assertEqual(priority.invoke_id, 10)
        self.assertFalse(priority.is_confirmed())
        self.assertFalse(priority.is_high_priority())

    def test_invoke_id_invalid_range(self) -> None:
        """Test from_bits with invalid invoke_id range"""
        with self.assertRaises(ValueError):
            InvokeIdAndPriority.from_bits(invoke_id=16)

    def test_long_invoke_id_from_bits(self) -> None:
        """Test LongInvokeIdAndPriority from_bits"""
        priority = LongInvokeIdAndPriority.from_bits(
            long_invoke_id=0x123456,
            self_descriptive="Self",
            processing_option="Break",
            service_class="confirmed",
            priority="high"
        )

        # Check individual bits
        self.assertEqual(priority.long_invoke_id, 0x123456)
        self.assertTrue(priority.is_self_descriptive())
        self.assertTrue(priority.is_break_on_error())
        self.assertTrue(priority.is_confirmed())
        self.assertTrue(priority.is_high_priority())

    def test_long_invoke_id_from_bits_defaults(self) -> None:
        """Test LongInvokeIdAndPriority with default values"""
        priority = LongInvokeIdAndPriority.from_bits(long_invoke_id=0x000001)

        self.assertEqual(priority.long_invoke_id, 0x000001)
        self.assertFalse(priority.is_self_descriptive())
        self.assertFalse(priority.is_break_on_error())
        self.assertTrue(priority.is_confirmed())  # Default is confirmed
        self.assertFalse(priority.is_high_priority())  # Default is normal


class TestVariableAccessSpecification(unittest.TestCase):
    """Test Variable-Access-Specification CHOICE type"""

    def test_variable_name(self) -> None:
        """Test variable-name [2] alternative"""
        spec = VariableAccessSpecification.variable_name(object_name=0x0010)

        buf = ByteBuffer.allocate(10)
        spec.put(buf)

        # Tag 2 + ObjectName (2 bytes)
        self.assertEqual(bytes(buf)[:3], b"\x02\x00\x10")

        buf.set_pos(0)
        decoded = VariableAccessSpecification.get(buf)
        self.assertEqual(decoded.value.value.value, 0x0010)

    def test_parameterized_access(self) -> None:
        """Test parameterized-access [4] alternative"""
        param = Data.integer(100)
        spec = VariableAccessSpecification.parameterized_access(
            variable_name=0x0010,
            selector=1,
            parameter=param
        )

        buf = ByteBuffer.allocate(50)
        spec.put(buf)

        buf.set_pos(0)
        decoded = VariableAccessSpecification.get(buf)
        self.assertEqual(decoded.value.value.value[0].value, 0x0010)
        self.assertEqual(decoded.value.value.value[1].value, 1)

    def test_block_number_access(self) -> None:
        """Test block-number-access [5] alternative"""
        spec = VariableAccessSpecification.block_number(block_number=100)

        buf = ByteBuffer.allocate(10)
        spec.put(buf)

        buf.set_pos(0)
        decoded = VariableAccessSpecification.get(buf)
        self.assertEqual(decoded.value.value.value[0].value, 100)

    def test_read_data_block_access(self) -> None:
        """Test read-data-block-access [6] alternative"""
        spec = VariableAccessSpecification.read_data_block(
            last_block=True,
            block_number=1,
            raw_data=b"\x01\x02\x03\x04"
        )

        buf = ByteBuffer.allocate(50)
        spec.put(buf)

        buf.set_pos(0)
        decoded = VariableAccessSpecification.get(buf)
        self.assertTrue(decoded.value.value.value[0].value.value)
        self.assertEqual(decoded.value.value.value[1].value, 1)
        self.assertEqual(bytes(decoded.value.value.value[2].value), b"\x01\x02\x03\x04")

    def test_write_data_block_access(self) -> None:
        """Test write-data-block-access [7] alternative"""
        spec = VariableAccessSpecification.from_write_data_block(
            last_block=False,
            block_number=5
        )

        buf = ByteBuffer.allocate(10)
        spec.put(buf)

        buf.set_pos(0)
        decoded = VariableAccessSpecification.get(buf)
        self.assertFalse(decoded.value.value.value[0].value.value)
        self.assertEqual(decoded.value.value.value[1].value, 5)


class TestGetDataResult(unittest.TestCase):
    """Test Get-Data-Result CHOICE type"""

    def test_data_alternative(self) -> None:
        """Test data [0] alternative"""
        data = Data.integer(42)
        result = GetDataResult.data(data)

        buf = ByteBuffer.allocate(10)
        result.put(buf)

        buf.set_pos(0)
        decoded = GetDataResult.get(buf)
        self.assertEqual(decoded.value.value.value.value.value, 42)

    def test_data_access_result_alternative(self) -> None:
        """Test data-access-result [1] alternative"""
        error = DataAccessResult1(DataAccessResult(DataAccessResultList().members[1]))
        result = GetDataResult.data_access_result(error)

        buf = ByteBuffer.allocate(10)
        result.put(buf)

        buf.set_pos(0)
        decoded = GetDataResult.get(buf)
        self.assertEqual(decoded.value.value.value.value, 1)


class TestDataBlockTypes(unittest.TestCase):
    """Test Data Block types"""

    def test_data_block_result(self) -> None:
        """Test Data-Block-Result SEQUENCE"""
        block = DataBlockResult((
            axdr.BooleanType(True),
            Unsigned16(1),
            axdr.OctetStringType(b"\x01\x02\x03")
        ))

        buf = ByteBuffer.allocate(50)
        block.put(buf)

        buf.set_pos(0)
        decoded = DataBlockResult.get(buf)
        self.assertTrue(decoded.value[0].value.value)
        self.assertEqual(decoded.value[1].value, 1)
        self.assertEqual(bytes(decoded.value[2].value), b"\x01\x02\x03")

    def test_data_block_g(self) -> None:
        """Test DataBlock-G SEQUENCE"""
        result = DataBlockGResult(
            DataBlockGResult.alternatives[0].type_(  # raw-data [0]
                axdr.OctetStringType(b"\x01\x02\x03\x04")
            )
        )
        block = DataBlockG((
            axdr.BooleanType(True),
            Unsigned32(1),
            result
        ))

        buf = ByteBuffer.allocate(50)
        block.put(buf)

        buf.set_pos(0)
        decoded = DataBlockG.get(buf)
        self.assertTrue(decoded.value[0].value.value)
        self.assertEqual(decoded.value[1].value, 1)

    def test_data_block_sa(self) -> None:
        """Test DataBlock-SA SEQUENCE"""
        block = DataBlockSA((
            axdr.BooleanType(False),
            Unsigned32(5),
            axdr.OctetStringType(b"\xab\xcd\xef")
        ))

        buf = ByteBuffer.allocate(50)
        block.put(buf)

        buf.set_pos(0)
        decoded = DataBlockSA.get(buf)
        self.assertFalse(decoded.value[0].value.value)
        self.assertEqual(decoded.value[1].value, 5)
        self.assertEqual(bytes(decoded.value[2].value), b"\xab\xcd\xef")


class TestActionResponseWithOptionalData(unittest.TestCase):
    """Test Action-Response-With-Optional-Data"""

    def test_with_return_parameters(self) -> None:
        """Test with return-parameters present"""
        data = Data.integer(100)
        get_result = GetDataResult.data(data)
        response = ActionResponseWithOptionalData((
            ActionResult(ActionResultList().members[0]),  # success
            get_result
        ))

        buf = ByteBuffer.allocate(50)
        response.put(buf)

        buf.set_pos(0)
        decoded = ActionResponseWithOptionalData.get(buf)
        self.assertEqual(decoded.value[0].value.value, 0)

    def test_without_return_parameters(self) -> None:
        """Test without return-parameters (OPTIONAL)"""
        response = ActionResponseWithOptionalData((
            ActionResult(ActionResultList().members[0]),  # success
        ))

        buf = ByteBuffer.allocate(50)
        response.put(buf)

        buf.set_pos(0)
        decoded = ActionResponseWithOptionalData.get(buf)
        self.assertEqual(decoded.value[0].value.value, 0)


class TestNotificationBody(unittest.TestCase):
    """Test Notification-Body"""

    def test_notification_body(self) -> None:
        """Test Notification-Body with data value"""
        data = Data.visible_string("test")
        body = NotificationBody((data,))
        buf = ByteBuffer.allocate(50)
        body.put(buf)
        buf.set_pos(0)
        decoded = NotificationBody.get(buf)
        self.assertEqual(decoded.value[0].value.value.value, "test")


class TestAccessRequestTypes(unittest.TestCase):
    """Test Access Request types"""

    def test_access_request_get(self) -> None:
        """Test Access-Request-Get"""
        descriptor = CosemAttributeDescriptor.from_components(
            class_id=1,
            instance_id=b"\x00\x00\x01\x00\x00\xff",
            attribute_id=2
        )
        request = AccessRequestGet((descriptor,))

        buf = ByteBuffer.allocate(50)
        request.put(buf)

        buf.set_pos(0)
        decoded = AccessRequestGet.get(buf)
        self.assertEqual(decoded.value[0].value[0].value, 1)

    def test_access_request_get_with_selection(self) -> None:
        """Test Access-Request-Get-With-Selection"""
        descriptor = CosemAttributeDescriptor.from_components(
            class_id=1,
            instance_id=b"\x00\x00\x01\x00\x00\xff",
            attribute_id=2
        )
        selection = SelectiveAccessDescriptor.from_components(
            access_selector=1,
            access_parameters=Data.integer(100)
        )
        request = AccessRequestGetWithSelection((descriptor, selection))

        buf = ByteBuffer.allocate(50)
        request.put(buf)

        buf.set_pos(0)
        decoded = AccessRequestGetWithSelection.get(buf)
        self.assertEqual(decoded.value[0].value[0].value, 1)

    def test_access_request_specification_choice(self) -> None:
        """Test Access-Request-Specification CHOICE"""
        descriptor = CosemAttributeDescriptor.from_components(
            class_id=1,
            instance_id=b"\x00\x00\x01\x00\x00\xff",
            attribute_id=2
        )
        get_request = AccessRequestGet((descriptor,))
        tagged = AccessRequestGet1(get_request)
        spec = AccessRequestSpecification(tagged)

        buf = ByteBuffer.allocate(50)
        spec.put(buf)

        buf.set_pos(0)
        decoded = AccessRequestSpecification.get(buf)
        self.assertEqual(decoded.value.value.value[0].value[0].value, 1)


class TestAccessResponseTypes(unittest.TestCase):
    """Test Access Response types"""

    def test_access_response_get(self) -> None:
        """Test Access-Response-Get"""
        response = AccessResponseGet((
            DataAccessResult1(DataAccessResult(DataAccessResultList().members[0])),
        ))

        buf = ByteBuffer.allocate(10)
        response.put(buf)

        buf.set_pos(0)
        decoded = AccessResponseGet.get(buf)
        self.assertEqual(decoded.value[0].value.value.value, 0)

    def test_access_response_specification_choice(self) -> None:
        """Test Access-Response-Specification CHOICE"""
        response = AccessResponseGet((
            DataAccessResult1(DataAccessResult(DataAccessResultList().members[0])),
        ))
        tagged = AccessResponseGet1(response)
        spec = AccessResponseSpecification(tagged)

        buf = ByteBuffer.allocate(10)
        spec.put(buf)

        buf.set_pos(0)
        decoded = AccessResponseSpecification.get(buf)
        self.assertEqual(decoded.value.value.value[0].value[0].value.value, 0)


class TestAccessRequestBody(unittest.TestCase):
    """Test Access-Request-Body"""

    def test_access_request_body(self) -> None:
        """Test Access-Request-Body with all components"""
        descriptor = CosemAttributeDescriptor.from_components(
            class_id=1,
            instance_id=b"\x00\x00\x01\x00\x00\xff",
            attribute_id=2
        )
        get_request = AccessRequestGet((descriptor,))
        tagged = AccessRequestGet1(get_request)
        spec = AccessRequestSpecification(tagged)

        request_spec_list = ListOfAccessRequestSpecification([spec])
        data_list = ListOfData([Data.integer(100)])

        body = AccessRequestBody((
            request_spec_list,
            data_list
        ))

        buf = ByteBuffer.allocate(100)
        body.put(buf)

        buf.set_pos(0)
        decoded = AccessRequestBody.get(buf)
        self.assertEqual(len(decoded.value[0].value), 1)
        self.assertEqual(len(decoded.value[1].value), 1)


class TestAccessResponseBodyContent(unittest.TestCase):
    """Test Access-Response-Body-Content"""

    def test_with_optional_request_spec(self) -> None:
        """Test with optional access-request-specification present"""
        request_spec_list = ListOfAccessRequestSpecification0(
            ListOfAccessRequestSpecification([])
        )
        data_list = ListOfData([Data.integer(100)])
        response_spec_list = ListOfAccessResponseSpecification([])

        body = AccessResponseBodyContent((
            request_spec_list,
            data_list,
            response_spec_list
        ))

        buf = ByteBuffer.allocate(100)
        body.put(buf)

        buf.set_pos(0)
        decoded = AccessResponseBodyContent.get(buf)
        self.assertIsNotNone(decoded.value[0])

    def test_without_optional_request_spec(self) -> None:
        """Test with optional access-request-specification absent"""
        data_list = ListOfData([Data.integer(100)])
        response_spec_list = ListOfAccessResponseSpecification([])

        body = AccessResponseBodyContent((
            None,  # Optional field absent
            data_list,
            response_spec_list
        ))

        buf = ByteBuffer.allocate(100)
        body.put(buf)

        buf.set_pos(0)
        decoded = AccessResponseBodyContent.get(buf)
        self.assertIsNone(decoded.value[0])


class TestListOfData(unittest.TestCase):
    """Test List-Of-Data SEQUENCE OF"""

    def test_empty_list(self) -> None:
        """Test empty list"""
        data_list = ListOfData([])

        buf = ByteBuffer.allocate(10)
        data_list.put(buf)

        buf.set_pos(0)
        decoded = ListOfData.get(buf)
        self.assertEqual(len(decoded.value), 0)

    def test_list_with_elements(self) -> None:
        """Test list with multiple elements"""
        data_list = ListOfData([
            Data.integer(1),
            Data.integer(2),
            Data.integer(3)
        ])

        buf = ByteBuffer.allocate(50)
        data_list.put(buf)

        buf.set_pos(0)
        decoded = ListOfData.get(buf)
        self.assertEqual(len(decoded.value), 3)
        self.assertEqual(decoded.value[0].value.value.value, 1)
        self.assertEqual(decoded.value[1].value.value.value, 2)
        self.assertEqual(decoded.value[2].value.value.value, 3)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def test_invalid_invoke_id_range(self) -> None:
        """Test invoke_id out of valid range (0-15)"""
        with self.assertRaises(ValueError):
            InvokeIdAndPriority.from_bits(invoke_id=16)

        with self.assertRaises(ValueError):
            InvokeIdAndPriority.from_bits(invoke_id=-1)

    def test_invalid_long_invoke_id_range(self) -> None:
        """Test long_invoke_id out of valid range (0-0xFFFFFF)"""
        with self.assertRaises(ValueError):
            LongInvokeIdAndPriority.from_bits(long_invoke_id=0x1000000)

    def test_cosem_object_instance_id_wrong_size(self) -> None:
        """Test CosemObjectInstanceId with wrong size"""
        # Should be SIZE(6)
        with self.assertRaises(Exception):
            CosemObjectInstanceId(b"\x00\x00\x01")  # Only 3 bytes

    def test_data_access_result_invalid_value(self) -> None:
        """Test DataAccessResult with invalid enumeration value"""
        # Valid values are 0-19 and 250
        buf = ByteBuffer.wrap(b"\xff")  # 255 is invalid
        with self.assertRaises(ValueError):
            DataAccessResult.get(buf)


class TestRoundTrip(unittest.TestCase):
    """Test encode/decode round-trip for complex types"""

    def test_cosem_attribute_descriptor_roundtrip(self) -> None:
        """Test full round-trip for CosemAttributeDescriptor"""
        original = CosemAttributeDescriptor.from_components(
            class_id=7,  # Clock
            instance_id=b"\x00\x00\x01\x00\x00\xff",
            attribute_id=2
        )

        buf = ByteBuffer.allocate(50)
        original.put(buf)

        buf.set_pos(0)
        decoded = CosemAttributeDescriptor.get(buf)

        self.assertEqual(original.value[0].value, decoded.value[0].value)
        self.assertEqual(bytes(original.value[1].value), bytes(decoded.value[1].value))
        self.assertEqual(original.value[2].value, decoded.value[2].value)

    def test_variable_access_specification_roundtrip(self) -> None:
        """Test full round-trip for VariableAccessSpecification"""
        original = VariableAccessSpecification.read_data_block(
            last_block=True,
            block_number=10,
            raw_data=b"\x01\x02\x03\x04\x05"
        )

        buf = ByteBuffer.allocate(50)
        original.put(buf)

        buf.set_pos(0)
        decoded = VariableAccessSpecification.get(buf)

        self.assertEqual(
            original.value.value.value[0].value.value,
            decoded.value.value.value[0].value.value
        )
        self.assertEqual(
            original.value.value.value[1].value,
            decoded.value.value.value[1].value
        )
        self.assertEqual(
            bytes(original.value.value.value[2].value),
            bytes(decoded.value.value.value[2].value)
        )

    def test_invoke_id_priority_roundtrip(self) -> None:
        """Test full round-trip for InvokeIdAndPriority"""
        original = InvokeIdAndPriority.from_bits(
            invoke_id=7,
            service_class="confirmed",
            priority="high"
        )

        buf = ByteBuffer.allocate(10)
        buf.put_uint8(original.value)

        buf.set_pos(0)
        decoded_value = buf.get_uint8()
        decoded = InvokeIdAndPriority(decoded_value)

        self.assertEqual(original.value, decoded.value)
        self.assertEqual(original.invoke_id, decoded.invoke_id)
        self.assertEqual(original.is_confirmed(), decoded.is_confirmed())
        self.assertEqual(original.is_high_priority(), decoded.is_high_priority())


if __name__ == "__main__":
    unittest.main()
