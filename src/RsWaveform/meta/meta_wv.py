"""WV meta data for Storage container."""

import typing

import numpy as np

from .defaults import META_WV_DEFAULTS
from .meta_base import MetaBase


class MetaWv(MetaBase):
    """WV meta data for Storage container."""

    def __init__(self, no_defaults: bool = False, **kwargs):
        """Initialize WV Meta class."""
        if no_defaults:
            values = {}
        else:
            values = META_WV_DEFAULTS.copy()
        values.update(kwargs)
        MetaBase.__init__(self, values)

    @property
    def type(self) -> typing.Optional[str]:
        """Waveform type for WV format."""
        return self._items.get("type")

    @type.setter
    def type(self, value: str) -> None:
        self._items["type"] = value

    @property
    def copyright(self) -> typing.Optional[str]:
        """Coypright for WV format."""
        return self._items.get("copyright")

    @copyright.setter
    def copyright(self, value: str) -> None:
        self._items["copyright"] = value

    @property
    def marker(self) -> typing.Dict[str, typing.List[typing.List[int]]]:
        """Markers for WV format."""
        if "marker" not in self._items:
            self._items["marker"] = {}
        return self._items["marker"]

    @marker.setter
    def marker(self, value: typing.Dict[str, typing.List[typing.List[int]]]) -> None:
        self._items["marker"] = value

    @property
    def control_list(
        self,
    ) -> typing.Union[None, np.ndarray, typing.List[typing.List[int]]]:
        """Binary marker element stream for WV format.

        The list/np.ndarray format should be 'Marker 1-4 x Samples'

        Example:
        control_list = [[0, 1], [1, 0], [1, 0], [0, 1]]

        whereat Marker 1 looks like [0, 1], Marker 2 [1, 0], Marker 3 [1, 0],
        Marker 4 [0, 1].
        """
        return self._items.get("control_list")

    @control_list.setter
    def control_list(
        self, value: typing.Union[np.ndarray, typing.List[typing.List[int]]]
    ) -> None:
        self._items["control_list"] = value

    @property
    def control_length(self) -> typing.Optional[int]:
        """Control length for WV format."""
        return self._items.get("control_length")

    @control_length.setter
    def control_length(self, value: typing.Optional[int]) -> None:
        self._items["control_length"] = value

    @property
    def rms(self) -> typing.Optional[float]:
        """The RMS value of the signal."""
        return self._items.get("rms")

    @rms.setter
    def rms(self, value: float) -> None:
        self._items["rms"] = value

    @property
    def peak(self) -> typing.Optional[float]:
        """The signal peak value of the signal."""
        return self._items.get("peak")

    @peak.setter
    def peak(self, value: float) -> None:
        self._items["peak"] = value

    @property
    def samples(self) -> typing.Optional[int]:
        """The sample count of the waveform."""
        return self._items.get("samples")

    @samples.setter
    def samples(self, value: int) -> None:
        self._items["samples"] = value

    @property
    def reflevel(self) -> typing.Optional[float]:
        """The reference value of the signal."""
        return self._items.get("reflevel")

    @reflevel.setter
    def reflevel(self, value: float) -> None:
        self._items["reflevel"] = value
