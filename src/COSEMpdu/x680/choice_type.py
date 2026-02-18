# src/COSEMpdu/x680/choice_type.py
"""
ASN.1 CHOICE Type Definition (X.680 §28)

This module defines the abstract syntax for CHOICE types.
Encoding/decoding (BER) is handled separately in x690 module.

Standards:
    - X.680 §28: CHOICE type definition
    - X.690 §8.13: CHOICE encoding rules (handled in x690)
    - IEC 61334-6 §6.6: DLMS/COSEM CHOICE usage
"""
from typing import ClassVar, Optional
from .tag import Class
from .type import Type, UType


class ChoiceType(UType):
    """
    ASN.1 CHOICE type metadata (X.680 §28).
    
    CHOICE defines a type where exactly one alternative is present.
    This Protocol describes the structure without encoding logic.
    
    Example ASN.1:
        Dummy_PDU ::= CHOICE {
            a [0] INTEGER,
            b [1] BYTE STRING (SIZE(4))
        }
    
    Attributes:
        alternatives: Mapping of tag numbers to ASN.1 type classes (ClassVar)
        selected_tag: Tag number of the currently chosen alternative
        class_: Tag class for alternatives (default CONTEXT_SPECIFIC)
    
    Note:
        - Encoding/decoding is handled in x690 module (BER)
        - This Protocol only describes the abstract syntax structure
        - For IEC 61334-6, alternatives should be explicitly tagged
    """
    
    # Class variable: defines available alternatives for this CHOICE type
    alternatives: ClassVar[dict[int, type[Type]]]
    
    # Instance variables: which alternative was actually chosen
    selected_tag: int
    value: Type
    class_: Class
    
    def __init__(
        self,
        selected_tag: int,
        value: Type,
        class_: Class = Class.CONTEXT_SPECIFIC
    ) -> None:
        """
        Initialize CHOICE type instance.
        
        Args:
            selected_tag: Tag number of the chosen alternative
            class_: Tag class (default CONTEXT_SPECIFIC)
        """
        if selected_tag not in self.alternatives:
            raise ValueError(
                f"Tag {selected_tag} not in alternatives: "
                f"{list(self.alternatives.keys())}"
            )
        self.selected_tag = selected_tag
        self.class_ = class_
        self.value = value

    @property
    def selected_alternative(self) -> int:
        """Return the tag number of the selected alternative."""
        return self.selected_tag
    
    @property
    def alternative_value(self) -> Optional[Type]:
        """Return the value of the selected alternative."""
        return self.value
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"tag={self.selected_tag}, "
            f"class={self.class_.name}, "
            f"value={self.value!r})"
        )
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ChoiceType):
            return False
        return (
            self.selected_tag == other.selected_tag and
            self.class_ == other.class_ and
            self.value == other.value
        )
