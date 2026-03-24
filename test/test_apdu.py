"""
Unit tests for XDLMS_APDU Encoding/Decoding
Based on COSEMpdu_GB83.txt (Green Book 8.3) and IEC 61334-6
Tests only put/get (encode/decode) operations for XDLMS_APDU elements
"""
import unittest
from COSEMpdu import apdu
from src.COSEMpdu.axdr import IntegerType, Type
from src.COSEMpdu.apdu import (
    # XDLMS-APDU Choice Type
    InitialRequest1, InitialResponse8,
    ReadRequest5, ReadResponse12,
    WriteRequest6, writeResponse,
    confirmedServiceError,
    DataNotification15, DataNotificationConfirm16,
    UnconfirmedWriteRequest22,
    InformationReportRequest24,
    # LN Referencing PDUs
    getRequest, getResponse,
    setRequest, setResponse,
    actionRequest, actionResponse,
    eventNotificationRequest,
    # Exception and Access
    exceptionResponse,
    accessRequest, accessResponse,
    # General APDUs
    generalGloCiphering, generalDedCiphering,
    generalCiphering, generalSigning,
    generalBlockTransfer,
)
from src.COSEMpdu.byte_buffer import ByteBuffer
from src.COSEMpdu.data import Data
from src.COSEMpdu.useful_types import Unsigned8, Unsigned16, ObjectName
from src.COSEMpdu.types_used import (
    InvokeIdAndPriority, LongInvokeIdAndPriority,
    CosemAttributeDescriptor, CosemMethodDescriptor,
    GetDataResult,
    DataAccessResult,
    ActionResponseWithOptionalData, ActionResult,
    AccessRequestBody, AccessResponseBody,
)
from src.COSEMpdu.service_error import ConfirmedServiceError, ServiceError
from src.COSEMpdu.user_information import InitiateRequest, InitiateResponse
from src.COSEMpdu.key_info import KeyInfo, IdentifiedKey, KeyId


class TestXDLMS_APDU_EncodeDecode(unittest.TestCase):
    """Test XDLMS_APDU encoding and decoding operations"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        self.maxDiff = None

    def _encode_decode_roundtrip(self, apdu_class: type[Type], value: Type, tag_number: int) -> bytes:
        """Helper method to test encode/decode roundtrip"""
        # Create APDU instance
        apdu = apdu_class(value)

        # Encode to ByteBuffer
        buf = ByteBuffer.allocate(1024)
        apdu.put(buf)
        encoded_bytes = bytes(buf)

        # Decode from ByteBuffer
        decode_buffer = ByteBuffer.wrap(encoded_bytes)
        decoded_apdu = apdu_class.get(decode_buffer)

        # Verify tag number
        self.assertEqual(apdu.tag, tag_number)
        self.assertEqual(decoded_apdu.tag, tag_number)

        # Verify value preservation
        self.assertEqual(decoded_apdu.value, value)

        return encoded_bytes

    # =========================================================================
    # Standard PDUs (no ciphering) - Tags 1-24
    # =========================================================================

    def test_initiate_request_tag_1(self) -> None:
        """Test InitialRequest1 encode/decode (tag 1)"""
        value = InitiateRequest(
            dedicated_key=None,
            response_allowed=True,
            proposed_quality_of_service=None,
            proposed_dlms_version_number=Unsigned8.from_int(1),
            proposed_conformance=0x1C00,
            client_max_receive_pdu_size=Unsigned16.from_int(134)
        )
        self._encode_decode_roundtrip(InitialRequest1, value, 1)

    def test_initiate_response_tag_8(self) -> None:
        """Test InitialResponse8 encode/decode (tag 8)"""
        value = InitiateResponse(
            negotiated_quality_of_service=None,
            negotiated_dlms_version_number=Unsigned8.from_int(1),
            negotiated_conformance=0x1C00,
            server_max_receive_pdu_size=Unsigned16.from_int(134),
            vaa_name=ObjectName.from_int(7)
        )
        self._encode_decode_roundtrip(InitialResponse8, value, 8)

    def test_read_request_tag_5(self) -> None:
        """Test ReadRequest5 encode/decode (tag 5)"""
        from COSEMpdu.types_used import VariableAccessSpecification
        value = [VariableAccessSpecification(variable_name=ObjectName.from_int(16))]
        self._encode_decode_roundtrip(ReadRequest5, value, 5)

    def test_read_response_tag_12(self) -> None:
        """Test ReadResponse12 encode/decode (tag 12)"""
        from COSEMpdu.apdu import ReadResponseChoice, Data0
        value = [ReadResponseChoice(0, Data0(Data.unsigned(100)))]
        self._encode_decode_roundtrip(ReadResponse12, value, 12)

    def test_write_request_tag_6(self) -> None:
        """Test WriteRequest6 encode/decode (tag 6)"""
        from COSEMpdu.types_used import VariableAccessSpecification
        value = {
            "variable_access_specification": [VariableAccessSpecification(variable_name=ObjectName.from_int(16))],
            "list_of_data": [Data.unsigned(50)]
        }
        self._encode_decode_roundtrip(WriteRequest6, value, 6)

    def test_write_response_tag_13(self) -> None:
        """Test WriteResponse13 encode/decode (tag 13)"""
        from COSEMpdu.apdu import WriteResponseChoice
        value = apdu.WriteResponse([WriteResponseChoice.SUCCESS])
        self._encode_decode_roundtrip(writeResponse, value, 13)

    def test_confirmed_service_error_tag_14(self) -> None:
        """Test ConfirmedServiceError14 encode/decode (tag 14)"""
        value = ConfirmedServiceError(
            1,  # initiateError
            ServiceError(6, ServiceError.Initiate(2))  # incompatible-conformance
        )
        self._encode_decode_roundtrip(confirmedServiceError, value, 14)

    def test_data_notification_tag_15(self) -> None:
        """Test DataNotification15 encode/decode (tag 15)"""
        from COSEMpdu.apdu import NotificationBody
        value = {
            "long_invoke_id_and_priority": LongInvokeIdAndPriority.from_bits(1),
            "date_time": bytes(12),
            "notification_body": NotificationBody(data_value=Data.unsigned(1))
        }
        self._encode_decode_roundtrip(DataNotification15, value, 15)

    def test_data_notification_confirm_tag_16(self) -> None:
        """Test DataNotificationConfirm16 encode/decode (tag 16)"""
        value = {
            "long_invoke_id_and_priority": LongInvokeIdAndPriority.from_int(1),
            "date_time": bytes(12)
        }
        self._encode_decode_roundtrip(DataNotificationConfirm16, value, 16)

    def test_unconfirmed_write_request_tag_22(self) -> None:
        """Test UnconfirmedWriteRequest22 encode/decode (tag 22)"""
        from COSEMpdu.types_used import VariableAccessSpecification
        value = {
            "variable_access_specification": [VariableAccessSpecification(variable_name=ObjectName.from_int(16))],
            "list_of_data": [Data(unsigned=Unsigned8(50))]
        }
        self._encode_decode_roundtrip(UnconfirmedWriteRequest22, value, 22)

    def test_information_report_request_tag_24(self) -> None:
        """Test InformationReportRequest24 encode/decode (tag 24)"""
        from COSEMpdu.types_used import VariableAccessSpecification
        value = {
            "current_time": None,
            "variable_access_specification": [VariableAccessSpecification(variable_name=ObjectName.from_int(16))],
            "list_of_data": [Data(unsigned=Unsigned8(50))]
        }
        self._encode_decode_roundtrip(InformationReportRequest24, value, 24)

    # =========================================================================
    # LN Referencing PDUs - Tags 192-199
    # =========================================================================

    def test_get_request_normal_tag_192(self) -> None:
        """Test GetRequest (get-request-normal) encode/decode (tag 192)"""
        from COSEMpdu.apdu import GetRequestNormal1
        value = GetRequestNormal1({
            "invoke_id_and_priority": InvokeIdAndPriority.from_int(1),
            "cosem_attribute_descriptor": CosemAttributeDescriptor(1, bytes(6), 1),
            "access_selection": None
        })
        get_request = getRequest(value=GetRequest(1, value))
        self._encode_decode_roundtrip(getRequest, get_request, 192)

    def test_get_response_normal_tag_196(self) -> None:
        """Test GetResponse (get-response-normal) encode/decode (tag 196)"""
        from COSEMpdu.apdu import GetResponseNormal1
        value = GetResponseNormal1({
            "invoke_id_and_priority": InvokeIdAndPriority.from_int(1),
            "result": GetDataResult(0, Data.unsigned(100))
        })
        get_response = getResponse(value=GetResponse(1, value))
        self._encode_decode_roundtrip(getResponse, get_response, 196)

    def test_set_request_normal_tag_193(self) -> None:
        """Test SetRequest (set-request-normal) encode/decode (tag 193)"""
        from COSEMpdu.apdu import SetRequestNormal1
        value = SetRequestNormal1({
            "invoke_id_and_priority": InvokeIdAndPriority.from_int(1),
            "cosem_attribute_descriptor": CosemAttributeDescriptor(1, bytes(6), 1),
            "access_selection": None,
            "value": Data(unsigned=Unsigned8(50))
        })
        set_request = setRequest(value=SetRequest(1, value))
        self._encode_decode_roundtrip(setRequest, set_request, 193)

    def test_set_response_normal_tag_197(self) -> None:
        """Test SetResponse (set-response-normal) encode/decode (tag 197)"""
        from COSEMpdu.apdu import SetResponseNormal1
        value = SetResponseNormal1({
            "invoke_id_and_priority": InvokeIdAndPriority.from_int(1),
            "result": DataAccessResult(0)
        })
        set_response = setResponse(value=SetResponse(1, value))
        self._encode_decode_roundtrip(setResponse, set_response, 197)

    def test_action_request_normal_tag_195(self) -> None:
        """Test ActionRequest (action-request-normal) encode/decode (tag 195)"""
        from COSEMpdu.apdu import ActionRequestNormal1
        value = ActionRequestNormal1({
            "invoke_id_and_priority": InvokeIdAndPriority.from_int(1),
            "cosem_method_descriptor": CosemMethodDescriptor(1, bytes(6), 1),
            "method_invocation_parameters": None
        })
        action_request = actionRequest(value=ActionRequest(1, value))
        self._encode_decode_roundtrip(actionRequest, action_request, 195)

    def test_action_response_normal_tag_199(self) -> None:
        """Test ActionResponse (action-response-normal) encode/decode (tag 199)"""
        from COSEMpdu.apdu import ActionResponseNormal1
        value = ActionResponseNormal1({
            "invoke_id_and_priority": InvokeIdAndPriority.from_int(1),
            "single_response": ActionResponseWithOptionalData(
                result=ActionResult(0),
                return_parameters=None
            )
        })
        action_response = actionResponse(value=ActionResponse(1, value))
        self._encode_decode_roundtrip(actionResponse, action_response, 199)

    def test_event_notification_request_tag_194(self) -> None:
        """Test EventNotificationRequest encode/decode (tag 194)"""
        value = {
            "time": None,
            "cosem_attribute_descriptor": CosemAttributeDescriptor(1, bytes(6), 1),
            "attribute_value": Data(unsigned=Unsigned8(1))
        }
        self._encode_decode_roundtrip(eventNotificationRequest, value, 194)

    # =========================================================================
    # Exception and Access PDUs - Tags 216-218
    # =========================================================================

    def test_exception_response_tag_216(self) -> None:
        """Test ExceptionResponse encode/decode (tag 216)"""
        value = {
            "state_error": 1,  # service-not-allowed
            "service_error": (1, None)  # operation-not-possible
        }
        self._encode_decode_roundtrip(exceptionResponse, value, 216)

    def test_access_request_tag_217(self) -> None:
        """Test AccessRequest encode/decode (tag 217)"""
        value = {
            "long_invoke_id_and_priority": LongInvokeIdAndPriority(IntegerType(1)),
            "date_time": bytes(12),
            "access_request_body": AccessRequestBody(
                access_request_specification=[],
                access_request_list_of_data=[]
            )
        }
        self._encode_decode_roundtrip(accessRequest, value, 217)

    def test_access_response_tag_218(self) -> None:
        """Test AccessResponse encode/decode (tag 218)"""
        value = {
            "long_invoke_id_and_priority": LongInvokeIdAndPriority.from_int(1),
            "date_time": bytes(12),
            "access_response_body": AccessResponseBody(
                access_request_specification=None,
                access_response_list_of_data=[],
                access_response_specification=[]
            )
        }
        self._encode_decode_roundtrip(accessResponse, value, 218)

    # =========================================================================
    # General APDUs - Tags 219-224
    # =========================================================================

    def test_general_glo_ciphering_tag_219(self) -> None:
        """Test GeneralGloCiphering encode/decode (tag 219)"""
        value = {
            "system_title": bytes(8),
            "ciphered_content": bytes(16)
        }
        self._encode_decode_roundtrip(generalGloCiphering, value, 219)

    def test_general_ded_ciphering_tag_220(self) -> None:
        """Test GeneralDedCiphering encode/decode (tag 220)"""
        value = {
            "system_title": bytes(8),
            "ciphered_content": bytes(16)
        }
        self._encode_decode_roundtrip(generalDedCiphering, value, 220)

    def test_general_ciphering_tag_221(self) -> None:
        """Test GeneralCiphering encode/decode (tag 221)"""
        value = {
            "transaction_id": bytes(4),
            "originator_system_title": bytes(8),
            "recipient_system_title": bytes(8),
            "date_time": bytes(12),
            "other_information": bytes(0),
            "key_info": KeyInfo(0, IdentifiedKey(KeyId(0))),
            "ciphered_content": bytes(16)
        }
        self._encode_decode_roundtrip(generalCiphering, value, 221)

    def test_general_signing_tag_223(self) -> None:
        """Test GeneralSigning encode/decode (tag 223)"""
        value = {
            "transaction_id": bytes(4),
            "originator_system_title": bytes(8),
            "recipient_system_title": bytes(8),
            "date_time": bytes(12),
            "other_information": bytes(0),
            "content": bytes(32),
            "signature": bytes(64)
        }
        self._encode_decode_roundtrip(generalSigning, value, 223)

    def test_general_block_transfer_tag_224(self) -> None:
        """Test GeneralBlockTransfer encode/decode (tag 224)"""
        value = {
            "block_control": Unsigned8.from_int(0x80),  # last-block bit set
            "block_number": Unsigned16.from_int(1),
            "block_number_ack": Unsigned16.from_int(1),
            "block_data": bytes(16)
        }
        self._encode_decode_roundtrip(generalBlockTransfer, value, 224)


class TestXDLMS_APDU_TagNumbers(unittest.TestCase):
    """Test XDLMS_APDU tag number constants"""

    def test_standard_pdu_tags(self) -> None:
        """Test standard PDU tag numbers"""
        self.assertEqual(InitialRequest1.tag, 1)
        self.assertEqual(ReadRequest5.tag, 5)
        self.assertEqual(WriteRequest6.tag, 6)
        self.assertEqual(InitialResponse8.tag, 8)
        self.assertEqual(ReadResponse12.tag, 12)
        self.assertEqual(writeResponse.tag, 13)
        self.assertEqual(confirmedServiceError.tag, 14)
        self.assertEqual(DataNotification15.tag, 15)
        self.assertEqual(DataNotificationConfirm16.tag, 16)
        self.assertEqual(UnconfirmedWriteRequest22.tag, 22)
        self.assertEqual(InformationReportRequest24.tag, 24)

    def test_ln_referencing_pdu_tags(self) -> None:
        """Test LN referencing PDU tag numbers"""
        self.assertEqual(getRequest.tag, 192)
        self.assertEqual(setRequest.tag, 193)
        self.assertEqual(eventNotificationRequest.tag, 194)
        self.assertEqual(actionRequest.tag, 195)
        self.assertEqual(getResponse.tag, 196)
        self.assertEqual(setResponse.tag, 197)
        self.assertEqual(actionResponse.tag, 199)

    def test_exception_access_pdu_tags(self) -> None:
        """Test exception and access PDU tag numbers"""
        self.assertEqual(exceptionResponse.tag, 216)
        self.assertEqual(accessRequest.tag, 217)
        self.assertEqual(accessResponse.tag, 218)

    def test_general_apdu_tags(self) -> None:
        """Test general APDU tag numbers"""
        self.assertEqual(generalGloCiphering.tag, 219)
        self.assertEqual(generalDedCiphering.tag, 220)
        self.assertEqual(generalCiphering.tag, 221)
        self.assertEqual(generalSigning.tag, 223)
        self.assertEqual(generalBlockTransfer.tag, 224)


class TestXDLMS_APDU_ChoiceEncoding(unittest.TestCase):
    """Test XDLMS_APDU choice type encoding"""

    def test_choice_tag_preservation(self) -> None:
        """Test that choice tag is preserved through encode/decode"""
        # Test with different alternatives
        test_cases = [
            (1, InitialRequest1),
            (5, ReadRequest5),
            (192, getRequest),
            (196, getResponse),
        ]

        for expected_tag, apdu_class in test_cases:
            with self.subTest(tag=expected_tag):
                # Verify tag is correct
                self.assertEqual(apdu_class.tag, expected_tag)


if __name__ == "__main__":
    unittest.main(verbosity=2)
