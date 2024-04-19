"""Save implementation for iqtar."""

import os
import re
import typing
from pathlib import Path

from ..iqw.save import Save as SaveIqw
from ..meta.defaults import META_IQTAR_DEFAULTS as META_DEFAULTS
from ..parent_storage import ParentStorage
from ..save_interface import SaveInterface
from ..storage import Storage
from ..utility.file_handling import write_file_handle, write_file_handle_tar


class Save(SaveInterface):
    """Save class for iqtar."""

    def save(
        self,
        file: typing.Union[str, typing.IO, Path],
        datas: ParentStorage,
        scale: float = 1.0,
    ) -> None:
        """Save iq samples to iqtar file."""
        self._write(file, datas, scale)

    @staticmethod
    def _write_date(file: typing.IO, data: ParentStorage):
        date = data.timestamp
        line = f"<DateTime>{date.isoformat()}</DateTime>\n"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_comment(file: typing.IO, data: Storage):
        line = (
            f"<Comment>{data.meta.get('comment', META_DEFAULTS['comment'])}"
            f"</Comment>\n"
        )
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_samples(file: typing.IO, data: Storage):
        line = f"<Samples>{len(data.data)}</Samples>\n"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_clock(file: typing.IO, data: Storage):
        clock = data.meta.get("clock")
        if not clock:
            raise ValueError("Clock is a mandatory parameter!")
        line = f'<Clock unit="Hz">{clock}</Clock>'
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_center_frequency(file: typing.IO, data: Storage):
        if data.meta.get("center_frequency", 0) != 0:
            file.write(
                (
                    f"<UserData><RohdeSchwarz>"
                    f"<SpectrumAnalyzer>"
                    f'<CenterFrequency unit="Hz">'
                    f'{data.meta.get("center_frequency")}'
                    f"</CenterFrequency>"
                    f"</SpectrumAnalyzer>"
                    f"</RohdeSchwarz></UserData>\n"
                ).encode("utf-8")
            )

    @staticmethod
    def _write_number_of_channels(file: typing.IO, data: ParentStorage):
        line = f"<NumberOfChannels>{data.number_of_storages()}</NumberOfChannels>\n"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_overhead(file: typing.IO):
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode("utf-8"))
        file.write(
            '<?xml-stylesheet type="text/xsl" '
            'href="open_IqTar_xml_file_in_web_browser.xslt"?>\n'.encode("utf-8")
        )
        file.write(
            "<RS_IQ_TAR_FileFormat "
            'fileFormatVersion="2" '
            "xsi:noNamespaceSchemaLocation="
            '"http://www.rohde-schwarz.com/file/RsIqTar.xsd" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            "\n".encode("utf-8")
        )
        file.write("<Name>Python iq.tar Writer</Name>\n".encode("utf-8"))

    @staticmethod
    def _write_datafilename(file: typing.IO, filenameiqw):
        line = "<DataFilename>" + filenameiqw + "</DataFilename>\n"
        file.write(line.encode("utf-8"))

    @staticmethod
    def _write_scaling_factor(file: typing.IO, data: Storage):
        line = (
            f'<ScalingFactor unit="V">'
            f"{data.meta.get('scalingfactor', 1)}</ScalingFactor>\n"
        )
        file.write(line.encode("utf-8"))
        pass

    def _write_xml(
        self,
        data: ParentStorage,
        filename_xml: typing.Union[str, Path],
        filename_iqw: str,
    ):
        with write_file_handle(filename_xml) as xml_file:
            self._write_overhead(xml_file)
            self._write_date(xml_file, data)
            self._write_comment(xml_file, data.storages[0])
            self._write_samples(xml_file, data.storages[0])
            self._write_clock(xml_file, data.storages[0])
            xml_file.write("<Format>complex</Format>\n".encode("utf-8"))
            xml_file.write("<DataType>float32</DataType>\n".encode("utf-8"))
            self._write_scaling_factor(xml_file, data.storages[0])
            self._write_datafilename(xml_file, filename_iqw)
            self._write_number_of_channels(xml_file, data)
            self._write_center_frequency(xml_file, data.storages[0])
            xml_file.write("</RS_IQ_TAR_FileFormat>\n".encode("utf-8"))

    @staticmethod
    def _write_data(
        binaryfile: typing.Union[str, Path], data: ParentStorage, scale: float = 1.0
    ):
        save_iqw = SaveIqw()
        save_iqw.save(binaryfile, data, scale)

    def _write(
        self,
        file: typing.Union[str, typing.IO, Path],
        data: ParentStorage,
        scale: float = 1.0,
    ):
        if isinstance(file, str):
            filename = Path(file).name
            path = Path(file).parent
            binaryfile = re.sub(
                "iq.tar", "complex.1ch.float32", filename, flags=re.IGNORECASE
            )
            xml_filename = re.sub("iq.tar", "xml", filename, flags=re.IGNORECASE)
        else:
            path = Path.home() / ".RsWaveform"
            binaryfile = "data.complex.1ch.float32"
            xml_filename = "data.xml"

        self._write_data(path / binaryfile, data, scale)
        self._write_xml(data, path / xml_filename, binaryfile)

        with write_file_handle_tar(file) as tar:
            tar.add(str(path / binaryfile), arcname=binaryfile)
            tar.add(str(path / xml_filename), arcname=xml_filename)
        os.remove(os.path.join(path, binaryfile))
        os.remove(os.path.join(path, xml_filename))
