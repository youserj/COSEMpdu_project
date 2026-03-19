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
from dataclasses import dataclass
from typing import ClassVar, Any, Self
from .tag import Tag
from .type import Type, NamedType, BuiltinType, Constraint


@dataclass
class ChoiceType(BuiltinType):
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
    
    Note:
        - Encoding/decoding is handled in x690 module (BER)
        - This Protocol only describes the abstract syntax structure
        - For IEC 61334-6, alternatives should be explicitly tagged
    """
    
    # Class variable: defines available alternatives for this CHOICE type
    alternatives: ClassVar[dict[Tag, NamedType[Type]]]
    value: Type

    def check_constraint(self, constraint: Constraint[Any]) -> None:
        raise NotImplementedError(f"Validation not implemented for {type(constraint.constraint_spec)}")
       
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"value={self.value!r})"
        )
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ChoiceType):
            return False
        return self.value == other.value

    def __str__(self) -> str:
        return f"{self.__class__.__name__}.{self.value}"

    @classmethod
    def from_id(cls, identifier: str, value: Type) -> Self:
        for n_t in cls.alternatives.values():
            if n_t.identifier == identifier:
                return cls(n_t.type_(value))
        else:
            raise ValueError(f"{identifier=} not in alternatives: {", ".join(map(str, (n_t.identifier for n_t in cls.alternatives.values())))}")
