from datetime import datetime

from rich.table import Table

from SimbioReader.mission_phases import load_mission_phases
from SimbioReader.simbioInfo import Phase


def test_mission_phases_are_loaded_from_packaged_table():
    phases = load_mission_phases()

    assert len(phases) == 39
    assert phases[0].acronym == "testing"
    assert phases[0].start == datetime(2000, 1, 1)
    assert phases[-1].acronym == "msp"
    assert phases[-1].end is None


def test_mission_phase_end_is_next_record_start():
    phases = load_mission_phases()

    assert phases[0].end == phases[1].start


def test_phase_table_has_separate_name_and_acronym_columns():
    table = Phase.show_all()

    assert isinstance(table, Table)
    assert [column.header for column in table.columns] == [
        "Phase Name",
        "Acronym",
        "Start Time",
        "End Time",
    ]
