# src/COSEMpdu/x680/sequence_type.py
from typing import ClassVar, Optional, Self, Any, Union, get_origin, get_args
from StructResult.result import Error
from types import UnionType
from .type import BuiltinType, NamedType, Type, TYPE_VALUE, NULL, DefaultNamedType, OptionalNamedType, is_classvar, InitError


def get_optional(type_: Any) -> Optional[type]:
    """Extract inner type from Optional[X] annotation."""
    origin = get_origin(type_)
    if origin in (Union, UnionType):
        args = get_args(type_)
        non_none_types = [arg for arg in args if arg is not type(None)]
        if len(non_none_types) == 1:
            return non_none_types[0]
    return None


class SequenceType(BuiltinType):
    """
    Base class for SEQUENCE types (X.680 §24)
    NATIVE REPRESENTATION: dataclass instance with fields corresponding to components

    ASN.1 semantics:
    - Ordered collection of named components (X.680 §3.6.60)
    - Components may be OPTIONAL or DEFAULT (X.680 §24.3)
    - Tag: UNIVERSAL 16 (X.680 §24.16)
    - XML notation: <SEQUENCE>...</SEQUENCE> (X.680 Table 4)

    A-XDR encoding note (IEC 61334-6 §6.9):
    - Components encoded in definition order
    - OPTIONAL/DEFAULT components omitted when absent/default
    - Explicit tags NOT encoded (redundant information)

    Usage pattern with @dataclass (simple case — all OPTIONAL/DEFAULT after mandatory):
        @dataclass
        class Credentials(SequenceType):
            userName: VisibleStringType
            password: VisibleStringType
            accountNumber: Optional[IntegerType] = None  # OPTIONAL component
            status: BooleanType = BooleanType(True)  # DEFAULT

    Usage pattern without @dataclass (when OPTIONAL/DEFAULT fields are mixed among mandatory):
        class MixedSequence(SequenceType):
            optionalField: Optional[IntegerType] = None   # OPTIONAL — before mandatory
            mandatoryField: VisibleStringType             # MANDATORY
            flag: BooleanType = BooleanType(False)        # DEFAULT — after mandatory

            def __init__(self, mandatoryField: VisibleStringType,
                         optionalField: Optional[IntegerType] = None,
                         flag: BooleanType = BooleanType(False)):
                self.mandatoryField = mandatoryField
                self.optionalField = optionalField
                self.flag = flag

    Component access:
        cred = Credentials(userName=..., password=...)
        cred.userName  # Direct attribute access
        cred.accountNumber  # None if absent (OPTIONAL)

    Note:
        - Encoding is concatenation of component encodings
        - Component order is fixed by ASN.1 definition
        - For DLMS/COSEM, component tags are omitted (unlike BER)
        - OPTIONAL/DEFAULT indicated by presence flag in A-XDR
        - Subclass components are created from __annotations__ (via __init_subclass__)
        - If all OPTIONAL/DEFAULT components are absent or appear only after mandatory
          fields, the class should be decorated with @dataclass
        - Otherwise, __init__ must reorder parameters: mandatory fields first,
          followed by Optional/Default fields in their original order
        - The order of __annotations__ matters, just like in ASN.1.
          The order of the components determines the encoding/decoding order.
        - When using @dataclass, do NOT use field() for DEFAULT components —
          it prevents proper DEFAULT detection.
    """
    components: ClassVar[tuple[NamedType[Type], ...]]

    @classmethod
    def validate(cls, value: Any) -> None | Error:
        raise RuntimeError()
        # if isinstance(value, int):
        #     return None
        # return Error.from_e(InitError(f"got {value=}, expected ENUM"))

    @classmethod
    def parse[U: TYPE_VALUE](cls, value: tuple[U]) -> Self:
        return cls(**{comp.identifier: None if val is None else comp.type_.parse(val) for comp, val in zip(cls.components, value, strict=True)})

    def normalize(self) -> tuple[TYPE_VALUE, ...]:
        return tuple(NULL if (value := getattr(self, comp.identifier)) is None else value.normalize() for comp in self.components)

    @classmethod
    def default(cls) -> Self:
        return cls(**{component.identifier: component.type_.default() for component in cls.components})

    def __str__(self) -> str:
        """
        ASN.1 value notation per X.680 §24.17:
        { identifier1 value1, identifier2 value2, ... }
        Omits components with value None (absent OPTIONAL components).
        DEFAULT values are ALWAYS included (cannot distinguish explicit vs default assignment in native representation).
        """
        return f"{self.__class__.__name__}[{len(self.components)}]"

    def __getitem__(self, key: int | str) -> Optional[Type]:
        if isinstance(key, int):
            key = self.components[key].identifier
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"not find component with name: {key}")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SequenceType):
            return False
        return self.normalize() == other.normalize()

    @classmethod
    def _init_sequence_components(cls) -> None:
        """
        Build <components> tuple from class annotations.
        Should be called from SequenceType.__init_subclass__ in encoding modules (ber/axdr).
        """
        elements: list[NamedType[Type] | OptionalNamedType | DefaultNamedType[Type]] = []
        if hasattr(cls, "components"):
            elements.extend(cls.components)
        for identifier, type_ in cls.__annotations__.items():
            if is_classvar(type_):
                continue
            if (
                hasattr(cls, identifier)
                and (value := cls.__dict__[identifier]) is not None
            ):
                n_t = DefaultNamedType(identifier, type_, value)
            elif in_type := get_optional(type_):
                n_t = OptionalNamedType(identifier, in_type)
            else:
                n_t = NamedType(identifier, type_)
            elements.append(n_t)
        cls.components = tuple(elements)
