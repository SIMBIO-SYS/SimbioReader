from dataclasses import dataclass
from enum import StrEnum
from typing import TypeVar

from .hric_class import Hric
from .stc_class import Stc
from .vihi_class import Vihi

InstrumentData = TypeVar("InstrumentData", Stc, Hric, Vihi)


class INSTRUMENT(StrEnum):
    STC = "STC"
    HRIC = "HRIC"
    VIHI = "VIHI"


instruments: list[INSTRUMENT] = [
    INSTRUMENT.STC,
    INSTRUMENT.VIHI,
    INSTRUMENT.HRIC,
]


@dataclass
class Compression:
    box: float
    rate: float
    ratio: int


@dataclass(slots=True, frozen=True)
class Simbio:
    channel: INSTRUMENT
    compression: Compression | None = None
    repetition_time: float | None = None

    _stc: Stc | None = None
    _vihi: Vihi | None = None
    _hric: Hric | None = None

    def __post_init__(self) -> None:
        try:
            channel = INSTRUMENT(self.channel)
        except ValueError as exc:
            valid = ", ".join(instrument.value for instrument in INSTRUMENT)
            raise ValueError(
                f"Unknown instrument {self.channel!r}. Expected one of: {valid}."
            ) from exc

        object.__setattr__(self, "channel", channel)

        instrument_data = {
            INSTRUMENT.STC: self._stc,
            INSTRUMENT.HRIC: self._hric,
            INSTRUMENT.VIHI: self._vihi,
        }
        if instrument_data[channel] is None:
            raise ValueError(f"Data for instrument {channel.value} are required.")

        unexpected = [
            instrument.value
            for instrument, value in instrument_data.items()
            if instrument is not channel and value is not None
        ]
        if unexpected:
            names = ", ".join(unexpected)
            raise ValueError(
                f"Data for {names} cannot be provided when the instrument is "
                f"{channel.value}."
            )

    def _get_instrument_data(
        self,
        expected: INSTRUMENT,
        value: InstrumentData | None,
    ) -> InstrumentData:
        if self.channel is not expected:
            raise AttributeError(
                f"The {expected.value} data are not available. "
                f"The current instrument is {self.channel.value}."
            )
        assert value is not None
        return value

    @property
    def stc(self) -> Stc:
        return self._get_instrument_data(INSTRUMENT.STC, self._stc)

    @property
    def hric(self) -> Hric:
        return self._get_instrument_data(INSTRUMENT.HRIC, self._hric)

    @property
    def vihi(self) -> Vihi:
        return self._get_instrument_data(INSTRUMENT.VIHI, self._vihi)
