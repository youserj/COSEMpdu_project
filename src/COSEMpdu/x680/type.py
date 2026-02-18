from typing import Self, TypeAlias, ClassVar, Protocol, runtime_checkable
from .tag import Tag
from ..byte_buffer import ByteBuffer

# Transcript represents minimal data needed for string parsing/reconstruction.
# Contains ONLY values (str or list of str), NO field names or structural metadata.
# Structural context (field names, types) is maintained by the concrete Type implementation.
Transcript: TypeAlias = str | list["Transcript"]



class ComponentEDV(Protocol):
    """
    Encoding Data Value component per X.690 §8.1.2
    
    Provides two levels of encoding interface:
    1. Full TLV: get()/put() - Tag + Length + Contents
    2. Contents only: get_contents()/put_contents() - Length + Contents only
    
    Used for:
    - Standard BER: use get()/put()
    - CHOICE alternatives: use get_contents()/put_contents()
    - SEQUENCE components in A-XDR: use get_contents()/put_contents()
    """
    
    def __len__(self) -> int:
        """Return octets required for full BER encoding (Tag + Length + Contents)"""
        ...
    
    @classmethod
    def get(cls, buf: ByteBuffer) -> Self:
        """
        Decode with full TLV (Tag + Length + Contents).
        MUST validate tag before decoding.
        """
        ...
    
    @classmethod
    def get_contents(cls, buf: ByteBuffer) -> Self:
        """
        Decode with Length + Contents ONLY (no Tag validation).
        
        Used for:
        - CHOICE alternatives (X.690 §8.13)
        - SEQUENCE components in A-XDR (IEC 61334-6 §6.9)
        - Explicitly tagged types where outer tag already validated
        """
        ...
    
    def put(self, buf: ByteBuffer) -> int:
        """
        Encode with full TLV (Tag + Length + Contents).
        Returns number of bytes written.
        """
        ...
    
    def put_contents(self, buf: ByteBuffer) -> int:
        """
        Encode with Length + Contents ONLY (no Tag).
        
        Used for:
        - CHOICE alternatives (X.690 §8.13)
        - SEQUENCE components in A-XDR (IEC 61334-6 §6.9)
        """
        ...


@runtime_checkable
class UType(ComponentEDV, Protocol):
    """
    Base protocol for ASN.1 types without encoding-specific metadata.
    
    Defines the interface for:
    - Parsing from human-readable representation (Transcript)
    - Serializing to human-readable representation (Transcript)
    - String representation for debugging
    
    Does NOT include encoding methods (A-XDR/BER) - those remain in Type subclasses.
    """
    
    @classmethod
    def parse(cls, value: Transcript) -> Self:
        """
        Construct instance from transcript representation.
        
        Args:
            value: String or list representation of the value
            
        Returns:
            Type instance with the value
            
        Raises:
            ValueError: If the value does not match the type
        """
        ...
    
    def to_transcript(self) -> Transcript:
        """
        Convert instance to transcript representation.
        
        Returns:
            String or list representation of the value
            
        Note:
            Result contains no structural metadata (field names, etc.)
        """
        ...
    
    def __str__(self) -> str:
        """
        Human-readable string representation for debugging.
        
        Returns:
            String representation of the value
        """
        ...


@runtime_checkable
class Type(UType, Protocol):
    """
    Base protocol for ASN.1 types with A-XDR/BER encoding support.
    
    IMPORTANT DESIGN NOTES:

    1. TAG SEMANTICS (IEC 61334-6:2000 §5.1, §6.6, §6.7):
       - tag attribute represents the ASN.1 universal tag (e.g., INTEGER=2)
       - A-XDR does NOT systematically encode tags:
         * CHOICE alternatives: ALWAYS encode raw tag number (1 byte)
         * ASN.1 explicit tags ([APPLICATION x]): encode in BER format
         * SEQUENCE components: NEVER encode tags (even if explicitly tagged)
         * Base constrained types (INTEGER(0..255)): NEVER encode tags

    2. BER ENCODING:
       - Systematically encodes tags (TLV structure)
       - Used for EXTERNAL, EMBEDDED PDV, ASN.1 explicit tags

    3. TRANSCRIPT USAGE:
       - Used ONLY for human-readable value representation/parsing
       - Contains pure data values (str/list[str]), NO structural metadata
       - Field names and type context are handled by container types (SEQUENCE, etc.)
    """
    
    tag: ClassVar[Tag]
    """ASN.1 universal tag (e.g., INTEGER=Tag(TagClass.UNIVERSAL, 2))"""

    @classmethod
    def get(cls, buf: ByteBuffer) -> Self:
        """Decode with Tag + Length + Contents"""
        cls.tag.validate(buf)  # Validate tag first
        return cls.get_contents(buf)  # Then decode length + contents

    def put(self, buf: ByteBuffer) -> int:
        """Encode with Tag + Length + Contents"""
        return self.tag.put(buf) + self.put_contents(buf)


class BuiltinType(Type, Protocol):
    """Built-in ASN.1 types per X.680 §16.2 (BOOLEAN, INTEGER, etc.)"""


class ReferencedType(Type, Protocol):
    """Referenced types per X.680 §16.3"""


class ConstrainedType(Type, Protocol):
    """Constrained types per X.680 §45"""
