import unittest
from typing import Type
from src.COSEMpdu import a_xdr, main as c_pdu, asn1
from src.COSEMpdu.byte_buffer import ByteBuffer as Buf


class TestType(unittest.TestCase):
    def test_Conformance(self):
        conf1 = c_pdu.Conformance.from_str("101001100100110010101101")
        buf = Buf.allocate(10)
        conf1.put(buf)
        print(F"{conf1}: {buf.buf.hex(' ')}")
        buf.set_pos(0)
        conf2 = c_pdu.Conformance.get(buf)
        self.assertEqual(conf1, conf2, "put-get check")

    def test_NullData(self):
        value = c_pdu.NullData.default()
        buf = Buf.allocate(10)
        value.put(buf)
        print(value, buf, buf.buf.hex(" "))
        value2 = c_pdu.NullData.from_str(" ")
        print(value2)

    def test_Boolean(self):
        buf = Buf(memoryview(b'\x03\x00'))
        value = c_pdu.Boolean.get(buf)
        print(value)

    def test_EnumeratedType(self):
        buf = Buf(memoryview(b'\x00\x03'))
        value = c_pdu.ApplicationReference.get(buf)
        value2 = c_pdu.ApplicationReference.from_int(3)
        buf2 = a_xdr.create_buf(value2)
        print(value)

    def test_ServiceError(self):
        buf = Buf(memoryview(b'\x00\x03'))
        value = c_pdu.ServiceError.get(buf)
        print(value, isinstance(value, c_pdu.ApplicationReference))
        enum1 = c_pdu.ApplicationReference.from_str("3")
        self.assertEqual(enum1, value)
        s_e = c_pdu.ServiceError.from_str("2:3")
        print(s_e)

    def test_ConfirmedServiceError(self):
        buf = Buf(memoryview(b'\x01\x00\x02'))
        value = c_pdu.ConfirmedServiceError.get(buf)
        print(value, isinstance(value, c_pdu.ApplicationReference))
        enum1 = c_pdu.ApplicationReference.from_str("2")
        self.assertEqual(enum1, value)

    def test_confirmedServiceError(self):
        buf = Buf(memoryview(b'\x0e\x01\x00\x02'))
        value = c_pdu.confirmedServiceError.get(buf)
        print(value, isinstance(value, c_pdu.ApplicationReference))
        enum1 = c_pdu.ApplicationReference.from_str("2")
        self.assertEqual(enum1, value)
        pdu = c_pdu.XDLMSAPDU(c_pdu.confirmedServiceError.from_str("2:2:2"))
        buf = Buf(memoryview(bytearray(100)))
        pdu.put(buf)
        print(pdu, buf.buf.hex(" "))

    def test_Bitstring(self):
        value = c_pdu.BitString.from_str("100101")
        print(value, value.to_list())
        buf = Buf(memoryview(b'\x04\x28\xff\xff\xff\xff\xff\xff'))
        value2 = c_pdu.BitString.get(buf)
        value2.inverse(2)
        print(value2, buf)

    def test_Optional2(self):
        # class MyOptional(a_xdr.Optional, a_xdr.IntegerType):
        #     """"""
        MyOptional = a_xdr.get_optional(a_xdr.IntegerType)
        buf = Buf(memoryview(b'\x00\x02\x05\x04'))
        value = MyOptional.get(buf)
        value2 = MyOptional.from_str("5")
        print(value)
        buf2 =Buf.allocate(10)
        value.put(buf2)
        print(buf2.buf.hex(" "))

    def test_initiate_req(self):
        value = c_pdu.InitiateRequest.from_str("031122,1, 4, 5, 101001100100110010101101, 6")
        buf = Buf(memoryview(bytearray(100)))
        value.dedicated_key
        value.put(buf)
        print(value, buf.buf.hex(' '))

    def test_put_APDU(self):
        pdu = c_pdu.XDLMSAPDU(c_pdu.initiateRequest.from_str("01 ,0,, 6, 101001100100110010101101, 128"))
        pdu.validation()
        buf = Buf(memoryview(bytearray(100)))
        pdu.put(buf)
        print(pdu, buf.buf.hex(" "))

    def test_Data(self):
        print(c_pdu.Data.get_elements())
        self.check_with_buf('00', c_pdu.Data)
        self.check_with_buf('0301', c_pdu.Data)
        self.check_with_buf('01020f010f02', c_pdu.Data)
        self.check_with_buf('01030f010f020f03', c_pdu.Data)

    def check_with_buf(self, value: str, type_: Type[asn1.Type]):
        data = bytes.fromhex(value)
        input_buf = Buf(memoryview(data))
        value = type_.get(input_buf)
        output_buf = Buf.allocate(len(data))
        value.put(output_buf)
        self.assertEqual(bytes(input_buf.buf), bytes(output_buf.buf), "check by contents")
        print(F"{value} - {output_buf}, {output_buf.buf.hex()}")

    def test_get_APDU(self):
        self.check_with_buf('01 00 00 00 06 5F 1F 04 00 00 7E 1F 04 B0', c_pdu.XDLMSAPDU)
        self.check_with_buf('01011000112233445566778899AABBCCDDEEFF0000065F1F0400007E1F04B0', c_pdu.XDLMSAPDU)
        self.check_with_buf('08 00 06 5F 1F 04 00 00 50 1F 01 F4 00 07', c_pdu.XDLMSAPDU)
        self.check_with_buf('0800065F1F0400007C1F04000007', c_pdu.XDLMSAPDU)
        self.check_with_buf('C0010000080000010000FF0200', c_pdu.XDLMSAPDU)
        self.check_with_buf('C0010000080000010000FF020103010100', c_pdu.XDLMSAPDU)

    def test_getRequestNormal(self):
        value = c_pdu.XDLMSAPDU(c_pdu.getRequest(c_pdu.getRequestNormal.from_elements(
            invoke_id_and_priority=c_pdu.InvokeIdAndPriority.from_int(3),
            # c_pdu.CosemAttributeDescriptor.from_str("8, 00 00 01 00 01 ff, 2"),
            cosem_attribute_descriptor=c_pdu.CosemAttributeDescriptor((
                c_pdu.CosemClassId.from_int(8),
                c_pdu.CosemObjectInstanceId.from_str("00 00 01 00 01 ff"),
                c_pdu.CosemObjectAttributeId.from_int(2)
            )),
            access_selection=c_pdu.SelectiveAccessDescriptorOptional.default()
            )))
        value2 = c_pdu.getRequest(c_pdu.getRequestNormal((
            c_pdu.InvokeIdAndPriority.from_int(3),
            # c_pdu.CosemAttributeDescriptor.from_str("8, 00 00 01 00 01 ff, 2"),
            c_pdu.CosemAttributeDescriptor((
                c_pdu.CosemClassId.from_int(8),
                c_pdu.CosemObjectInstanceId.from_str("00 00 01 00 01 ff"),
                c_pdu.CosemObjectAttributeId.from_int(2)
            )),
            c_pdu.SelectiveAccessDescriptorOptional.default()
            )))
        valueX = c_pdu.XDLMSAPDU(c_pdu.getRequest(c_pdu.getRequestNormal.from_str("3, (8, 00 00 01 00 01 ff, 2),")))
        buf = a_xdr.create_buf(value)
        buf2 = a_xdr.create_buf(value2)
        print(value, buf.buf.hex(" "))
        val_in = c_pdu.XDLMSAPDU.get(buf)
        print(val_in == value)

        value = c_pdu.XDLMSAPDU(c_pdu.getRequest(c_pdu.getRequestNormal.from_str("3, (7, 00 00 60 61 01 ff, 2), (1,5:0)")))
        buf = a_xdr.create_buf(value)
        print(value, buf.buf.hex(" "))
        self.assertEqual(buf.buf, bytes.fromhex("c0 01 03 00 07 00 00 60 61 01 ff 02 01 01 05 00 00 00 00 00"), "generate with selection")

    def test_getRequestWithList(self):
        value = c_pdu.XDLMSAPDU(c_pdu.getRequest(c_pdu.getRequestWithList.from_str("1, ((7, 00 00 68 67 00 ff, 2),(2,5:0);(8, 00 00 01 00 00 ff, 3),)")))
        buf = a_xdr.create_buf(value)
        print(value, buf.buf.hex(" "))

    def test_getResponse(self):
        class My(c_pdu.Structure):  # don't work this. think more!!!
            a: c_pdu.Integer
            b: c_pdu.Enum
            __slots__ = a_xdr._value

        # is pretty
        # buf = Buf(memoryview(bytes.fromhex("C4 01 81 00 09 06 01 00 15 07 00 FF")))
        buf = Buf(memoryview(bytes.fromhex("C4 01 81 00 02 02 0F FE 16 1B")))
        value: c_pdu.getResponseNormal = c_pdu.XDLMSAPDU.get(buf)
        res = value.result
        print(value, res)
        data_buf = a_xdr.create_buf(res)
        print(data_buf)
        
        value2 = My.get(data_buf)  # good. think as struct build in Response
        print(value2)

    def test_Array(self):
        IntegerArray = c_pdu.get_array_of(c_pdu.Integer)
        value = IntegerArray.from_str("1; 2; 3; 4")
        buf = a_xdr.create_buf(value)
        print(value, buf.buf.hex(" "))
        value2 = c_pdu.Data.get(buf)
        print(value2 == value)

    def test_Structure(self):
        class MyStruct(c_pdu.Structure):
            a: c_pdu.Integer
            b: c_pdu.Long
            c: c_pdu.Unsigned
            __slots__ = c_pdu._value

        value = MyStruct.from_str("1, 2, 3")
        buf = a_xdr.create_buf(value)
        print(value, buf.buf.hex(" "))
        value2 = c_pdu.Data.get(buf)
        print(value2 == value)

    def test_variableName(self):
        value = c_pdu.variableName.from_int(1)
        print(value)

    def test_ParameterizedAccess(self):
        value = c_pdu.ParameterizedAccess.from_str("1,1,3:1")
        print(value)

    def test_BlockNumberAccess(self):
        value = c_pdu.BlockNumberAccess.from_str("1")
        print(value)

    def test_readRequest(self):
        pdu = c_pdu.XDLMSAPDU(c_pdu.readRequest.from_str("2: 1; 4: 1, 1, 3:1; 5: 2"))
        pdu.validation()
        buf = Buf(memoryview(bytearray(100)))
        pdu.put(buf)
        print(pdu, buf.buf.hex(" "))

    def test_ActionRequest(self):
        pdu = c_pdu.XDLMSAPDU.from_str("195:1:1, (8, 00 00 01 00 00 ff, 3),")
        a_r = c_pdu.actionRequest.from_str("1:1, (8, 00 00 01 00 00 ff, 3),")
        a_r_n = c_pdu.actionRequestNormal.from_str("1, (8, 00 00 01 00 00 ff, 3),")
        a_r_n2 = c_pdu.ActionRequestNormal.from_str("1, (8, 00 00 01 00 00 ff, 3),3:1")
        a_r_n_pbb = c_pdu.actionRequestNextPblock.from_str("1, 1")
        a_r.value = a_r_n_pbb
        self.assertEqual(a_xdr.create_buf(a_r).buf, bytes.fromhex('c3 02 01 00 00 00 01 00'))
        a_r_wl = c_pdu.actionRequestWithList.from_str("1, (8, 00 00 01 00 00 ff, 3);(8, 00 00 01 00 00 ff, 2), 3:1;3:0")
        a_r_wl.invoke_id_and_priority.value = bytearray(b'\x02')
        # a_r_wl.invoke_id_and_priority = c_pdu.InvokeIdAndPriority.from_str("4")  todo: don't work, maybe make special <set> method
        a_r.value = a_r_wl
        print(F"! {a_xdr.create_buf(a_r).buf.hex(' ')}")
        buf = a_xdr.create_buf(pdu)
        buf2 = Buf(memoryview(bytearray(100)))
        pdu.put(buf2)
        print(a_r_n, a_r_n2, buf.buf.hex(" "), len(pdu))
        print(buf2.buf.hex(" "))

    def test_ReadResponse(self):
        pdu = c_pdu.XDLMSAPDU(c_pdu.ReadResponse_((c_pdu.Data_(c_pdu.Boolean.from_str("0")), c_pdu.Data_(c_pdu.Boolean.default()))))
        pdu = c_pdu.XDLMSAPDU(c_pdu.ReadResponse_((c_pdu.Data_.default(), c_pdu.Data_.default())))
        buf = a_xdr.create_buf(pdu)
        print(buf.buf.hex(" "))

    def test_sequence_of_Data(self):
        sofData = a_xdr.get_sequence_of(c_pdu.Data)
        data = sofData.from_str("3:1;3:0")
        print(data)

    def test_WriteRequest(self):
        w_r = c_pdu.WriteRequest_((
            c_pdu.SequenceOfVariableAccessSpecification((c_pdu.variableName.from_int(4),)),
            c_pdu.SequenceOfData((
                c_pdu.NullData.default(),
                c_pdu.Integer.from_int(10)
            ))
        ))
        w_r = c_pdu.WriteRequest_.from_elements(
            variable_access_specification=c_pdu.SequenceOfVariableAccessSpecification((c_pdu.variableName.from_int(4),)),
            list_of_data=c_pdu.SequenceOfData((
                c_pdu.NullData.default(),
                c_pdu.Integer.from_int(10))))
        pdu = c_pdu.XDLMSAPDU(w_r)
        buf = a_xdr.create_buf(pdu)
        print(buf.buf.hex(" "))

    def test_WriteResponse(self):
        w_r = c_pdu.WriteResponse_IMP((
            c_pdu.WriteResponseElement(c_pdu.Success()),
            c_pdu.WriteResponseElement(c_pdu.DataAccessResult_IMP.from_int(4)),
        ))
        pdu = c_pdu.XDLMSAPDU(w_r)
        buf = a_xdr.create_buf(pdu)
        self.assertEqual(buf.buf, bytes.fromhex("0d 02 00 01 04"))
        print(buf.buf.hex(" "))

    def test_SetRequest(self):
        s_r_n = c_pdu.setRequestNormal.from_elements(
            invoke_id_and_priority=c_pdu.InvokeIdAndPriority.from_int(10),
            cosem_attribute_descriptor=c_pdu.CosemAttributeDescriptor.from_elements(
                class_id=c_pdu.CosemClassId.from_int(8),
                instance_id=c_pdu.CosemObjectInstanceId.from_str("00 00 01 00 00 ff"),
                attribute_id=c_pdu.CosemObjectAttributeId.from_int(2)),
            access_selection=c_pdu.SelectiveAccessDescriptorOptional.default(),
            value_=c_pdu.Data(
                c_pdu.Unsigned.from_str("4")
            ))
        pdu = c_pdu.XDLMSAPDU(c_pdu.setRequest(s_r_n))
        buf = a_xdr.create_buf(pdu)
        print(buf.buf.hex(" "))
        self.assertEqual(buf.buf, bytes.fromhex("c1 01 0a 00 08 00 00 01 00 00 ff 02 00 11 04 00"))

    def test_AccessRequest(self):
        a_r = c_pdu.accessRequest.from_elements(
            long_invoke_id_and_priority=c_pdu.LongInvokeIdAndPriority.from_int(1073741824),
            date_time=a_xdr.OctetStringType.from_str(""),
            access_request_body=c_pdu.AccessRequestBody.from_elements(
                access_request_specification=c_pdu.ListOfAccessRequestSpecification((
                    c_pdu.AccessRequestSpecification(c_pdu.accessRequestGet.from_elements(
                        cosem_attribute_descriptor=c_pdu.CosemAttributeDescriptor.from_elements(
                            class_id=c_pdu.CosemClassId.from_int(8),
                            instance_id=c_pdu.CosemObjectInstanceId.from_str("00 01 02 03 04 05"),
                            attribute_id=c_pdu.CosemObjectAttributeId.from_int(2)),)),
                    c_pdu.AccessRequestSpecification(c_pdu.accessRequestSet.from_elements(
                        cosem_attribute_descriptor=c_pdu.CosemAttributeDescriptor.from_elements(
                            class_id=c_pdu.CosemClassId.from_int(8),
                            instance_id=c_pdu.CosemObjectInstanceId.from_str("07 01 02 03 04 05"),
                            attribute_id=c_pdu.CosemObjectAttributeId.from_int(3)),)),
                )),
                access_request_list_of_data=c_pdu.ListOfData((
                        c_pdu.Data(c_pdu.Unsigned.from_int(1)),
                        c_pdu.Data(c_pdu.NullData())
                ))
            )
        )
        pdu = c_pdu.XDLMSAPDU(a_r)
        buf = a_xdr.create_buf(pdu)
        print(buf.buf.hex(" "))

        buf = Buf.allocate(1000)
        buf.write(bytes.fromhex("D94000000000040100010000600100FF020100080000010000FF0202001"
                                "400000D0000FF0702001400000D0000FF0804000001040203090100090C"
                                "FFFFFFFFFFFFFF00000000000901FF0203090101090CFFFFFFFFFFFFFF0"
                                "0000000000901FF0203090102090CFFFFFFFFFFFFFF00000000000901FF"
                                "0203090103090CFFFFFFFFFFFFFF00000000000901FF010402080901001"
                                "1FF11FF11FF11FF11FF11FF11FF02080901011102110111011101110111"
                                "011101020809010211FF11FF11FF11FF11FF11FF11FF020809010311011"
                                "10211021102110211021102"))
        print(buf.set_pos(0))
        pdu = c_pdu.XDLMSAPDU.get(buf)
        print(pdu)
