from dataclasses import dataclass
from typing import Iterator, Optional, Self, ClassVar, Protocol, runtime_checkable, overload
from .type import BuiltinType


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


class NamedBitList:
    """
    NamedBitList ::= NamedBit | NamedBitList "," NamedBit
    """
    bits: ClassVar[tuple[NamedBit, ...]]

    def get_mask(self) -> int:
        """Битовая маска всех именованных битов"""
        mask = 0
        for bit in self.bits:
            mask |= (1 << bit.position)
        return mask

    def get_bit(self, identifier: str) -> Optional[NamedBit]:
        """Получить NamedBit по имени"""
        for bit in self.bits:
            if bit.identifier == identifier:
                return bit
        return None

    def __getitem__(self, identifier: str) -> int:
        """Получить позицию бита по имени"""
        bit = self.get_bit(identifier)
        if bit is None:
            raise KeyError(f"No named bit: {identifier}")
        return bit.position

    def __contains__(self, identifier: str) -> bool:
        return self.get_bit(identifier) is not None

    def __iter__(self) -> Iterator[NamedBit]:
        return iter(self.bits)

    def __len__(self) -> int:
        return len(self.bits)

    def __str__(self) -> str:
        return "{" + ", ".join(str(b) for b in self.bits) + "}"


@runtime_checkable
@dataclass
class BitStringType(BuiltinType, Protocol):
    """
    BIT STRING type (X.680 22)
    NATIVE REPRESENTATION:
    - value: tuple[int, ...] of bits (0/1) in LSB0 order
    - named_bits: ClassVar[Optional[NamedBitList]] - имена битов для ЭТОГО ТИПА
    Примеры ASN.1:
        Status ::= BIT STRING { read(0), write(1), execute(2) }
        Bits ::= BIT STRING { flag0(0), flag1(1), flag2(2) } (SIZE(4))
    """
    named_bits: ClassVar[Optional[NamedBitList]] = None  # ← ClassVar!
    value: tuple[int, ...]  # биты в порядке LSB0: (bit0, bit1, bit2, ...)

    @classmethod
    def from_bin(cls, bin_str: str) -> Self:
        """
        Создать из двоичной строки: '101' -> (1,0,1)
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
        Создать из шестнадцатеричной строки: 'A5' -> (1,0,1,0,0,1,0,1)
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
        Создать из целого числа с заданной длиной:
        42, 6 -> 101010 (6 бит)
        """
        bits: list[int] = []
        for i in range(length - 1, -1, -1):
            bits.append((value >> i) & 1)
        return cls(tuple(bits))

    @classmethod
    def from_bytes(cls, data: bytes, bit_length: Optional[int] = None) -> Self:
        """
        Создать из байтов (big-endian, MSB first)
        """
        bits: list[int] = []
        for byte in data:
            bits.extend([(byte >> i) & 1 for i in range(7, -1, -1)])
        if bit_length is not None:
            bits = bits[:bit_length]
        return cls(tuple(bits))

    @classmethod
    def empty(cls) -> Self:
        """Пустая битовая строка"""
        return cls(())

    @classmethod
    def zeros(cls, length: int) -> Self:
        """Битовая строка из всех нулей заданной длины"""
        return cls(tuple([0] * length))

    @classmethod
    def ones(cls, length: int) -> Self:
        """Битовая строка из всех единиц заданной длины"""
        return cls(tuple([1] * length))

    @property
    def bit_length(self) -> int:
        """Длина в битах"""
        return len(self.value)

    @property
    def octet_length(self) -> int:
        """Длина в октетах (с округлением вверх)"""
        return (len(self.value) + 7) // 8

    @overload
    def __getitem__(self, key: int | str) -> int: ...

    @overload
    def __getitem__(self, key: slice) -> Self: ...

    def __getitem__(self, key: int | str | slice) -> int | Self:
        """
        Доступ к битам:
        - int: bits[0] -> первый бит (LSB0), возвращает int (0/1)
        - str: bits['read'] -> значение именованного бита, возвращает int (0/1)
        - slice: bits[1:4] -> срез, возвращает новый BitStringType
        """
        if isinstance(key, int):
            # Доступ по индексу
            if key < 0 or key >= len(self.value):
                raise IndexError(f"Bit index {key} out of range [0, {len(self.value)-1}]")
            return self.value[key]
        elif isinstance(key, str):
            # Доступ по имени бита
            named_bits = self.__class__.named_bits
            if named_bits is None:
                raise KeyError(f"Type {self.__class__.__name__} has no named bits")
            position = named_bits[key]
            if position >= len(self.value):
                return 0  # Бит вне длины считается 0
            return self.value[position]
        elif isinstance(key, slice):
            # Срез битовой строки
            sliced = self.value[key]
            return self.__class__(sliced)
        else:
            raise TypeError(f"Expected int, str or slice, got {type(key)}")

    def __setitem__(self, key: int | str | slice, value: int | bool | Self) -> None:
        """
        Установка битов:
        - int: bits[0] = 1 -> установка одного бита
        - str: bits['read'] = True -> установка именованного бита
        - slice: bits[1:4] = (1,0,1) -> установка среза
        """
        if isinstance(key, int):
            # Установка по индексу
            if key < 0 or key >= len(self.value):
                raise IndexError(f"Bit index {key} out of range [0, {len(self.value)-1}]")
            bits = list(self.value)
            bits[key] = int(value)
            self.value = tuple(bits)
        
        elif isinstance(key, str):
            # Установка по имени
            named_bits = self.__class__.named_bits
            if named_bits is None:
                raise KeyError(f"Type {self.__class__.__name__} has no named bits")
            
            position = named_bits[key]
            if position >= len(self.value):
                # Расширяем строку
                bits = list(self.value)
                bits.extend([0] * (position - len(bits) + 1))
                bits[position] = int(value)
                self.value = tuple(bits)
            else:
                bits = list(self.value)
                bits[position] = int(value)
                self.value = tuple(bits)
        
        elif isinstance(key, slice):
            # Установка среза
            if isinstance(value, (tuple, list)):
                # Значение как последовательность битов
                new_bits = list(self.value)
                new_bits[key] = list(int(v) for v in value)
                self.value = tuple(new_bits)
            elif isinstance(value, self.__class__):
                # Значение как другой BitStringType
                new_bits = list(self.value)
                new_bits[key] = list(value.value)
                self.value = tuple(new_bits)
            else:
                raise TypeError(f"Expected tuple, list or BitStringType for slice assignment, got {type(value)}")
        
        else:
            raise TypeError(f"Expected int, str or slice, got {type(key)}")

    def get_value(self, identifier: str, default: int = 0) -> int:
        """Безопасное получение значения именованного бита"""
        try:
            return self[identifier]
        except KeyError:
            return default

    def set(self, identifier: str, value: int = 1) -> None:
        """Установка именованного бита"""
        self[identifier] = value

    def clear(self, identifier: str) -> None:
        """Сброс именованного бита в 0"""
        self[identifier] = 0

    def toggle(self, identifier: str) -> None:
        """Инвертирование именованного бита"""
        self[identifier] = 1 - self[identifier]

    def has_bit(self, identifier: str) -> bool:
        """Проверить, установлен ли именованный бит"""
        return bool(self.get_value(identifier, 0))

    def has_any(self, *identifiers: str) -> bool:
        """Проверить, установлен ли хотя бы один из указанных битов"""
        return any(self.has_bit(ident) for ident in identifiers)

    def has_all(self, *identifiers: str) -> bool:
        """Проверить, установлены ли все указанные биты"""
        return all(self.has_bit(ident) for ident in identifiers)

    def to_bin(self) -> str:
        """Двоичное представление: '1011'"""
        return "".join(map(str, self.value))

    def hex(self) -> str:
        """Шестнадцатеричное представление: 'A5'"""
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
        """Целочисленное представление (big-endian)"""
        result = 0
        for bit in self.value:
            result = (result << 1) | bit
        return result

    def __bytes__(self) -> bytes:
        """Байтовое представление с выравниванием до октета"""
        return bytes.fromhex(self.hex())

    def __str__(self) -> str:
        """ASN.1 notation: '101'B или '{read, write}'"""
        named_bits = self.__class__.named_bits
        if named_bits:
            # Для NamedBitList показываем установленные имена
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
        """Побитовое И"""
        min_len = min(len(self.value), len(other.value))
        result = tuple(self.value[i] & other.value[i] for i in range(min_len))
        return self.__class__(result)

    def __or__(self, other: Self) -> Self:
        """Побитовое ИЛИ"""
        max_len = max(len(self.value), len(other.value))
        result = [0] * max_len
        for i, bit in enumerate(self.value):
            result[i] = bit
        for i, bit in enumerate(other.value):
            result[i] |= bit
        return self.__class__(tuple(result))

    def __xor__(self, other: Self) -> Self:
        """Побитовое исключающее ИЛИ"""
        min_len = min(len(self.value), len(other.value))
        result = tuple(self.value[i] ^ other.value[i] for i in range(min_len))
        return self.__class__(tuple(result))

    def __invert__(self) -> Self:
        """Побитовое НЕ"""
        result = tuple(1 - b for b in self.value)
        return self.__class__(result)

    def __lshift__(self, shift: int) -> Self:
        """Сдвиг влево (добавление нулей справа)"""
        if shift < 0:
            return self.__rshift__(-shift)
        bits = list(self.value)
        bits.extend([0] * shift)
        return self.__class__(tuple(bits))

    def __rshift__(self, shift: int) -> Self:
        """Сдвиг вправо (отбрасывание битов справа)"""
        if shift < 0:
            return self.__lshift__(-shift)
        if shift >= len(self.value):
            return self.__class__(())
        return self.__class__(self.value[:-shift])

    def __add__(self, other: Self) -> Self:
        """Конкатенация битовых строк"""
        result = self.value + other.value
        return self.__class__(result)

    def __getslice__(self, start: int, end: int) -> Self:
        """Срез битовой строки"""
        return self.__class__(self.value[start:end])

    @classmethod
    def get_named_bits(cls) -> Optional[NamedBitList]:
        """Получить список именованных битов для этого типа"""
        return cls.named_bits

    @property
    def available_bits(self) -> dict[str, int]:
        """Словарь доступных именованных битов {имя: позиция}"""
        named_bits = self.__class__.named_bits
        if named_bits is None:
            return {}
        return {bit.identifier: bit.position for bit in named_bits}

    @property
    def set_bits(self) -> dict[str, int]:
        """Словарь установленных именованных битов {имя: позиция}"""
        named_bits = self.__class__.named_bits
        if named_bits is None:
            return {}
        result = {}
        for named_bit in named_bits:
            if named_bit.position < len(self.value) and self.value[named_bit.position]:
                result[named_bit.identifier] = named_bit.position
        return result

    @classmethod
    def get_named_bit(cls, identifier: str) -> Optional[NamedBit]:
        """Получить NamedBit по имени для этого типа"""
        if cls.named_bits is None:
            return None
        return cls.named_bits.get_bit(identifier)

    def __bool__(self) -> bool:
        """True если есть хотя бы один ненулевой бит"""
        return any(b == 1 for b in self.value)
