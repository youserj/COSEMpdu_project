from typing import Self
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


class IdentifiedKey(SequenceType):
    """Identified-Key"""
    components = (
        NamedType("key-id", KeyId),
    )


class IdentifiedKey0(TaggedType[IdentifiedKey]):
    """[0] Identified-Key"""
    tag = 0
    mode = TaggingMode.IMPLICIT
    value: IdentifiedKey


class WrappedKey(SequenceType):
    """Wrapped-Key"""
    components = (
        NamedType("kek-id", KekId),
        NamedType("key-ciphered-data", axdr.OctetStringType),
    )


class WrappedKey1(TaggedType[WrappedKey]):
    """[1] Wrapped-Key"""
    tag = 1
    mode = TaggingMode.IMPLICIT
    value: WrappedKey


class AgreedKey(SequenceType):
    """Agreed-Key"""
    components = (
        NamedType("key-parameters", OctetStringType),
        NamedType("key-ciphered-data", OctetStringType),
    )


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
        0: NamedType("identified-key", IdentifiedKey0),
        1: NamedType("wrapped-key", WrappedKey1),
        2: NamedType("agreed-key", AgreedKey2)
    }

    # Convenience constructors
    @classmethod
    def identified_key(cls, key_id: KeyId) -> Self:
        """Create KeyInfo from Identified-Key alternative"""
        return cls(IdentifiedKey0(IdentifiedKey((key_id,))))

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
