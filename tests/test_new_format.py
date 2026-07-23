from datetime import datetime
from pathlib import Path

import pytest

from SimbioReader.sr import INSTRUMENT, SimbioReader

PRODUCT_DIRECTORY = Path(
    "tests/data/sim_raw_stc_cruise_ico4b_2021-04-24_001"
)
LABEL = PRODUCT_DIRECTORY / (
    "sim_raw_sc_stc_winx_internal_cruise_ico4b_2021-04-24_001__0_1.lblx"
)
IMAGE = LABEL.with_suffix(".dat")


def _reader(path: Path = LABEL) -> SimbioReader:
    return SimbioReader(file_path=path, updateCheck=False)


def test_simbio_reader_accepts_data_file():
    reader = _reader(IMAGE)

    assert reader.lblx_file == LABEL


def test_simbio_reader_accepts_label():
    reader = _reader()

    assert reader.lblx_file == LABEL


def test_simbio_reader_rejects_nonexistent_label():
    with pytest.raises(FileNotFoundError, match="does not exists"):
        _reader(PRODUCT_DIRECTORY / "missing.lblx")


def test_simbio_reader_accepts_product_directory():
    reader = _reader(PRODUCT_DIRECTORY)

    assert reader.lblx_file == LABEL


def test_simbio_reader_reads_identification_metadata():
    reader = _reader()

    assert reader.channel is INSTRUMENT.STC
    assert reader.processing_level == "Raw"
    assert reader.version_id == "0.1"
    assert reader.information_model_version == "1.22.0.0"
    assert reader.lid.endswith(
        "sim_raw_sc_stc_winx_internal_cruise_ico4b_2021-04-24_001"
    )
    assert reader.title == (
        "BEPICOLOMBO MPO SIMBIO-SYS MERCURY ORBIT STC RAW SCIENCE DATA PRODUCT"
    )


def test_simbio_reader_reads_time_coordinates():
    coordinates = _reader().time_coordinates

    assert coordinates.start_utc == datetime(2019, 11, 27, 7, 3, 0, 103517)
    assert coordinates.end_utc == datetime(2019, 11, 27, 7, 3, 0, 103517)
    assert coordinates.start_scet == "1/0683974498:50090"
    assert coordinates.end_scet == "1/0683974498:50090"


def test_simbio_reader_reads_target():
    target = _reader().target

    assert target.name == "MERCURY"
    assert target.target_type == "Planet"
    assert str(target) == "Target(name=MERCURY, type=Planet)"


def test_simbio_reader_loads_product_structures():
    reader = _reader()

    assert len(reader.data_arrays) == 1
    assert reader.image_file.name == LABEL.with_suffix(".dat").name
    assert reader.csv_file.name == LABEL.with_suffix(".csv").name
