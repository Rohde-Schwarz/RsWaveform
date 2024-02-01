"""Storage wrapper class for list of Storages."""

import abc
import typing
from datetime import datetime

from .Storage import Storage


class ParentStorage(abc.ABC):
    """ParentStorage class implementation."""

    def __init__(self, number_of_storages: int = 1):
        """Initialize ParentStorage class."""
        if number_of_storages <= 0:
            raise ValueError("Only positive number of storages allowed!")
        self._storages = [Storage() for _ in range(number_of_storages)]
        self._filename: str = ""
        self._timestamp: datetime = datetime.now()

    @property
    def timestamp(self) -> datetime:
        """Get timestamp."""
        return self._timestamp

    def number_of_storages(self) -> int:
        """Get number of storages."""
        return len(self._storages)

    def add_storage(self, storage: Storage):
        """Add storage to parentStorage."""
        self._storages.append(storage)

    @property
    def storages(self) -> typing.List[Storage]:
        """Get storages."""
        return self._storages

    @storages.setter
    def storages(self, storages: typing.List[Storage]):
        """Set all storages."""
        self._storages = storages

    @property
    def filename(self) -> str:
        """Get filename."""
        return self._filename

    @filename.setter
    def filename(self, filename: str):
        """Set filename."""
        self._filename = filename
