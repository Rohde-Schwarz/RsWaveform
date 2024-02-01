import numpy as np

import RsWaveform.utility.dsp as dsp


def get_array() -> np.ndarray:
    values = np.arange(16)
    return values


def test_convert_to_db():
    db = dsp.convert_to_db(10)
    assert db == 20


def test_calculate_peak():
    data = get_array()
    peak = dsp.calculate_peak(data)
    assert peak == dsp.convert_to_db(np.max(data))


def test_calculate_rms():
    data = get_array()
    rms = dsp.calculate_rms(data)
    assert rms == 18.896484375


def test_calculate_par():
    data = get_array()
    peak = dsp.calculate_peak(data)
    rms = dsp.calculate_rms(data)
    par = dsp.calculate_par(data)
    assert par == peak - rms


def test_normalize():
    # Test default reference
    reference = float(np.float16(1 - np.float_power(2, -15)))
    data = get_array()
    normalized = dsp.normalize(data)
    assert np.max(np.abs(normalized)) == reference

    # Test any reference
    reference = 2
    data = get_array()
    normalized = dsp.normalize(data, reference)
    assert np.max(np.abs(normalized)) == reference
