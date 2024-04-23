"""Load implementation for iqw."""

from __future__ import annotations

import typing

import numpy as np

from ..load_interface import LoadInterface
from ..parent_storage import ParentStorage
from ..utility.fake_jit import jit
from ..utility.file_handling import read_file_handle

if typing.TYPE_CHECKING:
    from pathlib import Path


class Load(LoadInterface):
    """Load class for iqw."""

    def load(self, file: typing.Union[str, typing.IO, Path]) -> ParentStorage:
        """Load iwq data from file."""
        parent_storage = ParentStorage(no_defaults=True)
        with read_file_handle(file) as fp:
            content = fp.read()
        iq_data = self._extract_iq(content)
        parent_storage.storages[0].data = iq_data
        if isinstance(file, str):
            parent_storage.filename = file
        return parent_storage

    def load_in_chunks(
        self, file: typing.Union[str, typing.IO, Path], samples: int, offset: int
    ) -> ParentStorage:
        """Load chunk iwq data from file."""
        parent_storage = ParentStorage()
        with read_file_handle(file) as fp:
            fp.read(offset * 4 * 2)
            content = fp.read(samples * 4 * 2)
        iq_data = self._extract_iq(content)
        parent_storage.storages[0].data = iq_data
        if isinstance(file, str):
            parent_storage.filename = file
        return parent_storage

    def load_meta(self, file: typing.Union[str, typing.IO, Path]) -> ParentStorage:
        """Load meta information only from iqw file."""
        raise Exception("Iqw does not contain meta data!")

    @staticmethod
    def _extract_data(content: bytes):
        dt = np.dtype(np.float32)
        i_values = np.frombuffer(
            buffer=Load._extract_pairs(content, 0),
            dtype=dt,
        )
        q_values = np.frombuffer(
            buffer=Load._extract_pairs(content, 1),
            dtype=dt,
        )
        data = i_values + 1j * q_values
        return data

    def _extract_iq(self, content: bytes) -> np.ndarray:
        data = self._extract_data(content)
        return data

    @staticmethod
    @jit(forceobj=True)
    def _extract_pairs(buf: bytes, start: int = 0) -> bytes:
        """Extract data pairs from binary buffer."""
        single_pair = bytearray()
        length = len(buf)
        for idx in np.arange(start * 4, length, 8):
            single_pair.extend(buf[idx : idx + 4])
        return single_pair
