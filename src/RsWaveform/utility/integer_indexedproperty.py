"""A IndexedProperty that check for integer keys."""

from indexedproperty import IndexedProperty


class IntegerIndexedProperty(IndexedProperty):
    """A IndexedProperty that check for integer keys."""

    class _Trampoline(IndexedProperty._Trampoline):
        def moduserindex(self, index=0):
            """Modify user index."""
            if not isinstance(index, int):
                raise ValueError("Just integer as keys allowed.")
            return super().moduserindex(index)

        def modindex(self, index=0):
            """Modify index."""
            if not isinstance(index, int):
                raise ValueError("Just integer as keys allowed.")
            return super().modindex(index)
