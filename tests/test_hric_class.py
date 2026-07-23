from pathlib import Path

from lxml import etree

from SimbioReader.simbio_classes import Hric
from SimbioReader.sr import SimbioReader

NAMESPACE = "http://psa.esa.int/psa/bc/mpo/sim/v1"
PREFIX = "bc_mpo_simbio-sys"


def test_hric_maps_mission_xml_block():
    element = etree.fromstring(
        f"""
        <{PREFIX}:HRIC xmlns:{PREFIX}="{NAMESPACE}">
          <{PREFIX}:windows_read>1</{PREFIX}:windows_read>
          <{PREFIX}:window>2</{PREFIX}:window>
          <{PREFIX}:test_mode>3</{PREFIX}:test_mode>
          <{PREFIX}:detector_clock unit="Hz">4.5</{PREFIX}:detector_clock>
          <{PREFIX}:HRIC_HK>
            <{PREFIX}:tec_current unit="A">0.188300</{PREFIX}:tec_current>
            <{PREFIX}:pe_voltage unit="V">3.254898</{PREFIX}:pe_voltage>
          </{PREFIX}:HRIC_HK>
          <{PREFIX}:HRIC_General_Parameters>
            <{PREFIX}:Ifov>
              <{PREFIX}:hk_angle_param unit="arcsec">1.1</{PREFIX}:hk_angle_param>
            </{PREFIX}:Ifov>
            <{PREFIX}:Focal_Length>
              <{PREFIX}:hk_length_param unit="m">2.1</{PREFIX}:hk_length_param>
            </{PREFIX}:Focal_Length>
            <{PREFIX}:f_number>3.1</{PREFIX}:f_number>
            <{PREFIX}:Detector>
              <{PREFIX}:detector_description>bla</{PREFIX}:detector_description>
              <{PREFIX}:Pixel_Height>
                <{PREFIX}:hk_length_param unit="micrometer">10</{PREFIX}:hk_length_param>
              </{PREFIX}:Pixel_Height>
              <{PREFIX}:Pixel_Width>
                <{PREFIX}:hk_length_param unit="micrometer">11</{PREFIX}:hk_length_param>
              </{PREFIX}:Pixel_Width>
              <{PREFIX}:detector_type>1</{PREFIX}:detector_type>
            </{PREFIX}:Detector>
            <{PREFIX}:filter_available>1</{PREFIX}:filter_available>
          </{PREFIX}:HRIC_General_Parameters>
        </{PREFIX}:HRIC>
        """
    )

    hric = Hric.from_xml(element, {PREFIX: NAMESPACE})

    assert hric.windows_read == 1
    assert hric.window == 2
    assert hric.test_mode == 3
    assert hric.detector_clock == 4.5
    assert hric.detector_clock_unit == "Hz"
    assert hric.housekeeping.tec_current == 0.1883
    assert hric.housekeeping.tec_current_unit == "A"
    assert hric.housekeeping.pe_voltage == 3.254898
    assert hric.general_parameters.ifov == 1.1
    assert hric.general_parameters.ifov_unit == "arcsec"
    assert hric.general_parameters.focal_length == 2.1
    assert hric.general_parameters.f_number == 3.1
    assert hric.general_parameters.detector.description == "bla"
    assert hric.general_parameters.detector.pixel_height == 10
    assert hric.general_parameters.detector.pixel_height_unit == "micrometer"
    assert hric.general_parameters.detector.pixel_width == 11
    assert hric.general_parameters.detector.detector_type == 1
    assert hric.general_parameters.filter_available == 1


def test_reader_populates_simbio_hric():
    label = Path(
        "tests/data/sim_raw_hric_cruise_ico4b_2021-04-24_001/"
        "sim_raw_sc_hric_winx_internal_cruise_ico4b_2021-04-24_001__0_1.lblx"
    )

    reader = SimbioReader(label, updateCheck=False)

    assert isinstance(reader.simbio.hric, Hric)
    assert reader.simbio.hric.windows_read == 1
    assert reader.simbio.hric.housekeeping.tec_current == 0.1883
