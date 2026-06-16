import unittest
from src.COSEMpdu import x690
from src.COSEMpdu import byte_buffer as buffer
from src.COSEMpdu.ber import Tag
from src.COSEMpdu.x680 import Class


class TestType(unittest.TestCase):
    def test_Length(self) -> None:
        buf = buffer.ByteBuffer(memoryview(b"\x81\x83"))
        value = x690.Length.get(buf)
        buf_out = buffer.ByteBuffer.allocate(1000)
        value.put(buf_out)
        print(buf_out)
        self.assertEqual(0x83, value.value, "check __int__")

    def test_Tag(self) -> None:
        t = Tag(1, Class.UNIVERSAL)
        buf = buffer.ByteBuffer.allocate(10)
        self.assertEqual(t.put(buf), 1)
        self.assertEqual(bytes(buf.buf), b"\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        buf.set_pos(0)
        t = Tag(10, Class.APPLICATION)
        t.put(buf)
        self.assertEqual(bytes(buf.buf), b"\x4a\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        buf.set_pos(0)
        t = Tag(31, Class.APPLICATION)
        self.assertEqual(t.put(buf), 2)
        self.assertEqual(bytes(buf.buf), b"\x5f\x1f\x00\x00\x00\x00\x00\x00\x00\x00")
        buf.set_pos(0)
        t = Tag(3999, Class.APPLICATION)
        self.assertEqual(t.put(buf), 3)
        self.assertEqual(bytes(buf.buf), b"\x5f\x9f\x1f\x00\x00\x00\x00\x00\x00\x00")
        buf.set_pos(0)
        t = Tag(7777777, Class.APPLICATION)
        self.assertEqual(t.put(buf), 5)
        buf.set_pos(0)
        t2 = Tag.get(buf)
        print(t2)
        self.assertEqual(bytes(buf.buf), b"_\x83\xda\xdbq\x00\x00\x00\x00\x00")
