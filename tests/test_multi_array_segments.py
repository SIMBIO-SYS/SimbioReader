from pathlib import Path
from types import SimpleNamespace

from SimbioReader.simbio_classes import INSTRUMENT
from SimbioReader.sr import SimbioReader


def _reader(channel, *file_names):
    reader = object.__new__(SimbioReader)
    object.__setattr__(reader, "channel", channel)
    object.__setattr__(
        reader,
        "data_arrays",
        tuple(
            SimpleNamespace(parent_filename=Path(file_name))
            for file_name in file_names
        ),
    )
    return reader


def test_get_segment_by_file_returns_matching_vihi_multi_array():
    reader = _reader(INSTRUMENT.VIHI, "segment_1.qub", "segment_2.qub")

    segment = reader.get_segment_by_file(Path("/data/segment_2.qub"))

    assert segment is reader.data_arrays[1]


def test_get_segment_by_file_is_disabled_for_single_vihi_array():
    reader = _reader(INSTRUMENT.VIHI, "segment_1.qub")

    assert reader.get_segment_by_file("segment_1.qub") is None


def test_get_segment_by_file_is_disabled_for_other_channels():
    reader = _reader(INSTRUMENT.HRIC, "segment_1.dat", "segment_2.dat")

    assert reader.get_segment_by_file("segment_1.dat") is None
