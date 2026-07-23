# SimbioReader handoff

Updated: `2026-07-23`

Branch: `Version_1.0`

Current development version: `1.0.0-dev.2`

## Current role

SimbioReader parses SIMBIO-SYS PDS4 labels and their referenced image,
spectral, and housekeeping structures. The current model hierarchy covers:

- SIMBIO general parameters and channel-specific STC, HRIC, and VIHI data;
- Display Settings, Imaging, Geometry, and Reference List;
- XML units, including geometric position and velocity vectors;
- product identification, time coordinates, target, and processing software.

The package exposes one console command, `simbioReader`.

## CLI

The CLI is organized into five subcommands:

- `version`: code and PSA/SIMBIO-SYS model compatibility;
- `about`: package and author metadata;
- `phases`: phases, subphases, and tests;
- `filters`: HRIC/STC filters with optional cross-instrument lookup;
- `info`: formatted information for one PDS4 product.

The standalone `simbioInfo` entry point and `infocli.py` were removed. Their
supported phase and filter workflows are available through `simbioReader`.

## Compatibility notes

- Python requirement: 3.14.
- PSA model: `1.22.0.0 (1M00_1500)`.
- SIMBIO-SYS model: `1.12.0.0 (1M00_1000)`.
- `savePreview()` remains as an obsolete stub: it prints a warning and raises
  `DeprecatedMethodError`.
- `get_segment_by_file()` returns data only for VIHI products containing more
  than one array.
- `integration_time` is intentionally not modeled because it is scheduled for
  removal from the source schema.

## Documentation

- `README.md` describes installation, Python API, CLI, and development checks.
- `CHANGELOG.md` contains the merged project history and the complete
  Version 1.0 branch changes.
- `docs/source` contains the Sphinx user guide, CLI guide, typed-model
  reference, mission-data reference, and class map.
- `docs/model-coverage-audit.md` records XML coverage with stable `SC-*` IDs.
- `docs/unused-code-audit.md` records legacy-code decisions with stable
  `UC-*` IDs.

## Verification

Run from the repository root:

```bash
uv run pytest
uv run ruff check src tests
uv run sphinx-build -W -M html docs/source docs/build
uv build
```

At this handoff, the focused test run reports 69 passing tests, Ruff reports
no lint errors, and the Sphinx HTML build succeeds with warnings treated as
errors. Generated caches, coverage output, and documentation builds must not
be committed.

The focused Pyright check for `sr.py` and `simbio_class.py` passes. The complete
package check reports four auxiliary-module errors tracked as `SIMCAL-017` in
`../SimCal/TODO.md`; they are documented but not corrected in this increment.

## Next work

- Remove the obsolete preview stubs in the next incompatible release.
- Revisit the remaining high-confidence module findings documented in the
  unused-code audit.
- Replace the SIMBIO-SYS compatibility value if the current coded identifier
  changes before the final 1.0 release.
