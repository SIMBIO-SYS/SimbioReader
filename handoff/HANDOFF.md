# SimbioReader handoff

Updated: 2026-11-06

Current development version: `0.9.3`.

## Current role

SimbioReader parses SIMBIO-SYS PDS4 labels and their referenced image,
spectral, housekeeping, detector, and filter data. The `simbioReader` command
shows product information; `simbioInfo` exposes mission phases, subphases,
tests, and filter definitions.

## Current changes

- The package metadata targets Python 3.14 and version `0.9.3`.
- Image selection supports filters and VIHI segments; missing attributes raise AttributeError.
- Single-test subphase searches return lists, and date queries normalize aware inputs to UTC.
- VIHI segment details render without filters. Tests use local src and default uv groups.
- Filter output checks that the decoded product exposes a `filters` collection
  before iterating it. This keeps non-filter-bearing products readable.
- `FLUSSO_DATI.md` documents parsing, decoded objects, and output paths.

## Verification

Run the project checks from this repository:

```bash
uv run --locked python -m pytest
uv run --locked ruff check src test
```

Do not commit `.venv`, `__pycache__`, coverage output, or other generated
runtime artefacts.

## Reader corrections

- Decode UnsignedLSB2 as little-endian unsigned integers.
- Honor array offsets, axis sequence and index order; reject truncated arrays in every verbosity mode.
- Read the stop SCET from its own label field.
- Support VIHI segments in summaries and detector/data-structure output.
- Declare python-dateutil directly and align the lockfile and Python classifiers.

## Remaining limitations

XML parsing still requires the existing namespace prefixes. File areas, imaging and geometry are associated by position. Pyright reports existing typing issues that require a separate review. Preview labels have not been validated with a PDS4 validator in this change.

Next work: replace ambiguous tag-name lookups with full namespace-aware XPath
paths. Keep that parser change on the dedicated codex/full-label-xpath branch.

On this Mac, hidden flags are reapplied to .venv .pth files. A local
sitecustomize.py adds src to sys.path; it is not committed and disappears when
the environment is recreated. Use uv run --no-editable for a portable workaround.
