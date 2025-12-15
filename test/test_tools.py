from SimbioReader.tools import gen_filename, new_lvid
from pathlib import Path 

def test_filename():
    old_name=Path("sim_raw_sc_hric_cust0_internal_cruise_cruise_2021-04-24_001__0_1.dat")
    new_name=gen_filename(old_name)
    assert new_name == "sim_browse_raw_sc_hric_cust0_internal_cruise_cruise_2021-04-24_001__0_1"

def test_filename_cal():
    old_name=Path("sim_cal_sc_hric_cust0_internal_cruise_cruise_2021-04-24_001__0_1.dat")
    new_name=gen_filename(old_name)
    assert new_name == "sim_browse_cal_sc_hric_cust0_internal_cruise_cruise_2021-04-24_001__0_1"

def test_lvid():
    oldLVID="urn:esa:psa:bc_mpo_sim:data_raw:sim_raw_sc_hric_template::0.1"
    file_name=Path("sim_cal_sc_hric_cruise_cruise_2021-04-24_001_cust0_internal__0_1.dat")
    file_version='0.1'
    newLVID=new_lvid(oldLVID, file_name, file_version)
    assert newLVID == "urn:esa:psa:bc_mpo_sim:data_calibrated:sim_cal_sc_hric_cruise_cruise_2021-04-24_001_cust0_internal::0.1"