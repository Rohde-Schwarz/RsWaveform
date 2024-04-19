"""Save implementation for generic waveform."""

from __future__ import annotations

import math
import typing

import numpy as np

from ..meta.defaults import META_WV_DEFAULTS as META_DEFAULTS
from ..parent_storage import ParentStorage
from ..save_interface import SaveInterface
from ..storage import Storage
from ..utility.dsp import calculate_peak, calculate_rms
from ..utility.fake_jit import jit
from ..utility.file_handling import write_file_handle
from .utility.array_to_bytes import pack_bool_array_to_bytes

if typing.TYPE_CHECKING:
    from pathlib import Path


class Save(SaveInterface):
    """Save class for generic waveform."""

    def save(
        self,
        file: typing.Union[str, typing.IO, Path],
        datas: ParentStorage,
        scale: float = np.power(2, np.iinfo(np.int16).bits - 1),
    ) -> None:
        """Save waveform data to file."""
        if datas.number_of_storages() == 1:
            self._write(file, datas, scale)
        else:
            self._write_mwv(file, datas, scale)

    def _write(
        self,
        file: typing.Union[str, typing.IO, Path],
        data: ParentStorage,
        scale: float = np.power(2, np.iinfo(np.int16).bits - 1),
    ):
        int16_data = self._prepare_data(data.storages[0], scale)
        with write_file_handle(file) as fp:
            self._write_type(fp, data.storages[0])
            self._write_copyright(fp, data.storages[0])
            self._write_comment(fp, data.storages[0])
            self._write_level_offset(fp, data.storages[0])
            self._write_date(fp, data)
            self._write_clock(fp, data.storages[0])
            self._write_samples(fp, data.storages[0])
            self._write_reflevel(fp, data.storages[0])

            self._write_control_length(fp, data.storages[0])
            self._write_control_list(fp, data.storages[0])
            self._write_marker(fp, data.storages[0])

            self._write_empty_tag(fp)
            self._write_waveform(
                fp, int16_data, data.storages[0].meta.get("encryption_flag", False)
            )

    def _write_mwv(
        self,
        file: typing.Union[str, typing.IO, Path],
        datas: ParentStorage,
        scale: float = np.power(2, np.iinfo(np.int16).bits - 1),
    ):
        tmp_storage = Storage()
        tmp_storage.data = np.array([])
        for d in datas.storages:
            tmp_storage.data = np.append(d.data, tmp_storage.data)
        # first storage used as reference
        tmp_storage.meta.update(datas.storages[0].meta)
        tmp_storage.meta["type"] = "SMU-MWV"
        int16_data = self._prepare_data(tmp_storage, scale)
        with write_file_handle(file) as fp:
            self._write_type(fp, tmp_storage)
            self._write_copyright(fp, tmp_storage)
            self._write_date(fp, datas)
            self._write_samples(fp, tmp_storage)
            self._write_reflevel(fp, tmp_storage)

            self._write_mwv_segment_count(fp, datas)
            self._write_mwv_segment_length(fp, datas.storages)
            self._write_mwv_segment_start(fp, datas.storages)
            self._write_mwv_clock_mode(fp)
            self._write_mwv_level_mode(fp)

            self._write_mwv_clock(fp, datas.storages)
            self._write_mwv_segment_level_offs(fp, datas.storages)
            self._write_mwv_segment_comment(fp, datas.storages)
            self._write_mwv_segment_files(fp, datas.storages)

            self._write_empty_tag(fp)
            self._write_waveform(
                fp, int16_data, tmp_storage.meta.get("encryption", False)
            )

    @staticmethod
    @jit(forceobj=True)
    def _prepare_data(
        data: Storage, scale: float = np.power(2, np.iinfo(np.int16).bits - 1)
    ) -> np.ndarray:
        samples = len(data.data)
        dt = np.int16
        info = np.iinfo(dt)
        int16_samples = np.zeros((2 * samples,)).astype(dt)
        real = np.round(scale * np.real(data.data))
        real[real > info.max] = info.max
        real[real < info.min] = info.min
        int16_samples[slice(0, None, 2)] = real.astype(dt)
        imag = np.round(scale * np.imag(data.data))
        imag[imag > info.max] = info.max
        imag[imag < info.min] = info.min
        int16_samples[slice(1, None, 2)] = imag.astype(dt)
        return int16_samples

    @staticmethod
    def _write_type(file: typing.IO, data: Storage):
        type_data = data.meta.get("type", META_DEFAULTS["type"])
        if isinstance(type_data, tuple):
            type_data = type_data[0]
        line = f"{{TYPE:{type_data}}}"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_copyright(file: typing.IO, data: Storage):
        line = f"{{COPYRIGHT:{data.meta.get('copyright', META_DEFAULTS['copyright'])}}}"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_comment(file: typing.IO, data: Storage):
        line = f"{{COMMENT:{data.meta.get('comment', META_DEFAULTS['comment'])}}}"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_date(file: typing.IO, data: ParentStorage):
        date = data.timestamp
        line = f"{{DATE:{date.strftime('%Y-%m-%d;%H:%M:%S')}}}"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_level_offset(file: typing.IO, data: Storage):
        def invert_values(value: float) -> float:
            if value != 0.0:
                value = value * -1
            return value

        peak = data.meta.get("peak")
        rms = data.meta.get("rms")
        if peak is None:
            peak = invert_values(calculate_peak(data.data))
        if rms is None:
            rms = invert_values(calculate_rms(data.data))
        line = f"{{LEVEL OFFS:{rms:.6f},{peak:.6f}}}"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_clock(file: typing.IO, data: Storage):
        clock = data.meta.get("clock")
        if not clock:
            raise ValueError("Clock is a mandatory parameter!")
        line = f"{{CLOCK:{clock}}}"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_samples(file: typing.IO, data: Storage):
        line = f"{{SAMPLES:{len(data.data)}}}"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_reflevel(file: typing.IO, data: Storage):
        reflevel = data.meta.get("reflevel")
        if reflevel:
            line = f"{{REFLEVEL:{reflevel:.6f}}}"
            file.write(line.encode("utf-8"))

    @staticmethod
    def _write_marker(file: typing.IO, data: Storage):
        marker_keys = [
            key for key in data.meta.get("marker", {}) if key.startswith("marker_list")
        ]
        if not marker_keys:
            return
        for marker in marker_keys:
            marker_string = ";".join(
                [
                    ":".join([str(el) for el in entry])
                    for entry in data.meta["marker"][marker]
                ]
            )
            line = f"{{{marker.replace('_', ' ').upper()}: {marker_string}}}"
            file.write(line.encode("utf-8"))

    @staticmethod
    def _write_control_length(file: typing.IO, data: Storage):
        control_length = data.meta.get("control_length")
        if not control_length:
            return
        line = f"{{CONTROL LENGTH:{control_length}}}"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_control_list(file: typing.IO, data: Storage):
        control_list = data.meta.get("control_list")
        if control_list is None:
            return
        if isinstance(control_list, list):
            control_list = np.array(control_list)
        list_bytes = pack_bool_array_to_bytes(control_list)
        line = f"{{CONTROL LIST WIDTH4-{len(list_bytes) + 1}:#"
        file.write(line.encode())
        file.write(list_bytes)
        file.write(b"}")

    @staticmethod
    def _write_empty_tag(file: typing.IO):
        scale = 512
        rand_empty = int(np.around(np.random.rand() * scale))
        line = f"{{EMPTYTAG-{rand_empty + 1}:#"
        file.write(line.encode("utf-8"))
        empty = 32 * np.ones((rand_empty,)).astype(np.uint8)
        file.write(empty.tobytes())
        file.write(b"}")

    @staticmethod
    def _write_waveform(
        file: typing.IO, int16_data: np.ndarray, encryption_flag: bool = False
    ):
        prefix = "W" if encryption_flag else ""
        line = f"{{{prefix}WAVEFORM-{len(int16_data) * 2 + 1}:#"
        file.write(line.encode())
        chunk_size = 82000000  # randomly chosen number. Might be changed!
        number_blocks = math.ceil(int16_data.size / chunk_size)
        for block_idx in range(number_blocks):
            idx_start = block_idx * chunk_size
            idx_stop = (block_idx + 1) * chunk_size
            if idx_stop > int16_data.size - 1:
                idx_stop = int16_data.size
            bins = int16_data[idx_start:idx_stop].tobytes()
            file.write(bins)
        file.write(b"}")

    @staticmethod
    def _write_mwv_segment_count(file: typing.IO, datas: ParentStorage):
        line = f"{{MWV_SEGMENT_COUNT:{datas.number_of_storages()}}}"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_mwv_segment_length(file: typing.IO, datas: typing.List[Storage]):
        segment_length = []
        for data in datas:
            segment_length.append(str(len(data.data)))
        line = f"{{MWV_SEGMENT_LENGTH:{','.join(segment_length)}}}"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_mwv_segment_start(file: typing.IO, datas: typing.List[Storage]):
        segment_start = []
        start_segment = 0
        for data in datas:
            segment_start.append(str(start_segment))
            start_segment += len(data.data)
        line = f"{{MWV_SEGMENT_START:{','.join(segment_start)}}}"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_mwv_clock(file: typing.IO, datas: typing.List[Storage]):
        max_clock: float = 0.0
        all_clocks = []
        for data in datas:
            if float(data.meta.get("clock", 0)) > max_clock:
                max_clock = float(data.meta.get("clock", 0))
            all_clocks.append(str(data.meta.get("clock")))
        line = f"{{CLOCK:{max_clock}}}"
        file.write(line.encode("utf-8"))
        line = f"{{MWV_SEGMENT_CLOCK:{','.join(all_clocks)}}}"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_mwv_segment_level_offs(file: typing.IO, datas: typing.List[Storage]):
        level_offs = []
        for data in datas:
            level_offs.append(str(data.meta.get("rms", 0)))
            level_offs.append(str(data.meta.get("peak", 0)))
        line = f"{{MWV_SEGMENT_LEVEL_OFFS:{','.join(level_offs)}}}"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_mwv_clock_mode(file: typing.IO, mode: str = "UNCHANGED"):
        line = f"{{MWV_SEGMENT_CLOCK_MODE:{mode}}}"
        file.write(line.encode())

    @staticmethod
    def _write_mwv_level_mode(file: typing.IO, mode: str = "UNCHANGED"):
        line = f"{{MWV_SEGMENT_LEVEL_MODE:{mode}}}"
        file.write(line.encode())

    @staticmethod
    def _write_mwv_segment_comment(file: typing.IO, datas: typing.List[Storage]):
        for index, data in enumerate(datas):
            line = f"{{MWV_SEGMENT{index}_COMMENT:{data.meta.get('comment')}}}"
            file.write(line.encode("utf-8"))

    @staticmethod
    def _write_mwv_segment_files(file: typing.IO, datas: typing.List[Storage]):
        file_names = []
        for data in datas:
            if "filename" in data.meta:
                file_names.append(str(data.meta.get("filename", "")))
        if file_names:
            line = f"{{MWV_SEGMENT_FILES:{','.join(file_names)}}}"
            file.write(line.encode("utf-8"))
