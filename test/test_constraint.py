"""
Tests for constraint specifications and constrained ASN.1 types.

Covers:
    - ConstraintSpec hierarchy (ValueRange, SingleValue, SizeConstraint)
    - ConstraintError
    - ConstrainedType.get_lc() safety wrapper
    - ConstrainedIntegerType (init, encode/decode via BER IntegerType)
    - ConstrainedBitStringType, ConstrainedSequenceOfType, ConstrainedOctetString
"""
import sys
import unittest
from typing import ClassVar
from StructResult.result import Error, NULL

sys.path.insert(0, "src")

from COSEMpdu.byte_buffer import ByteBuffer
from COSEMpdu.x680 import ConstraintError, ConstraintSpec, SingleValue, SizeConstraint, ValueRange
from COSEMpdu.axdr import ConstrainedIntegerType, ConstrainedBitStringType, ConstrainedSequenceOfType, ConstrainedOctetStringType, IntegerType

# from COSEMpdu.x680.bit_string_type import BitStringType
# from COSEMpdu.x680.octet_string_type import OctetStringType
# from COSEMpdu.x680.sequence_of_type import SequenceOfType
# from COSEMpdu.x680.type import INTEGER, BIT_STRING, OCTET_STRING


# ═══════════════════════════════════════════════════════════════
# Helper: dynamically build a ConstrainedIntegerType subclass
# ═══════════════════════════════════════════════════════════════

def make_constrained_integer(class_name: str, constraint_spec: ConstraintSpec):
    """Create a new ConstrainedIntegerType subclass with the given constraint."""
    return type(
        class_name,
        (ConstrainedIntegerType,),
        {
            "constraint_spec": constraint_spec,
            "exception_spec": None,
        },
    )


# ═══════════════════════════════════════════════════════════════
# ValueRange
# ═══════════════════════════════════════════════════════════════


class TestValueRange(unittest.TestCase):
    def test_contains_inclusive(self) -> None:
        vr = ValueRange(0, 100)
        self.assertTrue(vr.contains(0))
        self.assertTrue(vr.contains(50))
        self.assertTrue(vr.contains(100))
        self.assertFalse(vr.contains(-1))
        self.assertFalse(vr.contains(101))

    def test_contains_exclusive_lower(self) -> None:
        vr = ValueRange(0, 100, lower_inclusive=False)
        self.assertFalse(vr.contains(0))
        self.assertTrue(vr.contains(1))
        self.assertTrue(vr.contains(100))

    def test_contains_exclusive_upper(self) -> None:
        vr = ValueRange(0, 100, upper_inclusive=False)
        self.assertTrue(vr.contains(0))
        self.assertTrue(vr.contains(99))
        self.assertFalse(vr.contains(100))

    def test_contains_exclusive_both(self) -> None:
        vr = ValueRange(0, 100, lower_inclusive=False, upper_inclusive=False)
        self.assertFalse(vr.contains(0))
        self.assertTrue(vr.contains(50))
        self.assertFalse(vr.contains(100))

    def test_str_inclusive(self) -> None:
        vr = ValueRange(0, 255)
        self.assertEqual(str(vr), "(0..255)")

    def test_str_exclusive_lower(self) -> None:
        vr = ValueRange(0, 255, lower_inclusive=False)
        self.assertEqual(str(vr), "(0<..255)")

    def test_str_exclusive_upper(self) -> None:
        vr = ValueRange(0, 255, upper_inclusive=False)
        self.assertEqual(str(vr), "(0..<255)")


# ═══════════════════════════════════════════════════════════════
# SingleValue
# ═══════════════════════════════════════════════════════════════


class TestSingleValue(unittest.TestCase):
    def test_contains_int(self) -> None:
        sv = SingleValue(42)
        self.assertTrue(sv.contains(42))
        self.assertFalse(sv.contains(0))
        self.assertFalse(sv.contains(43))

    def test_contains_str(self) -> None:
        sv = SingleValue("A")
        self.assertTrue(sv.contains("A"))
        self.assertFalse(sv.contains("B"))

    def test_str(self) -> None:
        sv = SingleValue(42)
        self.assertEqual(str(sv), "42")

    def test_str_string_value(self) -> None:
        sv = SingleValue("X")
        self.assertEqual(str(sv), "X")


# ═══════════════════════════════════════════════════════════════
# SizeConstraint
# ═══════════════════════════════════════════════════════════════


class TestSizeConstraint(unittest.TestCase):
    def test_fixed_size_contains(self) -> None:
        sc = SizeConstraint(4)
        self.assertTrue(sc.contains(4))
        self.assertFalse(sc.contains(3))
        self.assertFalse(sc.contains(5))

    def test_range_size_contains(self) -> None:
        sc = SizeConstraint(max_size=10, min_size=2)
        self.assertTrue(sc.contains(2))
        self.assertTrue(sc.contains(10))
        self.assertTrue(sc.contains(5))
        self.assertFalse(sc.contains(1))
        self.assertFalse(sc.contains(11))

    def test_str_fixed(self) -> None:
        sc = SizeConstraint(4)
        self.assertEqual(str(sc), "SIZE(4)")

    def test_str_range(self) -> None:
        sc = SizeConstraint(max_size=10, min_size=2)
        self.assertEqual(str(sc), "SIZE(2..10)")


# ═══════════════════════════════════════════════════════════════
# ConstraintError
# ═══════════════════════════════════════════════════════════════


class TestConstraintError(unittest.TestCase):
    def test_is_exception(self) -> None:
        self.assertTrue(issubclass(ConstraintError, Exception))

    def test_raise_and_catch(self) -> None:
        with self.assertRaises(ConstraintError) as ctx:
            raise ConstraintError("out of range")
        self.assertIn("out of range", str(ctx.exception))


# ═══════════════════════════════════════════════════════════════
# ConstrainedType.get_lc – safety wrapper
# ═══════════════════════════════════════════════════════════════


class TestConstrainedTypeSafety(unittest.TestCase):
    """Test that ConstrainedType.get_lc catches ConstraintError and returns
    a safe StructResult Error rather than propagating the exception."""

    def test_get_lc_catches_constraint_error(self) -> None:
        # Build a constrained integer 0..100, then decode a value > 100
        # via the BER IntegerType codec.
        class SmallInt(ConstrainedIntegerType):
            constraint_spec: ClassVar[ConstraintSpec] = ValueRange(0, 100)
            exception_spec = None

        # BER-encode 200 as a two's-complement integer (0x00 0xc8)
        ber_int = IntegerType(200)
        buf = ByteBuffer.wrap(b"")
        ber_int.put(buf)
        encoded = bytes(buf)

        # Decode with ConstrainedIntegerType — ConstrainedType.get_lc()
        # wraps ConstrainedIntegerType.__init__ which raises ConstraintError
        # inside get_lc's try/except → returns Error
        from StructResult.result import ValueOrError, Error

        buf2 = ByteBuffer.wrap(encoded)
        result = SmallInt.get(buf2)
        self.assertIsInstance(result, Error)

    def test_get_lc_allows_ok_value(self) -> None:
        class SmallInt(ConstrainedIntegerType):
            constraint_spec: ClassVar[ConstraintSpec] = ValueRange(0, 100)
            exception_spec = None

        int = IntegerType(50)
        buf = ByteBuffer.allocate(100)
        if isinstance(int.put(buf), Error):
            self.fail("put Error")
        encoded = bytes(buf)

        buf2 = ByteBuffer.wrap(encoded)
        result = SmallInt.get(buf2)
        self.assertIsInstance(result, SmallInt)
        self.assertEqual(result.value, 50)


# ═══════════════════════════════════════════════════════════════
# ConstrainedIntegerType
# ═══════════════════════════════════════════════════════════════


class TestConstrainedIntegerType(unittest.TestCase):
    """Tests for ConstrainedIntegerType: constraint validation in __init__,
    signed/fixed_length derivation via _init_subclass."""

    def test_valid_value(self) -> None:
        T = make_constrained_integer("_U8", ValueRange(0, 255))
        obj = T(42)
        self.assertEqual(obj.value, 42)

    def test_invalid_value_below(self) -> None:
        T = make_constrained_integer("_U8", ValueRange(0, 255))
        self.assertTrue(T.new(-1).has(NULL, ConstraintError))

    def test_invalid_value_above(self) -> None:
        T = make_constrained_integer("_U8", ValueRange(0, 255))
        self.assertTrue(T.new(256).has(NULL, ConstraintError))

    def test_boundary_lower(self) -> None:
        T = make_constrained_integer("_U8", ValueRange(0, 255))
        obj = T(0)
        self.assertEqual(obj.value, 0)

    def test_boundary_upper(self) -> None:
        T = make_constrained_integer("_U8", ValueRange(0, 255))
        obj = T(255)
        self.assertEqual(obj.value, 255)

    def test_unsigned_when_lower_non_negative(self) -> None:
        T = make_constrained_integer("_U16", ValueRange(0, 65535))
        self.assertEqual(T.signed, False)
        self.assertIsNotNone(T.fixed_length)

    def test_fixed_length_derivation(self) -> None:
        """Range 0..255 → 8 bits → 1 octet fixed_length"""
        T = make_constrained_integer("_U8", ValueRange(0, 255))
        self.assertEqual(T.fixed_length, 1)

    def test_fixed_length_wide_range(self) -> None:
        """Range 0..65535 → 16 bits → 2 octets"""
        T = make_constrained_integer("_U16", ValueRange(0, 65535))
        self.assertEqual(T.fixed_length, 2)

    def test_repr(self) -> None:
        T = make_constrained_integer("_U8", ValueRange(0, 255))
        obj = T(42)
        r = repr(obj)
        self.assertIn("_U8", r)
        self.assertIn("42", r)

    def test_str_uses_named_numbers(self) -> None:
        """If named_numbers is defined, str() returns identifier."""
        class Result(make_constrained_integer("_R", ValueRange(0, 1))):
            Success: int = 0
            Failure: int = 1

        obj = Result(0)
        self.assertEqual(obj.value, Result.Success)


# ═══════════════════════════════════════════════════════════════
# ConstrainedBitStringType
# ═══════════════════════════════════════════════════════════════


class TestConstrainedBitStringType(unittest.TestCase):
    def test_valid_exact_size(self) -> None:
        class BS8(ConstrainedBitStringType):
            constraint_spec: ClassVar[ConstraintSpec] = SizeConstraint(8)
            exception_spec = None

        obj = BS8((1, 0, 1, 0, 1, 0, 1, 0))
        self.assertEqual(len(obj.value), 8)

    def test_invalid_size(self) -> None:
        class BS8(ConstrainedBitStringType):
            constraint_spec: ClassVar[ConstraintSpec] = SizeConstraint(8)
            exception_spec = None

        self.assertTrue(BS8.new((1, 0, 1)).has(NULL, ConstraintError))

    def test_fixed_length_set(self) -> None:
        class BS8(ConstrainedBitStringType):
            constraint_spec: ClassVar[ConstraintSpec] = SizeConstraint(8)
            exception_spec = None

        self.assertEqual(BS8.fixed_length, 8)


# ═══════════════════════════════════════════════════════════════
# ConstrainedSequenceOfType
# ═══════════════════════════════════════════════════════════════


class TestConstrainedSequenceOfType(unittest.TestCase):
    def test_valid_exact_count(self) -> None:
        class SO3(ConstrainedSequenceOfType):
            constraint_spec: ClassVar[ConstraintSpec] = SizeConstraint(3)
            exception_spec = None

        # Avoid _T requirement; just check __init__ validation
        # ConstrainedSequenceOfType.__init__ only checks fixed_length vs len(value)
        # _init_subclass calls super(__init_subclass__) → SequenceOfType._init_subclass
        # which looks for _T annotation. We'll test only the fixed_length/fixed_count aspect.
        # For now test that fixed_length forces the correct subclass behaviour.

        self.assertEqual(SO3.fixed_length, 3)

    def test_fixed_length_set(self) -> None:
        class SO5(ConstrainedSequenceOfType):
            constraint_spec: ClassVar[ConstraintSpec] = SizeConstraint(5)
            exception_spec = None

        self.assertEqual(SO5.fixed_length, 5)


# ═══════════════════════════════════════════════════════════════
# ConstrainedOctetString
# ═══════════════════════════════════════════════════════════════


class TestConstrainedOctetString(unittest.TestCase):
    def test_valid_exact_size(self) -> None:
        class OS4(ConstrainedOctetStringType):
            constraint_spec: ClassVar[ConstraintSpec] = SizeConstraint(4)
            exception_spec = None

        obj = OS4(b"\x01\x02\x03\x04")
        self.assertEqual(len(obj.value), 4)

    def test_invalid_size(self) -> None:
        class OS4(ConstrainedOctetStringType):
            constraint_spec: ClassVar[ConstraintSpec] = SizeConstraint(4)
            exception_spec = None

        self.assertTrue(OS4.new(b"\x01\x02").has(NULL, ConstraintError))

    def test_fixed_length_set(self) -> None:
        class OS4(ConstrainedOctetStringType):
            constraint_spec: ClassVar[ConstraintSpec] = SizeConstraint(4)
            exception_spec = None

        self.assertEqual(OS4.fixed_length, 4)

    def test_default_all_zeroes(self) -> None:
        class OS4(ConstrainedOctetStringType):
            constraint_spec: ClassVar[ConstraintSpec] = SizeConstraint(4)
            exception_spec = None

        obj = OS4.default()
        self.assertEqual(obj.value, b"\x00\x00\x00\x00")


if __name__ == "__main__":
    unittest.main()