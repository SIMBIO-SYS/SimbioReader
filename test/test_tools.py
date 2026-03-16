import xml.dom.minidom as md
from pathlib import Path

import pytest

from SimbioReader.tools import (
    gen_filename,
    getElement,
    getFromXml,
    getValue,
    lvidUpdate,
    new_lvid,
    updateXML,
)

def test_filename():
    old_name = Path("sim_raw_sc_hric_cust0_internal_cruise_cruise_2021-04-24_001__0_1.dat")
    new_name = gen_filename(old_name)
    assert isinstance(new_name, Path)
    assert new_name == Path("sim_browse_raw_sc_hric_cust0_internal_cruise_cruise_2021-04-24_001__0_1")

def test_filename_cal():
    old_name = Path("sim_cal_sc_hric_cust0_internal_cruise_cruise_2021-04-24_001__0_1.dat")
    new_name = gen_filename(old_name)
    assert isinstance(new_name, Path)
    assert new_name == Path("sim_browse_cal_sc_hric_cust0_internal_cruise_cruise_2021-04-24_001__0_1")

def test_lvid():
    oldLVID="urn:esa:psa:bc_mpo_sim:data_raw:sim_raw_sc_hric_template::0.1"
    file_name=Path("sim_cal_sc_hric_cruise_cruise_2021-04-24_001_cust0_internal__0_1.dat")
    file_version='0.1'
    newLVID=new_lvid(oldLVID, file_name, file_version)
    assert newLVID == "urn:esa:psa:bc_mpo_sim:data_calibrated:sim_cal_sc_hric_cruise_cruise_2021-04-24_001_cust0_internal::0.1"


def test_get_value_returns_text():
    xml_string = "<root><name>John Doe</name><age>30</age></root>"
    doc = md.parseString(xml_string)
    root = doc.documentElement

    assert getValue(root, "name") == "John Doe"
    assert getValue(root, "age") == "30"


def test_get_value_raises_if_tag_not_found():
    xml_string = "<root><name>John Doe</name></root>"
    doc = md.parseString(xml_string)
    root = doc.documentElement

    with pytest.raises(IndexError, match="Tag 'age' not found"):
        getValue(root, "age")


def test_get_value_raises_if_tag_has_no_child_nodes():
    xml_string = "<root><empty/></root>"
    doc = md.parseString(xml_string)
    root = doc.documentElement

    with pytest.raises(AttributeError, match="Tag 'empty' has no child nodes"):
        getValue(root, "empty")


def test_get_element_returns_element_by_index():
    xml_string = "<root><item>a</item><item>b</item></root>"
    doc = md.parseString(xml_string)
    root = doc.documentElement

    first = getElement(root, "item")
    second = getElement(root, "item", 1)

    assert first.firstChild.nodeValue == "a"
    assert second.firstChild.nodeValue == "b"


def test_get_element_raises_if_tag_not_found():
    xml_string = "<root><item>a</item></root>"
    doc = md.parseString(xml_string)
    root = doc.documentElement

    with pytest.raises(IndexError, match="Tag 'missing' not found"):
        getElement(root, "missing")


def test_get_element_raises_if_index_out_of_range():
    xml_string = "<root><item>a</item></root>"
    doc = md.parseString(xml_string)
    root = doc.documentElement

    with pytest.raises(IndexError, match="index 1 is out of range"):
        getElement(root, "item", 1)


def test_get_element_raises_if_index_is_negative():
    xml_string = "<root><item>a</item></root>"
    doc = md.parseString(xml_string)
    root = doc.documentElement

    with pytest.raises(IndexError, match="Element index cannot be negative"):
        getElement(root, "item", -1)


def test_update_xml_updates_first_matching_tag():
    xml_string = "<root><version_id>0.1</version_id><version_id>0.2</version_id></root>"
    doc = md.parseString(xml_string)
    root = doc.documentElement

    updateXML(root, "version_id", "0.3")

    versions = root.getElementsByTagName("version_id")
    assert versions[0].firstChild.nodeValue == "0.3"
    assert versions[1].firstChild.nodeValue == "0.2"


def test_update_xml_updates_element_by_index():
    xml_string = "<root><version_id>0.1</version_id><version_id>0.2</version_id></root>"
    doc = md.parseString(xml_string)
    root = doc.documentElement

    updateXML(root, "version_id", "0.4", idx=1)

    versions = root.getElementsByTagName("version_id")
    assert versions[0].firstChild.nodeValue == "0.1"
    assert versions[1].firstChild.nodeValue == "0.4"


def test_update_xml_raises_if_tag_not_found():
    xml_string = "<root><name>SIMBIO</name></root>"
    doc = md.parseString(xml_string)
    root = doc.documentElement

    with pytest.raises(IndexError):
        updateXML(root, "version_id", "0.3")


def test_update_xml_raises_if_target_has_no_child_nodes():
    xml_string = "<root><version_id/></root>"
    doc = md.parseString(xml_string)
    root = doc.documentElement

    with pytest.raises(AttributeError):
        updateXML(root, "version_id", "0.3")


def test_lvid_update_updates_lidvid_reference_and_returns_value():
    xml_string = (
        "<root><lidvid_reference>"
        "urn:esa:psa:bc_mpo_sim:data_raw:sim_raw_sc_hric_template::0.1"
        "</lidvid_reference></root>"
    )
    doc = md.parseString(xml_string)
    root = doc.documentElement
    file_name = Path(
        "sim_cal_sc_hric_cruise_cruise_2021-04-24_001_cust0_internal__0_1.dat"
    )

    new_lvid_value = lvidUpdate(root, file_name, "0.2")

    assert (
        new_lvid_value
        == "urn:esa:psa:bc_mpo_sim:data_calibrated:sim_cal_sc_hric_cruise_cruise_2021-04-24_001_cust0_internal::0.2"
    )
    assert getFromXml(root, "lidvid_reference") == new_lvid_value
