import unittest
import sys
import os

# Добавляем путь для импорта (замените на ваш реальный путь)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.COSEMpdu.x680.bit_string import BitStringType, NamedBit, NamedBitList


class TestNamedBit(unittest.TestCase):
    """Тесты для NamedBit"""
    
    def test_create_named_bit(self):
        """Создание именованного бита"""
        bit = NamedBit("read", 0)
        self.assertEqual(bit.identifier, "read")
        self.assertEqual(bit.position, 0)
        self.assertEqual(str(bit), "read(0)")
        self.assertEqual(int(bit), 1)  # 1 << 0 = 1
        
        bit2 = NamedBit("write", 1)
        self.assertEqual(str(bit2), "write(1)")
        self.assertEqual(int(bit2), 2)  # 1 << 1 = 2
        
        bit3 = NamedBit("execute", 2)
        self.assertEqual(int(bit3), 4)  # 1 << 2 = 4
    
    def test_named_bit_immutable(self):
        """NamedBit должен быть неизменяемым (frozen)"""
        bit = NamedBit("test", 5)
        with self.assertRaises(AttributeError):
            bit.identifier = "new"
        with self.assertRaises(AttributeError):
            bit.position = 10


class TestNamedBitList(unittest.TestCase):
    """Тесты для NamedBitList"""
    
    def setUp(self):
        class MyNamedBitList(NamedBitList):
            bits = (
                NamedBit("read", 0),
                NamedBit("write", 1),
                NamedBit("execute", 2)
            )

        self.named_bits = MyNamedBitList()
    
    def test_from_dict(self):
        """Создание NamedBitList из словаря"""
        self.assertEqual(len(self.named_bits), 3)
        
        # Проверяем порядок (должен сохраняться)
        bits = list(self.named_bits)
        self.assertEqual(bits[0].identifier, "read")
        self.assertEqual(bits[0].position, 0)
        self.assertEqual(bits[1].identifier, "write")
        self.assertEqual(bits[1].position, 1)
        self.assertEqual(bits[2].identifier, "execute")
        self.assertEqual(bits[2].position, 2)
    
    def test_get_mask(self):
        """Получение битовой маски"""
        mask = self.named_bits.get_mask()
        self.assertEqual(mask, 0b111)  # биты 0,1,2 = 7
        
        # Тест с другими битами
        class NamedBitList1(NamedBitList):
            bits = (
                NamedBit("flag0", 0),
                NamedBit("flag2", 2),
                NamedBit("flag5", 5),
            )

        bits2 = NamedBitList1()
        self.assertEqual(bits2.get_mask(), (1 << 0) | (1 << 2) | (1 << 5))
    
    def test_get_bit(self):
        """Получение NamedBit по имени"""
        bit = self.named_bits.get_bit("read")
        self.assertIsNotNone(bit)
        self.assertEqual(bit.identifier, "read")
        self.assertEqual(bit.position, 0)
        
        bit = self.named_bits.get_bit("write")
        self.assertEqual(bit.position, 1)
        
        # Несуществующий бит
        bit = self.named_bits.get_bit("nonexistent")
        self.assertIsNone(bit)
    
    def test_getitem(self):
        """Доступ по имени через []"""
        self.assertEqual(self.named_bits["read"], 0)
        self.assertEqual(self.named_bits["write"], 1)
        self.assertEqual(self.named_bits["execute"], 2)
        
        with self.assertRaises(KeyError):
            _ = self.named_bits["nonexistent"]
    
    def test_contains(self):
        """Проверка наличия имени"""
        self.assertIn("read", self.named_bits)
        self.assertIn("write", self.named_bits)
        self.assertIn("execute", self.named_bits)
        self.assertNotIn("nonexistent", self.named_bits)
    
    def test_iter(self):
        """Итерация по NamedBitList"""
        identifiers = [bit.identifier for bit in self.named_bits]
        self.assertEqual(identifiers, ["read", "write", "execute"])
    
    def test_len(self):
        """Длина списка"""
        self.assertEqual(len(self.named_bits), 3)
        class N(NamedBitList):
            bits = tuple()
        n = N()
        self.assertEqual(len(n), 0)
    
    def test_str(self):
        """Строковое представление"""
        self.assertEqual(str(self.named_bits), "{read(0), write(1), execute(2)}")

        class N(NamedBitList):
            bits = tuple()
        n = N()

        self.assertEqual(str(n), "{}")


# Создаем конкретные типы для тестирования
class Status(BitStringType):
    """Status ::= BIT STRING { read(0), write(1), execute(2) }"""
    named_bits = NamedBitList.from_dict({
        "read": 0,
        "write": 1,
        "execute": 2
    })


class Flags(BitStringType):
    """Flags ::= BIT STRING { flag0(0), flag1(1), flag2(2), flag3(3) }"""
    named_bits = NamedBitList.from_dict({
        "flag0": 0,
        "flag1": 1,
        "flag2": 2,
        "flag3": 3
    })


class EmptyBitString(BitStringType):
    """BIT STRING without named bits"""
    pass


class TestBitStringType(unittest.TestCase):
    """Тесты для BitStringType"""
    
    # ────────────────────────── ТЕСТЫ КОНСТРУКТОРОВ ──────────────────────────
    
    def test_from_bin(self):
        """Создание из двоичной строки"""
        bits = BitStringType.from_bin("101")
        self.assertEqual(bits.value, (1, 0, 1))
        self.assertEqual(bits.bit_length, 3)
        
        # С кавычками и B
        bits = BitStringType.from_bin("'101'B")
        self.assertEqual(bits.value, (1, 0, 1))
        
        # Пустая строка
        bits = BitStringType.from_bin("")
        self.assertEqual(bits.value, ())
                
        # Ошибки
        with self.assertRaises(ValueError):
            BitStringType.from_bin("102")  # не двоичная
        with self.assertRaises(ValueError):
            BitStringType.from_bin("'101'")  # неполный формат
    
    def test_from_hex(self):
        """Создание из шестнадцатеричной строки"""
        # 'A5'H = 10100101
        bits = BitStringType.from_hex("A5")
        self.assertEqual(bits.value, (1, 0, 1, 0, 0, 1, 0, 1))
        self.assertEqual(bits.bit_length, 8)
        
        # С кавычками и H
        bits = BitStringType.from_hex("'A5'H")
        self.assertEqual(bits.value, (1, 0, 1, 0, 0, 1, 0, 1))
        
        # С ограничением длины
        bits = BitStringType.from_hex("A5", bit_length=5)
        self.assertEqual(bits.value, (1, 0, 1, 0, 0))  # первые 5 бит
        
        # Пустая строка
        bits = BitStringType.from_hex("")
        self.assertEqual(bits.value, ())
        
        # Ошибки
        with self.assertRaises(ValueError):
            BitStringType.from_hex("XYZ")  # не hex
    
    def test_from_int(self):
        """Создание из целого числа"""
        # 42 = 101010 (6 бит)
        bits = BitStringType.from_int(42, 6)
        self.assertEqual(bits.value, (1, 0, 1, 0, 1, 0))
        
        # 0
        bits = BitStringType.from_int(0, 4)
        self.assertEqual(bits.value, (0, 0, 0, 0))
        
        # Максимальное значение
        bits = BitStringType.from_int(255, 8)
        self.assertEqual(bits.value, (1, 1, 1, 1, 1, 1, 1, 1))
            
    def test_from_bytes(self):
        """Создание из байтов"""
        # b'\xA5' = 10100101
        bits = BitStringType.from_bytes(b'\xA5')
        self.assertEqual(bits.value, (1, 0, 1, 0, 0, 1, 0, 1))
        
        # Многобайтовое значение
        bits = BitStringType.from_bytes(b'\x0F\xF0')
        expected = (0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0)
        self.assertEqual(bits.value, expected)
        
        # С ограничением длины
        bits = BitStringType.from_bytes(b'\xA5', bit_length=4)
        self.assertEqual(bits.value, (1, 0, 1, 0))  # первые 4 бита
        
        # Пустые байты
        bits = BitStringType.from_bytes(b'')
        self.assertEqual(bits.value, ())
    
    def test_empty_zeros_ones(self):
        """Создание пустых, нулевых и единичных строк"""
        # Пустая
        bits = BitStringType.empty()
        self.assertEqual(bits.value, ())
        self.assertEqual(bits.bit_length, 0)
        
        # Нули
        bits = BitStringType.zeros(5)
        self.assertEqual(bits.value, (0, 0, 0, 0, 0))
        self.assertEqual(bits.bit_length, 5)
        
        # Единицы
        bits = BitStringType.ones(3)
        self.assertEqual(bits.value, (1, 1, 1))
        self.assertEqual(bits.bit_length, 3)
    
    # ────────────────────────── ТЕСТЫ СВОЙСТВ ──────────────────────────
    
    def test_len_and_bool(self):
        """Длина и булево значение"""
        bits = BitStringType.from_bin("101")
        self.assertEqual(bits.bit_length, 3)
        self.assertTrue(bool(bits))
        
        bits = BitStringType.zeros(4)
        self.assertEqual(bits.bit_length, 4)
        self.assertFalse(bool(bits))
        
        bits = BitStringType.empty()
        self.assertEqual(bits.bit_length, 0)
        self.assertFalse(bool(bits))
    
    def test_bit_length_and_octet_length(self):
        """Длина в битах и октетах"""
        bits = BitStringType.from_bin("101")
        self.assertEqual(bits.bit_length, 3)
        self.assertEqual(bits.octet_length, 1)  # ceil(3/8) = 1
        
        bits = BitStringType.from_bin("1" * 12)
        self.assertEqual(bits.bit_length, 12)
        self.assertEqual(bits.octet_length, 2)  # ceil(12/8) = 2
    
    # ────────────────────────── ТЕСТЫ ДОСТУПА К БИТАМ ──────────────────────────
    
    def test_getitem_int(self):
        """Доступ по индексу"""
        bits = BitStringType.from_bin("1010")
        self.assertEqual(bits[0], 1)
        self.assertEqual(bits[1], 0)
        self.assertEqual(bits[2], 1)
        self.assertEqual(bits[3], 0)
        
        with self.assertRaises(IndexError):
            _ = bits[4]
        with self.assertRaises(IndexError):
            _ = bits[-1]
    
    def test_setitem_int(self):
        """Установка по индексу"""
        bits = BitStringType.from_bin("1010")
        bits[0] = 0
        self.assertEqual(bits.value, (0, 0, 1, 0))
        
        bits[2] = 0
        self.assertEqual(bits.value, (0, 0, 0, 0))
        
        bits[1] = 1
        self.assertEqual(bits.value, (0, 1, 0, 0))
        
        # bool значение
        bits[0] = True
        self.assertEqual(bits[0], 1)
        
        with self.assertRaises(IndexError):
            bits[4] = 1
    
    def test_getitem_str_with_named_bits(self):
        """Доступ по имени (с именованными битами)"""
        status = Status.from_bin("101")
        
        self.assertEqual(status["read"], 1)
        self.assertEqual(status["write"], 0)
        self.assertEqual(status["execute"], 1)
        
        # Бит вне длины - считается 0
        status = Status.from_bin("1")  # только read
        self.assertEqual(status["write"], 0)  # write позиция 1, нет бита
        
        # Нет именованных битов
        empty = EmptyBitString.from_bin("101")
        with self.assertRaises(KeyError):
            _ = empty["read"]
    
    def test_setitem_str_with_named_bits(self):
        """Установка по имени"""
        status = Status.zeros(3)
        
        status["read"] = 1
        self.assertEqual(status.value, (1, 0, 0))
        
        status["write"] = True
        self.assertEqual(status.value, (1, 1, 0))
        
        status["execute"] = 1
        self.assertEqual(status.value, (1, 1, 1))
        
        # Автоматическое расширение
        status = Status.from_bin("1")  # только бит 0
        status["execute"] = 1  # бит 2
        self.assertEqual(status.bit_length, 3)
        self.assertEqual(status.value, (1, 0, 1))
        
        # Нет именованных битов
        empty = EmptyBitString.zeros(3)
        with self.assertRaises(KeyError):
            empty["read"] = 1
    
    def test_get_set_clear_toggle(self):
        """Методы для работы с именованными битами"""
        status = Status.zeros(3)
                
        # set
        status.set("read")
        self.assertEqual(status["read"], 1)
        status.set("write", 0)
        self.assertEqual(status["write"], 0)
        
        # clear
        status.clear("read")
        self.assertEqual(status["read"], 0)
        
        # toggle
        status.toggle("execute")
        self.assertEqual(status["execute"], 1)
        status.toggle("execute")
        self.assertEqual(status["execute"], 0)
    
    def test_has_bit_has_any_has_all(self):
        """Проверки наличия битов"""
        status = Status.from_bin("101")
        
        self.assertTrue(status.has_bit("read"))
        self.assertFalse(status.has_bit("write"))
        self.assertTrue(status.has_bit("execute"))
        
        self.assertTrue(status.has_any("read", "write"))
        self.assertTrue(status.has_any("write", "execute"))
        self.assertFalse(status.has_any("write"))
        
        self.assertTrue(status.has_all("read", "execute"))
        self.assertFalse(status.has_all("read", "write"))
        self.assertTrue(status.has_all())  # пустой список = True
    
    # ────────────────────────── ТЕСТЫ ПРЕОБРАЗОВАНИЯ ──────────────────────────
    
    def test_to_bin(self):
        """Преобразование в двоичную строку"""
        bits = BitStringType.from_bin("101")
        self.assertEqual(bits.to_bin(), "101")
        
        bits = BitStringType.empty()
        self.assertEqual(bits.to_bin(), "")
        
        bits = BitStringType.zeros(4)
        self.assertEqual(bits.to_bin(), "0000")
    
    def test_hex(self):
        """Преобразование в шестнадцатеричную строку"""
        bits = BitStringType.from_bin("10100101")  # A5
        self.assertEqual(bits.hex(), "A5")
        
        bits = BitStringType.from_bin("101")  # 5 бит
        self.assertEqual(bits.hex(), "A0")  # pad to 10100000
        
        bits = BitStringType.empty()
        self.assertEqual(bits.hex(), "")
    
    def test_to_int(self):
        """Преобразование в целое число"""
        bits = BitStringType.from_bin("101")
        self.assertEqual(int(bits), 5)  # 101b = 5
        
        bits = BitStringType.from_bin("0")
        self.assertEqual(int(bits), 0)
        
        bits = BitStringType.from_bin("1" * 16)
        self.assertEqual(int(bits), 65535)
    
    def test_to_bytes(self):
        """Преобразование в байты"""
        bits = BitStringType.from_bin("10100101")
        self.assertEqual(bytes(bits), b'\xA5')
        
        bits = BitStringType.from_bin("101")  # 5 бит
        self.assertEqual(bytes(bits), b'\xA0')  # pad to 10100000
    
    def test_str_without_named_bits(self):
        """Строковое представление без именованных битов"""
        bits = BitStringType.from_bin("101")
        self.assertEqual(str(bits), "'101'B")
        
        bits = BitStringType.empty()
        self.assertEqual(str(bits), "''B")
    
    def test_str_with_named_bits(self):
        """Строковое представление с именованными битами"""
        status = Status.from_bin("101")
        self.assertEqual(str(status), "{read, execute}")
        
        status = Status.zeros(3)
        self.assertEqual(str(status), "{}")
        
        # Частично установленные
        status = Status.from_bin("100")
        self.assertEqual(str(status), "{read}")
        
        status = Status.from_bin("010")
        self.assertEqual(str(status), "{write}")
    
    def test_repr(self):
        """Представление для отладки"""
        bits = BitStringType.from_bin("101")
        self.assertEqual(repr(bits), "BitStringType('101')")
        
        status = Status.from_bin("101")
        self.assertEqual(repr(status), "Status('101')")
    
    # ────────────────────────── ТЕСТЫ БИТОВЫХ ОПЕРАЦИЙ ──────────────────────────
    
    def test_and(self):
        """Побитовое И"""
        bits1 = BitStringType.from_bin("1100")
        bits2 = BitStringType.from_bin("1010")
        result = bits1 & bits2
        self.assertEqual(result.value, (1, 0, 0, 0))
        
        # Разная длина
        bits1 = BitStringType.from_bin("110")
        bits2 = BitStringType.from_bin("1010")
        result = bits1 & bits2
        self.assertEqual(result.value, (1, 0, 0))  # только до длины меньшего
    
    def test_or(self):
        """Побитовое ИЛИ"""
        bits1 = BitStringType.from_bin("1100")
        bits2 = BitStringType.from_bin("1010")
        result = bits1 | bits2
        self.assertEqual(result.value, (1, 1, 1, 0))
        
        # Разная длина - расширяем до большего
        bits1 = BitStringType.from_bin("110")
        bits2 = BitStringType.from_bin("1010")
        result = bits1 | bits2
        self.assertEqual(result.value, (1, 1, 1, 0))  # bits1 расширен до 4 бит
    
    def test_xor(self):
        """Побитовое исключающее ИЛИ"""
        bits1 = BitStringType.from_bin("1100")
        bits2 = BitStringType.from_bin("1010")
        result = bits1 ^ bits2
        self.assertEqual(result.value, (0, 1, 1, 0))
    
    def test_invert(self):
        """Побитовое НЕ"""
        bits = BitStringType.from_bin("1010")
        result = ~bits
        self.assertEqual(result.value, (0, 1, 0, 1))
        
        # Пустая строка
        bits = BitStringType.empty()
        result = ~bits
        self.assertEqual(result.value, ())
    
    def test_lshift(self):
        """Сдвиг влево"""
        bits = BitStringType.from_bin("101")
        result = bits << 2
        self.assertEqual(result.value, (1, 0, 1, 0, 0))
        
        # Сдвиг на 0
        result = bits << 0
        self.assertEqual(result.value, (1, 0, 1))
        
        # Отрицательный сдвиг = сдвиг вправо
        result = bits << -1
        self.assertEqual(result.value, (1, 0))  # 101 >> 1 = 10
    
    def test_rshift(self):
        """Сдвиг вправо"""
        bits = BitStringType.from_bin("101")
        result = bits >> 1
        self.assertEqual(result.value, (1, 0))
        
        result = bits >> 2
        self.assertEqual(result.value, (1,))
        
        result = bits >> 3
        self.assertEqual(result.value, ())
        
        # Отрицательный сдвиг = сдвиг влево
        result = bits >> -1
        self.assertEqual(result.value, (1, 0, 1, 0))
    
    def test_add(self):
        """Конкатенация"""
        bits1 = BitStringType.from_bin("101")
        bits2 = BitStringType.from_bin("010")
        result = bits1 + bits2
        self.assertEqual(result.value, (1, 0, 1, 0, 1, 0))
        
        # Пустые строки
        bits1 = BitStringType.empty()
        result = bits1 + bits2
        self.assertEqual(result.value, (0, 1, 0))
    
    def test_getslice(self):
        """Срез"""
        bits = BitStringType.from_bin("101101")
        self.assertEqual(bits[1:4].value, (0, 1, 1))  # индексы 1,2,3
        self.assertEqual(bits[:3].value, (1, 0, 1))
        self.assertEqual(bits[3:].value, (1, 0, 1))
        self.assertEqual(bits[1:5:2].value, (0, 1))  # с шагом
    
    # ────────────────────────── ТЕСТЫ ИНФОРМАЦИИ ОБ ИМЕНАХ ──────────────────────────
    
    def test_get_named_bits_classmethod(self):
        """Получение NamedBitList через метод класса"""
        named_bits = Status.get_named_bits()
        self.assertIsNotNone(named_bits)
        self.assertEqual(len(named_bits), 3)
        self.assertIn("read", named_bits)
        
        named_bits = EmptyBitString.get_named_bits()
        self.assertIsNone(named_bits)
    
    def test_get_named_bit_classmethod(self):
        """Получение NamedBit через метод класса"""
        bit = Status.get_named_bit("read")
        self.assertIsNotNone(bit)
        self.assertEqual(bit.identifier, "read")
        self.assertEqual(bit.position, 0)
        
        bit = Status.get_named_bit("nonexistent")
        self.assertIsNone(bit)
        
        bit = EmptyBitString.get_named_bit("read")
        self.assertIsNone(bit)
    
    def test_available_bits_property(self):
        """Словарь доступных именованных битов"""
        status = Status.from_bin("101")
        available = status.available_bits
        self.assertEqual(available, {
            "read": 0,
            "write": 1,
            "execute": 2
        })
        
        empty = EmptyBitString.from_bin("101")
        self.assertEqual(empty.available_bits, {})
    
    def test_set_bits_property(self):
        """Словарь установленных именованных битов"""
        status = Status.from_bin("101")
        set_bits = status.set_bits
        self.assertEqual(set_bits, {
            "read": 0,
            "execute": 2
        })
        
        status = Status.zeros(3)
        self.assertEqual(status.set_bits, {})
        
        # Бит вне диапазона
        status = Status.from_bin("1")  # только read
        self.assertEqual(status.set_bits, {"read": 0})


class TestInheritance(unittest.TestCase):
    """Тесты наследования BitStringType"""
    
    def test_different_types_different_names(self):
        """Разные типы имеют разные именованные биты"""
        status = Status.from_bin("101")
        flags = Flags.from_bin("1010")
        
        # Status имеет read/write/execute
        self.assertEqual(status["read"], 1)
        self.assertEqual(status["execute"], 1)
        
        # Flags имеет flag0/flag1/flag2/flag3
        self.assertEqual(flags["flag0"], 1)
        self.assertEqual(flags["flag1"], 0)
        self.assertEqual(flags["flag2"], 1)
        self.assertEqual(flags["flag3"], 0)
        
        # Проверяем что у Status нет flag0
        with self.assertRaises(KeyError):
            _ = status["flag0"]
        
        # А у Flags нет read
        with self.assertRaises(KeyError):
            _ = flags["read"]
    
    def test_classvar_is_shared_per_class(self):
        """named_bits как ClassVar разделяется на уровне класса"""
        status1 = Status.from_bin("101")
        status2 = Status.from_bin("010")
        
        # Оба экземпляра имеют доступ к тем же именам
        self.assertEqual(status1.available_bits, status2.available_bits)
        self.assertIs(status1.__class__.named_bits, status2.__class__.named_bits)
    
    def test_operations_preserve_type(self):
        """Битовые операции сохраняют тип"""
        status1 = Status.from_bin("101")
        status2 = Status.from_bin("010")
        
        result_and = status1 & status2
        self.assertIsInstance(result_and, Status)
        self.assertEqual(result_and.value, (0, 0, 0))
        
        result_or = status1 | status2
        self.assertIsInstance(result_or, Status)
        self.assertEqual(result_or.value, (1, 1, 1))
        
        result_xor = status1 ^ status2
        self.assertIsInstance(result_xor, Status)
        self.assertEqual(result_xor.value, (1, 1, 1))
        
        result_not = ~status1
        self.assertIsInstance(result_not, Status)
        self.assertEqual(result_not.value, (0, 1, 0))
            
class TestEdgeCases(unittest.TestCase):
    """Тесты граничных случаев"""
    
    def test_empty_bit_string(self):
        """Пустая битовая строка"""
        empty = BitStringType.empty()
        self.assertEqual(empty.bit_length, 0)
        self.assertEqual(empty.to_bin(), "")
        self.assertEqual(empty.hex(), "")
        self.assertEqual(int(empty), 0)
        self.assertEqual(bytes(empty), b'')
        self.assertEqual(str(empty), "''B")
        
        # Операции с пустой строкой
        bits = BitStringType.from_bin("101")
        self.assertEqual((empty & bits).value, ())
        self.assertEqual((empty | bits).value, (1, 0, 1))
        self.assertEqual((empty + bits).value, (1, 0, 1))
    
    def test_very_long_bit_string(self):
        """Очень длинная битовая строка"""
        # 1000 бит
        long_bits = BitStringType.ones(1000)
        self.assertEqual(long_bits.bit_length, 1000)
        self.assertEqual(long_bits.octet_length, 125)  # 1000/8 = 125
        
        # Проверяем несколько битов
        self.assertEqual(long_bits[0], 1)
        self.assertEqual(long_bits[999], 1)
        
        # Сдвиг
        shifted = long_bits >> 500
        self.assertEqual(shifted.bit_length, 500)
        
        # Конвертация в int (должно работать)
        int_val = int(long_bits)
        self.assertEqual(int_val.bit_length(), 1000)
    
    def test_bit_operations_with_different_lengths(self):
        """Битовые операции с разной длиной"""
        short = BitStringType.from_bin("101")  # 3 бита
        long = BitStringType.from_bin("110011")  # 6 бит
        
        # AND - до меньшей длины
        result = short & long
        self.assertEqual(result.bit_length, 3)
        self.assertEqual(result.value, (1, 0, 0))
        
        # OR - до большей длины
        result = short | long
        self.assertEqual(result.bit_length, 6)
        self.assertEqual(result.value, (1, 1, 1, 0, 1, 1))  # 101 + ext = 101011 OR 110011 = 111011
        
        # XOR - до меньшей длины
        result = short ^ long
        self.assertEqual(result.bit_length, 3)
        self.assertEqual(result.value, (0, 1, 1))  # 101 ^ 110 = 011
    
    def test_named_bit_out_of_range(self):
        """Именованный бит вне текущей длины"""
        status = Status.from_bin("1")  # только бит 0
        
        # Чтение - должно вернуть 0
        self.assertEqual(status["write"], 0)  # бит 1
        self.assertEqual(status["execute"], 0)  # бит 2
        
        # Запись - должно расширить строку
        status["execute"] = 1
        self.assertEqual(status.bit_length, 3)
        self.assertEqual(status.value, (1, 0, 1))
        
        # Запись с большим отступом
        status["write"] = 1
        self.assertEqual(status.value, (1, 1, 1))
    
    def test_multiple_named_bits_same_position(self):
        """Два имени на одну позицию (возможно в ASN.1)"""
        class DuplicateBits(BitStringType):
            named_bits = NamedBitList.from_dict({
                "first": 0,
                "second": 0  # тот же бит
            })
        
        bits = DuplicateBits.from_bin("1")
        self.assertEqual(bits["first"], 1)
        self.assertEqual(bits["second"], 1)
        
        bits["first"] = 0
        self.assertEqual(bits["first"], 0)
        self.assertEqual(bits["second"], 0)
    
    def test_preserve_value_on_operations(self):
        """Операции не изменяют исходный объект"""
        original = Status.from_bin("101")
        original_copy = Status(original.value)  # копия
        
        result = original & Status.from_bin("010")
        
        # Оригинал не изменился
        self.assertEqual(original.value, (1, 0, 1))
        self.assertEqual(original_copy.value, original.value)
        
        # Результат - новый объект
        self.assertIsNot(result, original)
        self.assertNotEqual(result.value, original.value)


if __name__ == '__main__':
    unittest.main(verbosity=2)