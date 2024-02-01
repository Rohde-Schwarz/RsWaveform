import io
import os
import tarfile
import tempfile
import typing
from contextlib import contextmanager
from pathlib import Path

import pytest

from RsWaveform.utility.file_handling import (
    read_file_handle,
    read_file_handle_tar,
    write_file_handle,
    write_file_handle_tar,
)


@pytest.fixture
def content() -> bytes:
    return b"test"


@pytest.fixture
def file_name() -> str:
    return "test.txt"


@pytest.fixture
def file(file_name, content) -> str:  # type: ignore[misc]
    with open(file_name, "wb") as fp:
        fp.write(content)
    yield file_name
    if os.path.exists(file_name):
        os.remove(file_name)


@pytest.fixture
def empty_file(file_name: str) -> str:  # type: ignore[misc]
    yield file_name
    if os.path.exists(file_name):
        os.remove(file_name)


@contextmanager
def create_temp_tarfile(
    contents: typing.Dict[str, bytes]
) -> typing.Generator[Path, None, None]:
    """Create a temporary tar file with the given contents."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        with tarfile.open(temp_file.name, "w:") as tar:
            for name, data in contents.items():
                info = tarfile.TarInfo(name)
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
    yield Path(temp_file.name)
    Path(temp_file.name).unlink()


def test_read_file_with_file_name(file, content):
    read_file(file, content)


def test_read_file_with_file_path(file, content):
    read_file(Path(file), content)


def test_read_file_with_file_io(file, content):
    with open(file, "rb") as ofp:
        read_file(ofp, content)


def test_write_file_with_file_io(empty_file, content):
    with open(empty_file, "wb") as ofp:
        write_file(ofp, content)
    read_file(empty_file, content)


def test_write_file_with_file_name(empty_file, content):
    write_file(empty_file, content)
    read_file(empty_file, content)


def test_write_file_with_file_path(empty_file, content):
    write_file(Path(empty_file), content)
    read_file(Path(empty_file), content)


def write_file(file_name, content):
    with write_file_handle(file_name) as fp:
        fp.write(content)


def read_file(file, content):
    with read_file_handle(file) as fp:
        read = fp.read()
        assert read == content


def test_write_file_with_path(empty_file, content):
    write_file(Path(empty_file), content)
    read_file(Path(empty_file), content)


def test_read_file_handle_tar_existing_tarfile():
    with create_temp_tarfile({"file1.txt": b"Hello, World!"}) as temp_tar:
        with read_file_handle_tar(temp_tar) as tar:
            assert isinstance(tar, tarfile.TarFile)
            assert "file1.txt" in tar.getnames()


def test_read_file_handle_tar_nonexistent_tarfile():
    with pytest.raises(FileNotFoundError):
        with read_file_handle_tar("nonexistent.tar"):
            pass


def test_write_file_handle_tar():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_tar = Path(temp_dir) / "test.tar"
        name = "file1.txt"
        data = b"Hello, World!"
        with write_file_handle_tar(temp_tar) as tar:
            assert isinstance(tar, tarfile.TarFile)
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))

            with read_file_handle_tar(tar) as sub_tar:
                assert "file1.txt" in sub_tar.getnames()
                member = sub_tar.getmember("file1.txt")
                assert member.size == len(data)  # length of "Hello, World!"

        with open(temp_tar, mode="rb") as read_tar:
            with read_file_handle_tar(io.BytesIO(read_tar.read())) as sub_tar:
                assert "file1.txt" in sub_tar.getnames()
                member = sub_tar.getmember("file1.txt")
                assert member.size == len(data)  # length of "Hello, World!"

        with read_file_handle_tar(temp_tar) as tar:
            assert "file1.txt" in tar.getnames()
            member = tar.getmember("file1.txt")
            assert member.size == len(data)  # length of "Hello, World!"
