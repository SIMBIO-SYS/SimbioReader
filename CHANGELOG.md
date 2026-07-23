# Changelog

All notable changes to SimbioReader are documented in this file.

## Unreleased — Version 1.0.0 development branch

Changes since the branch diverged from `main` at commit `90819e5`.

### Added

- Typed XML models for SIMBIO general parameters and the STC, HRIC, and VIHI
  instrument branches.
- Typed models for Display Settings, Imaging, Geometry, and Reference List.
- Geometry position and velocity vectors, with optional `None` values when a
  label does not provide the vector block.
- Preservation of XML measurement units throughout instrument, detector,
  imaging, geometry, and vector models.
- Mission phase loading from the packaged `mission_phases.tab` database.
- Model-coverage and unused-code audit documents with stable issue IDs.
- Tests for instrument mapping, discipline-area models, geometry vectors,
  current display output, CLI behavior, obsolete methods, and VIHI multi-array
  segment selection.
- Ruff configuration and uv-managed development and documentation dependency
  groups.

### Changed

- Advanced the package version to `1.0.0-dev.1` and migrated the build backend
  from Poetry to uv.
- Advanced the package version to `1.0.0-dev.2`.
- Unified command-line functionality under `simbioReader` with the
  `version`, `about`, `phases`, `filters`, and `info` subcommands.
- `version` now displays code version and PSA/SIMBIO-SYS data-model
  compatibility in `version (coded)` form.
- `phases` now reads the packaged mission-phase table and displays phase name
  and acronym in separate columns.
- `filters` now accepts an optional channel, searches both HRIC and STC when
  omitted, displays every filter when no selector is supplied, and normalizes
  case and hyphens.
- `SimbioReader.show()` and `summary()` now use the typed model hierarchy.
  Housekeeping and detector values are rendered as `parameter = value unit`;
  CSV housekeeping is included with `--hk`; geometry uses leaf names in a
  compact two-column layout.
- Units are displayed as symbols by default, with `--no-symbols` retaining the
  source label spelling.
- `get_segment_by_file()` now operates only on VIHI products containing more
  than one data array.
- Tests and fixtures moved from `test` to `tests`, and project configuration
  now targets the new location.
- CI workflows now use uv and Python 3.14.

### Deprecated

- `SimbioReader.savePreview()` now prints an obsolescence warning and raises
  `DeprecatedMethodError`. It is scheduled for removal in a future release.

### Removed

- Legacy `Detector` and `HK` wrappers identified as `UC-SR-001` and
  `UC-SR-002`; current typed detector and housekeeping models replace them.
- Legacy `Data` identified as `UC-SR-004`, including its obsolete
  `savePreview()` method (`UC-SR-007`).
- The now-unused `pandas` runtime dependency.
- The now-unused `mystrtools` runtime dependency.
- The unused `SimbioReader.tools` module and its XML/LID helper functions,
  which no production code called.
- The separate `simbioInfo` console entry point and obsolete `infocli.py`
  module; their supported functionality is available through `simbioReader`.
- Legacy `SimbioObject`, preview implementation, filter accessors, image
  helper, and unreachable preview code identified by the unused-code audit.
- The unused `SizeError` exception.
- Obsolete calibrated fixtures and tests tied to the previous reader
  structure.
- Poetry lock data and the standalone documentation requirements file.

### Fixed

- Corrected mission phase names and boundaries using the dates in the phase
  database.
- Guarded filter rendering for products without filter metadata.

### Documentation

- Record the four remaining package-wide Pyright findings as `SIMCAL-017` in
  the central Calibrator issue register; this versioning pass does not alter
  the affected auxiliary code.
- Updated tests to use current model attributes and fixture paths.
- Removed static-analysis errors and rich-click markup deprecation warnings.

## 0.7.0

- Added `get_filters`.

## 0.6.7

- Fixed file-name version handling.

## 0.6.5

- Updated dependencies.

## 0.6.4

- Removed unused functions and adopted standard-library replacements.
- Improved package tests.

## 0.6.1

- Removed the legacy log call.
- Fixed raw/calibrated product differences.
- Fixed browse-label generation.

## 0.6.0 — 2025-12-10

- Introduced the one-product-for-all-filters data format.

## 0.6.0-dev.2

- Fixed project metadata.

## 0.5.11 — 2025-12-03

- Fixed calibrated-product `lvid_reference` generation for JIRA ticket 157,
  item 11.

## 0.5.10 — 2025-10-22

- Fixed LVID generation.

## 0.5.9 — 2025-09-26

- Fixed `savePreview` for calibrated files.

## 0.5.8 — 2025-09-18

- Fixed preview bugs and changed template copying to template renaming.

## 0.5.7 — 2025-09-18

- `savePreview` returns the browse-product LVID when given a PDS4 template.

## 0.5.6 — 2025-09-17

- Fixed bugs.

## 0.5.5 — 2025-09-17

- Fixed the LID generator.

## 0.5.4 — 2025-09-17

- Fixed data-model keys for mission phases.

## 0.5.2 — 2025-09-16

- Fixed label reading.

## 0.5.0 — 2025-09-15

- Added PDS browse-label generation.

## 0.2.2 — 2024-09-02

- Updated the filter database.

## 0.2.1 — 2024-09-02

- Fixed filter definitions.

## 0.2.0

- Added `__main__.py`.
- Added the original `simbioInfo` phase, subphase, test, and filter CLI.
- Added Sphinx documentation.

## 0.1.8

- Fixed bugs.

## 0.1.7

- Added ICO 11 information.

## 0.1.6

- Enabled update checks.
- Added ICO 10 information.

## 0.1.4

- Disabled automatic updates.

## 0.1.2

- Updated mission phases.

## 0.1.1

- Fixed requirements.

## 0.1.0

- First release.
