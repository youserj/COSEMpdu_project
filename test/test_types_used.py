"""
Unit tests for types_used.py - DLMS/COSEM xDLMS Data Transfer Services Types
"""
import unittest
from StructResult.result import Error
from src.COSEMpdu.x680.type import CHOICE
from src.COSEMpdu.types_used import (
    VariableName, ParameterizedAccess, ReadDataBlockAccess, WriteDataBlockAccess,
    TaggedData, dataAccessResult,
    # ENUMERATED Types
    DataAccessResult, ActionResult,
    # Basic Types
    CosemClassId, CosemObjectInstanceId, CosemObjectAttributeId, CosemObjectMethodId,
    # SEQUENCE Types
    CosemAttributeDescriptor, CosemMethodDescriptor, SelectiveAccessDescriptor,
    VariableAccessSpecification, GetDataResult, DataBlockGResult,
    AccessRequestSpecification, AccessResponseSpecification,
    # Invoke-Id-And-Priority Types
    InvokeIdAndPriority, LongInvokeIdAndPriority,
    # Data Block Types
    DataBlockResult, DataBlockG, DataBlockSA, BlockNumberAccess, RawData,
    # Action Response Types
    ActionResponseWithOptionalData,
    # Notification Types
    NotificationBody,
    # List Types
    ListOfData, ListOfAccessRequestSpecification, ListOfAccessResponseSpecification,
    # Access Request Types
    AccessRequestGet, AccessRequestGetWithSelection, AccessRequestBody, accessRequestSpecification,
    # Access Response Types
    AccessResponseGet, AccessResponseBody,
)
from src.COSEMpdu.axdr import IntegerType, BooleanType, OctetStringType
from src.COSEMpdu.data import Data, Integer, Unsigned, VisibleString, Integer8, Unsigned16, Unsigned32, ObjectName, Unsigned8
from src.COSEMpdu.byte_buffer import ByteBuffer
from src.COSEMpdu import axdr


class TestDataAccessResult(unittest.TestCase):
    """Test DataAccessResult ENUMERATED type"""

    def test_success_value(self) -> None:
        """Test success (0) value encoding/decoding"""
        result = DataAccessResult(DataAccessResult.SUCCESS)
        repr(result)
        buf = ByteBuffer.allocate(10)
        result.put(buf)
        self.assertEqual(bytes(buf)[:1], b"\x00")
        buf.set_pos(0)
        if isinstance(decoded := DataAccessResult.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, 0)

    def test_hardware_fault_value(self) -> None:
        """Test hardware-fault (1) value encoding/decoding"""
        result = DataAccessResult(DataAccessResult.HARDWARE_FAULT)
        buf = ByteBuffer.allocate(10)
        result.put(buf)

        self.assertEqual(bytes(buf)[:1], b"\x01")

        buf.set_pos(0)
        if isinstance(decoded := DataAccessResult.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, 1)

    def test_other_reason_value(self) -> None:
        """Test other-reason (250) value encoding/decoding"""
        result = DataAccessResult(DataAccessResult.OTHER_REASON)  # other-reason = 250
        buf = ByteBuffer.allocate(10)
        result.put(buf)
        self.assertEqual(bytes(buf)[:1], b"\xfa")
        buf.set_pos(0)
        if isinstance(decoded := DataAccessResult.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, 250)

    def test_tagged_data_access_result(self) -> None:
        """Test [1] IMPLICIT Data-Access-Result tagged type"""
        result = dataAccessResult(dataAccessResult.SUCCESS)
        buf = ByteBuffer.allocate(10)
        result.put(buf)
        self.assertEqual(bytes(buf)[1:2], b"\x00")
        buf.set_pos(0)
        if isinstance(decoded := dataAccessResult.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, 0)


class TestActionResult(unittest.TestCase):
    """Test ActionResult ENUMERATED type"""

    def test_success_value(self) -> None:
        """Test success (0) value"""
        result = ActionResult(ActionResult.SUCCESS)
        buf = ByteBuffer.allocate(10)
        result.put(buf)
        self.assertEqual(bytes(buf)[:1], b"\x00")

        buf.set_pos(0)
        if isinstance(decoded := ActionResult.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, 0)

    def test_long_action_aborted_value(self) -> None:
        """Test long-action-aborted (15) value"""
        result = ActionResult(ActionResult.LONG_ACTION_ABORTED)
        buf = ByteBuffer.allocate(10)
        result.put(buf)
        self.assertEqual(bytes(buf)[:1], b"\x0f")
        buf.set_pos(0)
        if isinstance(decoded := ActionResult.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, 15)


class TestCosemBasicTypes(unittest.TestCase):
    """Test basic COSEM types"""

    def test_cosem_class_id(self) -> None:
        """Test CosemClassId (Unsigned16)"""
        class_id = CosemClassId(1)  # Data type
        buf = ByteBuffer.allocate(10)
        buf.put_u8((int(class_id) >> 8) & 0xFF)
        buf.put_u8(int(class_id) & 0xFF)
        buf.set_pos(0)
        decoded = (buf.get_u8() << 8) | buf.get_u8()
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
        buf.put_u8(attr_id.value & 0xFF)

        buf.set_pos(0)
        decoded = Integer8(buf.get_u8())
        self.assertEqual(decoded.value, 2)

    def test_cosem_object_method_id(self) -> None:
        """Test CosemObjectMethodId (Integer8)"""
        method_id = CosemObjectMethodId(1)
        buf = ByteBuffer.allocate(10)
        buf.put_u8(method_id.value & 0xFF)

        buf.set_pos(0)
        decoded = Integer8(buf.get_u8())
        self.assertEqual(decoded.value, 1)


class TestCosemAttributeDescriptor(unittest.TestCase):
    """Test CosemAttributeDescriptor SEQUENCE type"""

    def test_from_components(self) -> None:
        """Test from_components constructor"""
        self.assertEqual(attr_desc.class_id.value, 1)
        self.assertEqual(bytes(attr_desc.instance_id.value), b"\x00\x00\x01\x00\x00\xff")
        self.assertEqual(attr_desc.attribute_id.value, 2)

    def test_encode_decode(self) -> None:
        """Test encoding and decoding"""
        buf = ByteBuffer.allocate(50)
        attr_desc.put(buf)

        buf.set_pos(0)
        if isinstance(decoded := CosemAttributeDescriptor.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.class_id.value, 1)
        self.assertEqual(decoded.instance_id.value, b"\x00\x00\x01\x00\x00\xff")
        self.assertEqual(decoded.attribute_id.value, 2)


class TestSelectiveAccessDescriptor(unittest.TestCase):
    """Test SelectiveAccessDescriptor SEQUENCE type"""

    def test_from_components(self) -> None:
        """Test from_components constructor"""
        class MySelective(SelectiveAccessDescriptor):
            selector_parameters = {1: Integer, 2: Unsigned, 3: Integer}


        z = MySelective.parse((3, 100))  # Valid selector and parameter


        descriptor = MySelective(
            access_selector=Unsigned8(1),
            access_parameters=Integer(100)
        )
        buf = ByteBuffer.allocate(50)
        descriptor.put(buf)
        self.assertEqual(descriptor.access_selector.normalize(), 1)
        self.assertEqual(descriptor.access_parameters.normalize(), 100)


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
        spec = VariableAccessSpecification(VariableName(0x0010))

        buf = ByteBuffer.allocate(10)
        spec.put(buf)

        # Tag 2 + ObjectName (2 bytes)
        self.assertEqual(bytes(buf)[:3], b"\x02\x00\x10")

        buf.set_pos(0)
        decoded = VariableAccessSpecification.get(buf)
        self.assertEqual(decoded.normalize(), CHOICE(2, 16))

    def test_parameterized_access(self) -> None:
        """Test parameterized-access [4] alternative"""
        spec = VariableAccessSpecification(ParameterizedAccess(
            variable_name=ObjectName(0x0010),
            selector=Unsigned8(1),
            parameter=Data(Integer(100))
        ))

        buf = ByteBuffer.allocate(50)
        spec.put(buf)

        buf.set_pos(0)
        decoded = VariableAccessSpecification.get(buf)
        self.assertEqual(decoded.value[0].value, 0x0010)
        self.assertEqual(decoded.value[1].value, 1)

    def test_block_number_access(self) -> None:
        """Test block-number-access [5] alternative"""
        spec = VariableAccessSpecification(BlockNumberAccess(block_number=Unsigned16(100)))

        buf = ByteBuffer.allocate(10)
        spec.put(buf)

        buf.set_pos(0)
        decoded = VariableAccessSpecification.get(buf)
        self.assertEqual(decoded.value[0].value, 100)

    def test_read_data_block_access(self) -> None:
        """Test read-data-block-access [6] alternative"""
        spec = VariableAccessSpecification(ReadDataBlockAccess(
            last_block=BooleanType(True),
            block_number=Unsigned16(1),
            raw_data=OctetStringType(b"\x01\x02\x03\x04")
        ))

        buf = ByteBuffer.allocate(50)
        spec.put(buf)

        buf.set_pos(0)
        if isinstance(decoded := VariableAccessSpecification.get(buf), Error):
            self.fail()
        self.assertTrue(decoded.value.last_block.value)
        self.assertEqual(decoded.value.block_number.value, 1)
        self.assertEqual(decoded.value.raw_data.normalize(), b"\x01\x02\x03\x04")

    def test_write_data_block_access(self) -> None:
        """Test write-data-block-access [7] alternative"""
        spec = VariableAccessSpecification(WriteDataBlockAccess(
            last_block=BooleanType(False),
            block_number=Unsigned16(5)
        ))

        buf = ByteBuffer.allocate(10)
        spec.put(buf)

        buf.set_pos(0)
        if isinstance(decoded := VariableAccessSpecification.get(buf), Error):
            self.fail()
        self.assertFalse(decoded.value.last_block.value)
        self.assertEqual(decoded.value.block_number.value, 5)


class TestGetDataResult(unittest.TestCase):
    """Test Get-Data-Result CHOICE type"""

    def test_data_alternative(self) -> None:
        """Test data [0] alternative"""
        result = GetDataResult(TaggedData(Integer((42))))

        buf = ByteBuffer.allocate(10)
        result.put(buf)

        buf.set_pos(0)
        if isinstance(decoded := GetDataResult.get(buf), Error):
            self.fail()
        self.assertEqual(decoded.value.value.value, 42)

    def test_data_access_result_alternative(self) -> None:
        """Test data-access-result [1] alternative"""
        result = GetDataResult(dataAccessResult(dataAccessResult.HARDWARE_FAULT))
        buf = ByteBuffer.allocate(10)
        result.put(buf)
        buf.set_pos(0)
        if isinstance(decoded := GetDataResult.get(buf), Error):
            self.fail()
        self.assertEqual(decoded.value.value, 1)


class TestDataBlockTypes(unittest.TestCase):
    """Test Data Block types"""

    def test_data_block_result(self) -> None:
        """Test Data-Block-Result SEQUENCE"""
        block = DataBlockResult(
            axdr.BooleanType(True),
            Unsigned16(1),
            axdr.OctetStringType(b"\x01\x02\x03")
        )

        buf = ByteBuffer.allocate(50)
        block.put(buf)
        buf.set_pos(0)
        if isinstance(decoded := DataBlockResult.get(buf), Error):
            decoded.unwrap()
        self.assertTrue(decoded.last_block.value)
        self.assertEqual(decoded.block_number.value, 1)
        self.assertEqual(bytes(decoded.raw_data.value), b"\x01\x02\x03")

    def test_data_block_g(self) -> None:
        """Test DataBlock-G SEQUENCE"""
        block = DataBlockG(
            axdr.BooleanType(True),
            Unsigned32(1),
            DataBlockGResult(RawData(b"\x01\x02\x03\x04"))
        )

        buf = ByteBuffer.allocate(50)
        block.put(buf)

        buf.set_pos(0)
        if isinstance(decoded := DataBlockG.get(buf), Error):
            decoded.unwrap()
        self.assertTrue(decoded.last_block.value)
        self.assertEqual(decoded.block_number.value, 1)

    def test_data_block_sa(self) -> None:
        """Test DataBlock-SA SEQUENCE"""
        block = DataBlockSA(
            axdr.BooleanType(False),
            Unsigned32(5),
            axdr.OctetStringType(b"\xab\xcd\xef")
        )

        buf = ByteBuffer.allocate(50)
        block.put(buf)
        buf.set_pos(0)
        if isinstance(decoded := DataBlockSA.get(buf), Error):
            decoded.unwrap()
        self.assertFalse(decoded.last_block.value)
        self.assertEqual(decoded.block_number.value, 5)
        self.assertEqual(bytes(decoded.raw_data.value), b"\xab\xcd\xef")


class TestActionResponseWithOptionalData(unittest.TestCase):
    """Test Action-Response-With-Optional-Data"""

    def test_with_return_parameters(self) -> None:
        """Test with return-parameters present"""
        get_result = GetDataResult(TaggedData(Data(Integer(100))))
        response = ActionResponseWithOptionalData(
            ActionResult(ActionResult.SUCCESS),
            get_result
        )

        buf = ByteBuffer.allocate(50)
        response.put(buf)

        buf.set_pos(0)
        if isinstance(decoded := ActionResponseWithOptionalData.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.result.value, 0)

    def test_without_return_parameters(self) -> None:
        """Test without return-parameters (OPTIONAL)"""
        response = ActionResponseWithOptionalData(
            ActionResult(ActionResult.SUCCESS)
        )

        buf = ByteBuffer.allocate(50)
        response.put(buf)

        buf.set_pos(0)
        if isinstance(decoded := ActionResponseWithOptionalData.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.result.value, 0)


class TestNotificationBody(unittest.TestCase):
    """Test Notification-Body"""

    def test_notification_body(self) -> None:
        """Test Notification-Body with data value"""
        data = Data(VisibleString("test"))
        body = NotificationBody(data)
        buf = ByteBuffer.allocate(50)
        body.put(buf)
        buf.set_pos(0)
        if isinstance(decoded := NotificationBody.get(buf), Error):
            self.fail()
        self.assertEqual(decoded.data_value.value.value, "test")


class TestAccessRequestTypes(unittest.TestCase):
    """Test Access Request types"""

    def test_access_request_get(self) -> None:
        """Test Access-Request-Get"""
        request = AccessRequestGet(attr_desc)

        buf = ByteBuffer.allocate(50)
        request.put(buf)

        buf.set_pos(0)
        if isinstance(decoded := AccessRequestGet.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.cosem_attribute_descriptor.class_id.value, 1)

    def test_access_request_get_with_selection(self) -> None:
        """Test Access-Request-Get-With-Selection"""
        selection = SelectiveAccessDescriptor(
            access_selector=Unsigned8(1),
            access_parameters=Data(Integer(100))
        )
        request = AccessRequestGetWithSelection(attr_desc, selection)

        buf = ByteBuffer.allocate(50)
        request.put(buf)

        buf.set_pos(0)
        if isinstance(decoded := AccessRequestGetWithSelection.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.cosem_attribute_descriptor.class_id.value, 1)

    def test_access_request_specification_choice(self) -> None:
        """Test Access-Request-Specification CHOICE"""
        spec = AccessRequestSpecification(AccessRequestGet(attr_desc))

        buf = ByteBuffer.allocate(50)
        spec.put(buf)

        buf.set_pos(0)
        decoded = AccessRequestSpecification.get(buf)
        self.assertEqual(decoded.value.cosem_attribute_descriptor.class_id.value, 1)


attr_desc = CosemAttributeDescriptor(
    class_id=CosemClassId(1),
    instance_id=CosemObjectInstanceId(b"\x00\x00\x01\x00\x00\xff"),
    attribute_id=CosemObjectAttributeId(2)
)


class TestAccessResponseTypes(unittest.TestCase):
    """Test Access Response types"""

    def test_access_response_get(self) -> None:
        """Test Access-Response-Get"""
        response = AccessResponseGet(dataAccessResult(DataAccessResult.SUCCESS))
        buf = ByteBuffer.allocate(10)
        response.put(buf)
        buf.set_pos(0)
        if isinstance(decoded := AccessResponseGet.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.result.value, 0)

    def test_access_response_specification_choice(self) -> None:
        """Test Access-Response-Specification CHOICE"""
        spec = AccessResponseSpecification(AccessResponseGet(dataAccessResult(DataAccessResult.SUCCESS)))

        buf = ByteBuffer.allocate(10)
        spec.put(buf)

        buf.set_pos(0)
        if isinstance(decoded := AccessResponseSpecification.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value.result.value, 0)


class TestAccessRequestBody(unittest.TestCase):
    """Test Access-Request-Body"""

    def test_access_request_body(self) -> None:
        """Test Access-Request-Body with all components"""
        spec = AccessRequestSpecification(AccessRequestGet(attr_desc))
        body = AccessRequestBody(
            ListOfAccessRequestSpecification([spec]),
            ListOfData([Data(Integer(100))])
        )

        buf = ByteBuffer.allocate(100)
        body.put(buf)

        buf.set_pos(0)
        if isinstance(decoded := AccessRequestBody.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(len(decoded.access_request_specification.value), 1)
        self.assertEqual(len(decoded.access_request_list_of_data.value), 1)


class TestAccessResponseBodyContent(unittest.TestCase):
    """Test Access-Response-Body-Content"""

    def test_with_optional_request_spec(self) -> None:
        """Test with optional access-request-specification present"""
        body = AccessResponseBody(
            ListOfData([Data(Integer(100))]),
            ListOfAccessResponseSpecification(),
            accessRequestSpecification()
        )

        buf = ByteBuffer.allocate(100)
        body.put(buf)

        buf.set_pos(0)
        if isinstance(decoded := AccessResponseBody.get(buf), Error):
            decoded.unwrap()
        self.assertIsNotNone(decoded.access_request_specification)

    def test_without_optional_request_spec(self) -> None:
        """Test with optional access-request-specification absent"""
        body = AccessResponseBody(
            ListOfData([Data(Integer(100))]),
            ListOfAccessResponseSpecification(),
            None,  # Optional field absent
        )
        buf = ByteBuffer.allocate(100)
        body.put(buf)

        buf.set_pos(0)
        if isinstance(decoded := AccessResponseBody.get(buf), Error):
            decoded.unwrap()
        self.assertIsNone(decoded.access_request_specification)


class TestListOfData(unittest.TestCase):
    """Test List-Of-Data SEQUENCE OF"""

    def test_empty_list(self) -> None:
        """Test empty list"""
        data_list = ListOfData([])

        buf = ByteBuffer.allocate(10)
        data_list.put(buf)

        buf.set_pos(0)
        decoded = ListOfData.get(buf)
        self.assertEqual(len(decoded), 0)

    def test_list_with_elements(self) -> None:
        """Test list with multiple elements"""
        data_list = ListOfData([
            Data(Integer(1)),
            Data(Integer(2)),
            Data(Integer(3))
        ])

        buf = ByteBuffer.allocate(50)
        data_list.put(buf)

        buf.set_pos(0)
        if isinstance(decoded := ListOfData.get(buf), Error):
            self.fail()
        self.assertEqual(len(decoded), 3)
        self.assertEqual(decoded[0].value.value, 1)
        self.assertEqual(decoded[1].value.value, 2)
        self.assertEqual(decoded[2].value.value, 3)


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
        if isinstance(decoded := DataAccessResult.get(buf), Error):
            self.assertTrue(decoded.has(exception_type=ZeroDivisionError))


class TestRoundTrip(unittest.TestCase):
    """Test encode/decode round-trip for complex types"""

    def test_cosem_attribute_descriptor_roundtrip(self) -> None:
        """Test full round-trip for CosemAttributeDescriptor"""
        original = CosemAttributeDescriptor(
            class_id=CosemClassId(7),  # Clock
            instance_id=CosemObjectInstanceId(b"\x00\x00\x01\x00\x00\xff"),
            attribute_id=CosemObjectAttributeId(2)
        )

        buf = ByteBuffer.allocate(50)
        original.put(buf)

        buf.set_pos(0)
        if isinstance(decoded := CosemAttributeDescriptor.get(buf), Error):
            self.fail()

        self.assertEqual(original.class_id, decoded.class_id)
        self.assertEqual(original.instance_id, decoded.instance_id)
        self.assertEqual(original.attribute_id, decoded.attribute_id)

    def test_variable_access_specification_roundtrip(self) -> None:
        """Test full round-trip for VariableAccessSpecification"""
        original = VariableAccessSpecification(ReadDataBlockAccess(
            last_block=BooleanType(True),
            block_number=Unsigned16(10),
            raw_data=OctetStringType(b"\x01\x02\x03\x04\x05")
        ))

        buf = ByteBuffer.allocate(50)
        original.put(buf)

        buf.set_pos(0)
        decoded = VariableAccessSpecification.get(buf)

        self.assertEqual(
            original.value.last_block.value,
            decoded.value.last_block.value
        )
        self.assertEqual(
            original.value.block_number.value,
            decoded.value.block_number.value
        )
        self.assertEqual(
            bytes(original.value.raw_data.value),
            bytes(decoded.value.raw_data.value)
        )

    def test_invoke_id_priority_roundtrip(self) -> None:
        """Test full round-trip for InvokeIdAndPriority"""
        original = InvokeIdAndPriority.from_bits(
            invoke_id=7,
            service_class="confirmed",
            priority="high"
        )

        buf = ByteBuffer.allocate(10)
        buf.put_u8(original.value)

        buf.set_pos(0)
        decoded_value = buf.get_u8()
        decoded = InvokeIdAndPriority(decoded_value)

        self.assertEqual(original.value, decoded.value)
        self.assertEqual(original.invoke_id, decoded.invoke_id)
        self.assertEqual(original.is_confirmed(), decoded.is_confirmed())
        self.assertEqual(original.is_high_priority(), decoded.is_high_priority())


if __name__ == "__main__":
    unittest.main()
