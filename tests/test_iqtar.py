import datetime
import io
import os
import tarfile
import typing
from pathlib import Path

import numpy as np
import pytest

from RsWaveform import IqTar
from RsWaveform.iqtar.load import Load
from RsWaveform.iqtar.save import Save
from RsWaveform.meta import Meta
from RsWaveform.parent_storage import ParentStorage
from RsWaveform.storage import Storage


@pytest.mark.parametrize("output_kind", ["buffer", "path", "string", "tar"])
def test_save_without_home_directory(
    tmp_path, monkeypatch, reference, meta, output_kind
):
    home = tmp_path / "new-user"
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    data = ParentStorage()
    data.storages[0].data = reference
    data.storages[0].meta = meta
    archive_path = tmp_path / "roundtrip.iq.tar"
    buffer = io.BytesIO()
    target: typing.Any
    if output_kind == "buffer":
        target = buffer
    elif output_kind == "path":
        target = archive_path
    elif output_kind == "string":
        target = str(archive_path)
    else:
        target = tarfile.open(fileobj=buffer, mode="w:")

    Save().save(target, data)
    if output_kind == "tar":
        assert not target.closed
        target.close()
    if output_kind in ["buffer", "tar"]:
        assert not buffer.closed
        archive_path.write_bytes(buffer.getvalue())
    actual = Load().load(archive_path)
    assert actual.storages[0].data == pytest.approx(reference, rel=0.0001)
    assert actual.storages[0].meta["clock"] == meta["clock"]
    assert not home.exists()
    assert sorted(p.name for p in tmp_path.iterdir()) == [archive_path.name]


def test_save_cleans_staging_files_on_error(tmp_path, monkeypatch, reference):
    data = ParentStorage()
    data.storages[0].data = reference
    # An invalid clock makes writing XML fail after writing the samples.
    data.storages[0].meta["clock"] = 0.0
    staged = []
    original_write_data = Save._write_data

    def record_write_data(filename, parent, scale):
        staged.append(filename)
        return original_write_data(filename, parent, scale)

    monkeypatch.setattr(Save, "_write_data", staticmethod(record_write_data))
    with pytest.raises(ValueError, match="Clock is a mandatory parameter"):
        Save().save(str(tmp_path / "incomplete.iq.tar"), data)
    assert staged
    assert all(not file.exists() for file in staged)
    assert list(tmp_path.iterdir()) == []


@pytest.fixture
def reference() -> np.ndarray:
    return np.array([0.2, 0.6]) + 1j * np.array([0.4, 0.8])


@pytest.fixture
def reference_huge() -> np.ndarray:
    return np.concatenate((np.array([0.2 + 0.6j] * 5), np.array([0.5 + 0.5j] * 5)))


@pytest.fixture()
def meta():
    _meta = Meta(
        **{  # type: ignore[arg-type]
            "clock": 10000.0,
            "scalingfactor": 1.0,
            "datatype": "float32",
            "format": "complex",
            "name": "Python iq.tar Writer (iqdata.py)",
            "comment": "RS WaveForm, TheAE-RA",
            "samples": 2,
            "date": datetime.datetime(2023, 3, 1, 10, 19, 37, 43312),
        }
    )
    return _meta


@pytest.fixture()
def meta_multi_channel():
    _meta = Meta(
        **{  # type: ignore[arg-type]
            "clock": 10000.0,
            "scalingfactor": 1.0,
            "datatype": "float32",
            "format": "complex",
            "name": "Python iq.tar Writer",
            "comment": "RS WaveForm, TheAE-RA",
            "samples": 2,
            "date": datetime.datetime(2023, 3, 3, 8, 9, 25, 842264),
        }
    )
    return _meta


def test_loader_load(reference_iqtar_file_name: str, reference: np.ndarray, meta: Meta):
    loader = Load()
    parent_storage = loader.load(reference_iqtar_file_name)
    assert parent_storage.number_of_storages() == 1
    assert parent_storage.storages[0].data == pytest.approx(reference, rel=0.0001)
    assert meta == parent_storage.storages[0].meta


def test_loader_load_multi_channel(
    reference_iqtar_file_name_multi_channel: str,
    reference: np.ndarray,
    meta_multi_channel: dict,
):
    loader = Load()
    parent_storage = loader.load(reference_iqtar_file_name_multi_channel)
    assert parent_storage.number_of_storages() > 1
    assert parent_storage.storages[0].meta == meta_multi_channel


def test_loader_chunk(
    reference_iqtar_file_name_huge: str, reference_huge: np.ndarray, meta: dict
):
    loader = Load()
    parent_storage = loader.load_in_chunks(reference_iqtar_file_name_huge, 10, 5)
    assert parent_storage.number_of_storages() == 1
    assert parent_storage.storages[0].data == pytest.approx(reference_huge, rel=0.0001)
    meta["date"] = datetime.datetime(2023, 4, 11, 10, 32, 30, 586434)
    meta["name"] = "Python iq.tar Writer"
    meta["samples"] = 100015
    assert meta == parent_storage.storages[0].meta


def test_loader_only_meta(reference_iqtar_file_name: str, meta: dict):
    loader = Load()
    parent_storage = loader.load_meta(reference_iqtar_file_name)
    meta["datafilename"] = "dummy.complex.1ch.float32"
    assert parent_storage.storages[0].meta == meta


def test_loader_load_iso_time(
    reference_iqtar_file_name_iso_time: str,
):
    loader = Load()
    parent_storage = loader.load_meta(reference_iqtar_file_name_iso_time)
    expected_datetime = datetime.datetime(
        2025,
        10,
        7,
        16,
        33,
        36,
        997730,
        tzinfo=datetime.timezone(datetime.timedelta(seconds=7200)),
    )
    assert parent_storage.storages[0].meta["date"] == expected_datetime


def test_saver_save(reference_iqtar_file_name, reference: np.ndarray, meta: Meta):
    saver = Save()
    parent_storage = ParentStorage()
    parent_storage.storages[0].data = reference
    parent_storage.storages[0].meta = meta
    dirname = os.path.dirname(__file__)
    tmp_folder = os.path.join(dirname, "data", "dummy_tmp.iq.tar")
    saver.save(tmp_folder, parent_storage)
    with open(reference_iqtar_file_name, "rb") as file:
        bins = file.read()
    os.remove(tmp_folder)
    with open(reference_iqtar_file_name, "rb") as file:
        ref = file.read()
    assert bins == ref


def test_saver_save_multi_channel(
    reference_iqtar_file_name_multi_channel: str,
    reference: np.ndarray,
    meta_multi_channel: Meta,
):
    saver = Save()
    parent_storage = ParentStorage()
    storage_1 = Storage()
    storage_1.data = reference
    storage_1.meta = meta_multi_channel

    storage_2 = Storage()
    storage_2.data = reference
    storage_2.meta = meta_multi_channel
    parent_storage.storages = [storage_1, storage_2]

    dirname = os.path.dirname(__file__)
    tmp_folder = os.path.join(dirname, "data", "dummy_tmp.iq.tar")
    saver.save(tmp_folder, parent_storage)
    with open(reference_iqtar_file_name_multi_channel, "rb") as file:
        bins = file.read()
    os.remove(tmp_folder)
    with open(reference_iqtar_file_name_multi_channel, "rb") as file:
        ref = file.read()
    assert bins == ref


def test_load(reference_iqtar_file_name: str, reference, meta):
    iqtar = IqTar(file=reference_iqtar_file_name)
    assert iqtar.parent_storage.number_of_storages() == 1
    assert iqtar.filename == reference_iqtar_file_name
    assert iqtar.data[0] == pytest.approx(reference, rel=0.0001)
    assert iqtar.meta[0] == meta


def test_load_chunks(reference_iqtar_file_name_huge: str, reference_huge, meta):
    iqtar = IqTar(file=reference_iqtar_file_name_huge, nr_samples=10, samples_offset=5)
    assert iqtar.parent_storage.number_of_storages() == 1
    assert iqtar.filename == reference_iqtar_file_name_huge
    assert iqtar.data[0] == pytest.approx(reference_huge, rel=0.0001)
    meta["date"] = datetime.datetime(2023, 4, 11, 10, 32, 30, 586434)
    meta["name"] = "Python iq.tar Writer"
    meta["samples"] = 100015
    assert iqtar.meta[0] == meta


def test_load_only_meta(reference_iqtar_file_name: str, meta: dict):
    iqtar = IqTar(file=reference_iqtar_file_name, only_meta_data=True)
    meta["datafilename"] = "dummy.complex.1ch.float32"
    assert iqtar.meta[0] == meta


def test_save(reference_iqtar_file_name: str, reference: np.ndarray, meta: dict):
    np.random.seed(900)
    iqtar = IqTar()
    iqtar.data[0] = reference
    iqtar.meta[0] = meta
    dirname = os.path.dirname(__file__)
    tmp_folder = os.path.join(dirname, "data", "dummy_tmp.iq.tar")
    iqtar.save(tmp_folder)
    with open(reference_iqtar_file_name, "rb") as file:
        bins = file.read()
    os.remove(tmp_folder)
    with open(reference_iqtar_file_name, "rb") as file:
        ref = file.read()
    assert bins == ref
