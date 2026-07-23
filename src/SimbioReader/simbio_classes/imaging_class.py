from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.etree import _Element


@dataclass(slots=True, frozen=True)
class ImagingDetector:
    first_line: int
    first_sample: int
    lines: int


@dataclass(slots=True, frozen=True)
class OpticalFilter:
    name: str
    identifier: str
    bandwidth: float
    bandwidth_unit: str
    center_wavelength: float
    center_wavelength_unit: str
    comment: str


@dataclass(slots=True, frozen=True)
class Subframe:
    first_line: int
    first_sample: int
    lines: int
    samples: int
    line_fov: float
    line_fov_unit: str
    sample_fov: float
    sample_fov_unit: str
    name: str
    description: str


@dataclass(slots=True, frozen=True)
class DeviceTemperature:
    device_name: str
    temperature: float
    temperature_unit: str


@dataclass(slots=True, frozen=True)
class Imaging:
    local_identifier_reference: str
    local_reference_type: str
    detector: ImagingDetector
    exposure_duration: float
    exposure_duration_unit: str
    optical_filter: OpticalFilter | None
    subframe: Subframe
    device_temperatures: tuple[DeviceTemperature, ...]

    @classmethod
    def from_xml(
        cls,
        element: _Element,
        namespaces: dict[str, str],
    ) -> Imaging:
        """Build imaging metadata from the PDS discipline-area XML."""

        def text(path: str, context: _Element = element) -> str:
            value = str(
                context.xpath(f"string({path})", namespaces=namespaces)
            ).strip()
            if not value:
                raise ValueError(f"Missing imaging XML value at {path}")
            return value

        def unit(path: str, context: _Element = element) -> str:
            return text(f"{path}/@unit", context)

        reference = "pds:Local_Internal_Reference[1]"
        detector_path = "img:Detector[1]"
        filter_path = "img:Optical_Filter[1]"
        subframe_path = "img:Subframe[1]"
        temperature_elements = element.xpath(
            "img:Instrument_State[1]/img:Device_Temperatures[1]/"
            "img:Device_Temperature",
            namespaces=namespaces,
        )
        filter_elements = element.xpath(
            filter_path,
            namespaces=namespaces,
        )
        optical_filter = None
        if filter_elements:
            optical_filter = OpticalFilter(
                name=text(f"{filter_path}/img:filter_name[1]"),
                identifier=text(f"{filter_path}/img:filter_id[1]"),
                bandwidth=float(text(f"{filter_path}/img:bandwidth[1]")),
                bandwidth_unit=unit(
                    f"{filter_path}/img:bandwidth[1]"
                ),
                center_wavelength=float(
                    text(
                        f"{filter_path}/img:center_filter_wavelength[1]"
                    )
                ),
                center_wavelength_unit=unit(
                    f"{filter_path}/img:center_filter_wavelength[1]"
                ),
                comment=text(f"{filter_path}/img:comment[1]"),
            )

        return cls(
            local_identifier_reference=text(
                f"{reference}/pds:local_identifier_reference[1]"
            ),
            local_reference_type=text(
                f"{reference}/pds:local_reference_type[1]"
            ),
            detector=ImagingDetector(
                first_line=int(
                    text(f"{detector_path}/img:first_line[1]")
                ),
                first_sample=int(
                    text(f"{detector_path}/img:first_sample[1]")
                ),
                lines=int(text(f"{detector_path}/img:lines[1]")),
            ),
            exposure_duration=float(
                text("img:Exposure[1]/img:exposure_duration[1]")
            ),
            exposure_duration_unit=unit(
                "img:Exposure[1]/img:exposure_duration[1]"
            ),
            optical_filter=optical_filter,
            subframe=Subframe(
                first_line=int(
                    text(f"{subframe_path}/img:first_line[1]")
                ),
                first_sample=int(
                    text(f"{subframe_path}/img:first_sample[1]")
                ),
                lines=int(text(f"{subframe_path}/img:lines[1]")),
                samples=int(text(f"{subframe_path}/img:samples[1]")),
                line_fov=float(text(f"{subframe_path}/img:line_fov[1]")),
                line_fov_unit=unit(
                    f"{subframe_path}/img:line_fov[1]"
                ),
                sample_fov=float(
                    text(f"{subframe_path}/img:sample_fov[1]")
                ),
                sample_fov_unit=unit(
                    f"{subframe_path}/img:sample_fov[1]"
                ),
                name=text(f"{subframe_path}/img:name[1]"),
                description=text(
                    f"{subframe_path}/img:description[1]"
                ),
            ),
            device_temperatures=tuple(
                DeviceTemperature(
                    device_name=text("img:device_name[1]", item),
                    temperature=float(
                        text("img:temperature_value[1]", item)
                    ),
                    temperature_unit=unit(
                        "img:temperature_value[1]",
                        item,
                    ),
                )
                for item in temperature_elements
            ),
        )
