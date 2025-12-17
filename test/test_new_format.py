from SimbioReader.sr import SimbioReader
from pathlib import Path
import pytest

def test_simbio_reader_init_file_dat():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_001/sim_cal_sc_stc_cruise_ico11_2024-04-08_001_winx_internal__0_1.dat")
    reader = SimbioReader(file_path=file_path)
    assert reader.pdsLabel.name == "sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx"

def test_simbio_reader_init_file_lblx():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_001/sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx")
    reader = SimbioReader(file_path=file_path)
    assert reader.pdsLabel.name == "sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx"

def test_simbio_reader_init_file_lblx_notexist():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_002/sim_cal_sc_stc_cruise_ico11_2024-04-08_003__0_1.lblx")
    with pytest.raises(FileNotFoundError,match="does not exist"):
        reader = SimbioReader(file_path=file_path)
    

def test_simbio_reader_init_folder():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_001")
    reader = SimbioReader(file_path=file_path)
    assert reader.pdsLabel.name == "sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx"

def test_simbio_reader_init_folder_multi_lblx():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_002")
    with pytest.raises(FileExistsError,match="Multiple .lblx files found in directory"):
        reader = SimbioReader(file_path=file_path)

def test_simbio_reader_init_channel():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_001/sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx")
    reader = SimbioReader(file_path=file_path)
    assert reader.channel == "stc"

def test_simbio_reader_init_unknown_channel():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_002/sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx")
    with pytest.raises(ValueError,match="Unknown channel 'unknown' found in label."):
        reader = SimbioReader(file_path=file_path)

def test_simbio_reader_init_level():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_001/sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx")
    reader = SimbioReader(file_path=file_path)
    assert reader.level == "calibrated"

def test_simbio_reader_init_lid():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_001/sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx")
    reader = SimbioReader(file_path=file_path)
    assert reader.lid == "urn:esa:psa:bc_mpo_simbio-sys:data_calibrated:sim_cal_sc_stc_cruise_ico11_2024-04-08_001"

def test_simbio_reader_init_version():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_001/sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx")
    reader = SimbioReader(file_path=file_path)
    assert reader.version == "0.1"

def test_simbio_reader_init_title():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_001/sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx")
    reader = SimbioReader(file_path=file_path)
    assert reader.title == "BEPICOLOMBO MPO SIMBIO-SYS MERCURY ORBIT STC CALIBRATED DATA PRODUCT"

def test_simbio_reader_init_lvid():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_001/sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx")
    reader = SimbioReader(file_path=file_path)
    assert reader.lvid == "urn:esa:psa:bc_mpo_simbio-sys:data_calibrated:sim_cal_sc_stc_cruise_ico11_2024-04-08_001::0.1"

def test_simbio_reader_init_datamodel_version():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_001/sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx")
    reader = SimbioReader(file_path=file_path)
    assert reader.dataModelVersion == "1.22.0.0"

def test_simbio_reader_init_start_stop_time():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_001/sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx")
    reader = SimbioReader(file_path=file_path)
    assert reader.startTime.isoformat() == "2024-04-08T01:05:18.055390"
    assert reader.stopTime.isoformat() == "2024-04-08T01:05:18.055390"

def test_simbio_reader_init_start_stop_scet():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_001/sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx")
    reader = SimbioReader(file_path=file_path)
    assert reader.start_scet == "1/0777258316:00904"
    assert reader.stop_scet == "1/0777258316:00904"

def test_simbio_reader_init_target():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_001/sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx")
    reader = SimbioReader(file_path=file_path)
    assert reader.target.name == "MERCURY"
    assert reader.target.target_type == "Planet"

def test_simbio_reader_init_target_str():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_001/sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx")
    reader = SimbioReader(file_path=file_path)
    assert str(reader.target) == "Target(name=MERCURY, type=Planet)"

        # temporary
def test_simbio_reader_init_files():
    file_path = Path("test/data/sim_cal_stc_cruise_ico11_2024-04-08_001/sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx")
    reader = SimbioReader(file_path=file_path)
    assert reader.data.items_number == 4 
    