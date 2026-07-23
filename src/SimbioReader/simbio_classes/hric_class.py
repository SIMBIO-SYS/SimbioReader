from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.etree import _Element


@dataclass(slots=True, frozen=True)
class HricHousekeeping:
    tec_current: float
    tec_current_unit: str
    pe_voltage: float
    pe_voltage_unit: str


@dataclass(slots=True, frozen=True)
class HricDetector:
    description: str
    pixel_height: float
    pixel_height_unit: str
    pixel_width: float
    pixel_width_unit: str
    detector_type: int


@dataclass(slots=True, frozen=True)
class HricGeneralParameters:
    ifov: float
    ifov_unit: str
    focal_length: float
    focal_length_unit: str
    f_number: float
    detector: HricDetector
    filter_available: int


@dataclass(slots=True, frozen=True)
class Hric:
    windows_read: int
    window: int
    test_mode: int
    detector_clock: float
    detector_clock_unit: str
    housekeeping: HricHousekeeping
    general_parameters: HricGeneralParameters

    @classmethod
    def from_xml(
        cls,
        element: _Element,
        namespaces: dict[str, str],
    ) -> Hric:
        """Build the HRIC metadata model from the mission-area XML block."""

        prefix = "bc_mpo_simbio-sys"

        def text(path: str) -> str:
            value = element.xpath(f"string({path})", namespaces=namespaces)
            if not value:
                raise ValueError(f"Missing HRIC XML value at {path}")
            return str(value)

        def child(name: str) -> str:
            return text(f"{prefix}:{name}[1]")

        def unit(path: str) -> str:
            return text(f"{path}/@unit")

        housekeeping_path = f"{prefix}:HRIC_HK[1]"
        general_path = f"{prefix}:HRIC_General_Parameters[1]"
        detector_path = f"{general_path}/{prefix}:Detector[1]"

        housekeeping = HricHousekeeping(
            tec_current=float(
                text(f"{housekeeping_path}/{prefix}:tec_current[1]")
            ),
            tec_current_unit=unit(
                f"{housekeeping_path}/{prefix}:tec_current[1]"
            ),
            pe_voltage=float(
                text(f"{housekeeping_path}/{prefix}:pe_voltage[1]")
            ),
            pe_voltage_unit=unit(
                f"{housekeeping_path}/{prefix}:pe_voltage[1]"
            ),
        )
        detector = HricDetector(
            description=text(
                f"{detector_path}/{prefix}:detector_description[1]"
            ),
            pixel_height=float(
                text(
                    f"{detector_path}/{prefix}:Pixel_Height[1]/"
                    f"{prefix}:hk_length_param[1]"
                )
            ),
            pixel_height_unit=unit(
                f"{detector_path}/{prefix}:Pixel_Height[1]/"
                f"{prefix}:hk_length_param[1]"
            ),
            pixel_width=float(
                text(
                    f"{detector_path}/{prefix}:Pixel_Width[1]/"
                    f"{prefix}:hk_length_param[1]"
                )
            ),
            pixel_width_unit=unit(
                f"{detector_path}/{prefix}:Pixel_Width[1]/"
                f"{prefix}:hk_length_param[1]"
            ),
            detector_type=int(
                text(f"{detector_path}/{prefix}:detector_type[1]")
            ),
        )
        general_parameters = HricGeneralParameters(
            ifov=float(
                text(
                    f"{general_path}/{prefix}:Ifov[1]/"
                    f"{prefix}:hk_angle_param[1]"
                )
            ),
            ifov_unit=unit(
                f"{general_path}/{prefix}:Ifov[1]/"
                f"{prefix}:hk_angle_param[1]"
            ),
            focal_length=float(
                text(
                    f"{general_path}/{prefix}:Focal_Length[1]/"
                    f"{prefix}:hk_length_param[1]"
                )
            ),
            focal_length_unit=unit(
                f"{general_path}/{prefix}:Focal_Length[1]/"
                f"{prefix}:hk_length_param[1]"
            ),
            f_number=float(text(f"{general_path}/{prefix}:f_number[1]")),
            detector=detector,
            filter_available=int(
                text(f"{general_path}/{prefix}:filter_available[1]")
            ),
        )
        return cls(
            windows_read=int(child("windows_read")),
            window=int(child("window")),
            test_mode=int(child("test_mode")),
            detector_clock=float(child("detector_clock")),
            detector_clock_unit=unit(f"{prefix}:detector_clock[1]"),
            housekeeping=housekeeping,
            general_parameters=general_parameters,
        )
