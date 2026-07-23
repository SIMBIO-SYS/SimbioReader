import sys
import types
from pathlib import Path

from click.testing import CliRunner

if "mystrtools" not in sys.modules:
    mystrtools_stub = types.ModuleType("mystrtools")
    mystrtools_stub.convert_case = lambda value, *_args, **_kwargs: value
    sys.modules["mystrtools"] = mystrtools_stub

from SimbioReader.cli import cli


def test_cli_exposes_expected_commands():
    assert set(cli.commands) == {
        "about",
        "filters",
        "info",
        "phases",
        "version",
    }


def test_cli_without_command_shows_help():
    result = CliRunner().invoke(cli)

    assert result.exit_code == 0
    assert "Commands" in result.output
    assert "info" in result.output


def test_cli_info_summarize_mode(monkeypatch, tmp_path: Path):
    class FakeConsole:
        all_messages: list[str] = []

        def print(self, message):
            self.all_messages.append(str(message))

    class FakeReader:
        init_args = None
        summary_called = False
        show_called = False

        def __init__(self, file, console, debug, verbose):
            self.__class__.init_args = (file, console, debug, verbose)

        def summary(self):
            self.__class__.summary_called = True
            return "SUMMARY OUTPUT"

        def show(self, **kwargs):
            self.__class__.show_called = True
            return "SHOW OUTPUT"

    monkeypatch.setattr("SimbioReader.cli.Console", FakeConsole)
    monkeypatch.setattr("SimbioReader.cli.SimbioReader", FakeReader)

    input_file = tmp_path / "input.lblx"
    input_file.write_text("x", encoding="utf-8")

    result = CliRunner().invoke(cli, ["info", str(input_file), "--summarize"])

    assert result.exit_code == 0
    assert FakeReader.summary_called is True
    assert FakeReader.show_called is False
    assert FakeReader.init_args[0] == input_file
    assert "SUMMARY OUTPUT" in FakeConsole.all_messages


def test_cli_info_show_mode_with_flags(monkeypatch, tmp_path: Path):
    class FakeConsole:
        all_messages: list[str] = []

        def print(self, message):
            self.all_messages.append(str(message))

    class FakeReader:
        init_args = None
        show_kwargs = None

        def __init__(self, file, console, debug, verbose):
            self.__class__.init_args = (file, console, debug, verbose)

        def show(self, **kwargs):
            self.__class__.show_kwargs = kwargs
            return "SHOW OUTPUT"

    monkeypatch.setattr("SimbioReader.cli.Console", FakeConsole)
    monkeypatch.setattr("SimbioReader.cli.SimbioReader", FakeReader)

    input_file = tmp_path / "input.lblx"
    input_file.write_text("x", encoding="utf-8")

    result = CliRunner().invoke(
        cli,
        [
            "info",
            str(input_file),
            "--hk",
            "--detector",
            "--data-structure",
            "--all",
            "--filters",
            "--debug",
            "--verbose",
            "--no-symbols",
        ],
    )

    assert result.exit_code == 0
    assert FakeReader.init_args[0] == input_file
    assert FakeReader.init_args[2:] == (True, True)
    assert FakeReader.show_kwargs == {
        "hk": True,
        "detector": True,
        "data_structure": True,
        "filters": True,
        "all_info": True,
        "no_symbols": True,
    }
    assert "SHOW OUTPUT" in FakeConsole.all_messages


def test_cli_version_does_not_require_product():
    result = CliRunner().invoke(cli, ["version"])

    assert result.exit_code == 0
    assert "SimbioReader version" in result.output
    assert "PDS Information Model" in result.output
    assert "1.22.0.0" in result.output
    assert "1M00_1500" in result.output
    assert "1.22.0.0 (1M00_1500)" in result.output
    assert "SIMBIO-SYS Data Model" in result.output
    assert "1.12.0.0 (1M00_1000)" in result.output


def test_cli_about_uses_package_metadata(monkeypatch):
    monkeypatch.setattr(
        "SimbioReader.cli.metadata",
        lambda _name: {
            "Name": "SimbioReader",
            "Version": "1.2.3",
            "Summary": "Reader description",
            "Author": "Romolo Politi",
            "Author-email": "author@example.org",
        },
    )

    result = CliRunner().invoke(cli, ["about"])

    assert result.exit_code == 0
    assert "Romolo Politi" in result.output
    assert "Reader description" in result.output


def test_cli_info_fails_with_missing_file():
    result = CliRunner().invoke(
        cli,
        ["info", "/path/that/does/not/exist.lblx"],
    )

    assert result.exit_code == 2
    assert isinstance(result.exception, SystemExit)


def test_cli_phases_and_filters_help():
    runner = CliRunner()

    assert runner.invoke(cli, ["phases", "--help"]).exit_code == 0
    assert runner.invoke(cli, ["filters", "--help"]).exit_code == 0


def test_cli_filter_name_does_not_require_channel():
    result = CliRunner().invoke(cli, ["filters", "--name", "pan-l"])

    assert result.exit_code == 0
    assert "PAN-L" in result.output


def test_cli_filter_name_is_case_insensitive():
    lower = CliRunner().invoke(cli, ["filters", "stc", "--name", "win-x"])
    upper = CliRunner().invoke(cli, ["filters", "STC", "--name", "WIN-X"])

    assert lower.exit_code == 0
    assert upper.exit_code == 0
    assert "WIN-X" in lower.output
    assert "WIN-X" in upper.output


def test_cli_filter_name_ignores_kebab_case():
    result = CliRunner().invoke(cli, ["filters", "--name", "pAnL"])

    assert result.exit_code == 0
    assert "PAN-L" in result.output


def test_cli_filters_without_arguments_shows_both_instruments():
    result = CliRunner().invoke(cli, ["filters"])

    assert result.exit_code == 0
    assert "HRIC" in result.output
    assert "STC" in result.output
