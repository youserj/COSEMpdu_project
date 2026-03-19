"""
Unit tests for ConstrainedType with BER encoding/decoding (X.680 §45, X.690)
Tests cover ValueRange constraints and validation during encode/decode
"""
import unittest
from typing import ClassVar
from dataclasses import dataclass
from COSEMpdu import x690
from src.COSEMpdu.byte_buffer import ByteBuffer
from src.COSEMpdu.ber import IntegerType, EnumeratedType
from src.COSEMpdu.x680 import ValueRange, Constraint


class TestValueRange(unittest.TestCase):
    """Test ValueRange constraint per X.680 §47.4"""
    
    def test_valid_range(self):
        """Valid range: lower <= upper"""
        range_constraint = ValueRange(0, 255)
        self.assertEqual(range_constraint.lower_endpoint, 0)
        self.assertEqual(range_constraint.upper_endpoint, 255)
    
    def test_invalid_range(self):
        """Invalid range: lower > upper should raise"""
        with self.assertRaises(ValueError):
            ValueRange(255, 0)
    
    def test_single_value_range(self):
        """Single value range: lower == upper"""
        range_constraint = ValueRange(42, 42)
        self.assertEqual(range_constraint.lower_endpoint, 42)
        self.assertEqual(range_constraint.upper_endpoint, 42)
    
    def test_negative_range(self):
        """Negative value range"""
        range_constraint = ValueRange(-128, 127)
        self.assertEqual(range_constraint.lower_endpoint, -128)
        self.assertEqual(range_constraint.upper_endpoint, 127)
    
    def test_contains_method(self):
        """Test contains() method"""
        range_constraint = ValueRange(0, 100)
        self.assertTrue(range_constraint.contains(0))
        self.assertTrue(range_constraint.contains(50))
        self.assertTrue(range_constraint.contains(100))
        self.assertFalse(range_constraint.contains(-1))
        self.assertFalse(range_constraint.contains(101))
    
    def test_str_representation(self):
        """Test string representation"""
        range_constraint = ValueRange(0, 255)
        self.assertEqual(str(range_constraint), "(0..255)")


class TestConstrainedIntegerType(unittest.TestCase):
    """Test ConstrainedType with INTEGER and ValueRange"""
    
    def setUp(self):
        """Set up test ConstrainedType classes"""
        # Unsigned8 ::= INTEGER (0..255)
        @dataclass
        class Unsigned8(IntegerType):
            constraint = Constraint(ValueRange(0, 255))
        
        # PortNumber ::= INTEGER (1..65535)
        @dataclass
        class PortNumber(IntegerType):
            constraint = Constraint(
                constraint_spec=ValueRange(1, 65535)
            )
        
        # Temperature ::= INTEGER (-40..85)
        @dataclass
        class Temperature(IntegerType):
            constraint= Constraint(
                constraint_spec=ValueRange(-40, 85)
            )
        
        self.Unsigned8 = Unsigned8
        self.PortNumber = PortNumber
        self.Temperature = Temperature
    
    def test_valid_unsigned8_encode(self):
        """Encode valid Unsigned8 value"""
        value = self.Unsigned8(100)
        buf = ByteBuffer.allocate(10)
        written = value.put(buf)
        
        self.assertEqual(written, 3)  # Tag + Length + Content
        self.assertEqual(bytes(buf)[:written], b'\x02\x01\x64')
    
    def test_valid_unsigned8_decode(self):
        """Decode valid Unsigned8 value"""
        buf = ByteBuffer.wrap(b'\x02\x01\x64')
        value = self.Unsigned8.get(buf)
        
        self.assertEqual(value.value, 100)
    
    def test_unsigned8_boundary_low(self):
        """Test Unsigned8 lower boundary (0)"""
        value = self.Unsigned8(0)
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        
        buf.set_pos(0)
        decoded = self.Unsigned8.get(buf)
        self.assertEqual(decoded.value, 0)
    
    def test_unsigned8_boundary_high(self):
        """Test Unsigned8 upper boundary (255)"""
        value = self.Unsigned8(255)
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        
        buf.set_pos(0)
        decoded = self.Unsigned8.get(buf)
        self.assertEqual(decoded.value, 255)
    
    def test_unsigned8_below_range(self):
        """Test Unsigned8 value below range should raise"""
        with self.assertRaises(ValueError):
            self.Unsigned8(-1)
    
    def test_unsigned8_above_range(self):
        """Test Unsigned8 value above range should raise"""
        with self.assertRaises(ValueError):
            self.Unsigned8(256)
    
    def test_unsigned8_decode_out_of_range(self):
        """Decode value outside constraint range should raise"""
        # Encode 300 (outside 0..255)
        buf = ByteBuffer.wrap(b'\x02\x02\x01\x2c')  # INTEGER 300
        
        with self.assertRaises(ValueError):
            self.Unsigned8.get(buf)
    
    def test_port_number_valid(self):
        """Test valid PortNumber (1..65535)"""
        value = self.PortNumber(8080)
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        
        buf.set_pos(0)
        decoded = self.PortNumber.get(buf)
        self.assertEqual(decoded.value, 8080)
    
    def test_port_number_boundary(self):
        """Test PortNumber boundaries"""
        # Lower boundary
        value = self.PortNumber(1)
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        buf.set_pos(0)
        decoded = self.PortNumber.get(buf)
        self.assertEqual(decoded.value, 1)
        
        # Upper boundary
        value = self.PortNumber(65535)
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        buf.set_pos(0)
        decoded = self.PortNumber.get(buf)
        self.assertEqual(decoded.value, 65535)
    
    def test_temperature_negative(self):
        """Test Temperature with negative values (-40..85)"""
        value = self.Temperature(-40)
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        
        buf.set_pos(0)
        decoded = self.Temperature.get(buf)
        self.assertEqual(decoded.value, -40)
    
    def test_temperature_positive(self):
        """Test Temperature with positive values"""
        value = self.Temperature(25)
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        
        buf.set_pos(0)
        decoded = self.Temperature.get(buf)
        self.assertEqual(decoded.value, 25)
    
    def test_temperature_out_of_range(self):
        """Test Temperature out of range"""
        with self.assertRaises(ValueError):
            self.Temperature(-41)
        
        with self.assertRaises(ValueError):
            self.Temperature(86)


class TestConstrainedEnumeratedType(unittest.TestCase):
    """Test ConstrainedType with ENUMERATED"""
    
    def setUp(self):
        """Set up test ConstrainedType for Enumerated"""
        # ServiceError ::= ENUMERATED (0..4)
        @dataclass
        class ServiceError(EnumeratedType):
            constraint = Constraint(
                constraint_spec=ValueRange(0, 4)
            )
        
        self.ServiceError = ServiceError
    
    def test_valid_enumerated_encode(self):
        """Encode valid enumerated value"""
        value = self.ServiceError(2)
        buf = ByteBuffer.allocate(10)
        written = value.put(buf)
        
        self.assertEqual(written, 3)  # Tag + Length + Content
        self.assertEqual(bytes(buf)[:written], b'\x0a\x01\x02')
    
    def test_valid_enumerated_decode(self):
        """Decode valid enumerated value"""
        buf = ByteBuffer.wrap(b'\x0a\x01\x02')
        value = self.ServiceError.get(buf)
        
        self.assertEqual(value.value, 2)
    
    def test_enumerated_boundary(self):
        """Test enumerated boundaries"""
        # Lower boundary
        value = self.ServiceError(0)
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        buf.set_pos(0)
        decoded = self.ServiceError.get(buf)
        self.assertEqual(decoded.value, 0)
        
        # Upper boundary
        value = self.ServiceError(4)
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        buf.set_pos(0)
        decoded = self.ServiceError.get(buf)
        self.assertEqual(decoded.value, 4)
    
    def test_enumerated_out_of_range(self):
        """Test enumerated out of range"""
        with self.assertRaises(ValueError):
            self.ServiceError(5)
        
        with self.assertRaises(ValueError):
            self.ServiceError(-1)
    
    def test_enumerated_decode_out_of_range(self):
        """Decode enumerated outside constraint range"""
        # Encode 10 (outside 0..4)
        buf = ByteBuffer.wrap(b'\x0a\x01\x0a')
        
        with self.assertRaises(ValueError):
            self.ServiceError.get(buf)


class TestConstraintValidation(unittest.TestCase):
    """Test constraint validation logic"""
    
    def setUp(self):
        """Set up test constrained types"""
        @dataclass
        class ConstrainedInt(IntegerType):
            constraint = Constraint(
                constraint_spec=ValueRange(10, 20)
            )
        
        self.ConstrainedInt = ConstrainedInt
    
    def test_constructor_validation(self):
        """Test validation at construction time"""
        # Valid values
        value1 = self.ConstrainedInt(10)
        value2 = self.ConstrainedInt(15)
        value3 = self.ConstrainedInt(20)
        
        self.assertEqual(value1.value, 10)
        self.assertEqual(value2.value, 15)
        self.assertEqual(value3.value, 20)
    
    def test_constructor_invalid_value(self):
        """Test invalid value at construction"""
        with self.assertRaises(ValueError):
            self.ConstrainedInt(9)
        
        with self.assertRaises(ValueError):
            self.ConstrainedInt(21)
    

class TestConstraintInheritance(unittest.TestCase):
    """Test constraint inheritance in subclasses"""
    
    def test_subclass_inherits_constraint(self):
        """Test that subclasses inherit parent constraint"""
        @dataclass
        class BaseConstrained(IntegerType):
            constraint = Constraint(
                constraint_spec=ValueRange(0, 100)
            )
        
        @dataclass
        class DerivedConstrained(BaseConstrained):
            pass
        
        # Derived class should have same constraint
        value = DerivedConstrained(50)
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        
        buf.set_pos(0)
        decoded = DerivedConstrained.get(buf)
        self.assertEqual(decoded.value, 50)
        
        # Out of range should still fail
        with self.assertRaises(ValueError):
            DerivedConstrained(101)


class TestConstraintWithLargeValues(unittest.TestCase):
    """Test constraints with large integer values"""
    
    def setUp(self):
        """Set up test constrained types with large ranges"""
        @dataclass
        class LargeInt(IntegerType):
            constraint = Constraint(
                constraint_spec=ValueRange(0, 2**32 - 1)
            )
        
        self.LargeInt = LargeInt
    
    def test_large_value_encode(self):
        """Encode large value within constraint"""
        value = self.LargeInt(2**32 - 1)
        buf = ByteBuffer.allocate(20)
        written = value.put(buf)
        
        # Should encode successfully
        self.assertGreater(written, 0)
    
    def test_large_value_decode(self):
        """Decode large value within constraint"""
        # First encode to get valid bytes
        value = self.LargeInt(2**31)
        buf = ByteBuffer.allocate(20)
        value.put(buf)
        
        buf.set_pos(0)
        decoded = self.LargeInt.get(buf)
        self.assertEqual(decoded.value, 2**31)
    
    def test_large_value_out_of_range(self):
        """Test large value outside constraint"""
        with self.assertRaises(ValueError):
            self.LargeInt(2**32)


class TestConstraintEdgeCases(unittest.TestCase):
    """Test edge cases for constraints"""
    
    def test_zero_range(self):
        """Test constraint with zero range (single value)"""
        @dataclass
        class FixedValue(IntegerType):
            constraint = Constraint(
                constraint_spec=ValueRange(42, 42)
            )
        
        # Only value 42 is valid
        value = FixedValue(42)
        buf = ByteBuffer.allocate(10)
        value.put(buf)
        
        buf.set_pos(0)
        decoded = FixedValue.get(buf)
        self.assertEqual(decoded.value, 42)
        
        # Any other value should fail
        with self.assertRaises(ValueError):
            FixedValue(41)
        
        with self.assertRaises(ValueError):
            FixedValue(43)
    
    def test_full_integer_range(self):
        """Test constraint with full integer range"""
        @dataclass
        class UnboundedInt(IntegerType):
            constraint = Constraint(
                constraint_spec=ValueRange(-2**63, 2**63 - 1)
            )
        
        # Should accept wide range
        value = UnboundedInt(0)
        buf = ByteBuffer.allocate(20)
        value.put(buf)
        
        buf.set_pos(0)
        decoded = UnboundedInt.get(buf)
        self.assertEqual(decoded.value, 0)


class TestConstraintRoundTrip(unittest.TestCase):
    """Test round-trip encode/decode with constraints"""
    
    def test_round_trip_valid_values(self):
        """Test round-trip for valid values"""
        @dataclass
        class TestConstrained(IntegerType):
            constraint = Constraint(
                constraint_spec=ValueRange(-100, 100)
            )
        
        test_values = [-100, -50, 0, 50, 100]
        
        for value in test_values:
            with self.subTest(value=value):
                original = TestConstrained(value)
                buf = ByteBuffer.allocate(20)
                original.put(buf)
                
                buf.set_pos(0)
                decoded = TestConstrained.get(buf)
                
                self.assertEqual(decoded.value, value)
    
    def test_round_trip_preserves_constraint(self):
        """Test that constraint is preserved after round-trip"""
        @dataclass
        class TestConstrained(IntegerType):
            constraint = Constraint(
                constraint_spec=ValueRange(0, 255)
            )
        
        original = TestConstrained(128)
        buf = ByteBuffer.allocate(20)
        original.put(buf)
        
        buf.set_pos(0)
        decoded = TestConstrained.get(buf)
        
        # Decoded value should still be constrained
        self.assertEqual(decoded.value, 128)
        
        # Should still reject out-of-range values
        with self.assertRaises(ValueError):
            TestConstrained(256)


class TestConstraintWithSequence(unittest.TestCase):
    """Test constraints in SEQUENCE components"""
    
    def test_constrained_component_in_sequence(self):
        """Test constrained type as SEQUENCE component"""
        from src.COSEMpdu.ber import SequenceType
        from src.COSEMpdu.x680 import NamedType
        from src.COSEMpdu.ber import BooleanType
        
        @dataclass
        class ConstrainedInt(IntegerType):
            constraint = Constraint(
                constraint_spec=ValueRange(0, 255)
            )
        
        @dataclass(frozen=True)
        class TestSequence(SequenceType):
            components = (
                NamedType('id', ConstrainedInt),
                NamedType('flag', BooleanType),
            )
            id: ConstrainedInt
            flag: BooleanType
        
        # Valid sequence
        seq = TestSequence(
            id=ConstrainedInt(100),
            flag=BooleanType(True)
        )
        
        buf = ByteBuffer.allocate(50)
        seq.put(buf)
        
        buf.set_pos(0)
        decoded = TestSequence.get(buf)
        
        self.assertEqual(decoded.id.value, 100)
        self.assertTrue(decoded.flag.value)
    
    def test_constrained_component_invalid_in_sequence(self):
        """Test invalid constrained type in SEQUENCE"""
        from src.COSEMpdu.ber import SequenceType
        from src.COSEMpdu.x680 import NamedType
        from src.COSEMpdu.ber import BooleanType
        
        @dataclass
        class ConstrainedInt(IntegerType):
            constraint = Constraint(
                constraint_spec=ValueRange(0, 255)
            )
        
        @dataclass(frozen=True)
        class TestSequence(SequenceType):
            components = (
                NamedType('id', ConstrainedInt),
                NamedType('flag', BooleanType),
            )
            id: ConstrainedInt
            flag: BooleanType
        
        # Invalid value should fail at construction
        with self.assertRaises(ValueError):
            TestSequence(
                id=ConstrainedInt(300),  # Out of range
                flag=BooleanType(True)
            )


if __name__ == '__main__':
    unittest.main()