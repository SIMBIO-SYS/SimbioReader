from pathlib import Path

from SimbioReader.simbio_classes import Display, Geometry, Imaging, Reference
from SimbioReader.sr import SimbioReader


def test_reader_populates_discipline_area_models():
    label = Path(
        "tests/data/sim_raw_stc_cruise_ico4b_2021-04-24_001/"
        "sim_raw_sc_stc_winx_internal_cruise_ico4b_2021-04-24_001__0_1.lblx"
    )

    reader = SimbioReader(label, updateCheck=False)

    assert isinstance(reader.display, Display)
    assert reader.display.horizontal_display_axis == "Sample"
    assert reader.display.vertical_display_direction == "Bottom to Top"

    assert isinstance(reader.imaging, Imaging)
    assert reader.imaging.detector.first_line == 1
    assert reader.imaging.exposure_duration == 0
    assert reader.imaging.exposure_duration_unit == "ms"
    assert reader.imaging.optical_filter.name == "WIN-X"
    assert reader.imaging.optical_filter.bandwidth_unit == "nm"
    assert reader.imaging.subframe.samples == 64
    assert len(reader.imaging.device_temperatures) == 5
    assert reader.imaging.device_temperatures[0].device_name == "TemperatureFPA1"
    assert reader.imaging.device_temperatures[0].temperature_unit == "K"

    assert isinstance(reader.geometry, Geometry)
    assert reader.geometry.kernel_type == "mk"
    assert reader.geometry.image_display.central_body.name == "Mercury"
    assert reader.geometry.orbiter.identification.coordinate_system.coordinate_system_type == (
        "Planetocentric"
    )
    assert len(reader.geometry.orbiter.surface.footprint_vertices) == 4
    assert (
        reader.geometry.orbiter.surface.footprint_vertices[0].reference_pixel_location
        == "Upper Left Corner"
    )
    assert reader.geometry.orbiter.illumination.maximum_phase_angle == 0
    assert (
        reader.geometry.orbiter.illumination.maximum_phase_angle_unit == "deg"
    )
    assert (
        reader.geometry.orbiter.pixel_dimensions.horizontal_pixel_footprint_unit
        == "m"
    )
    assert (
        reader.geometry.orbiter.distances.spacecraft_target_center_distance_unit
        == "km"
    )
    assert reader.geometry.orbiter.vectors.earth_to_spacecraft is None
    assert reader.geometry.orbiter.vectors.spacecraft_to_target is None
    assert reader.geometry.orbiter.vectors.sun_to_spacecraft is None
    assert reader.geometry.orbiter.vectors.sun_to_target is None
    assert reader.geometry.orbiter.vectors.spacecraft_relative_to_earth is None
    assert reader.geometry.orbiter.vectors.spacecraft_relative_to_sun is None
    assert reader.geometry.orbiter.vectors.spacecraft_relative_to_target is None

    assert isinstance(reader.reference, Reference)
    assert len(reader.reference.internal_references) == 2
    assert reader.reference.internal_references[0].reference_type == "data_to_browse"
    assert reader.reference.internal_references[0].lidvid_reference == (
        "urn:esa:psa:bc_mpo_simbio-sys:browse_raw:"
        "sim_raw_sc_browse_stc_template::0.1"
    )
    assert reader.reference.internal_references[1].lid_reference == (
        "urn:esa:psa:bc_mpo_simbio-sys:document:eaicd"
    )
    assert len(reader.reference.external_references) == 1
    assert reader.reference.external_references[0].doi == (
        "10.1007/s11214-020-00704-8"
    )
