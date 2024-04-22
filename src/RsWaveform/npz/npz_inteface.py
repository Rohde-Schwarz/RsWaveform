"""Npz interface."""

import numpy as np
import numpy.typing as npt


class NpzInterface:
    """Interface class for Npz."""

    def __init__(self) -> None:
        """Instantiate interface class."""
        self._dtype: npt.DTypeLike = np.dtype(np.float16)

    @property
    def dtype(self) -> npt.DTypeLike:
        """Dtype for loading and saving.

        Returns:
            DTypeLike: Numpy dtype
        """
        return self._dtype

    @dtype.setter
    def dtype(self, value: npt.DTypeLike) -> None:
        """Dtype for loading and saving.

        Args:
            value (DTypeLike): Numpy dtype
        """
        self._dtype = value
