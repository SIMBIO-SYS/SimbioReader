import pytest
from pathlib import Path
from SimbioReader.__main__ import SimbioReader
from rich.console import Console

def test_simbio_reader_initialization():
    file_path = Path("test_data/test_file.dat")
    console = Console()
    reader = SimbioReader(file_path, console=console, debug=True, verbose=True)
    assert reader.fileName == file_path.absolute()
    assert reader.channel in ["STC", "HRIC", "VIHI"]

def test_simbio_reader_read():
    file_path = Path("test_data/test_file.dat")
    console = Console()
    reader = SimbioReader(file_path, console=console, debug=True, verbose=True)
    reader.read()
    assert reader.title is not None
    assert reader.dataModelVersion is not None
    assert reader.startTime is not None
    assert reader.stopTime is not None
    assert reader.level is not None
    assert reader.tarName is not None
    assert reader.tarType is not None
    assert reader.startScet is not None
    assert reader.stopScet is not None
    assert reader.phaseName is not None
    assert reader.exposure is not None
    assert reader.firstLine is not None
    assert reader.firstSample is not None
    assert reader.lines is not None
    assert reader.samples is not None
    assert reader.lineFov is not None
    assert reader.sampleFov is not None

def test_simbio_reader_show():
    file_path = Path("test_data/test_file.dat")
    console = Console()
    reader = SimbioReader(file_path, console=console, debug=True, verbose=True)
    columns = reader.Show(hk=True, detector=True, data_structure=True, all_info=True)
    assert columns is not None

def test_simbio_reader_save_preview():
    file_path = Path("test_data/test_file.dat")
    console = Console()
    reader = SimbioReader(file_path, console=console, debug=True, verbose=True)
    reader.savePreview(img_type='png', quality=100, outFolder=Path("test_data/output"))
    assert (Path("test_data/output") / f"{file_path.stem}.png").exists()

def test_simbio_reader_image():
    file_path = Path("test_data/test_file.dat")
    console = Console()
    reader = SimbioReader(file_path, console=console, debug=True, verbose=True)
    image = reader.image()
    assert image is not None