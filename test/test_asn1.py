import unittest
from src.COSEMpdu import asn1


class TestType(unittest.TestCase):
    def test_Tagged(self):
        class DoubleLong(asn1.WithoutCoding, asn1.TaggedType):
            Tag = asn1.Tag(5, asn1.Class.APPLICATION)
            Type = asn1.IntegerType
            Size = 4
            __slots__ = ("value", )

    def test_choice(self):
        class Data(asn1.WithoutCoding, asn1.Choice):
            ELEMENTS = (
                asn1.NamedType("null", asn1.NullType),
                asn1.NamedType("integer", asn1.IntegerType)
            )

        value = Data.get_named_type(2)
        print(value)
        value = Data.get_named_type(5)
        print(value)
        value = Data.get_named_type(5)
        print(value)
