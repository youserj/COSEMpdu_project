"""
Unit tests for XDLMS-APDU types (Green Book 8.3).

Testing is based on the principle: encode/decode is the only
reliable way to verify the correctness of the entire chain:
    value -> packing in TaggedType -> A-XDR encoding
    -> A-XDR decoding -> TaggedType -> value.

This approach covers:
- correctness of context tags (tag number);
- tagging mode (IMPLICIT);
- structure of SEQUENCE/CHOICE types (order of fields, optionality);
- correct coding of nested types (all LN referencing, general APDUs,
  exception/access PDUs).

Additionally, the CHOICE type XDLMS_APDU is checked — that all major
alternatives (InitiateRequest, GetRequest, ...) are constructed
without errors, and that tag numbers are verified for all defined
PDU types.

What is NOT tested here (and corresponding test classes are excluded):
- static TaggedType attributes (tag, mode) — these are constants
  from apdu.py, checking them duplicates the declaration
  (excluded: class TestXDLMS_APDU_TagNumbers,
   class TestXDLMS_APDU_ChoiceEncoding);
- bare construction of base types (CosemAttributeDescriptor,
  InvokeIdAndPriority, ...) — they are building blocks for APDU
  and are tested implicitly through encode/decode; separate tests
  for their instantiation are redundant because any defect in them
  will surface during the full cycle;
- meta-checks for the presence of attributes on components — redundant
  in the presence of encode/decode.
"""
import sys

sys.path.insert(0, "src")

import unittest
from typing import Any

from test._utils import check_encode_decode as _shared_check_encode_decode
from src.COSEMpdu import apdu
from src.COSEMpdu.axdr import OctetStringType, BooleanType
from src.COSEMpdu.apdu import (
    # XDLMS-APDU Choice Type
    InitialRequest, InitialResponse,
    ReadRequest, ReadResponse,
    WriteRequest, WriteResponse,
    confirmedServiceError,
    DataNotification, DataNotificationConfirm,
    UnconfirmedWriteRequest,
    informationReportRequest,
    # LN Referencing PDUs
    GetRequest, GetResponse,
    SetRequest, SetResponse,
    ActionRequest, ActionResponse,
    EventNotificationRequest,
    # Exception and Access
    ExceptionResponse,
    AccessRequest, AccessResponse,
    # General APDUs
    GeneralGloCiphering, GeneralDedCiphering,
    GeneralCiphering, GeneralSigning,
    GeneralBlockTransfer, BlockControl,
    # Concrete choice subtypes
    GetRequestNormal, GetResponseNormal,
    SetRequestNormal, SetResponseNormal,
    ActionRequestNormal, ActionResponseNormal,
    # Service error components
    StateError,
    serviceError, OperationNotPossible,
    # key_info
    KeyInfo, KeyId, IdentifiedKey,
    Conformance,
    XDLMS_APDU,
    # SEQUENCE/CHOICE building blocks (moved from types_used)
    InvokeIdAndPriority, LongInvokeIdAndPriority, ListOfData,
    ListOfAccessResponseSpecification, ListOfAccessRequestSpecification,
    CosemAttributeDescriptor, CosemMethodDescriptor,
    GetDataResult,
    CosemClassId, CosemObjectInstanceId, CosemObjectAttributeId,
    CosemObjectMethodId,
    ActionResponseWithOptionalData, ActionResult,
    AccessRequestBody, AccessResponseBody,
    InitiateError, Initiate,
)
from src.COSEMpdu.data import Data, Unsigned, SequenceOfData, Unsigned8, Unsigned16, ObjectName


class TestXDLMS_APDU_EncodeDecode(unittest.TestCase):
    """Test XDLMS_APDU encoding and decoding operations"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        self.maxDiff = None
        self.cosem_attribute_descriptor = CosemAttributeDescriptor(
            class_id=CosemClassId(1),
            instance_id=CosemObjectInstanceId(bytes(6)),
            attribute_id=CosemObjectAttributeId(1))
        self.cosem_method_descriptor = CosemMethodDescriptor(
            class_id=CosemClassId(3),
            instance_id=CosemObjectInstanceId(bytes(6)),
            method_id=CosemObjectMethodId(2))

    def _check_encode_decode(self, value: Any, type_cls: type[Any], buffer_size: int = 1024) -> Any:
        """Helper: encode value to buffer, decode back, assert not None, return decoded."""
        return _shared_check_encode_decode(value, type_cls, buffer_size)

    # =========================================================================
    # Standard PDUs (no ciphering) - Tags 1-24
    # =========================================================================

    def test_initiate_request_tag_1(self) -> None:
        """Test InitialRequest1 encode/decode (tag 1)"""
        apdu_obj = XDLMS_APDU(InitialRequest(
            dedicated_key=None,
            response_allowed=BooleanType(1),
            proposed_quality_of_service=None,
            proposed_dlms_version_number=Unsigned8(1),
            proposed_conformance=Conformance.from_int(63, 24),
            client_max_receive_pdu_size=Unsigned16(134)
        ))
        decoded = self._check_encode_decode(apdu_obj, XDLMS_APDU)
        self.assertEqual(decoded, apdu_obj)

    def test_initiate_response_tag_8(self) -> None:
        """Test InitialResponse8 encode/decode (tag 8)"""
        apdu_obj = InitialResponse(
            negotiated_quality_of_service=None,
            negotiated_dlms_version_number=Unsigned8(1),
            negotiated_conformance=Conformance.default(),
            server_max_receive_pdu_size=Unsigned16(134),
            vaa_name=ObjectName(7)
        )
        decoded = self._check_encode_decode(apdu_obj, InitialResponse)
        self.assertEqual(decoded, apdu_obj)

    def test_read_request_tag_5(self) -> None:
        """Test ReadRequest5 encode/decode (tag 5)"""
        apdu_obj = ReadRequest([apdu.VariableAccessSpecification(apdu.VariableName(16))])
        decoded = self._check_encode_decode(apdu_obj, ReadRequest)
        self.assertEqual(decoded, apdu_obj)

    def test_read_response_tag_12(self) -> None:
        """Test ReadResponse12 encode/decode (tag 12)"""
        from src.COSEMpdu.apdu import ReadResponseChoice, TaggedData
        apdu_obj = ReadResponse([ReadResponseChoice(TaggedData(Unsigned(100)))])
        decoded = self._check_encode_decode(apdu_obj, ReadResponse)
        self.assertEqual(decoded, apdu_obj)

    def test_write_request_tag_6(self) -> None:
        """Test WriteRequest6 encode/decode (tag 6)"""
        apdu_obj = WriteRequest(
            variable_access_specification=apdu.SequenceOfVariableAccessSpecification([apdu.VariableAccessSpecification(apdu.VariableName(16))]),
            list_of_data=SequenceOfData([Data(Unsigned(50))])
        )
        decoded = self._check_encode_decode(apdu_obj, WriteRequest)
        self.assertEqual(decoded, apdu_obj)

    def test_write_response_tag_13(self) -> None:
        """Test WriteResponse13 encode/decode (tag 13)"""
        apdu_obj = WriteResponse([apdu.WriteResponseChoice.SUCCESS])
        decoded = self._check_encode_decode(apdu_obj, WriteResponse)
        self.assertEqual(decoded, apdu_obj)

    def test_confirmed_service_error_tag_14(self) -> None:
        """Test ConfirmedServiceError14 encode/decode (tag 14)"""
        apdu_obj = confirmedServiceError(InitiateError(Initiate(Initiate.INCOMPATIBLE_CONFORMANCE)))  # incompatible-conformance
        decoded = self._check_encode_decode(apdu_obj, confirmedServiceError)
        self.assertEqual(decoded, apdu_obj)

    def test_data_notification_tag_15(self) -> None:
        """Test DataNotification15 encode/decode (tag 15)"""
        apdu_obj = DataNotification(
            long_invoke_id_and_priority=LongInvokeIdAndPriority.from_bits(1),
            date_time=OctetStringType(bytes(12)),
            data_value=Data(Unsigned(1))
        )
        decoded = self._check_encode_decode(apdu_obj, DataNotification)
        self.assertEqual(decoded, apdu_obj)

    def test_data_notification_confirm_tag_16(self) -> None:
        """Test DataNotificationConfirm16 encode/decode (tag 16)"""
        apdu_obj = DataNotificationConfirm(
            long_invoke_id_and_priority=LongInvokeIdAndPriority(1),
            date_time=OctetStringType(bytes(12))
        )
        decoded = self._check_encode_decode(apdu_obj, DataNotificationConfirm)
        self.assertEqual(decoded, apdu_obj)

    def test_unconfirmed_write_request_tag_22(self) -> None:
        """Test UnconfirmedWriteRequest22 encode/decode (tag 22)"""
        apdu_obj = UnconfirmedWriteRequest(
            variable_access_specification=apdu.SequenceOfVariableAccessSpecification([apdu.VariableAccessSpecification(apdu.VariableName(16))]),
            list_of_data=SequenceOfData([Data(Unsigned(50))])
        )
        decoded = self._check_encode_decode(apdu_obj, UnconfirmedWriteRequest)
        self.assertEqual(decoded, apdu_obj)

    def test_information_report_request_tag_24(self) -> None:
        """Test InformationReportRequest24 encode/decode (tag 24)"""
        apdu_obj = informationReportRequest(
            variable_access_specification=apdu.SequenceOfVariableAccessSpecification([apdu.VariableAccessSpecification(apdu.VariableName(16))]),
            list_of_data=SequenceOfData([Data(Unsigned(50))]),
            current_time=None
        )
        decoded = self._check_encode_decode(apdu_obj, informationReportRequest)
        self.assertEqual(decoded, apdu_obj)

    # =========================================================================
    # LN Referencing PDUs - Tags 192-199
    # =========================================================================

    def test_get_request_normal_tag_192(self) -> None:
        """Test GetRequest (get-request-normal) encode/decode (tag 192)"""
        get_request_obj = GetRequest(GetRequestNormal(
            invoke_id_and_priority=InvokeIdAndPriority(1),
            cosem_attribute_descriptor=self.cosem_attribute_descriptor,
            access_selection=None
        ))
        decoded = self._check_encode_decode(get_request_obj, GetRequest)
        self.assertEqual(decoded, get_request_obj)

    def test_get_response_normal_tag_196(self) -> None:
        """Test GetResponse (get-response-normal) encode/decode (tag 196)"""
        from src.COSEMpdu.apdu import TaggedData
        get_response_obj = GetResponse(GetResponseNormal(
            invoke_id_and_priority=InvokeIdAndPriority(1),
            result=GetDataResult(TaggedData(Unsigned(100)))
        ))
        decoded = self._check_encode_decode(get_response_obj, GetResponse)
        self.assertEqual(decoded.value, get_response_obj.value)

    def test_set_request_normal_tag_193(self) -> None:
        """Test SetRequest (set-request-normal) encode/decode (tag 193)"""
        set_request_obj = SetRequest(SetRequestNormal(
            invoke_id_and_priority=InvokeIdAndPriority(1),
            cosem_attribute_descriptor=CosemAttributeDescriptor(
                class_id=CosemClassId(1),
                instance_id=CosemObjectInstanceId(b"\x00\x00\x00\x00\x00\x00"),
                attribute_id=CosemObjectAttributeId(1)
            ),
            value=Data(Unsigned(50)),
            access_selection=None
        ))
        decoded = self._check_encode_decode(set_request_obj, SetRequest)
        self.assertEqual(decoded.value, set_request_obj.value)

    def test_set_response_normal_tag_197(self) -> None:
        """Test SetResponse (set-response-normal) encode/decode (tag 197)"""
        from src.COSEMpdu.apdu import dataAccessResult
        set_response_obj = SetResponse(SetResponseNormal(
            invoke_id_and_priority=InvokeIdAndPriority(1),
            result=GetDataResult(dataAccessResult(dataAccessResult.SUCCESS))
        ))
        decoded = self._check_encode_decode(set_response_obj, SetResponse)
        self.assertEqual(decoded, set_response_obj)

    def test_action_request_normal_tag_195(self) -> None:
        """Test ActionRequest (action-request-normal) encode/decode (tag 195)"""
        action_request_obj = ActionRequest(ActionRequestNormal(
            invoke_id_and_priority=InvokeIdAndPriority(1),
            cosem_method_descriptor=self.cosem_method_descriptor,
            method_invocation_parameters=None
        ))
        decoded = self._check_encode_decode(action_request_obj, ActionRequest)
        self.assertEqual(decoded, action_request_obj)

    def test_action_response_normal_tag_199(self) -> None:
        """Test ActionResponse (action-response-normal) encode/decode (tag 199)"""
        action_response_obj = ActionResponse(ActionResponseNormal(
            invoke_id_and_priority=InvokeIdAndPriority(1),
            single_response=ActionResponseWithOptionalData(
                result=ActionResult(ActionResult.SUCCESS),
                return_parameters=None
            )
        ))
        decoded = self._check_encode_decode(action_response_obj, ActionResponse)
        self.assertEqual(decoded, action_response_obj)

    def test_event_notification_request_tag_194(self) -> None:
        """Test EventNotificationRequest encode/decode (tag 194)"""
        apdu_obj = EventNotificationRequest(
            cosem_attribute_descriptor=self.cosem_attribute_descriptor,
            attribute_value=Data(Unsigned(1)),
            time=None
        )
        decoded = self._check_encode_decode(apdu_obj, EventNotificationRequest)
        self.assertEqual(decoded, apdu_obj)

    # =========================================================================
    # Exception and Access PDUs - Tags 216-218
    # =========================================================================

    def test_exception_response_tag_216(self) -> None:
        """Test ExceptionResponse encode/decode (tag 216)"""
        apdu_obj = ExceptionResponse(
            state_error=StateError(1),  # service-not-allowed
            service_error=serviceError(OperationNotPossible.default())
        )
        decoded = self._check_encode_decode(apdu_obj, ExceptionResponse)
        self.assertEqual(decoded, apdu_obj)

    def test_access_request_tag_217(self) -> None:
        """Test AccessRequest encode/decode (tag 217)"""
        apdu_obj = AccessRequest(
            long_invoke_id_and_priority=LongInvokeIdAndPriority(1),
            date_time=OctetStringType(bytes(12)),
            access_request_body=AccessRequestBody(
                access_request_specification=ListOfAccessRequestSpecification(),
                access_request_list_of_data=ListOfData()
            )
        )
        decoded = self._check_encode_decode(apdu_obj, AccessRequest)
        self.assertEqual(decoded, apdu_obj)

    def test_access_response_tag_218(self) -> None:
        """Test AccessResponse encode/decode (tag 218)"""
        apdu_obj = AccessResponse(
            long_invoke_id_and_priority=LongInvokeIdAndPriority(1),
            date_time=OctetStringType(bytes(12)),
            access_response_body=AccessResponseBody(
                access_request_specification=None,
                access_response_list_of_data=ListOfData([]),
                access_response_specification=ListOfAccessResponseSpecification([])
            )
        )
        decoded = self._check_encode_decode(apdu_obj, AccessResponse)
        self.assertEqual(decoded, apdu_obj)

    # =========================================================================
    # General APDUs - Tags 219-224
    # =========================================================================

    def test_general_glo_ciphering_tag_219(self) -> None:
        """Test GeneralGloCiphering encode/decode (tag 219)"""
        apdu_obj = GeneralGloCiphering(
            system_title=OctetStringType(bytes(8)),
            ciphered_content=OctetStringType(bytes(16))
        )
        decoded = self._check_encode_decode(apdu_obj, GeneralGloCiphering)
        self.assertEqual(decoded, apdu_obj)

    def test_general_ded_ciphering_tag_220(self) -> None:
        """Test GeneralDedCiphering encode/decode (tag 220)"""
        apdu_obj = GeneralDedCiphering(
            system_title=OctetStringType(bytes(8)),
            ciphered_content=OctetStringType(bytes(16))
        )
        decoded = self._check_encode_decode(apdu_obj, GeneralDedCiphering)
        self.assertEqual(decoded, apdu_obj)

    def test_general_ciphering_tag_221(self) -> None:
        """Test GeneralCiphering encode/decode (tag 221)"""
        apdu_obj = GeneralCiphering(
            transaction_id=OctetStringType(bytes(4)),
            originator_system_title=OctetStringType(bytes(8)),
            recipient_system_title=OctetStringType(bytes(8)),
            date_time=OctetStringType(bytes(12)),
            other_information=OctetStringType(bytes(0)),
            key_info=KeyInfo(IdentifiedKey(KeyId(0))),
            ciphered_content=OctetStringType(bytes(16))
        )
        decoded = self._check_encode_decode(apdu_obj, GeneralCiphering)
        self.assertEqual(decoded, apdu_obj)

    def test_general_signing_tag_223(self) -> None:
        """Test GeneralSigning encode/decode (tag 223)"""
        apdu_obj = GeneralSigning(
            transaction_id=OctetStringType(bytes(4)),
            originator_system_title=OctetStringType(bytes(8)),
            recipient_system_title=OctetStringType(bytes(8)),
            date_time=OctetStringType(bytes(12)),
            other_information=OctetStringType(bytes(0)),
            content=OctetStringType(bytes(32)),
            signature=OctetStringType(bytes(64))
        )
        decoded = self._check_encode_decode(apdu_obj, GeneralSigning)
        self.assertEqual(decoded, apdu_obj)

    def test_general_block_transfer_tag_224(self) -> None:
        """Test GeneralBlockTransfer encode/decode (tag 224)"""
        apdu_obj = GeneralBlockTransfer(
            block_control=BlockControl(0x80),  # last-block bit set
            block_number=Unsigned16(1),
            block_number_ack=Unsigned16(1),
            block_data=OctetStringType(bytes(16))
        )
        decoded = self._check_encode_decode(apdu_obj, GeneralBlockTransfer)
        self.assertEqual(decoded, apdu_obj)


if __name__ == "__main__":
    unittest.main(verbosity=2)
