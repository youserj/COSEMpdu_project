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
from typing import ClassVar, Protocol, Self, Any
from StructResult.result import Error
from .type import Type, BuiltinType, CHOICE, InitError


class ChoiceType[T: Type](BuiltinType, Protocol):
    """
    ASN.1 CHOICE type protocol (X.680 §28).

    Defines the abstract structure for CHOICE types — a discriminated union
    where exactly one alternative is present.  Encoding/decoding logic is
    provided by concrete implementations that subclass this protocol:

    * ``ber.ChoiceType`` — BER encoding (X.690 §8.13), used in ACSE layer
    * ``axdr.ChoiceType`` — A-XDR encoding (IEC 61334-6 §6.6), used in DLMS/COSEM

    **Typical usage**

    .. code-block:: python

        class MyChoice(axdr.ChoiceType):                # use A-XDR for COSEM
            value: FooType | BarType                     # union annotation → auto-generates alternatives

    ``alternatives`` (``dict[int, Type]``) is automatically derived from
    the ``value`` annotation by the concrete subclass constructor
    (see ``ber.ChoiceType`` / ``axdr.ChoiceType``).  Tag numbers are taken
    from the ``tag`` attribute of each type class in the union.  You may
    also override the mapping manually:

    .. code-block:: python

        class MyChoice(axdr.ChoiceType):
            alternatives = {1: FooType, 2: BarType}      # explicit tag → type mapping
            value: FooType | BarType

    **Attributes:**

    ``alternatives``
        ClassVar mapping tag numbers (``int``) directly to Python type
        classes (``Type``).  Each type class must provide a ``tag``
        attribute for automatic generation; manual overrides may use
        arbitrary tag numbers.

    ``value``
        Instance of the currently selected alternative.  The annotation
        should be a union of all possible alternative types so that
        type-checkers and the auto-generation of ``alternatives`` work
        correctly.

    **Methods** (no encoding — see ``ber.ChoiceType`` / ``axdr.ChoiceType``)

    ``validate(value)``
        Check that *value* is an instance of one of the alternatives.

    ``default()``
        Return an instance with the first alternative set to its default.

    ``parse(value)`` / ``normalize()``
        Conversion from/to the ``CHOICE`` helper type (see ``x680.type``).
    """

    # Class variable: defines available alternatives for this CHOICE type
    alternatives: ClassVar[dict[int, Type]]
    value: T

    def __init__(self, value: T) -> None:
        self.value = value

    @classmethod
    def validate(cls, value: Any) -> None | Error:
        for it in cls.alternatives.values():
            if isinstance(value, it):
                break
        return Error.from_e(InitError(f"got {value=}, expected {", ".join((it.__name__ for it in cls.alternatives.values()))}"))  # TODO: make better

    @classmethod
    def parse(cls, value: CHOICE) -> Self:
        raise NotImplementedError()

    def normalize(self) -> CHOICE:
        raise NotImplementedError()

    @classmethod
    def default(cls) -> Self:
        return cls(cls.alternatives[next(iter(cls.alternatives))].default())  # type: ignore

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
