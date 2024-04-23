"""Load, manipulate and save R&S waveform files."""

from __future__ import annotations

import io
import typing
from importlib.metadata import PackageNotFoundError, version

import numpy as np

from . import iqtar, iqw, wv
from .load_interface import LoadInterface
from .meta import Meta
from .parent_storage import ParentStorage
from .save_interface import SaveInterface
from .utility.dsp import (
    calculate_par,
    calculate_peak,
    calculate_rms,
    convert_to_db,
    normalize,
)
from .utility.integer_indexedproperty import IntegerIndexedProperty

if typing.TYPE_CHECKING:
    from pathlib import Path

__version__ = "unknown"
try:
    __version__ = version(__package__)
except PackageNotFoundError:
    # package is not installed
    pass


class RsWaveform(object):
    """RsWaveform class for loading and saving IQ data."""

    def __init__(
        self,
        load: typing.Type[LoadInterface] = wv.Load,
        save: typing.Type[SaveInterface] = wv.Save,
        file: typing.Union[None, str, typing.IO, Path] = None,
        nr_samples: typing.Union[None, int] = None,
        samples_offset: typing.Union[None, int] = None,
        only_meta_data: bool = False,
    ) -> None:
        """Initialize an R&S Waveform class."""
        if not issubclass(load, LoadInterface):
            raise ValueError(f"Loader is not of type {type(LoadInterface)}")
        if not issubclass(save, SaveInterface):
            raise ValueError(f"Saver is not of type {type(SaveInterface)}")
        self.loader = load()
        self.saver = save()
        self._parent_storage = ParentStorage()
        if file:
            if not only_meta_data:
                if nr_samples is None and samples_offset is None:
                    self.load(file)
                elif nr_samples is not None and samples_offset is not None:
                    self.load_in_chunks(file, nr_samples, samples_offset)
                else:
                    raise ValueError(
                        "You need to define both nr_samples and "
                        "samples_offset to load chunks!"
                    )
            else:
                self.load_meta(file)

    def load(self, file: typing.Union[str, typing.IO, Path]) -> None:
        """Load a waveform file with a set loader class."""
        self._parent_storage = self.loader.load(file)

    def load_in_chunks(
        self,
        file: typing.Union[str, typing.IO, Path],
        nr_samples: int,
        samples_offset: int,
    ) -> None:
        """Load a chunk of a waveform file with a set loader class."""
        self._parent_storage = self.loader.load_in_chunks(
            file, nr_samples, samples_offset
        )

    def load_meta(self, file: typing.Union[str, typing.IO, Path]) -> None:
        """Load meta of a waveform file with a set loader class."""
        self._parent_storage = self.loader.load_meta(file)

    def save(
        self,
        file: typing.Union[str, typing.IO, Path],
        scale: float = np.power(2, np.iinfo(np.int16).bits - 1),
    ) -> None:
        """Saver a waveform file with a set saver class."""
        self.saver.save(file, self._parent_storage, scale)

    def tobytes(self) -> bytes:
        """Get waveform file content as bytes."""
        with io.BytesIO() as bio:
            self.save(bio)
            data = bio.getvalue()
        return data

    def frombytes(self, binary_data: typing.Union[bytes, io.BytesIO]) -> None:
        """Load waveform from bytes file content."""
        if isinstance(binary_data, bytes):
            with io.BytesIO(binary_data) as bio:
                self.load(bio)
        else:
            self.load(binary_data)

    @property
    def filename(self) -> str:
        """Get the waveform filename."""
        return self._parent_storage.filename

    @filename.setter
    def filename(self, file_name: str) -> None:
        """Set the waveform filename."""
        self._parent_storage.filename = file_name

    @IntegerIndexedProperty
    def meta(self, index: int = 0) -> Meta:
        """Get the waveform storage metadata."""
        return self._parent_storage.storages[index].meta

    @meta.setter
    def meta_setter(self, index: int, meta: Meta) -> None:
        """Set the waveform storage metadata."""
        self._parent_storage.storages[index].meta = meta

    @IntegerIndexedProperty
    def data(self, index: int = 0) -> np.ndarray:
        """Get the waveform IQ data."""
        return self._parent_storage.storages[index].data

    @data.setter
    def data_setter(self, index: int, data: np.ndarray) -> None:
        """Set the waveform storage IQ data."""
        self._parent_storage.storages[index].data = data

    @property
    def parent_storage(self) -> ParentStorage:
        """Get parent storage."""
        return self._parent_storage


class Iqw(RsWaveform, object):
    """Iqw class for loading and saving IQ data."""

    def __init__(
        self,
        load: typing.Type[LoadInterface] = iqw.Load,
        save: typing.Type[SaveInterface] = iqw.Save,
        file: typing.Union[None, str, typing.IO, Path] = None,
        nr_samples: typing.Union[None, int] = None,
        samples_offset: typing.Union[None, int] = None,
    ) -> None:
        """Initialize a Iqw class."""
        super().__init__(load, save, file, nr_samples, samples_offset, False)

    def save(
        self, file: typing.Union[str, typing.IO, Path], scale: float = 1.0
    ) -> None:
        """Saver an iqw file with a set saver class."""
        self.saver.save(file, self._parent_storage, scale)


class IqTar(RsWaveform, object):
    """Iqtar class for loading and saving IQ data."""

    def __init__(
        self,
        load: typing.Type[LoadInterface] = iqtar.Load,
        save: typing.Type[SaveInterface] = iqtar.Save,
        file: typing.Union[None, str, Path] = None,
        nr_samples: typing.Union[None, int] = None,
        samples_offset: typing.Union[None, int] = None,
        only_meta_data: bool = False,
    ) -> None:
        """Initialize a IQtar class."""
        super().__init__(load, save, file, nr_samples, samples_offset, only_meta_data)

    def save(
        self, file: typing.Union[str, typing.IO, Path], scale: float = 1.0
    ) -> None:
        """Saver an iqw file with a set saver class."""
        self.saver.save(file, self._parent_storage, scale)


__all__ = [
    "RsWaveform",
    "Iqw",
    "IqTar",
    "load_interface",
    "save_interface",
    "calculate_par",
    "calculate_peak",
    "calculate_rms",
    "normalize",
    "convert_to_db",
]
