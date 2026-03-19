from dataclasses import dataclass
from typing import ClassVar, Optional, Protocol
from .type import Type


# @dataclass
# class ConstrainedType(Type, Protocol):
#     constraint_spec: ClassVar[ConstraintSpec]
#     exception_spec: Optional[ExceptionSpec] = None
