from RsWaveform import __version__
from RsWaveform.__main__ import main


def test_main_prints_version(capsys):
    try:
        main(["--version"])
    except SystemExit:
        pass
    assert capsys.readouterr().out == f"{__version__}\n"
