"""Load R&S waveform files."""

from __future__ import annotations

import abc
import typing

from .parent_storage import ParentStorage

if typing.TYPE_CHECKING:
    from pathlib import Path


class LoadInterface(abc.ABC):
    """Load R&S waveform implementation."""

    @abc.abstractmethod
    def load(self, file: typing.Union[str, typing.IO, Path]) -> ParentStorage:
        """Abstract load implementation."""

    @abc.abstractmethod
    def load_in_chunks(
        self, file: typing.Union[str, typing.IO, Path], samples: int, offset: int
    ) -> ParentStorage:
        """Abstract load implementation for chunks."""

    @abc.abstractmethod
    def load_meta(self, file: typing.Union[str, typing.IO, Path]) -> ParentStorage:
        """Abstract load implementation for meta information only."""
