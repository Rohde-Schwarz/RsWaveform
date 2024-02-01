"""Meta base class implementation."""

import typing

META_DATA_DICT = ["_items", "meta_attribute"]


class MetaBase:
    """Common meta data for Storage container."""

    def __init__(self, defaults: typing.Optional[dict] = None) -> None:
        """Initialize Base Meta class."""
        if defaults is None:
            defaults = {}
        if not hasattr(self, "_items"):
            self._items = {}
        for key, value in defaults.items():
            self._items[key] = value

    def __getitem__(self, key):
        """Set item to internal dict."""
        return self._items[key]

    def __setitem__(self, key, value):
        """Get item from internal dict."""
        self._items[key] = value

    def __delitem__(self, key):
        """Delete item from internal dict."""
        del self._items[key]

    def __contains__(self, key):
        """Check if a key is in the dictionary."""
        return key in self._items

    def __iter__(self):
        """Iterate over the keys in the dictionary."""
        return iter(self._items)

    def __len__(self):
        """Get the number of key-value pairs."""
        return len(self._items)

    def __repr__(self):
        """Write the representation of Meta."""
        return self._items.__repr__()

    def __eq__(self, other):
        """Compare two MetaBase objects for equality."""
        if isinstance(other, MetaBase):
            return self._items == other._items
        if isinstance(other, dict):
            return self._items == other
        return False

    def __ne__(self, other):
        """Check if two MetaBase objects are not equal."""
        return not self == other

    def pop(self, key, default=None):
        """Remove a key and return its value. If key is not found, return default."""
        return self._items.pop(key, default)

    def popitem(self):
        """Remove and return a (key, value) pair as a 2-tuple.

        Pairs are returned in LIFO order.
        """
        return self._items.popitem()

    def clear(self):
        """Remove all items from the dictionary."""
        self._items.clear()

    def setdefault(self, key, default=None):
        """If key is in the dictionary, return its value.

        If not, insert key with a value of default and return default.
        """
        return self._items.setdefault(key, default)

    def copy(self):
        """Return a shallow copy of the dictionary."""
        instance_type = type(self)
        kwargs = self._items.copy()
        kwargs["no_defaults"] = True
        return instance_type(**kwargs)

    def keys(self):
        """Get the keys in the dictionary."""
        return self._items.keys()

    def values(self):
        """Get the values in the dictionary."""
        return self._items.values()

    def items(self):
        """Get the key-value pairs in the dictionary."""
        return self._items.items()

    def get(self, key, default=None):
        """Get the value for a key, or a default value if the key is not in the dict."""
        return self._items.get(key, default)

    def update(self, *args, **kwargs):
        """Update the dictionary with the key-value pairs from another dictionary."""
        return self._items.update(*args, **kwargs)

    # Shared properties ###

    @property
    def comment(self) -> typing.Optional[str]:
        """Mandatory parameter for all types of waveforms."""
        return self._items.get("comment")

    @comment.setter
    def comment(self, value: str) -> None:
        """Setter for comment."""
        self._items["comment"] = value

    @property
    def clock(self) -> typing.Optional[float]:
        """Mandatory parameter for all types of waveforms."""
        return self._items.get("clock")

    @clock.setter
    def clock(self, value: float) -> None:
        """Setter for clock."""
        self._items["clock"] = value
