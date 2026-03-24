"""
ASN.1 GeneralizedTime Type Definition (X.680 §42)
This module defines the abstract syntax for GeneralizedTime types.
Encoding/decoding (BER) is handled separately in x690 module.

Standards:
- X.680 §42: GeneralizedTime type definition
- X.690 §8.23: GeneralizedTime encoding rules (handled in x690)
- X.680 Table 1: UNIVERSAL tag 24
"""
from typing import Self, Optional
from dataclasses import dataclass
from .type import Transcript, UsefulType, STRING


@dataclass
class GeneralizedTime(UsefulType):
    """
    ASN.1 GeneralizedTime type (X.680 §42).

    GeneralizedTime represents a calendar date and time of day with
    optional fractional seconds and time zone information.

    Example ASN.1:
        CreationTime ::= GeneralizedTime
        ExpiryTime ::= GeneralizedTime

    Attributes:
        value: String representation in ASN.1 format
               Format: YYYYMMDDHHMMSS[.fff][Z|±HHMM]
               - YYYY: 4-digit year (0000-9999)
               - MM: 2-digit month (01-12)
               - DD: 2-digit day (01-31)
               - HH: 2-digit hour (00-23)
               - MM: 2-digit minute (00-59)
               - SS: 2-digit second (00-60, 60 for leap second)
               - .fff: Optional fractional seconds (1+ digits)
               - Z: UTC time, or ±HHMM: local time offset

    Note:
        - More flexible than UTCTime (supports 4-digit years)
        - Supports fractional seconds precision
        - Supports explicit time zone offsets
        - BER encoding: VisibleString with UNIVERSAL tag 24
        - For DLMS/COSEM, typically used without fractional seconds

    References:
        - X.680 §42: GeneralizedTime notation
        - X.680 Table 1: UNIVERSAL tag 24
        - X.690 §8.23: GeneralizedTime BER encoding
        - IEC 61334-6 §6.12: DLMS GeneralizedTime usage

    Usage pattern:
        # Create from string
        time = GeneralizedTimeType("20240115120000Z")

        # Create with fractional seconds
        time = GeneralizedTimeType("20240115120000.5Z")

        # Create with time zone offset
        time = GeneralizedTimeType("20240115120000+0300")

        # Convert to transcript
        transcript = time.to_transcript()  # "20240115120000Z"

    GeneralizedTime value in ASN.1 string format.

    Valid formats:
    - Basic: YYYYMMDDHHMMSSZ (UTC time)
    - With offset: YYYYMMDDHHMMSS±HHMM (local time)
    - With fractions: YYYYMMDDHHMMSS.fffZ (fractional seconds)

    Note:
        - No separators between components (except optional decimal point)
        - Must terminate with Z or ±HHMM
        - Fractional seconds optional but must have at least one digit
    """
    value: STRING

    @classmethod
    def default(cls) -> Self:
        return cls("00000101000000Z")  # Default to 0000-01-01T00:00:00Z, though this may be invalid

    def __post_init__(self) -> None:
        """
        Validate GeneralizedTime format per X.680 §42.3.
        Raises:
            ValueError: If format is invalid or components out of range
        """
        self._validate_format()

    def _validate_format(self) -> None:
        """
        Validate GeneralizedTime string format.

        Checks:
        - Minimum length (14 chars + timezone)
        - Numeric components
        - Valid ranges for each component
        - Timezone format (Z or ±HHMM)
        - Fractional seconds format (if present)

        Raises:
            ValueError: If validation fails
        """
        value = self.value

        # Minimum length: YYYYMMDDHHMMSS + timezone = 15 chars
        if len(value) < 15:
            raise ValueError(
                f"GeneralizedTime too short: {len(value)} chars, "
                f"minimum 15 (YYYYMMDDHHMMSS+timezone)"
            )

        # Extract components
        try:
            year = int(value[0:4])
            month = int(value[4:6])
            day = int(value[6:8])
            hour = int(value[8:10])
            minute = int(value[10:12])
            second = int(value[12:14])
        except ValueError as e:
            raise ValueError(f"GeneralizedTime contains non-numeric components: {e}")

        # Validate ranges
        if not (0 <= year <= 9999):
            raise ValueError(f"Year out of range (0-9999): {year}")
        if not (1 <= month <= 12):
            raise ValueError(f"Month out of range (1-12): {month}")
        if not (1 <= day <= 31):
            raise ValueError(f"Day out of range (1-31): {day}")
        if not (0 <= hour <= 23):
            raise ValueError(f"Hour out of range (0-23): {hour}")
        if not (0 <= minute <= 59):
            raise ValueError(f"Minute out of range (0-59): {minute}")
        if not (0 <= second <= 60):  # 60 for leap second
            raise ValueError(f"Second out of range (0-60): {second}")

        # Validate timezone
        remainder = value[14:]
        if remainder.endswith("Z"):
            # UTC time - check for fractional seconds before Z
            frac_part = remainder[:-1]
            if frac_part and not frac_part.startswith("."):
                raise ValueError(
                    f"Invalid fractional seconds format: {frac_part}, "
                    f"must start with '.'"
                )
            if frac_part:
                self._validate_fractional_seconds(frac_part[1:])
        elif remainder[0] in ("+", "-"):
            # Timezone offset ±HHMM
            if len(remainder) != 5:
                raise ValueError(
                    f"Invalid timezone offset format: {remainder}, "
                    f"must be ±HHMM (5 chars)"
                )
            try:
                tz_hour = int(remainder[1:3])
                tz_min = int(remainder[3:5])
                if not (0 <= tz_hour <= 23):
                    raise ValueError(f"Timezone hour out of range (0-23): {tz_hour}")
                if not (0 <= tz_min <= 59):
                    raise ValueError(f"Timezone minute out of range (0-59): {tz_min}")
            except ValueError as e:
                raise ValueError(f"Invalid timezone offset: {e}")
        else:
            raise ValueError(f"GeneralizedTime must end with 'Z' or ±HHMM, got: {remainder}")

    def _validate_fractional_seconds(self, frac: str) -> None:
        """
        Validate fractional seconds component.

        Args:
            frac: Fractional seconds string (digits only)

        Raises:
            ValueError: If format is invalid
        """
        if not frac:
            raise ValueError("Fractional seconds must have at least one digit")
        if not frac.isdigit():
            raise ValueError(f"Fractional seconds must be numeric: {frac}")

    @classmethod
    def parse(cls, value: Transcript) -> Self:
        """
        Construct GeneralizedTime from transcript representation.

        Args:
            value: String representation like "20240115120000Z"

        Returns:
            GeneralizedTimeType instance

        Raises:
            ValueError: If string cannot be parsed as GeneralizedTime
            TypeError: If value is not a string

        Example:
            >>> GeneralizedTimeType.parse("20240115120000Z")
            GeneralizedTimeType(value='20240115120000Z')
        """
        if isinstance(value, list):
            raise TypeError(
                "GeneralizedTime cannot be parsed from list, expected string"
            )

        if not isinstance(value, str):
            raise TypeError(
                f"GeneralizedTime requires string value, got {type(value)}"
            )

        return cls(value)

    def to_transcript(self) -> Transcript:
        """
        Convert to string representation.

        Returns:
            String in ASN.1 GeneralizedTime format

        Example:
            >>> GeneralizedTimeType("20240115120000Z").to_transcript()
            '20240115120000Z'
        """
        return self.value

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns:
            GeneralizedTime value string

        Example:
            >>> str(GeneralizedTimeType("20240115120000Z"))
            '20240115120000Z'
        """
        return self.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value!r})"

    def __eq__(self, other: object) -> bool:
        """
        Compare GeneralizedTime values for equality.

        Two GeneralizedTime values are equal if their string
        representations are identical (note: does not normalize
        timezones - "20240115120000Z" != "20240115150000+0300"
        even though they represent the same instant).

        Args:
            other: Another GeneralizedTimeType instance

        Returns:
            True if string values match exactly
        """
        if not isinstance(other, GeneralizedTime):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __lt__(self, other: "GeneralizedTime") -> bool:
        """
        Compare GeneralizedTime values lexicographically.

        Note: This is a string comparison, not a temporal comparison.
        For accurate temporal comparison, convert to datetime first.

        Args:
            other: Another GeneralizedTimeType instance

        Returns:
            True if self.value < other.value (string comparison)
        """
        if not isinstance(other, GeneralizedTime):
            return NotImplemented
        return self.value < other.value

    @property
    def year(self) -> int:
        """Return 4-digit year (0000-9999)."""
        return int(self.value[0:4])

    @property
    def month(self) -> int:
        """Return month (01-12)."""
        return int(self.value[4:6])

    @property
    def day(self) -> int:
        """Return day (01-31)."""
        return int(self.value[6:8])

    @property
    def hour(self) -> int:
        """Return hour (00-23)."""
        return int(self.value[8:10])

    @property
    def minute(self) -> int:
        """Return minute (00-59)."""
        return int(self.value[10:12])

    @property
    def second(self) -> int:
        """Return second (00-60)."""
        return int(self.value[12:14])

    @property
    def has_fractional_seconds(self) -> bool:
        """Check if fractional seconds are present."""
        remainder = self.value[14:]
        if remainder.endswith("Z"):
            return "." in remainder
        if remainder[0] in ("+", "-"):
            frac_part = remainder[1:]
            return "." in frac_part
        return False

    @property
    def fractional_seconds(self) -> Optional[str]:
        """
        Return fractional seconds string (without decimal point).

        Returns:
            Fractional seconds digits or None if not present

        Example:
            >>> GeneralizedTimeType("20240115120000.5Z").fractional_seconds
            '5'
            >>> GeneralizedTimeType("20240115120000Z").fractional_seconds
            None
        """
        remainder = self.value[14:]
        if remainder.endswith("Z"):
            frac_part = remainder[:-1]
            if "." in frac_part:
                return frac_part.split(".")[1]
        elif remainder[0] in ("+", "-"):
            tz_start = remainder[0:5]
            frac_part = remainder[5:]
            if frac_part and frac_part.startswith("."):
                return frac_part[1:]
        return None

    @property
    def is_utc(self) -> bool:
        """Check if time is in UTC (ends with 'Z')."""
        return self.value.endswith("Z")

    @property
    def timezone_offset(self) -> Optional[str]:
        """
        Return timezone offset string (±HHMM) or None if UTC.

        Returns:
            Timezone offset like "+0300" or None for UTC

        Example:
            >>> GeneralizedTimeType("20240115120000+0300").timezone_offset
            '+0300'
            >>> GeneralizedTimeType("20240115120000Z").timezone_offset
            None
        """
        if self.is_utc:
            return None
        remainder = self.value[14:]
        if remainder[0] in ("+", "-"):
            # Check for fractional seconds before timezone
            if "." in remainder:
                frac_end = remainder.index(".")
                # Find timezone after fractional seconds
                tz_start = remainder[frac_end:]
                for i, c in enumerate(tz_start):
                    if c in ("+", "-") and i > 0:
                        return tz_start[i:i + 5]
            else:
                return remainder[0:5]
        return None

    def to_utc(self) -> "GeneralizedTime":
        """
        Convert to UTC representation (requires timezone offset).

        Note: This is a string manipulation only. For accurate
        timezone conversion, use Python's datetime module.

        Returns:
            New GeneralizedTimeType with 'Z' suffix

        Raises:
            ValueError: If no timezone offset present (already UTC)
        """
        if self.is_utc:
            return self

        # For proper timezone conversion, external library needed
        # This is a placeholder that just changes the suffix
        raise NotImplementedError(
            "Timezone conversion requires datetime library. "
            "Use .value property and convert externally."
        )

    def truncate_to(self, precision: str) -> "GeneralizedTime":
        """
        Truncate GeneralizedTime to specified precision.

        Args:
            precision: One of 'year', 'month', 'day', 'hour', 'minute', 'second'

        Returns:
            New GeneralizedTimeType truncated to precision

        Raises:
            ValueError: If precision is invalid

        Example:
            >>> time = GeneralizedTimeType("20240115120000Z")
            >>> time.truncate_to('minute')
            GeneralizedTimeType(value='202401151200Z')
        """
        valid_precisions = ("year", "month", "day", "hour", "minute", "second")
        if precision not in valid_precisions:
            raise ValueError(f"Invalid precision: {precision}, must be one of {valid_precisions}")

        # Determine cutoff position
        cutoffs = {
            "year": 4,
            "month": 6,
            "day": 8,
            "hour": 10,
            "minute": 12,
            "second": 14,
        }

        cutoff = cutoffs[precision]
        base = self.value[:cutoff]

        # Add timezone (preserve original)
        remainder = self.value[14:]
        if remainder.endswith("Z"):
            # Handle fractional seconds
            if "." in remainder:
                tz = "Z"
            else:
                tz = "Z"
        elif remainder[0] in ("+", "-"):
            tz = remainder[0:5]
        else:
            tz = "Z"  # Default to UTC if malformed

        return type(self)(base + tz)
