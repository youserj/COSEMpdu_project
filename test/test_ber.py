import unittest
from src.COSEMpdu import ber, main as c_pdu, asn1, byte_buffer as bb
from sys import getsizeof


class TestType(unittest.TestCase):
    # def test_Null(self):
    #     value = a_xdr.NULL
    #     print(value)
    #
    # def test_Boolean(self):
    #     buf = a_xdr.Buffer(memoryview(b'\x01\x00'))
    #     value = a_xdr.BooleanType.get(buf)
    #     print(value)
    #
    # def test_int(self):
    #     value = c_pdu.Integer8.from_int(125)
    #     print(value)
    #     value2 = c_pdu.Integer8.from_int(123)
    #     print(value == value2)
    #
    # def test_octet_string(self):
    #     value = c_pdu.OctetString.from_str("010203")
    #     print(value)
    #     value2 = c_pdu.OctetString4.default()
    #     value3 = c_pdu.OctetString.default()
    #
    # def test_to_buf(self):
    #     buf = a_xdr.Buffer(memoryview(bytearray(100)))
    #     value = c_pdu.OctetString.from_str("31 32 33")
    #     value.put(buf)
    #     c_pdu.Integer8.default().put(buf)
    #     value.put(buf)
    #     print(str(buf), buf.buf.hex(' '))
    #     buf.set_pos(0)
    #     print(str(buf), buf.buf.hex(' '))
    #     value2 = c_pdu.OctetString.get(buf)
    #     print(value2)
    #     value3 = c_pdu.Unsigned16.get(buf)
    #     print(value3)
    #     print(str(buf), buf.buf.hex(' '))
    #
    # def test_simple_sequence(self):
    #     class MySeq(a_xdr.SequenceType):
    #         __slots__ = ("values",)
    #         x: c_pdu.Integer8
    #         y: c_pdu.Unsigned16
    #
    #     buf = a_xdr.Buffer(memoryview(b'1234'))
    #     value = MySeq.get(buf)
    #     print(value)
    #     value = MySeq.from_str("1 4")
    #     print(value)
    #     buf = a_xdr.Buffer(memoryview(bytearray(10)))
    #     value.put(buf)
    #     print(buf)
    #     value = MySeq.default()
    #     print(value.x)
    #
    # def test_Optional(self):
    #     opt = a_xdr.get_optional(c_pdu.Integer8)
    #     value = opt.from_str("13")
    #     buf = a_xdr.Buffer(memoryview(bytearray(10)))
    #     value.put(buf)
    #     print(value)
    #     buf = a_xdr.Buffer(memoryview(b'\x041234'))
    #     value = a_xdr.get_optional(c_pdu.Integer8).get(buf)
    #     print(value)
    #
    # def test_choice(self):
    #     value = c_pdu.Data.from_str("5: 4")
    #     print(value)
    #     value = c_pdu.Data(c_pdu.Integer64.from_int(1030))
    #     buf = a_xdr.Buffer(memoryview(bytearray(10)))
    #     value.put(buf)
    #     print(bytes(buf), buf)
    #     buf.set_pos(0)
    #     value = c_pdu.Data.get(buf)
    #     print(value)
    #     value = c_pdu.Data.from_str("1: 5:4; 5:2; 9:31 32 33")
    #     buf = a_xdr.Buffer(memoryview(bytearray(19)))
    #     value.put(buf)
    #     print(value, bytes(buf).hex(" "))
    #     print(len(value))
    #
    # def test_create_buf(self):
    #     value = c_pdu.Data.from_str("1: 5:4; 5:2; 9:31 32 33")
    #     # value = pdu.Data.from_str("1: 3:True")
    #     buf = a_xdr.create_buf(value)
    #     value2 = c_pdu.Data.get(buf)
    #     print(buf, value2)
    #     print(getsizeof(buf))
    #     print(getsizeof(value))
    #     print(getsizeof(value2))

    def test_bitstring(self):
        value = ber.BitStringType.from_str("1001011001001111001010101010")
        buf = bb.ByteBuffer.allocate(100)
        value.put(buf)
        print(value, value.to_list(), buf.buf.hex(" "))
        buf = bb.ByteBuffer(memoryview(b'\x03\x05\x03\xff\xff\xff\xff'))
        value2 = ber.BitStringType.get(buf)
        value2.inverse(2)
        print(value2, buf)