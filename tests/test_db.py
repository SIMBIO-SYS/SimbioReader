from datetime import datetime

import pytest

from SimbioReader.simbioInfo import Test as MissionTest
from SimbioReader.simbioInfo import (
    get_phase,
    get_subphase,
    get_subphases_by_phase,
)


def test_pahse_get_by_name():
    test01 = get_phase(name="necp")
    assert test01.extended_name == "Near-Earth Commissioning Phase"


def test_pase_date_type():
    test01 = get_phase(name="necp")
    assert isinstance(test01.start, datetime)


def test_pase_date_value():
    test01 = get_phase(name="necp")
    assert test01.start == datetime(2018, 10, 20, 1, 45, 0)


def test_pase_get_by_date_str():
    test01 = get_phase(dt="2018-11-11 00:00:00")
    assert test01.extended_name == "Near-Earth Commissioning Phase"


def test_pase_get_by_date_datetime():
    test01 = get_phase(dt=datetime(2018, 11, 11, 0, 0, 0))
    assert test01.extended_name == "Near-Earth Commissioning Phase"


def test_subphase_name():
    test01 = get_subphase(name="necp")
    assert test01.extended_name == "Near-Earth Commissioning Phase"


def test_subpase_date_type():
    test01 = get_subphase(name="ico1")
    assert isinstance(test01.start, datetime)


def test_subpase_date_value_fail():
    test01 = get_subphase(name="ico1")
    assert test01.start != datetime(2018, 12, 10, 0, 0, 0)


def test_get_subphases_by_phase():
    test01 = get_subphases_by_phase(phase_name="necp")
    assert test01 == "necp"


def test_subpase_date_value():
    test01 = get_subphase(name="ico1")
    assert test01.start != datetime(2019, 6, 7, 10, 0, 0)


def test_subpase_get_by_date():
    test01 = get_subphase(dt="2019-06-07 10:30:00")
    assert test01.extended_name == "Instrument Check-Out #1"


def test_subphase_outside_known_intervals_is_not_available():
    with pytest.raises(ValueError, match="No subphase found"):
        get_subphase(dt="2025-01-01 00:00:00")


def test_none_subphase_sentinel_is_not_available():
    with pytest.raises(ValueError, match="SubPhase None not found"):
        get_subphase(name="None")


def test_get_test_by_name():
    test01 = MissionTest("Hric performance", subphase="ico9")
    assert test01.name == "HRIC Performance Test"
