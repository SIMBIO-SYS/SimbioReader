# Repository instructions

- Before each commit, increment the package's development version unless the
  user explicitly instructs otherwise. Increment `.devN` if present. Starting
  from a stable version, advance the patch version and append `.dev1`
  (for example, `1.0.4` becomes `1.0.5.dev1`).
- Keep `pyproject.toml`, `uv.lock`, and current version references in the
  documentation aligned with the new version.
