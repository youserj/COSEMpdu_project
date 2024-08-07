import unittest
from src.COSEMpdu import a_xdr, main as c_pdu, asn1
from src.COSEMpdu.byte_buffer import ByteBuffer as Buf
from sys import getsizeof


class TestType(unittest.TestCase):
    def test_Null(self):
        value = a_xdr.NullType.default()
        buf = a_xdr.create_buf(value)
        # buf = Buf.allocate(1)
        value.put(buf)
        print(value, buf.buf.hex(" "))
        value2 = a_xdr.NullType.from_str(" ")
        print(value2)

    def test_BooleanType(self):
        buf = Buf(memoryview(b'\x01'))
        value = a_xdr.BooleanType.get(buf)
        print(value, buf)

    def test_int(self):
        value = c_pdu.Integer8.from_int(125)
        print(value)
        value2 = c_pdu.Integer8.from_int(123)
        print(value == value2)

    def test_octet_string(self):
        value = c_pdu.OctetString.from_str("010203")
        print(value)
        value2 = c_pdu.OctetString4.default()
        value3 = c_pdu.OctetString.default()

    def test_to_buf(self):
        buf = Buf(memoryview(bytearray(100)))
        value = c_pdu.OctetString.from_str("31 32 33")
        value.put(buf)
        c_pdu.Integer8.default().put(buf)
        value.put(buf)
        print(str(buf), buf.buf.hex(' '))
        buf.set_pos(0)
        print(str(buf), buf.buf.hex(' '))
        value2 = c_pdu.OctetString.get(buf)
        print(value2)
        value3 = c_pdu.Unsigned16.get(buf)
        print(value3)
        print(str(buf), buf.buf.hex(' '))

    def test_simple_sequence(self):
        class MySeq(a_xdr.SequenceType):
            __slots__ = ("values",)
            x: c_pdu.Integer8
            y: c_pdu.Unsigned16

        buf = Buf(memoryview(b'1234'))
        value = MySeq.get(buf)
        print(value)
        value = MySeq.from_str("1 4")
        print(value)
        buf = Buf(memoryview(bytearray(10)))
        value.put(buf)
        print(buf)
        value = MySeq.default()
        print(value.x)

    def test_Optional(self):
        class OptionalInteger8(a_xdr.Optional, c_pdu.Integer8):
            __slots__ = a_xdr._value


        value = OptionalInteger8.from_str("13")
        buf = Buf(memoryview(bytearray(10)))
        value.put(buf)
        print(value)
        buf = Buf(memoryview(b'\x041234'))
        value = OptionalInteger8.get(buf)
        print(value)

    def test_choice(self):
        value = c_pdu.Data.from_str("5: 4")
        print(value)
        value = c_pdu.Data(c_pdu.Integer64.from_int(1030))
        buf = Buf(memoryview(bytearray(10)))
        value.put(buf)
        print(bytes(buf), buf)
        buf.set_pos(0)
        value = c_pdu.Data.get(buf)
        print(value)
        value = c_pdu.Data.from_str("1: 5:4; 5:2; 9:31 32 33")
        buf = Buf(memoryview(bytearray(19)))
        value.put(buf)
        print(value, bytes(buf).hex(" "))
        print(len(value))

    def test_create_buf(self):
        value = c_pdu.Data.from_str("1: 5:4; 5:2; 9:31 32 33")
        # value = pdu.Data.from_str("1: 3:True")
        buf = a_xdr.create_buf(value)
        value2 = c_pdu.Data.get(buf)
        print(buf, value2)
        print(getsizeof(buf))
        print(getsizeof(value))
        print(getsizeof(value2))

    def test_BitstringType(self):
        value = a_xdr.BitStringType.from_str("100101")
        print(value, value.to_list())
        buf = Buf(memoryview(b'\x28\xff\xff\xff\xff\xff\xff'))
        value2 = a_xdr.BitStringType.get(buf)
        value2.inverse(2)
        print(value2, buf)

    def test_decide_len(self):
        a = -108473286571685614323
        z = (a.bit_length() >> 3) + 1
        y = a.to_bytes(z, "big", signed=True)
        print(y, z, hex(a))

    def test_IntegerType(self):
        value = a_xdr.IntegerType.from_int(1444)
        buf = Buf(memoryview(bytearray(100)))
        value.put(buf)
        print(value, bytes(buf).hex(" "))

    def test_EXPLICIT(self):
        pass
        # class NewInteger(a_xdr.EXPLICIT):
        #     Type = a_xdr.IntegerType
        #     Tag = asn1.Tag(4)
        #
        # buf = Buf(memoryview(bytearray(10)))
        # value = NewInteger.from_int(1)
        # value.put(buf)
        # print(value, '-', bytes(buf).hex(" "))

