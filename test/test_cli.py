from pathlib import Path
import sys
import types

from click.testing import CliRunner

if "mystrtools" not in sys.modules:
    mystrtools_stub = types.ModuleType("mystrtools")
    mystrtools_stub.convert_case = lambda value, *_args, **_kwargs: value
    sys.modules["mystrtools"] = mystrtools_stub

from SimbioReader.cli import cli


def test_cli_summarize_mode(monkeypatch, tmp_path: Path):
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

    runner = CliRunner()
    result = runner.invoke(cli, [str(input_file), "--summarize"])

    assert result.exit_code == 0
    assert FakeReader.summary_called is True
    assert FakeReader.show_called is False
    assert FakeReader.init_args[0] == input_file
    assert FakeReader.init_args[2] is False
    assert FakeReader.init_args[3] is False
    assert "SUMMARY OUTPUT" in FakeConsole.all_messages


def test_cli_show_mode_with_flags(monkeypatch, tmp_path: Path):
    class FakeConsole:
        all_messages: list[str] = []

        def print(self, message):
            self.all_messages.append(str(message))

    class FakeReader:
        init_args = None
        show_kwargs = None

        def __init__(self, file, console, debug, verbose):
            self.__class__.init_args = (file, console, debug, verbose)

        def summary(self):
            return "SUMMARY OUTPUT"

        def show(self, **kwargs):
            self.__class__.show_kwargs = kwargs
            return "SHOW OUTPUT"

    monkeypatch.setattr("SimbioReader.cli.Console", FakeConsole)
    monkeypatch.setattr("SimbioReader.cli.SimbioReader", FakeReader)

    input_file = tmp_path / "input.lblx"
    input_file.write_text("x", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            str(input_file),
            "--hk",
            "--detector",
            "--data-structure",
            "--all",
            "--filters",
            "--debug",
            "--verbose",
        ],
    )

    assert result.exit_code == 0
    assert FakeReader.init_args[0] == input_file
    assert FakeReader.init_args[2] is True
    assert FakeReader.init_args[3] is True
    assert FakeReader.show_kwargs == {
        "hk": True,
        "detector": True,
        "data_structure": True,
        "filters": True,
        "all_info": True,
    }
    assert "SHOW OUTPUT" in FakeConsole.all_messages


def test_cli_version_exits_before_reader_creation(monkeypatch, tmp_path: Path):
    class FakeConsole:
        all_messages: list[str] = []

        def print(self, message):
            self.all_messages.append(str(message))

    class FakeReader:
        init_count = 0

        def __init__(self, *args, **kwargs):
            self.__class__.init_count += 1

    monkeypatch.setattr("SimbioReader.cli.Console", FakeConsole)
    monkeypatch.setattr("SimbioReader.cli.SimbioReader", FakeReader)

    input_file = tmp_path / "input.lblx"
    input_file.write_text("x", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli, [str(input_file), "--version"])

    assert result.exit_code == 0
    assert FakeReader.init_count == 0
    assert any("SimbioReader version" in msg for msg in FakeConsole.all_messages)
    assert any("DataModel version" in msg for msg in FakeConsole.all_messages)


def test_cli_fails_with_missing_file():
    runner = CliRunner()
    result = runner.invoke(cli, ["/path/that/does/not/exist.lblx"])

    assert result.exit_code == 2
    assert isinstance(result.exception, SystemExit)
