from dataclasses import dataclass
from typing import Any
from .type import OCTET_STRING, Constraint, RestrictedCharacterStringType, STRING


@dataclass
class GraphicString(RestrictedCharacterStringType):
    value: OCTET_STRING

    def check_constraint(self, constraint: Constraint[Any]) -> None:
        raise NotImplementedError(f"Validation not implemented for {type(constraint.constraint_spec)}")


@dataclass
class VisibleString(RestrictedCharacterStringType):
    value: STRING

    def check_constraint(self, constraint: Constraint[Any]) -> None:
        raise NotImplementedError(f"Validation not implemented for {type(constraint.constraint_spec)}")


@dataclass
class Utf8String(RestrictedCharacterStringType):
    value: STRING

    def check_constraint(self, constraint: Constraint[Any]) -> None:
        raise NotImplementedError(f"Validation not implemented for {type(constraint.constraint_spec)}")
