"""
COSEM PDU Types Implementation
Based on COSEMpdu_GB83.txt (Green Book 8.3)
Implements A-XDR encoding/decoding according to IEC 61334-6
"""

from .x680 import (
    ValueRange,
)
from .axdr import ConstrainedIntegerType, IntegerType


class Integer8(ConstrainedIntegerType):
    constraint_spec = ValueRange(-128, 127)
    value: IntegerType


class Integer16(ConstrainedIntegerType):
    constraint_spec = ValueRange(-32768, 32767)
    value: IntegerType


class Integer32(ConstrainedIntegerType):
    constraint_spec = ValueRange(-2147483648, 2147483647)
    value: IntegerType


class Integer64(ConstrainedIntegerType):
    constraint_spec = ValueRange(-9223372036854775808, 9223372036854775807)
    value: IntegerType


class Unsigned8(ConstrainedIntegerType):
    constraint_spec = ValueRange(0, 255)
    value: IntegerType


class Unsigned16(ConstrainedIntegerType):
    constraint_spec = ValueRange(0, 65535)
    value: IntegerType


class Unsigned32(ConstrainedIntegerType):
    constraint_spec = ValueRange(0, 4294967295)
    value: IntegerType


class Unsigned64(ConstrainedIntegerType):
    constraint_spec = ValueRange(0, 18446744073709551615)
    value: IntegerType

# ============================================================================
# xDLMS APDU Types (COSEMpdu_GB83.txt)
# ============================================================================


class ObjectName(Integer16):
    """ObjectName"""
