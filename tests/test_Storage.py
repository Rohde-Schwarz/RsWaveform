try:
    import msgpack as pickle
    import msgpack_numpy as m

    m.patch()
except ImportError:
    import pickle  # type: ignore

from datetime import datetime

import numpy as np
import pytest

from RsWaveform.meta import Meta
from RsWaveform.parent_storage import ParentStorage
from RsWaveform.storage import Storage, encode_datetime, msgpack_import


@pytest.fixture
def reference_now() -> datetime:
    return datetime.now()


@pytest.fixture
def reference_meta() -> dict:
    return {}


@pytest.fixture
def reference_name() -> str:
    return "test.wv"


@pytest.fixture
def reference_data() -> np.ndarray:
    return np.array([1 + 1j, 1 - 1j, 1 + 0j, -1 + 1j])


@pytest.fixture
def reference_serde(
    reference_now, reference_meta, reference_data, reference_name
) -> dict:
    return {
        "data": reference_data,
        "meta": reference_meta,
        "filename": reference_name,
        "timestamp": reference_now,
    }


def test_creation():
    storage = Storage()
    assert isinstance(storage.data, np.ndarray)
    assert np.array_equal(storage.data, np.zeros((1024,), dtype=np.complex128))
    assert isinstance(storage.meta, Meta)


def test_creation_parent_storage():
    parent_storage = ParentStorage()
    assert isinstance(parent_storage.timestamp, datetime)
    assert parent_storage.timestamp.date() == datetime.now().date()


def test_create_from_serialize(
    reference_serde, reference_meta, reference_now, reference_data, reference_name
):
    if msgpack_import:
        bins = pickle.dumps(reference_serde, default=encode_datetime)
    else:
        bins = pickle.dumps(reference_serde)
    storage = Storage(bins)
    assert np.array_equal(storage.data, reference_data)
    assert storage.meta == reference_meta


def test_serialize(
    reference_serde, reference_meta, reference_now, reference_data, reference_name
):
    storage = Storage()
    storage.data = reference_data
    storage.meta = reference_meta
    storage.filename = reference_name  # type: ignore[attr-defined]
    storage.timestamp = reference_now  # type: ignore[attr-defined]
    bins = storage.serialize()
    if msgpack_import:
        reference = pickle.dumps(reference_serde, default=encode_datetime)
    else:
        reference = pickle.dumps(reference_serde)
    assert bins == reference


def test_deserialize(
    reference_serde, reference_meta, reference_now, reference_data, reference_name
):
    if msgpack_import:
        bins = pickle.dumps(reference_serde, default=encode_datetime)
    else:
        bins = pickle.dumps(reference_serde)
    storage = Storage()
    storage.deserialize(bins)
    assert np.array_equal(storage.data, reference_data)
    assert storage.meta == reference_meta
    assert storage.filename == reference_name  # type: ignore[attr-defined]
    assert storage.timestamp == reference_now  # type: ignore[attr-defined]
