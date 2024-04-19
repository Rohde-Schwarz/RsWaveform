"""Load implementation for generic waveform."""

from __future__ import annotations

import logging
import re
import typing
from datetime import datetime

import numpy as np

from ..load_interface import LoadInterface
from ..meta import Meta
from ..parent_storage import ParentStorage
from ..storage import Storage
from ..utility.fake_jit import jit
from ..utility.file_handling import read_file_handle
from .utility.array_to_bytes import unpack_bytes_to_bool_array

if typing.TYPE_CHECKING:
    from pathlib import Path


LOGGER = logging.getLogger(__name__)


class Load(LoadInterface):
    """Load class for generic waveform."""

    def load(self, file: typing.Union[str, typing.IO, Path]) -> ParentStorage:
        """Load waveform data from file."""
        with read_file_handle(file) as fp:
            content = fp.read()

        tags = self._split_data_via_tags_meta(content)
        samples = int(tags["samples"])
        mwv_segment_count = int(tags.pop("mwv_segment_count", 1))

        tags.update(self._split_data_via_tags_waveform(content))
        tags.update(self._split_data_via_tags_control_list_width4(content, samples))

        parent_storage = ParentStorage()
        if isinstance(file, str):
            parent_storage.filename = file
        storages = [Storage() for _ in range(mwv_segment_count)]
        if mwv_segment_count > 1:  # multi segment waveform
            value = tags.pop("mwv_segment_length").decode()
            tags = self._extract_mwv_comments(mwv_segment_count, tags, content)
            segment_lengths = [int(length) for length in value.split(",")]

        else:
            segment_lengths = [samples]

        iq_data = self._extract_iq(tags)
        for index in range(mwv_segment_count):
            start_index = sum(segment_lengths[0:index])
            end_index = segment_lengths[index] + start_index
            storages[index].data = iq_data[start_index:end_index]
            meta = self._extract_meta(tags, index)
            meta = self._handle_mwv_meta_data(meta, index)
            storages[index].meta = Meta(**meta)
        if samples != len(iq_data):
            LOGGER.warning(
                (
                    "Sanity problem. Sample count from tag '%s' and actual sample "
                    "count from bytes '%s' does not match."
                ),
                samples,
                len(iq_data),
            )
        parent_storage.storages = storages
        return parent_storage

    @staticmethod
    def _read_chunks(stream: typing.IO, separators: list) -> typing.Tuple[bytes, bytes]:
        regex = "(" + "|".join(separators) + ")"
        chunk_size = 4096
        buffer = b""
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                return buffer, b""
            buffer += chunk
            while True:
                try:
                    part, separator, buffer = re.split(regex.encode("utf-8"), buffer)
                except ValueError:
                    break
                else:
                    return part, separator + buffer

    def load_in_chunks(
        self,
        file: typing.Union[str, typing.IO, Path],
        samples: int,
        offset: int,
    ) -> ParentStorage:
        """Load chunk waveform data from file."""
        separators = ["{WWAVEFORM", "{WAVEFORM"]
        with read_file_handle(file) as fp:
            header_content, content = self._read_chunks(fp, separators)
            content += fp.read((samples + 4) * 4 + 100)
            # +4 due to opt words and 100 just an offset to make sure we get everything

        tags = self._split_data_via_tags_meta(header_content)
        tags.update(self._split_data_via_tags_waveform(content, True))
        tags.update(
            self._split_data_via_tags_control_list_width4(content, samples, True)
        )

        mwv_segment_count = int(tags.pop("mwv segment count", 1))
        if mwv_segment_count > 1:  # multi segment waveform
            raise ValueError("feature only supported for non multi segment wv")
        parent_storage = ParentStorage()
        if isinstance(file, str):
            parent_storage.filename = file
        storages = [Storage() for _ in range(mwv_segment_count)]
        iq_data = self._extract_iq_chunks(tags, samples, offset)
        index = 0
        storages[index].data = iq_data
        meta = self._extract_meta(tags, index)
        meta = self._handle_mwv_meta_data(meta, index)
        storages[index].meta = Meta(**meta)
        if samples != len(iq_data):
            raise ValueError(
                "Sanity problem. Sample setting and actual sample count does not match."
            )
        parent_storage.storages = storages
        return parent_storage

    def load_meta(self, file: typing.Union[str, typing.IO, Path]) -> ParentStorage:
        """Load meta information only from wv file."""
        separators = ["{WWAVEFORM", "{WAVEFORM"]
        with read_file_handle(file) as fp:
            header_content, _ = self._read_chunks(fp, separators)

        tags = self._split_data_via_tags_meta(header_content)
        samples = int(tags["samples"])
        tags.update(
            self._split_data_via_tags_control_list_width4(header_content, samples)
        )
        meta = self._extract_meta(tags)
        parent_storage = ParentStorage()
        parent_storage.storages[0].meta = Meta(**meta)
        parent_storage.storages[0].data = np.array([])
        return parent_storage

    @staticmethod
    @jit(forceobj=True)
    def _extract_iq(tags: dict) -> np.ndarray:
        iq_bytes = tags.pop("waveform")
        if not iq_bytes:
            raise ValueError("No waveform data availabe.")
        from_dtype = np.dtype(np.int16)
        to_dtype = np.dtype(np.float16)
        i_values = Load._fix_to_double(
            np.frombuffer(
                buffer=Load._extract_pairs(iq_bytes, 0),
                dtype=from_dtype,
            ),
            to_dtype,
        )
        q_values = Load._fix_to_double(
            np.frombuffer(
                buffer=Load._extract_pairs(iq_bytes, 1),
                dtype=from_dtype,
            ),
            to_dtype,
        )
        iq = i_values + 1j * q_values
        return iq

    @staticmethod
    @jit(forceobj=True)
    def _extract_iq_chunks(
        tags: dict, nr_samples: int, samples_offset: int
    ) -> np.ndarray:
        iq_bytes = tags.pop("waveform")

        if not iq_bytes:
            raise ValueError("No waveform data availabe.")
        from_dtype = np.dtype(np.int16)
        to_dtype = np.dtype(np.float16)
        i_values = Load._fix_to_double(
            np.frombuffer(
                buffer=Load._extract_pairs(
                    iq_bytes, 0, length=nr_samples, offset=samples_offset
                ),
                dtype=from_dtype,
            ),
            to_dtype,
        )
        q_values = Load._fix_to_double(
            np.frombuffer(
                buffer=Load._extract_pairs(
                    iq_bytes, 1, length=nr_samples, offset=samples_offset
                ),
                dtype=from_dtype,
            ),
            to_dtype,
        )
        iq = i_values + 1j * q_values
        return iq

    @staticmethod
    @jit(forceobj=True)
    def _fix_to_double(values: np.ndarray, to_float_type: np.dtype) -> np.ndarray:
        dt_info = np.iinfo(values.dtype)
        maximum = to_float_type.type(dt_info.max)
        converted = to_float_type.type(values) / maximum
        return converted

    @staticmethod
    @jit(forceobj=True)
    def _extract_pairs(
        buf: bytes, start: int = 0, offset: int = 0, length: int = 0
    ) -> bytes:
        """Extract data pairs from binary buffer."""
        actual_length = length * 4
        actual_offset = offset * 4
        single_pair = bytearray()
        if actual_length == 0 or actual_length > len(buf):
            actual_length = len(buf)
            actual_offset = 0
        if actual_length + actual_offset > len(buf):
            actual_offset = len(buf) - actual_length
        indices = np.arange(start * 2 + actual_offset, actual_offset + actual_length, 4)
        for idx in indices:
            temp = buf[idx : idx + 2]
            single_pair.extend(temp)
        return single_pair

    @staticmethod
    def _extract_meta(tags: dict, index: int = 0) -> dict:
        meta: typing.Dict[str, typing.Any] = {}
        marker = {}
        for key, value in tags.items():
            if isinstance(value, bytes):
                value = value.decode()
            if key == "type":
                value = tuple(x.strip() for x in value.split(","))[0]
            elif key == "level_offs":
                offset, peak = value.split(",")
                value = None
                meta.update(rms=float(offset), peak=float(peak))
            elif key in ["vector_max", "clock"]:
                value = float(value)
            elif key == "date":
                value = datetime.strptime(value, "%Y-%m-%d;%H:%M:%S")
            elif key == "control_length":
                value = int(value)
            elif re.match(r"marker_list_\d+", key):
                marker_list = []
                for sub in value.split(";"):
                    marker_list.append([int(x) for x in sub.split(":")])
                if marker_list:
                    marker.update({key: marker_list})
                continue
            elif key == "samples":
                value = int(value)
            elif key == "reflevel":
                value = float(value)
            elif key == "mwv_segment_level_offs":
                possible_values = value.split(",")
                offset = possible_values[index * 2]
                peak = possible_values[index * 2 + 1]
                value = (float(offset), float(peak))
            elif key == "mwv_segment_clock":
                value = float(value.split(",")[index])
            elif key == "mwv_segment_length":
                value = float(value.split(",")[index])
            elif (
                re.search(r"mwv_segment\d{1,}_comment", key)
                and key != f"mwv_segment{index}_comment"
            ):
                continue
            if value is None:
                continue
            meta.update({key: value})
        meta.update(marker=marker)
        return meta

    @staticmethod
    def _handle_mwv_meta_data(meta: dict, index: int = 0) -> dict:
        if "mwv_segment_clock" in meta:
            meta["clock"] = meta.pop("mwv_segment_clock")
        if "mwv_segment_level_offs" in meta:
            offset, peak = meta.pop("mwv_segment_level_offs")
            meta.update(rms=float(offset), peak=float(peak))
        if "mwv_segment_length" in meta:
            meta["samples"] = meta.pop("mwv_segment_length")
        if f"mwv_segment{index}_comment" in meta:
            meta["comment"] = meta.pop(f"mwv_segment{index}_comment")
        return meta

    @staticmethod
    @jit(forceobj=True)
    def _split_data_via_tags_meta(content: bytes) -> dict:
        tok_regex = Load._create_regex_pattern()
        extracted: typing.Dict[str, typing.Any] = {}
        for mo in re.finditer(tok_regex, content):
            if not mo.lastgroup:
                continue
            kind = mo.lastgroup
            value = mo.group()
            extracted.update({kind: value})
        return extracted

    @staticmethod
    def _split_data_via_tags_waveform(
        content: bytes, partial_read: bool = False
    ) -> dict:
        extracted: typing.Dict[str, typing.Any] = {}
        # search for waveform data
        waveform, encryption_flag = Load._extract_waveform(content, partial_read)
        extracted.update({"waveform": waveform, "encryption_flag": encryption_flag})
        return extracted

    @staticmethod
    def _split_data_via_tags_control_list_width4(
        content: bytes, samples: int, partial_read: bool = False
    ) -> dict:
        extracted: typing.Dict[str, typing.Any] = {}
        # search for waveform data
        control_list = Load._extract_binary_tags(
            content, "CONTROL LIST WIDTH4", partial_read
        )
        if control_list:
            unpacked_list = unpack_bytes_to_bool_array(control_list, samples)
            extracted.update({"control_list": unpacked_list})
        return extracted

    @staticmethod
    @jit(forceobj=True)
    def _extract_waveform(
        content: bytes, partial_read: bool = False
    ) -> typing.Tuple[bytes, bool]:
        m_waveform = re.search(rb"(?<={)(\w{0,1}WAVEFORM)", content)
        if not m_waveform:
            raise ValueError("Waveform does not contain waveform tag.")
        encryption_flag = Load._is_waveform_encrypted(
            content[m_waveform.start() : m_waveform.end()]
        )
        iq = Load._extract_binary_tags(
            content, f"{'W' if encryption_flag else ''}WAVEFORM", partial_read
        )
        return iq, encryption_flag

    @staticmethod
    @jit(forceobj=True)
    def _extract_binary_tags(
        content: bytes, tag: str, partial_read: bool = False
    ) -> typing.Optional[bytes]:
        m_tag = re.search(rb"(?<={)(%s)" % tag.encode("utf-8"), content)
        if not m_tag:
            return None
        start_index = m_tag.start()
        tag_content = content[start_index:]
        m_content = re.findall(
            rb"(?<=%s\-)([\d]+)(?=\:)" % tag.encode("utf-8"), tag_content
        )
        if not m_content:
            raise ValueError(f"Waveform does not contain {tag} byte count.")
        count = int(m_content[0].decode())
        pattern = rf"{count}:( |)#".encode("utf-8")  # Binary data
        m_pattern = re.search(pattern, tag_content)
        if not m_pattern:
            raise ValueError(
                f"Could not extract {tag} data. Could not find {tag} section."
            )
        start_index = m_pattern.end()
        end_index = (len(content) if partial_read else start_index + count) - 1
        if start_index + count > len(tag_content) and partial_read is False:
            raise ValueError(
                f"Could not extract {tag} data. Provided byte count inconclusive."
            )
        binary = tag_content[start_index:end_index]
        if partial_read is False:
            closing = tag_content[end_index]
            if chr(closing) != "}":
                raise ValueError(
                    f"Could not extract {tag} data. Malformed {tag} section because "
                    f"there is no '}}' after {count} binary samples."
                )

        return binary

    @staticmethod
    @jit(forceobj=True)
    def _is_waveform_encrypted(waveform_tag: bytes) -> bool:
        encrypted = re.findall(rb"(\w{0,1})WAVEFORM", waveform_tag, re.IGNORECASE)
        if encrypted[0] == b"":
            return False
        if encrypted[0] != b"W":
            raise ValueError(
                f"Not supported waveform tag format {waveform_tag.decode()}"
            )
        return True

    @staticmethod
    def _create_regex_pattern() -> bytes:
        token_specification = Load._get_regex_tokens()
        tok_regex = "|".join(
            rf"(?P<{pair[0].lower().replace(' ', '_').replace('.', '')}"
            rf"{'_%s' % pair[1].replace(' ', '') if pair[1] != '' else ''}>"
            rf"(?<={{{pair[0]}{pair[1]}:)\s{{0,1}}({pair[2]})(?=}}))"
            for pair in token_specification
        )
        return tok_regex.encode("utf-8")

    @staticmethod
    def _get_regex_tokens() -> list:
        token_specification = [
            ("TYPE", r"", r"([\w-]+)(,[\s]*([\d]+))?"),  # Waveform type
            ("COPYRIGHT", r"", r"[\w \&]+"),  # Copyright of waveform
            ("COMMENT", r"", r"[\w \.]+"),  # Copyright of waveform
            ("DATE", r"", r"[\d\-;\:]+"),  # Timestamp of waveform
            ("SAMPLES", r"", r"[\de\-\+]+"),  # Sample count
            ("CLOCK", r"", r"[\d\.e\-\+]+"),  # Waveform sampling frequency
            ("REFLEVEL", r"", r"[\d\.e\-\+]+"),  # Reference level for playback
            ("VECTOR MAX", r"", r"[\d\.\-e\+]+"),  # tbd
            ("LEVEL OFFS", r"", r"([\d\.\-e\+]+),([\d\.\-e\+]+)"),
            # Level offset to dBFS
            ("CONTROL LENGTH", r"", r"[\d\.e\-\+]+"),  # control length count
            ("MWV_SEGMENT_LENGTH", r"", r"[\d,]+"),  # multi segment length
            ("MWV_SEGMENT_COUNT", r"", r"[\de\.\+\-]+"),  # multi segment counter
            ("MWV_SEGMENT_CLOCK", r"", r"[\d\.e\-\+,]+"),
            # list of clocks in multi segment wv
            ("MWV_SEGMENT_LEVEL_OFFS", r"", r"[\d\.e\-\+,]+"),
            # list of level offsets in multi segment wv
        ]
        token_specification.extend(
            [
                ("MARKER LIST", f" {idx}", r"[\d:;]+") for idx in range(1, 5)
            ],  # Marker list mode x
        )

        token_specification.extend(
            [
                ("MARKER MODE", f" {idx}", r"[\w]+") for idx in range(1, 5)
            ],  # Marker list mode x
        )
        return token_specification

    @staticmethod
    def _get_regex_mwv_comment_tokens(mwv_segment_count: int) -> list:
        token_specification = [
            (f"MWV_SEGMENT{idx}_COMMENT", r"[\w \.]+")
            for idx in range(mwv_segment_count)
        ]

        return token_specification

    @staticmethod
    def _create_regex_mwv_comment_pattern(mwv_segment_count: int) -> bytes:
        token_specification = Load._get_regex_mwv_comment_tokens(mwv_segment_count)
        tok_regex = "|".join(
            rf"(?P<{pair[0].lower().replace(' ', '_').replace('.', '')}>"
            rf"(?<={{{pair[0]}:)\s{{0,1}}({pair[1]})(?=}}))"
            for pair in token_specification
        )
        return tok_regex.encode("utf-8")

    # due to the high number of mwv comments, we only extract them, if needed
    # and only the number of comments, which might be available
    @staticmethod
    def _extract_mwv_comments(
        mwv_segment_count: int, tags: dict, content: bytes
    ) -> dict:
        # due to performance issues, in the first step we only grab the part of the
        # content containing the meta, throwing away all samples
        regex = rb"^(.*?)\{W{0,1}WAV"
        for meta_part in re.finditer(regex, content):
            tok_regex = Load._create_regex_mwv_comment_pattern(mwv_segment_count)
            for mo in re.finditer(tok_regex, meta_part.group()):
                if not mo.lastgroup:
                    continue
                kind = mo.lastgroup
                value = mo.group()
                tags.update({kind: value})
        return tags
