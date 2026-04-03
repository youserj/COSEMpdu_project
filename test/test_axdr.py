"""
Unit tests for A-XDR encoding rules (IEC 61334-6:2000)
Tests cover all type encodings per standard specifications.
"""
from re import I
import unittest
from dataclasses import dataclass
from src.COSEMpdu import x680
from src.COSEMpdu.x680.constrained_type import SizeConstraint, ValueRange
from src.COSEMpdu.axdr import (
    create_alternatives,
    ConstrainedIntegerType, ConstrainedOctetStringType, ConstrainedBitStringType, ConstrainedSequenceOfType,
    BooleanType, IntegerType, BitStringType, OctetStringType, TaggedType,
    ChoiceType, SequenceType, EnumeratedType, NullType, SequenceOfType,
    _encode_variable_length_integer, get_length
)
from src.COSEMpdu.byte_buffer import ByteBuffer
from src.COSEMpdu.x680 import NamedType, OptionalNamedType, DefaultNamedType


@dataclass
class Integer0(TaggedType[IntegerType]):
    tag = 0
    mode = x680.TaggingMode.IMPLICIT
    value: IntegerType


@dataclass
class OctetString1(TaggedType[OctetStringType]):
    tag = 1
    mode = x680.TaggingMode.IMPLICIT
    value: OctetStringType


@dataclass
class TestChoice(ChoiceType):
    alternatives = create_alternatives(
        NamedType("first", Integer0),
        NamedType("second", OctetString1)
    )


class TestVariableLengthInteger(unittest.TestCase):
    """Test helper functions for variable-length integer encoding (§6.1.2)"""

    def test_encode_short_form(self) -> None:
        """Values 0-127 encode as single octet (§6.1.2)"""
        self.assertEqual(_encode_variable_length_integer(0), b"\x00")
        self.assertEqual(_encode_variable_length_integer(1), b"\x01")
        self.assertEqual(_encode_variable_length_integer(127), b"\x7F")

    def test_encode_long_form(self) -> None:
        """Values >127 encode as length octet + value octets (§6.1.2)"""
        self.assertEqual(_encode_variable_length_integer(128), b"\x81\x80")
        self.assertEqual(_encode_variable_length_integer(255), b"\x81\xFF")
        self.assertEqual(_encode_variable_length_integer(256), b"\x82\x01\x00")
        self.assertEqual(_encode_variable_length_integer(65535), b"\x82\xFF\xFF")

    def test_decode_short_form(self) -> None:
        """Decode short form values (0-127)"""
        buf = ByteBuffer.wrap(b"\x00")
        self.assertEqual(get_length(buf), 0)

        buf = ByteBuffer.wrap(b"\x7F")
        self.assertEqual(get_length(buf), 127)

    def test_decode_long_form(self) -> None:
        """Decode long form values (>127)"""
        buf = ByteBuffer.wrap(b"\x81\x80")
        self.assertEqual(get_length(buf), 128)

        buf = ByteBuffer.wrap(b"\x82\x01\x00")
        self.assertEqual(get_length(buf), 256)

    def test_decode_invalid(self) -> None:
        """Invalid length octet (0x80) raises ValueError"""
        buf = ByteBuffer.wrap(b"\x80")
        self.assertTrue(get_length(buf).has(exception_type=ValueError))


class TestBooleanType(unittest.TestCase):
    """Test BOOLEAN encoding per IEC 61334-6 §6.2"""

    def test_encode_false(self) -> None:
        """FALSE encodes as 0x00 (1 byte, no tag/length)"""
        val = BooleanType(value=False)
        buf = ByteBuffer.allocate(1)
        written = val.put(buf)
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf), b"\x00")

    def test_encode_true(self) -> None:
        """TRUE encodes as 0xFF (1 byte, no tag/length)"""
        val = BooleanType(value=True)
        buf = ByteBuffer.allocate(1)
        written = val.put(buf)
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf), b"\xFF")

    def test_decode_false(self) -> None:
        """Decode FALSE from 0x00"""
        buf = ByteBuffer.wrap(b"\x00")
        val = BooleanType.get(buf)
        self.assertFalse(val.value)
        self.assertEqual(buf.get_pos(), 1)

    def test_decode_true(self) -> None:
        """Decode TRUE from 0xFF"""
        buf = ByteBuffer.wrap(b"\xFF")
        val = BooleanType.get(buf)
        self.assertTrue(val.value)
        self.assertEqual(buf.get_pos(), 1)

    def test_decode_nonzero(self) -> None:
        """Any non-zero value decodes as TRUE"""
        buf = ByteBuffer.wrap(b"\x01")
        val = BooleanType.get(buf)
        self.assertTrue(val.value)


class TestIntegerType(unittest.TestCase):
    """Test INTEGER encoding per IEC 61334-6 §6.1"""

    def test_encode_fixed_length_1byte(self) -> None:
        """Fixed-length INTEGER(0..255) encodes as 1 byte (§6.1.1)"""
        @dataclass
        class OneByte(ConstrainedIntegerType):
            constraint_spec = ValueRange(0, 255)
            value: IntegerType

        val = OneByte(IntegerType(value=42))
        buf = ByteBuffer.allocate(1)
        written = val.put(buf)
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf), b"\x2A")

    def test_encode_fixed_length_2bytes(self) -> None:
        """Fixed-length INTEGER(0..65535) encodes as 2 bytes"""
        @dataclass
        class TwoByte(ConstrainedIntegerType):
            constraint_spec = ValueRange(0, 20000)
            value: IntegerType

        val = TwoByte(IntegerType(12345))
        buf = ByteBuffer.allocate(2)
        written = val.put(buf)
        self.assertEqual(written, 2)
        self.assertEqual(bytes(buf), b"\x30\x39")

    def test_encode_variable_short(self) -> None:
        """Variable-length 0-127 encodes as single octet (§6.1.2)"""
        val = IntegerType(value=100)
        buf = ByteBuffer.allocate(1)
        written = val.put(buf)
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf), b"\x64")

    def test_encode_variable_long(self) -> None:
        """Variable-length >127 encodes as length + value"""
        val = IntegerType(value=300)
        buf = ByteBuffer.allocate(3)
        written = val.put(buf)
        self.assertEqual(written, 3)
        self.assertEqual(bytes(buf), b"\x82\x01\x2C")

    def test_decode_fixed_length(self) -> None:
        """Decode fixed-length INTEGER"""
        @dataclass
        class TwoByte(ConstrainedIntegerType):
            constraint_spec = ValueRange(0, 65535)
            value: IntegerType

        buf = ByteBuffer.wrap(b"\x30\x39")
        val = TwoByte.get(buf)
        self.assertEqual(val.value.value, 12345)
        self.assertEqual(val.fixed_length, 2)

    def test_decode_variable_short(self) -> None:
        """Decode variable-length short form"""
        buf = ByteBuffer.wrap(b"\x64")
        val = IntegerType.get(buf)
        self.assertEqual(val.value, 100)

    def test_decode_variable_long(self) -> None:
        """Decode variable-length long form"""
        buf = ByteBuffer.wrap(b"\x82\x01\x2C")
        val = IntegerType.get(buf)
        self.assertEqual(val.value, 300)

    def test_encode_zero_fixed(self) -> None:
        """Fixed-length 0 bytes encodes nothing"""
        @dataclass
        class Empty(ConstrainedIntegerType):
            constraint_spec = ValueRange(0, 0)

        val = Empty(IntegerType(0))
        buf = ByteBuffer.allocate(1)
        written = val.put(buf)
        self.assertEqual(written, 1)


class TestBitStringType(unittest.TestCase):
    """Test BIT STRING encoding per IEC 61334-6 §6.4"""

    def test_encode_fixed_length(self) -> None:
        """Fixed-length BIT STRING encodes content only (§6.4.1)"""
        @dataclass
        class OctetBit(ConstrainedBitStringType):
            constraint_spec = SizeConstraint(8)
            value: BitStringType

        val = OctetBit(BitStringType((1, 0, 1, 1, 0, 0, 1, 1)))
        buf = ByteBuffer.allocate(1)
        written = val.put(buf)
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf), b"\xB3")

    def test_encode_fixed_length_padded(self) -> None:
        """Fixed-length BIT STRING pads to octet boundary"""
        @dataclass
        class FourBit(ConstrainedBitStringType):
            constraint_spec = SizeConstraint(4)
            value: BitStringType

        val = FourBit(BitStringType((1, 0, 1, 1)))
        buf = ByteBuffer.allocate(1)
        written = val.put(buf)
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf), b"\xB0")

    def test_encode_variable_length(self) -> None:
        """Variable-length BIT STRING encodes length + unused_bits + content (§6.4.2)"""
        val = BitStringType(value=(1, 0, 1, 1, 0))
        buf = ByteBuffer.allocate(4)
        written = val.put(buf)
        # Length=5 bits (0x05), unused_bits=3, content=0xB0
        self.assertEqual(written, 2)
        self.assertEqual(bytes(buf)[:2], b"\x05\xB0")

    def test_decode_fixed_length(self) -> None:
        """Decode fixed-length BIT STRING"""
        @dataclass
        class OctetBit(ConstrainedBitStringType):
            constraint_spec = SizeConstraint(8)
            value: BitStringType

        buf = ByteBuffer.wrap(b"\xB3")
        val = OctetBit.get(buf)
        self.assertEqual(val.value.value, (1, 0, 1, 1, 0, 0, 1, 1))

    def test_decode_variable_length(self) -> None:
        """Decode variable-length BIT STRING"""
        buf = ByteBuffer.wrap(b"\x05\xB0")
        val = BitStringType.get(buf)
        self.assertEqual(val.value, (1, 0, 1, 1, 0))

    def test_encode_empty_fixed(self) -> None:
        """Empty fixed-length BIT STRING encodes nothing"""
        @dataclass
        class Empty(ConstrainedBitStringType):
            constraint_spec = SizeConstraint(0)
            value: BitStringType

        val = Empty(BitStringType(()))
        buf = ByteBuffer.allocate(1)
        written = val.put(buf)
        self.assertEqual(written, 0)

    def test_encode_empty_variable(self) -> None:
        """Empty variable-length BIT STRING encodes length=0"""
        val = BitStringType(value=())
        buf = ByteBuffer.allocate(1)
        written = val.put(buf)
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf), b"\x00")


@dataclass
class Octet(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(4)
    value: OctetStringType


class TestOctetStringType(unittest.TestCase):
    """Test OCTET STRING encoding per IEC 61334-6 §6.5"""

    def test_encode_fixed_length(self) -> None:
        """Fixed-length OCTET STRING encodes content only (§6.5.1)"""
        val = Octet(OctetStringType(b"ABCD"))
        buf = ByteBuffer.allocate(4)
        written = val.put(buf)
        self.assertEqual(written, 4)
        self.assertEqual(bytes(buf), b"ABCD")

    def test_encode_variable_length(self) -> None:
        """Variable-length OCTET STRING encodes length + content (§6.5.2)"""
        val = OctetStringType(value=b"ABC")
        buf = ByteBuffer.allocate(4)
        written = val.put(buf)
        self.assertEqual(written, 4)
        self.assertEqual(bytes(buf), b"\x03ABC")

    def test_decode_fixed_length(self) -> None:
        """Decode fixed-length OCTET STRING"""
        buf = ByteBuffer.wrap(b"ABCD")
        val = Octet.get(buf)
        self.assertEqual(val.value.value, b"ABCD")

    def test_decode_variable_length(self) -> None:
        """Decode variable-length OCTET STRING"""
        buf = ByteBuffer.wrap(b"\x03ABC")
        val = OctetStringType.get(buf)
        self.assertEqual(val.value, b"ABC")

    def test_encode_empty_fixed(self) -> None:
        """Empty fixed-length OCTET STRING encodes nothing"""
        @dataclass
        class Octet(ConstrainedOctetStringType):
            constraint_spec = SizeConstraint(0)

        val = Octet(OctetStringType(b""))
        buf = ByteBuffer.allocate(1)
        written = val.put(buf)
        self.assertEqual(written, 0)


class TestEnumeratedType(unittest.TestCase):
    """Test ENUMERATED encoding per IEC 61334-6 §6.3"""

    def test_encode(self) -> None:
        """ENUMERATED encodes as single octet (0-255)"""
        val = EnumeratedType(value=42)
        buf = ByteBuffer.allocate(1)
        written = val.put(buf)
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf), b"\x2A")

    def test_decode(self) -> None:
        """Decode ENUMERATED from single octet"""
        buf = ByteBuffer.wrap(b"\x2A")
        val = EnumeratedType.get(buf)
        self.assertEqual(val.value, 42)

    def test_encode_out_of_range(self) -> None:
        """Value >255 raises ValueError"""
        val = EnumeratedType(value=256)
        buf = ByteBuffer.allocate(1)
        with self.assertRaises(ValueError):
            val.put(buf)

    def test_encode_negative(self) -> None:
        """Negative value raises ValueError"""
        val = EnumeratedType(value=-1)
        buf = ByteBuffer.allocate(1)
        with self.assertRaises(ValueError):
            val.put(buf)


class TestNullType(unittest.TestCase):
    """Test NULL encoding per IEC 61334-6 §6.13"""

    def test_encode(self) -> None:
        """NULL in SEQUENCE encodes as 0 bytes (§6.13)"""
        val = NullType(None)
        buf = ByteBuffer.allocate(1)
        written = val.put(buf)
        self.assertEqual(written, 0)

    def test_decode(self) -> None:
        """Decode NULL (no bytes consumed)"""
        buf = ByteBuffer.wrap(b"\x00\x00")
        val = NullType.get(buf)
        self.assertIsInstance(val, NullType)
        self.assertEqual(buf.get_pos(), 0)  # No bytes consumed

    def test_equality(self) -> None:
        """All NULL values are equal"""
        self.assertEqual(NullType(None), NullType(None))

    def test_repr(self) -> None:
        """String representation"""
        self.assertEqual(repr(NullType(None)), "NullType()")


class TestChoiceType(unittest.TestCase):
    """Test CHOICE encoding per IEC 61334-6 §6.6"""

    def test_encode_integer_alternative(self) -> None:
        """CHOICE with INTEGER alternative encodes tag + content (§6.6)"""
        val = TestChoice.from_id("first", IntegerType(value=42))
        buf = ByteBuffer.allocate(3)
        written = val.put(buf)
        # Tag=0, Length=1 (for value 42), Content=0x2A
        self.assertEqual(written, 2)
        self.assertEqual(bytes(buf)[:2], b"\x00\x2A")

    def test_encode_octetstring_alternative(self) -> None:
        """CHOICE with OCTET STRING alternative"""
        val = TestChoice.from_id("second", OctetStringType(value=b"AB"))
        buf = ByteBuffer.allocate(5)
        written = val.put(buf)
        # Tag=1, Length=2, Content='AB'
        self.assertEqual(written, 4)
        self.assertEqual(bytes(buf)[:4], b"\x01\x02AB")

    def test_decode_integer_alternative(self) -> None:
        """Decode CHOICE with INTEGER alternative"""
        buf = ByteBuffer.wrap(b"\x00\x2A")
        val = TestChoice.get(buf)
        self.assertEqual(val.selected, "first")
        self.assertEqual(val.value.value.value, 42)

    def test_decode_invalid_tag(self) -> None:
        """Invalid tag raises ValueError"""
        buf = ByteBuffer.wrap(b"\x05\x00")
        with self.assertRaises(ValueError):
            TestChoice.get(buf)

    def test_init_invalid_tag(self) -> None:
        """Initialize with invalid tag raises ValueError"""
        with self.assertRaises(ValueError):
            TestChoice.from_id("5", IntegerType(0))


class TestSequenceType(unittest.TestCase):
    """Test SEQUENCE encoding per IEC 61334-6 §6.9"""

    def test_encode_no_optional(self) -> None:
        """SEQUENCE without OPTIONAL encodes components consecutively (§6.9)"""
        @dataclass
        class TestSeq(SequenceType):
            components = (
                NamedType("a", IntegerType),
                NamedType("b", BooleanType),
            )

        val = TestSeq((IntegerType(value=10), BooleanType(value=True)))
        buf = ByteBuffer.allocate(3)
        written = val.put(buf)
        # a=10 (0x0A), b=TRUE (0xFF)
        self.assertEqual(written, 2)
        self.assertEqual(bytes(buf)[:2], b"\x0A\xFF")

    def test_encode_with_optional_present(self) -> None:
        """SEQUENCE with OPTIONAL present encodes presence flag=1"""
        @dataclass
        class TestSeq(SequenceType):
            components = (
                NamedType("a", IntegerType),
                OptionalNamedType("b", BooleanType),
            )

        val = TestSeq((IntegerType(value=10), BooleanType(value=True)))
        buf = ByteBuffer.allocate(4)
        written = val.put(buf)
        self.assertEqual(written, 3)
        self.assertEqual(bytes(buf)[:3], b"\x0A\x01\xFF")

    def test_encode_with_optional_absent(self) -> None:
        """SEQUENCE with OPTIONAL absent encodes presence flag=0"""
        @dataclass
        class TestSeq(SequenceType):
            components = (
                NamedType("a", IntegerType),
                OptionalNamedType("b", BooleanType),
            )

        val = TestSeq((IntegerType(value=10), None))
        buf = ByteBuffer.allocate(4)
        written = val.put(buf)
        # presence=0, a=10
        self.assertEqual(written, 2)
        self.assertEqual(bytes(buf)[:2], b"\x0A\x00")

    def test_encode_with_default_present(self) -> None:
        """SEQUENCE with DEFAULT present encodes presence flag=1"""
        @dataclass
        class TestSeq(SequenceType):
            components = (
                NamedType("a", IntegerType),
                DefaultNamedType("b", BooleanType, default=BooleanType(False)),
            )

        val = TestSeq((IntegerType(value=10), BooleanType(value=True)))
        buf = ByteBuffer.allocate(4)
        written = val.put(buf)
        # presence=1, a=10, b=TRUE
        self.assertEqual(written, 3)

    def test_encode_with_default_absent(self) -> None:
        """SEQUENCE with DEFAULT absent encodes presence flag=0"""
        @dataclass
        class TestSeq(SequenceType):
            components = (
                NamedType("a", IntegerType),
                DefaultNamedType("b", BooleanType, default=BooleanType(False)),
            )

        val = TestSeq((IntegerType(value=10), BooleanType(value=False)))
        buf = ByteBuffer.allocate(4)
        written = val.put(buf)
        # presence=0, a=10
        self.assertEqual(written, 2)
        self.assertEqual(bytes(buf)[:2], b"\x0A\x00")

    def test_decode_with_optional_present(self) -> None:
        """Decode SEQUENCE with OPTIONAL present"""
        @dataclass
        class TestSeq(SequenceType):
            components = (
                NamedType("a", IntegerType),
                OptionalNamedType("b", BooleanType),
            )

        buf = ByteBuffer.wrap(b"\x0A\x01\xFF")
        val = TestSeq.get(buf)
        self.assertEqual(val["a"].value, 10)
        self.assertTrue(val["b"].value)

    def test_decode_with_optional_absent(self) -> None:
        """Decode SEQUENCE with OPTIONAL absent"""
        @dataclass
        class TestSeq(SequenceType):
            components = (
                NamedType("a", IntegerType),
                OptionalNamedType("b", BooleanType),
            )

        buf = ByteBuffer.wrap(b"\x0A\x00")
        val = TestSeq.get(buf)
        self.assertEqual(val["a"].value, 10)
        self.assertIsNone(val["b"])


class TestSequenceOfType(unittest.TestCase):
    """Test SEQUENCE OF encoding per IEC 61334-6 §6.10"""

    def test_encode_fixed_length(self) -> None:
        """Fixed-length SEQUENCE OF encodes components only (§6.10.1)"""
        class TestSeqOf(ConstrainedSequenceOfType[IntegerType]):
            component_type = IntegerType
            constraint_spec = SizeConstraint(2)

        val = TestSeqOf(SequenceOfType(
            value=[IntegerType(value=1), IntegerType(value=2)]
        ))
        buf = ByteBuffer.allocate(2)
        written = val.put(buf)
        self.assertEqual(written, 2)
        self.assertEqual(bytes(buf), b"\x01\x02")

    def test_encode_variable_length(self) -> None:
        """Variable-length SEQUENCE OF encodes count + components (§6.10.2)"""
        @dataclass
        class TestSeqOf(SequenceOfType):
            component_type = IntegerType

        val = TestSeqOf(
            value=(IntegerType(value=1), IntegerType(value=2)),
        )
        buf = ByteBuffer.allocate(4)
        written = val.put(buf)
        # count=2, values=1, 2
        self.assertEqual(written, 3)
        self.assertEqual(bytes(buf)[:3], b"\x02\x01\x02")

    def test_decode_fixed_length(self) -> None:
        """Decode fixed-length SEQUENCE OF"""
        @dataclass
        class SequenceOfIntegerType(SequenceOfType[IntegerType]):
            component_type = IntegerType


        @dataclass
        class TestSeqOf(ConstrainedSequenceOfType[SequenceOfIntegerType]):
            constraint_spec = SizeConstraint(2)
            value: SequenceOfIntegerType

        buf = ByteBuffer.wrap(b"\x01\x02")
        val = TestSeqOf.get(buf)
        self.assertEqual(len(val.value), 2)
        self.assertEqual(val.value[0].value, 1)
        self.assertEqual(val.value[1].value, 2)

    def test_decode_variable_length(self) -> None:
        """Decode variable-length SEQUENCE OF"""
        @dataclass
        class TestSeqOf(SequenceOfType[IntegerType]):
            component_type = IntegerType

        buf = ByteBuffer.wrap(b"\x02\x01\x02")
        val = TestSeqOf.get(buf)
        self.assertEqual(len(val.value), 2)

    def test_encode_empty_fixed(self) -> None:
        """Empty fixed-length SEQUENCE OF encodes nothing"""
        @dataclass
        class TestSeqOf(ConstrainedSequenceOfType[IntegerType]):
            component_type = IntegerType
            constraint_spec = SizeConstraint(0)

        val = TestSeqOf(SequenceOfType([]))
        buf = ByteBuffer.allocate(1)
        written = val.put(buf)
        self.assertEqual(written, 0)

    def test_encode_empty_variable(self) -> None:
        """Empty variable-length SEQUENCE OF encodes count=0"""
        @dataclass
        class TestSeqOf(SequenceOfType):
            component_type = IntegerType

        val = TestSeqOf(value=())
        buf = ByteBuffer.allocate(1)
        written = val.put(buf)
        self.assertEqual(written, 1)
        self.assertEqual(bytes(buf), b"\x00")

    def test_is_empty(self) -> None:
        """is_empty property"""
        @dataclass
        class TestSeqOf(SequenceOfType):
            component_type = IntegerType

        val = TestSeqOf(value=())
        self.assertTrue(val.is_empty)

        val = TestSeqOf(value=(IntegerType(value=1),))
        self.assertFalse(val.is_empty)


class TestIntegration(unittest.TestCase):
    """Integration tests for complex A-XDR encodings"""

    def test_nested_choice_in_sequence(self) -> None:
        """Test CHOICE inside SEQUENCE (common DLMS pattern)"""
        @dataclass
        class Integer0(TaggedType[IntegerType]):
            tag = 0
            mode = x680.TaggingMode.IMPLICIT
            value: IntegerType

        @dataclass
        class Boolean1(TaggedType[BooleanType]):
            tag = 1
            mode = x680.TaggingMode.IMPLICIT
            value: BooleanType

        class InnerChoice(ChoiceType):
            alternatives = create_alternatives(
                NamedType("first", Integer0),
                NamedType("second", Boolean1)
            )

        @dataclass
        class OuterSeq(SequenceType):
            components = (
                NamedType("flag", BooleanType),
                NamedType("choice", InnerChoice),
            )

        val = OuterSeq((
            BooleanType(value=True),
            InnerChoice.from_id("first", value=IntegerType(value=42))
        ))
        buf = ByteBuffer.allocate(10)
        written = val.put(buf)
        # flag=1, choice_tag=0, choice_value=42
        self.assertEqual(written, 3)
        self.assertEqual(bytes(buf)[:3], b"\xFF\x00\x2A")

    def test_sequence_of_choice(self) -> None:
        """Test SEQUENCE OF CHOICE (DLMS service list pattern)"""
        @dataclass
        class Enumerated0(TaggedType[EnumeratedType]):
            tag = 0
            mode = x680.TaggingMode.IMPLICIT
            value: EnumeratedType

        @dataclass
        class Integer1(TaggedType[IntegerType]):
            tag = 1
            mode = x680.TaggingMode.IMPLICIT
            value: IntegerType

        @dataclass
        class ServiceChoice(ChoiceType):
            alternatives = create_alternatives(
                NamedType("first", Enumerated0),
                NamedType("second", Integer1)
            )

        ServiceList = SequenceOfType[ServiceChoice]

        val = ServiceList([
            ServiceChoice.from_id("first", value=EnumeratedType(value=1)),
            ServiceChoice.from_id("second", value=IntegerType(value=100)),
        ])
        buf = ByteBuffer.allocate(10)
        written = val.put(buf)
        # count=2, [tag0=0,val=1], [tag1=1,val=100]
        self.assertEqual(written, 5)
        self.assertEqual(bytes(buf.extract())[:6], b"\x02\x00\x01\x01\x64")

    def test_roundtrip_complex(self) -> None:
        """Test encode/decode roundtrip for complex structure"""
        @dataclass
        class TestSeq(SequenceType):
            components = (
                NamedType("id", IntegerType),
                OptionalNamedType("data", OctetStringType),
                NamedType("choice", TestChoice),
            )

        # Encode
        original = TestSeq((
            IntegerType(value=123),
            OctetStringType(value=b"TEST"),
            TestChoice.from_id("first", value=IntegerType(value=456))
        ))
        buf = ByteBuffer.allocate(20)
        original.put(buf)

        # Decode
        buf.set_pos(0)
        decoded = TestSeq.get(buf)

        # Verify
        self.assertEqual(decoded["id"].value, 123)
        self.assertEqual(decoded["data"].value, b"TEST")
        self.assertEqual(decoded["choice"].selected, "first")
        self.assertEqual(decoded["choice"].value.value.value, 456)


if __name__ == "__main__":
    unittest.main()
