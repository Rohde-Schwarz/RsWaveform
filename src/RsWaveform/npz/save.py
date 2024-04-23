"""Save implementation for generic waveform."""

from __future__ import annotations

import typing

import numpy as np

from ..parent_storage import ParentStorage
from ..save_interface import SaveInterface
from .npz_inteface import NpzInterface

if typing.TYPE_CHECKING:
    from pathlib import Path


class Save(SaveInterface, NpzInterface):
    """Save class for generic waveform."""

    def save(
        self,
        file: typing.Union[str, typing.IO, Path],
        datas: ParentStorage,
        scale: float = np.power(2, np.iinfo(np.int16).bits - 1),
    ) -> None:
        """Save waveform data to file."""
        data_objs = []
        for storage in datas.storages:
            i_values = np.real(storage.data).astype(self.dtype)
            q_values = np.imag(storage.data).astype(self.dtype)
            meta = storage.meta._items  # pylint: disable=W0212
            data_objs.append({"i": i_values, "q": q_values, "meta": meta})
        np.savez_compressed(file=file, storages=data_objs)  # type: ignore
