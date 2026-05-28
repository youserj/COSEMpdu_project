from typing import Self
from dataclasses import dataclass
from .x680.type import NamedType, OCTET_STRING
from .x680.enumerated_type import EnumerationList, EnumerationMember
from .x680.tagged_type import TaggingMode
from . import axdr
from .axdr import SequenceType, TaggedType, EnumeratedType, OctetStringType


# =============================================================================
# ENUMERATED Types (A-XDR: encoded as fixed-length unsigned integer in 1 byte)
# Using EnumerationList pattern from service_error.py
# =============================================================================


class KeyIdList(EnumerationList):
    """KeyId enumeration members"""
    members = (
        EnumerationMember("global-unicast-encryption-key", 0),
        EnumerationMember("global-broadcast-encryption-key", 1),
    )


class KeyId(EnumeratedType):
    """Key-Id"""
    named_members = KeyIdList()


class KekIdList(EnumerationList):
    """KekId enumeration members"""
    members = (
        EnumerationMember("master-key", 0),
    )


class KekId(EnumeratedType):
    """Kek-Id"""
    named_members = KekIdList()


# =============================================================================
# SEQUENCE Types (A-XDR: components encoded in order, no identifier)
# =============================================================================

@dataclass
class IdentifiedKey(SequenceType):
    """Identified-Key"""
    key_id: KeyId


class identifiedKey(TaggedType[IdentifiedKey]):
    """identified-key"""
    tag = 0
    mode = TaggingMode.IMPLICIT
    value: IdentifiedKey


class WrappedKey(SequenceType):
    """Wrapped-Key"""
    kek_id: KekId


class WrappedKey1(TaggedType[WrappedKey]):
    """[1] Wrapped-Key"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: WrappedKey


class AgreedKey(SequenceType):
    """Agreed-Key"""
    key_parameters: OctetStringType
    key_ciphered_data: OctetStringType


class AgreedKey2(TaggedType[AgreedKey]):
    """[2] Agreed-Key"""
    tag = 2
    mode = TaggingMode.IMPLICIT
    value: AgreedKey


# =============================================================================
# CHOICE Type (A-XDR: tag (1 byte) + encoding of chosen alternative)
# =============================================================================


class KeyInfo(axdr.ChoiceType):
    """Key-Info"""
    alternatives = {
        0: NamedType("identified-key", identifiedKey),
        1: NamedType("wrapped-key", WrappedKey1),
        2: NamedType("agreed-key", AgreedKey2)
    }

    # Convenience constructors
    @classmethod
    def identified_key(cls, key_id: KeyId) -> Self:
        """Create KeyInfo from Identified-Key alternative"""
        return cls(identifiedKey(IdentifiedKey((key_id,))))

    @classmethod
    def wrapped_key(cls, kek_id: KekId, key_ciphered_data: OCTET_STRING) -> Self:
        """Create KeyInfo from Wrapped-Key alternative"""
        return cls(WrappedKey1(WrappedKey((kek_id, axdr.OctetStringType(key_ciphered_data),))))

    @classmethod
    def agreed_key(cls, key_parameters: OCTET_STRING, key_ciphered_data: OCTET_STRING) -> Self:
        """Create KeyInfo from Agreed-Key alternative"""
        return cls(AgreedKey2(AgreedKey((
            axdr.OctetStringType(key_parameters),
            axdr.OctetStringType(key_ciphered_data)
        ))))

    def __repr__(self) -> str:
        """Human-readable representation"""
        return f"KeyInfo.{self.value!r}"
