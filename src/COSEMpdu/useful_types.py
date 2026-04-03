"""
COSEM PDU Types Implementation
Based on COSEMpdu_GB83.txt (Green Book 8.3)
Implements A-XDR encoding/decoding according to IEC 61334-6
"""

from dataclasses import dataclass
from .x680 import (
    ValueRange,
)
from .axdr import ConstrainedIntegerType, IntegerType


@dataclass
class Integer8(ConstrainedIntegerType):
    constraint_spec = ValueRange(-128, 127)
    value: IntegerType


@dataclass
class Integer16(ConstrainedIntegerType):
    constraint_spec = ValueRange(-32768, 32767)
    value: IntegerType


@dataclass
class Integer32(ConstrainedIntegerType):
    constraint_spec = ValueRange(-2147483648, 2147483647)
    value: IntegerType


@dataclass
class Integer64(ConstrainedIntegerType):
    constraint_spec = ValueRange(-9223372036854775808, 9223372036854775807)
    value: IntegerType


@dataclass
class Unsigned8(ConstrainedIntegerType):
    constraint_spec = ValueRange(0, 255)
    value: IntegerType


@dataclass
class Unsigned16(ConstrainedIntegerType):
    constraint_spec = ValueRange(0, 65535)
    value: IntegerType


@dataclass
class Unsigned32(ConstrainedIntegerType):
    constraint_spec = ValueRange(0, 4294967295)
    value: IntegerType


@dataclass
class Unsigned64(ConstrainedIntegerType):
    constraint_spec = ValueRange(0, 18446744073709551615)
    value: IntegerType

# ============================================================================
# xDLMS APDU Types (COSEMpdu_GB83.txt)
# ============================================================================


@dataclass
class ObjectName(Integer16):
    """ObjectName"""
