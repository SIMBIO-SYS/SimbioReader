# SimbioReader handoff

Updated: 2026-07-22

Current development version: `0.6.8-dev.1`.

## Current role

SimbioReader parses SIMBIO-SYS PDS4 labels and their referenced image,
spectral, housekeeping, detector, and filter data. The `simbioReader` command
shows product information; `simbioInfo` exposes mission phases, subphases,
tests, and filter definitions.

## Current changes

- The package metadata now targets Python 3.14 and version `0.6.8-dev.1`.
- Filter output checks that the decoded product exposes a `filters` collection
  before iterating it. This keeps non-filter-bearing products readable.
- `FLUSSO_DATI.md` documents parsing, decoded objects, and output paths.

## Verification

Run the project checks from this repository:

```bash
python -m pytest
ruff check src tests
```

Do not commit `.venv`, `__pycache__`, coverage output, or other generated
runtime artefacts.

## Next work

- Add a regression test for filter output on a product without filter metadata.
- Confirm the Python classifiers match the Python 3.14-only requirement.
