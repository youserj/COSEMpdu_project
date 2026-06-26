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
from typing import ClassVar, Self, Optional, cast, TypeAlias, Annotated, Iterator, get_args
from StructResult.result import ValueOrError, Error
from . import x690
from .x680 import OptionalNamedType, DefaultNamedType, INTEGER, SEQUENCE_OF
from . import x680
from .byte_buffer import ByteBuffer, ReadableByteBuffer, U8Putter, RawPutter


# =============================================================================
# Helper Functions
# =============================================================================

def get_length(buf: ReadableByteBuffer) -> ValueOrError[int]:
    """
    Decode variable-length integer per IEC 61334-6 §6.1.2.

    Returns:
        Decoded integer value
    """
    if isinstance(first := buf.get_u8(), Error):
        return first
    if not (first & 0x80):
        # Short form: bits 7-1 = value (0-127)
        return first
    # Long form: bits 7-1 = number of value bytes
    num_bytes = first & 0x7F
    if num_bytes == 0:
        return Error.from_e(ValueError("Invalid variable-length integer encoding"))
    return buf.get_uint(num_bytes)


class Type(x680.Type, x690.EDTLV):
    @classmethod
    def get(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """Decode with Length + Contents"""
        return cls.get_lc(buf)  # Then decode length + contents

    def put(self, buf: ByteBuffer) -> ValueOrError[int]:
        """Encode with Length + Contents"""
        return self.put_lc(buf)


TagNumber: TypeAlias = Annotated[int, "0-255"]


class ImplicitTaggedType(Type):
    """
    Mixin for COSEM Data types with tag-prefixed A-XDR encoding
    (IEC 61334-6 §6.7).

    Provides ``get`` / ``put`` methods that verify and encode a single
    tag byte, then delegate to the concrete type's ``get_lc`` / ``put_lc``
    for the actual A-XDR content.

    Usage::
        class NullData(DataType, NullType):
            tag = 0

        class Boolean(DataType, BooleanType):
            tag = 3

    In the MRO, ``DataType`` (first parent) handles the tag layer;
    the second parent (e.g. ``BooleanType``, ``NullType``) provides
    ``get_lc`` / ``put_lc`` for content encoding/decoding.
    """
    tag: ClassVar[int]

    @classmethod
    def get(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """IMPLICIT mode (§6.6):
                [Tag(1)] [Contents without inner tag]
        """
        if isinstance(tag_number := buf.get_u8(), Error):
            return tag_number
        if tag_number != cls.tag:
            return Error.from_e(x690.TagError(f"expected tag {cls.tag}, got {tag_number}"))
        return cls.get_lc(buf)

    def put(self, buf: ByteBuffer) -> ValueOrError[int]:
        return buf.put_chain(
            U8Putter(self.tag).put,
            self.put_lc
        )


# =============================================================================
# BOOLEAN Type (IEC 61334-6 §6.2)
# =============================================================================


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
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode BOOLEAN from A-XDR (IEC 61334-6 §6.2)

        Returns instance and advances buffer position.
        """
        # Single octet, no tag/length
        if isinstance(content := buf.get_u8(), Error):
            return content
        return cls.new(content)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode BOOLEAN to A-XDR (IEC 61334-6 §6.2)

        Returns number of bytes written (always 1).

        Content encoding:
            FALSE → 0x00
            TRUE  → 0xFF
        """
        return buf.put_u8(self.value)


# =============================================================================
# INTEGER Type (IEC 61334-6 §6.1)
# =============================================================================

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
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """Variable-length encoding (§6.1.2)"""
        if isinstance(first := buf.get_u8(), Error):
            return first
        if not (first & 0x80):
            # Short form: 0-127
            return cls.new(first)
        # Long form: length octet + value octets
        length = first & 0x7F
        return cls.get_c(buf, length)

    @classmethod
    def get_c(cls, buf: ReadableByteBuffer, length: int) -> ValueOrError[Self]:
        if isinstance(content := buf.read(length), Error):
            return content
        # Decode as two's complement
        value = int.from_bytes(content, byteorder="big", signed=True)
        return cls.new(value)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """Variable-length encoding"""
        if 0 <= self.value <= 127:
            return buf.put_u8(self.value)
        num_bytes = (self.value.bit_length() + 7) // 8  # Calculate bytes needed for value
        return buf.put_chain(
            U8Putter(0x80 | num_bytes).put,  # Length octet: bit 8 = 1, bits 7-1 = number of value bytes
            RawPutter(self.value.to_bytes(num_bytes, byteorder="big")).put
        )


# =============================================================================
# BIT STRING Type (IEC 61334-6 §6.4)
# =============================================================================

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
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        if isinstance(num_bits := get_length(buf), Error):
            return num_bits
        if num_bits == 0:
            return cls.new(())
        return cls.get_c(buf, num_bits)

    @classmethod
    def get_c(cls, buf: ReadableByteBuffer, length: int) -> ValueOrError[Self]:
        bits: list[int] = []
        num_octets = (length + 7) // 8
        if isinstance(data := buf.read(num_octets), Error):
            return data
        for byte in data:
            for i in range(8):
                bits.append(1 if (byte & (1 << (7 - i))) else 0)
        bits = bits[:length]  # Trim to exact bit length
        return cls.new(tuple(bits))

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        n = len(self.value)
        if n == 0:
            # Length = 0 bits
            return buf.put_u8(0)
        # Encode length (number of BITS)
        return buf.put_chain(
            x690.Length(len(self.value)).put,
            self.put_c
        )

    def put_c(self, buf: ByteBuffer) -> ValueOrError[int]:
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
        return buf.write(data_bytes)


# =============================================================================
# OCTET STRING Type (IEC 61334-6 §6.5)
# =============================================================================

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
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        if isinstance(num_octets := get_length(buf), Error):
            return num_octets
        return cls.get_c(buf, num_octets)

    @classmethod
    def get_c(cls, buf: ReadableByteBuffer, length: int) -> ValueOrError[Self]:
        """decode content"""
        if isinstance(data := buf.read(length), Error):
            return data
        return cls.new(bytes(data))

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        return buf.put_chain(
            x690.Length(len(self.value)).put,
            self.put_c
        )

    def put_c(self, buf: ByteBuffer) -> ValueOrError[int]:
        return buf.write(self.value)


class VisibleString(Type, x680.VisibleString):

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        # Variable-length encoding (§6.5.2) only
        if isinstance(num_octets := get_length(buf), Error):
            return num_octets
        if isinstance(data := buf.read(num_octets), Error):
            return data
        return cls.new(data.decode(encoding="ascii"))

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        return buf.put_chain(
            x690.Length(len(self.value)).put,
            RawPutter(self.value.encode("ascii")).put
        )

    def __str__(self) -> str:
        return repr(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


class Utf8String(Type, x680.VisibleString):  # todo: copypast VisibleString

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        if isinstance(num_octets := get_length(buf), Error):
            return num_octets
        if isinstance(data := buf.read(num_octets), Error):
            return data
        return cls.new(data.decode(encoding="utf-8"))

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        return buf.put_chain(
            x690.Length(len(encode := self.value.encode("utf-8"))).put,
            RawPutter(encode).put
        )

    def __str__(self) -> str:
        return repr(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


# =============================================================================
# CHOICE Type (IEC 61334-6 §6.6)
# =============================================================================
Alternatives: TypeAlias = dict[int, "ImplicitTaggedType | ChoiceType"]


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
    alternatives: Alternatives
    value: ImplicitTaggedType

    def __init_subclass__(cls) -> None:
        if (
            not hasattr(cls, "alternatives")
            and (values := cls.__annotations__.get("value"))
        ):
            cls.alternatives = {type_.tag: type_ for type_ in get_args(values)}

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode CHOICE from A-XDR (IEC 61334-6 §6.6)

        Returns instance with chosen alternative and advances buffer position.
        """
        if isinstance(tag := buf.get_u8(), Error):
            return tag
        return cls.get_c(buf, tag)

    @classmethod
    def get_c(cls, buf: ReadableByteBuffer, tag: int) -> ValueOrError[Self]:
        if (t_ := cls.alternatives.get(tag)) is None:
            return Error.from_e(ValueError(f"{tag} not in alternatives: {", ".join((t_.__name__ for t_ in cls.alternatives.values()))}"))
        if isinstance(value := t_.get_lc(buf), Error):
            return value
        return cls(value)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode CHOICE to A-XDR (IEC 61334-6 §6.6)

        Returns number of bytes written.
        """
        return self.value.put(buf)


# =============================================================================
# SEQUENCE Type (IEC 61334-6 §6.9)
# =============================================================================

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
    components: ClassVar[tuple[x680.NamedType[Type], ...]]

    def __init_subclass__(cls) -> None:
        """create <components> from annotations"""
        cls._init_sequence_components()

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode SEQUENCE from A-XDR (IEC 61334-6 §6.9)

        Returns instance and advances buffer position.
        """
        components_data: dict[str, Optional[Type]] = {}
        for n_t in cls.components:
            # Check for OPTIONAL/DEFAULT presence flag
            if isinstance(n_t, (OptionalNamedType, DefaultNamedType)):
                if isinstance(presence_flag := buf.get_u8(), Error):
                    return presence_flag
                if presence_flag == 0:  # Component absent
                    if isinstance(n_t, x680.DefaultNamedType):
                        components_data[n_t.identifier] = n_t.default
                    else:
                        components_data[n_t.identifier] = None
                    continue
            # Decode the component using its A-XDR get_contents()
            if isinstance(value := n_t.type_.get_lc(buf), Error):
                return value
            components_data[n_t.identifier] = value
        return cls(**components_data)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode SEQUENCE to A-XDR (IEC 61334-6 §6.9)

        Returns number of bytes written.
        """
        written = 0
        for n_t in self.components:
            value = getattr(self, n_t.identifier)
            # Handle OPTIONAL/DEFAULT with presence flag
            if isinstance(n_t, (OptionalNamedType, DefaultNamedType)):
                if (
                    value is None
                    or (
                        isinstance(n_t, DefaultNamedType)
                        and value == n_t.default
                )):
                    if isinstance(tmp := buf.put_u8(0), Error):  # Component absent
                        return tmp
                    written += tmp
                    continue
                if isinstance(tmp := buf.put_u8(1), Error):  # Component present
                    return tmp
                written += tmp
            # if not isinstance(value, n_t.type_):
            #     return Error.from_e(TypeError(f"got {value} in Required component <{n_t.identifier}>, expected {n_t.type_}"))
            if isinstance(tmp := value.put_lc(buf), Error):  # Component present
                return tmp
            written += tmp  # Encode component contents (no tag/length)
        return written


ENUM_VALUE: TypeAlias = Annotated[INTEGER, "0-255"]


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
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode ENUMERATED from A-XDR (IEC 61334-6 §6.3)

        Returns instance and advances buffer position.
        """
        # Single octet, no tag/length
        if isinstance(index := buf.get_u8(), Error):
            return index
        return cls.new(index)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode ENUMERATED to A-XDR (IEC 61334-6 §6.3)

        Returns number of bytes written (always 1).
        """
        return buf.put_u8(self.value)


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
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:  # noqa: ARG003
        """
        Decode NULL from A-XDR (IEC 61334-6 §6.13)

        Returns instance (no bytes consumed in SEQUENCE).
        """
        # NULL has no content in SEQUENCE components
        return cls(None)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:  # noqa: ARG002
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
        return isinstance(other, self.__class__)


class NullType0(ImplicitTaggedType, NullType):
    """[0] IMPLICIT NULL"""
    tag = 0


null = NullType(None)


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
    value: SEQUENCE_OF[T]

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode SEQUENCE OF from A-XDR (IEC 61334-6 §6.10)

        Args:
            fixed_length: Number of components (None for variable-length)

        Returns instance and advances buffer position.
        """
        if isinstance(num_components := get_length(buf), Error):
            return num_components
        return cls.get_c(buf, num_components)

    @classmethod
    def get_c(cls, buf: ReadableByteBuffer, length: int) -> ValueOrError[Self]:
        components: list[T] = []
        for _ in range(length):
            if isinstance(component := cast("T", cls._T.get(buf)), Error):
                return component
            components.append(component)
        return cls(components)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode SEQUENCE OF to A-XDR (IEC 61334-6 §6.10)

        Returns number of bytes written.
        """
        # Variable-length encoding (§6.10.2)
        return buf.put_chain(
            x690.Length(len(self.value)).put,
            self.put_c
        )

    def put_c(self, buf: ByteBuffer) -> ValueOrError[int]:
        return buf.put_chain(*(comp.put for comp in self.value))

    def __iter__(self) -> Iterator[T]:
        for val in self.value:
            yield val

    @property
    def is_empty(self) -> bool:
        """Check if sequence contains no components"""
        return len(self.value) == 0


class ObjectIdentifierType(Type, x680.ObjectIdentifierType):
    """
    OBJECT IDENTIFIER with A-XDR encoding/decoding (IEC 61334-6)

    A-XDR encoding structure:
        [Length(1+)] [Content(N)]  # NO tag, NO length in content

    Content:
        - BER base-128 variable-length subidentifiers (X.690 §8.19)

    Standards:
        - IEC 61334-6 §6.5 (applied as variable-length byte string)
        - X.690 §8.19 (BER OID content encoding)
        - X.680 §31 (OBJECT IDENTIFIER type definition)

    Note:
        - DLMS uses for Application-context-name, Mechanism-name, etc.
        - A-XDR omits BER tag (0x06), keeping only A-XDR var-length + BER content.
    """

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        # 1. Decode A-XDR variable-length integer for content length
        if isinstance(num_octets := get_length(buf), Error):
            return num_octets
        if num_octets == 0:
            return cls(())
        # 2. Read raw OID content octets
        if isinstance(data := buf.read(num_octets), Error):
            return data
        content = bytes(data)
        arcs: list[int] = []
        # 3. Decode first octet per X.690 §8.19.4
        # arc0 is strictly restricted to {0, 1, 2}. arc1 can be any >=0 integer.
        first = content[0]
        if first < 40:
            arcs.extend([0, first])
        elif first < 80:
            arcs.extend([1, first - 40])
        else:
            arcs.extend([2, first - 80])
        # 4. Decode remaining subidentifiers (base-128)
        pos = 1
        while pos < len(content):
            arc_value = 0
            while True:
                if pos >= len(content):
                    return Error.from_e(ValueError("Truncated OBJECT IDENTIFIER encoding"))
                octet = content[pos]
                pos += 1
                arc_value = (arc_value << 7) | (octet & 0x7F)
                if not (octet & 0x80):
                    break
            arcs.append(arc_value)
        return cls.new(tuple(arcs))

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        content = bytearray()
        # Encode first two arcs into single octet
        content.append(self.value[0] * 40 + self.value[1])
        # Encode remaining arcs using base-128 variable-length
        for arc in self.value[2:]:
            if arc == 0:
                content.append(0x00)
            else:
                arc_bits = arc.bit_length()
                num_octets = (arc_bits + 6) // 7
                chunks: list[int] = []
                val = arc
                for _ in range(num_octets):
                    chunks.append(val & 0x7F)
                    val >>= 7
                chunks.reverse()
                # Set continuation bit (0x80) on all but last octet
                for i in range(len(chunks) - 1):
                    chunks[i] |= 0x80
                content.extend(chunks)
        # Write A-XDR variable-length header + BER OID content
        return buf.put_chain(
            x690.Length(len(content)).put,
            RawPutter(content).put
        )


class GeneralizedTime(Type, x680.GeneralizedTime):

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        if isinstance(length := get_length(buf), Error):
            return length
        if isinstance(data := buf.read(length), Error):
            return data
        return cls.new(data.decode("ascii"))

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        data = self.value.encode("ascii")
        return buf.put_chain(
            x690.Length(len(data)).put,
            RawPutter(data).put
        )


class ConstrainedIntegerType(x680.ConstrainedIntegerType, IntegerType):

    @classmethod
    def __init_subclass__(cls) -> None:
        cls._init_subclass()

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        """
        Decode INTEGER from A-XDR (IEC 61334-6 §6.1.1)

        Args:
            fixed_length: Number of octets (None for variable-length)

        Returns instance and advances buffer position.
        """
        if isinstance(cls.fixed_length, int):
            if isinstance(content := buf.read(cls.fixed_length), Error):
                return content
            # Decode as unsigned for non-negative, signed for negative ranges
            # DLMS typically uses unsigned for constrained types
            value = int.from_bytes(content, byteorder="big", signed=cls.signed)
            return cls.new(value)
        return super().get_lc(buf)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        """
        Encode INTEGER to A-XDR (IEC 61334-6 §6.1)

        Returns number of bytes written.
        """
        if isinstance(self.fixed_length, int):
            if self.fixed_length == 0:
                return 0
            content_bytes = self.value.to_bytes(
                self.fixed_length,
                byteorder="big",
                signed=self.signed
            )
            return buf.write(content_bytes)
        return super().put_lc(buf)


class ConstrainedOctetStringType(x680.ConstrainedOctetString, OctetStringType):

    @classmethod
    def __init_subclass__(cls) -> None:
        cls._init_subclass()

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:
        if isinstance(cls.fixed_length, int):
            return cls.get_c(buf, cls.fixed_length)
        return cls.get_lc(buf)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        if isinstance(self.fixed_length, int):
            return self.put_c(buf)
        return self.put_lc(buf)


class ConstrainedBitStringType(x680.ConstrainedBitStringType, BitStringType):

    def __init_subclass__(cls) -> None:
        cls._init_subclass()
        return super().__init_subclass__()

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:  # copypast from other
        if isinstance(cls.fixed_length, int):
            return cls.get_c(buf, cls.fixed_length)
        return cls.get_lc(buf)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        if isinstance(self.fixed_length, int):
            return self.put_c(buf)
        return self.put_lc(buf)

    @classmethod
    def from_bits(cls, *bits: int) -> Self:
        """Create with bits set at given positions: (0, 3, 5) -> bits 0,3,5 = 1, rest 0"""
        if not bits:
            return cls.default()
        result = list(cls.default().value) if cls.fixed_length else [0] * (max(bits) + 1)
        for pos in bits:
            result[pos] = 1
        return cls(tuple(result))


class ConstrainedSequenceOfType[T: SequenceOfType[Type]](x680.ConstrainedSequenceOfType[T], SequenceOfType[T]):
    @classmethod
    def __init_subclass__(cls) -> None:
        cls._init_subclass()

    @classmethod
    def get_lc(cls, buf: ReadableByteBuffer) -> ValueOrError[Self]:  # copypast from other
        if isinstance(cls.fixed_length, int):
            return cls.get_c(buf, cls.fixed_length)
        return cls.get_lc(buf)

    def put_lc(self, buf: ByteBuffer) -> ValueOrError[int]:
        if isinstance(self.fixed_length, int):
            return self.put_c(buf)
        return self.put_lc(buf)
