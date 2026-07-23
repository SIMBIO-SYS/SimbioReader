from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.etree import _Element


@dataclass(slots=True, frozen=True)
class VihiFrameParameters:
    frame_summing: int
    external_repetition_time: float
    dark_acquisition_rate: float


@dataclass(slots=True, frozen=True)
class VihiFrameElaboration:
    dark_subtraction: int
    spatial_binning: int
    spectral_binning: int
    binning_sequence: int
    spectral_editing: int


@dataclass(slots=True, frozen=True)
class VihiHousekeeping:
    temperature_fpa_package: float
    temperature_fpa_package_unit: str
    temperature_fpa1: float
    temperature_fpa1_unit: str
    temperature_fpa2: float
    temperature_fpa2_unit: str
    temperature_pe: float
    temperature_pe_unit: str
    temperature_spectrometer: float
    temperature_spectrometer_unit: str
    temperature_calib_unit: float
    temperature_calib_unit_measurement_unit: str
    tec_current: float
    tec_current_unit: str
    voltage_at_3_3v: float
    voltage_at_3_3v_unit: str


@dataclass(slots=True, frozen=True)
class Vihi:
    frame_parameters: VihiFrameParameters
    start_pixel: int
    stop_pixel: int
    frame_elaboration: VihiFrameElaboration
    housekeeping: VihiHousekeeping

    @classmethod
    def from_xml(
        cls,
        element: _Element,
        namespaces: dict[str, str],
    ) -> Vihi:
        """Build the VIHI metadata model from the mission-area XML block."""

        prefix = "bc_mpo_simbio-sys"

        def text(path: str) -> str:
            value = element.xpath(f"string({path})", namespaces=namespaces)
            if not value:
                raise ValueError(f"Missing VIHI XML value at {path}")
            return str(value)

        def child(name: str) -> str:
            return text(f"{prefix}:{name}[1]")

        def unit(path: str) -> str:
            return text(f"{path}/@unit")

        frame_parameters_path = f"{prefix}:Frame_Parameters[1]"
        frame_elaboration_path = f"{prefix}:Frame_Elaboration[1]"
        housekeeping_path = f"{prefix}:VIHI_HK[1]"

        frame_parameters = VihiFrameParameters(
            frame_summing=int(
                text(f"{frame_parameters_path}/{prefix}:frame_summing[1]")
            ),
            external_repetition_time=float(
                text(
                    f"{frame_parameters_path}/"
                    f"{prefix}:external_repetition_time[1]"
                )
            ),
            dark_acquisition_rate=float(
                text(
                    f"{frame_parameters_path}/"
                    f"{prefix}:dark_acquisition_rate[1]"
                )
            ),
        )
        frame_elaboration = VihiFrameElaboration(
            dark_subtraction=int(
                text(
                    f"{frame_elaboration_path}/"
                    f"{prefix}:dark_subtraction[1]"
                )
            ),
            spatial_binning=int(
                text(
                    f"{frame_elaboration_path}/{prefix}:spatial_binning[1]"
                )
            ),
            spectral_binning=int(
                text(
                    f"{frame_elaboration_path}/{prefix}:spectral_binning[1]"
                )
            ),
            binning_sequence=int(
                text(
                    f"{frame_elaboration_path}/{prefix}:binning_sequence[1]"
                )
            ),
            spectral_editing=int(
                text(
                    f"{frame_elaboration_path}/{prefix}:spectral_editing[1]"
                )
            ),
        )
        housekeeping = VihiHousekeeping(
            temperature_fpa_package=float(
                text(
                    f"{housekeeping_path}/"
                    f"{prefix}:temperature_fpa_package[1]"
                )
            ),
            temperature_fpa_package_unit=unit(
                f"{housekeeping_path}/"
                f"{prefix}:temperature_fpa_package[1]"
            ),
            temperature_fpa1=float(
                text(f"{housekeeping_path}/{prefix}:temperature_fpa1[1]")
            ),
            temperature_fpa1_unit=unit(
                f"{housekeeping_path}/{prefix}:temperature_fpa1[1]"
            ),
            temperature_fpa2=float(
                text(f"{housekeeping_path}/{prefix}:temperature_fpa2[1]")
            ),
            temperature_fpa2_unit=unit(
                f"{housekeeping_path}/{prefix}:temperature_fpa2[1]"
            ),
            temperature_pe=float(
                text(f"{housekeeping_path}/{prefix}:temperature_pe[1]")
            ),
            temperature_pe_unit=unit(
                f"{housekeeping_path}/{prefix}:temperature_pe[1]"
            ),
            temperature_spectrometer=float(
                text(
                    f"{housekeeping_path}/"
                    f"{prefix}:temperature_spectrometer[1]"
                )
            ),
            temperature_spectrometer_unit=unit(
                f"{housekeeping_path}/"
                f"{prefix}:temperature_spectrometer[1]"
            ),
            temperature_calib_unit=float(
                text(
                    f"{housekeeping_path}/"
                    f"{prefix}:temperature_calib_unit[1]"
                )
            ),
            temperature_calib_unit_measurement_unit=unit(
                f"{housekeeping_path}/"
                f"{prefix}:temperature_calib_unit[1]"
            ),
            tec_current=float(
                text(f"{housekeeping_path}/{prefix}:tec_current[1]")
            ),
            tec_current_unit=unit(
                f"{housekeeping_path}/{prefix}:tec_current[1]"
            ),
            voltage_at_3_3v=float(
                text(f"{housekeeping_path}/{prefix}:voltage_at_3.3v[1]")
            ),
            voltage_at_3_3v_unit=unit(
                f"{housekeeping_path}/{prefix}:voltage_at_3.3v[1]"
            ),
        )
        return cls(
            frame_parameters=frame_parameters,
            start_pixel=int(child("start_pixel")),
            stop_pixel=int(child("stop_pixel")),
            frame_elaboration=frame_elaboration,
            housekeeping=housekeeping,
        )
