from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from RsWaveform.meta import Meta
from RsWaveform.npz import Load, Save
from RsWaveform.parent_storage import ParentStorage
from RsWaveform.storage import Storage


@pytest.fixture
def reference() -> np.ndarray:  # type: ignore
    return np.array([0.2, 0.6]) + 1j * np.array([0.4, 0.8])


@pytest.fixture
def meta() -> Meta:
    return Meta(
        **{  # type: ignore[arg-type]
            "type": "SMU-WV",
            "copyright": "Rohde & Schwarz",
            "comment": "Test waveform file",
            "control_length": 2,
            "date": datetime(2023, 1, 5, 10, 3, 52),
            "clock": 100000000.0,
            "rms": 2.220459,
            "peak": 0.0,
            "samples": 2,
            "reflevel": -20.0,
        }
    )


@patch("RsWaveform.npz.save.np")
def test_save(mock_np: MagicMock, reference, meta):
    mock_np.real = np.real
    mock_np.imag = np.imag
    mock_np.iinfo = np.iinfo
    parent_storage = ParentStorage()
    storage = Storage()
    storage.data = reference
    storage.meta = meta
    parent_storage.storages[0] = storage
    saver = Save()
    saver.dtype = np.float16
    filename = "test.npz"
    saver.save(filename, parent_storage)
    call_args = mock_np.savez_compressed.call_args[1]
    assert filename == call_args.get("file")
    assert np.array_equal(
        np.real(reference).astype(np.float16), call_args.get("storages")[0]["i"]
    )
    assert np.array_equal(
        np.imag(reference).astype(np.float16), call_args.get("storages")[0]["q"]
    )
    assert meta._items == call_args.get("storages")[0]["meta"]  # pylint: disable=W0212


def test_load(reference, meta, reference_npz_file_name):
    loader = Load()
    loader.dtype = np.float16
    parent_storage = loader.load(reference_npz_file_name)
    storage = parent_storage.storages[0]
    assert np.array_equal(
        np.real(storage.data).astype(np.float16), np.real(reference).astype(np.float16)
    )
    assert np.array_equal(
        np.imag(storage.data).astype(np.float16), np.imag(reference).astype(np.float16)
    )
    assert storage.meta == meta


@patch("RsWaveform.npz.load.np")
def test_load_not_schema(mock_np, reference_npz_file_name):
    mock_np.load.return_value.get.return_value = None
    loader = Load()
    loader.dtype = np.float16
    with pytest.raises(ValueError):
        loader.load(reference_npz_file_name)


@patch("RsWaveform.npz.load.np")
def test_load_skip_i_is_none(mock_np, reference_npz_file_name, caplog):
    mock_np.zeros = np.zeros
    mock_np.load.return_value.get.return_value = [{"i": None}]
    loader = Load()
    loader.dtype = np.float16
    loader.load(reference_npz_file_name)
    assert caplog.record_tuples[0] == (
        "RsWaveform.npz.load",
        30,
        (
            f"Skipping index 0 of file {reference_npz_file_name}"
            " content because no i values are in it."
        ),
    )


@patch("RsWaveform.npz.load.np")
def test_load_q_is_none(mock_np, reference_npz_file_name):
    mock_np.zeros = np.zeros
    real_values = np.array([1, 2])
    mock_np.load.return_value.get.return_value = [{"i": real_values, "q": None}]
    loader = Load()
    loader.dtype = np.float16
    parent_storage = loader.load(reference_npz_file_name)
    storage = parent_storage.storages[0]
    assert np.array_equal(real_values, storage.data)


@patch("RsWaveform.npz.load.np")
def test_load_skip_i_and_q_not_equal(mock_np, reference_npz_file_name, caplog):
    mock_np.zeros = np.zeros
    mock_np.load.return_value.get.return_value = [
        {"i": np.array([1, 2]), "q": np.array([3, 4, 5])}
    ]
    loader = Load()
    loader.dtype = np.float16
    loader.load(reference_npz_file_name)
    assert caplog.record_tuples[0] == (
        "RsWaveform.npz.load",
        30,
        (
            f"Skipping index 0 of file {reference_npz_file_name}"
            " content because i value and q value lengths are not identical."
        ),
    )


def test_load_in_chunks(reference, meta, reference_npz_file_name):
    loader = Load()
    loader.dtype = np.float16
    parent_storage = loader.load_in_chunks(reference_npz_file_name, 1, 0)
    storage = parent_storage.storages[0]
    assert np.array_equal(
        np.real(storage.data[:1]).astype(np.float16),
        np.real(reference[:1]).astype(np.float16),
    )
    assert np.array_equal(
        np.imag(storage.data[:1]).astype(np.float16),
        np.imag(reference[:1]).astype(np.float16),
    )
    assert storage.meta == meta
    with pytest.raises(ValueError):
        loader.load_in_chunks(reference_npz_file_name, 10, 0)


def test_load_meta(meta, reference_npz_file_name):
    loader = Load()
    loader.dtype = np.float16
    parent_storage = loader.load_meta(reference_npz_file_name)
    storage = parent_storage.storages[0]
    assert storage.meta == meta
