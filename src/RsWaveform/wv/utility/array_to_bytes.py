"""Convert arrays to a binary representation."""

import logging

import numpy as np

LOGGER = logging.getLogger(__name__)


def pack_bool_array_to_bytes(bool_array: np.ndarray) -> bytes:
    """Pack array values into a binary representation.

    Args:
        bool_array (np.ndarray): Array containing boolean values in integer
            representation.

    Raises:
        ValueError: If any of the number of rows or columns does not match 4.

    Returns:
        bytes: Packed list as bytes.
    """
    if len(bool_array.shape) != 2:
        raise ValueError("Array should have just two dimensions.")

    # Check if the number of rows is always 4.
    is_four = [x == 4 for x in bool_array.shape]
    if not any(is_four):
        raise ValueError("Number of rows must be four for packing into bytes")

    # Check if array is in column-wise major order, transpose if necessary
    if is_four[0]:
        bool_array = bool_array.T

    # We need an even number of samples for the columns
    if bool_array.shape[0] % 2 != 0:
        bool_array = np.concatenate([bool_array, np.zeros((1, 4))], axis=0)

    # Convert boolean array to integers (0 or 1)
    int_array = bool_array.astype(np.uint8)
    int_array = int_array.reshape((int(int_array.shape[0] / 2), 8))

    # Pack two columns into a single byte
    packed = np.packbits(int_array, axis=1, bitorder="big")
    packed_bytes = packed.tobytes()

    return packed_bytes


def unpack_bytes_to_bool_array(packed_bytes: bytes, num_samples: int) -> np.ndarray:
    """Unpack array values from a binary representation.

    Args:
        packed_bytes (bytes): Packed list as bytes.
        num_samples (int): The numnber of samples to extract.

    Returns:
        np.ndarray: The unpacked list.
    """
    # Unpack bytes to numpy array of integers (0 or 1)
    int_array = np.frombuffer(packed_bytes, dtype=np.uint8)

    # Unpack each byte to 8 bits (columns)
    bool_array = np.unpackbits(int_array, axis=0, bitorder="big")
    bool_array = bool_array.reshape(int(bool_array.shape[0] / 4), 4).T

    # Trim extra bits if the number of samples is not a multiple of 4
    bool_array = bool_array[:, :num_samples]

    return bool_array
