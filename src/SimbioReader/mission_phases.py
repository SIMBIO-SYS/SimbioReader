from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from dateutil.parser import parse


@dataclass(frozen=True, slots=True)
class MissionPhase:
    start: datetime
    end: datetime | None
    acronym: str
    name: str
    folder: str


@lru_cache(maxsize=1)
def load_mission_phases() -> tuple[MissionPhase, ...]:
    """Load mission-phase intervals from the packaged PSA table."""
    table_path = Path(__file__).parent / "mission_phases" / "mission_phases.tab"
    records = []
    with table_path.open(encoding="utf-8", newline="") as stream:
        for row in csv.reader(stream):
            if not row or row[0].lstrip().startswith("#"):
                continue
            start, acronym, name, folder = (value.strip() for value in row)
            records.append(
                (
                    parse(start, ignoretz=True),
                    acronym,
                    name,
                    folder,
                )
            )

    records.sort(key=lambda record: record[0])
    return tuple(
        MissionPhase(
            start=start,
            end=records[index + 1][0] if index + 1 < len(records) else None,
            acronym=acronym,
            name=name,
            folder=folder,
        )
        for index, (start, acronym, name, folder) in enumerate(records)
    )
