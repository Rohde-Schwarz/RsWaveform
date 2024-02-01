import re

from RsWaveform import __version__


def test_version():
    assert re.match(r"[\d.]+", __version__)
