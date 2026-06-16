# src/COSEMpdu/x690/bit_string.py
from typing import ClassVar, Self, cast, Optional, get_args
from StructResult.result import ValueOrError, Error
from .x680 import SEQUENCE_OF, OBJECT_IDENTIFIER, UniversalClassTagAssignments
from . import x680
from .byte_buffer import ByteBuffer, put_chain, ReadableByteBuffer
from .x690 import Tag, Length, TagError, EDTLV


def put_lc(buf: ByteBuffer, length: int, data: bytes) -> ValueOrError[int]:
    """common put length and contents to buffer"""
    return put_chain(
        Length(length).put(buf),
        buf.write(data)
    )


class ExplicitTaggedType(x680.Type, EDTLV):
    """
    EXPLICIT tagged type for BER encoding (X.690 §8.14).

    In EXPLICIT tagging the outer tag wraps the **complete** base
    encoding — the wire format is:

        ``[outer tag] [length] [inner TLV]``

    where *inner TLV* is the normal Tag-Length-Value encoding of the
    base type (e.g. ``INTEGER``, ``OCTET STRING`` …).  The inner type
    therefore **retains its own universal tag**.

    **Two tags, two roles**

    ======== =====================================================
    Tag      Role
    ======== =====================================================
    ``tag2`` outer (explicit) tag — must be ``constructed=True``
             per X.690 §8.14.3.  Defined on the subclass.
    ``tag``   inner tag — inherited from the concrete base type
             (e.g. ``IntegerType.tag = Tag(UNIVERSAL 2)``)
    ======== =====================================================

    **Inheritance note**

    The class extends ``x680.Type`` — *not* ``ber.Type`` — so that
    ``super().get()`` / ``super().put()`` go through the MRO to the
    concrete type's ``get()`` / ``put()`` which already include
    inner-tag validation and length framing.  This is the key design
    choice that keeps the EXPLICIT logic **thin** (only outer tag +
    outer length).

    Contrast with ``ImplicitTaggedType``, which extends ``ber.Type``
    and performs pure tag substitution — the outer tag directly
    replaces the inner tag, no inner TLV frame is emitted.

    Usage::

        class MyExplicitType(ExplicitTaggedType, IntegerType):
            tag2 = Tag(class_number=42, class_=Class.Context, constructed=True)

    References:
        - X.690 §8.14: Encoding of a tagged value
    """
    tag2: ClassVar[Tag]

    @classmethod
    def get(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode EXPLICIT tagged value from BER (X.690 §8.14).

        Decoding sequence:

        1. Validate outer tag (``tag2``).
        2. Decode **outer length** — the byte count of the inner
           TLV frame.
        3. Reject indefinite length (not supported).
        4. Call ``super().get()`` — thanks to the MRO this reaches
           ``ber.Type.get()`` on the concrete base type, which
           itself validates the **inner tag**, decodes the inner
           length, and reads the contents.
        5. Verify that exactly the declared outer length was
           consumed (length-mismatch guard).
        """
        if isinstance(err := cls.tag2.validate(buf), Error):
            return err
        # EXPLICIT: decode length, then complete base encoding (TLV)
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value == -1:
            return Error.from_e(ValueError("Indefinite length not supported for tagged types"))
        # Decode inner value (with its own tag)
        start_pos = buf.get_pos()
        if isinstance(result := super().get(buf), Error):
            return result
        consumed = buf.get_pos() - start_pos
        if consumed != length.value:
            return Error.from_e(ValueError(f"Tagged type length mismatch: declared {length.value}, consumed {consumed}"))
        return result

    def __str__(self) -> str:
        """
        ASN.1 notation representation.

        Uses ``super().__class__.__name__`` to obtain the name of
        the **concrete** type (e.g. ``IntegerType``) rather than
        ``ExplicitTaggedType`` itself.
        """
        return f"[{int(self.tag2)}] EXPLICIT {super().__class__.__name__}"

    def put(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode EXPLICIT tagged value per X.690 §8.14.

        Encoding algorithm (length-writeback pattern):

        1. Write outer tag (``tag2``).
        2. Reserve 1 byte for the outer length (position ``l_pos``).
        3. Call ``super().put()`` → concrete type's full TLV encoding
           (inner tag + inner length + contents).  Record the number
           of bytes written as ``n_super``.
        4. Create a ``Length(n_super)``.  If its DER-encoded form is
           longer than 1 byte, ``shift_right`` the inner TLV frame
           to make room.
        5. Write the outer length into the reserved slot.
        6. Reposition past the moved data and return the total number
           of bytes written.

        Wire format::

            [outer tag] [outer length] [inner TLV]

        Returns number of bytes written.
        """
        # Encode the outer tag
        start_pos: int = buf.get_pos()
        if isinstance(n_tag2 := self.tag2.put(buf), Error):
            return n_tag2
        sub_buf = buf.sub_buffer()
        if isinstance(err := buf.shift_pos(1), Error):
            return err
        if isinstance(n_super := super().put(buf), Error):
            return n_super
        length = Length(n_super)
        if (step := len(length) - 1) > 0:
            if isinstance(shift := buf.shift_right(start_pos + 2, n_super, step), Error):
                return shift
            buf.set_pos(shift)
        if isinstance(err := length.put(sub_buf), Error):
            return err
        return buf.get_pos() - start_pos


class ImplicitTaggedType(x680.Type, EDTLV):
    """
    IMPLICIT โ�� pure tag substitution for BER (X.690 ยง8.14.1).

    In IMPLICIT tagging the outer tag replaces the inner type's tag
    entirely.  Contents encoding/decoding is delegated straight to the
    inner type with no wrapping, no inner Tag-Length frame, and no
    conditional logic.

    Because *all* behaviour is inherited:
      - ``get()``  / ``put()``     โ�� outer tag from ``ber.Type``
      - ``get_lc()`` / ``put_lc()`` โ�� contents from the ``_T`` protocol
    this class requires **zero method overrides**.  Only ``tag`` must be
    supplied by the subclass.

    Usage::

        class MyImplicitType(ImplicitTaggedType[IntegerType]):
            tag = Tag(class_number=42, class_=Class.Context)

    Contrast with ``TaggedType``, which handles **both** IMPLICIT and
    EXPLICIT at the cost of runtime ``if``-checks in every method.
    """
    tag: ClassVar[Tag]

    @classmethod
    def get(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """Decode with Tag + Length + Contents"""
        if isinstance(err := cls.tag.validate(buf), Error):
            return err
        return cls.get_lc(buf)  # Then decode length + contents

    def put(self, buf: ByteBuffer) -> ValueOrError[int]:
        """Encode with Tag + Length + Contents"""
        return put_chain(
            self.tag.put(buf),
            self.put_lc(buf)
        )


type TaggedType = ImplicitTaggedType | ExplicitTaggedType
type NamedType = x680.NamedType[TaggedType]


class BitStringType(ImplicitTaggedType, x680.BitStringType):
    """
    BIT STRING with BER encoding/decoding (X.690 ยง8.6)

    BER encoding structure (primitive form):
        [Tag=0x03] [Length] [unused_bits(1)] [padded_bits(N)]

    Standards:
        - Tag: UNIVERSAL 3 (X.690 ยง8.6)
        - Primitive encoding (constructed form not supported)
        - Unused bits in final octet: 0-7 (X.690 ยง8.6.2.2)
        - Bits ordered MSB-first within each octet (X.690 ยง8.6.2.1)
    """
    # Cached BER tag instance (primitive form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.BitString,
        constructed=False
    )

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode BIT STRING from BER (X.690 ยง8.6)
        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value < 0:
            return Error.from_e(ValueError("Indefinite length form not supported for BIT STRING primitive"))
        # Empty bitstring: length = 0
        if length.value == 0:
            return cls.new(())
        # First octet: unused bits count (0-7)
        if isinstance(unused_bits := buf.get_u8(), Error):
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
        return cls.new(tuple(bits))

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode BIT STRING to BER primitive form (X.690 ยง8.6.2)
        Returns number of bytes written.
        """
        n = len(self.value)
        unused_bits = (8 - (n % 8)) % 8                 # Pad bits to octet boundary
        padded = list(self.value) + [0] * unused_bits   # Convert to bytes (MSB-first per octet)
        data_bytes = bytearray()
        for i in range(0, len(padded), 8):
            byte = 0
            for j in range(8):
                if padded[i + j]:
                    byte |= (1 << (7 - j))
            data_bytes.append(byte)
        return put_chain(
            Length(1 + len(data_bytes)).put(buf),
            buf.put_u8(unused_bits),
            buf.write(bytes(data_bytes))
        )


class BooleanType(ImplicitTaggedType, x680.BooleanType):
    """
    BOOLEAN with BER encoding/decoding (X.690 ยง8.2)

    BER encoding structure:
        [Tag=0x01] [Length=0x01] [Content]

    Content:
        - FALSE โ�� 0x00 (all bits zero)
        - TRUE  โ�� 0xFF (any non-zero value, sender's option per X.690 ยง8.2.2)
                  DER/CER requires 0xFF (all bits one, X.690 ยง11.1)

    Standards:
        - Tag: UNIVERSAL 1 (X.680 ยง17.2, X.690 ยง8.2)
        - Length: always 1 octet (X.690 ยง8.2.1)
        - Content: 1 octet (X.690 ยง8.2.2)
        - A-XDR: same as BER (IEC 61334-6 ยง6.3)
    """
    # Cached BER tag instance (primitive form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.Boolean,
        constructed=False
    )

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode BOOLEAN from BER (X.690 ยง8.2)
        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value != 1:
            return Error.from_e(ValueError(f"BOOLEAN length must be 1, got {length.value}"))
        if isinstance(content := buf.get_u8(), Error):
            return content
        return cls.new(content)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode BOOLEAN to BER (X.690 ยง8.2.2)
        Returns number of bytes written (always 3).

        Content encoding:
            FALSE โ�� 0x00
            TRUE  โ�� 0xFF (all bits one, DER/CER compliant)
        """
        return put_chain(
            Length(1).put(buf),
            buf.put_u8(self.value)
        )


class GraphicString(ImplicitTaggedType, x680.GraphicString):
    """GRAPHIC STRING with BER encoding/decoding (X.690 ยง8.21)"""

    # Cached BER tag instance (primitive form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.GraphicString,
        constructed=False
    )

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode GRAPHIC STRING contents only (no tag validation).

        Used for:
            - CHOICE alternatives (X.690 ยง8.13)
            - SEQUENCE components in A-XDR (IEC 61334-6 ยง6.9)

        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value < 0:
            return Error.from_e(ValueError("Indefinite length form not supported for GRAPHIC STRING primitive"))
        if length.value == 0:
            return cls.new("")
        if isinstance(value := buf.read(length.value), Error):
            return value
        return cls.new(bytes(value).decode("ascii", errors="replace"))  # GRAPHIC STRING is ISO 8859-1, but we'll decode as ASCII for display

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode GRAPHIC STRING contents only (no tag).

        Used for:
            - CHOICE alternatives (X.690 ยง8.13)
            - SEQUENCE components in A-XDR (IEC 61334-6 ยง6.9)
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


class ChoiceType(x680.ChoiceType[TaggedType]):
    """
    CHOICE with BER encoding/decoding (X.690 ยง8.13)

    BER encoding structure:
        [Tag=chosen_alternative] [Length] [Contents]

    Standards:
        - Tag: From chosen alternative (X.690 ยง8.13)
        - IEC 61334-6 ยง6.6: CHOICE alternatives must be explicitly tagged
        - A-XDR: Tag number encoded as 1 byte for CHOICE alternatives

    Note:
        - Encoding is identical to the chosen alternative type
        - Tag identifies which alternative was selected
        - For DLMS/COSEM, alternatives use CONTEXT SPECIFIC class
    """
    alternatives: ClassVar[dict[int, TaggedType]]
    value: TaggedType

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, "alternatives"):
            cls.alternatives = {(type_.tag2 if hasattr(type_, "tag2") else type_.tag).class_number: type_ for type_ in get_args(cls.__annotations__["value"])}

    @classmethod
    def get(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode CHOICE from BER (X.690 ยง8.13)
        Returns instance with chosen alternative and advances buffer position.
        """
        if isinstance(tag := Tag.get(buf), Error):
            return tag
        if (t_ := cls.alternatives.get(tag.class_number)) is None:
            return Error.from_e(ValueError(f"got {tag=}, expected {", ".join(map(str, (t_.__class__.__name__ for t_ in cls.alternatives.values())))}"))
        if isinstance(value := t_.get_lc(buf), Error):
            return value
        return cls(value)

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        return cls.get(buf)

    def put(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode CHOICE to BER (X.690 ยง8.13)
        Returns number of bytes written.

        Encoding is identical to the chosen alternative type.
        """
        return self.value.put(buf)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        return self.put(buf)


class EnumeratedType(ImplicitTaggedType, x680.EnumeratedType):
    """
    ENUMERATED with BER encoding/decoding (X.690 ยง8.4)

    BER encoding structure (primitive form):
        [Tag=0x0A] [Length] [Content]
    Content:
        - Enumeration index as signed integer (two's complement)
        - Minimal octets required (X.690 ยง8.3.2)

    Standards:
        - Tag: UNIVERSAL 10 (X.680 ยง19.7, X.690 ยง8.4)
        - Encoding: Same as INTEGER (X.690 ยง8.4)
        - Primitive encoding (constructed form not used)
        - IEC 61334-6 ยง6.4: DLMS ENUMERATED range 0..255 (1 byte)

    Note:
        - Enumeration indices assigned per X.680 ยง19.3
        - Root enumeration: indices start at 0
        - Extension additions: indices continue from root
    """
    # Cached BER tag instance (primitive form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.Enumerated,
        constructed=False
    )

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode ENUMERATED from BER (X.690 ยง8.4)
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
        return cls.new(index)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode ENUMERATED to BER primitive form (X.690 ยง8.4)
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


class IntegerType(ImplicitTaggedType, x680.IntegerType):
    """
    INTEGER with BER encoding/decoding (X.690 ยง8.3)

    BER encoding structure (primitive form):
        [Tag=0x02] [Length] [Content]

    Content:
        - Two's complement binary number (X.690 ยง8.3.3)
        - Minimal octets required (X.690 ยง8.3.2)
        - No leading zero bytes except for sign

    Standards:
        - Tag: UNIVERSAL 2 (X.680 ยง18.8, X.690 ยง8.3)
        - Primitive encoding (constructed form not used)
        - A-XDR: Fixed-length for constrained types (IEC 61334-6 ยง6.1)

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
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode INTEGER from BER (X.690 ยง8.3)
        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value < 0:
            return Error.from_e(ValueError("Indefinite length form not supported for INTEGER"))
        if length.value == 0:
            return Error.from_e(ValueError("INTEGER length must be >= 1"))

        # Read content octets as big-endian two's complement
        if isinstance(content := buf.read(length.value), Error):
            return content
        value = int.from_bytes(content, byteorder="big", signed=True)
        return cls.new(value)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode INTEGER to BER primitive form (X.690 ยง8.3)
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


class NullType(ImplicitTaggedType, x680.NullType):
    """
    NULL with BER encoding/decoding (X.690 ยง8.8)
    BER encoding structure (primitive form):
        [Tag=0x05] [Length=0x00] [Contents=<empty>]

    Standards:
        - Tag: UNIVERSAL 5 (X.680 ยง23.2, X.690 ยง8.8)
        - Primitive encoding (constructed form not used)
        - Length: always 0 octets (X.690 ยง8.8.2)
        - Contents: empty (no octets)

    Note:
        - NULL has only one value (the null value)
        - Used to indicate absence of information or as placeholder
        - IEC 61334-6: NULL encoding same as BER (ยง6.13)
    """
    # Cached BER tag instance (primitive form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.Null,
        constructed=False
    )

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode NULL from BER (X.690 ยง8.8)
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
        Encode NULL to BER primitive form (X.690 ยง8.8)
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


class ObjectIdentifierType(ImplicitTaggedType, x680.ObjectIdentifierType):
    """
    OBJECT IDENTIFIER with BER encoding/decoding (X.690 ยง8.19).

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
        - X.690 ยง8.19: Encoding of an object identifier value
        - X.680 ยง31: Notation for the object identifier type
        - ITU-T X.660 | ISO/IEC 9834-1: OID registration procedures
    """

    # Cached BER tag instance (primitive form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.ObjectIdentifier,
        constructed=False
    )
    value: OBJECT_IDENTIFIER

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode OBJECT IDENTIFIER contents only (no tag validation).

        Used for:
            - CHOICE alternatives (X.690 ยง8.13)
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
        return cls.new(tuple(arcs))

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode OBJECT IDENTIFIER contents only (no tag).

        Used for:
            - CHOICE alternatives (X.690 ยง8.13)
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
        return put_lc(buf, len(content_bytes), bytes(content_bytes))


class OctetStringType(ImplicitTaggedType, x680.OctetStringType):
    """
    OCTET STRING with BER encoding/decoding (X.690 ยง8.7)

    BER encoding structure (primitive form):
        [Tag=0x04] [Length] [Contents(N)]

    Standards:
        - Tag: UNIVERSAL 4 (X.680 ยง22.2, X.690 ยง8.7)
        - Primitive encoding (constructed form optional)
        - Contents: raw octets (no unused bits like BIT STRING)
        - A-XDR: same as BER for variable-length (IEC 61334-6 ยง6.5)

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
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode OCTET STRING from BER (X.690 ยง8.7)
        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value < 0:
            return Error.from_e(ValueError("Indefinite length form not supported for OCTET STRING primitive"))
        # Read octets directly (no unused_bits like BIT STRING)
        # if length.value == 0:
        #     return cls.new(b"")
        if isinstance(data := buf.read(length.value), Error):
            return data
        return cls.new(bytes(data))

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode OCTET STRING to BER primitive form (X.690 ยง8.7.2)
        Returns number of bytes written.

        Content encoding:
            - Direct octet content (no padding)
            - No unused_bits octet (unlike BIT STRING)
        """
        return put_lc(buf, len(self.value), self.value)


class SequenceType(ImplicitTaggedType, x680.SequenceType):
    """
    SEQUENCE with BER encoding/decoding (X.690 ยง8.9)

    BER encoding structure (constructed form):
        [Tag=0x30] [Length] [Component1] [Component2] ... [ComponentN]

    Standards:
        - Tag: UNIVERSAL 16 (X.680 ยง24.16, X.690 ยง8.9)
        - Constructed encoding (always, X.690 ยง8.9.1)
        - Components encoded in definition order (X.690 ยง8.9.2)
        - OPTIONAL/DEFAULT components may be absent (X.690 ยง8.9.3)
        - IEC 61334-6 ยง6.9: SEQUENCE component tags NOT encoded
    """
    # Cached BER tag instance (constructed form)
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.Sequence,
        constructed=True
    )
    components: ClassVar[tuple[NamedType, ...]]

    def __init_subclass__(cls) -> None:
        """create <components> from annotations"""
        cls._init_sequence_components()

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode SEQUENCE from BER (X.690 ยง8.9)
        Returns instance and advances buffer position.
        """
        if isinstance(length := Length.get(buf), Error):
            return length
        if length.value < 0:
            return Error.from_e(ValueError("Indefinite length form not supported for SEQUENCE"))
        # Read all component encodings within the length
        start_pos = buf.get_pos()
        components_data: dict[str, Optional[TaggedType]] = {}
        for n_t in cls.components:
            if buf.get_pos() - start_pos >= length.value:  # Component is absent (OPTIONAL or DEFAULT)
                components_data[n_t.identifier] = None
                continue
            # Decode the component using its own get() method. This handles tag, length, and contents for each component
            if isinstance(value := n_t.type_.get(buf), Error):
                if value.has(exception_type=TagError):
                    if isinstance(n_t, x680.OptionalNamedType):
                        value = None
                    elif isinstance(n_t, x680.DefaultNamedType):
                        value = n_t.default
                    else:
                        return Error.from_e(ValueError(f"can't get {cls.__name__} from {buf}"))
                else:
                    return Error.from_e(RuntimeError(f"unknown exception {value}, can't get {cls.__name__} from {buf}"))
            components_data[n_t.identifier] = value
        return cls(**components_data)

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
        start_pos: int = buf.get_pos()
        sub_buf = buf.sub_buffer()
        if isinstance(err := buf.shift_pos(1), Error):
            return err
        for n_t in self.components:
            value = getattr(self, n_t.identifier)
            if (
                isinstance(n_t, x680.DefaultNamedType)
                and value == n_t.default
            ):
                continue
            if value is None:
                if isinstance(n_t, x680.OptionalNamedType):
                    continue
                return Error.from_e(ValueError(f"Required component <{n_t.identifier}> not set"))
            if isinstance(tmp := value.put(buf), Error):
                return tmp
            counter += tmp
        length = Length(counter)
        if (step := len(length) - 1) > 0:
            if isinstance(shift := buf.shift_right(start_pos + 1, counter, step), Error):
                return shift
            buf.set_pos(shift)
        if isinstance(err := length.put(sub_buf), Error):
            return err
        return buf.get_pos() - start_pos


class SequenceOfType[T: TaggedType](ImplicitTaggedType, x680.SequenceOfType[T]):
    """
    SEQUENCE OF with BER encoding/decoding (X.690 ยง8.10)
    BER encoding structure (constructed form):
        [Tag=0x30] [Length] [Component1] [Component2] ... [ComponentN]

    Standards:
        - Tag: UNIVERSAL 16 (X.680 ยง25.2, X.690 ยง8.10)
        - Constructed encoding (always, X.690 ยง8.10.1)
        - Components encoded in order of appearance (X.690 ยง8.10.3)
        - IEC 61334-6 ยง6.10: DLMS/COSEM SEQUENCE OF usage

    Note:
        - Each component is encoded using its own BER encoding rules
        - Length field covers all component encodings combined
        - Empty sequence: Length = 0, no component encodings
    """
    # Class variable: universal tag for SEQUENCE OF (constructed)
    # X.680 Table 1, X.690 ยง8.10.1: UNIVERSAL 16, constructed
    tag: ClassVar[Tag] = Tag(
        class_number=x680.UniversalClassTagAssignments.SequenceOf,
        constructed=True
    )
    _T: ClassVar[type[TaggedType]]

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode SEQUENCE OF from BER (X.690 ยง8.10)
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
            if isinstance(component := cast("T", cls._T.get(buf)), Error):
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
        start_pos: int = buf.get_pos()
        sub_buf = buf.sub_buffer()
        if isinstance(_ := buf.shift_pos(1), Error):
            return _
        for component in self.value:
            if isinstance(tmp := component.put(buf), Error):
                return tmp
            counter += tmp
        length = Length(counter)
        if (step := len(length) - 1) > 0:
            if isinstance(shift := buf.shift_right(start_pos + 1, counter, step), Error):
                return shift
            buf.set_pos(shift)
        if isinstance(err := length.put(sub_buf), Error):
            return err
        return buf.get_pos() - start_pos

    @property
    def is_empty(self) -> bool:
        """Check if sequence contains no components"""
        return len(self.value) == 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(component={self._T.__name__}, count={len(self.value)})"


class GeneralizedTime(ImplicitTaggedType, x680.GeneralizedTime):
    """GeneralizedTime with BER encoding (X.690 ยง8.23)"""
    tag: ClassVar[Tag] = Tag(class_number=UniversalClassTagAssignments.GeneralizedTime, constructed=False)

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """Decode GeneralizedTime from BER VisibleString"""
        if isinstance(length := Length.get(buf), Error):
            return length
        if isinstance(value := buf.read(length.value), Error):
            return value
        data = bytes(value).decode("ascii")
        return cls.new(data)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """Encode GeneralizedTime to BER VisibleString"""
        data = self.value.encode("ascii")
        return put_lc(buf, len(data), data)


class ConstrainedBitStringType(x680.ConstrainedBitStringType, BitStringType):
    def __init_subclass__(cls) -> None:
        cls._init_subclass()
        return super().__init_subclass__()
