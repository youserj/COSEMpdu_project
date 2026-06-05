from typing import Any, Self
from StructResult.result import Error
from .type import BuiltinType, BOOLEAN, Simple, InitError


class BooleanType(Simple[BOOLEAN], BuiltinType):
    """
    BOOLEAN type (X.680 §17)
    NATIVE REPRESENTATION: bool
    """
    value: BOOLEAN

    @classmethod
    def validate(cls, value: Any) -> None | Error:
        if isinstance(value, bool):
            return None
        return Error.from_e(InitError(f"got {value=}, expected BOOLEAN"))

    @classmethod
    def default(cls) -> Self:
        """Default value: FALSE"""
        return cls(False)  # noqa: FBT003

    def __bool__(self) -> bool:
        return self.value

    def __str__(self) -> str:
        return "TRUE" if self.value else "FALSE"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"
