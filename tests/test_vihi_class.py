from pathlib import Path
from types import SimpleNamespace

from lxml import etree

from SimbioReader.simbio_classes import Vihi
from SimbioReader.sr import SimbioReader

NAMESPACE = "http://psa.esa.int/psa/bc/mpo/sim/v1"
PREFIX = "bc_mpo_simbio-sys"


def test_vihi_maps_mission_xml_block():
    element = etree.fromstring(
        f"""
        <{PREFIX}:VIHI xmlns:{PREFIX}="{NAMESPACE}">
          <{PREFIX}:Frame_Parameters>
            <{PREFIX}:frame_summing>2</{PREFIX}:frame_summing>
            <{PREFIX}:external_repetition_time>0.5</{PREFIX}:external_repetition_time>
            <{PREFIX}:dark_acquisition_rate>0.25</{PREFIX}:dark_acquisition_rate>
          </{PREFIX}:Frame_Parameters>
          <{PREFIX}:start_pixel>3</{PREFIX}:start_pixel>
          <{PREFIX}:stop_pixel>4</{PREFIX}:stop_pixel>
          <{PREFIX}:Frame_Elaboration>
            <{PREFIX}:dark_subtraction>1</{PREFIX}:dark_subtraction>
            <{PREFIX}:spatial_binning>2</{PREFIX}:spatial_binning>
            <{PREFIX}:spectral_binning>3</{PREFIX}:spectral_binning>
            <{PREFIX}:binning_sequence>4</{PREFIX}:binning_sequence>
            <{PREFIX}:spectral_editing>5</{PREFIX}:spectral_editing>
          </{PREFIX}:Frame_Elaboration>
          <{PREFIX}:VIHI_HK>
            <{PREFIX}:temperature_fpa_package unit="K">10.1</{PREFIX}:temperature_fpa_package>
            <{PREFIX}:temperature_fpa1 unit="K">10.2</{PREFIX}:temperature_fpa1>
            <{PREFIX}:temperature_fpa2 unit="K">10.3</{PREFIX}:temperature_fpa2>
            <{PREFIX}:temperature_pe unit="K">10.4</{PREFIX}:temperature_pe>
            <{PREFIX}:temperature_spectrometer unit="K">10.5</{PREFIX}:temperature_spectrometer>
            <{PREFIX}:temperature_calib_unit unit="K">10.6</{PREFIX}:temperature_calib_unit>
            <{PREFIX}:tec_current unit="A">0.7</{PREFIX}:tec_current>
            <{PREFIX}:voltage_at_3.3v unit="V">3.3</{PREFIX}:voltage_at_3.3v>
          </{PREFIX}:VIHI_HK>
        </{PREFIX}:VIHI>
        """
    )

    vihi = Vihi.from_xml(element, {PREFIX: NAMESPACE})

    assert vihi.frame_parameters.frame_summing == 2
    assert vihi.frame_parameters.external_repetition_time == 0.5
    assert vihi.frame_parameters.dark_acquisition_rate == 0.25
    assert vihi.start_pixel == 3
    assert vihi.stop_pixel == 4
    assert vihi.frame_elaboration.dark_subtraction == 1
    assert vihi.frame_elaboration.spatial_binning == 2
    assert vihi.frame_elaboration.spectral_binning == 3
    assert vihi.frame_elaboration.binning_sequence == 4
    assert vihi.frame_elaboration.spectral_editing == 5
    assert vihi.housekeeping.temperature_fpa_package == 10.1
    assert vihi.housekeeping.temperature_fpa_package_unit == "K"
    assert vihi.housekeeping.temperature_fpa1 == 10.2
    assert vihi.housekeeping.temperature_fpa2 == 10.3
    assert vihi.housekeeping.temperature_pe == 10.4
    assert vihi.housekeeping.temperature_spectrometer == 10.5
    assert vihi.housekeeping.temperature_calib_unit == 10.6
    assert vihi.housekeeping.tec_current == 0.7
    assert vihi.housekeeping.tec_current_unit == "A"
    assert vihi.housekeeping.voltage_at_3_3v == 3.3
    assert vihi.housekeeping.voltage_at_3_3v_unit == "V"


def test_reader_populates_simbio_vihi(monkeypatch):
    label = Path(
        "tests/data/sim_raw_vihi_cruise_ico4b_2021-04-24_002/"
        "sim_raw_sc_vihi_internal_cruise_ico4b_2021-04-24_002__0_1.lblx"
    )

    monkeypatch.setattr(
        "SimbioReader.sr.pds4_tools.read",
        lambda **_: SimpleNamespace(structures=[]),
    )

    reader = SimbioReader(label, updateCheck=False)

    assert isinstance(reader.simbio.vihi, Vihi)
    assert reader.simbio.vihi.frame_parameters.frame_summing == 1
    assert reader.simbio.vihi.housekeeping.voltage_at_3_3v == 1
    vectors = reader.geometry.orbiter.vectors
    assert vectors.earth_to_spacecraft is not None
    assert vectors.earth_to_spacecraft.x == 0
    assert vectors.earth_to_spacecraft.x_unit == "km"
    assert vectors.earth_to_spacecraft.light_time_correction_applied == "None"
    assert vectors.spacecraft_to_target is not None
    assert vectors.sun_to_spacecraft is not None
    assert vectors.sun_to_target is not None
    assert vectors.spacecraft_relative_to_earth is not None
    assert vectors.spacecraft_relative_to_earth.x_unit == "km/s"
    assert vectors.spacecraft_relative_to_sun is not None
    assert vectors.spacecraft_relative_to_target is not None
