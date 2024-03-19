"""Storage wrapper class for waveform data."""

import abc
import typing

import numpy as np

from .meta import Meta

try:
    msgpack_import = True
    import msgpack as pickle
    import msgpack_numpy as m

    m.patch()

except ImportError:
    msgpack_import = False
    import pickle
from datetime import datetime


def decode_datetime(obj):
    """Decode datetime for msgpack."""
    if "__datetime__" in obj:
        obj = datetime.strptime(obj["as_str"], "%Y%m%dT%H:%M:%S.%f")
    return obj


def encode_datetime(obj):
    """Encode datetime for msgpack."""
    if isinstance(obj, datetime):
        obj = {"__datetime__": True, "as_str": obj.strftime("%Y%m%dT%H:%M:%S.%f")}
    return obj


class Storage(abc.ABC):
    """Storage class implementation."""

    def __init__(self, serialized: typing.Optional[bytes] = None) -> None:
        """Initialize Storage class."""
        if serialized:
            self.deserialize(serialized)
        else:
            self.data: np.ndarray = np.zeros((0,), dtype=np.complex128)
            self.meta: Meta = Meta()

    @property
    def samples(self) -> int:
        """Number of waveform samples."""
        return len(self.data)

    def serialize(self) -> bytes:
        """Serialize content from storage."""
        if msgpack_import:
            content = pickle.dumps(self.__dict__, default=encode_datetime)
        else:
            content = pickle.dumps(self.__dict__)
        return content

    def deserialize(self, bins: bytes) -> None:
        """Deserialize content from binary."""
        if msgpack_import:
            content = pickle.loads(bins, object_hook=decode_datetime)
        else:
            content = pickle.loads(bins)
        self.__dict__ = content
