# Ignore patterns notes

This skill excludes paths using three layers:

## 1) Git-ignored content
- Tree output: `tree --gitignore`
- File enumeration: `git ls-files -co --exclude-standard`

This ensures `.gitignore` (and standard git ignore sources) are respected.

## 2) Built-in "generated/build/runtime artifacts" exclusions
These are excluded even if not in `.gitignore`:
- `.env`, `.env.*`
- `.venv`
- caches: `__pycache__`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`
- packaging: `*.egg-info`
- coverage: `.coverage`, `htmlcov`
- repo metadata: `.git`
- tool markers: `uv.lock`, `.python-version`, `.dockerignore`, `.gitignore`
- tests (requested exclusion): `tests/`
- output artifacts: `docs/artifacts/` (prevents self-inclusion recursion)

## 3) User-configurable excludes (persistent)
The generator reads an optional config file:
- `docs/artifacts/repo_codebook.config.json`

You can add more patterns under:
- `ignore_globs_extra`: list[str]

These extra patterns are applied to:
- code file enumeration and inclusion checks
- tree generation (best-effort; patterns are converted to a `tree -I` expression)

## Empty files
Empty (or whitespace-only) text files are:
- described as `skipped (empty file)`
- omitted from the code section
