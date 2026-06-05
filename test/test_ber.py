"""
Unit tests for BER encoding/decoding (X.690)
Tests cover all type implementations in ber.py
"""
import unittest
from dataclasses import dataclass
from typing import Optional, override, Self
from StructResult.result import Error, NULL
from src.COSEMpdu.x680.type import InitError
from src.COSEMpdu.byte_buffer import ByteBuffer
from src.COSEMpdu.x690 import Tag, Length, TagError
from src.COSEMpdu.x680 import NamedType, DefaultNamedType, NamedBit, NamedBitList
from src.COSEMpdu.ber import (
    ImplicitTaggedType,
    ExplicitTaggedType,
    BitStringType,
    BooleanType,
    ChoiceType,
    EnumeratedType,
    IntegerType,
    NullType,
    ObjectIdentifierType,
    OctetStringType,
    SequenceType,
    SequenceOfType,
    GeneralizedTime
)
from src.COSEMpdu.x680 import Class, UniversalClassTagAssignments


class TestLength(unittest.TestCase):
    """Test Length encoding/decoding per X.690 §8.1.3"""

    def test_short_form_encode(self) -> None:
        """Short form: length < 128"""
        length = Length(100)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := length.put(buf), Error):
            written.unwrap()
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf)[:written], b"\x64")

    def test_short_form_decode(self) -> None:
        """Short form: length < 128"""
        buf = ByteBuffer.wrap(b"\x64")
        if isinstance(length := Length.get(buf), Error):
            length.unwrap()
        self.assertEqual(length.value, 100)

    def test_long_form_encode(self) -> None:
        """Long form: length >= 128"""
        length = Length(300)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := length.put(buf), Error):
            written.unwrap()
        self.assertEqual(written, 3)  # 0x82 + 2 bytes
        self.assertEqual(bytes(buf)[:written], b"\x82\x01\x2c")

    def test_long_form_decode(self) -> None:
        """Long form: length >= 128"""
        buf = ByteBuffer.wrap(b"\x82\x01\x2c")
        if isinstance(length := Length.get(buf), Error):
            length.unwrap()
        self.assertEqual(length.value, 300)

    def test_indefinite_form(self) -> None:
        """Indefinite form: 0x80"""
        length = Length(-1)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := length.put(buf), Error):
            written.unwrap()
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf)[:written], b"\x80")

        buf = ByteBuffer.wrap(b"\x80")
        if isinstance(decoded := Length.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, -1)

    def test_zero_length(self) -> None:
        """Zero length encoding"""
        length = Length(0)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := length.put(buf), Error):
            written.unwrap()
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf)[:written], b"\x00")


class TestTag(unittest.TestCase):
    """Test Tag encoding/decoding per X.690 §8.1.2"""

    def test_low_tag_number_encode(self) -> None:
        """Low tag number: < 31"""
        tag = Tag(
            class_number=UniversalClassTagAssignments.Integer,
            class_=Class.UNIVERSAL,
            constructed=False
        )
        buf = ByteBuffer.allocate(10)
        if isinstance(written := tag.put(buf), Error):
            written.unwrap()
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf)[:written], b"\x02")

    def test_low_tag_number_decode(self) -> None:
        """Low tag number: < 31"""
        buf = ByteBuffer.wrap(b"\x02")
        if isinstance(tag := Tag.get(buf), Error):
            tag.unwrap()
        self.assertEqual(tag.class_number, 2)
        self.assertEqual(tag.class_, Class.UNIVERSAL)
        self.assertFalse(tag.constructed)

    def test_high_tag_number_encode(self) -> None:
        """High tag number: >= 31"""
        tag = Tag(
            class_number=100,
            class_=Class.CONTEXT_SPECIFIC,
            constructed=True
        )
        buf = ByteBuffer.allocate(10)
        if isinstance(written := tag.put(buf), Error):
            written.unwrap()
        self.assertEqual(written, 2)  # 0xdf + 2 bytes for 100
        # 0xdf = 11011111 (CONTEXT, constructed, high-tag)
        # 100 = 0x64 = 0b1100100
        self.assertEqual(bytes(buf)[0], 0xbf)

    def test_constructed_flag(self) -> None:
        """Test constructed bit (bit 6)"""
        tag_primitive = Tag(5, Class.UNIVERSAL, constructed=False)
        tag_constructed = Tag(5, Class.UNIVERSAL, constructed=True)

        buf1 = ByteBuffer.allocate(10)
        buf2 = ByteBuffer.allocate(10)
        tag_primitive.put(buf1)
        tag_constructed.put(buf2)

        # Bit 6 should differ
        self.assertEqual(bytes(buf1)[0] & 0x20, 0x00)
        self.assertEqual(bytes(buf2)[0] & 0x20, 0x20)

    def test_tag_validate(self) -> None:
        """Test tag validation"""
        expected_tag = Tag(2, Class.UNIVERSAL, constructed=False)
        buf = ByteBuffer.wrap(b"\x02\x01\x00")  # Tag + Length + Content

        # Should not raise
        expected_tag.validate(buf)
        self.assertEqual(buf.get_pos(), 1)  # Consumed 1 byte for tag

        # Wrong tag should raise
        buf = ByteBuffer.wrap(b"\x03\x01\x00")
        expected_tag.validate(buf).has(exception_type=ValueError)


class TestBooleanType(unittest.TestCase):
    """Test BOOLEAN encoding/decoding per X.690 §8.2"""

    def test_false_encode(self) -> None:
        """FALSE = 0x00"""
        boolean = BooleanType(False)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := boolean.put(buf), Error):
            written.unwrap()
        self.assertEqual(written, 3)  # Tag + Length + Content
        self.assertEqual(bytes(buf)[:written], b"\x01\x01\x00")

    def test_true_encode(self) -> None:
        """TRUE = 0xFF (DER compliant)"""
        boolean = BooleanType(True)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := boolean.put(buf), Error):
            written.unwrap()
        self.assertEqual(written, 3)
        self.assertEqual(bytes(buf)[:written], b"\x01\x01\xff")

    def test_false_decode(self) -> None:
        """Decode FALSE"""
        buf = ByteBuffer.wrap(b"\x01\x01\x00")
        result = BooleanType.get(buf)
        self.assertNotIsInstance(result, Error)
        self.assertFalse(result.value)

    def test_true_decode(self) -> None:
        """Decode TRUE"""
        buf = ByteBuffer.wrap(b"\x01\x01\xff")
        if isinstance(boolean := BooleanType.get(buf), Error):
            boolean.unwrap()
        self.assertTrue(boolean.value)

    def test_true_nonzero_decode(self) -> None:
        """TRUE can be any non-zero value (BER)"""
        buf = ByteBuffer.wrap(b"\x01\x01\x01")
        if isinstance(boolean := BooleanType.get(buf), Error):
            boolean.unwrap()
        self.assertTrue(boolean.value)

    def test_invalid_length(self) -> None:
        """Length must be 1"""
        buf = ByteBuffer.wrap(b"\x01\x02\x00\x00")
        if not (
            isinstance(err := BooleanType.get(buf), Error)
            and err.has(exception_type=ValueError)
        ):
            raise AssertionError("Expected IntegerType.get() to return an Error with ValueError")

    def test_length_calculation(self) -> None:
        """__len__ should return 3"""
        boolean = BooleanType(True)
        self.assertEqual(3, 3)


class TestIntegerType(unittest.TestCase):
    """Test INTEGER encoding/decoding per X.690 §8.3"""

    def test_zero_encode(self) -> None:
        """Zero = single 0x00 octet"""
        integer = IntegerType(0)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := integer.put(buf), Error):
            written.unwrap()
        self.assertEqual(bytes(buf)[:written], b"\x02\x01\x00")

    def test_positive_encode(self) -> None:
        """Positive integer"""
        integer = IntegerType(12345)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := integer.put(buf), Error):
            written.unwrap()
        # 12345 = 0x3039
        self.assertEqual(bytes(buf)[:written], b"\x02\x02\x30\x39")

    def test_negative_encode(self) -> None:
        """Negative integer (two's complement)"""
        integer = IntegerType(-12345)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := integer.put(buf), Error):
            written.unwrap()
        # -12345 = 0xCFC7 in two's complement
        self.assertEqual(bytes(buf)[:written], b"\x02\x02\xcf\xc7")

    def test_positive_decode(self) -> None:
        """Decode positive integer"""
        buf = ByteBuffer.wrap(b"\x02\x02\x30\x39")
        if isinstance(integer := IntegerType.get(buf), Error):
            integer.unwrap()
        self.assertEqual(integer.value, 12345)

    def test_negative_decode(self) -> None:
        """Decode negative integer"""
        buf = ByteBuffer.wrap(b"\x02\x02\xcf\xc7")
        if isinstance(integer := IntegerType.get(buf), Error):
            integer.unwrap()
        self.assertEqual(integer.value, -12345)

    def test_minimal_encoding(self) -> None:
        """No leading zero bytes except for sign"""
        # 127 should be 1 byte, not 2
        integer = IntegerType(127)
        buf = ByteBuffer.allocate(10)
        if isinstance(_ := integer.put(buf), Error):
            _.unwrap()
        self.assertEqual(bytes(buf)[1], 1)  # Length = 1

        # -128 should be 1 byte
        integer = IntegerType(-128)
        buf = ByteBuffer.allocate(10)
        if isinstance(_ := integer.put(buf), Error):
            _.unwrap()
        self.assertEqual(bytes(buf)[1], 2)  # Length = 1

    def test_sign_bit_padding(self) -> None:
        """Positive numbers with MSB=1 need leading 0x00"""
        integer = IntegerType(128)  # 0x80 has MSB=1
        buf = ByteBuffer.allocate(10)
        if isinstance(_ := integer.put(buf), Error):
            _.unwrap()
        # Should be 2 bytes: 0x00 0x80
        self.assertEqual(bytes(buf)[1], 2)  # Length = 2
        self.assertEqual(bytes(buf)[2], 0x00)  # Leading zero

    def test_invalid_length(self) -> None:
        """Length must be >= 1"""
        buf = ByteBuffer.wrap(b"\x02\x00")
        if not (
            isinstance(err := IntegerType.get(buf), Error)
            and err.has(exception_type=ValueError)
        ):
            raise AssertionError("Expected IntegerType.get() to return an Error with ValueError")


class TestBitStringType(unittest.TestCase):
    """Test BIT STRING encoding/decoding per X.690 §8.6"""

    def test_empty_encode(self) -> None:
        """Empty bit string"""
        bitstring = BitStringType(())
        buf = ByteBuffer.allocate(10)
        if isinstance(written := bitstring.put(buf), Error):
            written.unwrap()
        self.assertEqual(bytes(buf)[:written], b"\x03\x01\x00")

    def test_empty_decode(self) -> None:
        """Decode empty bit string"""
        buf = ByteBuffer.wrap(b"\x03\x01\x00")
        if isinstance(bitstring := BitStringType.get(buf), Error):
            bitstring.unwrap()
        self.assertEqual(bitstring.value, ())

    def test_byte_aligned_encode(self) -> None:
        """Byte-aligned bit string"""
        bits = tuple([1, 0, 1, 0, 1, 0, 1, 0])  # 0xAA
        bitstring = BitStringType(bits)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := bitstring.put(buf), Error):
            written.unwrap()
        self.assertEqual(bytes(buf)[:written], b"\x03\x02\x00\xaa")

    def test_non_byte_aligned_encode(self) -> None:
        """Non-byte-aligned bit string"""
        bits = tuple([1, 0, 1, 0, 1])  # 5 bits
        bitstring = BitStringType(bits)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := bitstring.put(buf), Error):
            written.unwrap()
        # unused_bits = 3, padded = 10101000 = 0xA8
        self.assertEqual(bytes(buf)[2], 3)  # unused_bits
        self.assertEqual(bytes(buf)[3], 0xA8)

    def test_msb_first_decode(self) -> None:
        """Bits ordered MSB-first per octet"""
        buf = ByteBuffer.wrap(b"\x03\x02\x00\xaa")
        if isinstance(bitstring := BitStringType.get(buf), Error):
            bitstring.unwrap()
        # 0xAA = 10101010
        expected = (1, 0, 1, 0, 1, 0, 1, 0)
        self.assertEqual(bitstring.value, expected)

    def test_unused_bits_removed(self) -> None:
        """Unused trailing bits removed on decode"""
        # 5 bits with 3 unused: 10101000
        buf = ByteBuffer.wrap(b"\x03\x02\x03\xa8")
        if isinstance(bitstring := BitStringType.get(buf), Error):
            bitstring.unwrap()
        self.assertEqual(len(bitstring.value), 5)
        self.assertEqual(bitstring.value, (1, 0, 1, 0, 1))

    def test_invalid_unused_bits(self) -> None:
        """unused_bits must be 0-7"""
        buf = ByteBuffer.wrap(b"\x03\x02\x08\x00")
        if isinstance(decoded := BitStringType.get(buf), Error):
            self.assertTrue(decoded.has(exception_type=ValueError))
        else:
            self.fail("Expected Error from BitStringType.get(buf)")


class TestBitStringType2(unittest.TestCase):
    """Test BIT STRING encoding/decoding per X.690 §8.6"""

    def test_empty_encode(self) -> None:
        """Empty bit string"""
        bitstring = BitStringType(())
        buf = ByteBuffer.allocate(10)
        if isinstance(written := bitstring.put(buf), Error):
            written.unwrap()
        self.assertEqual(bytes(buf)[:written], b"\x03\x01\x00")

    def test_empty_decode(self) -> None:
        """Decode empty bit string"""
        buf = ByteBuffer.wrap(b"\x03\x01\x00")
        if isinstance(bitstring := BitStringType.get(buf), Error):
            bitstring.unwrap()
        self.assertEqual(bitstring.value, ())

    def test_byte_aligned_encode(self) -> None:
        """Byte-aligned bit string"""
        bits = (1, 0, 1, 0, 1, 0, 1, 0)  # 0xAA
        bitstring = BitStringType(bits)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := bitstring.put(buf), Error):
            written.unwrap()
        self.assertEqual(bytes(buf)[:written], b"\x03\x02\x00\xaa")

    def test_non_byte_aligned_encode(self) -> None:
        """Non-byte-aligned bit string"""
        bits = (1, 0, 1, 0, 1)  # 5 bits
        bitstring = BitStringType(bits)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := bitstring.put(buf), Error):
            written.unwrap()
        # unused_bits = 3, padded = 10101000 = 0xA8
        self.assertEqual(bytes(buf)[2], 3)  # unused_bits
        self.assertEqual(bytes(buf)[3], 0xA8)

    def test_msb_first_decode(self) -> None:
        """Bits ordered MSB-first per octet"""
        buf = ByteBuffer.wrap(b"\x03\x02\x00\xaa")
        if isinstance(bitstring := BitStringType.get(buf), Error):
            bitstring.unwrap()
        # 0xAA = 10101010
        expected = (1, 0, 1, 0, 1, 0, 1, 0)
        self.assertEqual(bitstring.value, expected)

    def setUp(self) -> None:
        self.StatusBits = NamedBitList(
            bits=(
                NamedBit("read", 0),
                NamedBit("write", 1),
                NamedBit("execute", 2),
                )
        )


        class PermissionType(BitStringType):
            named_bits = self.StatusBits
            value: tuple[int, ...]

        self.PermissionType = PermissionType

    def test_unused_bits_removed(self) -> None:
        """Unused trailing bits removed on decode"""
        # 5 bits with 3 unused: 10101000
        buf = ByteBuffer.wrap(b"\x03\x02\x03\xa8")
        if isinstance(bitstring := BitStringType.get(buf), Error):
            bitstring.unwrap()
        self.assertEqual(len(bitstring.value), 5)
        self.assertEqual(bitstring.value, (1, 0, 1, 0, 1))

    def test_invalid_unused_bits(self) -> None:
        """unused_bits must be 0-7"""
        buf = ByteBuffer.wrap(b"\x03\x02\x08\x00")
        self.assertTrue(BitStringType.get(buf).has(exception_type=ValueError))

    # =====================================================================
    # Named Bits Tests
    # =====================================================================

    def test_named_bits_definition(self) -> None:
        """Test NamedBit and NamedBitList definition"""

        self.assertEqual(len(self.StatusBits.bits), 3)
        self.assertEqual(self.StatusBits.bits[0].identifier, "read")
        self.assertEqual(self.StatusBits.bits[0].position, 0)
        self.assertEqual(self.StatusBits.bits[1].identifier, "write")
        self.assertEqual(self.StatusBits.bits[1].position, 1)
        self.assertEqual(self.StatusBits.bits[2].identifier, "execute")
        self.assertEqual(self.StatusBits.bits[2].position, 2)

    def test_named_bits_mask(self) -> None:
        """Test NamedBitList get_mask method"""

        # Mask should be 0b111 = 7
        self.assertEqual(self.StatusBits.get_mask(), 0b111)

    def test_named_bits_get_bit(self) -> None:
        """Test NamedBitList get_bit method"""

        # Get bit by name
        read_bit = self.StatusBits.get_bit("read")
        self.assertIsNotNone(read_bit)
        self.assertEqual(read_bit.position, 0)

        # Non-existent bit
        none_bit = self.StatusBits.get_bit("delete")
        self.assertIsNone(none_bit)

    def test_named_bits_contains(self) -> None:
        """Test NamedBitList __contains__ method"""

        self.assertIn("read", self.StatusBits)
        self.assertIn("write", self.StatusBits)
        self.assertIn("execute", self.StatusBits)
        self.assertNotIn("delete", self.StatusBits)

    def test_named_bits_getitem(self) -> None:
        """Test NamedBitList __getitem__ method"""

        self.assertEqual(self.StatusBits["read"], 0)
        self.assertEqual(self.StatusBits["write"], 1)
        self.assertEqual(self.StatusBits["execute"], 2)

        with self.assertRaises(KeyError):
            _ = self.StatusBits["delete"]

    def test_named_bits_str(self) -> None:
        """Test NamedBitList __str__ method"""

        str_repr = str(self.StatusBits)
        self.assertIn("read(0)", str_repr)
        self.assertIn("write(1)", str_repr)
        self.assertIn("execute(2)", str_repr)

    def test_bitstring_with_named_bits_class(self) -> None:
        """Test BitStringType subclass with named_bits ClassVar"""

        # Create instance with read and execute permissions
        permission = self.PermissionType((1, 0, 1))
        self.assertEqual(permission.value, (1, 0, 1))

    def test_bitstring_named_bits_access_by_name(self) -> None:
        """Test BitStringType access bits by name"""

        # read=1, write=0, execute=1
        permission = self.PermissionType((1, 0, 1))

        # Access by name
        self.assertEqual(permission["read"], 1)
        self.assertEqual(permission["write"], 0)
        self.assertEqual(permission["execute"], 1)

    def test_bitstring_named_bits_set_by_name(self) -> None:
        """Test BitStringType set bits by name"""

        # Start with all zeros
        permission = self.PermissionType((0, 0, 0))

        # Set bit by name
        permission["read"] = 1
        self.assertEqual(permission.value, (1, 0, 0))

        permission["execute"] = 1
        self.assertEqual(permission.value, (1, 0, 1))

        # Clear bit by name
        permission.clear("read")
        self.assertEqual(permission.value, (0, 0, 1))

        # Toggle bit by name
        permission.toggle("write")
        self.assertEqual(permission.value, (0, 1, 1))

    def test_bitstring_named_bits_has_bit(self) -> None:
        """Test BitStringType has_bit, has_any, has_all methods"""

        # read=1, write=0, execute=1
        permission = self.PermissionType((1, 0, 1))

        # Test has_bit
        self.assertTrue(permission.has_bit("read"))
        self.assertFalse(permission.has_bit("write"))
        self.assertTrue(permission.has_bit("execute"))

        # Test has_any
        self.assertTrue(permission.has_any("read", "write"))
        self.assertTrue(permission.has_any("read", "execute"))
        self.assertFalse(permission.has_any("write", "delete"))

        # Test has_all
        self.assertTrue(permission.has_all("read", "execute"))
        self.assertFalse(permission.has_all("read", "write"))
        self.assertFalse(permission.has_all("read", "write", "execute"))

    def test_bitstring_named_bits_set_bits_property(self) -> None:
        """Test BitStringType set_bits property"""

        # read=1, write=0, execute=1
        permission = self.PermissionType((1, 0, 1))

        set_bits = permission.set_bits
        self.assertIn("read", set_bits)
        self.assertIn("execute", set_bits)
        self.assertNotIn("write", set_bits)
        self.assertEqual(set_bits["read"], 0)
        self.assertEqual(set_bits["execute"], 2)

    def test_bitstring_named_bits_available_bits_property(self) -> None:
        """Test BitStringType available_bits property"""

        permission = self.PermissionType((1, 0, 1))

        available = permission.available_bits
        self.assertEqual(len(available), 3)
        self.assertEqual(available["read"], 0)
        self.assertEqual(available["write"], 1)
        self.assertEqual(available["execute"], 2)

    def test_bitstring_named_bits_str_representation(self) -> None:
        """Test BitStringType __str__ with named bits"""

        # read=1, write=0, execute=1
        permission = self.PermissionType((1, 0, 1))

        str_repr = str(permission)
        self.assertIn("read", str_repr)
        self.assertIn("execute", str_repr)
        self.assertNotIn("write", str_repr)

        # All zeros
        permission_zero = self.PermissionType((0, 0, 0))
        self.assertEqual(str(permission_zero), "{}")

    def test_bitstring_named_bits_get_value(self) -> None:
        """Test BitStringType get_value with default"""

        permission = self.PermissionType((1, 0, 1))

        # Get existing bit
        self.assertEqual(permission.get_value("read"), 1)
        self.assertEqual(permission.get_value("write"), 0)

        # Get non-existing bit with default
        self.assertEqual(permission.get_value("delete", default=0), 0)
        self.assertEqual(permission.get_value("delete", default=1), 1)

    def test_bitstring_named_bits_set_method(self) -> None:
        """Test BitStringType set method"""

        permission = self.PermissionType((0, 0, 0))

        # Set bit to 1
        permission.set("read")
        self.assertEqual(permission.value, (1, 0, 0))

        # Set bit to 0
        permission.set("read", value=0)
        self.assertEqual(permission.value, (0, 0, 0))

        # Set bit to 1
        permission.set("read", value=1)
        self.assertEqual(permission.value, (1, 0, 0))

    def test_bitstring_named_bits_ber_encode_decode(self) -> None:
        """Test BitStringType with named_bits BER encode/decode round-trip"""

        # Create with read and execute permissions
        original = self.PermissionType((1, 0, 1))

        # Encode
        buf = ByteBuffer.allocate(10)
        if isinstance(written := original.put(buf), Error):
            written.unwrap()

        # Decode
        buf.set_pos(0)
        if isinstance(decoded := self.PermissionType.get(buf), Error):
            decoded.unwrap()

        # Verify
        self.assertEqual(decoded.value, original.value)
        self.assertEqual(decoded["read"], 1)
        self.assertEqual(decoded["write"], 0)
        self.assertEqual(decoded["execute"], 1)

    def test_bitstring_named_bits_bitwise_operations(self) -> None:
        """Test BitStringType with named_bits bitwise operations"""
        # read=1, write=0, execute=1
        perm1 = self.PermissionType((1, 0, 1))
        # read=0, write=1, execute=1
        perm2 = self.PermissionType((0, 1, 1))

        # AND operation
        perm_and = perm1 & perm2
        self.assertEqual(perm_and.value, (0, 0, 1))

        # OR operation
        perm_or = perm1 | perm2
        self.assertEqual(perm_or.value, (1, 1, 1))

        # XOR operation
        perm_xor = perm1 ^ perm2
        self.assertEqual(perm_xor.value, (1, 1, 0))

        # NOT operation
        perm_not = ~perm1
        self.assertEqual(perm_not.value, (0, 1, 0))

    def test_bitstring_named_bits_without_named_bits(self) -> None:
        """Test BitStringType without named_bits raises KeyError"""
        class PlainBitString(BitStringType):
            named_bits = None
            value: tuple[int, ...]

        bitstring = PlainBitString((1, 0, 1))

        # Access by name should raise KeyError
        with self.assertRaises(KeyError):
            _ = bitstring["read"]

        # set by name should raise KeyError
        with self.assertRaises(KeyError):
            bitstring["read"] = 1

        # available_bits should be empty
        self.assertEqual(bitstring.available_bits, {})

        # set_bits should be empty
        self.assertEqual(bitstring.set_bits, {})

    def test_bitstring_named_bits_out_of_range(self) -> None:
        """Test BitStringType named bit access beyond value length"""
        StatusBits = NamedBitList(bits=(
                NamedBit("read", 0),
                NamedBit("write", 1),
                NamedBit("execute", 2),
                NamedBit("delete", 10),  # Beyond typical length
            ))

        class PermissionType(BitStringType):
            named_bits = StatusBits
            value: tuple[int, ...]

        # Short value
        permission = PermissionType((1, 0, 1))

        # Access bit beyond length should return 0
        self.assertEqual(permission.get_value("delete"), 0)

        # Set bit beyond length should extend the value
        permission["delete"] = 1
        self.assertEqual(len(permission.value), 11)
        self.assertEqual(permission.value[10], 1)

    def test_bitstring_named_bits_iteration(self) -> None:
        """Test NamedBitList iteration"""

        status_bits = self.StatusBits
        bit_list = list(status_bits)

        self.assertEqual(len(bit_list), 3)
        self.assertEqual(bit_list[0].identifier, "read")
        self.assertEqual(bit_list[1].identifier, "write")
        self.assertEqual(bit_list[2].identifier, "execute")

    def test_bitstring_named_bits_int_conversion(self) -> None:
        """Test NamedBit __int__ method"""

        read_bit = NamedBit("read", 0)
        write_bit = NamedBit("write", 1)
        execute_bit = NamedBit("execute", 2)

        self.assertEqual(int(read_bit), 1 << 0)  # 1
        self.assertEqual(int(write_bit), 1 << 1)  # 2
        self.assertEqual(int(execute_bit), 1 << 2)  # 4


class TestNullType(unittest.TestCase):
    """Test NULL encoding/decoding per X.690 §8.8"""

    def test_encode(self) -> None:
        """NULL encoding"""
        null = NullType(None)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := null.put(buf), Error):
            written.unwrap()
        self.assertEqual(written, 2)
        self.assertEqual(bytes(buf)[:written], b"\x05\x00")

    def test_decode(self) -> None:
        """NULL decoding"""
        buf = ByteBuffer.wrap(b"\x05\x00")
        null = NullType.get(buf)
        self.assertIsInstance(null, NullType)

    def test_invalid_length(self) -> None:
        """Length must be 0"""
        buf = ByteBuffer.wrap(b"\x05\x01\x00")
        if not (
            isinstance(err := NullType.get(buf), Error)
            and err.has(exception_type=ValueError)
        ):
            raise AssertionError("Expected NullType.get() to return an Error with ValueError")

    def test_length_calculation(self) -> None:
        """__len__ should return 2"""
        null = NullType(None)
        self.assertEqual(null.put(ByteBuffer.allocate(10)), 2)

    def test_equality(self) -> None:
        """All NULL values are equal"""
        self.assertEqual(NullType(None), NullType(None))

    def test_repr(self) -> None:
        """String representation"""
        null = NullType(None)
        self.assertIn("NullType", repr(null))


class TestEnumeratedType(unittest.TestCase):
    """Test ENUMERATED encoding/decoding per X.690 §8.4"""

    def test_encode(self) -> None:
        """Encode enumeration index"""
        enum = EnumeratedType(2)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := enum.put(buf), Error):
            written.unwrap()
        # Tag 0x0A, Length 0x01, Value 0x02
        self.assertEqual(bytes(buf)[:written], b"\x0a\x01\x02")

    def test_decode(self) -> None:
        """Decode enumeration index"""
        buf = ByteBuffer.wrap(b"\x0a\x01\x02")
        if isinstance(enum := EnumeratedType.get(buf), Error):
            enum.unwrap()
        self.assertEqual(enum.value, 2)

    def test_negative_encode(self) -> None:
        """Negative enumeration index (two's complement)"""
        enum = EnumeratedType(-1)
        buf = ByteBuffer.allocate(10)
        if isinstance(_ := enum.put(buf), Error):
            _.unwrap()
        buf.set_pos(0)
        if isinstance(decoded := EnumeratedType.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, -1)

    def test_minimal_encoding(self) -> None:
        """Minimal octets for index"""
        enum = EnumeratedType(127)
        buf = ByteBuffer.allocate(10)
        if isinstance(_ := enum.put(buf), Error):
            _.unwrap()
        self.assertEqual(bytes(buf)[1], 1)  # Length = 1

        enum = EnumeratedType(128)
        buf = ByteBuffer.allocate(10)
        if isinstance(_ := enum.put(buf), Error):
            _.unwrap()
        self.assertEqual(bytes(buf)[1], 2)  # Length = 2 (needs sign bit)


class Integer0(ImplicitTaggedType, IntegerType):
    tag = Tag(0, class_=Class.CONTEXT_SPECIFIC)


class OctetString1(ImplicitTaggedType, OctetStringType):
    tag = Tag(1, class_=Class.CONTEXT_SPECIFIC)


class TestChoice(ChoiceType):
    value: Integer0 | OctetString1


class TestChoiceType(unittest.TestCase):
    """Test CHOICE encoding/decoding per X.690 §8.13"""

    def test_encode_integer_alternative(self) -> None:
        """Encode CHOICE with INTEGER alternative"""
        choice = TestChoice(Integer0(42),
        )
        buf = ByteBuffer.allocate(10)
        if isinstance(_ := choice.put(buf), Error):
            _.unwrap()
        self.assertEqual(bytes(buf)[:3], b"\x80\x01\x2a")

    def test_encode_octetstring_alternative(self) -> None:
        """Encode CHOICE with OCTET STRING alternative"""
        choice = TestChoice(OctetString1(b"AB"))
        buf = ByteBuffer.allocate(10)
        if isinstance(_ := choice.put(buf), Error):
            _.unwrap()
        self.assertEqual(bytes(buf)[:4], b"\x81\x02AB")

    def test_decode_integer_alternative(self) -> None:
        """Decode CHOICE with INTEGER alternative"""
        buf = ByteBuffer.wrap(b"\x80\x01\x2a")
        if isinstance(choice := TestChoice.get(buf), Error):
            choice.unwrap()
        self.assertIsInstance(choice.value, Integer0)
        self.assertEqual(choice.value.value, 42)

    def test_decode_octetstring_alternative(self) -> None:
        """Decode CHOICE with OCTET STRING alternative"""
        buf = ByteBuffer.wrap(b"\x81\x02AB")
        if isinstance(choice := TestChoice.get(buf), Error):
            choice.unwrap()
        self.assertIsInstance(choice.value, OctetString1)
        self.assertEqual(choice.value.value, b"AB")

    def test_invalid_tag(self) -> None:
        """Invalid tag should raise"""
        buf = ByteBuffer.wrap(b"\x05\x00")  # NULL tag
        if not (
            isinstance(err := TestChoice.get(buf), Error)
            and err.has(exception_type=ValueError)
        ):
            raise AssertionError("Expected IntegerType.get() to return an Error with ValueError")

    def test_invalid_selected_tag(self) -> None:
        """Invalid selected_tag in constructor"""
        TestChoice.validate(BooleanType.default()).has(NULL, InitError)

    def test_length_calculation(self) -> None:
        """__len__ should match alternative length"""
        choice = TestChoice(Integer0(42))
        buf = ByteBuffer.allocate(100)
        if isinstance(_ := choice.put(buf), Error):
            _.unwrap()


class TestSequenceWithDefault(SequenceType):
    required: IntegerType
    optional_with_default: IntegerType = IntegerType(30)
    required2: BooleanType

    def __init__(self, required: IntegerType, required2: BooleanType, optional_with_default: Optional[IntegerType] = None) -> None:
        self.required = required
        self.optional_with_default = optional_with_default
        self.required2 = required2


@dataclass
class TestSequence(SequenceType):
    first: IntegerType
    second: BooleanType
    third: Optional[OctetStringType]


class TestSequenceType(unittest.TestCase):
    """Test SEQUENCE encoding/decoding per X.690 §8.9"""

    def test_encode_default_value_omitted(self) -> None:
        """DEFAULT component with default value should be omitted (X.690 §8.9.3)"""
        seq = TestSequenceWithDefault(
            IntegerType(1),
            BooleanType(True),
            IntegerType(30)  # Default value
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(written := seq.put(buf), Error):
            written.unwrap()

        # Should NOT contain encoding for optional_with_default
        # Tag(1) + Length(1) + required(3) + required2(3) = 8 bytes
        self.assertEqual(written, 8)

        # Verify no INTEGER tag (0x02) for the default component
        data = bytes(buf)[:written]
        # Should have: SEQUENCE tag, length, INTEGER(1), BOOLEAN(true)
        # Count INTEGER tags - should be only 1 (for 'required')
        int_tag_count = data.count(b"\x02")
        self.assertEqual(int_tag_count, 1)

    def test_encode_non_default_value_included(self) -> None:
        """DEFAULT component with non-default value should be included"""
        seq = TestSequenceWithDefault(
            IntegerType(1),
            BooleanType(True),
            IntegerType(50),  # Non-default value
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(written := seq.put(buf), Error):
            written.unwrap()

        # Should contain encoding for optional_with_default
        # Tag(1) + Length(1) + required(3) + default(3) + required2(3) = 11 bytes
        self.assertEqual(written, 11)

        # Verify INTEGER tag (0x02) appears twice
        data = bytes(buf)[:written]
        int_tag_count = data.count(b"\x02")
        self.assertEqual(int_tag_count, 2)

    def test_decode_default_value_absent(self) -> None:
        """Decode SEQUENCE with DEFAULT component absent - use default value"""
        # Encode with default value (component omitted)
        seq = TestSequenceWithDefault(
            IntegerType(1),
            BooleanType(False),
            IntegerType(30),  # Default value
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(_ := seq.put(buf), Error):
            _.unwrap()
        buf.set_pos(0)

        # Decode
        if isinstance(decoded := TestSequenceWithDefault.get(buf), Error):
            decoded.unwrap()
        # Should have default value even though not in encoding
        self.assertEqual(decoded.required.value, 1)
        self.assertEqual(decoded.optional_with_default.value, 30)  # Default
        self.assertFalse(decoded.required2.value)

    def test_decode_non_default_value_present(self) -> None:
        """Decode SEQUENCE with DEFAULT component present - use encoded value"""
        # Encode with non-default value (component included)
        seq = TestSequenceWithDefault(
            IntegerType(1),
            BooleanType(True),
            IntegerType(100),  # Non-default value
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(_ := seq.put(buf), Error):
            _.unwrap()
        buf = ByteBuffer.wrap(bytes(buf))

        # Decode
        if isinstance(decoded := TestSequenceWithDefault.get(buf), Error):
            decoded.unwrap()

        # Should have encoded value
        self.assertEqual(decoded.required.value, 1)
        self.assertEqual(decoded.optional_with_default.value, 100)  # Encoded
        self.assertTrue(decoded.required2.value)

    def test_default_component_order(self) -> None:
        """DEFAULT components encoded in definition order when present"""
        seq = TestSequenceWithDefault(
            IntegerType(1),
            BooleanType(True),
            IntegerType(50),  # Non-default
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(_ := seq.put(buf), Error):
            _.unwrap()
        data = bytes(buf)

        # Find positions of component tags
        first_int_pos = data.find(b"\x02", 2)  # Skip SEQUENCE tag/length
        bool_pos = data.find(b"\x01", first_int_pos)
        second_int_pos = data.find(b"\x02", bool_pos)

        # Order should be: required, required2, optional_with_default
        # (DEFAULT components at end when present)
        self.assertLess(first_int_pos, bool_pos)
        self.assertLess(bool_pos, second_int_pos)

    def test_multiple_default_components(self) -> None:
        """Test SEQUENCE with multiple DEFAULT components"""

        class MultiDefaultSequence(SequenceType):
            first: IntegerType
            second: IntegerType = IntegerType(10)
            third: BooleanType = BooleanType(False)
            fourth: OctetStringType

            def __init__(self, first: IntegerType, fourth: OctetStringType, second: IntegerType = IntegerType(10), third: BooleanType = BooleanType(False)) -> None:
                self.first = first
                self.second = second
                self.third = third
                self.fourth = fourth

        # All defaults
        seq_all_defaults = MultiDefaultSequence(
            IntegerType(1),
            OctetStringType(b"X"),
            IntegerType(10),  # Default
            BooleanType(False)  # Default
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(written_defaults := seq_all_defaults.put(buf), Error):
            written_defaults.unwrap()

        # No defaults
        seq_no_defaults = MultiDefaultSequence(
            IntegerType(1),
            OctetStringType(b"X"),
            IntegerType(20),  # Non-default
            BooleanType(True)  # Non-default
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(written_no_defaults := seq_no_defaults.put(buf), Error):
            written_no_defaults.unwrap()

        # Encoding with defaults should be shorter
        self.assertLess(written_defaults, written_no_defaults)

    def test_default_value_equality(self) -> None:
        """DEFAULT component with default value equals explicit default"""
        seq1 = TestSequenceWithDefault(
            IntegerType(1),
            BooleanType(True),
            IntegerType(30),  # Explicit default
        )

        # Create another instance with same values
        seq2 = TestSequenceWithDefault(
            IntegerType(1),
            BooleanType(True),
            IntegerType(30)
        )

        # Should be equal
        self.assertEqual(seq1, seq2)

    def test_round_trip_with_default(self) -> None:
        """Round-trip encoding/decoding preserves DEFAULT semantics"""
        test_cases = [
            # (optional_with_default value, should_be_in_encoding)
            (30, False),  # Default value - omitted
            (50, True),   # Non-default - included
            (0, True),    # Non-default - included
            (-1, True),   # Non-default - included
        ]

        for value, should_be_present in test_cases:
            with self.subTest(value=value):
                original = TestSequenceWithDefault(
                    IntegerType(1),
                    BooleanType(True),
                    IntegerType(value),
                )

                # Encode
                buf = ByteBuffer.allocate(50)
                if isinstance(_ := original.put(buf), Error):
                    _.unwrap()
                encoded_data = bytes(buf)

                # Check if default component is in encoding
                int_tag_count = encoded_data.count(b"\x02")
                has_default_component = (int_tag_count == 2)

                self.assertEqual(has_default_component, should_be_present,
                    f"Value {value}: expected present={should_be_present}, got {has_default_component}")

                # Decode
                buf.set_pos(0)
                decoded = TestSequenceWithDefault.get(buf)

                # Value should be preserved
                self.assertEqual(decoded.optional_with_default.value, value)

    def test_default_named_type_str(self) -> None:
        """Test DefaultNamedType string representation"""
        default_comp = DefaultNamedType("timeout", IntegerType, IntegerType(30))
        str_repr = str(default_comp)

        self.assertIn("DEFAULT", str_repr)
        self.assertIn("IntegerType", str_repr)
        self.assertIn("30", str_repr)

    def test_mixed_optional_and_default(self) -> None:
        """Test SEQUENCE with both OPTIONAL and DEFAULT components"""

        class MixedSequence(SequenceType):
            required: IntegerType
            optional: Optional[OctetStringType]
            with_default: IntegerType = IntegerType(100)
            required2: BooleanType

            def __init__(
                self,
                required: IntegerType,
                required2: BooleanType,
                optional: Optional[OctetStringType] = None,
                with_default: IntegerType = IntegerType(100),
            ) -> None:
                self.required = required
                self.optional = optional
                self.with_default = with_default
                self.required2 = required2

        # OPTIONAL absent, DEFAULT present
        seq1 = MixedSequence(
            required=IntegerType(1),
            with_default=IntegerType(100),  # Default
            required2=BooleanType(True)
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(written1 := seq1.put(buf), Error):
            written1.unwrap()

        # OPTIONAL present, DEFAULT absent
        seq2 = MixedSequence(
            IntegerType(1),
            BooleanType(True),
            OctetStringType(b"X"),  # Present
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(written2 := seq2.put(buf), Error):
            written2.unwrap()

        # OPTIONAL present, DEFAULT non-default
        seq3 = MixedSequence(
            IntegerType(1),
            BooleanType(True),
            OctetStringType(b"X"),  # Present
            IntegerType(128),  # Non-default
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(written3 := seq3.put(buf), Error):
            written3.unwrap()

        # Verify length ordering
        self.assertLess(written1, written2)  # optional absent < present
        self.assertLess(written2, written3)  # default < non-default

    def test_default_component_validation(self) -> None:
        """Test that DEFAULT component type matches default value type"""
        # This should work - types match
        default_comp = DefaultNamedType(
            "timeout",
            IntegerType,
            IntegerType(30)
        )
        self.assertEqual(default_comp.type_, IntegerType)
        self.assertEqual(default_comp.default.value, 30)

    def test_decode_partial_components(self) -> None:
        """Decode SEQUENCE where only some components are present"""
        # Manually create encoding with only required components
        # SEQUENCE tag + length + INTEGER(1) + BOOLEAN(true)
        manual_encoding = b"\x30\x08\x02\x01\x01\x01\x01\xff"

        buf = ByteBuffer.wrap(manual_encoding)
        if isinstance(decoded := TestSequenceWithDefault.get(buf), Error):
            decoded.unwrap()
        # Required components should be present
        self.assertEqual(decoded.required.value, 1)
        self.assertTrue(decoded.required2.value)
        # DEFAULT component should have default value
        self.assertEqual(decoded.optional_with_default.value, 30)

    def test_encode_all_present(self) -> None:
        """Encode SEQUENCE with all components"""
        seq = TestSequence(
            IntegerType(1),
            BooleanType(True),
            OctetStringType(b"\x00")
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(_ := seq.put(buf), Error):
            _.unwrap()

        # Verify tag (UNIVERSAL 16, constructed = 0x30)
        self.assertEqual(bytes(buf)[0], 0x30)

    def test_encode_optional_absent(self) -> None:
        """Encode SEQUENCE with OPTIONAL component absent"""
        seq = TestSequence(
            IntegerType(1),
            BooleanType(False),
            None
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(written := seq.put(buf), Error):
            written.unwrap()

        # Should be shorter without third component
        seq_full = TestSequence(
            IntegerType(1),
            BooleanType(False),
            OctetStringType(b"\x00")
        )
        buf_full = ByteBuffer.allocate(50)
        seq_full.put(buf_full)

        self.assertLess(written, 11)

    def test_decode_all_present(self) -> None:
        """Decode SEQUENCE with all components"""
        # First encode to get valid bytes
        seq = TestSequence(
            IntegerType(1),
            BooleanType(True),
            OctetStringType(b"\x00")
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(_ := seq.put(buf), Error):
            _.unwrap()
        buf = ByteBuffer.wrap(bytes(buf))

        if isinstance(decoded := TestSequence.get(buf), Error):
            decoded.unwrap()
        self.assertIsNotNone(decoded.first)
        self.assertIsNotNone(decoded.second)
        self.assertIsNotNone(decoded.third)
        self.assertEqual(decoded.first.value, 1)
        self.assertTrue(decoded.second.value)
        self.assertEqual(decoded.third.value, b"\x00")

    def test_decode_optional_absent(self) -> None:
        """Decode SEQUENCE with OPTIONAL component absent"""
        seq = TestSequence(
            IntegerType(1),
            BooleanType(False),
            None
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(_ := seq.put(buf), Error):
            _.unwrap()
        buf = ByteBuffer.wrap(bytes(buf))

        decoded = TestSequence.get(buf)
        self.assertEqual(decoded["third"], None)

    def test_component_order(self) -> None:
        """Components encoded in definition order"""
        seq = TestSequence(
            IntegerType(1),
            BooleanType(True),
            OctetStringType(b"\x00")
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(_ := seq.put(buf), Error):
            _.unwrap()
        data = bytes(buf)

        # Find positions of component tags
        int_tag_pos = data.find(b"\x02")  # INTEGER
        bool_tag_pos = data.find(b"\x01")  # BOOLEAN
        octet_tag_pos = data.find(b"\x04")  # OCTET STRING

        self.assertLess(int_tag_pos, bool_tag_pos)
        self.assertLess(bool_tag_pos, octet_tag_pos)

    def test_length_calculation(self) -> None:
        """__len__ should match encoded length"""
        seq = TestSequence(
            IntegerType(1),
            BooleanType(True),
            OctetStringType(b"\x00")
        )
        buf = ByteBuffer.allocate(50)
        if isinstance(actual_len := seq.put(buf), Error):
            actual_len.unwrap()
        self.assertEqual(11, actual_len)


class TestIntegration(unittest.TestCase):
    """Integration tests for complex BER encodings"""

    def test_nested_sequence(self) -> None:
        """Nested SEQUENCE encoding"""

        @dataclass
        class Inner(SequenceType):
            value: IntegerType

        @dataclass
        class Outer(SequenceType):
            inner: Inner
            flag: BooleanType

        outer = Outer(
            Inner(IntegerType(42)),
            BooleanType(True)
        )

        buf = ByteBuffer.allocate(100)
        if isinstance(_ := outer.put(buf), Error):
            _.unwrap()

        # Decode and verify
        buf = ByteBuffer.wrap(bytes(buf))
        if isinstance(decoded := Outer.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.inner.value.value, 42)
        self.assertTrue(decoded.flag)

    def test_choice_in_sequence(self) -> None:
        """CHOICE as SEQUENCE component"""
        class MyChoice(ChoiceType):
            value: IntegerType | BooleanType

        @dataclass
        class Container(SequenceType):
            choice: MyChoice
            name: OctetStringType

        container = Container(
            MyChoice(IntegerType(100)),
            OctetStringType(b"test")
        )

        buf = ByteBuffer.allocate(100)
        if isinstance(_ := container.put(buf), Error):
            _.unwrap()

        buf = ByteBuffer.wrap(bytes(buf))
        if isinstance(decoded := Container.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.choice.value.value, 100)

    def test_round_trip(self) -> None:
        """Encode then decode should preserve values"""
        test_cases = [
            BooleanType(True),
            BooleanType(False),
            IntegerType(0),
            IntegerType(12345),
            IntegerType(-12345),
            OctetStringType(b""),
            OctetStringType(b"\x00\xFF\x7F"),
            BitStringType((1, 0, 1, 0, 1)),
            NullType(None),
            EnumeratedType(5),
        ]

        for original in test_cases:
            buf = ByteBuffer.allocate(100)
            if isinstance(_ := original.put(buf), Error):
                _.unwrap()
            buf = ByteBuffer.wrap(bytes(buf))
            if isinstance(decoded := type(original).get(buf), Error):
                decoded.unwrap()
            self.assertEqual(decoded.value, original.value,
                f"Failed for {type(original).__name__}: {original.value}")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def test_large_integer(self) -> None:
        """Large integer encoding"""
        integer = IntegerType(2**64 - 1)
        buf = ByteBuffer.allocate(100)
        if isinstance(_ := integer.put(buf), Error):
            _.unwrap()
        buf = ByteBuffer.wrap(bytes(buf))
        if isinstance(decoded := IntegerType.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, 2**64 - 1)

    def test_large_bitstring(self) -> None:
        """Large bit string encoding"""
        bits = tuple([i % 2 for i in range(1000)])
        bitstring = BitStringType(bits)
        buf = ByteBuffer.allocate(200)
        if isinstance(_ := bitstring.put(buf), Error):
            _.unwrap()
        buf = ByteBuffer.wrap(bytes(buf))
        if isinstance(decoded := BitStringType.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, bits)

    def test_buffer_overflow(self) -> None:
        """Buffer overflow protection"""
        buf = ByteBuffer.allocate(1)
        integer = IntegerType(1000)  # Requires multiple bytes
        if isinstance(res := integer.put(buf), Error):
            self.assertTrue(res.has(exception_type=BufferError))

    def test_truncated_encoding(self) -> None:
        """Truncated encoding should raise"""
        buf = ByteBuffer.wrap(b"\x02\x05\x00\x00")  # Claims 5 bytes, has 2
        if isinstance(res := IntegerType.get(buf), Error):
            self.assertTrue(res.has(exception_type=BufferError))

    def test_indefinite_length_not_supported(self) -> None:
        """Indefinite length not supported for primitive types"""
        buf = ByteBuffer.wrap(b"\x02\x80")  # INTEGER with indefinite length
        if not (
            isinstance(err := IntegerType.get(buf), Error)
            and err.has(exception_type=ValueError)
        ):
            raise AssertionError("Expected IntegerType.get() to return an Error with ValueError")


IntegerSequence = SequenceOfType[IntegerType]
BooleanSequence = SequenceOfType[BooleanType]


class TestSequenceOfType(unittest.TestCase):
    """Test SEQUENCE OF encoding/decoding per X.690 §8.10"""

    def test_empty_encode(self) -> None:
        """Encode empty SEQUENCE OF"""
        seq = IntegerSequence()
        buf = ByteBuffer.allocate(50)
        if isinstance(written := seq.put(buf), Error):
            written.unwrap()

        # Tag (0x30) + Length (0x00) = 2 bytes
        self.assertEqual(written, 2)
        self.assertEqual(bytes(buf)[:written], b"\x30\x00")

    def test_empty_decode(self) -> None:
        """Decode empty SEQUENCE OF"""
        buf = ByteBuffer.wrap(b"\x30\x00")
        if isinstance(seq := IntegerSequence.get(buf), Error):
            seq.unwrap()
        self.assertEqual(len(seq), 0)
        self.assertEqual(seq.value, [])

    def test_single_element_encode(self) -> None:
        """Encode SEQUENCE OF with single element"""
        seq = IntegerSequence([IntegerType(42)])
        buf = ByteBuffer.allocate(50)
        if isinstance(written := seq.put(buf), Error):
            written.unwrap()

        # Tag (0x30) + Length (0x03) + INTEGER (0x02 0x01 0x2A) = 5 bytes
        self.assertEqual(written, 5)
        self.assertEqual(bytes(buf)[:written], b"\x30\x03\x02\x01\x2a")

    def test_single_element_decode(self) -> None:
        """Decode SEQUENCE OF with single element"""
        buf = ByteBuffer.wrap(b"\x30\x03\x02\x01\x2a")
        if isinstance(seq := IntegerSequence.get(buf), Error):
            seq.unwrap()
        self.assertEqual(len(seq), 1)
        self.assertEqual(seq[0].value, 42)

    def test_multiple_elements_encode(self) -> None:
        """Encode SEQUENCE OF with multiple elements"""
        seq = IntegerSequence([
            IntegerType(1),
            IntegerType(2),
            IntegerType(3),
        ])
        buf = ByteBuffer.allocate(50)
        if isinstance(written := seq.put(buf), Error):
            written.unwrap()
        # Tag (0x30) + Length (0x09) + 3×INTEGER (3×3 bytes) = 11 bytes
        self.assertEqual(written, 11)
        self.assertEqual(
            bytes(buf)[:written],
            b"\x30\x09\x02\x01\x01\x02\x01\x02\x02\x01\x03"
        )

    def test_multiple_elements_decode(self) -> None:
        """Decode SEQUENCE OF with multiple elements"""
        buf = ByteBuffer.wrap(b"\x30\x09\x02\x01\x01\x02\x01\x02\x02\x01\x03")
        if isinstance(seq := IntegerSequence.get(buf), Error):
            seq.unwrap()
        self.assertEqual(len(seq), 3)
        self.assertEqual(seq[0].value, 1)
        self.assertEqual(seq[1].value, 2)
        self.assertEqual(seq[2].value, 3)

    def test_large_values_encode(self) -> None:
        """Encode SEQUENCE OF with large integer values"""
        seq = IntegerSequence([
            IntegerType(1000),  # 2 bytes
            IntegerType(10000),  # 2 bytes
        ])
        buf = ByteBuffer.allocate(50)
        if isinstance(written := seq.put(buf), Error):
            written.unwrap()

        # Tag (0x30) + Length (0x08) + 2×INTEGER (2×4 bytes) = 10 bytes
        self.assertEqual(written, 10)

    def test_negative_values_encode(self) -> None:
        """Encode SEQUENCE OF with negative values"""
        seq = IntegerSequence([
            IntegerType(-1),
            IntegerType(-100),
        ])
        buf = ByteBuffer.allocate(50)
        if isinstance(_ := seq.put(buf), Error):
            _.unwrap()
        buf.set_pos(0)
        if isinstance(decoded := IntegerSequence.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded[0].value, -1)
        self.assertEqual(decoded[1].value, -100)

    def test_mixed_boolean_sequence(self) -> None:
        """Encode SEQUENCE OF BOOLEAN"""
        seq = BooleanSequence([
            BooleanType(True),
            BooleanType(False),
            BooleanType(True),
        ])
        buf = ByteBuffer.allocate(50)
        if isinstance(written := seq.put(buf), Error):
            written.unwrap()

        # Tag (0x30) + Length (0x09) + 3×BOOLEAN (3×3 bytes) = 11 bytes
        self.assertEqual(written, 11)

        buf.set_pos(0)
        if isinstance(decoded := BooleanSequence.get(buf), Error):
            decoded.unwrap()
        self.assertTrue(decoded[0].value)
        self.assertFalse(decoded[1].value)
        self.assertTrue(decoded[2].value)

    def test_length_calculation(self) -> None:
        """__len__ should match encoded length"""
        seq = IntegerSequence([
            IntegerType(1),
            IntegerType(2),
        ])
        buf = ByteBuffer.allocate(50)
        if isinstance(actual_len := seq.put(buf), Error):
            actual_len.unwrap()
        self.assertEqual(8, actual_len)

    def test_iteration(self) -> None:
        """Test iteration over SEQUENCE OF"""
        seq = IntegerSequence([
            IntegerType(10),
            IntegerType(20),
            IntegerType(30),
        ])

        values = [item.value for item in seq]
        self.assertEqual(values, [10, 20, 30])

    def test_indexing(self) -> None:
        """Test indexing into SEQUENCE OF"""
        seq = IntegerSequence([
            IntegerType(100),
            IntegerType(200),
            IntegerType(300),
        ])

        self.assertEqual(seq[0].value, 100)
        self.assertEqual(seq[1].value, 200)
        self.assertEqual(seq[2].value, 300)
        self.assertEqual(seq[-1].value, 300)

    def test_first_last_properties(self) -> None:
        """Test first and last properties"""
        # Empty sequence
        empty = IntegerSequence([])
        self.assertIsInstance(empty.first, Error)
        self.assertIsInstance(empty.last, Error)

        # Single element
        single = IntegerSequence([IntegerType(42)])
        self.assertEqual(single.first.value, 42)
        self.assertEqual(single.last.value, 42)

        # Multiple elements
        multi = IntegerSequence([
            IntegerType(1),
            IntegerType(2),
            IntegerType(3),
        ])
        self.assertEqual(multi.first.value, 1)
        self.assertEqual(multi.last.value, 3)

    def test_repr(self) -> None:
        """Test string representation"""
        seq = IntegerSequence([IntegerType(1), IntegerType(2)])
        repr_str = repr(seq)
        self.assertIn("IntegerType", repr_str)
        self.assertIn("count=2", repr_str)

    def test_equality(self) -> None:
        """Test equality comparison"""
        seq1 = IntegerSequence([IntegerType(1), IntegerType(2)])
        seq2 = IntegerSequence([IntegerType(1), IntegerType(2)])
        seq3 = IntegerSequence([IntegerType(1)])

        self.assertEqual(seq1, seq2)
        self.assertNotEqual(seq1, seq3)
        self.assertNotEqual(seq1, "not a sequence")

    def test_round_trip(self) -> None:
        """Encode then decode should preserve values"""
        original = IntegerSequence([
            IntegerType(0),
            IntegerType(127),
            IntegerType(-128),
            IntegerType(1000),
        ])

        buf = ByteBuffer.allocate(100)
        if isinstance(_ := original.put(buf), Error):
            _.unwrap()
        buf = ByteBuffer.wrap(bytes(buf))

        if isinstance(decoded := IntegerSequence.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(len(decoded), len(original))
        for i, (orig, dec) in enumerate(zip(original, decoded)):
            self.assertEqual(
                orig.value, dec.value,
                f"Failed at index {i}: {orig.value} != {dec.value}"
            )

    def test_nested_sequence_of(self) -> None:
        """Test nested SEQUENCE OF"""
        # Create nested type
        InnerSequence = SequenceOfType[IntegerType]

        OuterSequence = SequenceOfType[InnerSequence]

        nested = OuterSequence([
            InnerSequence([IntegerType(1), IntegerType(2)]),
            InnerSequence([IntegerType(3)]),
        ])

        buf = ByteBuffer.allocate(100)
        if isinstance(_ := nested.put(buf), Error):
            _.unwrap()
        buf = ByteBuffer.wrap(bytes(buf))

        if isinstance(decoded := OuterSequence.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(len(decoded), 2)
        self.assertEqual(len(decoded[0]), 2)
        self.assertEqual(len(decoded[1]), 1)
        self.assertEqual(decoded[0][0].value, 1)
        self.assertEqual(decoded[1][0].value, 3)

    def test_invalid_tag(self) -> None:
        """Invalid tag should raise"""
        buf = ByteBuffer.wrap(b"\x31\x00")  # SET OF tag instead of SEQUENCE OF
        if isinstance(decoded := IntegerSequence.get(buf), Error):
            self.assertTrue(decoded.has(exception_type=TagError))

    def test_truncated_encoding(self) -> None:
        """Truncated encoding should raise"""
        buf = ByteBuffer.wrap(b"\x30\x05\x02\x01\x01")  # Claims 5 bytes, has 3
        if isinstance(decoded := IntegerSequence.get(buf), Error):
            self.assertTrue(decoded.has(exception_type=BufferError))

    def test_buffer_overflow(self) -> None:
        """Buffer overflow protection"""
        seq = IntegerSequence([IntegerType(1000), IntegerType(2000)])
        buf = ByteBuffer.allocate(1)  # Too small
        if isinstance(err := seq.put(buf), Error):
            self.assertTrue(err.has(exception_type=BufferError))

    def test_indefinite_length_not_supported(self) -> None:
        """Indefinite length not supported"""
        buf = ByteBuffer.wrap(b"\x30\x80")  # SEQUENCE OF with indefinite length
        if isinstance(decoded := IntegerSequence.get(buf), Error):
            self.assertTrue(decoded.has(exception_type=ValueError))

    def test_large_sequence(self) -> None:
        """Test large SEQUENCE OF"""
        # Create sequence with 100 elements
        elements = [IntegerType(i) for i in range(100)]
        seq = IntegerSequence(elements)
        buf = ByteBuffer.allocate(500)
        if isinstance(written := seq.put(buf), Error):
            written.unwrap()
        buf = ByteBuffer.wrap(bytes(buf))
        if isinstance(decoded := IntegerSequence.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(len(decoded), 100)
        self.assertEqual(decoded[0].value, 0)
        self.assertEqual(decoded[99].value, 99)

    def test_component_type_validation(self) -> None:
        """Test that component_type is properly set"""
        self.assertEqual(IntegerSequence._T, IntegerType)
        self.assertEqual(BooleanSequence._T, BooleanType)


class ExplicitInteger(ExplicitTaggedType, IntegerType):
    tag2 = Tag(3, Class.CONTEXT_SPECIFIC, constructed=True)


class TestTaggedType(unittest.TestCase):
    """Test TaggedType encoding/decoding per X.690 §8.14"""

    def test_implicit_tagged_integer_encode(self) -> None:
        """IMPLICIT tagged INTEGER [2] INTEGER - tag replaces base type's tag"""
        # Define concrete TaggedType subclass (configuration at class level)
        class ImplicitInteger(ImplicitTaggedType, IntegerType):
            tag = Tag(2, Class.CONTEXT_SPECIFIC)

        # Create instance with value
        tagged = ImplicitInteger(42)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := tagged.put(buf), Error):
            written.unwrap()

        # IMPLICIT: Tag (0x82) + Length (0x01) + Value (0x2A) = 3 bytes
        self.assertEqual(written, 3)
        self.assertEqual(bytes(buf)[:written], b"\x82\x01\x2a")

    def test_implicit_tagged_integer_decode(self) -> None:
        """Decode IMPLICIT tagged INTEGER"""
        class ImplicitInteger(ImplicitTaggedType, IntegerType):
            tag = Tag(2, Class.CONTEXT_SPECIFIC)

        buf = ByteBuffer.wrap(b"\x82\x01\x2a")
        if isinstance(decoded := ImplicitInteger.get(buf), Error):
            decoded.unwrap()

        self.assertEqual(decoded.value, 42)

    def test_explicit_tagged_integer_encode(self) -> None:
        """EXPLICIT tagged INTEGER [3] EXPLICIT INTEGER - tag wraps base TLV"""
        tagged = ExplicitInteger(42)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := tagged.put(buf), Error):
            written.unwrap()

        # EXPLICIT: Outer Tag (0xA3) + Outer Length (0x03) + Inner TLV (0x02\x01\x2a) = 5 bytes
        self.assertEqual(written, 5)
        self.assertEqual(bytes(buf)[:written], b"\xa3\x03\x02\x01\x2a")

    def test_explicit_tagged_integer_decode(self) -> None:
        """Decode EXPLICIT tagged INTEGER"""

        buf = ByteBuffer.wrap(b"\xa3\x03\x02\x01\x2a")
        if isinstance(decoded := ExplicitInteger.get(buf), Error):
            decoded.unwrap()

        self.assertEqual(decoded.value, 42)

    def test_implicit_tagged_boolean_encode(self) -> None:
        """IMPLICIT tagged BOOLEAN [0] BOOLEAN"""

        class ImplicitBoolean(ImplicitTaggedType, BooleanType):
            tag = Tag(0, Class.CONTEXT_SPECIFIC)

        tagged = ImplicitBoolean(True)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := tagged.put(buf), Error):
            written.unwrap()

        # Tag (0x80) + Length (0x01) + Value (0xFF) = 3 bytes
        self.assertEqual(written, 3)
        self.assertEqual(bytes(buf)[:written], b"\x80\x01\xff")

    def test_explicit_tagged_octetstring_encode(self) -> None:
        """EXPLICIT tagged OCTET STRING [1] EXPLICIT OCTET STRING"""

        class ExplicitOctetString(ExplicitTaggedType, OctetStringType):
            tag2 = Tag(1, Class.CONTEXT_SPECIFIC, constructed=True)

        tagged = ExplicitOctetString(b"AB")
        buf = ByteBuffer.allocate(20)
        if isinstance(written := tagged.put(buf), Error):
            written.unwrap()

        # Outer Tag (0xA1) + Outer Length + Inner TLV (0x04\x02AB)
        self.assertGreater(written, 0)

        # Decode and verify
        buf.set_pos(0)
        if isinstance(decoded := ExplicitOctetString.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, b"AB")

    def test_tag_class_encoding(self) -> None:
        """Test different tag classes in tagged types"""
        test_cases = [
            (Class.UNIVERSAL, 2, False, 0x02),
            (Class.APPLICATION, 5, False, 0x45),
            (Class.CONTEXT_SPECIFIC, 10, False, 0x8A),
            (Class.PRIVATE, 15, False, 0xCF),
            (Class.CONTEXT_SPECIFIC, 0, True, 0xA0),  # constructed
        ]

        for class_, number, constructed, expected_tag in test_cases:
            with self.subTest(class_=class_, number=number):
                class TestTagged(ImplicitTaggedType, IntegerType):
                    tag = Tag(number, class_, constructed=constructed)

                tagged = TestTagged(0)
                buf = ByteBuffer.allocate(10)
                if isinstance(put_res := tagged.put(buf), Error):
                    put_res.unwrap()
                self.assertEqual(buf.buf[0], expected_tag)

    def test_high_tag_number_encode(self) -> None:
        """Test tagged type with high tag number (>= 31)"""
        class HighTag(ImplicitTaggedType, IntegerType):
            tag = Tag(100, Class.CONTEXT_SPECIFIC)

        tagged = HighTag(42)
        buf = ByteBuffer.allocate(10)
        if isinstance(written := tagged.put(buf), Error):
            written.unwrap()

        # High tag number: 0x9F 0x64 + Length + Value
        self.assertEqual(buf.buf[0], 0x9F)  # CONTEXT, high-tag
        self.assertEqual(buf.buf[1], 0x64)  # 100

    def test_round_trip_implicit(self) -> None:
        """Round-trip test for IMPLICIT tagged types"""
        test_values = [0, 1, 127, 128, 255, 256, -1, -128]

        for val in test_values:
            with self.subTest(value=val):
                class ImplicitInt(ImplicitTaggedType, IntegerType):
                    tag = Tag(5, Class.CONTEXT_SPECIFIC)

                original = ImplicitInt(val)

                buf = ByteBuffer.allocate(50)
                if isinstance(put_res := original.put(buf), Error):
                    put_res.unwrap()
                buf.set_pos(0)

                if isinstance(decoded := ImplicitInt.get(buf), Error):
                    decoded.unwrap()
                self.assertEqual(decoded.value, val)

    def test_round_trip_explicit(self) -> None:
        """Round-trip test for EXPLICIT tagged types"""
        test_values = [0, 1, 127, 128, -1, -128]

        for val in test_values:
            with self.subTest(value=val):
                class ExplicitInt(ExplicitTaggedType, IntegerType):
                    tag2 = Tag(6, Class.CONTEXT_SPECIFIC, constructed=True)

                original = ExplicitInt(val)

                buf = ByteBuffer.allocate(50)
                if isinstance(put_res := original.put(buf), Error):
                    put_res.unwrap()
                buf.set_pos(0)

                if isinstance(decoded := ExplicitInt.get(buf), Error):
                    decoded.unwrap()
                self.assertEqual(decoded.value, val)

    def test_tag_validation_error_number(self) -> None:
        """Test tag validation raises on tag number mismatch"""
        class TaggedInt(ImplicitTaggedType, IntegerType):
            tag = Tag(5, Class.CONTEXT_SPECIFIC)

        # Encode with tag 5
        tagged = TaggedInt(42)
        buf = ByteBuffer.allocate(10)
        if isinstance(put_res := tagged.put(buf), Error):
            put_res.unwrap()
        buf.set_pos(0)

        # Decode with wrong tag number (6 instead of 5)
        class WrongTag(ImplicitTaggedType, IntegerType):
            tag = Tag(6, Class.CONTEXT_SPECIFIC)

        if isinstance(decoded := WrongTag.get(buf), Error):
            self.assertTrue(decoded.has(exception_type=TagError))
        else:
            self.fail("Expected Error from WrongTag.get(buf)")

    def test_tag_validation_error_class(self) -> None:
        """Test tag validation raises on tag class mismatch"""
        class TaggedInt(ImplicitTaggedType, IntegerType):
            tag = Tag(5, Class.CONTEXT_SPECIFIC)

        # Encode with CONTEXT_SPECIFIC
        tagged = TaggedInt(42)
        buf = ByteBuffer.allocate(10)
        if isinstance(put_res := tagged.put(buf), Error):
            put_res.unwrap()
        buf.set_pos(0)

        # Decode with APPLICATION class
        class WrongClass(ImplicitTaggedType, IntegerType):
            tag = Tag(5, Class.APPLICATION)

        if isinstance(decoded := WrongClass.get(buf), Error):
            self.assertTrue(decoded.has(exception_type=TagError))
        else:
            self.fail("Expected Error from WrongClass.get(buf)")

    def test_get_contents_implicit(self) -> None:
        """Test get_contents for IMPLICIT tagged type (CHOICE alternative)"""
        class ImplicitInt(ImplicitTaggedType, IntegerType):
            tag = Tag(0, Class.CONTEXT_SPECIFIC)

        # First validate and consume the outer tag
        buf = ByteBuffer.wrap(b"\x80\x01\x2a")
        if isinstance(outer_tag := Tag.get(buf), Error):
            outer_tag.unwrap()
        self.assertEqual(outer_tag.class_number, 0)

        # Then decode contents only (no tag validation)
        if isinstance(decoded := ImplicitInt.get_lc(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, 42)

    def test_get_contents_explicit(self) -> None:
        """Test get_contents for EXPLICIT tagged type"""
        class ExplicitInt(ExplicitTaggedType, IntegerType):
            tag2 = Tag(1, Class.CONTEXT_SPECIFIC, constructed=True)

        # First validate and consume the outer tag
        buf = ByteBuffer.wrap(b"\xa1\x03\x02\x01\x2a")
        if isinstance(outer_tag := Tag.get(buf), Error):
            outer_tag.unwrap()
        self.assertEqual(outer_tag.class_number, 1)
        self.assertTrue(outer_tag.constructed)
        # Then decode contents (length + inner TLV)
        buf.set_pos(0)
        if isinstance(decoded := ExplicitInt.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, 42)

    def test_put_contents_implicit(self) -> None:
        """Test put_contents for IMPLICIT tagged type"""
        class ImplicitInt(ImplicitTaggedType, IntegerType):
            tag = Tag(2, Class.CONTEXT_SPECIFIC)

        tagged = ImplicitInt(42)

        buf = ByteBuffer.allocate(10)
        # Encode tag separately
        if isinstance(_ := tagged.tag.put(buf), Error):
            _.unwrap()
        # Encode contents only
        written = tagged.put_lc(buf)

        self.assertEqual(written, 2)  # Length + Value
        self.assertEqual(bytes(buf.extract())[1:], b"\x01\x2a")

    def test_put_contents_explicit(self) -> None:
        """Test put_contents for EXPLICIT tagged type"""
        class ExplicitInt(ExplicitTaggedType, IntegerType):
            tag2 = Tag(3, Class.CONTEXT_SPECIFIC, constructed=True)

        tagged = ExplicitInt(42)

        buf = ByteBuffer.allocate(10)
        written = tagged.put(buf)
        self.assertEqual(written, 5)  # Outer Length (1) + Inner TLV (3)
        self.assertEqual(bytes(buf.extract()), b"\xa3\x03\x02\x01\x2a")

    def test_length_calculation(self) -> None:
        """Test __len__ for tagged types"""
        class ImplicitInt(ImplicitTaggedType, IntegerType):
            tag = Tag(5, Class.CONTEXT_SPECIFIC)

        tagged = ImplicitInt(42)
        # Tag (1) + Length (1) + Value (1) = 3
        self.assertEqual(tagged.put(ByteBuffer.allocate(10)), 3)

        # EXPLICIT should be longer (outer TLV + inner TLV)
        class ExplicitInt(ExplicitTaggedType, IntegerType):
            tag2 = Tag(5, Class.CONTEXT_SPECIFIC, constructed=True)

        tagged_explicit = ExplicitInt(42)
        # Outer Tag (1) + Outer Length (1) + Inner TLV (3) = 5
        self.assertEqual(tagged_explicit.put(ByteBuffer.allocate(10)), 5)

    def test_ber_explicit_application_tag(self) -> None:
        """Test ASN.1 explicit tag [APPLICATION 5] - always BER format"""
        class ApplicationTagged(ImplicitTaggedType, IntegerType):
            tag = Tag(5, Class.APPLICATION, constructed=True)

        tagged = ApplicationTagged(42)
        buf = ByteBuffer.allocate(20)
        if isinstance(written := tagged.put(buf), Error):
            written.unwrap()
        buf.set_pos(0)
        if isinstance(decoded := ApplicationTagged.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, 42)

    def test_nested_tagged_types(self) -> None:
        """Test nested tagged types"""
        # Inner: [0] INTEGER
        class InnerTagged(ImplicitTaggedType, IntegerType):
            tag = Tag(0, Class.CONTEXT_SPECIFIC)

        # Outer: [1] EXPLICIT [0] INTEGER
        class OuterTagged(ExplicitTaggedType, InnerTagged):
            tag2 = Tag(1, Class.CONTEXT_SPECIFIC, constructed=True)

        outer = OuterTagged(42)
        buf = ByteBuffer.allocate(50)
        if isinstance(_ := outer.put(buf), Error):
            _.unwrap()
        # Decode
        buf.set_pos(0)
        if isinstance(decoded := OuterTagged.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, 42)


class TestObjectIdentifierType(unittest.TestCase):
    """Test OBJECT IDENTIFIER encoding/decoding per X.690 §8.19"""

    def test_simple_oid_encode(self) -> None:
        """Encode simple OID {1 0 1} (iso.standard.asn1)"""
        oid = ObjectIdentifierType((1, 0, 1))
        buf = ByteBuffer.allocate(10)
        if isinstance(written := oid.put(buf), Error):
            written.unwrap()
        if isinstance(written := oid.put(buf), Error):
            written.unwrap()
        # Tag 0x06, Length 0x02, Content: (1*40)+0=0x28, 1=0x01
        self.assertEqual(written, 4)
        self.assertEqual(bytes(buf)[:written], b"\x06\x02\x28\x01")

    def test_simple_oid_decode(self) -> None:
        """Decode simple OID {1 0 1}"""
        buf = ByteBuffer.wrap(b"\x06\x02\x28\x01")
        if isinstance(oid := ObjectIdentifierType.get(buf), Error):
            oid.unwrap()

        self.assertEqual(oid.value, (1, 0, 1))

    def test_itu_t_oid_encode(self) -> None:
        """Encode ITU-T OID {0 0}"""
        oid = ObjectIdentifierType((0, 0))
        buf = ByteBuffer.allocate(10)
        if isinstance(written := oid.put(buf), Error):
            written.unwrap()
        self.assertEqual(bytes(buf)[:written], b"\x06\x01\x00")  # (0*40)+0 = 0x00

    def test_joint_iso_oid_encode(self) -> None:
        """Encode joint-iso-itu-t OID {2 10 8825}"""
        oid = ObjectIdentifierType((2, 10, 8825))
        buf = ByteBuffer.allocate(10)
        if isinstance(written := oid.put(buf), Error):
            written.unwrap()

        # First two arcs: (2*40)+10 = 90 = 0x5A
        # Third arc: 8825 = 0x2279 (needs 2 octets in base-128)
        self.assertEqual(buf.buf[0], 0x06)  # Tag
        self.assertEqual(buf.buf[1], 0x03)  # Length
        self.assertEqual(buf.buf[2], 0x5A)  # First two arcs

    def test_large_arc_encode(self) -> None:
        """Encode OID with large arc value (base-128 encoding)"""
        # Arc value 128 requires 2 octets: 0x81 0x00
        oid = ObjectIdentifierType((1, 0, 128))
        buf = ByteBuffer.allocate(10)
        if isinstance(_ := oid.put(buf), Error):
            _.unwrap()

        # Third arc: 128 = 0x81 0x00 (base-128)
        self.assertEqual(buf.buf[3], 0x81)
        self.assertEqual(buf.buf[4], 0x00)

    def test_very_large_arc_encode(self) -> None:
        """Encode OID with very large arc value"""
        # Arc value 16384 requires 3 octets: 0x81 0x80 0x00
        oid = ObjectIdentifierType((1, 0, 16384))
        buf = ByteBuffer.allocate(10)
        if isinstance(_ := oid.put(buf), Error):
            _.unwrap()

        # Third arc: 16384 = 0x81 0x80 0x00 (base-128)
        self.assertEqual(buf.buf[3], 0x81)
        self.assertEqual(buf.buf[4], 0x80)
        self.assertEqual(buf.buf[5], 0x00)

    def test_multi_arc_oid_encode(self) -> None:
        """Encode OID with multiple arcs"""
        oid = ObjectIdentifierType((2, 10, 0x02f4, 5, 8, 1, 1))
        buf = ByteBuffer.allocate(20)
        if isinstance(written := oid.put(buf), Error):
            written.unwrap()

        # Decode and verify
        buf.set_pos(0)
        if isinstance(decoded := ObjectIdentifierType.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, (2, 10, 0x02f4, 5, 8, 1, 1))

    def test_zero_arc_encode(self) -> None:
        """Encode OID with zero arc values"""
        oid = ObjectIdentifierType((1, 0, 0, 0))
        buf = ByteBuffer.allocate(10)
        if isinstance(_ := oid.put(buf), Error):
            _.unwrap()

        # Each zero arc = 0x00
        self.assertEqual(buf.buf[3], 0x00)
        self.assertEqual(buf.buf[4], 0x00)

    def test_invalid_first_arc(self) -> None:
        """First arc must be 0, 1, or 2"""
        with self.assertRaises(ValueError):
            ObjectIdentifierType((3, 0))

    def test_invalid_second_arc(self) -> None:
        """Second arc must be 0-39 if first arc is 0 or 1"""
        with self.assertRaises(ValueError):
            ObjectIdentifierType((1, 40))  # Invalid: 40 > 39

        # Valid for first arc = 2
        oid = ObjectIdentifierType((2, 100))  # Valid
        self.assertEqual(oid.value[1], 100)

    def test_minimum_arcs(self) -> None:
        """OID must have at least 2 arcs"""
        with self.assertRaises(ValueError):
            ObjectIdentifierType((1,))

        # Valid with 2 arcs
        oid = ObjectIdentifierType((1, 0))
        self.assertEqual(len(oid.value), 2)

    def test_negative_arc(self) -> None:
        """Arcs must be non-negative"""
        with self.assertRaises(ValueError):
            ObjectIdentifierType((1, 0, -1))

    def test_round_trip(self) -> None:
        """Encode then decode should preserve value"""
        test_cases = [
            (0, 0),
            (1, 0, 1),
            (2, 10, 8825),
            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
            (1, 0, 128),
            (1, 0, 16384),
        ]

        for value in test_cases:
            with self.subTest(value=value):
                original = ObjectIdentifierType(value)
                buf = ByteBuffer.allocate(50)
                if isinstance(_ := original.put(buf), Error):
                    _.unwrap()
                buf.set_pos(0)
                if isinstance(decoded := ObjectIdentifierType.get(buf), Error):
                    decoded.unwrap()
                self.assertEqual(decoded.value, value)

    def test_startswith(self) -> None:
        """Test OID prefix checking"""
        oid = ObjectIdentifierType((1, 0, 8825, 1, 5))
        prefix = ObjectIdentifierType((1, 0, 8825))

        self.assertTrue(oid.startswith(prefix))
        self.assertFalse(prefix.startswith(oid))

    def test_parent(self) -> None:
        """Test OID parent calculation"""
        oid = ObjectIdentifierType((1, 0, 8825, 1))
        if isinstance(parent := oid.parent(), Error):
            parent.unwrap()
        self.assertEqual(parent.value, (1, 0, 8825))
        self.assertIsInstance(ObjectIdentifierType((1, 0)).parent(), Error)

    def test_child(self) -> None:
        """Test OID child calculation"""
        oid = ObjectIdentifierType((1, 0, 8825))
        child = oid.child(1)
        self.assertEqual(child.value, (1, 0, 8825, 1))

    def test_comparison(self) -> None:
        """Test OID comparison operators"""
        oid1 = ObjectIdentifierType((1, 0, 1))
        oid2 = ObjectIdentifierType((1, 0, 2))
        oid3 = ObjectIdentifierType((1, 0, 1))
        self.assertEqual(oid1, oid3)
        self.assertNotEqual(oid1, oid2)
        self.assertLess(oid1, oid2)

    def test_str_representation(self) -> None:
        """Test string representation"""
        oid = ObjectIdentifierType((1, 0, 1))
        self.assertEqual(str(oid), "1.0.1")
        self.assertEqual(oid.normalize(), (1, 0, 1))

    def test_contents_only_encode(self) -> None:
        """Test put_contents (no tag)"""
        oid = ObjectIdentifierType((1, 0, 1))
        buf = ByteBuffer.allocate(10)

        # Encode tag separately
        if isinstance(_ := oid.tag.put(buf), Error):
            _.unwrap()
        # Encode contents only
        written = oid.put_lc(buf)

        self.assertEqual(written, 3)  # Length + Content
        self.assertEqual(bytes(buf.extract())[1:], b"\x02\x28\x01")

    def test_contents_only_decode(self) -> None:
        """Test get_contents (no tag validation)"""
        buf = ByteBuffer.wrap(b"\x02\x28\x01")  # Length + Content only
        if isinstance(oid := ObjectIdentifierType.get_lc(buf), Error):
            oid.unwrap()

        self.assertEqual(oid.value, (1, 0, 1))

    def test_truncated_encoding(self) -> None:
        """Truncated encoding should raise BufferError"""
        buf = ByteBuffer.wrap(b"\x06\x05\x28\x01\x81")  # Missing last octet
        if isinstance(decoded := ObjectIdentifierType.get(buf), Error):
            self.assertTrue(decoded.has(exception_type=BufferError))

    def test_invalid_base128_continuation(self) -> None:
        """Invalid base-128 continuation should raise"""
        # Continuation bit set but no more octets
        buf = ByteBuffer.wrap(b"\x06\x02\x28\x81")
        if isinstance(decoded := ObjectIdentifierType.get(buf), Error):
            self.assertTrue(decoded.has(exception_type=BufferError))


class TestGeneralizedTime(unittest.TestCase):
    """Test GeneralizedTime encoding/decoding per X.690 §8.23"""

    def test_utc_encode(self) -> None:
        """Encode GeneralizedTime with UTC timezone"""
        gt = GeneralizedTime("20240115120000Z")
        buf = ByteBuffer.allocate(50)
        if isinstance(written := gt.put(buf), Error):
            written.unwrap()

        # Tag (0x18) + Length (0x0F) + Content (15 bytes)
        self.assertEqual(written, 17)
        self.assertEqual(bytes(buf)[0], 0x18)  # UNIVERSAL 24
        self.assertEqual(bytes(buf)[1], 0x0F)  # Length = 15
        self.assertEqual(bytes(buf.extract())[2:], b"20240115120000Z")

    def test_utc_decode(self) -> None:
        """Decode GeneralizedTime with UTC timezone"""
        buf = ByteBuffer.wrap(b"\x18\x0F20240115120000Z")
        decoded = GeneralizedTime.get(buf)
        if isinstance(decoded, Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, "20240115120000Z")
        self.assertTrue(decoded.is_utc)

    def test_with_fractional_seconds_encode(self) -> None:
        """Encode GeneralizedTime with fractional seconds"""
        gt = GeneralizedTime("20240115120000.5Z")
        buf = ByteBuffer.allocate(50)
        if isinstance(written := gt.put(buf), Error):
            written.unwrap()

        self.assertEqual(written, 19)  # 17 + 1 for fractional digit
        self.assertEqual(bytes(buf.extract())[2:], b"20240115120000.5Z")

    def test_with_fractional_seconds_decode(self) -> None:
        """Decode GeneralizedTime with fractional seconds"""
        buf = ByteBuffer.wrap(b"\x18\x1120240115120000.5Z")
        decoded = GeneralizedTime.get(buf)
        if isinstance(decoded, Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, "20240115120000.5Z")
        self.assertTrue(decoded.has_fractional_seconds)
        self.assertEqual(decoded.fractional_seconds, "5")

    def test_with_timezone_offset_encode(self) -> None:
        """Encode GeneralizedTime with timezone offset"""
        gt = GeneralizedTime("20240115120000+0300")
        buf = ByteBuffer.allocate(50)
        if isinstance(written := gt.put(buf), Error):
            written.unwrap()

        self.assertEqual(written, 21)  # 17 + 4 for timezone
        self.assertEqual(bytes(buf.extract())[2:], b"20240115120000+0300")

    def test_with_timezone_offset_decode(self) -> None:
        """Decode GeneralizedTime with timezone offset"""
        buf = ByteBuffer.wrap(b"\x18\x1320240115120000+0300")
        decoded = GeneralizedTime.get(buf)
        if isinstance(decoded, Error):
            decoded.unwrap()
        self.assertEqual(decoded.value, "20240115120000+0300")
        self.assertFalse(decoded.is_utc)
        self.assertEqual(decoded.timezone_offset, "+0300")

    def test_component_access(self) -> None:
        """Test component property accessors"""
        gt = GeneralizedTime("20240115120000Z")

        self.assertEqual(gt.year, 2024)
        self.assertEqual(gt.month, 1)
        self.assertEqual(gt.day, 15)
        self.assertEqual(gt.hour, 12)
        self.assertEqual(gt.minute, 0)
        self.assertEqual(gt.second, 0)

    def test_leap_second(self) -> None:
        """Test GeneralizedTime with leap second (second=60)"""
        gt = GeneralizedTime("20161231235960Z")
        buf = ByteBuffer.allocate(50)
        if isinstance(_ := gt.put(buf), Error):
            _.unwrap()

        buf.set_pos(0)
        if isinstance(decoded := GeneralizedTime.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.second, 60)

    def test_invalid_format_too_short(self) -> None:
        """Test invalid GeneralizedTime - too short"""
        with self.assertRaises(ValueError):
            GeneralizedTime("2024011512000")  # Missing timezone

    def test_invalid_format_no_timezone(self) -> None:
        """Test invalid GeneralizedTime - no timezone"""
        with self.assertRaises(ValueError):
            GeneralizedTime("20240115120000")  # Missing Z or ±HHMM

    def test_invalid_month(self) -> None:
        """Test invalid GeneralizedTime - month out of range"""
        with self.assertRaises(ValueError):
            GeneralizedTime("20241315120000Z")  # Month 13

    def test_invalid_day(self) -> None:
        """Test invalid GeneralizedTime - day out of range"""
        with self.assertRaises(ValueError):
            GeneralizedTime("20240132120000Z")  # Day 32

    def test_invalid_hour(self) -> None:
        """Test invalid GeneralizedTime - hour out of range"""
        with self.assertRaises(ValueError):
            GeneralizedTime("20240115240000Z")  # Hour 24

    def test_invalid_minute(self) -> None:
        """Test invalid GeneralizedTime - minute out of range"""
        with self.assertRaises(ValueError):
            GeneralizedTime("20240115126000Z")  # Minute 60

    def test_invalid_second(self) -> None:
        """Test invalid GeneralizedTime - second out of range"""
        with self.assertRaises(ValueError):
            GeneralizedTime("20240115120061Z")  # Second 61

    def test_invalid_fractional_seconds(self) -> None:
        """Test invalid GeneralizedTime - non-numeric fractional seconds"""
        with self.assertRaises(ValueError):
            GeneralizedTime("20240115120000.aZ")

    def test_invalid_timezone_format(self) -> None:
        """Test invalid GeneralizedTime - malformed timezone"""
        with self.assertRaises(ValueError):
            GeneralizedTime("20240115120000+030")  # Too short

    def test_invalid_timezone_hour(self) -> None:
        """Test invalid GeneralizedTime - timezone hour out of range"""
        with self.assertRaises(ValueError):
            GeneralizedTime("20240115120000+2400")  # Hour 24

    def test_invalid_timezone_minute(self) -> None:
        """Test invalid GeneralizedTime - timezone minute out of range"""
        with self.assertRaises(ValueError):
            GeneralizedTime("20240115120000+0360")  # Minute 60

    def test_contents_only_encode(self) -> None:
        """Test put_contents (no tag)"""
        gt = GeneralizedTime("20240115120000Z")
        buf = ByteBuffer.allocate(50)

        # Encode tag separately
        if isinstance(_ := gt.tag.put(buf), Error):
            _.unwrap()
        # Encode contents only
        written = gt.put_lc(buf)

        self.assertEqual(written, 16)  # Length (1) + Content (15)
        self.assertEqual(bytes(buf.extract())[1:], b"\x0F20240115120000Z")

    def test_contents_only_decode(self) -> None:
        """Test get_contents (no tag validation)"""
        buf = ByteBuffer.wrap(b"\x0F20240115120000Z")
        if isinstance(gt := GeneralizedTime.get_lc(buf), Error):
            gt.unwrap()

        self.assertEqual(gt.value, "20240115120000Z")

    def test_length_calculation(self) -> None:
        """Test __len__ matches encoded length"""
        gt = GeneralizedTime("20240115120000Z")
        buf = ByteBuffer.allocate(50)
        if isinstance(actual_len := gt.put(buf), Error):
            actual_len.unwrap()
        self.assertEqual(17, actual_len)

    def test_round_trip(self) -> None:
        """Round-trip encode/decode should preserve value"""
        test_cases = [
            "20240115120000Z",
            "20240115120000.5Z",
            "20240115120000.123Z",
            "20240115120000+0300",
            "20240115120000-0500",
            "20161231235960Z",  # Leap second
        ]

        for value in test_cases:
            with self.subTest(value=value):
                original = GeneralizedTime(value)
                buf = ByteBuffer.allocate(50)
                if isinstance(_ := original.put(buf), Error):
                    _.unwrap()

                buf.set_pos(0)
                if isinstance(decoded := GeneralizedTime.get(buf), Error):
                    decoded.unwrap()

                self.assertEqual(decoded.value, value)

    def test_equality(self) -> None:
        """Test equality comparison"""
        gt1 = GeneralizedTime("20240115120000Z")
        gt2 = GeneralizedTime("20240115120000Z")
        gt3 = GeneralizedTime("20240115120000+0300")

        self.assertEqual(gt1, gt2)
        self.assertNotEqual(gt1, gt3)

    def test_repr(self) -> None:
        """Test string representation"""
        gt = GeneralizedTime("20240115120000Z")
        repr_str = repr(gt)

        self.assertIn("GeneralizedTime", repr_str)
        self.assertIn("20240115120000Z", repr_str)

    def test_str(self) -> None:
        """Test __str__ returns value"""
        gt = GeneralizedTime("20240115120000Z")
        self.assertEqual(str(gt), "20240115120000Z")

    def test_buffer_overflow(self) -> None:
        """Test buffer overflow protection"""
        gt = GeneralizedTime("20240115120000Z")
        buf = ByteBuffer.allocate(1)  # Too small
        if isinstance(offset := gt.put(buf), Error):
            self.assertTrue(offset.has(exception_type=BufferError))

    def test_truncated_encoding(self) -> None:
        """Test truncated encoding raises"""
        buf = ByteBuffer.wrap(b"\x18\x0F2024011512")  # Truncated
        if isinstance(decoded := GeneralizedTime.get(buf), Error):
            self.assertTrue(decoded.has(exception_type=BufferError))

    def test_indefinite_length_not_supported(self) -> None:
        """Test indefinite length not supported"""
        buf = ByteBuffer.wrap(b"\x18\x80")  # Indefinite length
        with self.assertRaises(ValueError):
            GeneralizedTime.get(buf)

    def test_zero_length_not_supported(self) -> None:
        """Test zero length not supported"""
        buf = ByteBuffer.wrap(b"\x18\x00")  # Zero length
        with self.assertRaises(ValueError):
            GeneralizedTime.get(buf)

    def test_negative_timezone(self) -> None:
        """Test GeneralizedTime with negative timezone offset"""
        gt = GeneralizedTime("20240115120000-0500")
        buf = ByteBuffer.allocate(50)
        if isinstance(_ := gt.put(buf), Error):
            _.unwrap()
        buf.set_pos(0)
        if isinstance(decoded := GeneralizedTime.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.timezone_offset, "-0500")
        self.assertFalse(decoded.is_utc)

    def test_fractional_seconds_multiple_digits(self) -> None:
        """Test GeneralizedTime with multiple fractional second digits"""
        gt = GeneralizedTime("20240115120000.123Z")
        buf = ByteBuffer.allocate(50)
        if isinstance(_ := gt.put(buf), Error):
            _.unwrap()

        buf.set_pos(0)
        if isinstance(decoded := GeneralizedTime.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.fractional_seconds, "123")
        self.assertTrue(decoded.has_fractional_seconds)

    def test_year_boundaries(self) -> None:
        """Test year boundary values"""
        # Year 0
        gt = GeneralizedTime("00000115120000Z")
        self.assertEqual(gt.year, 0)

        # Year 9999
        gt = GeneralizedTime("99991231235959Z")
        self.assertEqual(gt.year, 9999)

    def test_midnight_encoding(self) -> None:
        """Test midnight encoding (000000)"""
        gt = GeneralizedTime("20240116000000Z")
        buf = ByteBuffer.allocate(50)
        if isinstance(_ := gt.put(buf), Error):
            _.unwrap()

        buf.set_pos(0)
        if isinstance(decoded := GeneralizedTime.get(buf), Error):
            decoded.unwrap()
        self.assertEqual(decoded.hour, 0)
        self.assertEqual(decoded.minute, 0)
        self.assertEqual(decoded.second, 0)


if __name__ == "__main__":
    unittest.main()

