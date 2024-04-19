"""Load implementation for iqtar."""

from __future__ import annotations

import os
import typing
import xml.etree.ElementTree as ET
from datetime import datetime
from io import BytesIO

import numpy as np

from RsWaveform.meta import Meta

from ..iqw import Load as LoadIqw
from ..load_interface import LoadInterface
from ..parent_storage import ParentStorage
from ..storage import Storage
from ..utility.file_handling import read_file_handle, read_file_handle_tar
from ..utility.meta_utils import map_meta_information_name

if typing.TYPE_CHECKING:
    from pathlib import Path


class Load(LoadInterface):
    """Load class for iqw."""

    def load(self, file: typing.Union[str, typing.IO, Path]) -> ParentStorage:
        """Load iq tar data from file."""
        parent_storage = self._read(file)
        if isinstance(file, str):
            parent_storage.filename = file
        return parent_storage

    def load_in_chunks(
        self, file: typing.Union[str, typing.IO, Path], samples: int, offset: int
    ) -> ParentStorage:
        """Load chunk iq tar data from file."""
        parent_storage = self._read_in_chunks(file, samples, offset)
        if isinstance(file, str):
            parent_storage.filename = file
        return parent_storage

    def load_meta(self, file: typing.Union[str, typing.IO, Path]) -> ParentStorage:
        """Load meta information only from iqtar file."""
        xml_content = self._extract_data_from_xml_file(file)
        tags = self._split_data_via_tags(xml_content)
        meta = self._extract_meta(tags)
        parent_storage = ParentStorage()
        parent_storage.storages[0].data = np.array([])
        parent_storage.storages[0].meta = Meta(**meta)
        return parent_storage

    @staticmethod
    def _allowed_tags() -> list:
        allowed_tags = [
            [["Clock"], "unit"],
            [["DataFilename"], None],
            [["Samples"], None],
            [["ScalingFactor"], "unit"],
            [["NumberOfChannels"], "unit"],
            [["DataType"], None],
            [["Format"], None],
            [["Name"], None],
            [["Comment"], None],
            [["DateTime"], None],
            [["UserData", "RohdeSchwarz", "SpectrumAnalyzer", "CenterFrequency"], None],
        ]
        return allowed_tags

    def _split_data_via_tags(self, content: bytes) -> dict:
        with BytesIO(content) as content_handle:
            tree = ET.parse(content_handle)
            root = tree.getroot()
            extracted: typing.Dict[str, typing.Any] = {}
            allowed_tags = self._allowed_tags()
            for tags, unit in allowed_tags:
                tag = "/".join(tags)
                search_tag = tag.replace("_", " ")
                meta_key = tags[-1].lower()
                xml_tag = root.find(search_tag)
                if xml_tag is not None:
                    value = xml_tag.text
                    if unit:
                        unit = xml_tag.get(unit)
                    else:
                        unit = None
                    extracted.update(
                        {map_meta_information_name(meta_key): [value, unit]}
                    )
            del root
        return extracted

    @staticmethod
    def _extract_meta(tags: dict) -> dict:
        meta = {}
        for key, [value, unit] in tags.items():
            if isinstance(value, bytes):
                value = value.decode()
            if key == "clock":
                value = float(value)
            elif key == "samples":
                continue
            elif key == "numberofchannels":
                value = int(value)
            elif key == "scalingfactor":
                value = float(value)
                if unit and unit != "V":
                    raise ValueError("unsupported unit!")
            elif key == "datafilename":
                value = str(value)
            elif key == "date":
                date_pattern = "%Y-%m-%dT%H:%M:%S" + (".%f" if "." in value else "")
                value = datetime.strptime(value, date_pattern)
            meta.update({key: value})
        return meta

    @staticmethod
    def _extract_data_from_xml_file(file: typing.Union[str, typing.IO, Path]) -> bytes:
        with read_file_handle_tar(file) as tar:
            files = tar.getnames()
            xml_filenames = [file for file in files if ".xml" in file.lower()]
            xml_filename = xml_filenames[0]
            tar.extract(xml_filename)
        with read_file_handle(xml_filename) as fp:
            content = fp.read()
        os.remove(xml_filename)
        return content

    @staticmethod
    def _extract_data_from_binary_file(
        file: typing.Union[str, typing.IO, Path], binary_filename: str
    ) -> bytes:
        with read_file_handle_tar(file) as tar:
            tar.extract(binary_filename)
        with read_file_handle(binary_filename) as fp:
            content = fp.read()
        os.remove(binary_filename)
        return content

    @staticmethod
    def _extract_data_from_binary_file_chunks(
        file: typing.Union[str, typing.IO, Path],
        binary_filename: str,
        nr_samples: int,
        samples_offset: int,
    ) -> bytes:
        with read_file_handle_tar(file) as tar:
            tar.extract(binary_filename)
        with read_file_handle(binary_filename) as fp:
            fp.read(samples_offset * 4 * 2)
            content = fp.read(nr_samples * 4 * 2)
        os.remove(binary_filename)
        return content

    @staticmethod
    def _extract_data(content: bytes) -> np.ndarray:
        parent_storage = ParentStorage()
        parent_storage.storages = []
        load_iqw = LoadIqw()
        with BytesIO(content) as file_handle:
            iq_storage = load_iqw.load(file_handle)
        return iq_storage.storages[0].data

    @staticmethod
    def _scale_data(data: np.ndarray, meta: dict) -> np.ndarray:
        scaling_factor = meta.get("scalingfactor", 1)
        if scaling_factor != 1:
            data = scaling_factor * data
        return data

    def _read(self, file: typing.Union[str, typing.IO, Path]) -> ParentStorage:
        xml_content = self._extract_data_from_xml_file(file)

        tags = self._split_data_via_tags(xml_content)
        meta = self._extract_meta(tags)

        binary_file_name = meta.pop("datafilename")
        binary_content = self._extract_data_from_binary_file(file, binary_file_name)

        samples = self._extract_data(binary_content)
        samples = self._scale_data(samples, meta)

        parent_storage = ParentStorage()
        parent_storage.storages = []
        number_of_channels = meta.pop("numberofchannels", 1)
        for channel in range(number_of_channels):
            storage = Storage()
            samples_per_channel = int(len(samples) / number_of_channels)
            storage.data = samples[
                channel * samples_per_channel : samples_per_channel * (channel + 1)
            ]
            storage.meta = Meta(**meta)
            parent_storage.storages.append(storage)
        return parent_storage

    def _read_in_chunks(
        self,
        file: typing.Union[str, typing.IO, Path],
        nr_samples: int,
        samples_offset: int,
    ) -> ParentStorage:
        xml_content = self._extract_data_from_xml_file(file)

        tags = self._split_data_via_tags(xml_content)
        meta = self._extract_meta(tags)

        number_of_channels = meta.pop("numberofchannels", 1)
        if number_of_channels > 1:
            raise ValueError("Reading in chunks only supported for single channel!")

        binary_file_name = meta.pop("datafilename")
        binary_content = self._extract_data_from_binary_file_chunks(
            file, binary_file_name, nr_samples, samples_offset
        )

        samples = self._extract_data(binary_content)
        samples = self._scale_data(samples, meta)

        parent_storage = ParentStorage()
        parent_storage.storages = []

        storage = Storage()
        storage.data = samples
        storage.meta = Meta(**meta)
        parent_storage.storages.append(storage)
        return parent_storage
