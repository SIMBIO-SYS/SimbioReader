from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.etree import _Element


@dataclass(slots=True, frozen=True)
class InternalReference:
    reference_type: str
    lid_reference: str | None = None
    lidvid_reference: str | None = None

    @property
    def identifier(self) -> str:
        """Return the LIDVID when present, otherwise the LID."""
        identifier = self.lidvid_reference or self.lid_reference
        assert identifier is not None
        return identifier


@dataclass(slots=True, frozen=True)
class ExternalReference:
    doi: str
    reference_text: str


@dataclass(slots=True, frozen=True)
class Reference:
    internal_references: tuple[InternalReference, ...]
    external_references: tuple[ExternalReference, ...]

    @classmethod
    def from_xml(
        cls,
        element: _Element,
        namespaces: dict[str, str],
    ) -> Reference:
        """Build the product reference list from PDS XML."""

        def text(
            path: str,
            context: _Element,
            *,
            required: bool = True,
        ) -> str | None:
            value = str(
                context.xpath(f"string({path})", namespaces=namespaces)
            ).strip()
            if not value:
                if required:
                    raise ValueError(f"Missing reference XML value at {path}")
                return None
            return value

        internal_references = []
        for item in element.xpath(
            "pds:Internal_Reference",
            namespaces=namespaces,
        ):
            lid_reference = text(
                "pds:lid_reference[1]",
                item,
                required=False,
            )
            lidvid_reference = text(
                "pds:lidvid_reference[1]",
                item,
                required=False,
            )
            if lid_reference is None and lidvid_reference is None:
                raise ValueError(
                    "An internal reference requires a LID or LIDVID"
                )
            internal_references.append(
                InternalReference(
                    reference_type=str(
                        text("pds:reference_type[1]", item)
                    ),
                    lid_reference=lid_reference,
                    lidvid_reference=lidvid_reference,
                )
            )

        external_references = tuple(
            ExternalReference(
                doi=str(text("pds:doi[1]", item)),
                reference_text=str(
                    text("pds:reference_text[1]", item)
                ),
            )
            for item in element.xpath(
                "pds:External_Reference",
                namespaces=namespaces,
            )
        )
        return cls(
            internal_references=tuple(internal_references),
            external_references=external_references,
        )
