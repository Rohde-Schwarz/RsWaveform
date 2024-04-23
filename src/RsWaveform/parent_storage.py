"""Storage wrapper class for list of Storages."""

import abc
import typing
from datetime import datetime

from .storage import Storage


class ParentStorage(abc.ABC):
    """ParentStorage class implementation.

    Args:
        number_of_storages (int, optional): Initialize number of storages.
            Defaults to 1.
        no_defaults (bool, optional): Storage meta data should have no defaults at
            initialization. Defaults to False.

    Raises:
        ValueError: If number of storages is smaller than 1.
    """

    def __init__(self, number_of_storages: int = 1, no_defaults: bool = False):
        """Initialize ParentStorage class."""
        if number_of_storages <= 0:
            raise ValueError("Only positive number of storages allowed!")
        self._storages = [
            Storage(no_defaults=no_defaults) for _ in range(number_of_storages)
        ]
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
