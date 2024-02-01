import numpy as np
import pytest

from RsWaveform.wv.utility.array_to_bytes import (
    pack_bool_array_to_bytes,
    unpack_bytes_to_bool_array,
)


@pytest.fixture
def example_bool_array():
    return np.array([[0, 1], [1, 0], [1, 0], [0, 1]])


@pytest.mark.parametrize(
    "mode",
    [None, "append", "transposed"],
)
def test_pack_unpack_round_trip(mode, example_bool_array):
    if mode == "append":
        bool_array = np.concatenate([example_bool_array, np.ones((4, 1))], axis=1)
        reference_array = bool_array
        samples = bool_array.shape[1]
    elif mode == "transposed":
        bool_array = example_bool_array.T
        reference_array = bool_array.T
        samples = bool_array.shape[0]
    else:
        bool_array = example_bool_array
        reference_array = bool_array
        samples = bool_array.shape[1]
    packed_bytes = pack_bool_array_to_bytes(bool_array)
    unpacked_bool_array = unpack_bytes_to_bool_array(packed_bytes, samples)

    assert np.array_equal(reference_array, unpacked_bool_array)


def test_invalid_rows():
    invalid_bool_array = np.array([[0, 1], [1, 0], [1, 0]])
    with pytest.raises(
        ValueError, match="Number of rows must be four for packing into bytes"
    ):
        pack_bool_array_to_bytes(invalid_bool_array)


def test_pack(example_bool_array):
    packed_bytes = b"i"  # Corresponds to [0, 1, 1, 0, 1, 0, 0, 1]
    assert pack_bool_array_to_bytes(example_bool_array) == packed_bytes


def test_unpack(example_bool_array):
    packed_bytes = b"i"  # Corresponds to [0, 1, 1, 0, 1, 0, 0, 1]
    num_samples = 2
    unpacked_bool_array = unpack_bytes_to_bool_array(packed_bytes, num_samples)

    assert np.array_equal(unpacked_bool_array, example_bool_array)
