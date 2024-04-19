"""Save implementation for iqw."""

from __future__ import annotations

import math
import typing

import numpy as np

from ..parent_storage import ParentStorage
from ..save_interface import SaveInterface
from ..storage import Storage
from ..utility.fake_jit import jit
from ..utility.file_handling import write_file_handle

if typing.TYPE_CHECKING:
    from pathlib import Path


class Save(SaveInterface):
    """Save class for iqw."""

    def save(
        self,
        file: typing.Union[str, typing.IO, Path],
        datas: ParentStorage,
        scale: float = 1.0,
    ) -> None:
        """Save iq samples to iqw file."""
        self._write(file, datas, scale)

    @staticmethod
    @jit(forceobj=True)
    def _scale_data(iq_samples: np.ndarray, scale: float = 1.0) -> np.ndarray:
        iq_samples = (1 / scale) * iq_samples
        return iq_samples

    @staticmethod
    def _prepare_data(iq_samples: np.ndarray) -> np.ndarray:
        def get_real_or_complex_by_index(iq: complex, index: int):
            return iq.real if index == 0 else iq.imag

        sorted_iq_samples = [
            get_real_or_complex_by_index(iq, i) for iq in iq_samples for i in range(2)
        ]
        return np.asarray(sorted_iq_samples)

    def _write(
        self,
        file: typing.Union[str, typing.IO, Path],
        data: ParentStorage,
        scale: float = 1.0,
    ):
        with write_file_handle(file) as fp:
            for storage in data.storages:
                self._write_data(fp, storage, scale)

    def _write_data(self, file: typing.IO, data: Storage, scale: float = 1.0):
        scaled_iq_data = self._scale_data(data.data, scale)
        iq_data = self._prepare_data(scaled_iq_data)

        chunk_size = 82000000  # randomly chosen number. Might be changed!
        number_blocks = math.ceil(iq_data.size / chunk_size)
        for block_idx in range(number_blocks):
            idx_start = block_idx * chunk_size
            idx_stop = (block_idx + 1) * chunk_size
            if idx_stop > iq_data.size - 1:
                idx_stop = iq_data.size
            bins = iq_data[idx_start:idx_stop].astype(np.float32).tobytes()
            file.write(bins)
