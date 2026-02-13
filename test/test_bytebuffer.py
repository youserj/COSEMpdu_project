import unittest
from src.COSEMpdu.byte_buffer import ByteBuffer


class TestType(unittest.TestCase):
    def test_write_and_read_roundtrip(self):
        buf = ByteBuffer.allocate(10)
        self.assertEqual(buf.get_pos(), 0)
        written = buf.write(b'ABC')
        self.assertEqual(written, 3)
        self.assertEqual(buf.get_pos(), 3)

        buf.set_pos(0)
        self.assertEqual(bytes(buf.read(3)), b'ABC')
        self.assertEqual(buf.get_pos(), 3)

    def test_read_beyond_raises(self):
        buf = ByteBuffer.allocate(2)
        buf.write(b'AB')
        with self.assertRaises(BufferError):
            buf.read(3)

    def test_write_beyond_capacity_raises(self):
        buf = ByteBuffer.allocate(2)
        with self.assertRaises(BufferError):
            buf.write(b'ABC')

    def test_frozen_is_readonly(self):
        buf = ByteBuffer.allocate(3)
        buf.write(b'ABC')
        frozen = buf.frozen()
        self.assertTrue(frozen.buf.readonly)
        with self.assertRaises(TypeError):
            frozen.put_uint8(0x44)  # 'D'

    def test_set_and_shift_pos(self):
        buf = ByteBuffer.allocate(5)
        buf.write(b'12345')

        buf.set_pos(2)
        self.assertEqual(buf.get_pos(), 2)

        old = buf.shift_pos(2)
        self.assertEqual(old, 2)
        self.assertEqual(buf.get_pos(), 4)

        with self.assertRaises(IndexError):
            buf.set_pos(5)  # equal to len(buf) is invalid per implementation
        with self.assertRaises(IndexError):
            buf.set_pos(-1)

    # Additional comprehensive tests
    def test_allocate_and_len_and_bytes(self):
        buf = ByteBuffer.allocate(4)
        self.assertEqual(len(buf), 4)
        self.assertEqual(bytes(buf), b"\x00\x00\x00\x00")
        self.assertFalse(buf.buf.readonly)

    def test_wrap_and_read(self):
        data = b"hello"
        buf = ByteBuffer.wrap(data)
        self.assertEqual(len(buf), len(data))
        self.assertTrue(buf.buf.readonly)
        self.assertEqual(bytes(buf.read(5)), data)
        self.assertEqual(buf.get_pos(), 5)
        with self.assertRaises(BufferError):
            buf.read(1)

    def test_remaining_and_zero_length_read_write(self):
        buf = ByteBuffer.allocate(3)
        self.assertEqual(buf.remaining(), 3)

        # zero-length read should not move position
        mv = buf.read(0)
        self.assertEqual(len(mv), 0)
        self.assertEqual(buf.get_pos(), 0)

        # zero-length write via empty payload
        wrote = buf.write(b"")
        self.assertEqual(wrote, 0)
        self.assertEqual(buf.get_pos(), 0)
        self.assertEqual(buf.remaining(), 3)

    def test_put_get_uint8_and_get(self):
        buf = ByteBuffer.allocate(2)
        buf.put_uint8(0x41)  # 'A'
        self.assertEqual(buf.get_pos(), 1)

        buf.set_pos(0)
        self.assertEqual(buf.get_uint8(), 0x41)

        buf.set_pos(0)
        self.assertEqual(buf.get(), b"A")

    def test_get_uint_and_get_uint_pos(self):
        buf = ByteBuffer.allocate(4)
        buf.write(b"\x01\x02\x03\x04")
        buf.set_pos(0)
        self.assertEqual(buf.get_uint(2), 0x0102)
        # zero-length int should be zero and not move position
        self.assertEqual(buf.get_uint(0), 0)

        # get_uint_pos reads without changing current position
        self.assertEqual(buf.get_uint_pos(1, 2), 0x0203)
        self.assertEqual(buf.get_pos(), 2)  # from first get_uint(2)

        # reading past end by position should raise
        with self.assertRaises(BufferError):
            buf.get_uint_pos(3, 2)

    def test_read_pos_and_write_pos_behavior_and_errors(self):
        buf = ByteBuffer.allocate(4)
        buf.write(b"WXYZ")

        # read_pos should not move current position
        self.assertEqual(bytes(buf.read_pos(1, 2)), b"XY")
        self.assertEqual(buf.get_pos(), 4)

        # write_pos should not move current position and should update content
        buf.write_pos(b"12", 0)
        self.assertEqual(bytes(buf), b"12YZ")
        self.assertEqual(buf.get_pos(), 4)

        # mismatched explicit length should raise due to slice size mismatch
        with self.assertRaises(ValueError):
            buf.write_pos(b"ABC", 0, length=2)

        # writing beyond capacity should raise BufferError
        with self.assertRaises(BufferError):
            buf.write_pos(b"ABCD", 2)

    def test_slice_and_independent_position(self):
        buf = ByteBuffer.allocate(5)
        buf.write(b"abcde")
        buf.set_pos(2)
        sliced = buf.slice()
        self.assertEqual(bytes(sliced), b"cde")
        self.assertEqual(len(sliced), 3)
        self.assertEqual(sliced.get_pos(), 0)

        sliced.read(1)
        self.assertEqual(sliced.get_pos(), 1)
        # original buffer position should remain unchanged
        self.assertEqual(buf.get_pos(), 2)

    def test_getitem_and_str_contains(self):
        buf = ByteBuffer.allocate(3)
        buf.write(b"AbC")
        self.assertEqual(buf[1], ord("b"))
        s = str(buf)
        self.assertIn("ByteBuffer", s)
        self.assertIn("pos=", s)
        self.assertIn("frozen=", s)

    def test_remaining_with_pos_parameter(self):
        buf = ByteBuffer.allocate(10)
        buf.set_pos(3)
        self.assertEqual(buf.remaining(), 7)
        self.assertEqual(buf.remaining(5), 5)
        self.assertEqual(buf.remaining(0), 10)

    def test_set_pos_on_empty_buffer_noop(self):
        buf = ByteBuffer.allocate(0)
        # Should not raise, and position stays 0 regardless of index
        buf.set_pos(10)
        self.assertEqual(buf.get_pos(), 0)
        buf.set_pos(-5)
        self.assertEqual(buf.get_pos(), 0)

    def test_shift_pos_invalid_targets(self):
        buf = ByteBuffer.allocate(2)
        with self.assertRaises(IndexError):
            buf.shift_pos(3)  # 0 + 3 > len
        with self.assertRaises(IndexError):
            buf.shift_pos(-1)
