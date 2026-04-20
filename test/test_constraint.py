"""
Unit tests for ConstrainedType with BER encoding/decoding (X.680 §45, X.690)
Tests cover ValueRange constraints and validation during encode/decode
"""
import unittest
from src.COSEMpdu.byte_buffer import ByteBuffer
from src.COSEMpdu.ber import IntegerType, EnumeratedType, ConstrainedType
from src.COSEMpdu.x680.constrained_type import ValueRange


class TestValueRange(unittest.TestCase):
    """Test ValueRange constraint per X.680 §47.4"""

    def test_valid_range(self) -> None:
        """Valid range: lower <= upper"""
        range_constraint = ValueRange(0, 255)
        self.assertEqual(range_constraint.lower_endpoint, 0)
        self.assertEqual(range_constraint.upper_endpoint, 255)

    def test_single_value_range(self) -> None:
        """Single value range: lower == upper"""
        range_constraint = ValueRange(42, 42)
        self.assertEqual(range_constraint.lower_endpoint, 42)
        self.assertEqual(range_constraint.upper_endpoint, 42)

    def test_negative_range(self) -> None:
        """Negative value range"""
        range_constraint = ValueRange(-128, 127)
        self.assertEqual(range_constraint.lower_endpoint, -128)
        self.assertEqual(range_constraint.upper_endpoint, 127)

    def test_contains_method(self) -> None:
        """Test contains() method"""
        range_constraint = ValueRange(0, 100)
        self.assertTrue(range_constraint.contains(0))
        self.assertTrue(range_constraint.contains(50))
        self.assertTrue(range_constraint.contains(100))
        self.assertFalse(range_constraint.contains(-1))
        self.assertFalse(range_constraint.contains(101))

    def test_str_representation(self) -> None:
        """Test string representation"""
        range_constraint = ValueRange(0, 255)
        self.assertEqual(str(range_constraint), "(0..255)")


class Unsigned8(ConstrainedType[IntegerType]):
    constraint_spec = ValueRange(0, 255)
    value: IntegerType

# PortNumber ::= INTEGER (1..65535)


class PortNumber(ConstrainedType[IntegerType]):
    constraint_spec = ValueRange(1, 65535)
    value: IntegerType

# Temperature ::= INTEGER (-40..85)


class Temperature(ConstrainedType[IntegerType]):
    constraint_spec = ValueRange(-40, 85)
    value: IntegerType


class TestConstrainedIntegerType(unittest.TestCase):
    """Test ConstrainedType with INTEGER and ValueRange"""

    def test_valid_unsigned8_encode(self) -> None:
        """Encode valid Unsigned8 value"""
        value = Unsigned8(IntegerType(100))
        buf = ByteBuffer.allocate(10)
        written = value.put(buf)

        self.assertEqual(written, 3)  # Tag + Length + Content
        self.assertEqual(bytes(buf)[:written], b"\x02\x01\x64")

    def test_valid_unsigned8_decode(self) -> None:
        """Decode valid Unsigned8 value"""
        buf = ByteBuffer.wrap(b"\x02\x01\x64")
        value = Unsigned8.get(buf)

        self.assertEqual(value.value.value, 100)

    def test_unsigned8_boundary_low(self) -> None:
        """Test Unsigned8 lower boundary (0)"""
        value = Unsigned8(IntegerType(0))
        buf = ByteBuffer.allocate(10)
        value.put(buf)

        buf.set_pos(0)
        decoded = Unsigned8.get(buf)
        self.assertEqual(decoded.value.value, 0)

    def test_unsigned8_boundary_high(self) -> None:
        """Test Unsigned8 upper boundary (255)"""
        value = Unsigned8(IntegerType(255))
        buf = ByteBuffer.allocate(10)
        value.put(buf)

        buf.set_pos(0)
        decoded = Unsigned8.get(buf)
        self.assertEqual(decoded.value.value, 255)

    def test_unsigned8_below_range(self) -> None:
        """Test Unsigned8 value below range should raise"""
        with self.assertRaises(ValueError):
            Unsigned8(IntegerType(-1))

    def test_unsigned8_above_range(self) -> None:
        """Test Unsigned8 value above range should raise"""
        with self.assertRaises(ValueError):
            Unsigned8(IntegerType(256))

    def test_unsigned8_decode_out_of_range(self) -> None:
        """Decode value outside constraint range should raise"""
        # Encode 300 (outside 0..255)
        buf = ByteBuffer.wrap(b"\x02\x02\x01\x2c")  # INTEGER 300

        with self.assertRaises(ValueError):
            Unsigned8.get(buf)

    def test_port_number_valid(self) -> None:
        """Test valid PortNumber (1..65535)"""
        value = PortNumber(IntegerType(8080))
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        buf.set_pos(0)
        decoded = PortNumber.get(buf)
        self.assertEqual(decoded.value.value, 8080)

    def test_port_number_boundary(self) -> None:
        """Test PortNumber boundaries"""
        # Lower boundary
        value = PortNumber(IntegerType(1))
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        buf.set_pos(0)
        decoded = PortNumber.get(buf)
        self.assertEqual(decoded.value.value, 1)

        # Upper boundary
        value = PortNumber(IntegerType(65535))
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        buf.set_pos(0)
        decoded = PortNumber.get(buf)
        self.assertEqual(decoded.value.value, 65535)

    def test_temperature_negative(self) -> None:
        """Test Temperature with negative values (-40..85)"""
        value = Temperature(IntegerType(-40))
        buf = ByteBuffer.allocate(10)
        value.put(buf)

        buf.set_pos(0)
        decoded = Temperature.get(buf)
        self.assertEqual(decoded.value.value, -40)

    def test_temperature_positive(self) -> None:
        """Test Temperature with positive values"""
        value = Temperature(IntegerType(25))
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        buf.set_pos(0)
        decoded = Temperature.get(buf)
        self.assertEqual(decoded.value.value, 25)

    def test_temperature_out_of_range(self) -> None:
        """Test Temperature out of range"""
        with self.assertRaises(ValueError):
            Temperature(IntegerType(-41))

        with self.assertRaises(ValueError):
            Temperature(IntegerType(86))


class TestConstrainedEnumeratedType(unittest.TestCase):
    """Test ConstrainedType with ENUMERATED"""

    def setUp(self) -> None:
        """Set up test ConstrainedType for Enumerated"""
        # ServiceError ::= ENUMERATED (0..4)

        class ServiceError(ConstrainedType[EnumeratedType]):
            constraint_spec = ValueRange(0, 4)
            value: EnumeratedType

        self.ServiceError = ServiceError

    def test_valid_enumerated_encode(self) -> None:
        """Encode valid enumerated value"""
        value = self.ServiceError(EnumeratedType(2))
        buf = ByteBuffer.allocate(10)
        written = value.put(buf)

        self.assertEqual(written, 3)  # Tag + Length + Content
        self.assertEqual(bytes(buf)[:written], b"\x0a\x01\x02")

    def test_valid_enumerated_decode(self) -> None:
        """Decode valid enumerated value"""
        buf = ByteBuffer.wrap(b"\x0a\x01\x02")
        value = self.ServiceError.get(buf)

        self.assertEqual(value.value.value, 2)

    def test_enumerated_boundary(self) -> None:
        """Test enumerated boundaries"""
        # Lower boundary
        value = self.ServiceError(EnumeratedType(0))
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        buf.set_pos(0)
        decoded = self.ServiceError.get(buf)
        self.assertEqual(decoded.value.value, 0)

        # Upper boundary
        value = self.ServiceError(EnumeratedType(4))
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        buf.set_pos(0)
        decoded = self.ServiceError.get(buf)
        self.assertEqual(decoded.value.value, 4)

    def test_enumerated_out_of_range(self) -> None:
        """Test enumerated out of range"""
        with self.assertRaises(ValueError):
            self.ServiceError(EnumeratedType(5))

        with self.assertRaises(ValueError):
            self.ServiceError(EnumeratedType(-1))

    def test_enumerated_decode_out_of_range(self) -> None:
        """Decode enumerated outside constraint range"""
        # Encode 10 (outside 0..4)
        buf = ByteBuffer.wrap(b"\x0a\x01\x0a")

        with self.assertRaises(ValueError):
            self.ServiceError.get(buf)


class TestConstraintValidation(unittest.TestCase):
    """Test constraint validation logic"""

    def setUp(self) -> None:
        """Set up test constrained types"""

        class ConstrainedInt(ConstrainedType[IntegerType]):
            constraint_spec = ValueRange(10, 20)
            value: IntegerType

        self.ConstrainedInt = ConstrainedInt

    def test_constructor_validation(self) -> None:
        """Test validation at construction time"""
        # Valid values
        value1 = self.ConstrainedInt(IntegerType(10))
        value2 = self.ConstrainedInt(IntegerType(15))
        value3 = self.ConstrainedInt(IntegerType(20))

        self.assertEqual(value1.value.value, 10)
        self.assertEqual(value2.value.value, 15)
        self.assertEqual(value3.value.value, 20)

    def test_constructor_invalid_value(self) -> None:
        """Test invalid value at construction"""
        with self.assertRaises(ValueError):
            self.ConstrainedInt(IntegerType(9))

        with self.assertRaises(ValueError):
            self.ConstrainedInt(IntegerType(21))


class TestConstraintInheritance(unittest.TestCase):
    """Test constraint inheritance in subclasses"""

    def test_subclass_inherits_constraint(self) -> None:
        """Test that subclasses inherit parent constraint"""

        class BaseConstrained(ConstrainedType[IntegerType]):
            constraint_spec = ValueRange(0, 100)
            value: IntegerType

        class DerivedConstrained(BaseConstrained):
            value: IntegerType

        # Derived class should have same constraint
        value = DerivedConstrained(IntegerType(50))
        buf = ByteBuffer.allocate(10)
        value.put(buf)

        buf.set_pos(0)
        decoded = DerivedConstrained.get(buf)
        self.assertEqual(decoded.value.value, 50)

        # Out of range should still fail
        with self.assertRaises(ValueError):
            DerivedConstrained(IntegerType(101))


class LargeInt(ConstrainedType[IntegerType]):
    constraint_spec = ValueRange(0, 2**32 - 1)
    value: IntegerType


class TestConstraintWithLargeValues(unittest.TestCase):
    """Test constraints with large integer values"""

    def test_large_value_encode(self) -> None:
        """Encode large value within constraint"""
        value = LargeInt(IntegerType(2**32 - 1))
        buf = ByteBuffer.allocate(20)
        written = value.put(buf)

        # Should encode successfully
        self.assertGreater(written, 0)

    def test_large_value_decode(self) -> None:
        """Decode large value within constraint"""
        # First encode to get valid bytes
        value = LargeInt(IntegerType(2**31))
        buf = ByteBuffer.allocate(20)
        value.put(buf)

        buf.set_pos(0)
        decoded = LargeInt.get(buf)
        self.assertEqual(decoded.value.value, 2**31)

    def test_large_value_out_of_range(self) -> None:
        """Test large value outside constraint"""
        with self.assertRaises(ValueError):
            LargeInt(IntegerType(2**32))


class TestConstraintEdgeCases(unittest.TestCase):
    """Test edge cases for constraints"""

    def test_zero_range(self) -> None:
        """Test constraint with zero range (single value)"""

        class FixedValue(ConstrainedType[IntegerType]):
            constraint_spec = ValueRange(42, 42)
            value: IntegerType

        # Only value 42 is valid
        value = FixedValue(IntegerType(42))
        buf = ByteBuffer.allocate(10)
        value.put(buf)

        buf.set_pos(0)
        decoded = FixedValue.get(buf)
        self.assertEqual(decoded.value.value, 42)

        # Any other value should fail
        with self.assertRaises(ValueError):
            FixedValue(IntegerType(41))

        with self.assertRaises(ValueError):
            FixedValue(IntegerType(43))

    def test_full_integer_range(self) -> None:
        """Test constraint with full integer range"""

        class UnboundedInt(ConstrainedType[IntegerType]):
            constraint_spec = ValueRange(-2**63, 2**63 - 1)
            value: IntegerType

        # Should accept wide range
        value = UnboundedInt(IntegerType(0))
        buf = ByteBuffer.allocate(20)
        value.put(buf)

        buf.set_pos(0)
        decoded = UnboundedInt.get(buf)
        self.assertEqual(decoded.value.value, 0)


class TestConstraintRoundTrip(unittest.TestCase):
    """Test round-trip encode/decode with constraints"""

    def test_round_trip_valid_values(self) -> None:
        """Test round-trip for valid values"""

        class TestConstrained(ConstrainedType[IntegerType]):
            constraint_spec = ValueRange(-100, 100)
            value: IntegerType

        test_values = [-100, -50, 0, 50, 100]

        for value in test_values:
            with self.subTest(value=value):
                original = TestConstrained(IntegerType(value))
                buf = ByteBuffer.allocate(20)
                original.put(buf)

                buf.set_pos(0)
                decoded = TestConstrained.get(buf)

                self.assertEqual(decoded.value.value, value)

    def test_round_trip_preserves_constraint(self) -> None:
        """Test that constraint is preserved after round-trip"""

        class TestConstrained(ConstrainedType[IntegerType]):
            constraint_spec = ValueRange(0, 255)
            value: IntegerType

        original = TestConstrained(IntegerType(128))
        buf = ByteBuffer.allocate(20)
        original.put(buf)

        buf.set_pos(0)
        decoded = TestConstrained.get(buf)

        # Decoded value should still be constrained
        self.assertEqual(decoded.value.value, 128)

        # Should still reject out-of-range values
        with self.assertRaises(ValueError):
            TestConstrained(IntegerType(256))


class TestConstraintWithSequence(unittest.TestCase):
    """Test constraints in SEQUENCE components"""

    def test_constrained_component_in_sequence(self) -> None:
        """Test constrained type as SEQUENCE component"""
        from src.COSEMpdu.ber import SequenceType
        from src.COSEMpdu.x680 import NamedType
        from src.COSEMpdu.ber import BooleanType

        class ConstrainedInt(ConstrainedType[IntegerType]):
            constraint_spec = ValueRange(0, 255)
            value: IntegerType

        class TestSequence(SequenceType):
            components = (
                NamedType("id", ConstrainedInt),
                NamedType("flag", BooleanType),
            )

        # Valid sequence
        seq = TestSequence((
            ConstrainedInt(IntegerType(100)),
            BooleanType(True)
        ))

        buf = ByteBuffer.allocate(50)
        seq.put(buf)

        buf.set_pos(0)
        decoded = TestSequence.get(buf)

        self.assertEqual(decoded["id"].value.value, 100)
        self.assertTrue(decoded["flag"].value)

    def test_constrained_component_invalid_in_sequence(self) -> None:
        """Test invalid constrained type in SEQUENCE"""
        from src.COSEMpdu.ber import SequenceType
        from src.COSEMpdu.x680 import NamedType
        from src.COSEMpdu.ber import BooleanType

        class ConstrainedInt(ConstrainedType[IntegerType]):
            constraint_spec = ValueRange(0, 255)
            value: IntegerType

        class TestSequence(SequenceType):
            components = (
                NamedType("id", ConstrainedInt),
                NamedType("flag", BooleanType),
            )

        # Invalid value should fail at construction
        with self.assertRaises(ValueError):
            TestSequence((
                ConstrainedInt(IntegerType(300)),  # Out of range
                BooleanType(True)
            ))


if __name__ == "__main__":
    unittest.main()
