"""IQTAR meta data for Storage container."""

import typing

from .defaults import META_IQTAR_DEFAULTS
from .meta_base import MetaBase


class MetaIqtar(MetaBase):
    """IQTAR meta data for Storage container."""

    def __init__(self, no_defaults: bool = False, **kwargs):
        """Initialize IQTAR Meta class."""
        if no_defaults:
            values = {}
        else:
            values = META_IQTAR_DEFAULTS.copy()
        values.update(kwargs)
        MetaBase.__init__(self, values)

    @property
    def center_frequency(self) -> typing.Optional[str]:
        """Center frequency for IQTAR format."""
        return self._items.get("center_frequency")

    @center_frequency.setter
    def center_frequency(self, value: str) -> None:
        self._items["center_frequency"] = value

    @property
    def scalingfactor(self) -> typing.Optional[float]:
        """Scaling factor for IQTAR format."""
        return self._items.get("scalingfactor")

    @scalingfactor.setter
    def scalingfactor(self, value: float) -> None:
        self._items["scalingfactor"] = value
