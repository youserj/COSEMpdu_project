from dataclasses import dataclass
from StructResult.result import Error
from typing import Optional, Self, ClassVar, overload, Any
from .type import BuiltinType, BIT_STRING, Simple, InitError, is_classvar


@dataclass(frozen=True)
class NamedBit:
    """
    NamedBit ::= identifier "(" number ")" | identifier "(" DefinedValue ")"
    Example:
        read(0), write(1), execute(2)
    """
    identifier: str
    position: int  # bit number (LSB0, X.680)

    def __str__(self) -> str:
        return f"{self.identifier}({self.position})"

    def __int__(self) -> int:
        return 1 << self.position


class BitStringType(Simple[BIT_STRING], BuiltinType):
    """
    BIT STRING type (X.680 22)

    Native representation:
    - value: tuple[int, ...] of bits (0/1) in LSB0 order
    - named_bits: ClassVar[Optional[tuple[NamedBit, ...]]] — bit names defined for this type.
        Automatically populated in __init_subclass__ by scanning Final[int] class annotations.

    ASN.1 examples:
        Status ::= BIT STRING { read(0), write(1), execute(2) }
        Bits ::= BIT STRING { flag0(0), flag1(1), flag2(2) } (SIZE(4))

    Usage:
        class Status(BitStringType):
            read: Final[int] = 0
            write: Final[int] = 1
            execute: Final[int] = 2
    """
    named_bits: ClassVar[Optional[tuple[NamedBit, ...]]] = None  # ClassVar, per-type
    value: BIT_STRING

    def __init_subclass__(cls) -> None:
        """
        Build <members> tuple from `Final[int]` class annotations.
        Ignores ClassVar members.
        """
        named_bits: list[NamedBit] = []
        for identifier, type_ in cls.__annotations__.items():
            if is_classvar(type_):
                continue
            if (
                hasattr(cls, identifier)
                and isinstance(position := cls.__dict__[identifier], int)
            ):
                named_bits.append(NamedBit(identifier, position))
        cls.named_bits = tuple(named_bits)

    @classmethod
    def validate(cls, value: Any) -> None | Error:
        if isinstance(value, tuple):
            return None
        return Error.from_e(InitError(f"got {value=}, expected BIT_STRING"))

    @classmethod
    def default(cls) -> Self:
        """Default value: all bits 0"""
        if cls.named_bits:
            return cls((0,) * (cls.named_bits[-1].position + 1))
        return cls(())

    @classmethod
    def from_bin(cls, bin_str: str) -> Self:
        """
        Create from binary string: '101' -> (1,0,1)
        ASN.1 notation: '101'B
        """
        # Remove ASN.1 quotes and B suffix
        if bin_str.startswith("'") and bin_str.endswith("'B"):
            bin_str = bin_str[1:-2]
        elif bin_str.endswith("'B"):
            bin_str = bin_str[:-2]
        # Validate
        if not all(c in "01" for c in bin_str):
            raise ValueError(f"Invalid binary string: {bin_str}")
        bits = tuple(int(c) for c in bin_str)
        return cls(bits)

    @classmethod
    def from_hex(cls, hex_str: str, bit_length: Optional[int] = None) -> Self:
        """
        Create from hex string: 'A5' -> (1,0,1,0,0,1,0,1)
        ASN.1 notation: 'A5'H
        """
        if hex_str.startswith("'") and hex_str.endswith("'H"):
            hex_str = hex_str[1:-2]
        elif hex_str.endswith("'H"):
            hex_str = hex_str[:-2]
        data = bytes.fromhex(hex_str)
        bits: list[int] = []
        for byte in data:
            bits.extend([(byte >> i) & 1 for i in range(7, -1, -1)])
        if bit_length is not None:
            bits = bits[:bit_length]
        return cls(tuple(bits))

    @classmethod
    def from_int(cls, value: int, length: int) -> Self:
        """
        Create from integer with given length:
        42, 6 -> 101010 (6 bits)
        """
        bits: list[int] = []
        for i in range(length - 1, -1, -1):
            bits.append((value >> i) & 1)
        return cls(tuple(bits))

    @classmethod
    def from_bytes(cls, data: bytes, bit_length: Optional[int] = None) -> Self:
        """
        Create from bytes (big-endian, MSB first)
        """
        bits: list[int] = []
        for byte in data:
            bits.extend([(byte >> i) & 1 for i in range(7, -1, -1)])
        if bit_length is not None:
            bits = bits[:bit_length]
        return cls(tuple(bits))

    @classmethod
    def from_bits(cls, *bits: int) -> Self:
        """Create with bits set at given positions: (0, 3, 5) -> bits 0,3,5 = 1, rest 0"""
        if not bits:
            return cls.default()
        max_pos = max(bits)
        result = [0] * (max_pos + 1)
        for pos in bits:
            result[pos] = 1
        return cls(tuple(result))

    @classmethod
    def empty(cls) -> Self:
        """Empty bit string"""
        return cls(())

    @classmethod
    def zeros(cls, length: int) -> Self:
        """Bit string of all zeros of given length"""
        return cls(tuple([0] * length))

    @classmethod
    def ones(cls, length: int) -> Self:
        """Bit string of all ones of given length"""
        return cls(tuple([1] * length))

    @property
    def bit_length(self) -> int:
        """Length in bits"""
        return len(self.value)

    @property
    def octet_length(self) -> int:
        """Length in octets (rounded up)"""
        return (len(self.value) + 7) // 8

    @overload
    def __getitem__(self, key: int) -> int: ...

    @overload
    def __getitem__(self, key: slice) -> Self: ...

    def __getitem__(self, key: int | slice) -> int | Self:
        """
        Bit access:
        - int: bits[0] -> first bit (LSB0), returns int (0/1)
        - slice: bits[1:4] -> slice, returns new BitStringType
        """
        if isinstance(key, int):
            # Index access
            if key < 0:
                raise IndexError(f"Bit index {key} out of range [0, ...]")
            if key >= len(self.value):
                # If there is a named_bit with position == key, return 0
                named_bits = self.named_bits
                if named_bits and any(nb.position == key for nb in named_bits):
                    return 0
                raise IndexError(f"Bit index {key} out of range [0, {len(self.value)-1}]")
            return self.value[key]
        if isinstance(key, slice):
            # Bit string slice
            sliced = self.value[key]
            return self.__class__(sliced)
        raise TypeError(f"Expected int, str or slice, got {type(key)}")

    def __setitem__(self, key: int | slice, value: int | bool | Self) -> None:
        """
        Bit assignment:
        - int: bits[0] = 1 -> set a single bit
        - slice: bits[1:4] = (1,0,1) -> set a slice
        """
        if isinstance(key, int):
            # Set by index
            if key < 0:
                raise IndexError(f"Bit index {key} out of range [0, ...]")
            named_bits = self.__class__.named_bits
            if key >= len(self.value):
                # Auto-expand if key matches a named_bit position
                if named_bits and any(nb.position == key for nb in named_bits):
                    bits = list(self.value)
                    bits.extend([0] * (key - len(self.value) + 1))
                    bits[key] = int(value)
                    self.value = tuple(bits)
                    return
                raise IndexError(f"Bit index {key} out of range [0, {len(self.value)-1}]")
            bits = list(self.value)
            bits[key] = int(value)
            self.value = tuple(bits)
        elif isinstance(key, slice):
            # Set a slice
            if isinstance(value, (tuple, list)):
                # Value as a sequence of bits
                new_bits = list(self.value)
                new_bits[key] = list(int(v) for v in value)
                self.value = tuple(new_bits)
            elif isinstance(value, self.__class__):
                # Value as another BitStringType
                new_bits = list(self.value)
                new_bits[key] = list(value.value)
                self.value = tuple(new_bits)
            else:
                raise TypeError(f"Expected tuple, list or BitStringType for slice assignment, got {type(value)}")

        else:
            raise TypeError(f"Expected int, str or slice, got {type(key)}")

    def get_value(self, identifier: int, default: int = 0) -> int:
        """Safely get a named bit value"""
        try:
            return self[identifier]
        except KeyError:
            return default

    def set(self, identifier: int, value: int = 1) -> None:
        """Set a named bit"""
        self[identifier] = value

    def clear(self, identifier: int) -> None:
        """Clear a named bit to 0"""
        self[identifier] = 0

    def toggle(self, identifier: int) -> None:
        """Toggle a named bit"""
        self[identifier] = 1 - self[identifier]

    def has_bit(self, identifier: int) -> bool:
        """Check if a named bit is set"""
        return bool(self.get_value(identifier, 0))

    def has_any(self, *identifiers: int) -> bool:
        """Check if at least one of the specified bits is set"""
        return any(self.has_bit(ident) for ident in identifiers)

    def has_all(self, *identifiers: int) -> bool:
        """Check if all specified bits are set"""
        return all(self.has_bit(ident) for ident in identifiers)

    def to_bin(self) -> str:
        """Binary representation: '1011'"""
        return "".join(map(str, self.value))

    def hex(self) -> str:
        """Hexadecimal representation: 'A5'"""
        if not self.value:
            return ""
        # Pad to octet boundary
        padded = list(self.value)
        while len(padded) % 8 != 0:
            padded.append(0)
        # Convert to bytes
        data: list[int] = []
        for i in range(0, len(padded), 8):
            byte = 0
            for j in range(8):
                byte |= (padded[i + j] << (7 - j))
            data.append(byte)
        return bytes(data).hex().upper()

    def __int__(self) -> int:
        """Integer representation (big-endian)"""
        result = 0
        for bit in self.value:
            result = (result << 1) | bit
        return result

    def __bytes__(self) -> bytes:
        """Byte representation with octet-aligned padding"""
        return bytes.fromhex(self.hex())

    def __str__(self) -> str:
        """ASN.1 notation: '101'B or '{read, write}'"""
        named_bits = self.__class__.named_bits
        if named_bits:
            # Show set bit names
            set_bits: list[str] = []
            for named_bit in named_bits:
                if named_bit.position < len(self.value) and self.value[named_bit.position]:
                    set_bits.append(named_bit.identifier)
            if set_bits:
                return "{" + ", ".join(set_bits) + "}"
            return "{}"
        return f"'{self.to_bin()}'B"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_bin()!r})"

    def __and__(self, other: Self) -> Self:
        """Bitwise AND"""
        min_len = min(len(self.value), len(other.value))
        result = tuple(self.value[i] & other.value[i] for i in range(min_len))
        return self.__class__(result)

    def __or__(self, other: Self) -> Self:
        """Bitwise OR"""
        max_len = max(len(self.value), len(other.value))
        result = [0] * max_len
        for i, bit in enumerate(self.value):
            result[i] = bit
        for i, bit in enumerate(other.value):
            result[i] |= bit
        return self.__class__(tuple(result))

    def __xor__(self, other: Self) -> Self:
        """Bitwise XOR"""
        min_len = min(len(self.value), len(other.value))
        result = tuple(self.value[i] ^ other.value[i] for i in range(min_len))
        return self.__class__(tuple(result))

    def __invert__(self) -> Self:
        """Bitwise NOT"""
        result = tuple(1 - b for b in self.value)
        return self.__class__(result)

    def __lshift__(self, shift: int) -> Self:
        """Left shift (append zeros on the right)"""
        if shift < 0:
            return self.__rshift__(-shift)
        bits = list(self.value)
        bits.extend([0] * shift)
        return self.__class__(tuple(bits))

    def __rshift__(self, shift: int) -> Self:
        """Right shift (discard bits from the right)"""
        if shift < 0:
            return self.__lshift__(-shift)
        if shift >= len(self.value):
            return self.__class__(())
        return self.__class__(self.value[:-shift])

    def __add__(self, other: Self) -> Self:
        """Concatenation of bit strings"""
        result = self.value + other.value
        return self.__class__(result)

    def __bool__(self) -> bool:
        """True if at least one bit is set (non-zero)"""
        return any(b == 1 for b in self.value)

    def __contains__(self, item: int) -> bool:
        return bool(self.value[item])