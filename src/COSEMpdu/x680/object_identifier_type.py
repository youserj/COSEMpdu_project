"""
ASN.1 OBJECT IDENTIFIER Type Definition (X.680 §31)
This module defines the abstract syntax for OBJECT IDENTIFIER types.
Encoding/decoding (BER) is handled separately in x690 module.

Standards:
- X.680 §31: OBJECT IDENTIFIER type definition
- X.690 §8.19: OBJECT IDENTIFIER encoding rules (handled in x690)
- X.680 Table 1: UNIVERSAL tag 6
"""
from typing import Self
from StructResult.result import Error, ValueOrError
from .type import OBJECT_IDENTIFIER, BuiltinType, Simple


class ObjectIdentifierType(Simple[OBJECT_IDENTIFIER], BuiltinType):
    """
    ASN.1 OBJECT IDENTIFIER type (X.680 §31).

    An OBJECT IDENTIFIER is a globally unique identifier assigned to objects
    using a hierarchical tree structure. Each node in the tree is assigned
    by a registration authority.
    Example ASN.1:
        iso OBJECT IDENTIFIER ::= {1}
        standard OBJECT IDENTIFIER ::= {iso 0}
        asn1 OBJECT IDENTIFIER ::= {standard 1}

        -- Full OID: {iso standard asn1} = {1 0 1}

    Attributes:
        value: Tuple of non-negative integers representing OID arcs
               First arc: 0 (itu-t), 1 (iso), 2 (joint-iso-itu-t)
               Second arc: 0-39 (if first arc is 0 or 1), 0+ (if first arc is 2)
               Subsequent arcs: 0+ (unlimited)

    Note:
        - Minimum 2 arcs required (X.680 §31.10)
        - Encoding/decoding is handled in x690 module (BER)
        - This class only describes the abstract syntax structure

    References:
        - X.680 §31: Notation for the object identifier type
        - X.680 Table 1: UNIVERSAL tag 6
        - ITU-T X.660 | ISO/IEC 9834-1: OID registration procedures
    """
    value: OBJECT_IDENTIFIER

    def __init__(self, value: OBJECT_IDENTIFIER) -> None:
        """
        Validate OBJECT IDENTIFIER structure per X.680 §31.10.
        Raises:
            ValueError: If OID has less than 2 arcs or invalid arc values
        """
        if len(value) < 2:
            raise ValueError(f"OBJECT IDENTIFIER must have at least 2 arcs, got {len(value)}")
        # Validate first arc (0, 1, or 2)
        if value[0] not in (0, 1, 2):
            raise ValueError(f"First arc must be 0, 1, or 2, got {value[0]}")
        # Validate second arc (0-39 if first arc is 0 or 1)
        if value[0] in (0, 1) and value[1] > 39:
            raise ValueError(f"Second arc must be 0-39 when first arc is {value[0]}, got {value[1]}")
        # Validate all arcs are non-negative
        for i, arc in enumerate(value):
            if arc < 0:
                raise ValueError(f"Arc {i} must be non-negative, got {arc}")
        self.value = value

    @classmethod
    def default(cls) -> Self:
        return cls((0, 0))  # Default to {0 0}, though this may be invalid

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns:
            Dotted decimal notation

        Example:
            >>> str(ObjectIdentifierType((1, 0, 1)))
            '1.0.1'
        """
        return ".".join(str(arc) for arc in self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"

    def __eq__(self, other: object) -> bool:
        """
        Compare OBJECT IDENTIFIERs for equality.

        Two OIDs are equal if and only if all arcs are identical.
        """
        if not isinstance(other, ObjectIdentifierType):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __lt__(self, other: object) -> bool:
        """
        Compare OBJECT IDENTIFIERs lexicographically.

        Used for sorting OIDs in canonical order.
        """
        if not isinstance(other, ObjectIdentifierType):
            return NotImplemented
        return self.value < other.value

    @property
    def root_arc(self) -> int:
        """Return the root arc (first component)."""
        return self.value[0]

    @property
    def is_iso(self) -> bool:
        """Check if OID is under ISO root {1}."""
        return self.root_arc == 1

    @property
    def is_itu_t(self) -> bool:
        """Check if OID is under ITU-T root {0}."""
        return self.root_arc == 0

    @property
    def is_joint(self) -> bool:
        """Check if OID is under joint-iso-itu-t root {2}."""
        return self.root_arc == 2

    def startswith(self, prefix: "ObjectIdentifierType") -> bool:
        """
        Check if this OID starts with the given prefix.

        Example:
            >>> oid = ObjectIdentifierType((1, 0, 1, 5, 1))
            >>> prefix = ObjectIdentifierType((1, 0, 1))
            >>> oid.startswith(prefix)
            True
        """
        if not isinstance(prefix, ObjectIdentifierType):
            raise TypeError("Prefix must be ObjectIdentifierType")
        return self.value[:len(prefix.value)] == prefix.value

    def parent(self) -> ValueOrError[Self]:
        """
        Return parent OID (all arcs except last).

        Returns:
            Parent OID or Error if this is a root arc

        Example:
            >>> ObjectIdentifierType((1, 0, 1)).parent()
            ObjectIdentifierType(value=(1, 0))
        """
        if len(self.value) <= 2:
            return Error.from_e(ValueError("parent must be at least with 2 values"))
        return self.__class__(self.value[:-1])

    def child(self, arc: int) -> Self:
        """
        Return child OID with additional arc.

        Args:
            arc: Non-negative integer arc to append

        Returns:
            New ObjectIdentifierType with appended arc

        Example:
            >>> ObjectIdentifierType((1, 0)).child(1)
            ObjectIdentifierType(value=(1, 0, 1))
        """
        if arc < 0:
            raise ValueError(f"Arc must be non-negative, got {arc}")
        return self.__class__(self.value + (arc,))


# # Common OID aliases for convenience
# class CommonOIDs:
#     """
#     Commonly used OBJECT IDENTIFIERs.

#     References:
#         - ITU-T X.660 | ISO/IEC 9834-1: OID registration
#         - ISO/IEC 8824-1 (ASN.1 standards)
#         - ISO/IEC 8825-1 (BER encoding)
#     """

#     # Root arcs
#     ITU_T = ObjectIdentifierType((0,))
#     ISO = ObjectIdentifierType((1,))
#     JOINT_ISO_ITU_T = ObjectIdentifierType((2,))

#     # ISO/IEC 8824 (ASN.1)
#     ASN1_STANDARD = ObjectIdentifierType((1, 0, 8824))
#     ASN1_PART1 = ObjectIdentifierType((1, 0, 8824, 1))  # Basic notation
#     ASN1_PART2 = ObjectIdentifierType((1, 0, 8824, 2))  # Information objects
#     ASN1_PART3 = ObjectIdentifierType((1, 0, 8824, 3))  # Constraints
#     ASN1_PART4 = ObjectIdentifierType((1, 0, 8824, 4))  # Parameterization

#     # ISO/IEC 8825 (Encoding rules)
#     ASN1_ENCODING = ObjectIdentifierType((1, 0, 8825))
#     BER = ObjectIdentifierType((1, 0, 8825, 1))  # Basic Encoding Rules
#     PER = ObjectIdentifierType((1, 0, 8825, 2))  # Packed Encoding Rules
#     ECN = ObjectIdentifierType((1, 0, 8825, 3))  # Encoding Control Notation
#     XER = ObjectIdentifierType((1, 0, 8825, 4))  # XML Encoding Rules

#     # Joint ISO/ITU-T ASN.1 (newer standards)
#     JOINT_ASN1 = ObjectIdentifierType((2, 10, 8824))
#     JOINT_ASN1_ENCODING = ObjectIdentifierType((2, 10, 8825))

#     # DLMS/COSEM (IEC 62056)
#     DLMS = ObjectIdentifierType((2, 10, 13))  # Under joint-iso-itu-t
