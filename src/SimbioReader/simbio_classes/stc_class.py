from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.etree import _Element


@dataclass(slots=True, frozen=True)
class StcHousekeeping:
    tec_current: float
    tec_current_unit: str
    pe_voltage: float
    pe_voltage_unit: str


@dataclass(slots=True, frozen=True)
class StcDetector:
    description: str
    pixel_height: float
    pixel_height_unit: str
    pixel_width: float
    pixel_width_unit: str
    detector_type: int


@dataclass(slots=True, frozen=True)
class StcGeneralParameters:
    channel_1_fov: float
    channel_1_fov_unit: str
    channel_2_fov: float
    channel_2_fov_unit: str
    channel_1_focal_length: float
    channel_1_focal_length_unit: str
    channel_2_focal_length: float
    channel_2_focal_length_unit: str
    channel_1_f_number: float
    channel_2_f_number: float
    detector: StcDetector
    filter_available: int


@dataclass(slots=True, frozen=True)
class Stc:
    windows_read: int
    window: int
    test_mode: int
    detector_clock: float
    detector_clock_unit: str
    housekeeping: StcHousekeeping
    general_parameters: StcGeneralParameters

    @classmethod
    def from_xml(
        cls,
        element: _Element,
        namespaces: dict[str, str],
    ) -> Stc:
        """Build the STC metadata model from the mission-area XML block."""

        prefix = "bc_mpo_simbio-sys"

        def text(path: str) -> str:
            value = element.xpath(f"string({path})", namespaces=namespaces)
            if not value:
                raise ValueError(f"Missing STC XML value at {path}")
            return str(value)

        def child(name: str) -> str:
            return text(f"{prefix}:{name}[1]")

        def unit(path: str) -> str:
            return text(f"{path}/@unit")

        housekeeping_path = f"{prefix}:STC_HK[1]"
        general_path = f"{prefix}:STC_General_Parameters[1]"
        detector_path = f"{general_path}/{prefix}:Detector[1]"

        housekeeping = StcHousekeeping(
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
        detector = StcDetector(
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
        general_parameters = StcGeneralParameters(
            channel_1_fov=float(
                text(
                    f"{general_path}/{prefix}:Channel_1_fov[1]/"
                    f"{prefix}:hk_angle_param[1]"
                )
            ),
            channel_1_fov_unit=unit(
                f"{general_path}/{prefix}:Channel_1_fov[1]/"
                f"{prefix}:hk_angle_param[1]"
            ),
            channel_2_fov=float(
                text(
                    f"{general_path}/{prefix}:Channel_2_fov[1]/"
                    f"{prefix}:hk_angle_param[1]"
                )
            ),
            channel_2_fov_unit=unit(
                f"{general_path}/{prefix}:Channel_2_fov[1]/"
                f"{prefix}:hk_angle_param[1]"
            ),
            channel_1_focal_length=float(
                text(
                    f"{general_path}/{prefix}:Channel_1_focal_length[1]/"
                    f"{prefix}:hk_length_param[1]"
                )
            ),
            channel_1_focal_length_unit=unit(
                f"{general_path}/{prefix}:Channel_1_focal_length[1]/"
                f"{prefix}:hk_length_param[1]"
            ),
            channel_2_focal_length=float(
                text(
                    f"{general_path}/{prefix}:Channel_2_focal_length[1]/"
                    f"{prefix}:hk_length_param[1]"
                )
            ),
            channel_2_focal_length_unit=unit(
                f"{general_path}/{prefix}:Channel_2_focal_length[1]/"
                f"{prefix}:hk_length_param[1]"
            ),
            channel_1_f_number=float(
                text(f"{general_path}/{prefix}:channel_1_f_number[1]")
            ),
            channel_2_f_number=float(
                text(f"{general_path}/{prefix}:channel_2_f_number[1]")
            ),
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
