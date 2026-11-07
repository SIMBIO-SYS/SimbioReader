# Repository instructions

- Before each commit, increment the package's development version unless the
  user explicitly instructs otherwise. Increment `.devN` if present. Starting
  from a stable version, advance the patch version and append `.dev1`
  (for example, `1.0.4` becomes `1.0.5.dev1`).
- Keep `pyproject.toml`, `uv.lock`, and current version references in the
  documentation aligned with the new version.

## Updating the remote repository

When the user asks to update the remote repository, follow these steps in order:

1. Increment the development version unless the user instructs otherwise.
2. Update the tests to cover the changes and run them.
3. Update the relevant documentation.
4. Commit the changes with a message that explains what changed.
5. Push the commit to the remote branch.
