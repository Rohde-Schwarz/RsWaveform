"""Common DSP methods."""

import typing

import numpy as np

from .fake_jit import jit


@jit(forceobj=True)
def normalize(data: np.ndarray, reference: typing.Optional[float] = None):
    """Normalize data against a reference value."""
    if not reference:
        reference = float(np.float16(1 - np.float_power(2, -15)))
        # by default all waveforms are 16-bit quantized
    if np.max(np.abs(data)) != 0:
        return np.multiply(data, reference / np.max(np.abs(data)))
    else:
        return data


@jit(forceobj=True)
def convert_to_db(value: np.ndarray) -> np.ndarray:
    """Convert value from amplitude to dB."""
    return 20 * np.log10(np.float16(value))


@jit(forceobj=True)
def calculate_peak(data: np.ndarray) -> np.ndarray:
    """Calculate peak value in dB."""
    maximum_value = np.max(np.abs(data))
    return convert_to_db(np.float16(maximum_value))


@jit(forceobj=True)
def calculate_rms(data: np.ndarray) -> np.ndarray:
    """Calculate root-mean-square (RMS) value in dB."""
    magnitude = data * np.conj(data)
    rms = np.sqrt(np.mean(magnitude))
    return convert_to_db(np.abs(rms))


def calculate_par(data) -> float:
    """Calculate peak-to-average-ratio (PAR) value in dB."""
    return calculate_peak(data) - calculate_rms(data)
