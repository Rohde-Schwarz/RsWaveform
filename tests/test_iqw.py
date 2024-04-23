import io

import numpy as np
import pytest

from RsWaveform import Iqw
from RsWaveform.iqw.load import Load
from RsWaveform.iqw.save import Save
from RsWaveform.meta import Meta
from RsWaveform.parent_storage import ParentStorage


@pytest.fixture
def reference() -> np.ndarray:
    return np.array([0.2, 0.6]) + 1j * np.array([0.4, 0.8])


@pytest.fixture
def reference_huge() -> np.ndarray:
    return np.concatenate((np.array([0.2 + 0.6j] * 5), np.array([0.5 + 0.5j] * 5)))


def test_loader_load(reference_iqw_file_name, reference):
    loader = Load()
    parent_storage = loader.load(reference_iqw_file_name)
    assert parent_storage.number_of_storages() == 1
    assert parent_storage.storages[0].data == pytest.approx(reference, rel=0.0001)
    assert isinstance(parent_storage.storages[0].meta, Meta)


def test_saver_save(reference_iqw_file_name, reference: np.ndarray):
    saver = Save()
    parent_storage = ParentStorage()
    parent_storage.storages[0].data = reference
    with io.BytesIO() as file:
        saver.save(file, parent_storage)
        bins = file.getvalue()
    with open(reference_iqw_file_name, "rb") as file:
        ref = file.read()
    assert bins == ref


def test_loader_chunks(reference_iqw_file_name_huge: str, reference_huge: np.ndarray):
    loader = Load()
    parent_storage = loader.load_in_chunks(reference_iqw_file_name_huge, 10, 5)
    assert len(parent_storage.storages) == 1
    assert np.real(parent_storage.storages[0].data).astype(np.float16) == pytest.approx(
        np.real(reference_huge).astype(np.float16), rel=0.00000001
    )
    assert np.imag(parent_storage.storages[0].data).astype(np.float16) == pytest.approx(
        np.imag(reference_huge).astype(np.float16), rel=0.00000001
    )
    assert isinstance(parent_storage.storages[0].meta, Meta)


def test_loader_only_meta(reference_iqw_file_name: str):
    loader = Load()
    with pytest.raises(Exception):
        loader.load_meta(reference_iqw_file_name)


def test_load(reference_iqw_file_name, reference):
    iqw = Iqw(file=reference_iqw_file_name)
    assert iqw.parent_storage.number_of_storages() == 1
    assert iqw.filename == reference_iqw_file_name
    assert iqw.data[0] == pytest.approx(reference, rel=0.0001)
    assert isinstance(iqw.meta[0], Meta)


def test_load_chunks(reference_iqw_file_name_huge, reference_huge):
    iqw = Iqw(file=reference_iqw_file_name_huge, nr_samples=10, samples_offset=5)
    assert iqw.parent_storage.number_of_storages() == 1
    assert iqw.filename == reference_iqw_file_name_huge
    assert iqw.data[0] == pytest.approx(reference_huge, rel=0.0001)
    assert isinstance(iqw.meta[0], Meta)


def test_save(reference_iqw_file_name: str, reference: np.ndarray):
    np.random.seed(900)
    iqtar = Iqw()
    iqtar.data[0] = reference
    with io.BytesIO() as file:
        iqtar.save(file)
        bins = file.getvalue()
    with open(reference_iqw_file_name, "rb") as file:
        ref = file.read()
    assert bins == ref
