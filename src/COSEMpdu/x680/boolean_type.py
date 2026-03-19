from dataclasses import dataclass
from typing import Any
from .type import BuiltinType, BOOLEAN, Constraint, TYPE_VALUE, SEQUENCE_OF, Type


@dataclass
class BooleanType(BuiltinType):
    """
    BOOLEAN type (X.680 §17)
    NATIVE REPRESENTATION: bool
    """
    value: BOOLEAN

    def check_constraint(self, constraint: Constraint[Any]) -> None:
        raise NotImplementedError(f"Validation not implemented for {type(constraint.constraint_spec)}")

    def __bool__(self) -> bool:
        return self.value

    def __str__(self) -> str:
        return "TRUE" if self.value else "FALSE"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"