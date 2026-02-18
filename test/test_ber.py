"""
Unit tests for BER encoding/decoding (X.690)
Tests cover all type implementations in ber.py
"""
import unittest
from typing import ClassVar
from dataclasses import dataclass
from src.COSEMpdu.byte_buffer import ByteBuffer
from src.COSEMpdu.x690 import Tag, Length
from src.COSEMpdu.ber import (
    BitStringType,
    BooleanType,
    ChoiceType,
    EnumeratedType,
    IntegerType,
    NullType,
    OctetStringType,
    SequenceType,
)
from src.COSEMpdu.x680 import Class, UniversalClassTagAssignments


class TestLength(unittest.TestCase):
    """Test Length encoding/decoding per X.690 §8.1.3"""
    
    def test_short_form_encode(self):
        """Short form: length < 128"""
        length = Length(100)
        buf = ByteBuffer.allocate(10)
        written = length.put(buf)
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf)[:written], b'\x64')
    
    def test_short_form_decode(self):
        """Short form: length < 128"""
        buf = ByteBuffer.wrap(b'\x64')
        length = Length.get(buf)
        self.assertEqual(length.value, 100)
    
    def test_long_form_encode(self):
        """Long form: length >= 128"""
        length = Length(300)
        buf = ByteBuffer.allocate(10)
        written = length.put(buf)
        self.assertEqual(written, 3)  # 0x82 + 2 bytes
        self.assertEqual(bytes(buf)[:written], b'\x82\x01\x2c')
    
    def test_long_form_decode(self):
        """Long form: length >= 128"""
        buf = ByteBuffer.wrap(b'\x82\x01\x2c')
        length = Length.get(buf)
        self.assertEqual(length.value, 300)
    
    def test_indefinite_form(self):
        """Indefinite form: 0x80"""
        length = Length(-1)
        buf = ByteBuffer.allocate(10)
        written = length.put(buf)
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf)[:written], b'\x80')
        
        buf = ByteBuffer.wrap(b'\x80')
        decoded = Length.get(buf)
        self.assertEqual(decoded.value, -1)
    
    def test_zero_length(self):
        """Zero length encoding"""
        length = Length(0)
        buf = ByteBuffer.allocate(10)
        written = length.put(buf)
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf)[:written], b'\x00')


class TestTag(unittest.TestCase):
    """Test Tag encoding/decoding per X.690 §8.1.2"""
    
    def test_low_tag_number_encode(self):
        """Low tag number: < 31"""
        tag = Tag(
            class_number=UniversalClassTagAssignments.Integer,
            class_=Class.UNIVERSAL,
            constructed=False
        )
        buf = ByteBuffer.allocate(10)
        written = tag.put(buf)
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf)[:written], b'\x02')
    
    def test_low_tag_number_decode(self):
        """Low tag number: < 31"""
        buf = ByteBuffer.wrap(b'\x02')
        tag = Tag.get(buf)
        self.assertEqual(tag.class_number, 2)
        self.assertEqual(tag.class_, Class.UNIVERSAL)
        self.assertFalse(tag.constructed)
    
    def test_high_tag_number_encode(self):
        """High tag number: >= 31"""
        tag = Tag(
            class_number=100,
            class_=Class.CONTEXT_SPECIFIC,
            constructed=True
        )
        buf = ByteBuffer.allocate(10)
        written = tag.put(buf)
        self.assertEqual(written, 2)  # 0xdf + 2 bytes for 100
        # 0xdf = 11011111 (CONTEXT, constructed, high-tag)
        # 100 = 0x64 = 0b1100100
        self.assertEqual(bytes(buf)[0], 0xbf)
    
    def test_constructed_flag(self):
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
    
    def test_tag_validate(self):
        """Test tag validation"""
        expected_tag = Tag(2, Class.UNIVERSAL, constructed=False)
        buf = ByteBuffer.wrap(b'\x02\x01\x00')  # Tag + Length + Content
        
        # Should not raise
        expected_tag.validate(buf)
        self.assertEqual(buf.get_pos(), 1)  # Consumed 1 byte for tag
        
        # Wrong tag should raise
        buf = ByteBuffer.wrap(b'\x03\x01\x00')
        with self.assertRaises(ValueError):
            expected_tag.validate(buf)


class TestBooleanType(unittest.TestCase):
    """Test BOOLEAN encoding/decoding per X.690 §8.2"""
    
    def test_false_encode(self):
        """FALSE = 0x00"""
        boolean = BooleanType(False)
        buf = ByteBuffer.allocate(10)
        written = boolean.put(buf)
        self.assertEqual(written, 3)  # Tag + Length + Content
        self.assertEqual(bytes(buf)[:written], b'\x01\x01\x00')
    
    def test_true_encode(self):
        """TRUE = 0xFF (DER compliant)"""
        boolean = BooleanType(True)
        buf = ByteBuffer.allocate(10)
        written = boolean.put(buf)
        self.assertEqual(written, 3)
        self.assertEqual(bytes(buf)[:written], b'\x01\x01\xff')
    
    def test_false_decode(self):
        """Decode FALSE"""
        buf = ByteBuffer.wrap(b'\x01\x01\x00')
        boolean = BooleanType.get(buf)
        self.assertFalse(boolean.value)
    
    def test_true_decode(self):
        """Decode TRUE"""
        buf = ByteBuffer.wrap(b'\x01\x01\xff')
        boolean = BooleanType.get(buf)
        self.assertTrue(boolean.value)
    
    def test_true_nonzero_decode(self):
        """TRUE can be any non-zero value (BER)"""
        buf = ByteBuffer.wrap(b'\x01\x01\x01')
        boolean = BooleanType.get(buf)
        self.assertTrue(boolean.value)
    
    def test_invalid_length(self):
        """Length must be 1"""
        buf = ByteBuffer.wrap(b'\x01\x02\x00\x00')
        with self.assertRaises(ValueError):
            BooleanType.get(buf)
    
    def test_length_calculation(self):
        """__len__ should return 3"""
        boolean = BooleanType(True)
        self.assertEqual(len(boolean), 3)


class TestIntegerType(unittest.TestCase):
    """Test INTEGER encoding/decoding per X.690 §8.3"""
    
    def test_zero_encode(self):
        """Zero = single 0x00 octet"""
        integer = IntegerType(0)
        buf = ByteBuffer.allocate(10)
        written = integer.put(buf)
        self.assertEqual(bytes(buf)[:written], b'\x02\x01\x00')
    
    def test_positive_encode(self):
        """Positive integer"""
        integer = IntegerType(12345)
        buf = ByteBuffer.allocate(10)
        written = integer.put(buf)
        # 12345 = 0x3039
        self.assertEqual(bytes(buf)[:written], b'\x02\x02\x30\x39')
    
    def test_negative_encode(self):
        """Negative integer (two's complement)"""
        integer = IntegerType(-12345)
        buf = ByteBuffer.allocate(10)
        written = integer.put(buf)
        # -12345 = 0xCFC7 in two's complement
        self.assertEqual(bytes(buf)[:written], b'\x02\x02\xcf\xc7')
    
    def test_positive_decode(self):
        """Decode positive integer"""
        buf = ByteBuffer.wrap(b'\x02\x02\x30\x39')
        integer = IntegerType.get(buf)
        self.assertEqual(integer.value, 12345)
    
    def test_negative_decode(self):
        """Decode negative integer"""
        buf = ByteBuffer.wrap(b'\x02\x02\xcf\xc7')
        integer = IntegerType.get(buf)
        self.assertEqual(integer.value, -12345)
    
    def test_minimal_encoding(self):
        """No leading zero bytes except for sign"""
        # 127 should be 1 byte, not 2
        integer = IntegerType(127)
        buf = ByteBuffer.allocate(10)
        integer.put(buf)
        self.assertEqual(bytes(buf)[1], 1)  # Length = 1
        
        # -128 should be 1 byte
        integer = IntegerType(-128)
        buf = ByteBuffer.allocate(10)
        integer.put(buf)
        self.assertEqual(bytes(buf)[1], 2)  # Length = 1
    
    def test_sign_bit_padding(self):
        """Positive numbers with MSB=1 need leading 0x00"""
        integer = IntegerType(128)  # 0x80 has MSB=1
        buf = ByteBuffer.allocate(10)
        integer.put(buf)
        # Should be 2 bytes: 0x00 0x80
        self.assertEqual(bytes(buf)[1], 2)  # Length = 2
        self.assertEqual(bytes(buf)[2], 0x00)  # Leading zero
    
    def test_invalid_length(self):
        """Length must be >= 1"""
        buf = ByteBuffer.wrap(b'\x02\x00')
        with self.assertRaises(ValueError):
            IntegerType.get(buf)


class TestBitStringType(unittest.TestCase):
    """Test BIT STRING encoding/decoding per X.690 §8.6"""
    
    def test_empty_encode(self):
        """Empty bit string"""
        bitstring = BitStringType(())
        buf = ByteBuffer.allocate(10)
        written = bitstring.put(buf)
        self.assertEqual(bytes(buf)[:written], b'\x03\x01\x00')
    
    def test_empty_decode(self):
        """Decode empty bit string"""
        buf = ByteBuffer.wrap(b'\x03\x01\x00')
        bitstring = BitStringType.get(buf)
        self.assertEqual(bitstring.value, ())
    
    def test_byte_aligned_encode(self):
        """Byte-aligned bit string"""
        bits = tuple([1, 0, 1, 0, 1, 0, 1, 0])  # 0xAA
        bitstring = BitStringType(bits)
        buf = ByteBuffer.allocate(10)
        written = bitstring.put(buf)
        self.assertEqual(bytes(buf)[:written], b'\x03\x02\x00\xaa')
    
    def test_non_byte_aligned_encode(self):
        """Non-byte-aligned bit string"""
        bits = tuple([1, 0, 1, 0, 1])  # 5 bits
        bitstring = BitStringType(bits)
        buf = ByteBuffer.allocate(10)
        written = bitstring.put(buf)
        # unused_bits = 3, padded = 10101000 = 0xA8
        self.assertEqual(bytes(buf)[2], 3)  # unused_bits
        self.assertEqual(bytes(buf)[3], 0xA8)
    
    def test_msb_first_decode(self):
        """Bits ordered MSB-first per octet"""
        buf = ByteBuffer.wrap(b'\x03\x02\x00\xaa')
        bitstring = BitStringType.get(buf)
        # 0xAA = 10101010
        expected = tuple([1, 0, 1, 0, 1, 0, 1, 0])
        self.assertEqual(bitstring.value, expected)
    
    def test_unused_bits_removed(self):
        """Unused trailing bits removed on decode"""
        # 5 bits with 3 unused: 10101000
        buf = ByteBuffer.wrap(b'\x03\x02\x03\xa8')
        bitstring = BitStringType.get(buf)
        self.assertEqual(len(bitstring.value), 5)
        self.assertEqual(bitstring.value, tuple([1, 0, 1, 0, 1]))
    
    def test_invalid_unused_bits(self):
        """unused_bits must be 0-7"""
        buf = ByteBuffer.wrap(b'\x03\x02\x08\x00')
        with self.assertRaises(ValueError):
            BitStringType.get(buf)


class TestOctetStringType(unittest.TestCase):
    """Test OCTET STRING encoding/decoding per X.690 §8.7"""
    
    def test_empty_encode(self):
        """Empty octet string"""
        octetstring = OctetStringType(b'')
        buf = ByteBuffer.allocate(10)
        written = octetstring.put(buf)
        self.assertEqual(bytes(buf)[:written], b'\x04\x00')
    
    def test_empty_decode(self):
        """Decode empty octet string"""
        buf = ByteBuffer.wrap(b'\x04\x00')
        octetstring = OctetStringType.get(buf)
        self.assertEqual(octetstring.value, b'')
    
    def test_encode(self):
        """Encode octet string"""
        octetstring = OctetStringType(b'ABCD')
        buf = ByteBuffer.allocate(10)
        written = octetstring.put(buf)
        self.assertEqual(bytes(buf)[:written], b'\x04\x04ABCD')
    
    def test_decode(self):
        """Decode octet string"""
        buf = ByteBuffer.wrap(b'\x04\x04ABCD')
        octetstring = OctetStringType.get(buf)
        self.assertEqual(octetstring.value, b'ABCD')
    
    def test_binary_data(self):
        """Binary data encoding"""
        data = bytes([0x00, 0xFF, 0x7F, 0x80])
        octetstring = OctetStringType(data)
        buf = ByteBuffer.allocate(10)
        octetstring.put(buf)
        buf.set_pos(0)
        decoded = OctetStringType.get(buf)
        self.assertEqual(decoded.value, data)


class TestNullType(unittest.TestCase):
    """Test NULL encoding/decoding per X.690 §8.8"""
    
    def test_encode(self):
        """NULL encoding"""
        null = NullType()
        buf = ByteBuffer.allocate(10)
        written = null.put(buf)
        self.assertEqual(written, 2)
        self.assertEqual(bytes(buf)[:written], b'\x05\x00')
    
    def test_decode(self):
        """NULL decoding"""
        buf = ByteBuffer.wrap(b'\x05\x00')
        null = NullType.get(buf)
        self.assertIsInstance(null, NullType)
    
    def test_invalid_length(self):
        """Length must be 0"""
        buf = ByteBuffer.wrap(b'\x05\x01\x00')
        with self.assertRaises(ValueError):
            NullType.get(buf)
    
    def test_length_calculation(self):
        """__len__ should return 2"""
        null = NullType()
        self.assertEqual(len(null), 2)
    
    def test_equality(self):
        """All NULL values are equal"""
        self.assertEqual(NullType(), NullType())
    
    def test_repr(self):
        """String representation"""
        null = NullType()
        self.assertIn('NullType', repr(null))


class TestEnumeratedType(unittest.TestCase):
    """Test ENUMERATED encoding/decoding per X.690 §8.4"""
    
    def test_encode(self):
        """Encode enumeration index"""
        enum = EnumeratedType(2)
        buf = ByteBuffer.allocate(10)
        written = enum.put(buf)
        # Tag 0x0A, Length 0x01, Value 0x02
        self.assertEqual(bytes(buf)[:written], b'\x0a\x01\x02')
    
    def test_decode(self):
        """Decode enumeration index"""
        buf = ByteBuffer.wrap(b'\x0a\x01\x02')
        enum = EnumeratedType.get(buf)
        self.assertEqual(enum.value, 2)
    
    def test_negative_encode(self):
        """Negative enumeration index (two's complement)"""
        enum = EnumeratedType(-1)
        buf = ByteBuffer.allocate(10)
        enum.put(buf)
        buf.set_pos(0)
        decoded = EnumeratedType.get(buf)
        self.assertEqual(decoded.value, -1)
    
    def test_minimal_encoding(self):
        """Minimal octets for index"""
        enum = EnumeratedType(127)
        buf = ByteBuffer.allocate(10)
        enum.put(buf)
        self.assertEqual(bytes(buf)[1], 1)  # Length = 1
        
        enum = EnumeratedType(128)
        buf = ByteBuffer.allocate(10)
        enum.put(buf)
        self.assertEqual(bytes(buf)[1], 2)  # Length = 2 (needs sign bit)


class TestChoiceType(unittest.TestCase):
    """Test CHOICE encoding/decoding per X.690 §8.13"""
    
    def setUp(self):
        """Set up test CHOICE type"""
        class TestChoice(ChoiceType):
            alternatives: ClassVar = {
                0: IntegerType,
                1: OctetStringType,
            }
        
        self.TestChoice = TestChoice
    
    def test_encode_integer_alternative(self):
        """Encode CHOICE with INTEGER alternative"""
        choice = self.TestChoice(
            selected_tag=0,
            value=IntegerType(42),
            class_=Class.CONTEXT_SPECIFIC
        )
        buf = ByteBuffer.allocate(10)
        choice.put(buf)
        # Tag 0x02, Length 0x01, Value 0x2A
        self.assertEqual(bytes(buf)[:3], b'\x80\x01\x2a')
    
    def test_encode_octetstring_alternative(self):
        """Encode CHOICE with OCTET STRING alternative"""
        choice = self.TestChoice(
            selected_tag=1,
            value=OctetStringType(b'AB'),
            class_=Class.CONTEXT_SPECIFIC
        )
        buf = ByteBuffer.allocate(10)
        choice.put(buf)
        self.assertEqual(bytes(buf)[:4], b'\x81\x02AB')
    
    def test_decode_integer_alternative(self):
        """Decode CHOICE with INTEGER alternative"""
        buf = ByteBuffer.wrap(b'\x80\x01\x2a')
        choice = self.TestChoice.get(buf)
        self.assertEqual(choice.selected_tag, 0)
        self.assertEqual(choice.value.value, 42)
    
    def test_decode_octetstring_alternative(self):
        """Decode CHOICE with OCTET STRING alternative"""
        buf = ByteBuffer.wrap(b'\x01\x02AB')
        choice = self.TestChoice.get(buf)
        self.assertEqual(choice.selected_tag, 1)
        self.assertEqual(choice.value.value, b'AB')
    
    def test_invalid_tag(self):
        """Invalid tag should raise"""
        buf = ByteBuffer.wrap(b'\x05\x00')  # NULL tag
        with self.assertRaises(ValueError):
            self.TestChoice.get(buf)
    
    def test_invalid_selected_tag(self):
        """Invalid selected_tag in constructor"""
        with self.assertRaises(ValueError):
            self.TestChoice(
                selected_tag=99,
                value=IntegerType(0),
                class_=Class.CONTEXT_SPECIFIC
            )
    
    def test_length_calculation(self):
        """__len__ should match alternative length"""
        choice = self.TestChoice(
            selected_tag=0,
            value=IntegerType(42),
            class_=Class.CONTEXT_SPECIFIC
        )
        self.assertEqual(len(choice), len(IntegerType(42)))


class TestSequenceType(unittest.TestCase):
    """Test SEQUENCE encoding/decoding per X.690 §8.9"""
    
    def setUp(self):
        """Set up test SEQUENCE type"""
        @dataclass(frozen=True)
        class TestSequence(SequenceType):
            components: ClassVar = {
                'first': IntegerType,
                'second': BooleanType,
                'third': OctetStringType,
            }
            first: IntegerType
            second: BooleanType
            third: OctetStringType = None
        
        self.TestSequence = TestSequence
    
    def test_encode_all_present(self):
        """Encode SEQUENCE with all components"""
        seq = self.TestSequence(
            first=IntegerType(1),
            second=BooleanType(True),
            third=OctetStringType(b'\x00')
        )
        buf = ByteBuffer.allocate(50)
        seq.put(buf)
        
        # Verify tag (UNIVERSAL 16, constructed = 0x30)
        self.assertEqual(bytes(buf)[0], 0x30)
    
    def test_encode_optional_absent(self):
        """Encode SEQUENCE with OPTIONAL component absent"""
        seq = self.TestSequence(
            first=IntegerType(1),
            second=BooleanType(False),
            third=NullType()
        )
        buf = ByteBuffer.allocate(50)
        written = seq.put(buf)
        
        # Should be shorter without third component
        seq_full = self.TestSequence(
            first=IntegerType(1),
            second=BooleanType(False),
            third=OctetStringType(b'\x00')
        )
        buf_full = ByteBuffer.allocate(50)
        seq_full.put(buf_full)
        
        self.assertLess(written, len(seq_full))
    
    def test_decode_all_present(self):
        """Decode SEQUENCE with all components"""
        # First encode to get valid bytes
        seq = self.TestSequence(
            first=IntegerType(1),
            second=BooleanType(True),
            third=OctetStringType(b'\x00')
        )
        buf = ByteBuffer.allocate(50)
        seq.put(buf)
        buf = ByteBuffer.wrap(bytes(buf))
        
        decoded = self.TestSequence.get(buf)
        self.assertEqual(decoded.first.value, 1)
        self.assertTrue(decoded.second.value)
        self.assertEqual(decoded.third.value, b'\x00')
    
    def test_decode_optional_absent(self):
        """Decode SEQUENCE with OPTIONAL component absent"""
        seq = self.TestSequence(
            first=IntegerType(1),
            second=BooleanType(False),
            third=NullType()
        )
        buf = ByteBuffer.allocate(50)
        seq.put(buf)
        buf = ByteBuffer.wrap(bytes(buf))
        
        decoded = self.TestSequence.get(buf)
        self.assertIsNone(decoded.third)
    
    def test_component_order(self):
        """Components encoded in definition order"""
        seq = self.TestSequence(
            first=IntegerType(1),
            second=BooleanType(True),
            third=OctetStringType(b'\x00')
        )
        buf = ByteBuffer.allocate(50)
        seq.put(buf)
        data = bytes(buf)
        
        # Find positions of component tags
        int_tag_pos = data.find(b'\x02')  # INTEGER
        bool_tag_pos = data.find(b'\x01')  # BOOLEAN
        octet_tag_pos = data.find(b'\x04')  # OCTET STRING
        
        self.assertLess(int_tag_pos, bool_tag_pos)
        self.assertLess(bool_tag_pos, octet_tag_pos)
    
    def test_length_calculation(self):
        """__len__ should match encoded length"""
        seq = self.TestSequence(
            first=IntegerType(1),
            second=BooleanType(True),
            third=OctetStringType(b'\x00')
        )
        buf = ByteBuffer.allocate(50)
        actual_len = seq.put(buf)
        self.assertEqual(len(seq), actual_len)


class TestIntegration(unittest.TestCase):
    """Integration tests for complex BER encodings"""
    
    def test_nested_sequence(self):
        """Nested SEQUENCE encoding"""
        @dataclass(frozen=True)
        class Inner(SequenceType):
            components: ClassVar = {'value': IntegerType}
            value: IntegerType
        
        @dataclass(frozen=True)
        class Outer(SequenceType):
            components: ClassVar = {'inner': Inner, 'flag': BooleanType}
            inner: Inner
            flag: BooleanType
        
        outer = Outer(
            inner=Inner(value=IntegerType(42)),
            flag=BooleanType(True)
        )
        
        buf = ByteBuffer.allocate(100)
        outer.put(buf)
        
        # Decode and verify
        buf = ByteBuffer.wrap(bytes(buf))
        decoded = Outer.get(buf)
        self.assertEqual(decoded.inner.value.value, 42)
        self.assertTrue(decoded.flag.value)
    
    def test_choice_in_sequence(self):
        """CHOICE as SEQUENCE component"""
        class MyChoice(ChoiceType):
            alternatives: ClassVar = {
                0: IntegerType,
                1: BooleanType,
            }
        
        @dataclass(frozen=True)
        class Container(SequenceType):
            components: ClassVar = {'choice': MyChoice, 'name': OctetStringType}
            choice: MyChoice
            name: OctetStringType
        
        container = Container(
            choice=MyChoice(selected_tag=0, value=IntegerType(100), class_=Class.CONTEXT_SPECIFIC),
            name=OctetStringType(b'test')
        )
        
        buf = ByteBuffer.allocate(100)
        container.put(buf)
        
        buf = ByteBuffer.wrap(bytes(buf))
        decoded = Container.get(buf)
        self.assertEqual(decoded.choice.value.value, 100)
    
    def test_round_trip(self):
        """Encode then decode should preserve values"""
        test_cases = [
            BooleanType(True),
            BooleanType(False),
            IntegerType(0),
            IntegerType(12345),
            IntegerType(-12345),
            OctetStringType(b''),
            OctetStringType(b'\x00\xFF\x7F'),
            BitStringType(tuple([1, 0, 1, 0, 1])),
            NullType(),
            EnumeratedType(5),
        ]
        
        for original in test_cases:
            buf = ByteBuffer.allocate(100)
            original.put(buf)
            buf = ByteBuffer.wrap(bytes(buf))
            
            decoded = type(original).get(buf)
            self.assertEqual(decoded.value, original.value,
                           f"Failed for {type(original).__name__}: {original.value}")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_large_integer(self):
        """Large integer encoding"""
        integer = IntegerType(2**64 - 1)
        buf = ByteBuffer.allocate(100)
        integer.put(buf)
        buf = ByteBuffer.wrap(bytes(buf))
        decoded = IntegerType.get(buf)
        self.assertEqual(decoded.value, 2**64 - 1)
    
    def test_large_bitstring(self):
        """Large bit string encoding"""
        bits = tuple([i % 2 for i in range(1000)])
        bitstring = BitStringType(bits)
        buf = ByteBuffer.allocate(200)
        bitstring.put(buf)
        buf = ByteBuffer.wrap(bytes(buf))
        decoded = BitStringType.get(buf)
        self.assertEqual(decoded.value, bits)
    
    def test_buffer_overflow(self):
        """Buffer overflow protection"""
        buf = ByteBuffer.allocate(1)
        integer = IntegerType(1000)  # Requires multiple bytes
        
        with self.assertRaises(BufferError):
            integer.put(buf)
    
    def test_truncated_encoding(self):
        """Truncated encoding should raise"""
        buf = ByteBuffer.wrap(b'\x02\x05\x00\x00')  # Claims 5 bytes, has 2
        with self.assertRaises(BufferError):
            IntegerType.get(buf)
    
    def test_indefinite_length_not_supported(self):
        """Indefinite length not supported for primitive types"""
        buf = ByteBuffer.wrap(b'\x02\x80')  # INTEGER with indefinite length
        with self.assertRaises(ValueError):
            IntegerType.get(buf)


if __name__ == '__main__':
    unittest.main()