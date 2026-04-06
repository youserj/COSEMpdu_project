from typing import Self
from .type import BuiltinType, OCTET_STRING, Simple


class OctetStringType(Simple[OCTET_STRING], BuiltinType):
    """
    OCTET STRING type (X.680 §22, X.690 §8.7)
    NATIVE REPRESENTATION: bytes

    ASN.1 examples:
        ImageData ::= OCTET STRING
        'A5'H, '10100101'B (converted to bytes internally)

    Standards compliance:
    - Tag: UNIVERSAL 4 (X.680 §22.2)
    - Values: arbitrary sequence of octets (X.680 §6.3.49)
    - XML notation: <OCTET_STRING>hex</OCTET_STRING> (X.680 Table 4)
    """
    value: OCTET_STRING

    @classmethod
    def default(cls) -> Self:
        """Default to empty OCTET STRING"""
        return cls(b"")

    def __len__(self) -> int:
        """Length in octets (X.680 §22.6)"""
        return len(self.value)

    def __bytes__(self) -> bytes:
        """Direct access to native bytes representation"""
        return self.value

    def hex(self) -> str:
        """Hexadecimal string representation (uppercase, no prefix/suffix)"""
        return self.value.hex().upper()

    def __str__(self) -> str:
        """ASN.1 value notation: 'A5'H (X.680 §22.3)"""
        return f"'{self.hex()}'H"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(b'{self.value.hex()}')"

    @classmethod
    def empty(cls) -> Self:
        return cls(b"")
