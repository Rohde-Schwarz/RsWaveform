"""Meta data for Storage container."""

from .meta_iqtar import MetaIqtar
from .meta_wv import MetaWv


class Meta(MetaWv, MetaIqtar):
    """Meta data for Storage container.

    Args:
        no_defaults (bool, optional): Storage meta data should have no defaults at
            initialization. Defaults to False.
    """

    def __init__(self, no_defaults: bool = False, **kwargs):
        """Initialize Meta class."""
        MetaWv.__init__(self, no_defaults, **kwargs)
        MetaIqtar.__init__(self, no_defaults, **kwargs)
