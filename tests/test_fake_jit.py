import pytest

from RsWaveform.utility.fake_jit import jit


def test_jit_with_func():
    try:
        import numba  # noqa F401
    except ImportError:
        pass
    else:
        pytest.skip("Numba is install but test should check decorator in no-numba mode")

    def dummy(*args):
        pass

    fn = jit(dummy)
    assert dummy is fn


def test_jit_with_signature():
    fn = jit("Int32,Int32")
    assert callable(fn)
