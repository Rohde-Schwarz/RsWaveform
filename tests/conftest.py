import os

import pytest


@pytest.fixture(params=["dummy.wv", "dummy_2.wv"])
def reference_waveform_file_name(request) -> str:
    dirname = os.path.dirname(__file__)
    return os.path.join(os.path.realpath(dirname), "data", request.param)


@pytest.fixture
def reference_waveform_file_name_huge() -> str:
    dirname = os.path.dirname(__file__)
    return os.path.join(os.path.realpath(dirname), "data", "huge_dummy.wv")


@pytest.fixture
def reference_waveform_mwv_file_name() -> str:
    dirname = os.path.dirname(__file__)
    return os.path.join(os.path.realpath(dirname), "data", "dummy_mwv.wv")


@pytest.fixture
def reference_iqw_file_name() -> str:
    dirname = os.path.dirname(__file__)
    return os.path.join(os.path.realpath(dirname), "data", "dummy.iqw")


@pytest.fixture
def reference_iqw_file_name_huge() -> str:
    dirname = os.path.dirname(__file__)
    return os.path.join(os.path.realpath(dirname), "data", "dummy_huge.iqw")


@pytest.fixture
def reference_iqtar_file_name() -> str:
    dirname = os.path.dirname(__file__)
    return os.path.join(os.path.realpath(dirname), "data", "dummy.iq.tar")


@pytest.fixture
def reference_iqtar_file_name_huge() -> str:
    dirname = os.path.dirname(__file__)
    return os.path.join(os.path.realpath(dirname), "data", "dummy_huge.iq.tar")


@pytest.fixture
def reference_iqtar_file_name_multi_channel() -> str:
    dirname = os.path.dirname(__file__)
    return os.path.join(os.path.realpath(dirname), "data", "dummy_multi_channel.iq.tar")


@pytest.fixture
def reference_npz_file_name() -> str:
    dirname = os.path.dirname(__file__)
    return os.path.join(os.path.realpath(dirname), "data", "dummy.npz")
