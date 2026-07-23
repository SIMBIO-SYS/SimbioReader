import tomllib
from pathlib import Path


def test_simbio_reader_console_entrypoint_is_registered():
    configuration = tomllib.loads(
        Path("pyproject.toml").read_text(encoding="utf-8")
    )

    assert (
        configuration["project"]["scripts"]["simbioReader"]
        == "SimbioReader.cli:cli"
    )
