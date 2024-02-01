import pytest

from RsWaveform.utility.integer_indexedproperty import IntegerIndexedProperty


class DummyClass:
    def __init__(self, populate: int = 1):
        self._list = list(range(populate))

    @IntegerIndexedProperty
    def content(self, index: int = 0) -> int:
        return self._list[index]

    @content.setter
    def content_setter(self, index: int, value: int) -> None:
        self._list[index] = value


def test_moduserindex_valid_integer():
    prop = DummyClass()
    prop.content[0] = 42
    assert prop.content[0] == 42


def test_out_of_range_index():
    prop = DummyClass()

    with pytest.raises(IndexError):
        prop.content[1]


def test_invalid_non_integer():
    prop = DummyClass()

    with pytest.raises(ValueError, match="Just integer as keys allowed."):
        prop.content[1.5]

    with pytest.raises(ValueError, match="Just integer as keys allowed."):
        prop.content[1.5] = 5
