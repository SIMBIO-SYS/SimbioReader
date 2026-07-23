from pathlib import Path

from lxml import etree

from SimbioReader.simbio_classes import Stc
from SimbioReader.sr import SimbioReader

NAMESPACE = "http://psa.esa.int/psa/bc/mpo/sim/v1"
PREFIX = "bc_mpo_simbio-sys"


def test_stc_maps_mission_xml_block():
    element = etree.fromstring(
        f"""
        <{PREFIX}:STC xmlns:{PREFIX}="{NAMESPACE}">
          <{PREFIX}:windows_read>1</{PREFIX}:windows_read>
          <{PREFIX}:window>2</{PREFIX}:window>
          <{PREFIX}:test_mode>3</{PREFIX}:test_mode>
          <{PREFIX}:detector_clock unit="Hz">4.5</{PREFIX}:detector_clock>
          <{PREFIX}:STC_HK>
            <{PREFIX}:tec_current unit="A">0.188300</{PREFIX}:tec_current>
            <{PREFIX}:pe_voltage unit="V">3.254898</{PREFIX}:pe_voltage>
          </{PREFIX}:STC_HK>
          <{PREFIX}:STC_General_Parameters>
            <{PREFIX}:Channel_1_fov>
              <{PREFIX}:hk_angle_param unit="arcmin">1.1</{PREFIX}:hk_angle_param>
            </{PREFIX}:Channel_1_fov>
            <{PREFIX}:Channel_2_fov>
              <{PREFIX}:hk_angle_param unit="arcmin">1.2</{PREFIX}:hk_angle_param>
            </{PREFIX}:Channel_2_fov>
            <{PREFIX}:Channel_1_focal_length>
              <{PREFIX}:hk_length_param unit="m">2.1</{PREFIX}:hk_length_param>
            </{PREFIX}:Channel_1_focal_length>
            <{PREFIX}:Channel_2_focal_length>
              <{PREFIX}:hk_length_param unit="m">2.2</{PREFIX}:hk_length_param>
            </{PREFIX}:Channel_2_focal_length>
            <{PREFIX}:channel_1_f_number>3.1</{PREFIX}:channel_1_f_number>
            <{PREFIX}:channel_2_f_number>3.2</{PREFIX}:channel_2_f_number>
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
          </{PREFIX}:STC_General_Parameters>
        </{PREFIX}:STC>
        """
    )

    stc = Stc.from_xml(element, {PREFIX: NAMESPACE})

    assert stc.windows_read == 1
    assert stc.window == 2
    assert stc.test_mode == 3
    assert stc.detector_clock == 4.5
    assert stc.detector_clock_unit == "Hz"
    assert stc.housekeeping.tec_current == 0.1883
    assert stc.housekeeping.tec_current_unit == "A"
    assert stc.housekeeping.pe_voltage == 3.254898
    assert stc.housekeeping.pe_voltage_unit == "V"
    assert stc.general_parameters.channel_1_fov == 1.1
    assert stc.general_parameters.channel_1_fov_unit == "arcmin"
    assert stc.general_parameters.channel_2_fov == 1.2
    assert stc.general_parameters.channel_1_focal_length == 2.1
    assert stc.general_parameters.channel_2_focal_length == 2.2
    assert stc.general_parameters.channel_1_f_number == 3.1
    assert stc.general_parameters.channel_2_f_number == 3.2
    assert stc.general_parameters.detector.description == "bla"
    assert stc.general_parameters.detector.pixel_height == 10
    assert stc.general_parameters.detector.pixel_height_unit == "micrometer"
    assert stc.general_parameters.detector.pixel_width == 11
    assert stc.general_parameters.detector.detector_type == 1
    assert stc.general_parameters.filter_available == 1


def test_reader_populates_simbio_stc():
    label = Path(
        "tests/data/sim_raw_stc_cruise_ico4b_2021-04-24_001/"
        "sim_raw_sc_stc_winx_internal_cruise_ico4b_2021-04-24_001__0_1.lblx"
    )

    reader = SimbioReader(label, updateCheck=False)

    assert isinstance(reader.simbio.stc, Stc)
    assert reader.simbio.stc.windows_read == 1
    assert reader.simbio.stc.housekeeping.tec_current == 0.1883
