"""
Common test utilities for COSEMpdu tests.

Provides a shared encode/decode helper that:
- encodes a value into a ByteBuffer
- decodes it back using the given type class
- returns the decoded value
"""
import sys
sys.path.insert(0, "src")

from typing import Any, Type

from COSEMpdu.byte_buffer import ByteBuffer


def check_encode_decode(value: Any, type_cls: Type[Any], buffer_size: int = 1024) -> Any:
    """Encode value to buffer, decode back, assert not None, return decoded.

    Args:
        value: The fully constructed tagged/typed object to encode
               (must have a `put(buffer)` method).
        type_cls: The type class with a `get(buffer)` classmethod for decoding.
        buffer_size: Size of the ByteBuffer to allocate.

    Returns:
        The decoded object of type `type_cls`.
    """
    buffer = ByteBuffer.allocate(buffer_size)
    encoded = value.put(buffer)
    assert encoded > 0, f"Encoding produced {encoded} bytes, expected > 0"
    decoded_buffer = buffer.extract()
    decoded = type_cls.get(decoded_buffer)
    assert decoded is not None, "Decoding returned None"
    return decoded