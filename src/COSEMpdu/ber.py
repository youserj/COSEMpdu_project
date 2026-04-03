# src/COSEMpdu/x690/bit_string.py
from dataclasses import dataclass
from typing import ClassVar, Self, cast, Optional, Protocol
from StructResult.result import ValueOrError, Error
from .x680.type import SEQUENCE_OF, NamedType, OBJECT_IDENTIFIER
from . import x680
from .x680 import TaggingMode, UniversalClassTagAssignments
from .byte_buffer import ByteBuffer
from .x690 import Tag, Length, TagError


def put_lc(buf: ByteBuffer, length: int, data: bytes) -> ValueOrError[int]:
    """common put length and contents to buffer"""
    if isinstance(l := Length(length).put(buf), Error):
        return l
    if isinstance(v := buf.write(data), Error):
        return v
    return l + v


class Type(x680.Type, Protocol):
    tag: ClassVar[Tag]

    @classmethod
    def get(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        """Decode with Tag + Length + Contents"""
        if isinstance(err := cls.tag.validate(buf), Error):
            return err
        return cls.get_lc(buf)  # Then decode length + contents

    def put(self, buf: ByteBuffer) -> ValueOrError[int]:
        """Encode with Tag + Length + Contents"""
        if isinstance(ret := self.tag.put(buf), Error):
            return ret
        if isinstance(ret2 := self.put_lc(buf), Error):
            return ret2
        return ret + ret2


type SEQUENCE = tuple[Optional[Type], ...]


@dataclass
class TaggedType[T: Type](Type, x680.TaggedType[T]):
    tag: ClassVar[Tag]
    value: T

    def is_explicit(self) -> bool:
        """Check if this is an explicit tag (X.680 §30.6)"""
        if self.mode == x680.TaggingMode.DEFAULT:
            return True  # Default is EXPLICIT
        return self.mode == x680.TaggingMode.EXPLICIT

    @classmethod
    def is_implicit(cls) -> bool:
        """Check if this is an implicit tag (X.680 §30.6)"""
        return cls.mode == x680.TaggingMode.IMPLICIT

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        if cls.is_implicit():
            if isinstance(value := cls.get_type().get_lc(buf), Error):  # IMPLICIT: decode base type contents directly (no inner tag)
                return value
        else:
            if isinstance(length := Length.get(buf), Error):  # EXPLICIT: decode length, then complete base encoding (TLV)
                return length
            if length.value == -1:
                raise ValueError("Indefinite length not supported for tagged types")
            # Decode inner value (with its own tag)
            if isinstance(value := cls.get_type().get(buf), Error):
                return value
        return cls(value)

    def __str__(self) -> str:
        """ASN.1 notation representation"""
        mode_str = ""
        if self.mode == TaggingMode.IMPLICIT:
            mode_str = "IMPLICIT"
        elif self.mode == TaggingMode.EXPLICIT:
            mode_str = "EXPLICIT"
        return f"[{int(self.tag)}] {mode_str} {self.get_type().__name__}"

    def put(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode tagged type per X.690 §8.14

        Returns number of bytes written.

        X.690 §8.14:
        - IMPLICIT: encode outer tag + base type contents (no inner tag)
        - EXPLICIT: encode outer tag (constructed) + length + complete base encoding
        """
        # Encode the outer tag
        if self.is_explicit():
            # EXPLICIT: always constructed (X.690 §8.14.2)
            tag_to_encode = Tag(
                class_number=self.tag.class_number,
                class_=self.tag.class_,
                constructed=True
            )
        else:
            # IMPLICIT: preserve base type's constructed flag
            tag_to_encode = self.tag
        if isinstance(ret := tag_to_encode.put(buf), Error):
            return ret
        if isinstance(ret2 := self.put_lc(buf), Error):
            return ret2
        return ret + ret2

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        if self.is_explicit():
            # EXPLICIT: encode complete base encoding as contents
            if isinstance(l_pos := buf.shift_pos(1), Error):
                return l_pos
            if isinstance(counter := self.value.put(buf), Error):
                return counter
            length = Length(counter)
            if (step := len(length) - 1) > 0:
                if isinstance(end := buf.shift_right(l_pos + 1, counter, step), Error):
                    return end
            else:
                end = buf.get_pos()
            if isinstance(err := buf.set_pos(l_pos), Error):
                return err
            if isinstance(err := length.put(buf), Error):
                return err
            if isinstance(err := buf.set_pos(end), Error):
                return err
            return step + 1 + counter
        # IMPLICIT: encode base type contents only
        return self.value.put_lc(buf)


@dataclass
class BitStringType(Type, x680.BitStringType):
    """
    BIT STRING with BER encoding/decoding (X.690 §8.6)

    BER encoding structure (primitive form):
        [Tag=0x03] [Length] [unused_bits(1)] [padded_bits(N)]

    Standards:
        - Tag: UNIVERSAL 3 (X.690 §8.6)
        - Primitive encoding (constructed form not supported)
        - Unused bits in final octet: 0-7 (X.690 §8.6.2.2)
        - Bits ordered MSB-first within each octet (X.690 §8.6.2.1)
    """
    # Cached BER tag instance (primitive form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.BitString,
        constructed=False
    )

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        """
        Decode BIT STRING from BER (X.690 §8.6)
        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value < 0:
            return Error.from_e(ValueError("Indefinite length form not supported for BIT STRING primitive"))
        # Empty bitstring: length = 0
        if length.value == 0:
            return cls(())
        # First octet: unused bits count (0-7)
        if isinstance(unused_bits := buf.get_uint8(), Error):
            return unused_bits
        if not (0 <= unused_bits <= 7):
            return Error.from_e(ValueError(f"Invalid unused bits count: {unused_bits}"))
        # Remaining octets: bitstring contents
        data_length = length.value - 1
        if data_length < 0:
            return Error.from_e(ValueError("BIT STRING length too small (missing unused bits octet)"))
        # Read all data bytes at once
        if isinstance(data_view := buf.read(data_length), Error):
            return data_view
        # Extract bits MSB-first (bit 8 to bit 1 per octet)
        bits: list[int] = []
        for byte in data_view:
            for i in range(8):
                bits.append(1 if (byte & (1 << (7 - i))) else 0)
        # Remove unused trailing bits
        if unused_bits > 0:
            bits = bits[:-unused_bits]
        return cls(tuple(bits))

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode BIT STRING to BER primitive form (X.690 §8.6.2)
        Returns number of bytes written.
        """
        n = len(self.value)
        unused_bits = (8 - (n % 8)) % 8
        # Pad bits to octet boundary
        padded = list(self.value) + [0] * unused_bits
        # Convert to bytes (MSB-first per octet)
        data_bytes = bytearray()
        for i in range(0, len(padded), 8):
            byte = 0
            for j in range(8):
                if padded[i + j]:
                    byte |= (1 << (7 - j))
            data_bytes.append(byte)
        if isinstance(length := Length(1 + len(data_bytes)).put(buf), Error):
            return length
        if isinstance(u := buf.put_uint8(unused_bits), Error):
            return u
        if isinstance(v := buf.write(bytes(data_bytes)), Error):
            return v
        return length + u + v


@dataclass
class BooleanType(Type, x680.BooleanType):
    """
    BOOLEAN with BER encoding/decoding (X.690 §8.2)

    BER encoding structure:
        [Tag=0x01] [Length=0x01] [Content]

    Content:
        - FALSE → 0x00 (all bits zero)
        - TRUE  → 0xFF (any non-zero value, sender's option per X.690 §8.2.2)
                  DER/CER requires 0xFF (all bits one, X.690 §11.1)

    Standards:
        - Tag: UNIVERSAL 1 (X.680 §17.2, X.690 §8.2)
        - Length: always 1 octet (X.690 §8.2.1)
        - Content: 1 octet (X.690 §8.2.2)
        - A-XDR: same as BER (IEC 61334-6 §6.3)
    """
    # Cached BER tag instance (primitive form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.Boolean,
        constructed=False
    )

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        """
        Decode BOOLEAN from BER (X.690 §8.2)
        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value != 1:
            raise ValueError(f"BOOLEAN length must be 1, got {length.value}")
        if isinstance(content := buf.get_uint8(), Error):
            return content
        return cls(content != 0)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode BOOLEAN to BER (X.690 §8.2.2)
        Returns number of bytes written (always 3).

        Content encoding:
            FALSE → 0x00
            TRUE  → 0xFF (all bits one, DER/CER compliant)
        """
        if isinstance(length := Length(1).put(buf), Error):
            return length
        if isinstance(value := buf.put_uint8(0xFF if self.value else 0x00), Error):
            return value
        return length + value


@dataclass
class GraphicString(Type, x680.GraphicString):
    """GRAPHIC STRING with BER encoding/decoding (X.690 §8.21)"""

    # Cached BER tag instance (primitive form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.GraphicString,
        constructed=False
    )

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        """
        Decode GRAPHIC STRING contents only (no tag validation).

        Used for:
            - CHOICE alternatives (X.690 §8.13)
            - SEQUENCE components in A-XDR (IEC 61334-6 §6.9)

        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value < 0:
            raise ValueError(
                "Indefinite length form not supported for GRAPHIC STRING primitive"
            )
        if length.value == 0:
            return cls("")
        if isinstance(value := buf.read(length.value), Error):
            return value
        return cls(bytes(value).decode("ascii", errors="replace"))  # GRAPHIC STRING is ISO 8859-1, but we'll decode as ASCII for display

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode GRAPHIC STRING contents only (no tag).

        Used for:
            - CHOICE alternatives (X.690 §8.13)
            - SEQUENCE components in A-XDR (IEC 61334-6 §6.9)
        Returns number of bytes written.
        """
        return put_lc(buf, len(self.value), self.value.encode("ascii", errors="replace"))    # GRAPHIC STRING is ISO 8859-1, but we'll encode as ASCII for simplicity

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns:
            String representation of character content

        Note:
            - May contain non-printable characters
            - Use repr() for full byte representation
        """
        try:
            # Attempt UTF-8 decoding for display
            return self.value
        except Exception:
            return repr(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"


def create_alternatives(*values: NamedType[Type]) -> dict[Tag, NamedType[Type]]:
    return {value.type_.tag: value for value in values}


@dataclass
class ChoiceType(Type, x680.ChoiceType[Type]):
    """
    CHOICE with BER encoding/decoding (X.690 §8.13)

    BER encoding structure:
        [Tag=chosen_alternative] [Length] [Contents]

    Standards:
        - Tag: From chosen alternative (X.690 §8.13)
        - IEC 61334-6 §6.6: CHOICE alternatives must be explicitly tagged
        - A-XDR: Tag number encoded as 1 byte for CHOICE alternatives

    Note:
        - Encoding is identical to the chosen alternative type
        - Tag identifies which alternative was selected
        - For DLMS/COSEM, alternatives use CONTEXT SPECIFIC class
    """
    alternatives: ClassVar[dict[Tag, NamedType[Type]]]
    value: Type

    @classmethod
    def get(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        """
        Decode CHOICE from BER (X.690 §8.13)
        Returns instance with chosen alternative and advances buffer position.
        """
        if isinstance(tag := Tag.get(buf), Error):
            return tag
        if (n_t := cls.alternatives.get(tag)) is None:
            raise ValueError(f"{tag=} not in alternatives: {", ".join(map(str, (n_t.identifier for n_t in cls.alternatives.values())))}")
        # tag_byte = buf.get_uint8()
        # tag_number = tag_byte & 0x1F
        # for n_t in cls.alternatives:
        #     alternative_type = n_t.type_
        #     if int(alternative_type.tag) == tag_number:
        #         break
        # else:
        #     raise ValueError(f"Tag {tag_number} not in alternatives: {", ".join(map(str, (n_t.identifier for n_t in cls.alternatives)))}")
        if isinstance(value := n_t.type_.get_lc(buf), Error):
            return value
        return cls(value)

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        return cls.get(buf)

    def put(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode CHOICE to BER (X.690 §8.13)
        Returns number of bytes written.

        Encoding is identical to the chosen alternative type.
        """
        return self.value.put(buf)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        return self.put(buf)

    @property
    def selected(self) -> str:
        if (n_t := self.alternatives.get(self.value.tag)) is None:
            raise ValueError(f"Value {self.value} not in alternatives: {", ".join(map(str, (n_t.identifier for n_t in self.alternatives.values())))}")
        return n_t.identifier


@dataclass(frozen=True)
class EnumeratedType(Type, x680.EnumeratedType):
    """
    ENUMERATED with BER encoding/decoding (X.690 §8.4)

    BER encoding structure (primitive form):
        [Tag=0x0A] [Length] [Content]
    Content:
        - Enumeration index as signed integer (two's complement)
        - Minimal octets required (X.690 §8.3.2)

    Standards:
        - Tag: UNIVERSAL 10 (X.680 §19.7, X.690 §8.4)
        - Encoding: Same as INTEGER (X.690 §8.4)
        - Primitive encoding (constructed form not used)
        - IEC 61334-6 §6.4: DLMS ENUMERATED range 0..255 (1 byte)

    Note:
        - Enumeration indices assigned per X.680 §19.3
        - Root enumeration: indices start at 0
        - Extension additions: indices continue from root
    """
    # Cached BER tag instance (primitive form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.Enumerated,
        constructed=False
    )

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        """
        Decode ENUMERATED from BER (X.690 §8.4)
        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value < 0:
            return Error.from_e(ValueError("Indefinite length form not supported for ENUMERATED"))
        if length.value == 0:
            return Error.from_e(ValueError("ENUMERATED length must be >= 1"))
        # Read enumeration index as signed integer (two's complement)
        if isinstance(index := buf.get_uint(length.value), Error):
            return index
        # Convert to signed if high bit is set
        if index & (1 << (length.value * 8 - 1)):
            index -= (1 << (length.value * 8))
        return cls(index)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode ENUMERATED to BER primitive form (X.690 §8.4)
        Returns number of bytes written.

        Content encoding:
            - Enumeration index as signed integer (two's complement)
            - Minimal octets (no leading zero bytes except for sign)
        """
        # Convert to unsigned for byte encoding
        if self.value < 0:
            # Calculate minimum bytes needed for negative value
            value = self.value + (1 << ((self.value.bit_length() // 8 + 1) * 8))
            num_bytes = (self.value.bit_length() // 8) + 1
        else:
            value = self.value
            num_bytes = max(1, (self.value.bit_length() + 7) // 8)
            # Ensure sign bit is 0 for positive values
            if value & (1 << (num_bytes * 8 - 1)):
                num_bytes += 1

        # Write: tag + length + content
        content_bytes = value.to_bytes(num_bytes, byteorder="big")
        return put_lc(buf, num_bytes, content_bytes)


@dataclass
class IntegerType(Type, x680.IntegerType):
    """
    INTEGER with BER encoding/decoding (X.690 §8.3)

    BER encoding structure (primitive form):
        [Tag=0x02] [Length] [Content]

    Content:
        - Two's complement binary number (X.690 §8.3.3)
        - Minimal octets required (X.690 §8.3.2)
        - No leading zero bytes except for sign

    Standards:
        - Tag: UNIVERSAL 2 (X.680 §18.8, X.690 §8.3)
        - Primitive encoding (constructed form not used)
        - A-XDR: Fixed-length for constrained types (IEC 61334-6 §6.1)

    Note:
        - Positive integers: MSB must be 0 (may need leading 0x00)
        - Negative integers: MSB must be 1 (two's complement)
        - Zero: Single octet 0x00
    """
    # Cached BER tag instance (primitive form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.Integer,
        constructed=False
    )

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        """
        Decode INTEGER from BER (X.690 §8.3)
        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value < 0:
            raise ValueError("Indefinite length form not supported for INTEGER")
        if length.value == 0:
            raise ValueError("INTEGER length must be >= 1")

        # Read content octets as big-endian two's complement
        if isinstance(content := buf.read(length.value), Error):
            return content
        value = int.from_bytes(content, byteorder="big", signed=True)
        return cls(value)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode INTEGER to BER primitive form (X.690 §8.3)
        Returns number of bytes written.

        Content encoding:
            - Two's complement binary (minimal octets)
            - No leading zero bytes except for sign
        """
        # Calculate minimal bytes needed for two's complement
        if self.value == 0:
            content_bytes = b"\x00"
        else:
            # Calculate bit length for minimal representation
            bit_length = self.value.bit_length()
            # Add 1 for sign bit, round up to full bytes
            num_bytes = (bit_length + 1 + 7) // 8

            # Convert to two's complement bytes
            content_bytes = self.value.to_bytes(num_bytes, byteorder="big", signed=True)
        return put_lc(buf, len(content_bytes), content_bytes)


@dataclass
class NullType(Type, x680.NullType):
    """
    NULL with BER encoding/decoding (X.690 §8.8)
    BER encoding structure (primitive form):
        [Tag=0x05] [Length=0x00] [Contents=<empty>]

    Standards:
        - Tag: UNIVERSAL 5 (X.680 §23.2, X.690 §8.8)
        - Primitive encoding (constructed form not used)
        - Length: always 0 octets (X.690 §8.8.2)
        - Contents: empty (no octets)

    Note:
        - NULL has only one value (the null value)
        - Used to indicate absence of information or as placeholder
        - IEC 61334-6: NULL encoding same as BER (§6.13)
    """
    # Cached BER tag instance (primitive form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.Null,
        constructed=False
    )

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        """
        Decode NULL from BER (X.690 §8.8)
        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value != 0:
            return Error.from_e(ValueError(f"NULL length must be 0, got {length.value}"))
        # NULL has no contents - nothing to read
        return cls(None)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode NULL to BER primitive form (X.690 §8.8)
        Returns number of bytes written (always 2).

        Encoding:
            Tag(1) + Length(1) + Contents(0) = 2 bytes
        """
        return Length(0).put(buf)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __eq__(self, other: object) -> bool:
        """All NULL values are equal"""
        return isinstance(other, NullType)


@dataclass
class ObjectIdentifierType(Type, x680.ObjectIdentifierType):
    """
    OBJECT IDENTIFIER with BER encoding/decoding (X.690 §8.19).

    BER encoding structure:
        [Tag=0x06] [Length] [Content]

    Content encoding:
        - First two arcs: (arc0 * 40) + arc1 (single octet)
        - Subsequent arcs: base-128 variable-length encoding
          * Bit 8 = 1: more octets follow
          * Bit 8 = 0: last octet of subidentifier
          * Bits 7-1: value (MSB first)

    Example:
        OID {1 0 1} (iso.standard.asn1):
        - First two arcs: (1 * 40) + 0 = 40 = 0x28
        - Third arc: 1 = 0x01
        - Content: 0x28 0x01
        - Full encoding: 0x06 0x02 0x28 0x01

    References:
        - X.690 §8.19: Encoding of an object identifier value
        - X.680 §31: Notation for the object identifier type
        - ITU-T X.660 | ISO/IEC 9834-1: OID registration procedures
    """

    # Cached BER tag instance (primitive form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.ObjectIdentifier,
        constructed=False
    )
    value: OBJECT_IDENTIFIER

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        """
        Decode OBJECT IDENTIFIER contents only (no tag validation).

        Used for:
            - CHOICE alternatives (X.690 §8.13)
            - Explicitly tagged types where outer tag already validated

        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value < 0:
            return Error.from_e(ValueError("Indefinite length form not supported for OBJECT IDENTIFIER"))
        if length.value == 0:
            return Error.from_e(ValueError("OBJECT IDENTIFIER must have at least 1 content octet"))
        # Read all content octets
        if isinstance(content := buf.read(length.value), Error):
            return content
        # Decode first octet (first two arcs)
        first_octet = content[0]
        arc0 = first_octet // 40
        arc1 = first_octet % 40
        arcs = [arc0, arc1]
        # Decode remaining arcs (base-128 variable-length)
        pos = 1
        while pos < len(content):
            arc_value = 0
            while True:
                if pos >= len(content):
                    return Error.from_e(BufferError("Truncated OBJECT IDENTIFIER encoding"))
                octet = content[pos]
                pos += 1
                # Add 7 bits to arc value
                arc_value = (arc_value << 7) | (octet & 0x7F)
                # Check continuation bit
                if not (octet & 0x80):
                    break
            arcs.append(arc_value)
        return cls(tuple(arcs))

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode OBJECT IDENTIFIER contents only (no tag).

        Used for:
            - CHOICE alternatives (X.690 §8.13)
            - Explicitly tagged types where outer tag already encoded

        Returns number of bytes written.
        """
        # Encode first two arcs as single octet
        first_octet: int = (self.value[0] * 40) + self.value[1]
        content_bytes = bytearray([first_octet])
        # Encode remaining arcs (base-128 variable-length)
        for arc in self.value[2:]:
            if arc == 0:
                content_bytes.append(0x00)
            else:
                # Calculate number of octets needed
                arc_bits = arc.bit_length()
                num_octets = (arc_bits + 6) // 7
                # Encode in 7-bit chunks (MSB first)
                chunks: list[int] = []
                value = arc
                for _ in range(num_octets):
                    chunks.append(value & 0x7F)
                    value >>= 7
                # Reverse to get MSB first
                chunks.reverse()
                # Set continuation bit on all but last octet
                for i in range(len(chunks) - 1):
                    chunks[i] |= 0x80
                content_bytes.extend(chunks)
        return put_lc(buf, len(content_bytes), content_bytes)


@dataclass
class OctetStringType(Type, x680.OctetStringType):
    """
    OCTET STRING with BER encoding/decoding (X.690 §8.7)

    BER encoding structure (primitive form):
        [Tag=0x04] [Length] [Contents(N)]

    Standards:
        - Tag: UNIVERSAL 4 (X.680 §22.2, X.690 §8.7)
        - Primitive encoding (constructed form optional)
        - Contents: raw octets (no unused bits like BIT STRING)
        - A-XDR: same as BER for variable-length (IEC 61334-6 §6.5)

    Note:
        - Simpler than BIT STRING (no unused_bits octet)
        - Direct octet content
        - For DLMS/COSEM, used for binary data and VisibleString
    """
    # Cached BER tag instance (primitive form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.OctetString,
        constructed=False
    )

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        """
        Decode OCTET STRING from BER (X.690 §8.7)
        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value < 0:
            raise ValueError("Indefinite length form not supported for OCTET STRING primitive")
        # Read octets directly (no unused_bits like BIT STRING)
        if length.value == 0:
            return cls(b"")
        if isinstance(data := buf.read(length.value), Error):
            return data
        return cls(bytes(data))

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode OCTET STRING to BER primitive form (X.690 §8.7.2)
        Returns number of bytes written.

        Content encoding:
            - Direct octet content (no padding)
            - No unused_bits octet (unlike BIT STRING)
        """
        return put_lc(buf, len(self.value), self.value)


@dataclass
class SequenceType(Type, x680.SequenceType):
    """
    SEQUENCE with BER encoding/decoding (X.690 §8.9)

    BER encoding structure (constructed form):
        [Tag=0x30] [Length] [Component1] [Component2] ... [ComponentN]

    Standards:
        - Tag: UNIVERSAL 16 (X.680 §24.16, X.690 §8.9)
        - Constructed encoding (always, X.690 §8.9.1)
        - Components encoded in definition order (X.690 §8.9.2)
        - OPTIONAL/DEFAULT components may be absent (X.690 §8.9.3)
        - IEC 61334-6 §6.9: SEQUENCE component tags NOT encoded

    Note:
        - Encoding is concatenation of component encodings
        - Component order is fixed by ASN.1 definition
        - For DLMS/COSEM, component tags are omitted (unlike BER)
        - OPTIONAL/DEFAULT indicated by presence flag in A-XDR
    """
    # Cached BER tag instance (constructed form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.Sequence,
        constructed=True
    )
    components: ClassVar[tuple[NamedType[Type], ...]]
    value: SEQUENCE

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        """
        Decode SEQUENCE from BER (X.690 §8.9)
        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value < 0:
            return Error.from_e(ValueError("Indefinite length form not supported for SEQUENCE"))
        # Read all component encodings within the length
        start_pos = buf.get_pos()
        components_data: list[Optional[Type]] = []
        for n_t in cls.components:
            if buf.get_pos() - start_pos >= length.value:
                # Component is absent (OPTIONAL or DEFAULT)
                components_data.append(None)
                continue
            # Decode the component using its own get() method
            # This handles tag, length, and contents for each component
            if isinstance(value := n_t.type_.get(buf), Error):
                if value.has(exception_type=TagError):
                    if isinstance(n_t, x680.OptionalNamedType):
                        components_data.append(None)
                    elif isinstance(n_t, x680.DefaultNamedType):
                        components_data.append(n_t.default)
                    else:
                        return Error.from_e(ValueError(f"can't get {cls.__name__} from {buf}"))
            else:
                components_data.append(value)
        return cls(tuple(components_data))

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode SEQUENCE to BER constructed form (X.690 §8.9)
        Returns number of bytes written.

        Encoding:
            - Tag (1 byte for UNIVERSAL 16)
            - Length (variable)
            - Components in definition order (only present ones)
        """
        # Encode all present components
        counter: int = 0
        if isinstance(l_pos := buf.shift_pos(1), Error):
            return l_pos
        for value, n_t in zip(self.value, self.components):
            if (
                isinstance(n_t, x680.DefaultNamedType)
                and value == n_t.default
            ):
                continue
            if value is None:
                if isinstance(n_t, x680.OptionalNamedType):
                    continue
                raise ValueError(f"Required component <{n_t.identifier}> not set")
            if isinstance(tmp := value.put(buf), Error):
                return tmp
            counter += tmp
        length = Length(counter)
        if (step := len(length) - 1) > 0:
            if isinstance(end := buf.shift_right(l_pos + 1, counter, step), Error):
                return end
        else:
            end = buf.get_pos()
        if isinstance(err := buf.set_pos(l_pos), Error):
            return err
        length.put(buf)
        if isinstance(err := buf.set_pos(end), Error):
            return err
        return step + 1 + counter


@dataclass
class SequenceOfType[T: Type](Type, x680.SequenceOfType[T]):
    """
    SEQUENCE OF with BER encoding/decoding (X.690 §8.10)
    BER encoding structure (constructed form):
        [Tag=0x30] [Length] [Component1] [Component2] ... [ComponentN]

    Standards:
        - Tag: UNIVERSAL 16 (X.680 §25.2, X.690 §8.10)
        - Constructed encoding (always, X.690 §8.10.1)
        - Components encoded in order of appearance (X.690 §8.10.3)
        - IEC 61334-6 §6.10: DLMS/COSEM SEQUENCE OF usage

    Note:
        - Each component is encoded using its own BER encoding rules
        - Length field covers all component encodings combined
        - Empty sequence: Length = 0, no component encodings
    """
    # Class variable: universal tag for SEQUENCE OF (constructed)
    # X.680 Table 1, X.690 §8.10.1: UNIVERSAL 16, constructed
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.SequenceOf,
        constructed=True
    )
    component_type: ClassVar[type[Type]]

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        """
        Decode SEQUENCE OF from BER (X.690 §8.10)
        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value < 0:
            return Error.from_e(ValueError("Indefinite length form not supported for SEQUENCE OF"))
        if length.value == 0:
            return cls([])
        # Decode components until we've consumed all bytes
        components: SEQUENCE_OF[T] = []
        start_pos = buf.get_pos()
        bytes_read = 0
        while bytes_read < length.value:
            # Decode next component using component type's get() method
            if isinstance(component := cast("T", cls.component_type.get(buf)), Error):
                return component
            components.append(component)
            # Track bytes consumed
            current_pos = buf.get_pos()
            bytes_read = current_pos - start_pos
        # Verify we consumed exactly the expected length
        if bytes_read != length.value:
            return Error.from_e(BufferError(f"SEQUENCE OF decoded {bytes_read} bytes, expected {length.value}"))
        return cls(value=components)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode SEQUENCE OF to BER constructed form (X.690 §8.10)
        Returns number of bytes written.
        """
        counter: int = 0
        if isinstance(l_pos := buf.shift_pos(1), Error):
            return l_pos
        for component in self.value:
            if isinstance(tmp := component.put(buf), Error):
                return tmp
            counter += tmp
        length = Length(counter)
        if (step := len(length) - 1) > 0:
            if isinstance(end := buf.shift_right(l_pos + 1, counter, step), Error):
                return end
        else:
            end = buf.get_pos()
        if isinstance(err := buf.set_pos(l_pos), Error):
            return err
        length.put(buf)
        if isinstance(err := buf.set_pos(end), Error):
            return err
        return step + 1 + counter

    @property
    def is_empty(self) -> bool:
        """Check if sequence contains no components"""
        return len(self.value) == 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(component={self.component_type.__name__}, count={len(self.value)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SequenceOfType):
            return False
        return (
            self.component_type == other.component_type and
            self.value == other.value
        )


@dataclass
class GeneralizedTime(Type, x680.GeneralizedTime):
    """GeneralizedTime with BER encoding (X.690 §8.23)"""
    tag: ClassVar[Tag] = Tag(class_number=UniversalClassTagAssignments.GeneralizedTime, constructed=False)

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        """Decode GeneralizedTime from BER VisibleString"""
        if isinstance(length := Length.get(buf), Error):
            return length
        if isinstance(value := buf.read(length.value), Error):
            return value
        data = bytes(value).decode("ascii")
        return cls(data)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """Encode GeneralizedTime to BER VisibleString"""
        data = self.value.encode("ascii")
        return put_lc(buf, len(data), data)


@dataclass
class ConstrainedType[T: Type](Type, x680.ConstrainedType[T]):
    @classmethod
    def get(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        if isinstance(value := cls.get_type().get(buf), Error):
            return value
        return cls(value)

    def put(self, buf: ByteBuffer) -> ValueOrError[int]:
        return self.value.put(buf)

    @classmethod
    def get_lc(cls, buf: ByteBuffer) -> ValueOrError[Self]:
        if isinstance(value := cls.get_type().get_lc(buf), Error):
            return value
        return cls(value)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        return self.value.put_lc(buf)
