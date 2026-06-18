"""
Unit tests for Data and TypeDescription encoding/decoding (A-XDR)

Standards:
    - COSEMpdu_GB83.txt: Data and TypeDescription definition
    - IEC 61334-6 §6.6: CHOICE encoding (A-XDR)
    - IEC 61334-6 §6.4-6.5: BIT STRING, OCTET STRING encoding
"""
from typing import Final
from dataclasses import dataclass
import unittest
from StructResult.result import Error, NULL
from src.COSEMpdu.x680 import ConstraintError
from src.COSEMpdu.byte_buffer import ByteBuffer
from src.COSEMpdu.data import (
    # TypeDescription types
    ExternallyData,
    DiscriminatedUnion,
    OctetStringType,
    SequenceOfData,
    TypeDescription,
    TypeDescriptionArray,
    TypeDescriptionStructure,
    TypeDescriptionBoolean,
    TypeDescriptionOctetString,
    TypeDescriptionVisibleString,
    TypeDescriptionInteger,
    TypeDescriptionUnsigned,
    TypeDescriptionLong,
    TypeDescriptionLongUnsigned,
    TypeDescriptionEnum,
    TypeDescriptionFloat32,
    TypeDescriptionFloat64,
    TypeDescriptionDateTime,
    TypeDescriptionDate,
    TypeDescriptionTime,
    TypeDescriptionDontCare,
    # Data types
    Data,
    NullData,
    Array,
    Structure,
    Boolean,
    BitString,
    DoubleLong,
    DoubleLongUnsigned,
    OctetString,
    VisibleString,
    Utf8String,
    Bcd,
    Integer,
    Long,
    Unsigned,
    LongUnsigned,
    CompactArray,
    ContentsDescription,
    ArrayContents,
    Long64,
    Long64Unsigned,
    Enum,
    Float32,
    Float64,
    Time,
    DateTime,
    Date,
    DontCare,
    Unsigned16
)
from src.COSEMpdu import axdr


@dataclass
class RestrictionByEntry(Structure):
    """restriction_by_entry"""
    from_entry: DoubleLongUnsigned
    to_entry: DoubleLongUnsigned


class TestSequence(unittest.TestCase):
    def test_Sequence(self) -> None:
        r1 = RestrictionByEntry(
            DoubleLongUnsigned(1),
            DoubleLongUnsigned(2)
        )
        buf = ByteBuffer.allocate(20)
        r1.put(buf)
        buf.set_pos(0)
        r2 = RestrictionByEntry.get(buf)
        self.assertEqual(r1, r2)
        buf.set_pos(0)
        data = Data.get(buf)
        print(data)


class TestTypeDescriptionArray(unittest.TestCase):
    """Test TypeDescription array [1]"""

    def test_encode_decode(self) -> None:
        """Test array encoding/decoding"""
        # array: SEQUENCE { number-of-elements Unsigned16, type-description TypeDescription }
        original = TypeDescription(TypeDescriptionArray(
            Unsigned16(5),
            TypeDescription(TypeDescriptionInteger(None))
        ))
        buf = ByteBuffer.allocate(50)
        original.put(buf)
        buf.set_pos(0)
        if isinstance(decoded := TypeDescription.get(buf), Error):
            self.fail("Error")
        self.assertIsInstance(decoded.value, TypeDescriptionArray)
        self.assertEqual(decoded.value.number_of_elements.value, 5)


class TestTypeDescriptionStructure(unittest.TestCase):
    """Test TypeDescription structure [2]"""

    def test_encode_decode(self) -> None:
        """Test structure encoding/decoding"""
        # structure: SEQUENCE OF TypeDescription
        elements = SequenceOfData([
            TypeDescription(TypeDescriptionInteger(None)),
            TypeDescription(TypeDescriptionBoolean(None)),
        ])
        original = TypeDescription(TypeDescriptionStructure(elements))
        buf = ByteBuffer.allocate(50)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertIsInstance(decoded.value, TypeDescriptionStructure)
        self.assertEqual(len(decoded.value.value), 2)


class TestTypeDescriptionBoolean(unittest.TestCase):
    """Test TypeDescription boolean [3]"""

    def test_encode_decode(self) -> None:
        """Test boolean encoding/decoding"""
        original = TypeDescription(TypeDescriptionBoolean(None))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertIsInstance(decoded.value, TypeDescriptionBoolean)


class TestTypeDescriptionOctetString(unittest.TestCase):
    """Test TypeDescription octet-string [9]"""

    def test_encode_decode(self) -> None:
        """Test octet-string encoding/decoding"""
        original = TypeDescription(TypeDescriptionOctetString(None))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertIsInstance(decoded.value, TypeDescriptionOctetString)


class TestTypeDescriptionInteger(unittest.TestCase):
    """Test TypeDescription integer [15]"""

    def test_encode_decode(self) -> None:
        """Test integer encoding/decoding"""
        original = TypeDescription(TypeDescriptionInteger(None))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertIsInstance(decoded.value, TypeDescriptionInteger)


class TestTypeDescriptionUnsigned(unittest.TestCase):
    """Test TypeDescription unsigned [17]"""

    def test_encode_decode(self) -> None:
        """Test unsigned encoding/decoding"""
        original = TypeDescription(TypeDescriptionUnsigned(None))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertIsInstance(decoded.value, TypeDescriptionUnsigned)


class TestTypeDescriptionFloat32(unittest.TestCase):
    """Test TypeDescription float32 [23]"""

    def test_encode_decode(self) -> None:
        """Test float32 encoding/decoding"""
        original = TypeDescription(TypeDescriptionFloat32(None))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertIsInstance(decoded.value, TypeDescriptionFloat32)


class TestTypeDescriptionDateTime(unittest.TestCase):
    """Test TypeDescription date-time [25]"""

    def test_encode_decode(self) -> None:
        """Test date-time encoding/decoding"""
        original = TypeDescription(TypeDescriptionDateTime(None))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertIsInstance(decoded.value, TypeDescriptionDateTime)


class TestTypeDescriptionDontCare(unittest.TestCase):
    """Test TypeDescription dont-care [255]"""

    def test_encode_decode(self) -> None:
        """Test dont-care encoding/decoding"""
        original = TypeDescription(TypeDescriptionDontCare(None))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertIsInstance(decoded.value, TypeDescriptionDontCare)
        self.assertEqual(TypeDescriptionDontCare.tag, 255)


class TestDataNullData(unittest.TestCase):
    """Test Data null-data [0]"""

    def test_encode_decode(self) -> None:
        """Test null-data encoding/decoding"""
        original = Data(NullData(None))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, NullData)

    def test_tag_number(self) -> None:
        """Test tag number is 0"""
        self.assertEqual(NullData.tag, 0)


class TestDataBoolean(unittest.TestCase):
    """Test Data boolean [3]"""

    def test_encode_decode_true(self) -> None:
        """Test boolean TRUE encoding/decoding"""
        original = Data(Boolean(1))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Boolean)
        self.assertTrue(decoded.value.value)

    def test_encode_decode_false(self) -> None:
        """Test boolean FALSE encoding/decoding"""
        original = Data(Boolean(0))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Boolean)
        self.assertFalse(decoded.value.value)


class TestDataInteger(unittest.TestCase):
    """Test Data integer [15] (Integer8)"""

    def test_encode_decode_positive(self) -> None:
        """Test integer positive value encoding/decoding"""
        original = Data(Integer(127))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Integer)
        self.assertEqual(decoded.value.value, 127)

    def test_encode_decode_negative(self) -> None:
        """Test integer negative value encoding/decoding"""
        original = Data(Integer(-128))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Integer)
        self.assertEqual(decoded.value.value, -128)

    def test_encode_decode_zero(self) -> None:
        """Test integer zero value encoding/decoding"""
        original = Data(Integer(0))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Integer)
        self.assertEqual(decoded.value.value, 0)


class TestDataUnsigned(unittest.TestCase):
    """Test Data unsigned [17] (Unsigned8)"""

    def test_encode_decode(self) -> None:
        """Test unsigned encoding/decoding"""
        original = Data(Unsigned(255))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Unsigned)
        self.assertEqual(decoded.value.value, 255)


class TestDataLong(unittest.TestCase):
    """Test Data long [16] (Integer16)"""

    def test_encode_decode(self) -> None:
        """Test long encoding/decoding"""
        original = Data(Long(32767))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Long)
        self.assertEqual(decoded.value.value, 32767)


class TestDataLongUnsigned(unittest.TestCase):
    """Test Data long-unsigned [18] (Unsigned16)"""

    def test_encode_decode(self) -> None:
        """Test long-unsigned encoding/decoding"""
        original = Data(LongUnsigned(65535))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, LongUnsigned)
        self.assertEqual(decoded.value.value, 65535)


class TestDataDoubleLong(unittest.TestCase):
    """Test Data double-long [5] (Integer32)"""

    def test_encode_decode(self) -> None:
        """Test double-long encoding/decoding"""
        original = Data(DoubleLong(2147483647))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, DoubleLong)
        self.assertEqual(decoded.value.value, 2147483647)


class TestDataDoubleLongUnsigned(unittest.TestCase):
    """Test Data double-long-unsigned [6] (Unsigned32)"""

    def test_encode_decode(self) -> None:
        """Test double-long-unsigned encoding/decoding"""
        original = Data(DoubleLongUnsigned(4294967295))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, DoubleLongUnsigned)
        self.assertEqual(decoded.value.value, 4294967295)


class TestDataLong64(unittest.TestCase):
    """Test Data long64 [20] (Integer64)"""

    def test_encode_decode(self) -> None:
        """Test long64 encoding/decoding"""
        original = Data(Long64(9223372036854775807))
        buf = ByteBuffer.allocate(20)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Long64)
        self.assertEqual(decoded.value.value, 9223372036854775807)


class TestDataLong64Unsigned(unittest.TestCase):
    """Test Data long64-unsigned [21] (Unsigned64)"""

    def test_encode_decode(self) -> None:
        """Test long64-unsigned encoding/decoding"""
        original = Data(Long64Unsigned(18446744073709551615))
        buf = ByteBuffer.allocate(20)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Long64Unsigned)
        self.assertEqual(decoded.value.value, 18446744073709551615)


class TestDataOctetString(unittest.TestCase):
    """Test Data octet-string [9]"""

    def test_encode_decode_empty(self) -> None:
        """Test octet-string empty encoding/decoding"""
        original = Data(OctetString(b""))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, OctetString)
        self.assertEqual(decoded.value.value, b"")

    def test_encode_decode_data(self) -> None:
        """Test octet-string with data encoding/decoding"""
        original = Data(OctetString(b"\x00\x01\x02\x03"))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, OctetString)
        self.assertEqual(decoded.value.value, b"\x00\x01\x02\x03")


class TestDataVisibleString(unittest.TestCase):
    """Test Data visible-string [10]"""

    def test_encode_decode(self) -> None:
        """Test visible-string encoding/decoding"""
        original = Data(VisibleString("Hello"))
        buf = ByteBuffer.allocate(20)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, VisibleString)
        self.assertEqual(decoded.value.value, "Hello")


class TestDataUtf8String(unittest.TestCase):
    """Test Data utf8-string [12]"""

    def test_encode_decode(self) -> None:
        """Test utf8-string encoding/decoding"""
        original = Data(Utf8String("Привет"))
        buf = ByteBuffer.allocate(20)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Utf8String)
        self.assertEqual(decoded.value.value, "Привет")


class TestDataBitString(unittest.TestCase):
    """Test Data bit-string [4]"""

    def test_encode_decode(self) -> None:
        """Test bit-string encoding/decoding"""
        bits = (1, 0, 1, 1, 0, 0, 1)
        original = Data(BitString(bits))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, BitString)
        self.assertEqual(decoded.value.value, bits)


class TestDataEnum(unittest.TestCase):
    """Test Data enum [22] (Unsigned8)"""

    def test_encode_decode(self) -> None:
        """Test enum encoding/decoding"""
        class MyEnum(Enum):
            NO = 0
            ONE: Final = 1
            TWO: Final = 2

        original = MyEnum(42)
        self.assertTrue(int(original), 42)
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Enum)
        self.assertEqual(decoded, Data(Enum(42)))


class TestDataFloat32(unittest.TestCase):
    """Test Data float32 [23] (OCTET STRING SIZE(4))"""

    def test_encode_decode_valid(self) -> None:
        """Test float32 valid 4-byte encoding/decoding"""
        original = Data(Float32.from_float(3.1422341))  # π approx
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Float32)
        self.assertEqual(len(decoded.value.value), 4)


class TestDataFloat64(unittest.TestCase):
    """Test Data float64 [24] (OCTET STRING SIZE(8))"""

    def test_encode_decode_valid(self) -> None:
        """Test float64 valid 8-byte encoding/decoding"""
        original: Data = Data(Float64(b"\x40\x09\x21\xFB\x54\x44\x2D\x18"))
        buf = ByteBuffer.allocate(20)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(float(original.value), float(decoded.value))
        self.assertIsInstance(decoded.value, Float64)
        self.assertEqual(len(decoded.value.value), 8)


class TestDataDateTime(unittest.TestCase):
    """Test Data date-time [25] (OCTET STRING SIZE(12))"""

    def test_encode_decode_valid(self) -> None:
        """Test date-time valid 12-byte encoding/decoding"""
        # DLMS date-time format: 12 bytes
        dt_bytes = b"\x07\xE4\x01\x01\x0C\x00\x00\x00\xFF\x88\x00\x00"
        original = Data(DateTime(dt_bytes))
        buf = ByteBuffer.allocate(20)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, DateTime)
        self.assertEqual(len(decoded.value.value), 12)

    def test_encode_decode_invalid_length(self) -> None:
        """Test date-time invalid length raises error"""
        self.assertTrue(Data.new(DateTime.new(b"\x00" * 11)).has(NULL, ConstraintError))


class TestDataDate(unittest.TestCase):
    """Test Data date [26] (OCTET STRING SIZE(5))"""

    def test_encode_decode_valid(self) -> None:
        """Test date valid 5-byte encoding/decoding"""
        # DLMS date format: 5 bytes
        date_bytes = b"\x07\xE4\x01\x01\xFF"
        original = Data(Date(date_bytes))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Date)
        self.assertEqual(len(decoded.value.value), 5)

    def test_encode_decode_invalid_length(self) -> None:
        """Test date invalid length raises error"""
        self.assertTrue(Data.new(Date.new(b"\x00" * 4)).has(NULL, ConstraintError))  # Only 4 bytes


class TestDataTime(unittest.TestCase):
    """Test Data time [27] (OCTET STRING SIZE(4))"""

    def test_encode_decode_valid(self) -> None:
        """Test time valid 4-byte encoding/decoding"""
        # DLMS time format: 4 bytes
        time_bytes = b"\x0C\x00\x00\x00"
        original = Data(Time(time_bytes))
        self.assertEqual(Time.fromisoformat(original.value.isoformat()).value, time_bytes)
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Time)
        self.assertEqual(len(decoded.value.value), 4)

    def test_encode_decode_invalid_length(self) -> None:
        """Test time invalid length raises error"""
        self.assertTrue(Data.new(Time.new(b"\x00" * 3)).has(NULL, ConstraintError))  # Only 3 bytes


class TestDataArray(unittest.TestCase):
    """Test Data array [1] (SEQUENCE OF Data)"""

    def test_encode_decode_empty(self) -> None:
        """Test array empty encoding/decoding"""
        original = Data(Array())
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Array)
        self.assertEqual(len(decoded.value.value), 0)

    def test_encode_decode_with_elements(self) -> None:
        """Test array with elements encoding/decoding"""
        MyArray = Array[Integer]
        original = MyArray([Integer(1), Integer(2), Integer(3)])
        buf = ByteBuffer.allocate(50)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Array)
        self.assertEqual(len(decoded.value.value), 3)
        self.assertEqual(decoded.value.value[0].value.value, 1)
        self.assertEqual(decoded.value.value[1].value.value, 2)
        self.assertEqual(decoded.value.value[2].value.value, 3)


class TestDataStructure(unittest.TestCase):
    """Test Data structure [2] (SEQUENCE OF Data)"""

    def test_encode_decode_empty(self) -> None:
        """Test structure empty encoding/decoding"""
        original = Data(Structure.from_data())
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Structure)
        self.assertEqual(len(decoded.value.components), 0)

    def test_encode_decode_with_elements(self) -> None:
        """Test structure with elements encoding/decoding"""
        original = Data(Structure.from_data(
            Data(Integer(100)),
            Data(Boolean(1)),
            Data(OctetString(b"test"))))
        buf = ByteBuffer.allocate(50)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Structure)
        self.assertEqual(len(decoded.value.components), 3)


class TestDataCompactArray(unittest.TestCase):
    """Test Data compact-array [19]"""

    def test_encode_decode(self) -> None:
        """Test compact-array encoding/decoding"""
        # compact-array: SEQUENCE { contents-description TypeDescription, array-contents OCTET STRING }
        original = Data(CompactArray(
            contents_description=ContentsDescription(TypeDescriptionInteger(None)),
            array_contents=ArrayContents(b"\x00\x01\x02\x03")
        ))
        z = original.value.get_array()
        y = CompactArray.from_array(z)
        self.assertEqual(y, original.value)
        buf = ByteBuffer.allocate(50)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, CompactArray)
        self.assertIsInstance(decoded.value.contents_description.value, TypeDescriptionInteger)
        self.assertEqual(decoded.value.array_contents.value, b"\x00\x01\x02\x03")


class TestDataDontCare(unittest.TestCase):
    """Test Data dont-care [255]"""

    def test_encode_decode(self) -> None:
        """Test dont-care encoding/decoding"""
        original = Data(DontCare(None))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, DontCare)


class TestDataBcd(unittest.TestCase):
    """Test Data bcd [13] (Integer8)"""

    def test_encode_decode(self) -> None:
        """Test bcd encoding/decoding"""
        original = Data(Bcd(99))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Bcd)
        self.assertEqual(decoded.value.value, 99)


class TestDataChoiceInvalidTag(unittest.TestCase):
    """Test Data CHOICE with invalid tag"""

    def test_invalid_tag(self) -> None:
        """Test invalid tag raises ValueError"""
        buf = ByteBuffer.wrap(b"\xFF\x00")  # Tag 255 (not in alternatives except dont-care)
        Data.get(buf)
        self.assertEqual(buf.get_pos(), 1)


class TestDataConvenienceConstructors(unittest.TestCase):
    """Test Data convenience constructors"""

    def test_null_data_constructor(self) -> None:
        """Test null_data() constructor"""
        data = Data(NullData())
        self.assertIsInstance(data.value, NullData)

    def test_boolean_constructor(self) -> None:
        """Test boolean() constructor"""
        data = Data(Boolean(1))
        self.assertIsInstance(data.value, Boolean)
        self.assertTrue(data.value.value)

    def test_integer_constructor(self) -> None:
        """Test integer() constructor"""
        data = Data(Integer(42))
        self.assertIsInstance(data.value, Integer)
        self.assertEqual(data.value.value, 42)

    def test_unsigned_constructor(self) -> None:
        """Test unsigned() constructor"""
        data = Data(Unsigned(255))
        self.assertIsInstance(data.value, Unsigned)
        self.assertEqual(data.value.value, 255)

    def test_octet_string_constructor(self) -> None:
        """Test octet_string() constructor"""
        data = Data(OctetString(b"\xDE\xAD\xBE\xEF"))
        self.assertIsInstance(data.value, OctetString)
        self.assertEqual(data.value.value, b"\xDE\xAD\xBE\xEF")

    def test_visible_string_constructor(self) -> None:
        """Test visible_string() constructor"""
        data = Data(VisibleString(b"Hello"))
        self.assertIsInstance(data.value, VisibleString)
        self.assertEqual(data.value.value, b"Hello")

    def test_array_constructor(self) -> None:
        """Test array() constructor"""
        elements = [Data(Integer(1)), Data(Integer(2))]
        data = Data(Array(elements))
        self.assertIsInstance(data.value, Array)
        self.assertEqual(len(data.value.value), 2)

    def test_structure_constructor(self) -> None:
        """Test structure() constructor"""
        data = Data(Structure.from_data(Data(Integer(1)), Data(Boolean(1))))
        self.assertIsInstance(data.value, Structure)
        self.assertEqual(len(data.value.components), 2)

    def test_float32_constructor(self) -> None:
        """Test float32() constructor"""
        data = Data(Float32.from_float(4.0))
        self.assertIsInstance(data.value, Float32)
        self.assertEqual(len(data.value.value), 4)

    def test_float64_constructor(self) -> None:
        """Test float64() constructor"""
        data = Data(Float64.from_float(8.0))
        self.assertIsInstance(data.value, Float64)
        self.assertEqual(len(data.value.value), 8)

    def test_date_time_constructor(self) -> None:
        """Test date_time() constructor"""
        data = Data(DateTime(OctetStringType(b"\x07\xE4\x01\x01\x0C\x00\x00\x00\xFF\x88\x00\x00")))
        self.assertIsInstance(data.value, DateTime)
        self.assertEqual(len(data.value.value.value), 12)

    def test_date_constructor(self) -> None:
        """Test date() constructor"""
        data = Data(Date(OctetStringType(b"\x07\xE4\x01\x01\xFF")))
        self.assertIsInstance(data.value, Date)
        self.assertEqual(len(data.value.value.value), 5)

    def test_time_constructor(self) -> None:
        """Test time() constructor"""
        data = Data(Time(OctetStringType(b"\x0C\x00\x00\x00")))
        self.assertIsInstance(data.value, Time)
        self.assertEqual(len(data.value.value.value), 4)

    def test_dont_care_constructor(self) -> None:
        """Test dont_care() constructor"""
        data = Data(DontCare())
        self.assertIsInstance(data.value, DontCare)


class TestDataRoundTrip(unittest.TestCase):
    """Test Data round-trip encoding/decoding"""

    def test_round_trip_all_types(self) -> None:
        """Test round-trip for all Data types"""
        test_cases = [
            ("null-data", Data(NullData())),
            ("boolean-true", Data(Boolean(1))),
            ("boolean-false", Data(Boolean(0))),
            ("integer", Data(Integer(-128))),
            ("unsigned", Data(Unsigned(255))),
            ("long", Data(Long(32767))),
            ("long-unsigned", Data(LongUnsigned(65535))),
            ("double-long", Data(DoubleLong(2147483647))),
            ("double-long-unsigned", Data(DoubleLongUnsigned(4294967295))),
            ("enum", Data(Enum(42))),
            ("bcd", Data(Bcd(99))),
            ("octet-string", Data(OctetString(b"\xDE\xAD\xBE\xEF"))),
            ("visible-string", Data(VisibleString("Hello"))),
            ("bit-string", Data(BitString((1, 0, 1, 1, 0, 0, 1, 0)))),
            ("float32", Data(Float32.from_float(0.342))),
            ("float64", Data(Float64.from_float(234.3123))),
            ("date", Data(Date(b"\x07\xE4\x01\x01\xFF"))),
            ("time", Data(Time(b"\x0C\x00\x00\x00"))),
            ("date-time", Data(DateTime(b"\x07\xE4\x01\x01\x0C\x00\x00\x00\xFF\x88\x00\x00"))),
            ("dont-care", Data(DontCare())),
        ]

        for name, original in test_cases:
            with self.subTest(name=name):
                buf = ByteBuffer.allocate(100)
                original.put(buf)
                buf.set_pos(0)
                decoded = Data.get(buf)
                self.assertEqual(decoded.value, original.value)


class TestTypeDescriptionRoundTrip(unittest.TestCase):
    """Test TypeDescription round-trip encoding/decoding"""

    def test_round_trip_all_types(self) -> None:
        """Test round-trip for all TypeDescription types"""
        test_cases = [
            (NullData, TypeDescription(NullData(None))),
            (TypeDescriptionBoolean, TypeDescription(TypeDescriptionBoolean(None))),
            (TypeDescriptionInteger, TypeDescription(TypeDescriptionInteger(None))),
            (TypeDescriptionUnsigned, TypeDescription(TypeDescriptionUnsigned(None))),
            (TypeDescriptionLong, TypeDescription(TypeDescriptionLong(None))),
            (TypeDescriptionLongUnsigned, TypeDescription(TypeDescriptionLongUnsigned(None))),
            (TypeDescriptionOctetString, TypeDescription(TypeDescriptionOctetString(None))),
            (TypeDescriptionVisibleString, TypeDescription(TypeDescriptionVisibleString(None))),
            (TypeDescriptionEnum, TypeDescription(TypeDescriptionEnum(None))),
            (TypeDescriptionFloat32, TypeDescription(TypeDescriptionFloat32(None))),
            (TypeDescriptionFloat64, TypeDescription(TypeDescriptionFloat64(None))),
            (TypeDescriptionDateTime, TypeDescription(TypeDescriptionDateTime(None))),
            (TypeDescriptionDate, TypeDescription(TypeDescriptionDate(None))),
            (TypeDescriptionTime, TypeDescription(TypeDescriptionTime(None))),
            (TypeDescriptionDontCare, TypeDescription(TypeDescriptionDontCare(None))),
        ]

        for expected_class, original in test_cases:
            with self.subTest(expected_class=expected_class.__name__):
                buf = ByteBuffer.allocate(100)
                original.put(buf)
                buf.set_pos(0)
                decoded = TypeDescription.get(buf)
                self.assertIsInstance(decoded.value, expected_class)


class TestDataNestedStructures(unittest.TestCase):
    """Test Data with nested structures"""

    def test_nested_array(self) -> None:
        """Test nested array encoding/decoding"""
        inner_array = Data(Array([Data(Integer(1)), Data(Unsigned(2))]))
        outer_array = Data(Array([inner_array, Data(Integer(3))]))
        buf = ByteBuffer.allocate(100)
        outer_array.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Array)
        self.assertEqual(len(decoded.value.value), 2)

    def test_nested_structure(self) -> None:
        """Test nested structure encoding/decoding"""
        inner_struct = Data(Structure.from_data(Data(Integer(10)), Data(Boolean(1))))
        outer_struct = Data(Structure.from_data(inner_struct, Data(OctetString(b"test"))))
        buf = ByteBuffer.allocate(100)
        outer_struct.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Structure)
        self.assertEqual(len(decoded.value.components), 2)

    def test_mixed_nested(self) -> None:
        """Test mixed nested array and structure"""
        mixed = Data(Structure.from_data(
            Data(Array([Data(Integer(1)), Data(Integer(2))])),
            Data(Structure.from_data(Data(Boolean(1)), Data(OctetString(b"data")))),
        ))
        buf = ByteBuffer.allocate(100)
        mixed.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Structure)
        self.assertEqual(len(decoded.value.components), 2)


class TestDataEdgeCases(unittest.TestCase):
    """Test Data edge cases"""

    def test_buffer_overflow(self) -> None:
        """Test buffer overflow protection"""
        data = Data(Structure.from_data(*(Data(Integer(i)) for i in range(10))))
        buf = ByteBuffer.allocate(1)  # Too small
        self.assertTrue(data.put(buf).has(exception_type=BufferError))

    def test_empty_structure(self) -> None:
        """Test empty structure encoding/decoding"""
        data = Data(Structure.from_data())
        buf = ByteBuffer.allocate(10)
        data.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Structure)
        self.assertEqual(len(decoded.value.components), 0)

    def test_empty_array(self) -> None:
        """Test empty array encoding/decoding"""
        data = Data(Array([]))
        buf = ByteBuffer.allocate(10)
        data.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertIsInstance(decoded.value, Array)
        self.assertEqual(len(decoded.value.value), 0)

    def test_maximum_integer_values(self) -> None:
        """Test maximum integer values"""
        test_cases = [
            (Integer, -128, 127),
            (Unsigned, 0, 255),
            (Long, -32768, 32767),
            (LongUnsigned, 0, 65535),
            (DoubleLong, -2147483648, 2147483647),
            (DoubleLongUnsigned, 0, 4294967295),
        ]

        for constructor, min_val, max_val in test_cases:
            with self.subTest(constructor=constructor.__name__):
                # Test minimum
                data_min = Data(constructor(min_val))
                buf = ByteBuffer.allocate(20)
                data_min.put(buf)
                buf.set_pos(0)
                decoded_min = Data.get(buf)
                self.assertEqual(decoded_min.value.value, min_val)

                # Test maximum
                data_max = Data(constructor(max_val))
                buf = ByteBuffer.allocate(20)
                data_max.put(buf)
                buf.set_pos(0)
                decoded_max = Data.get(buf)
                self.assertEqual(decoded_max.value.value, max_val)


class TestDataRepr(unittest.TestCase):
    """Test Data __repr__ method"""

    def test_repr(self) -> None:
        """Test __repr__ returns meaningful string"""
        data = Data(Integer(42))
        repr_str = repr(data)
        self.assertIn("Data", repr_str)
        self.assertIn("Integer", repr_str)


class TestDataOctetImplicit(unittest.TestCase):
    def test_octetObj(self) -> None:
        class OctetStringObjectIdentifierType(axdr.ImplicitTaggedType, axdr.ObjectIdentifierType):
            tag = 9

        class IdentifierData(axdr.ChoiceType):
            value: OctetStringObjectIdentifierType | Unsigned

        buf = ByteBuffer.allocate(20)
        iddata = IdentifierData(OctetStringObjectIdentifierType((2, 16, 0x2f4, 5, 8, 1, 1)))
        iddata.put(buf)
        buf.set_pos(0)
        self.assertEqual(IdentifierData.get(buf), iddata)


# ==============================================================================
# Test Fixtures (Concrete implementations for testing)
# ==============================================================================


class TestSelector(Enum):
    """Concrete selector enum inheriting DLMS Enum behavior"""
    NULL_DATA: Final = 0
    BOOLEAN: Final = 3


class TestExternallyData(ExternallyData):
    """Controlled subset of alternatives to simplify testing"""
    value: NullData | Boolean


@dataclass
class TestDiscriminatedUnion(DiscriminatedUnion):
    """Concrete DiscriminatedUnion using the test fixtures above"""
    selector: TestSelector
    payload: TestExternallyData


# ==============================================================================
# Tests
# ==============================================================================

class TestExternallyData_(unittest.TestCase):
    """Tests for ExternallyData[T]"""

    def test_get_always_returns_error(self) -> None:
        buf = ByteBuffer.allocate(10)
        result = TestExternallyData.get(buf)

        self.assertIsInstance(result, Error)
        self.assertIn("can't get TestExternallyData separately", str(result.err.exceptions))

    def test_selected_property_returns_correct_identifier(self) -> None:
        """selected property should dynamically match the wrapped type's tag."""
        # Test with NullData (tag 0)
        obj_null = TestExternallyData(NullData())
        self.assertIsInstance(obj_null.value, NullData)

        # Test with Boolean (tag 3)
        obj_bool = TestExternallyData(Boolean(1))
        self.assertIsInstance(obj_bool.value, Boolean)


class TestDiscriminatedUnion_(unittest.TestCase):
    """Tests for DiscriminatedUnion (Structure wrapper)"""

    def test_subclass_auto_generates_components(self) -> None:
        """__init_subclass__ must create components tuple from annotations."""
        self.assertEqual(len(TestDiscriminatedUnion.components), 2)

        comp_selector, comp_payload = TestDiscriminatedUnion.components
        self.assertEqual(comp_selector.identifier, "selector")
        self.assertEqual(comp_payload.identifier, "payload")
        self.assertIs(comp_selector.type_, TestSelector)
        self.assertIs(comp_payload.type_, TestExternallyData)

    def test_get_lc_rejects_invalid_length(self) -> None:
        """A-XDR requires exactly 2 components for this pattern."""
        # Simulate a buffer where A-XDR length != 2
        buf = ByteBuffer.wrap(b"\x05\x00\x00\x00\x00\x00")
        result = TestDiscriminatedUnion.get_lc(buf)

        self.assertIsInstance(result, Error)
        self.assertIn("Invalid length", str(result.err.exceptions))

    def test_get_lc_rejects_unknown_selector(self) -> None:
        """Parser must fail if selector tag is not in payload.alternatives."""
        # Length=2, Selector tag=95 (not in alternatives), dummy payload byte
        buf = ByteBuffer.wrap(b"\x02\x5F\x00")
        result = TestDiscriminatedUnion.get_lc(buf)

        self.assertIsInstance(result, Error)
        self.assertIn("expected", str(result.err.exceptions))

    def test_roundtrip_null_data(self) -> None:
        """Full encode -> decode cycle for selector=0 (null-data)."""
        original = TestDiscriminatedUnion(
            TestSelector(0),
            TestExternallyData(NullData())
        )

        buf = ByteBuffer.allocate(20)
        original.put(buf)
        buf.set_pos(0)

        decoded = TestDiscriminatedUnion.get(buf)
        self.assertFalse(isinstance(decoded, Error))
        self.assertEqual(decoded, original)

    def test_roundtrip_boolean(self) -> None:
        """Full encode -> decode cycle for selector=3 (boolean)."""
        original = TestDiscriminatedUnion(
            TestSelector(3),
            TestExternallyData(Boolean(0))
        )

        buf = ByteBuffer.allocate(20)
        original.put(buf)
        buf.set_pos(0)

        decoded = TestDiscriminatedUnion.get(buf)
        self.assertFalse(isinstance(decoded, Error))
        self.assertEqual(decoded.selector.value, 3)
        self.assertIsInstance(decoded.payload.value, Boolean)
        self.assertFalse(decoded.payload.value.value)


if __name__ == "__main__":
    unittest.main()
