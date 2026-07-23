from dataclasses import FrozenInstanceError

import pytest

from SimbioReader.sr import INSTRUMENT, Simbio, SimbioReader, instruments


def test_instruments_are_string_enum_values():
    assert instruments == [INSTRUMENT.STC, INSTRUMENT.VIHI, INSTRUMENT.HRIC]
    assert INSTRUMENT.STC == "STC"


def test_simbio_exposes_only_selected_instrument_data():
    simbio = Simbio(
        channel=INSTRUMENT.STC,
        _stc="stc-data",
    )

    assert simbio.stc == "stc-data"
    with pytest.raises(AttributeError, match="VIHI data are not available"):
        _ = simbio.vihi


def test_simbio_normalizes_string_channel():
    simbio = Simbio(
        channel="VIHI",
        _vihi="vihi-data",
    )

    assert simbio.channel is INSTRUMENT.VIHI
    assert simbio.vihi == "vihi-data"


def test_simbio_rejects_unknown_instrument():
    with pytest.raises(ValueError, match="Unknown instrument"):
        Simbio(
            channel="INVALID",
            _stc="stc-data",
        )


def test_simbio_requires_selected_instrument_data():
    with pytest.raises(ValueError, match="Data for instrument HRIC are required"):
        Simbio(channel=INSTRUMENT.HRIC)


def test_simbio_rejects_data_for_other_instruments():
    with pytest.raises(ValueError, match="Data for VIHI cannot be provided"):
        Simbio(
            channel=INSTRUMENT.STC,
            _stc="stc-data",
            _vihi="vihi-data",
        )


def test_simbio_is_immutable():
    simbio = Simbio(
        channel=INSTRUMENT.HRIC,
        _hric="hric-data",
    )

    with pytest.raises(FrozenInstanceError):
        simbio._hric = "other-data"


def test_reader_rejects_unknown_legacy_attribute():
    reader = object.__new__(SimbioReader)

    with pytest.raises(AttributeError, match="startTime"):
        _ = reader.startTime


def _reader_for_representation():
    reader = object.__new__(SimbioReader)
    object.__setattr__(reader, "channel", INSTRUMENT.STC)
    object.__setattr__(reader, "processing_level", "Raw")
    object.__setattr__(reader, "lid", "urn:test:stc")
    object.__setattr__(reader, "version_id", "1.0")
    return reader


def test_reader_string_uses_current_public_attributes():
    reader = _reader_for_representation()

    assert str(reader) == (
        "SimbioReader(channel=STC, processing_level=Raw, "
        "lvid=urn:test:stc::1.0)"
    )


def test_reader_repr_is_unambiguous():
    reader = _reader_for_representation()

    assert repr(reader) == (
        "SimbioReader(channel='STC', processing_level='Raw', "
        "lid='urn:test:stc', version_id='1.0')"
    )
