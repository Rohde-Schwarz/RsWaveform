import io
import pathlib
import re
from datetime import datetime

import numpy as np
import pytest

from RsWaveform import RsWaveform, normalize
from RsWaveform.meta import Meta
from RsWaveform.parent_storage import ParentStorage
from RsWaveform.storage import Storage
from RsWaveform.wv.load import Load
from RsWaveform.wv.save import Save


@pytest.fixture
def reference() -> np.ndarray:
    return np.array([0.2, 0.6]) + 1j * np.array([0.4, 0.8])


@pytest.fixture
def reference_mwv() -> np.ndarray:
    return np.zeros(1000) + 1j * np.zeros(1000)


@pytest.fixture
def reference_huge() -> np.ndarray:
    return np.concatenate((np.array([0.2 + 0.6j] * 5), np.array([0.5 + 0.5j] * 5)))


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
            "marker": {"marker_list_1": [[0, 1], [32, 0], [63, 0]]},
            "control_list": np.array([[0, 1], [1, 0], [1, 0], [0, 1]]),
            "encryption_flag": False,
            "rms": 2.220459,
            "peak": 0.0,
            "samples": 2,
            "reflevel": -20.0,
        }
    )


@pytest.fixture
def meta_mwv() -> Meta:
    return Meta(
        **{  # type: ignore[arg-type]
            "type": "SMU-MWV",
            "copyright": "Rohde&Schwarz",
            "comment": "Test waveform file",
            "date": datetime(2023, 1, 4, 15, 48, 50),
            "clock": 2e8,
            "encryption_flag": False,
            "rms": 200.0,
            "peak": 200.0,
            "samples": 2000,
            "reflevel": -10.0,
        }
    )


# Test Load/Save interfaces #


def test_get_regex_token():
    tokens = Load._get_regex_tokens()
    assert isinstance(tokens, list)
    for x in tokens:
        assert isinstance(x, tuple)


def test_is_waveform_encrypted():
    assert Load._is_waveform_encrypted(b"WWAVEFORM")
    assert not Load._is_waveform_encrypted(b"WAVEFORM")
    with pytest.raises(ValueError):
        Load._is_waveform_encrypted(b"BWAVEFORM")
    with pytest.raises(ValueError):
        assert Load._is_waveform_encrypted(b"UWAVEFORM")


def test_loader(reference_waveform_file_name, meta, reference):
    loader = Load()
    parent_storage = loader.load(reference_waveform_file_name)
    assert len(parent_storage.storages) == 1
    data = parent_storage.storages[0].data
    assert data == pytest.approx(reference, rel=0.001)
    real_valued = np.real(data).astype(np.float16)
    assert real_valued == pytest.approx(
        np.real(reference).astype(np.float16), rel=0.00000001
    )
    imag_valued = np.imag(data).astype(np.float16)
    assert imag_valued == pytest.approx(
        np.imag(reference).astype(np.float16), rel=0.00000001
    )
    obtained_meta = parent_storage.storages[0].meta.copy()
    obtained_control_list = obtained_meta.pop("control_list", np.array([]))
    ref_meta = meta.copy()
    ref_control_list = ref_meta.pop("control_list", np.array([]))
    assert np.array_equal(obtained_control_list, ref_control_list)
    assert obtained_meta == ref_meta


def test_loader_chunks(
    reference_waveform_file_name_huge: str, reference_huge: np.ndarray
):
    loader = Load()
    parent_storage = loader.load_in_chunks(reference_waveform_file_name_huge, 10, 5)
    assert len(parent_storage.storages) == 1
    assert np.real(parent_storage.storages[0].data).astype(np.float16) == pytest.approx(
        np.real(reference_huge).astype(np.float16), rel=0.00000001
    )
    assert np.imag(parent_storage.storages[0].data).astype(np.float16) == pytest.approx(
        np.imag(reference_huge).astype(np.float16), rel=0.00000001
    )


def test_loader_meta_only(reference_waveform_file_name: str, meta):
    loader = Load()
    parent_storage = loader.load_meta(reference_waveform_file_name)
    meta.pop("encryption_flag")
    obtained_meta = parent_storage.storages[0].meta.copy()
    obtained_control_list = obtained_meta.pop("control_list", np.array([]))
    ref_meta = meta.copy()
    ref_control_list = ref_meta.pop("control_list", np.array([]))
    assert np.array_equal(obtained_control_list, ref_control_list)
    assert obtained_meta == ref_meta


def test_loader_mwv(
    reference_waveform_mwv_file_name: str, meta_mwv: dict, reference_mwv: np.ndarray
):
    loader = Load()
    parent_storage = loader.load(reference_waveform_mwv_file_name)
    assert len(parent_storage.storages) == 2
    assert parent_storage.storages[0].data == pytest.approx(reference_mwv, rel=0.001)
    assert np.real(parent_storage.storages[0].data).astype(np.float16) == pytest.approx(
        np.real(reference_mwv).astype(np.float16), rel=0.00000001
    )
    assert np.imag(parent_storage.storages[0].data).astype(np.float16) == pytest.approx(
        np.imag(reference_mwv).astype(np.float16), rel=0.00000001
    )
    assert parent_storage.storages[0].meta == meta_mwv
    assert parent_storage.storages[1].meta == meta_mwv


# Test Save class #
@pytest.mark.parametrize("calculate", [True, False])
def test_saver(
    calculate, reference_waveform_file_name: str, reference: np.ndarray, meta: Meta
):
    np.random.seed(900)
    saver = Save()
    parent_storage = ParentStorage()
    parent_storage.storages[0].data = normalize(reference)
    parent_storage.storages[0].meta = meta
    if calculate:
        parent_storage.storages[0].meta._items["rms"] = None
        parent_storage.storages[0].meta._items["peak"] = None
    with io.BytesIO() as file:
        saver.save(file, parent_storage)
        bins = file.getvalue()
    bins = re.sub(rb"\{DATE:[\d\-;\:]+\}", b"{DATE:2023-01-05;10:03:52}", bins)
    with open(reference_waveform_file_name, "rb") as file:
        ref = file.read()
    ref = re.sub(rb": #", b":#", ref)
    assert bins == ref


def test_saver_mwv(
    reference_waveform_mwv_file_name: str, reference_mwv: np.ndarray, meta_mwv: Meta
):
    np.random.seed(900)

    saver = Save()
    parent_storage = ParentStorage()

    data1 = Storage()
    data1.data = normalize(reference_mwv)
    data1.meta = meta_mwv

    data2 = Storage()
    data2.data = normalize(reference_mwv)
    data2.meta = meta_mwv

    parent_storage.storages = [data1, data2]
    with io.BytesIO() as file:
        saver.save(file, parent_storage)
        bins = file.getvalue()
    bins = re.sub(rb"\{DATE:[\d\-;\:]+\}", b"{DATE:2023-01-04;15:48:50}", bins)
    with open(reference_waveform_mwv_file_name, "rb") as file:
        ref = file.read()
    assert bins == ref


# Test RsWaveform


def test_load(reference_waveform_file_name, meta, reference):
    wv = RsWaveform(file=reference_waveform_file_name)
    assert wv.parent_storage.number_of_storages() == 1
    assert wv.filename == reference_waveform_file_name
    assert wv.data[0] == pytest.approx(reference, rel=0.001)
    assert np.real(wv.data[0]).astype(np.float16) == pytest.approx(
        np.real(reference).astype(np.float16), rel=0.00000001
    )
    assert np.imag(wv.data[0]).astype(np.float16) == pytest.approx(
        np.imag(reference).astype(np.float16), rel=0.00000001
    )
    obtained_meta = wv.meta[0].copy()
    obtained_control_list = obtained_meta.pop("control_list", np.array([]))
    ref_meta = meta.copy()
    ref_control_list = ref_meta.pop("control_list", np.array([]))
    assert np.array_equal(obtained_control_list, ref_control_list)
    assert obtained_meta == ref_meta


def test_load_with_sample_sanity_checking(
    reference_waveform_file_name, tmp_path, caplog
):
    ref_path = pathlib.Path(reference_waveform_file_name)
    mod_file = tmp_path / ref_path.name
    with open(reference_waveform_file_name, "rb") as frp, open(mod_file, "wb") as fwp:
        read_content = frp.read()
        new_content = read_content[:-1] + b"ffff" + read_content[-1:]
        fwp.write(new_content)
    with pytest.raises(
        ValueError,
        match=(
            r"Could not extract [\w]+ data. Malformed [\w]+ section because "
            r"there is no '}' after [\d]+ binary samples."
        ),
    ):
        RsWaveform(file=mod_file)


def test_load_chunks(
    reference_waveform_file_name_huge: str, reference_huge: np.ndarray
):
    wv = RsWaveform(
        file=reference_waveform_file_name_huge, nr_samples=10, samples_offset=5
    )
    assert wv.parent_storage.number_of_storages() == 1
    assert wv.filename == reference_waveform_file_name_huge
    assert np.real(wv.data[0]).astype(np.float16) == pytest.approx(
        np.real(reference_huge).astype(np.float16), rel=0.00000001
    )
    assert np.imag(wv.data[0]).astype(np.float16) == pytest.approx(
        np.imag(reference_huge).astype(np.float16), rel=0.00000001
    )


def test_load_meta_only(reference_waveform_file_name: str, meta: dict):
    wv = RsWaveform(file=reference_waveform_file_name, only_meta_data=True)
    meta.pop("encryption_flag")
    obtained_meta = wv.meta[0].copy()
    obtained_control_list = obtained_meta.pop("control_list", np.array([]))
    ref_meta = meta.copy()
    ref_control_list = ref_meta.pop("control_list", np.array([]))
    assert np.array_equal(obtained_control_list, ref_control_list)
    assert obtained_meta == ref_meta


def test_save(reference_waveform_file_name: str, reference: np.ndarray, meta: dict):
    np.random.seed(900)
    wv = RsWaveform()
    wv.data[0] = normalize(reference)
    wv.meta[0] = meta
    with io.BytesIO() as file:
        wv.save(file)
        bins = file.getvalue()
    bins = re.sub(rb"\{DATE:[\d\-;\:]+\}", b"{DATE:2023-01-05;10:03:52}", bins)
    with open(reference_waveform_file_name, "rb") as file:
        ref = file.read()
    ref = re.sub(rb": #", b":#", ref)
    assert bins == ref
