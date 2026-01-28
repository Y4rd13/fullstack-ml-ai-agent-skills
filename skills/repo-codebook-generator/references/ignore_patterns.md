# Ignore patterns notes

This skill excludes two categories of paths:

## 1) Git-ignored content
- The tree output uses: `tree --gitignore`
- The file enumeration uses: `git ls-files -co --exclude-standard`

This ensures files ignored by `.gitignore` and other standard ignore sources are excluded.

## 2) Additional "generated/build/runtime artifacts" noise
Beyond `.gitignore`, the skill applies an extra exclude list (via `tree -I` and post-filtering):
- .env files: `.env`, `.env.*`
- Virtual envs: `.venv`
- Caches: `__pycache__`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`
- Packaging artifacts: `*.egg-info`
- Coverage artifacts: `.coverage`, `htmlcov`
- Repo metadata: `.git`
- Lockfiles and tool markers: `uv.lock`, `.python-version`
- Ignore specs themselves: `.gitignore`, `.dockerignore`
- Tests (requested exclusion): `tests/`
- Generated artifact output: `docs/artifacts/` (prevents self-inclusion recursion)

## Empty files
- Empty (or whitespace-only) text files are noted as `skipped (empty file)` and are not included in the code section.

## Tree fallback
- If `tree` is not available, the generator falls back to a `find`-based listing (best-effort).
- In fallback mode, `.gitignore` semantics may not be fully replicated; the file list still relies on Git when available.

Notes:
- The exact patterns are defined in:
  - `scripts/get_tree.sh` (tree ignore pattern)
  - `scripts/generate_repo_codebook.py` (EXCLUDE_GLOBS / exclude logic)
- If you want to include tests, remove `tests` from both ignore lists.
