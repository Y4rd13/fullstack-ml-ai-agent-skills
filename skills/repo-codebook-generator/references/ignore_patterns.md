# Ignore patterns notes

This skill excludes paths using three layers:

## 1) Git-ignored content (source of truth)
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
The generator reads a persistent config file:
- `docs/artifacts/repo_codebook.config.json`

You can add more patterns under:
- `ignore_globs_extra`: `list[str]`

These extra patterns are applied to:
- code file enumeration and inclusion checks
- directory pruning during traversal (so excluded directories are not walked)
- tree generation (best-effort; patterns are converted to a `tree -I` expression)

### Directory patterns (important)
To ensure directory ignores work reliably (including pruning during traversal), directory-like entries are expanded internally:

- If you provide a directory path like:
  - `data`
  - `data/`
- The generator treats it as:
  - ignore the directory itself: `data`
  - ignore everything under it: `data/**`

- If you provide:
  - `data/**` or `data/*`
- The generator also ignores the base directory:
  - `data`
  - plus your provided glob

This guarantees:
- `os.walk` prunes excluded directories early
- file filtering excludes all descendants of the ignored directory

## Interactive ignore preflight (before generation)
By default (when running in a TTY), the generator runs an interactive preflight **before** writing `docs/artifacts/repo_codebook.md`:

1) It prints an "Ignore Summary" showing:
   - Layer 1: `.gitignore` / git excludes behavior
   - Layer 2: built-in excludes (components + globs)
   - Layer 3: current `ignore_globs_extra` from config

2) It asks (enumerated choices):
   1. Add more files/folders/patterns to ignore (persistent)
   2. Continue without changes

3) If you choose **1**, you can enter multiple paths/patterns (one per line; empty line ends).
   - Directories are canonicalized and saved as `dir/**`
   - Globs (e.g. `*.pdf`) are kept as-is
   - Each entry is persisted into `docs/artifacts/repo_codebook.config.json`

4) It prints what was added and shows the full updated ignore list.

5) It then asks again:
   1. Generate `repo_codebook.md` now
   2. Add more ignores (loops back)

### Non-interactive mode
To skip prompts (useful for CI), run with:
- `--non-interactive`

## Empty files
Empty (or whitespace-only) text files are:
- described as `skipped (empty file)`
- omitted from the code section when `skip_empty_files=true`