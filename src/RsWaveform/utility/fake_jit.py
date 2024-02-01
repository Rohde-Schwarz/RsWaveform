"""Fake numba jit decorator."""

try:
    from numba import jit as jit
except ImportError:

    def jit(
        signature_or_function=None,
        locals={},
        cache=False,
        pipeline_class=None,
        boundscheck=None,
        **options,
    ):
        """Fake decorator for numba."""
        if signature_or_function is not None and callable(signature_or_function):
            return signature_or_function
        else:
            return lambda fn: fn
