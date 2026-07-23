from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.etree import _Element


@dataclass(slots=True, frozen=True)
class Display:
    local_identifier_reference: str
    local_reference_type: str
    horizontal_display_axis: str
    horizontal_display_direction: str
    vertical_display_axis: str
    vertical_display_direction: str

    @classmethod
    def from_xml(
        cls,
        element: _Element,
        namespaces: dict[str, str],
    ) -> Display:
        """Build display settings from the PDS discipline-area XML."""

        def text(path: str) -> str:
            value = str(
                element.xpath(f"string({path})", namespaces=namespaces)
            ).strip()
            if not value:
                raise ValueError(f"Missing display XML value at {path}")
            return value

        reference = "pds:Local_Internal_Reference[1]"
        direction = "disp:Display_Direction[1]"
        return cls(
            local_identifier_reference=text(
                f"{reference}/pds:local_identifier_reference[1]"
            ),
            local_reference_type=text(
                f"{reference}/pds:local_reference_type[1]"
            ),
            horizontal_display_axis=text(
                f"{direction}/disp:horizontal_display_axis[1]"
            ),
            horizontal_display_direction=text(
                f"{direction}/disp:horizontal_display_direction[1]"
            ),
            vertical_display_axis=text(
                f"{direction}/disp:vertical_display_axis[1]"
            ),
            vertical_display_direction=text(
                f"{direction}/disp:vertical_display_direction[1]"
            ),
        )
