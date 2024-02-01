import inspect

import pytest

from RsWaveform.meta import Meta
from RsWaveform.meta.defaults import META_IQTAR_DEFAULTS, META_WV_DEFAULTS
from RsWaveform.meta.meta_iqtar import MetaIqtar
from RsWaveform.meta.meta_wv import MetaWv


def test_dictionary_behavior_of_meta_class():
    meta = Meta()
    meta.clear()
    assert len(meta) == 0
    with pytest.raises(KeyError):
        meta["not valid"]
    assert meta.get("not valid") is None
    meta["new key"] = True
    assert meta["new key"]
    assert meta.pop("new key")
    meta.update(test=True)
    assert meta["test"]
    assert meta.items() == meta._items.items()
    assert meta.keys() == meta._items.keys()
    assert list(meta.values()) == list(meta._items.values())
    assert meta == meta.copy()
    assert meta == meta._items
    assert not meta == 1
    assert meta != Meta()
    p = meta.popitem()
    assert p == ("test", True)
    meta.update(test=True)
    del meta["test"]
    assert "test" not in meta
    assert meta.setdefault("test") is None
    assert meta["test"] is None


@pytest.mark.parametrize(
    "meta_wrapper,defaults",
    [(MetaWv, META_WV_DEFAULTS), (MetaIqtar, META_IQTAR_DEFAULTS)],
)
def test_fill_with_defaults(meta_wrapper, defaults):
    meta = meta_wrapper()
    properties = inspect.getmembers(type(meta), lambda o: isinstance(o, property))
    for prop, _ in properties:
        reference = defaults[prop]
        assert getattr(meta, prop) == reference
        assert meta[prop] == reference


@pytest.mark.parametrize(
    "meta_wrapper,defaults,kwargs",
    [
        (
            MetaWv,
            META_WV_DEFAULTS,
            {
                "clock": 2e9,
                "comment": "Test WV",
                "copyright": "my copyright",
                "marker": {"marker list 1": [1, 2]},
            },
        ),
        (
            MetaIqtar,
            META_IQTAR_DEFAULTS,
            {
                "clock": 500e6,
                "comment": "Test IQTAR",
                "center_frequency": 2e9,
                "scalingfactor": 2,
            },
        ),
    ],
)
def test_fill_partly_from_kwargs(meta_wrapper, defaults, kwargs):
    new_defaults = defaults.copy()
    new_defaults.update(kwargs)
    meta = meta_wrapper(**kwargs)
    properties = inspect.getmembers(type(meta), lambda o: isinstance(o, property))
    for prop, _ in properties:
        reference = new_defaults[prop]
        assert getattr(meta, prop) == reference
        assert meta[prop] == reference


def test_meta():
    defaults = META_WV_DEFAULTS.copy()
    defaults.update(META_IQTAR_DEFAULTS)
    kwargs = {
        "clock": 2e9,
        "comment": "Test this",
        "copyright": "my copyright",
        "marker": {"marker list 1": [1, 2]},
        "center_frequency": 2e9,
        "scalingfactor": 2,
    }
    defaults.update(kwargs)
    meta = Meta(**kwargs)  # type: ignore[arg-type]
    properties = inspect.getmembers(type(meta), lambda o: isinstance(o, property))
    for prop, _ in properties:
        reference = defaults[prop]
        assert getattr(meta, prop) == reference
        assert meta[prop] == reference


def test_single_properties():
    meta = Meta(no_defaults=True)
    assert meta.marker == {}
    assert "marker" in meta._items
    assert meta.control_list is None
