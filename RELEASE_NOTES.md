# SimbioReader 1.0.4

Release preparation: 20 October 2026. Previous version: `1.0.3`.

## Changes

- Advance the package version from `1.0.3` to `1.0.4` and synchronize workspace
  dependency versions in the lockfile.
- Refresh the README and changelog for this release.
- No new runtime fixes or calibration algorithms are included.

## Compatibility

The lockfile records the coordinated workspace package versions.
Existing editable sibling sources remain the local development configuration.
Published distributions must be made available before downstream installation
without these workspace sources.
Generated science and browse product VID remains `0.1`; actual raw and
calibration source LIDVIDs retain their original versions.

## Validation

- `uv lock --check --offline`: passed. External dependency pins are unchanged.
- Wheel and source distribution built with `uv build --offline`; wheel metadata
  and archived `pyproject.toml` versions were inspected and match this release.
- Tests executed in the existing project `.venv` using
  `.venv/bin/python -m pytest tests -q -o addopts=''`: 71 passed; 1 failed.
  `tests/test_db.py::test_none_subphase_sentinel_is_not_available` expects
  `SubPhase None not found`, but receives `Phase 'None' not found.` from the
  existing mission database lookup. Runtime source and tests are unchanged.
  This known failure remains open; this release is not fully validated.
- Tests use the existing environments; installation of the new wheels into
  a clean environment has not been verified.
- `git diff --check`: passed.
No new science products are generated in this release preparation. Scientific
accuracy, regenerated-product PDS4 validation, container execution, and remote
publication are outside the verification performed here.
