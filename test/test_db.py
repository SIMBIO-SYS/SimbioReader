from SimbioReader.simbioInfo import get_phase, get_subphase,get_subphases_by_phase,Test
from datetime import datetime

def test_pahse_get_by_name():
    test01 = get_phase(name='necp')
    assert test01.extended_name == 'Near-Earth Commissioning Phase'

def test_pase_date_type():
    test01 = get_phase(name='necp')
    assert isinstance(test01.start, datetime)
    


def test_pase_date_value():
    test01 = get_phase(name='necp')
    assert test01.start == datetime(2018, 12, 10, 0, 0, 0)
    
def test_pase_get_by_date_str():
    test01 = get_phase(dt='2018-12-11 00:00:00')
    assert test01.extended_name == 'Near-Earth Commissioning Phase'
    

def test_pase_get_by_date_datetime():
    test01 = get_phase(dt=datetime(2018,12,11,0,0,0))
    assert test01.extended_name == 'Near-Earth Commissioning Phase'
    
def test_subphase_name():
    test01 = get_subphase(name='necp')
    assert test01.extended_name == 'Near-Earth Commissioning Phase'
    

def test_subpase_date_type():
    test01 = get_subphase(name='ico1')
    assert isinstance(test01.start, datetime)
    

def test_subpase_date_value_fail():
    test01 = get_subphase(name='ico1')
    assert test01.start != datetime(2018, 12, 10, 0, 0, 0)
    
def test_get_subphases_by_phase():
    test01 = get_subphases_by_phase(phase_name='necp')
    assert test01 == 'necp'


def test_subpase_date_value():
    test01 = get_subphase(name='ico1')
    assert test01.start != datetime(2019, 6, 7, 10, 0, 0)


def test_subpase_get_by_date():
    test01 = get_subphase(dt='2019-06-07 10:30:00')
    assert test01.extended_name == 'Instrument Check-Out #1'
    
def test_get_test_by_name():
    test01 = Test('Hric performance',subphase='ico9')
    assert test01.name == 'HRIC Performance Test'


def test_search_by_name_in_subphase_with_one_test():
    result = Test('images', subphase='first_images')
    assert result.name == 'Mercury first images'
    assert result.subphase == 'first_images'


def test_get_tests_by_subphase_always_returns_list():
    from SimbioReader.simbioInfo import get_test_by_subphase

    assert get_test_by_subphase('FIRST_IMAGES') == ['first_images']
    assert get_test_by_subphase('unknown_subphase') == []


def test_timezone_queries_use_utc():
    from dateutil.parser import parse
    from SimbioReader.simbioInfo import Test, get_phase, get_subphase

    # Local date is the previous day; UTC falls within first_images.
    text = '2026-10-17T23:30:00-08:00'
    for value in (text, parse(text)):
        assert get_phase(dt=value).name == 'cruise'
        assert get_subphase(dt=value).name == 'first_images'
        assert Test(dt=value).subphase == 'first_images'
        assert Test.show_all(date=value).row_count == 1
