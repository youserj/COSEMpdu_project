# src/COSEMpdu/x690/bit_string.py
from dataclasses import dataclass
from typing import ClassVar, Self, Iterator
from . import x680
from .byte_buffer import ByteBuffer
from .x690 import Tag, Length


@dataclass
class BitStringType(x680.BitStringType):
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
    def get_contents(cls, buf: ByteBuffer) -> Self:
        """
        Decode BIT STRING from BER (X.690 §8.6)
        Returns instance and advances buffer position.
        """
        length = Length.get(buf)
        if length.value < 0:
            raise ValueError("Indefinite length form not supported for BIT STRING primitive")
        # Empty bitstring: length = 0
        if length.value == 0:
            return cls(())
        # First octet: unused bits count (0-7)
        unused_bits = buf.get_uint8()
        if not (0 <= unused_bits <= 7):
            raise ValueError(f"Invalid unused bits count: {unused_bits}")
        # Remaining octets: bitstring contents
        data_length = length.value - 1
        if data_length < 0:
            raise ValueError("BIT STRING length too small (missing unused bits octet)")
        # Read all data bytes at once
        data_view = buf.read(data_length)
        # Extract bits MSB-first (bit 8 to bit 1 per octet)
        bits: list[int] = []
        for byte in data_view:
            for i in range(8):
                bits.append(1 if (byte & (1 << (7 - i))) else 0)
        # Remove unused trailing bits
        if unused_bits > 0:
            bits = bits[:-unused_bits]
        return cls(tuple(bits))

    def put_contents(self, buf: ByteBuffer) -> int:
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
        # Write: tag + length + unused_bits + data
        return Length(1 + len(data_bytes)).put(buf) + buf.put_uint8(unused_bits) + buf.write(bytes(data_bytes))

    def __len__(self) -> int:
        """
        Return octets required for BER encoding (X.690 §8.6.2)
        """
        n = len(self.value)
        padded_length = (n + 7) // 8
        return 1 + len(Length(1 + padded_length)) + 1 + padded_length


@dataclass
class BooleanType(x680.BooleanType):
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
    def get_contents(cls, buf: ByteBuffer) -> Self:
        """
        Decode BOOLEAN from BER (X.690 §8.2)
        Returns instance and advances buffer position.
        """
        length = Length.get(buf)
        if length.value != 1:
            raise ValueError(f"BOOLEAN length must be 1, got {length.value}")
        content = buf.get_uint8()
        return cls(content != 0)

    def put_contents(self, buf: ByteBuffer) -> int:
        """
        Encode BOOLEAN to BER (X.690 §8.2.2)
        Returns number of bytes written (always 3).
        
        Content encoding:
            FALSE → 0x00
            TRUE  → 0xFF (all bits one, DER/CER compliant)
        """
        # Write: tag + length(1) + content
        return Length(1).put(buf) + buf.put_uint8(0xFF if self.value else 0x00)
        
    def __len__(self) -> int:
        """
        Return octets required for BER encoding (X.690 §8.2)
        Always 3 bytes: Tag(1) + Length(1) + Content(1)
        """
        return 3


class ChoiceType(x680.ChoiceType):
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
    
    # Class variable: defines available alternatives for this CHOICE type
    alternatives: ClassVar[dict[int, type[x680.Type]]]
    
    @classmethod
    def get(cls, buf: ByteBuffer) -> Self:
        """
        Decode CHOICE from BER (X.690 §8.13)
        Returns instance with chosen alternative and advances buffer position.
        """
        # Peek at tag to determine which alternative was chosen
        tag_byte = buf.get_uint8()
        
        # Extract tag number from identifier octet (bits 5-1 for tag < 31)
        # For CHOICE alternatives in DLMS, tag is typically context-specific 0-30
        tag_number = tag_byte & 0x1F
        
        # Find the alternative type for this tag
        if tag_number not in cls.alternatives:
            raise ValueError(
                f"CHOICE tag {tag_number} not in alternatives: "
                f"{list(cls.alternatives.keys())}"
            )
        
        alternative_type = cls.alternatives[tag_number]
        
        # Decode the alternative value using its own get() method
        # This will consume the tag, length, and contents
        value = alternative_type.get_contents(buf)
        
        return cls(
            selected_tag=tag_number,
            value=value,
            class_=x680.Class.CONTEXT_SPECIFIC
        )
    
    @classmethod
    def get_contents(cls, buf: ByteBuffer) -> Self:
        return cls.get(buf)

    def put(self, buf: ByteBuffer) -> int:
        """
        Encode CHOICE to BER (X.690 §8.13)
        Returns number of bytes written.
        
        Encoding is identical to the chosen alternative type.
        """
        # Verify the selected tag is valid for this CHOICE
        if self.selected_tag not in self.alternatives:
            raise ValueError(
                f"Tag {self.selected_tag} not in alternatives: "
                f"{list(self.alternatives.keys())}"
            )
        return Tag(
            self.selected_tag, 
            x680.Class.CONTEXT_SPECIFIC,
            constructed=self.value.tag.constructed if isinstance(self.value, x680.Type) else False
        ).put(buf) + self.value.put_contents(buf)
    
    def put_contents(self, buf: ByteBuffer) -> int:
        return self.put(buf)
    
    def __len__(self) -> int:
        """
        Return octets required for BER encoding (X.690 §8.13)
        Same as the chosen alternative type.
        """
        return len(self.value)


@dataclass
class EnumeratedType(x680.EnumeratedType):
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
    def get_contents(cls, buf: ByteBuffer) -> Self:
        """
        Decode ENUMERATED from BER (X.690 §8.4)
        Returns instance and advances buffer position.
        """
        length = Length.get(buf)
        if length.value < 0:
            raise ValueError("Indefinite length form not supported for ENUMERATED")
        if length.value == 0:
            raise ValueError("ENUMERATED length must be >= 1")
        # Read enumeration index as signed integer (two's complement)
        index = buf.get_uint(length.value)
        # Convert to signed if high bit is set
        if index & (1 << (length.value * 8 - 1)):
            index -= (1 << (length.value * 8))
        return cls(index)
    
    def put_contents(self, buf: ByteBuffer) -> int:
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
        content_bytes = value.to_bytes(num_bytes, byteorder='big')
        return Length(num_bytes).put(buf) + buf.write(content_bytes)
    
    def __len__(self) -> int:
        """
        Return octets required for BER encoding (X.690 §8.4)
        """
        # Calculate minimal bytes for enumeration index
        if self.value < 0:
            num_bytes = (self.value.bit_length() // 8) + 1
        else:
            num_bytes = max(1, (self.value.bit_length() + 7) // 8)
            # Check if sign bit would be set
            if self.value & (1 << (num_bytes * 8 - 1)):
                num_bytes += 1
        return 1 + len(Length(num_bytes)) + num_bytes


@dataclass
class IntegerType(x680.IntegerType):
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
    def get_contents(cls, buf: ByteBuffer) -> Self:
        """
        Decode INTEGER from BER (X.690 §8.3)
        Returns instance and advances buffer position.
        """
        length = Length.get(buf)
        if length.value < 0:
            raise ValueError("Indefinite length form not supported for INTEGER")
        if length.value == 0:
            raise ValueError("INTEGER length must be >= 1")
        
        # Read content octets as big-endian two's complement
        content = buf.read(length.value)
        value = int.from_bytes(content, byteorder='big', signed=True)
        return cls(value)
    
    def put_contents(self, buf: ByteBuffer) -> int:
        """
        Encode INTEGER to BER primitive form (X.690 §8.3)
        Returns number of bytes written.
        
        Content encoding:
            - Two's complement binary (minimal octets)
            - No leading zero bytes except for sign
        """
        # Calculate minimal bytes needed for two's complement
        if self.value == 0:
            content_bytes = bytes([0x00])
        else:
            # Calculate bit length for minimal representation
            bit_length = self.value.bit_length()
            # Add 1 for sign bit, round up to full bytes
            num_bytes = (bit_length + 1 + 7) // 8
            
            # Convert to two's complement bytes
            content_bytes = self.value.to_bytes(num_bytes, byteorder='big', signed=True)
        return Length(len(content_bytes)).put(buf) + buf.write(content_bytes)
    
    def __len__(self) -> int:
        """
        Return octets required for BER encoding (X.690 §8.3)
        """
        # Calculate content length
        if self.value == 0:
            content_length = 1
        else:
            bit_length = self.value.bit_length()
            content_length = (bit_length + 1 + 7) // 8
        return 1 + len(Length(content_length)) + content_length
    

@dataclass(frozen=True)
class NullType(x680.NullType):
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
    
    def __post_init__(self) -> None:
        """Validate NULL has no value (always null)"""
        # NULL type has no instance value - it's a singleton type
        pass
    
    @classmethod
    def get_contents(cls, buf: ByteBuffer) -> Self:
        """
        Decode NULL from BER (X.690 §8.8)
        Returns instance and advances buffer position.
        """
        length = Length.get(buf)
        if length.value != 0:
            raise ValueError(f"NULL length must be 0, got {length.value}")
        # NULL has no contents - nothing to read
        return cls()
    
    def put_contents(self, buf: ByteBuffer) -> int:
        """
        Encode NULL to BER primitive form (X.690 §8.8)
        Returns number of bytes written (always 2).
        
        Encoding:
            Tag(1) + Length(1) + Contents(0) = 2 bytes
        """
        return Length(0).put(buf)
    
    def __len__(self) -> int:
        """
        Return octets required for BER encoding (X.690 §8.8)
        Always 2 bytes: Tag(1) + Length(1) + Contents(0)
        """
        return 2
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
    
    def __eq__(self, other: object) -> bool:
        """All NULL values are equal"""
        return isinstance(other, NullType)


@dataclass
class OctetStringType(x680.OctetStringType):
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
    def get_contents(cls, buf: ByteBuffer) -> Self:
        """
        Decode OCTET STRING from BER (X.690 §8.7)
        Returns instance and advances buffer position.
        """
        length = Length.get(buf)
        if length.value < 0:
            raise ValueError("Indefinite length form not supported for OCTET STRING primitive")
        # Read octets directly (no unused_bits like BIT STRING)
        if length.value == 0:
            return cls(b"")
        data = bytes(buf.read(length.value))
        return cls(data)
    
    def put_contents(self, buf: ByteBuffer) -> int:
        """
        Encode OCTET STRING to BER primitive form (X.690 §8.7.2)
        Returns number of bytes written.
        
        Content encoding:
            - Direct octet content (no padding)
            - No unused_bits octet (unlike BIT STRING)
        """
        data = bytes(self.value)
        return Length(len(data)).put(buf) + buf.write(data)
    
    def __len__(self) -> int:
        """
        Return octets required for BER encoding (X.690 §8.7)
        """
        data_length = len(self.value)
        return 1 + len(Length(data_length)) + data_length


@dataclass(frozen=True)
class SequenceType(x680.SequenceType):
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
    
    # Class variable: defines component types for this SEQUENCE
    components: ClassVar[dict[str, type[x680.UType]]]
    
    @classmethod
    def get_contents(cls, buf: ByteBuffer) -> Self:
        """
        Decode SEQUENCE from BER (X.690 §8.9)
        Returns instance and advances buffer position.
        """
        length = Length.get(buf)
        if length.value < 0:
            raise ValueError("Indefinite length form not supported for SEQUENCE")
        # Read all component encodings within the length
        start_pos = buf.get_pos()
        components_data: dict[str, type[x680.Type]] = {}
        for name, comp_type in cls.components.items():
            # Check if we've reached the end of the SEQUENCE contents
            if buf.get_pos() - start_pos >= length.value:
                # Component is absent (OPTIONAL or DEFAULT)
                components_data[name] = None
                continue
            # Decode the component using its own get() method
            # This handles tag, length, and contents for each component
            try:
                value = comp_type.get(buf)
                components_data[name] = value
            except ValueError:
                # Component is absent (OPTIONAL or DEFAULT)
                components_data[name] = None
        return cls(**components_data)
    
    def __iter__(self) -> Iterator[x680.UType]:
        for name in self.components.keys():
            value = getattr(self, name, None)
            if value is None:
                raise ValueError(f"not find component {name} in {self}")
            yield value

    def put_contents(self, buf: ByteBuffer) -> int:
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
        start: int = buf.shift_pos(1)
        for name in self.components.keys():
            value = getattr(self, name, None)
            if value is None:
                raise ValueError(f"not find component {name} in {self}")
            counter += value.put(buf)
        length = Length(counter)
        if (step := len(length)) > 1:
            end = buf.shift_right(start, counter, step)
        else:
            end = buf.get_pos()
        buf.set_pos(start)
        length.put(buf)
        buf.set_pos(end)
        return step + counter
    
    def __len__(self) -> int:
        """
        Return octets required for BER encoding (X.690 §8.9)
        """
        # Calculate total components length
        components_length = 0
        for name in self.components.keys():
            value = getattr(self, name, None)
            if value is not None:
                components_length += len(value)
        
        # Tag(1) + Length(1+) + Components(n)
        return 1 + len(Length(components_length)) + components_length