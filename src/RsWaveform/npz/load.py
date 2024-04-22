"""Load implementation for generic waveform."""

from __future__ import annotations

import logging
import typing

import numpy as np

from ..load_interface import LoadInterface
from ..meta import Meta
from ..parent_storage import ParentStorage
from ..storage import Storage
from .npz_inteface import NpzInterface

if typing.TYPE_CHECKING:
    from pathlib import Path


LOGGER = logging.getLogger(__name__)


class Load(LoadInterface, NpzInterface):
    """Load class for generic waveform."""

    def load(self, file: typing.Union[str, typing.IO, Path]) -> ParentStorage:
        """Load waveform data from npz file."""
        content = np.load(file=file, allow_pickle=True)
        data_objs = content.get("storages")
        if not data_objs:
            raise ValueError(f"File {file} is not compliant to data schema.")
        parent = ParentStorage(number_of_storages=len(data_objs))
        for idx, obj in enumerate(data_objs):
            i_values = obj.get("i")
            q_values = obj.get("q")
            meta = obj.get("meta", {})
            if i_values is None:
                LOGGER.warning(
                    (
                        "Skipping index %s of file %s content because no i values are"
                        " in it."
                    ),
                    idx,
                    str(file),
                )
                continue
            if q_values is None:
                q_values = np.zeros(i_values.size)
            if q_values is not None and len(i_values) != len(q_values):
                LOGGER.warning(
                    (
                        "Skipping index %s of file %s content because i value and"
                        " q value lengths are not identical."
                    ),
                    idx,
                    str(file),
                )
                continue
            storage = Storage()
            storage.data = i_values.astype(self.dtype) + 1j * q_values.astype(
                self.dtype
            )
            storage.meta = Meta(no_defaults=True, **meta)
            parent.storages[idx] = storage
        return parent

    def load_in_chunks(
        self,
        file: typing.Union[str, typing.IO, Path],
        samples: int,
        offset: int,
    ) -> ParentStorage:
        """Load chunk waveform data from file."""
        parent = self.load(file)
        for idx, storage in enumerate(parent.storages):
            if offset + samples > len(storage.data):
                raise ValueError(
                    f"Could not load chunks for index {idx} of file {file} because "
                    f"offset {offset} and sample count {samples} is greater than length"
                    f" of available data {len(storage.data)}. "
                )
            storage.data = storage.data[offset : offset + samples]
        return parent

    def load_meta(self, file: typing.Union[str, typing.IO, Path]) -> ParentStorage:
        """Load meta information only from wv file."""
        parent = self.load(file)
        for storage in parent.storages:
            storage.data = np.empty((0, 0))
        return parent
