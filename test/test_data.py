"""
Unit tests for Data and TypeDescription encoding/decoding (A-XDR)

Standards:
    - COSEMpdu_GB83.txt: Data and TypeDescription definition
    - IEC 61334-6 §6.6: CHOICE encoding (A-XDR)
    - IEC 61334-6 §6.4-6.5: BIT STRING, OCTET STRING encoding
"""

import unittest
from src.COSEMpdu.byte_buffer import ByteBuffer
from src.COSEMpdu.data import (
    # TypeDescription types
    SequenceOfData,
    TypeDescription,
    TypeDescriptionNullData,
    TypeDescriptionArray,
    TypeDescriptionArrayContent,
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
    CompactArrayContent,
    ContentsDescription,
    ArrayContents,
    Long64,
    Long64Unsigned,
    Enum,
    Float32,
    Float64,
    DateTime,
    Date,
    Time,
    DontCare
)
from src.COSEMpdu.useful_types import (
    Integer8, Integer16, Integer32, Integer64,
    Unsigned8, Unsigned16, Unsigned32, Unsigned64
)
from src.COSEMpdu import axdr
from src.COSEMpdu.axdr import IntegerType


class TestTypeDescriptionNullData(unittest.TestCase):
    """Test TypeDescription null-data [0]"""

    def test_encode_decode(self) -> None:
        """Test null-data encoding/decoding"""
        original = TypeDescription(TypeDescriptionNullData(axdr.NullType(None)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertEqual(decoded.selected, "null-data")
        self.assertIsInstance(decoded.value, TypeDescriptionNullData)

    def test_tag_number(self) -> None:
        """Test tag number is 0"""
        self.assertEqual(TypeDescriptionNullData.tag, 0)


class TestTypeDescriptionArray(unittest.TestCase):
    """Test TypeDescription array [1]"""

    def test_encode_decode(self) -> None:
        """Test array encoding/decoding"""
        # array: SEQUENCE { number-of-elements Unsigned16, type-description TypeDescription }
        content = TypeDescriptionArrayContent((
            Unsigned16(axdr.IntegerType(5)),
            TypeDescription(TypeDescriptionInteger(axdr.NullType(None)))
        ))
        original = TypeDescription(TypeDescriptionArray(content))
        buf = ByteBuffer.allocate(50)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertEqual(decoded.selected, "array")
        self.assertEqual(decoded.value.value[0].value.value, 5)


class TestTypeDescriptionStructure(unittest.TestCase):
    """Test TypeDescription structure [2]"""

    def test_encode_decode(self) -> None:
        """Test structure encoding/decoding"""
        # structure: SEQUENCE OF TypeDescription
        elements = SequenceOfData([
            TypeDescription(TypeDescriptionInteger(axdr.NullType(None))),
            TypeDescription(TypeDescriptionBoolean(axdr.NullType(None))),
        ])
        original = TypeDescription(TypeDescriptionStructure(elements))
        buf = ByteBuffer.allocate(50)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertEqual(decoded.selected, "structure")
        self.assertEqual(len(decoded.value.value), 2)


class TestTypeDescriptionBoolean(unittest.TestCase):
    """Test TypeDescription boolean [3]"""

    def test_encode_decode(self) -> None:
        """Test boolean encoding/decoding"""
        original = TypeDescription(TypeDescriptionBoolean(axdr.NullType(None)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertEqual(decoded.selected, "boolean")


class TestTypeDescriptionOctetString(unittest.TestCase):
    """Test TypeDescription octet-string [9]"""

    def test_encode_decode(self) -> None:
        """Test octet-string encoding/decoding"""
        original = TypeDescription(TypeDescriptionOctetString(axdr.NullType(None)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertEqual(decoded.selected, "octet-string")


class TestTypeDescriptionInteger(unittest.TestCase):
    """Test TypeDescription integer [15]"""

    def test_encode_decode(self) -> None:
        """Test integer encoding/decoding"""
        original = TypeDescription(TypeDescriptionInteger(axdr.NullType(None)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertEqual(decoded.selected, "integer")


class TestTypeDescriptionUnsigned(unittest.TestCase):
    """Test TypeDescription unsigned [17]"""

    def test_encode_decode(self) -> None:
        """Test unsigned encoding/decoding"""
        original = TypeDescription(TypeDescriptionUnsigned(axdr.NullType(None)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertEqual(decoded.selected, "unsigned")


class TestTypeDescriptionFloat32(unittest.TestCase):
    """Test TypeDescription float32 [23]"""

    def test_encode_decode(self) -> None:
        """Test float32 encoding/decoding"""
        original = TypeDescription(TypeDescriptionFloat32(axdr.NullType(None)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertEqual(decoded.selected, "float32")


class TestTypeDescriptionDateTime(unittest.TestCase):
    """Test TypeDescription date-time [25]"""

    def test_encode_decode(self) -> None:
        """Test date-time encoding/decoding"""
        original = TypeDescription(TypeDescriptionDateTime(axdr.NullType(None)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertEqual(decoded.selected, "date-time")


class TestTypeDescriptionDontCare(unittest.TestCase):
    """Test TypeDescription dont-care [255]"""

    def test_encode_decode(self) -> None:
        """Test dont-care encoding/decoding"""
        original = TypeDescription(TypeDescriptionDontCare(axdr.NullType(None)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = TypeDescription.get(buf)
        self.assertEqual(decoded.selected, "dont-care")
        self.assertEqual(TypeDescriptionDontCare.tag, 255)


class TestDataNullData(unittest.TestCase):
    """Test Data null-data [0]"""

    def test_encode_decode(self) -> None:
        """Test null-data encoding/decoding"""
        original = Data(NullData(axdr.NullType(None)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "null-data")
        self.assertIsInstance(decoded.value, NullData)

    def test_tag_number(self) -> None:
        """Test tag number is 0"""
        self.assertEqual(NullData.tag, 0)


class TestDataBoolean(unittest.TestCase):
    """Test Data boolean [3]"""

    def test_encode_decode_true(self) -> None:
        """Test boolean TRUE encoding/decoding"""
        original = Data(Boolean(axdr.BooleanType(True)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "boolean")
        self.assertTrue(decoded.value.value.value)

    def test_encode_decode_false(self) -> None:
        """Test boolean FALSE encoding/decoding"""
        original = Data(Boolean(axdr.BooleanType(False)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "boolean")
        self.assertFalse(decoded.value.value.value)


class TestDataInteger(unittest.TestCase):
    """Test Data integer [15] (Integer8)"""

    def test_encode_decode_positive(self) -> None:
        """Test integer positive value encoding/decoding"""
        original = Data(Integer(Integer8(IntegerType(127))))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "integer")
        self.assertEqual(decoded.value.value.value.value, 127)

    def test_encode_decode_negative(self) -> None:
        """Test integer negative value encoding/decoding"""
        original = Data(Integer(Integer8(IntegerType(-128))))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "integer")
        self.assertEqual(decoded.value.value.value.value, -128)

    def test_encode_decode_zero(self) -> None:
        """Test integer zero value encoding/decoding"""
        original = Data(Integer(Integer8(IntegerType(0))))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "integer")
        self.assertEqual(decoded.value.value.value.value, 0)


class TestDataUnsigned(unittest.TestCase):
    """Test Data unsigned [17] (Unsigned8)"""

    def test_encode_decode(self) -> None:
        """Test unsigned encoding/decoding"""
        original = Data(Unsigned(Unsigned8(IntegerType(255))))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "unsigned")
        self.assertEqual(decoded.value.value.value.value, 255)


class TestDataLong(unittest.TestCase):
    """Test Data long [16] (Integer16)"""

    def test_encode_decode(self) -> None:
        """Test long encoding/decoding"""
        original = Data(Long(Integer16(IntegerType(32767))))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "long")
        self.assertEqual(decoded.value.value.value.value, 32767)


class TestDataLongUnsigned(unittest.TestCase):
    """Test Data long-unsigned [18] (Unsigned16)"""

    def test_encode_decode(self) -> None:
        """Test long-unsigned encoding/decoding"""
        original = Data(LongUnsigned(Unsigned16(IntegerType(65535))))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "long-unsigned")
        self.assertEqual(decoded.value.value.value.value, 65535)


class TestDataDoubleLong(unittest.TestCase):
    """Test Data double-long [5] (Integer32)"""

    def test_encode_decode(self) -> None:
        """Test double-long encoding/decoding"""
        original = Data(DoubleLong(Integer32(axdr.IntegerType(2147483647))))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "double-long")
        self.assertEqual(decoded.value.value.value.value, 2147483647)


class TestDataDoubleLongUnsigned(unittest.TestCase):
    """Test Data double-long-unsigned [6] (Unsigned32)"""

    def test_encode_decode(self) -> None:
        """Test double-long-unsigned encoding/decoding"""
        original = Data(DoubleLongUnsigned(Unsigned32(axdr.IntegerType(4294967295))))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "double-long-unsigned")
        self.assertEqual(decoded.value.value.value.value, 4294967295)


class TestDataLong64(unittest.TestCase):
    """Test Data long64 [20] (Integer64)"""

    def test_encode_decode(self) -> None:
        """Test long64 encoding/decoding"""
        original = Data(Long64(Integer64(axdr.IntegerType(9223372036854775807))))
        buf = ByteBuffer.allocate(20)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "long64")
        self.assertEqual(decoded.value.value.value.value, 9223372036854775807)


class TestDataLong64Unsigned(unittest.TestCase):
    """Test Data long64-unsigned [21] (Unsigned64)"""

    def test_encode_decode(self) -> None:
        """Test long64-unsigned encoding/decoding"""
        original = Data(Long64Unsigned(Unsigned64(axdr.IntegerType(18446744073709551615))))
        buf = ByteBuffer.allocate(20)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "long64-unsigned")
        self.assertEqual(decoded.value.value.value.value, 18446744073709551615)


class TestDataOctetString(unittest.TestCase):
    """Test Data octet-string [9]"""

    def test_encode_decode_empty(self) -> None:
        """Test octet-string empty encoding/decoding"""
        original = Data(OctetString(axdr.OctetStringType(b"")))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "octet-string")
        self.assertEqual(decoded.value.value.value, b"")

    def test_encode_decode_data(self) -> None:
        """Test octet-string with data encoding/decoding"""
        original = Data(OctetString(axdr.OctetStringType(b"\x00\x01\x02\x03")))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "octet-string")
        self.assertEqual(decoded.value.value.value, b"\x00\x01\x02\x03")


class TestDataVisibleString(unittest.TestCase):
    """Test Data visible-string [10]"""

    def test_encode_decode(self) -> None:
        """Test visible-string encoding/decoding"""
        original = Data(VisibleString(axdr.VisibleString("Hello")))
        buf = ByteBuffer.allocate(20)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "visible-string")
        self.assertEqual(decoded.value.value.value, "Hello")


class TestDataUtf8String(unittest.TestCase):
    """Test Data utf8-string [12]"""

    def test_encode_decode(self) -> None:
        """Test utf8-string encoding/decoding"""
        original = Data(Utf8String(axdr.Utf8String("Привет")))
        buf = ByteBuffer.allocate(20)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "utf8-string")
        self.assertEqual(decoded.value.value.value, "Привет")


class TestDataBitString(unittest.TestCase):
    """Test Data bit-string [4]"""

    def test_encode_decode(self) -> None:
        """Test bit-string encoding/decoding"""
        bits = (1, 0, 1, 1, 0, 0, 1)
        original = Data(BitString(axdr.BitStringType(bits)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "bit-string")
        self.assertEqual(decoded.value.value.value, bits)


class TestDataEnum(unittest.TestCase):
    """Test Data enum [22] (Unsigned8)"""

    def test_encode_decode(self) -> None:
        """Test enum encoding/decoding"""
        original = Data(Enum(Unsigned8(IntegerType(42))))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "enum")
        self.assertEqual(decoded.value.value.value.value, 42)


class TestDataFloat32(unittest.TestCase):
    """Test Data float32 [23] (OCTET STRING SIZE(4))"""

    def test_encode_decode_valid(self) -> None:
        """Test float32 valid 4-byte encoding/decoding"""
        original = Data(Float32(axdr.OctetStringType(b"\x40\x49\x0F\xDB")))  # π approx
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "float32")
        self.assertEqual(len(decoded.value.value.value), 4)

    def test_encode_decode_invalid_length(self) -> None:
        """Test float32 invalid length raises error"""
        with self.assertRaises(ValueError):
            Data.float32(b"\x00\x01\x02")  # Only 3 bytes


class TestDataFloat64(unittest.TestCase):
    """Test Data float64 [24] (OCTET STRING SIZE(8))"""

    def test_encode_decode_valid(self) -> None:
        """Test float64 valid 8-byte encoding/decoding"""
        original = Data(Float64(axdr.OctetStringType(b"\x40\x09\x21\xFB\x54\x44\x2D\x18")))
        buf = ByteBuffer.allocate(20)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "float64")
        self.assertEqual(len(decoded.value.value.value), 8)

    def test_encode_decode_invalid_length(self) -> None:
        """Test float64 invalid length raises error"""
        with self.assertRaises(ValueError):
            Data.float64(b"\x00\x01\x02\x03\x04\x05\x06")  # Only 7 bytes


class TestDataDateTime(unittest.TestCase):
    """Test Data date-time [25] (OCTET STRING SIZE(12))"""

    def test_encode_decode_valid(self) -> None:
        """Test date-time valid 12-byte encoding/decoding"""
        # DLMS date-time format: 12 bytes
        dt_bytes = b"\x07\xE4\x01\x01\x0C\x00\x00\x00\xFF\x88\x00\x00"
        original = Data(DateTime(axdr.OctetStringType(dt_bytes)))
        buf = ByteBuffer.allocate(20)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "date-time")
        self.assertEqual(len(decoded.value.value.value), 12)

    def test_encode_decode_invalid_length(self) -> None:
        """Test date-time invalid length raises error"""
        with self.assertRaises(ValueError):
            Data.date_time(b"\x00" * 11)  # Only 11 bytes


class TestDataDate(unittest.TestCase):
    """Test Data date [26] (OCTET STRING SIZE(5))"""

    def test_encode_decode_valid(self) -> None:
        """Test date valid 5-byte encoding/decoding"""
        # DLMS date format: 5 bytes
        date_bytes = b"\x07\xE4\x01\x01\xFF"
        original = Data(Date(axdr.OctetStringType(date_bytes)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "date")
        self.assertEqual(len(decoded.value.value.value), 5)

    def test_encode_decode_invalid_length(self) -> None:
        """Test date invalid length raises error"""
        with self.assertRaises(ValueError):
            Data.date(b"\x00" * 4)  # Only 4 bytes


class TestDataTime(unittest.TestCase):
    """Test Data time [27] (OCTET STRING SIZE(4))"""

    def test_encode_decode_valid(self) -> None:
        """Test time valid 4-byte encoding/decoding"""
        # DLMS time format: 4 bytes
        time_bytes = b"\x0C\x00\x00\x00"
        original = Data.time(time_bytes)
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "time")
        self.assertEqual(len(decoded.value.value.value), 4)

    def test_encode_decode_invalid_length(self) -> None:
        """Test time invalid length raises error"""
        with self.assertRaises(ValueError):
            Data.time(b"\x00" * 3)  # Only 3 bytes


class TestDataArray(unittest.TestCase):
    """Test Data array [1] (SEQUENCE OF Data)"""

    def test_encode_decode_empty(self) -> None:
        """Test array empty encoding/decoding"""
        original = Data.array([])
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "array")
        self.assertEqual(len(decoded.value.value), 0)

    def test_encode_decode_with_elements(self) -> None:
        """Test array with elements encoding/decoding"""
        elements = SequenceOfData([
            Data(Integer(Integer8(axdr.IntegerType(1)))),
            Data(Integer(Integer8(axdr.IntegerType(2)))),
            Data(Integer(Integer8(axdr.IntegerType(3)))),
        ])
        original = Data(Array(elements))
        buf = ByteBuffer.allocate(50)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "array")
        self.assertEqual(len(decoded.value.value), 3)
        self.assertEqual(decoded.value.value[0].value.value, Integer8(axdr.IntegerType(1)))
        self.assertEqual(decoded.value.value[1].value.value, Integer8(axdr.IntegerType(2)))
        self.assertEqual(decoded.value.value[2].value.value, Integer8(axdr.IntegerType(3)))


class TestDataStructure(unittest.TestCase):
    """Test Data structure [2] (SEQUENCE OF Data)"""

    def test_encode_decode_empty(self) -> None:
        """Test structure empty encoding/decoding"""
        original = Data(Structure(SequenceOfData([])))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "structure")
        self.assertEqual(len(decoded.value.value), 0)

    def test_encode_decode_with_elements(self) -> None:
        """Test structure with elements encoding/decoding"""
        elements = SequenceOfData([
            Data(Integer(Integer8(IntegerType(100)))),
            Data(Boolean(axdr.BooleanType(True))),
            Data(OctetString(axdr.OctetStringType(b"test"))),
        ])
        original = Data(Structure(elements))
        buf = ByteBuffer.allocate(50)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "structure")
        self.assertEqual(len(decoded.value.value), 3)


class TestDataCompactArray(unittest.TestCase):
    """Test Data compact-array [19]"""

    def test_encode_decode(self) -> None:
        """Test compact-array encoding/decoding"""
        # compact-array: SEQUENCE { contents-description TypeDescription, array-contents OCTET STRING }
        content = CompactArrayContent((
            ContentsDescription(TypeDescription(TypeDescriptionInteger(axdr.null))),
            ArrayContents(axdr.OctetStringType(b"\x00\x01\x02\x03"))
        ))
        x = content.get_array()
        z = CompactArrayContent.from_array(ContentsDescription(TypeDescription.null_data()), x)
        original = Data(CompactArray(content))
        buf = ByteBuffer.allocate(50)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "compact-array")
        self.assertEqual(decoded.value.value[0].value.selected, "integer")
        self.assertEqual(decoded.value.value[1].value.value, b"\x00\x01\x02\x03")


class TestDataDontCare(unittest.TestCase):
    """Test Data dont-care [255]"""

    def test_encode_decode(self) -> None:
        """Test dont-care encoding/decoding"""
        original = Data(DontCare(axdr.NullType(None)))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "dont-care")
        self.assertEqual(DontCare.tag, 255)


class TestDataBcd(unittest.TestCase):
    """Test Data bcd [13] (Integer8)"""

    def test_encode_decode(self) -> None:
        """Test bcd encoding/decoding"""
        original = Data(Bcd(Integer8(axdr.IntegerType(99))))
        buf = ByteBuffer.allocate(10)
        original.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "bcd")
        self.assertEqual(decoded.value.value.value.value, 99)


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
        data = Data.null_data()
        self.assertEqual(data.selected, "null-data")

    def test_boolean_constructor(self) -> None:
        """Test boolean() constructor"""
        data = Data.boolean(True)
        self.assertEqual(data.selected, "boolean")
        self.assertTrue(data.value.value.value)

    def test_integer_constructor(self) -> None:
        """Test integer() constructor"""
        data = Data.integer(42)
        self.assertEqual(data.selected, "integer")
        self.assertEqual(data.value.value.value.value, 42)

    def test_unsigned_constructor(self) -> None:
        """Test unsigned() constructor"""
        data = Data.unsigned(255)
        self.assertEqual(data.selected, "unsigned")
        self.assertEqual(data.value.value.value.value, 255)

    def test_octet_string_constructor(self) -> None:
        """Test octet_string() constructor"""
        data = Data.octet_string(b"\xDE\xAD\xBE\xEF")
        self.assertEqual(data.selected, "octet-string")
        self.assertEqual(data.value.value.value, b"\xDE\xAD\xBE\xEF")

    def test_visible_string_constructor(self) -> None:
        """Test visible_string() constructor"""
        data = Data.visible_string(b"Hello")
        self.assertEqual(data.selected, "visible-string")
        self.assertEqual(data.value.value.value, b"Hello")

    def test_array_constructor(self) -> None:
        """Test array() constructor"""
        elements = [Data.integer(1), Data.integer(2)]
        data = Data.array(elements)
        self.assertEqual(data.selected, "array")
        self.assertEqual(len(data.value.value), 2)

    def test_structure_constructor(self) -> None:
        """Test structure() constructor"""
        elements = [Data.integer(1), Data.boolean(True)]
        data = Data.structure(elements)
        self.assertEqual(data.selected, "structure")
        self.assertEqual(len(data.value.value), 2)

    def test_float32_constructor(self) -> None:
        """Test float32() constructor"""
        data = Data.float32(b"\x40\x49\x0F\xDB")
        self.assertEqual(data.selected, "float32")
        self.assertEqual(len(data.value.value.value), 4)

    def test_float64_constructor(self) -> None:
        """Test float64() constructor"""
        data = Data.float64(b"\x40\x09\x21\xFB\x54\x44\x2D\x18")
        self.assertEqual(data.selected, "float64")
        self.assertEqual(len(data.value.value.value), 8)

    def test_date_time_constructor(self) -> None:
        """Test date_time() constructor"""
        data = Data.date_time(b"\x07\xE4\x01\x01\x0C\x00\x00\x00\xFF\x88\x00\x00")
        self.assertEqual(data.selected, "date-time")
        self.assertEqual(len(data.value.value.value), 12)

    def test_date_constructor(self) -> None:
        """Test date() constructor"""
        data = Data.date(b"\x07\xE4\x01\x01\xFF")
        self.assertEqual(data.selected, "date")
        self.assertEqual(len(data.value.value.value), 5)

    def test_time_constructor(self) -> None:
        """Test time() constructor"""
        data = Data.time(b"\x0C\x00\x00\x00")
        self.assertEqual(data.selected, "time")
        self.assertEqual(len(data.value.value.value), 4)

    def test_dont_care_constructor(self) -> None:
        """Test dont_care() constructor"""
        data = Data.dont_care()
        self.assertEqual(data.selected, "dont-care")


class TestDataRoundTrip(unittest.TestCase):
    """Test Data round-trip encoding/decoding"""

    def test_round_trip_all_types(self) -> None:
        """Test round-trip for all Data types"""
        test_cases = [
            ("null-data", Data.null_data()),
            ("boolean-true", Data.boolean(True)),
            ("boolean-false", Data.boolean(False)),
            ("integer", Data.integer(-128)),
            ("unsigned", Data.unsigned(255)),
            ("long", Data.long(32767)),
            ("long-unsigned", Data.long_unsigned(65535)),
            ("double-long", Data.double_long(2147483647)),
            ("double-long-unsigned", Data.double_long_unsigned(4294967295)),
            ("enum", Data.enum(42)),
            ("bcd", Data.bcd(99)),
            ("octet-string", Data.octet_string(b"\xDE\xAD\xBE\xEF")),
            ("visible-string", Data.visible_string("Hello")),
            ("bit-string", Data.bit_string((1, 0, 1, 1, 0, 0, 1, 0))),
            ("float32", Data.float32(b"\x40\x49\x0F\xDB")),
            ("float64", Data.float64(b"\x40\x09\x21\xFB\x54\x44\x2D\x18")),
            ("date", Data.date(b"\x07\xE4\x01\x01\xFF")),
            ("time", Data.time(b"\x0C\x00\x00\x00")),
            ("date-time", Data.date_time(b"\x07\xE4\x01\x01\x0C\x00\x00\x00\xFF\x88\x00\x00")),
            ("dont-care", Data.dont_care()),
        ]

        for name, original in test_cases:
            with self.subTest(name=name):
                buf = ByteBuffer.allocate(100)
                original.put(buf)
                buf.set_pos(0)
                decoded = Data.get(buf)
                self.assertEqual(decoded.selected, original.selected)


class TestTypeDescriptionRoundTrip(unittest.TestCase):
    """Test TypeDescription round-trip encoding/decoding"""

    def test_round_trip_all_types(self) -> None:
        """Test round-trip for all TypeDescription types"""
        test_cases = [
            ("null-data", TypeDescription(TypeDescriptionNullData(axdr.NullType(None)))),
            ("boolean", TypeDescription(TypeDescriptionBoolean(axdr.NullType(None)))),
            ("integer", TypeDescription(TypeDescriptionInteger(axdr.NullType(None)))),
            ("unsigned", TypeDescription(TypeDescriptionUnsigned(axdr.NullType(None)))),
            ("long", TypeDescription(TypeDescriptionLong(axdr.NullType(None)))),
            ("long-unsigned", TypeDescription(TypeDescriptionLongUnsigned(axdr.NullType(None)))),
            ("octet-string", TypeDescription(TypeDescriptionOctetString(axdr.NullType(None)))),
            ("visible-string", TypeDescription(TypeDescriptionVisibleString(axdr.NullType(None)))),
            ("enum", TypeDescription(TypeDescriptionEnum(axdr.NullType(None)))),
            ("float32", TypeDescription(TypeDescriptionFloat32(axdr.NullType(None)))),
            ("float64", TypeDescription(TypeDescriptionFloat64(axdr.NullType(None)))),
            ("date-time", TypeDescription(TypeDescriptionDateTime(axdr.NullType(None)))),
            ("date", TypeDescription(TypeDescriptionDate(axdr.NullType(None)))),
            ("time", TypeDescription(TypeDescriptionTime(axdr.NullType(None)))),
            ("dont-care", TypeDescription(TypeDescriptionDontCare(axdr.NullType(None)))),
        ]

        for name, original in test_cases:
            with self.subTest(name=name):
                buf = ByteBuffer.allocate(100)
                original.put(buf)
                buf.set_pos(0)
                decoded = TypeDescription.get(buf)
                self.assertEqual(decoded.selected, original.selected)


class TestDataNestedStructures(unittest.TestCase):
    """Test Data with nested structures"""

    def test_nested_array(self) -> None:
        """Test nested array encoding/decoding"""
        inner_array = Data.array([Data.integer(1), Data.integer(2)])
        outer_array = Data.array([inner_array, Data.integer(3)])
        buf = ByteBuffer.allocate(100)
        outer_array.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "array")
        self.assertEqual(len(decoded.value.value), 2)

    def test_nested_structure(self) -> None:
        """Test nested structure encoding/decoding"""
        inner_struct = Data.structure([Data.integer(10), Data.boolean(True)])
        outer_struct = Data.structure([inner_struct, Data.octet_string(b"test")])
        buf = ByteBuffer.allocate(100)
        outer_struct.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "structure")
        self.assertEqual(len(decoded.value.value), 2)

    def test_mixed_nested(self) -> None:
        """Test mixed nested array and structure"""
        mixed = Data.structure([
            Data.array([Data.integer(1), Data.integer(2)]),
            Data.structure([Data.boolean(True), Data.octet_string(b"data")]),
        ])
        buf = ByteBuffer.allocate(100)
        mixed.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "structure")
        self.assertEqual(len(decoded.value.value), 2)


class TestDataEdgeCases(unittest.TestCase):
    """Test Data edge cases"""

    def test_buffer_overflow(self) -> None:
        """Test buffer overflow protection"""
        data = Data.structure([Data.integer(i) for i in range(100)])
        buf = ByteBuffer.allocate(1)  # Too small
        with self.assertRaises(BufferError):
            data.put(buf)

    def test_empty_structure(self) -> None:
        """Test empty structure encoding/decoding"""
        data = Data.structure([])
        buf = ByteBuffer.allocate(10)
        data.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "structure")
        self.assertEqual(len(decoded.value.value), 0)

    def test_empty_array(self) -> None:
        """Test empty array encoding/decoding"""
        data = Data.array([])
        buf = ByteBuffer.allocate(10)
        data.put(buf)
        buf.set_pos(0)
        decoded = Data.get(buf)
        self.assertEqual(decoded.selected, "array")
        self.assertEqual(len(decoded.value.value), 0)

    def test_maximum_integer_values(self) -> None:
        """Test maximum integer values"""
        test_cases = [
            (Data.integer, -128, 127),
            (Data.unsigned, 0, 255),
            (Data.long, -32768, 32767),
            (Data.long_unsigned, 0, 65535),
            (Data.double_long, -2147483648, 2147483647),
            (Data.double_long_unsigned, 0, 4294967295),
        ]

        for constructor, min_val, max_val in test_cases:
            with self.subTest(constructor=constructor.__name__):
                # Test minimum
                data_min = constructor(min_val)
                buf = ByteBuffer.allocate(20)
                data_min.put(buf)
                buf.set_pos(0)
                decoded_min = Data.get(buf)
                self.assertEqual(decoded_min.value.value.value.value, min_val)

                # Test maximum
                data_max = constructor(max_val)
                buf = ByteBuffer.allocate(20)
                data_max.put(buf)
                buf.set_pos(0)
                decoded_max = Data.get(buf)
                self.assertEqual(decoded_max.value.value.value.value, max_val)


class TestDataRepr(unittest.TestCase):
    """Test Data __repr__ method"""

    def test_repr(self) -> None:
        """Test __repr__ returns meaningful string"""
        data = Data.integer(42)
        repr_str = repr(data)
        self.assertIn("Data", repr_str)
        self.assertIn("Integer", repr_str)


if __name__ == "__main__":
    unittest.main()
