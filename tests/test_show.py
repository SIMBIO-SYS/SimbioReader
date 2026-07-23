import io
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from SimbioReader.sr import SimbioReader


def _stc_reader() -> SimbioReader:
    label = Path(
        "tests/data/sim_raw_stc_cruise_ico4b_2021-04-24_001/"
        "sim_raw_sc_stc_winx_internal_cruise_ico4b_2021-04-24_001__0_1.lblx"
    )
    return SimbioReader(label, updateCheck=False)


def _render(renderable) -> str:
    stream = io.StringIO()
    console = Console(file=stream, width=180)
    console.print(renderable)
    return stream.getvalue()


def test_show_uses_current_models_and_requested_sections():
    reader = _stc_reader()

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


def test_show_all_includes_every_new_top_level_model():
    output = _render(_stc_reader().show(all_info=True))

    assert "SIMBIO" in output
    assert "Display" in output
    assert "Imaging" in output
    assert "Geometry" in output
    assert "References" in output


def test_geometry_uses_leaf_names_in_two_columns():
    reader = _stc_reader()
    panel = reader._model_panel(
        "Geometry",
        reader.geometry,
        leaf_names=True,
        two_columns=True,
    )
    output = _render(panel)

    assert len(panel.renderable.columns) == 6
    assert "Latitude" in output
    assert "Orbiter.Surface.Footprint Vertices" not in output


def test_summary_uses_the_new_show_summary():
    panel = _stc_reader().summary()
    output = _render(panel)

    assert isinstance(panel, Panel)
    assert "SimbioReader Info" in output
    assert "Target Info" in output
