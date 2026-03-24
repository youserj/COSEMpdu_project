from dataclasses import dataclass
from .type import RestrictedCharacterStringType


@dataclass
class GraphicString(RestrictedCharacterStringType):
    ...


@dataclass
class VisibleString(RestrictedCharacterStringType):
    ...


@dataclass
class Utf8String(RestrictedCharacterStringType):
    ...
