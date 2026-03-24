"""
A-XDR Encoding Rules for DLMS/COSEM (IEC 61334-6:2000)

This module implements A-XDR (Adapted XDR) encoding rules optimized for 
DLMS/COSEM protocol. Unlike BER, A-XDR omits redundant tag and length 
fields when the type is known from the specification.

Key differences from BER (X.690):
- SEQUENCE components: NO tags encoded (§6.9)
- Constrained INTEGER: Fixed-length, NO tag/length (§6.1)
- CHOICE alternatives: Tag number only (1 byte, §6.6)
- BOOLEAN: Single octet, NO tag/length (§6.2)
- Variable-length types: Length encoded as variable-length integer (§5.2)

Standards:
- IEC 61334-6:2000: A-XDR encoding rules
- X.680: ASN.1 notation
- X.690: BER encoding (reference for comparison)
"""

from dataclasses import dataclass
from typing import ClassVar, Self, Optional, cast, TypeAlias, Annotated, Protocol, Any
from COSEMpdu import x690
from .x680.tagged_type import TaggingMode
from .x680.constrained_type import ValueRange, SizeConstraint
from .x680.type import OptionalNamedType, DefaultNamedType, NamedType, INTEGER, SEQUENCE_OF
from . import x680
from .byte_buffer import ByteBuffer


# =============================================================================
# Helper Functions
# =============================================================================

def _encode_variable_length_integer(value: int) -> bytes:
    """
    Encode integer as variable-length per IEC 61334-6 §6.1.2.

    For values 0-127: single octet (bit 8 = 0)
    For values >127: length octet (bit 8 = 1) + value octets

    Returns:
        Encoded bytes
    """
    if 0 <= value <= 127:
        return bytes([value])
    # Calculate bytes needed for value
    num_bytes = (value.bit_length() + 7) // 8
    # Length octet: bit 8 = 1, bits 7-1 = number of value bytes
    length_octet = 0x80 | num_bytes
    value_bytes = value.to_bytes(num_bytes, byteorder="big")
    return bytes([length_octet]) + value_bytes


def _decode_variable_length_integer(buf: ByteBuffer) -> int:
    """
    Decode variable-length integer per IEC 61334-6 §6.1.2.

    Returns:
        Decoded integer value
    """
    first = buf.get_uint8()
    if not (first & 0x80):
        # Short form: bits 7-1 = value (0-127)
        return first
    # Long form: bits 7-1 = number of value bytes
    num_bytes = first & 0x7F
    if num_bytes == 0:
        raise ValueError("Invalid variable-length integer encoding")
    return buf.get_uint(num_bytes)


class Type(x680.Type, Protocol):
    @classmethod
    def get(cls, buf: ByteBuffer) -> Self:
        """Decode with Length + Contents"""
        return cls.get_lc(buf)  # Then decode length + contents

    def put(self, buf: ByteBuffer) -> int:
        """Encode with Length + Contents"""
        return self.put_lc(buf)


TagNumber: TypeAlias = Annotated[int, "0-255"]


@dataclass
class TaggedType[T: Type](Type, x680.TaggedType[T]):
    """
    TaggedType for A-XDR encoding (IEC 61334-6 §6.6, §6.7)

    Tagging modes:
    - IMPLICIT: Tag replaces original type's tag (no nested tag)
    - EXPLICIT: Tag wraps original type (may have nested tag for CHOICE)

    For DLMS/COSEM:
    - CHOICE alternatives: IMPLICIT (tag number only, 1 byte)
    - SEQUENCE components: NO tag encoded (§6.9)
    - APPLICATION tags: EXPLICIT (BER encoding per §6.7)
    """
    tag: ClassVar[TagNumber]
    mode: ClassVar[TaggingMode] = TaggingMode.IMPLICIT
    value: T

    @classmethod
    def get(cls, buf: ByteBuffer) -> Self:
        """
        Decode tagged type from A-XDR

        IMPLICIT mode (§6.6):
            [Tag(1)] [Contents without inner tag]

        EXPLICIT mode (§6.7):
            [Tag(1)] [Contents with inner tag if CHOICE]
        """
        # Read tag number (1 byte for A-XDR)
        tag_number = buf.get_uint8()
        if tag_number != cls.tag:
            raise ValueError(f"Expected tag {cls.tag}, got {tag_number}")
        return cls.get_lc(buf)

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        """
        Decode tagged type from A-XDR

        IMPLICIT mode (§6.6):
            [Tag(1)] [Contents without inner tag]

        EXPLICIT mode (§6.7):
            [Tag(1)] [Contents with inner tag if CHOICE]
        """
        # Decode contents based on tagging mode
        if cls.mode == TaggingMode.IMPLICIT:
            value = cls.get_type().get_lc(buf)  # IMPLICIT: contents without inner tag
        else:
            value = cls.get_type().get(buf)  # EXPLICIT: contents may have inner tag (e.g., nested CHOICE), get() includes tag/length if applicable
        return cls(value)

    def put(self, buf: ByteBuffer) -> int:
        """Encode with Length + Contents"""
        return buf.put_uint8(self.tag) + self.put_lc(buf)

    def put_lc(self, buf: ByteBuffer) -> int:
        """
        Encode tagged type to A-XDR

        IMPLICIT mode (§6.6):
            [Tag(1)] [Contents without inner tag]

        EXPLICIT mode (§6.7):
            [Tag(1)] [Contents with inner tag if CHOICE]

        Returns number of bytes written.
        """
        # Encode contents based on tagging mode
        if self.mode == TaggingMode.IMPLICIT:
            # IMPLICIT: contents without inner tag
            return self.value.put_lc(buf)
        # EXPLICIT: contents may have inner tag (e.g., nested CHOICE)
        return self.value.put(buf)  # put() includes tag/length if applicable

# =============================================================================
# BOOLEAN Type (IEC 61334-6 §6.2)
# =============================================================================


@dataclass
class BooleanType(Type, x680.BooleanType):
    """
    BOOLEAN with A-XDR encoding/decoding (IEC 61334-6 §6.2)

    A-XDR encoding structure:
        [Content(1)]  # NO tag, NO length

    Content:
        - FALSE → 0x00 (all bits zero)
        - TRUE  → 0xFF (sender's option, any non-zero)

    Standards:
        - IEC 61334-6 §6.2: BOOLEAN encoding
        - X.680 §17: BOOLEAN type definition
        - No tag/length (unlike BER which uses 3 bytes)

    Note:
        - Most compact boolean encoding (1 byte vs BER's 3 bytes)
        - Type known from specification, no tag needed
    """

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        """
        Decode BOOLEAN from A-XDR (IEC 61334-6 §6.2)

        Returns instance and advances buffer position.
        """
        # Single octet, no tag/length
        content = buf.get_uint8()
        return cls(content != 0)

    def put_lc(self, buf: ByteBuffer) -> int:
        """
        Encode BOOLEAN to A-XDR (IEC 61334-6 §6.2)

        Returns number of bytes written (always 1).

        Content encoding:
            FALSE → 0x00
            TRUE  → 0xFF
        """
        return buf.put_uint8(0xFF if self.value else 0x00)


# =============================================================================
# INTEGER Type (IEC 61334-6 §6.1)
# =============================================================================

@dataclass
class IntegerType(Type, x680.IntegerType):
    """
    INTEGER with A-XDR encoding/decoding (IEC 61334-6 §6.1)

    A-XDR provides TWO encoding forms:

    1. Fixed-length (constrained INTEGER):
       [Content(N)]  # NO tag, NO length
       - N determined by value range (e.g., INTEGER(0..255) = 1 byte)
       - Unsigned for non-negative ranges
       - Two's complement for signed ranges

    2. Variable-length (unconstrained INTEGER):
       [Length(1+)] [Content(N)]  # NO tag
       - Length: variable-length integer (§6.1.2)
       - Content: two's complement binary

    Standards:
        - IEC 61334-6 §6.1: INTEGER encoding
        - X.680 §18: INTEGER type definition
        - §6.1.1: Fixed-length encoding
        - §6.1.2: Variable-length encoding

    Note:
        - DLMS/COSEM mostly uses constrained INTEGERs (Unsigned8, Unsigned16, etc.)
        - More compact than BER for constrained types
    """
    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        """Variable-length encoding (§6.1.2)"""
        first = buf.get_uint8()
        if not (first & 0x80):
            # Short form: 0-127
            return cls(first)
        # Long form: length octet + value octets
        num_bytes = first & 0x7F
        return cls.get_c(buf, num_bytes)

    @classmethod
    def get_c(cls, buf: ByteBuffer, length: int) -> Self:
        content = buf.read(length)
        # Decode as two's complement
        value = int.from_bytes(content, byteorder="big", signed=True)
        return cls(value)

    def put_lc(self, buf: ByteBuffer) -> int:
        """Variable-length encoding"""
        if 0 <= self.value <= 127:
            return buf.put_uint8(self.value)
        encoded = _encode_variable_length_integer(self.value)
        return buf.write(encoded)


# =============================================================================
# BIT STRING Type (IEC 61334-6 §6.4)
# =============================================================================

@dataclass
class BitStringType(Type, x680.BitStringType):
    """
    BIT STRING with A-XDR encoding/decoding (IEC 61334-6 §6.4)

    A-XDR provides TWO encoding forms:

    1. Fixed-length (SIZE specified):
       [Content(N)]  # NO tag, NO length, NO unused_bits
       - N = (SIZE + 7) // 8 octets
       - Bits padded to octet boundary with zeros

    2. Variable-length (no SIZE):
       [Length(1+)] [unused_bits(1)] [Content(N)]  # NO tag
       - Length: number of BITS (not octets)
       - unused_bits: 0-7 (trailing unused bits in final octet)

    Standards:
        - IEC 61334-6 §6.4: BIT STRING encoding
        - X.680 §21: BIT STRING type definition
        - §6.4.1: Fixed-length encoding
        - §6.4.2: Variable-length encoding

    Note:
        - More compact than BER (no tag, no unused_bits for fixed-length)
        - DLMS uses fixed-length for conformance blocks
    """
    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        num_bits = _decode_variable_length_integer(buf)
        if num_bits == 0:
            return cls(())
        return cls.get_c(buf, num_bits)

    @classmethod
    def get_c(cls, buf: ByteBuffer, length: int) -> Self:
        bits: list[int] = []
        num_octets = (length + 7) // 8
        data = buf.read(num_octets)
        for byte in data:
            for i in range(8):
                bits.append(1 if (byte & (1 << (7 - i))) else 0)
        bits = bits[:length]  # Trim to exact bit length
        return cls(tuple(bits))

    def put_lc(self, buf: ByteBuffer) -> int:
        n = len(self.value)
        if n == 0:
            # Length = 0 bits
            return buf.put_uint8(0)
        # Encode length (number of BITS)
        length_bytes = _encode_variable_length_integer(len(self.value))
        return buf.write(length_bytes) + self.put_c(buf)

    def put_c(self, buf: ByteBuffer) -> int:
        n = len(self.value)
        unused_bits = (8 - (n % 8)) % 8
        # Pad to octet boundary
        padded = list(self.value) + [0] * unused_bits
        # Convert to bytes MSB-first
        data_bytes = bytearray()
        for i in range(0, len(padded), 8):
            byte = 0
            for j in range(8):
                if padded[i + j]:
                    byte |= (1 << (7 - j))
            data_bytes.append(byte)
        return buf.write(bytes(data_bytes))


# =============================================================================
# OCTET STRING Type (IEC 61334-6 §6.5)
# =============================================================================

@dataclass
class OctetStringType(Type, x680.OctetStringType):
    """
    OCTET STRING with A-XDR encoding/decoding (IEC 61334-6 §6.5)

    A-XDR provides TWO encoding forms:

    Standards:
        - IEC 61334-6 §6.5: OCTET STRING encoding
        - X.680 §22: OCTET STRING type definition
        - §6.5.1: Fixed-length encoding
        - §6.5.2: Variable-length encoding

    Note:
        - Simpler than BIT STRING (no unused_bits)
        - DLMS uses for VisibleString, data blocks, etc.
    """

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        num_octets = _decode_variable_length_integer(buf)
        if num_octets == 0:
            return cls(b"")
        return cls.get_c(buf, num_octets)

    @classmethod
    def get_c(cls, buf: ByteBuffer, length: int) -> Self:
        """decode content"""
        data = bytes(buf.read(length))
        return cls(data)

    def put_lc(self, buf: ByteBuffer) -> int:
        length_bytes = _encode_variable_length_integer(len(self.value))
        return buf.write(length_bytes) + self.put_c(buf)

    def put_c(self, buf: ByteBuffer) -> int:
        return buf.write(self.value)


@dataclass
class VisibleString(Type, x680.VisibleString):

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        # Variable-length encoding (§6.5.2) only
        num_octets = _decode_variable_length_integer(buf)
        if num_octets == 0:
            return cls("")
        data = bytes(buf.read(num_octets))
        return cls(data.decode(encoding="ascii"))

    def put_lc(self, buf: ByteBuffer) -> int:
        length_bytes = _encode_variable_length_integer(len(self.value))
        return buf.write(length_bytes) + buf.write(self.value.encode("ascii"))

    def __str__(self) -> str:
        return repr(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


@dataclass
class Utf8String(Type, x680.VisibleString):  # todo: copypast VisibleString

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        # Variable-length encoding (§6.5.2) only
        num_octets = _decode_variable_length_integer(buf)
        if num_octets == 0:
            return cls("")
        data = bytes(buf.read(num_octets))
        return cls(data.decode(encoding="utf-8"))

    def put_lc(self, buf: ByteBuffer) -> int:
        data = self.value.encode("utf-8")
        length_bytes = _encode_variable_length_integer(len(data))
        return buf.write(length_bytes) + buf.write(data)

    def __str__(self) -> str:
        return repr(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


# =============================================================================
# CHOICE Type (IEC 61334-6 §6.6)
# =============================================================================

@dataclass
class ChoiceType(Type, x680.ChoiceType[Type]):
    """
    CHOICE with A-XDR encoding/decoding (IEC 61334-6 §6.6)

    A-XDR encoding structure:
        [Tag(1)] [Contents]  # NO length for tag

    Tag:
        - Single octet (tag number only, 0-255)
        - Tag class is CONTEXT_SPECIFIC for DLMS

    Standards:
        - IEC 61334-6 §6.6: CHOICE encoding
        - X.680 §28: CHOICE type definition
        - All alternatives MUST be explicitly tagged

    Note:
        - Tag identifies selected alternative
        - Contents encoded per alternative type rules
        - More compact than BER (1 byte tag vs 2-3 bytes)
    """
    alternatives: ClassVar[dict[int, NamedType[TaggedType[Any]]]]
    value: TaggedType[Type]

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        """
        Decode CHOICE from A-XDR (IEC 61334-6 §6.6)

        Returns instance with chosen alternative and advances buffer position.
        """
        tag = buf.get_uint8()
        if (n_t := cls.alternatives.get(tag)) is None:
            raise ValueError(f"{tag} not in alternatives: {", ".join(map(str, (n_t.identifier for n_t in cls.alternatives.values())))}")
        return cls(n_t.type_.get_lc(buf))

    def put_lc(self, buf: ByteBuffer) -> int:
        """
        Encode CHOICE to A-XDR (IEC 61334-6 §6.6)

        Returns number of bytes written.
        """
        return self.value.put(buf)

    # todo: copypast from Ber.ChoiceType
    @property
    def selected(self) -> str:
        if (n_t := self.alternatives.get(self.value.tag)) is None:
            raise ValueError(f"Value {self.value} not in alternatives: {", ".join(map(str, (n_t.identifier for n_t in self.alternatives.values())))}")
        return n_t.identifier


# =============================================================================
# SEQUENCE Type (IEC 61334-6 §6.9)
# =============================================================================

@dataclass
class SequenceType(Type, x680.SequenceType):
    """
    SEQUENCE with A-XDR encoding/decoding (IEC 61334-6 §6.9)

    A-XDR encoding structure:
        [Component1] [Component2] ... [ComponentN]  # NO tag, NO length

    Component encoding:
        - Each component encoded per its type rules
        - NO tags for components (§6.9)
        - OPTIONAL/DEFAULT: presence flag precedes value (§6.8)

    Standards:
        - IEC 61334-6 §6.9: SEQUENCE encoding
        - X.680 §24: SEQUENCE type definition
        - §6.8: OPTIONAL/DEFAULT components

    Note:
        - Most compact SEQUENCE encoding (no tag/length overhead)
        - Component order fixed by ASN.1 definition
        - DLMS uses extensively for APDUs
    """

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        """
        Decode SEQUENCE from A-XDR (IEC 61334-6 §6.9)

        Returns instance and advances buffer position.
        """
        components_data: list[Optional[Type]] = []
        for n_t in cls.components:
            # Check for OPTIONAL/DEFAULT presence flag
            if isinstance(n_t, (OptionalNamedType, DefaultNamedType)):
                presence_flag = buf.get_uint8()
                if presence_flag == 0:
                    # Component absent
                    if isinstance(n_t, x680.DefaultNamedType):
                        components_data.append(n_t.default)
                    else:
                        components_data.append(None)
                    continue
            # Decode the component using its A-XDR get_contents()
            value = n_t.type_.get_lc(buf)
            components_data.append(value)
        return cls(tuple(components_data))

    def put_lc(self, buf: ByteBuffer) -> int:
        """
        Encode SEQUENCE to A-XDR (IEC 61334-6 §6.9)

        Returns number of bytes written.
        """
        written = 0
        for value, n_t in zip(self.value, self.components):
            # Handle OPTIONAL/DEFAULT with presence flag
            if isinstance(n_t, (OptionalNamedType, DefaultNamedType)):
                if value is None or (
                    isinstance(n_t, DefaultNamedType) and
                    value == n_t.default
                ):
                    # Component absent
                    written += buf.put_uint8(0)
                    continue
                # Component present
                written += buf.put_uint8(1)
            if value is None:
                raise ValueError(f"Required component <{n_t.identifier}> not set")
            written += value.put_lc(buf)  # Encode component contents (no tag/length)
        return written


ENUM_VALUE: TypeAlias = Annotated[INTEGER, "0-255"]

# =============================================================================
# ENUMERATED Type (IEC 61334-6 §6.3)
# =============================================================================


@dataclass(frozen=True)
class EnumeratedType(Type, x680.EnumeratedType):
    """
    ENUMERATED with A-XDR encoding/decoding (IEC 61334-6 §6.3)
    A-XDR encoding structure:
        [Content(1)]  # NO tag, NO length

    Content:
        - Enumeration index as unsigned integer (0-255)
        - Single octet per IEC 61334-6 §6.3
    Standards:
        - IEC 61334-6 §6.3: ENUMERATED encoding
        - X.680 §19: ENUMERATED type definition
        - Range restricted to 0..255 for A-XDR

    Note:
        - More compact than BER (1 byte vs 3-4 bytes)
        - DLMS uses for service errors, statuses, etc.
    """
    value: ENUM_VALUE

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        """
        Decode ENUMERATED from A-XDR (IEC 61334-6 §6.3)

        Returns instance and advances buffer position.
        """
        # Single octet, no tag/length
        index = buf.get_uint8()
        return cls(index)

    def put_lc(self, buf: ByteBuffer) -> int:
        """
        Encode ENUMERATED to A-XDR (IEC 61334-6 §6.3)

        Returns number of bytes written (always 1).
        """
        return buf.put_uint8(self.value)


# =============================================================================
# NULL Type (IEC 61334-6 §6.13)
# =============================================================================

@dataclass
class NullType(Type, x680.NullType):
    """
    NULL with A-XDR encoding/decoding (IEC 61334-6 §6.13)

    A-XDR encoding structure:
        [Tag(1)]  # For CHOICE alternatives only

    Standards:
        - IEC 61334-6 §6.13: NULL encoding
        - X.680 §23: NULL type definition

    Note:
        - In SEQUENCE: NO encoding (absence indicates NULL)
        - In CHOICE: Tag number only (1 byte)
        - Used to indicate absence of information
    """

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        """
        Decode NULL from A-XDR (IEC 61334-6 §6.13)

        Returns instance (no bytes consumed in SEQUENCE).
        """
        # NULL has no content in SEQUENCE components
        return cls(None)

    def put_lc(self, buf: ByteBuffer) -> int:
        """
        Encode NULL to A-XDR (IEC 61334-6 §6.13)

        Returns number of bytes written (0 in SEQUENCE).
        """
        # NULL has no content in SEQUENCE components
        return 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __eq__(self, other: object) -> bool:
        """All NULL values are equal"""
        return isinstance(other, NullType)


@dataclass
class NullType0(TaggedType[NullType]):
    """[0] IMPLICIT NULL"""
    tag = 0
    mode = TaggingMode.IMPLICIT
    value: NullType


null = NullType(None)

# =============================================================================
# SEQUENCE OF Type (IEC 61334-6 §6.10)
# =============================================================================


@dataclass
class SequenceOfType[T: Type](Type, x680.SequenceOfType[T]):
    """
    SEQUENCE OF with A-XDR encoding/decoding (IEC 61334-6 §6.10)

    A-XDR provides TWO encoding forms:
    1. Fixed-length (SIZE specified):
       [Component1] [Component2] ... [ComponentN]  # NO tag, NO length, NO count

    2. Variable-length (no SIZE):
       [Count(1+)] [Component1] [Component2] ... [ComponentN]  # NO tag
       - Count: number of components (variable-length integer)

    Standards:
        - IEC 61334-6 §6.10: SEQUENCE OF encoding
        - X.680 §25: SEQUENCE OF type definition
        - §6.10.1: Fixed-length encoding
        - §6.10.2: Variable-length encoding

    Note:
        - Each component encoded per its type rules
        - DLMS uses for lists, arrays, etc.
    """

    fixed_length: ClassVar[Optional[int]] = None  # Number of components (None = variable)
    value: SEQUENCE_OF[T]

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        """
        Decode SEQUENCE OF from A-XDR (IEC 61334-6 §6.10)

        Args:
            fixed_length: Number of components (None for variable-length)

        Returns instance and advances buffer position.
        """
        components: list[T] = []
        if cls.fixed_length is not None:
            # Fixed-length encoding (§6.10.1)
            for _ in range(cls.fixed_length):
                component = cast("T", cls.component_type.get_lc(buf))
                components.append(component)
        else:
            # Variable-length encoding (§6.10.2)
            num_components = _decode_variable_length_integer(buf)
            for _ in range(num_components):
                component = cast("T", cls.component_type.get_lc(buf))
                components.append(component)
        return cls(components)

    def put_lc(self, buf: ByteBuffer) -> int:
        """
        Encode SEQUENCE OF to A-XDR (IEC 61334-6 §6.10)

        Returns number of bytes written.
        """
        n = len(self.value)

        if self.fixed_length is not None:
            # Fixed-length encoding (§6.10.1)
            written = 0
            for component in self.value:
                written += component.put_lc(buf)
            return written
        # Variable-length encoding (§6.10.2)
        # Encode count
        count_bytes = _encode_variable_length_integer(n)
        written = buf.write(count_bytes)

        # Encode components
        for component in self.value:
            written += component.put_lc(buf)

        return written

    @property
    def is_empty(self) -> bool:
        """Check if sequence contains no components"""
        return len(self.value) == 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{len(self.value)}].{self.component_type.__name__}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SequenceOfType):
            return False
        return (
            self.component_type == other.component_type and
            self.value == other.value
        )


@dataclass
class GeneralizedTime(Type, x680.GeneralizedTime):

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        length = x690.Length.get(buf)
        data = buf.read(length.value).tobytes().decode("ascii")
        return cls(data)

    def put_lc(self, buf: ByteBuffer) -> int:
        data = self.value.encode("ascii")
        return x690.Length(len(data)).put(buf) + buf.write(data)


@dataclass
class ConstrainedIntegerType(Type, x680.ConstrainedType[IntegerType]):
    fixed_length: ClassVar[Optional[int]] = None
    signed: ClassVar[bool] = True
    value: IntegerType

    @classmethod
    def __init_subclass__(cls) -> None:
        if isinstance(v_r := cls.constraint_spec, ValueRange):
            if v_r.lower_endpoint >= 0:
                cls.signed = False
            cls.fixed_length = max(1, ((v_r.upper_endpoint - v_r.lower_endpoint).bit_length() + 7) // 8)

    @classmethod
    def from_int(cls, value: INTEGER) -> Self:
        return cls(IntegerType(value))

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        """
        Decode INTEGER from A-XDR (IEC 61334-6 §6.1.1)

        Args:
            fixed_length: Number of octets (None for variable-length)

        Returns instance and advances buffer position.
        """
        if isinstance(cls.fixed_length, int):
            if cls.fixed_length == 0:
                return cls(IntegerType(0))
            content = buf.read(cls.fixed_length)
            # Decode as unsigned for non-negative, signed for negative ranges
            # DLMS typically uses unsigned for constrained types
            value = int.from_bytes(content, byteorder="big", signed=cls.signed)
            return cls(IntegerType(value))
        return cls(IntegerType.get_lc(buf))

    def put_lc(self, buf: ByteBuffer) -> int:
        """
        Encode INTEGER to A-XDR (IEC 61334-6 §6.1)

        Returns number of bytes written.
        """
        if isinstance(self.fixed_length, int):
            if self.fixed_length == 0:
                return 0
            content_bytes = self.value.value.to_bytes(
                self.fixed_length,
                byteorder="big",
                signed=self.signed
            )
            return buf.write(content_bytes)
        return self.value.put_lc(buf)


@dataclass
class ConstrainedOctetStringType(Type, x680.ConstrainedType[OctetStringType]):
    fixed_length: ClassVar[Optional[int]] = None
    value: OctetStringType

    @classmethod
    def __init_subclass__(cls) -> None:
        if (  # Fixed-length encoding (§6.5.1)
            isinstance(cls.constraint_spec, SizeConstraint)
            and cls.constraint_spec.min_size is None
        ):
            cls.fixed_length = cls.constraint_spec.max_size

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        type_ = cls.get_type()
        if isinstance(cls.fixed_length, int):
            return cls(type_.get_c(buf, cls.fixed_length))
        return cls(type_.get_lc(buf))

    def put_lc(self, buf: ByteBuffer) -> int:
        if isinstance(self.fixed_length, int):
            return self.value.put_c(buf)
        return self.value.put_lc(buf)


@dataclass
class ConstrainedBitStringType(Type, x680.ConstrainedType[BitStringType]):
    fixed_length: ClassVar[Optional[int]] = None
    value: BitStringType

    @classmethod
    def __init_subclass__(cls) -> None:
        if (  # Fixed-length encoding (§6.4.1)
            isinstance(cls.constraint_spec, SizeConstraint)
            and cls.constraint_spec.min_size is None
        ):
            cls.fixed_length = cls.constraint_spec.max_size

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> Self:
        type_ = cls.get_type()
        if isinstance(cls.fixed_length, int):
            return cls(type_.get_c(buf, cls.fixed_length))
        return cls(type_.get_lc(buf))

    def put_lc(self, buf: ByteBuffer) -> int:
        if isinstance(self.fixed_length, int):
            return self.value.put_c(buf)
        return self.value.put_lc(buf)


def create_alternatives[U: Type](*values: NamedType[TaggedType[U]]) -> dict[int, NamedType[TaggedType[U]]]:
    return {value.type_.tag: value for value in values}
