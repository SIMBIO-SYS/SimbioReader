from pathlib import Path

import pytest
from rich.console import Console

from SimbioReader.exceptions import DeprecatedMethodError
from SimbioReader.sr import SimbioReader


def test_save_preview_reports_obsolescence_and_raises():
    reader = object.__new__(SimbioReader)
    console = Console(record=True)
    object.__setattr__(reader, "console", console)

    with pytest.raises(
        DeprecatedMethodError,
        match=r"savePreview\(\) is obsolete",
    ):
        reader.savePreview(
            img_type="png",
            quality=100,
            outFolder=Path("/tmp"),
        )

    assert "will be removed in a future" in console.export_text()
