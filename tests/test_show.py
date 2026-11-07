import io
from dataclasses import replace
from pathlib import Path

import pytest
from loguru import logger

from rich.console import Console
from rich.panel import Panel

from SimbioReader.sr import SimbioReader
from SimbioReader.simbio_classes.reference_class import InternalReference


def _stc_reader(**kwargs) -> SimbioReader:
    label = Path(
        "tests/data/sim_raw_stc_cruise_ico4b_2021-04-24_001/"
        "sim_raw_sc_stc_winx_internal_cruise_ico4b_2021-04-24_001__0_1.lblx"
    )
    return SimbioReader(label, updateCheck=False, **kwargs)


def _render(renderable) -> str:
    stream = io.StringIO()
    console = Console(file=stream, width=180)
    console.print(renderable)
    return stream.getvalue()


def test_show_uses_current_models_and_requested_sections():
    reader = _stc_reader()

    assert reader.frame_binning is None

    panel = reader.show(
        hk=True,
        detector=True,
        data_structure=True,
        filters=True,
    )
    output = _render(panel)

    assert isinstance(panel, Panel)
    assert "SimbioReader Info" in output
    assert "STC Housekeeping" in output
    assert "CSV Housekeeping Data" in output
    assert "Acquisition Time Scet" in output
    assert "1/0683974498:50090" in output
    assert "0.1883 A" in output
    assert "3.254898 V" in output
    assert "Tec Current Unit" not in output
    assert "Pe Voltage Unit" not in output
    assert "STC Detector" in output
    assert "10.0 µm" in output
    assert "Pixel Height Unit" not in output
    assert "Pixel Width Unit" not in output
    assert "Imaging Detector" in output
    assert "Imaging Subframe" in output
    assert "2.31 °" in output
    assert "Line Fov Unit" not in output
    assert "Optical Filter" in output
    assert "0.0 nm" in output
    assert "Bandwidth Unit" not in output
    assert "Geometry" in output
    assert "Processing Level" in output
    assert "Mission Phase" in output


def test_show_no_symbols_preserves_unit_names():
    output = _render(
        _stc_reader().show(
            hk=True,
            detector=True,
            data_structure=True,
            no_symbols=True,
        )
    )

    assert "10.0 micrometer" in output
    assert "10.0 µm" not in output
    assert "2.31 deg" in output
    assert "2.31 °" not in output


@pytest.mark.parametrize("section", ["imaging", "display", "geometry"])
def test_show_individual_metadata_section(section):
    panel = _stc_reader().show(**{section: True})
    assert [child.title for child in panel.renderable.renderables] == [
        "SimbioReader Info", "Target Info", section.title(),
    ]


def test_show_all_includes_every_new_top_level_model():
    output = _render(_stc_reader().show(all_info=True))

    assert "SIMBIO" in output
    assert "Display" in output
    assert "Imaging" in output
    assert "Geometry" in output
    assert "References" in output
    assert "Internal references" in output
    assert "External references" in output
    assert "data_to_browse" in output
    assert "10.1007/s11214-020-00704-8" in output


def test_references_by_type_returns_matching_items():
    refs = _stc_reader().reference
    (browse,) = refs.by_type("data_to_browse")
    (document,) = refs.by_type("data_to_document")
    assert browse.identifier.endswith("::0.1")
    assert document.identifier.endswith(":document:eaicd")
    assert refs.by_type("unknown") == ()


def test_show_references_identifies_associated_products():
    reader = _stc_reader()
    associated = tuple(
        InternalReference("data_to_associate", lidvid_reference=f"urn:example:sim_raw_{kind}_vihi::0.1")
        for kind in ("hk", "geometry", "other")
    )
    object.__setattr__(reader, "reference", replace(reader.reference, internal_references=associated))
    output = _render(reader.show(references=True))
    assert "Internal references" in output
    assert "External references" in output
    assert "Housekeeping" in output
    assert "Geometry" in output
    assert "Associated product" in output


def test_geometry_groups_vertices_and_vectors():
    output = _render(_stc_reader().show(geometry=True))
    assert "Upper Left Corner" in output
    assert "Earth To Spacecraft" in output
    assert "Latitude" in output
    assert "Orbiter.Surface.Footprint Vertices" not in output


def test_imaging_groups_temperature_values_by_sensor():
    output = _render(_stc_reader().show(imaging=True))
    assert "Device Temperatures" in output
    assert "TemperatureFPA1 = 268.032773 K" in output


def test_verbose_reader_logs_csv_once():
    messages = []
    sink = logger.add(lambda message: messages.append(message.record["message"]))
    try:
        _stc_reader(verbose=1)
    finally:
        logger.remove(sink)
    assert sum("Identified a CSV file" in message for message in messages) == 1


def test_summary_uses_the_new_show_summary():
    panel = _stc_reader().summary()
    output = _render(panel)

    assert isinstance(panel, Panel)
    assert "SimbioReader Info" in output
    assert "Target Info" in output
