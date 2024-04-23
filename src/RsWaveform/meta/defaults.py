"""Defaults for WV meta data."""

META_WV_DEFAULTS = {
    "type": ("SMU-WV", 0),
    "copyright": "Rohde & Schwarz",
    "comment": "Created with RsWaveform",
    "clock": 1e9,
    "marker": {},
    "control_length": None,
    "control_list": None,
    "rms": None,
    "peak": None,
    "samples": None,
    "reflevel": None,
}

META_IQTAR_DEFAULTS = {
    "center_frequency": 1e9,
    "comment": "Created with RsWaveform",
    "clock": 1e9,
    "scalingfactor": 1,
}
