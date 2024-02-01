"""File handling utilities."""

from __future__ import annotations

import io
import tarfile
import typing
from contextlib import contextmanager

if typing.TYPE_CHECKING:
    from pathlib import Path


@contextmanager
def read_file_handle(
    file: typing.Union[str, typing.IO, Path]
) -> typing.Generator[typing.IO, None, None]:
    """Read from a waveform file."""
    return _file_handle(file, "rb")


@contextmanager
def write_file_handle(
    file: typing.Union[str, typing.IO, Path]
) -> typing.Generator[typing.IO, None, None]:
    """Write to a waveform file."""
    return _file_handle(file, "wb+")


def _file_handle(
    file: typing.Union[str, typing.IO, Path],
    mode: str,
    encoding: typing.Optional[str] = None,
) -> typing.Generator[typing.IO, None, None]:
    """File handler context manager implementation."""
    if isinstance(file, io.IOBase):
        yield file
    else:
        with open(typing.cast(str, file), mode, encoding=encoding) as f:
            yield f


@contextmanager
def read_file_handle_tar(
    file: typing.Union[str, tarfile.TarFile, typing.IO, Path]
) -> typing.Generator[tarfile.TarFile, None, None]:
    """Read from a tar file."""
    return _file_handle_tar(file, "r:")


@contextmanager
def write_file_handle_tar(
    file: typing.Union[str, tarfile.TarFile, typing.IO, Path]
) -> typing.Generator[tarfile.TarFile, None, None]:
    """Write to a tar file."""
    return _file_handle_tar(file, "w:")


def _file_handle_tar(
    file: typing.Union[str, tarfile.TarFile, typing.IO, Path], mode: str
) -> typing.Generator[tarfile.TarFile, None, None]:
    """File handler context manager implementation."""
    if isinstance(file, tarfile.TarFile):
        yield file
    elif isinstance(file, io.BytesIO):
        with tarfile.open(fileobj=file, mode=mode) as f:  # not perfect
            yield f
    else:
        with tarfile.open(typing.cast(str, file), mode) as f:
            yield f
