"""Save R&S waveform files."""

from __future__ import annotations

import abc
import typing

from .parent_storage import ParentStorage

if typing.TYPE_CHECKING:
    from pathlib import Path


class SaveInterface(abc.ABC):
    """Load R&S waveform implementation."""

    @abc.abstractmethod
    def save(
        self,
        file: typing.Union[str, typing.IO, Path],
        datas: ParentStorage,
        scale: float = 1.0,
    ) -> None:
        """Abstract save implementation."""
        pass
