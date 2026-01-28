---
name: repo-codebook-generator
description: Generates a single repository "codebook" artifact (structure + one-line file descriptions + full source) respecting .gitignore and excluding non-source artifacts.
license: MIT
---

This skill is a boundary/artifact generator. It produces a single, versioned repository snapshot document.

## Output artifacts
- Codebook: `docs/artifacts/repo_codebook.md`
- Persistent config (state): `docs/artifacts/repo_codebook.config.json`
- Rationale: these are generated documentation artifacts, not production source.

## Non-negotiables
- Do NOT include secrets or env files (e.g., `.env`, `.env.*`).
- Exclude generated/build/runtime artifacts and other non-source noise.
- File descriptions must be 1 line max, objective, and accurate.
- Skip empty/whitespace-only files in the code section.
- If you add comments to code while generating/fixing: ONLY essential comments, in ENGLISH.

## Persistent config (stateful)
The generator maintains a stateful config file so users can add more ignores without editing `.gitignore` or the skill code.

- Path: `docs/artifacts/repo_codebook.config.json`
- Behavior: created automatically on first run if missing.

### Config fields
- `ignore_globs_extra`: additional glob patterns to exclude (e.g., `data/**`, `*.pdf`).
- `skip_empty_files`: if true, empty/whitespace-only files are omitted from the code section.
- `max_text_file_bytes`: maximum size for text files to include (bytes).

### Manage ignores (recommended)
Add patterns:
```bash
python skills/repo-codebook-generator/scripts/generate_repo_codebook.py --add-ignore "data/**" --add-ignore "*.pdf"
```

Remove patterns:
```bash
python skills/repo-codebook-generator/scripts/generate_repo_codebook.py --remove-ignore "*.pdf"
```

Update config only (no generation):
```bash
python skills/repo-codebook-generator/scripts/generate_repo_codebook.py --config-only --add-ignore "out/**"
```

## What counts as "generated/build/runtime artifacts"
Common examples: `.env`, `.venv`, `__pycache__`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `*.egg-info`, `.coverage`, `htmlcov`, lockfiles, etc.

## Steps (must follow in order)

### 1) Ensure output directory exists
Create:
- `docs/artifacts/`

### 2) Load persistent config
Read (or create) `docs/artifacts/repo_codebook.config.json` and apply:
- built-in excludes + `ignore_globs_extra`
- file-size threshold (`max_text_file_bytes`)
- empty-file behavior (`skip_empty_files`)

### 3) Generate project structure (tree) respecting `.gitignore`
Preferred: use `tree --gitignore` plus extra excludes via `-I`.

Recommended command (no colors, include dot dirs, directories first):
```bash
bash skills/repo-codebook-generator/scripts/get_tree.sh
```

Notes:
- `--gitignore` ensures `.gitignore` rules are applied.
- Extra ignores from config are applied best-effort (converted to a `tree -I` expression via `IGNORE_PATTERN_EXTRA`).
- If `tree` is not installed, the generator falls back to a `find`-based listing (best-effort).

### 4) Build the file list to document (matching tree semantics)
Use Git as the source of truth for "not ignored":
- `git ls-files -co --exclude-standard`

Then apply:
- built-in excludes
- persistent `ignore_globs_extra` from config

### 5) Write / update `docs/artifacts/repo_codebook.md`
The document must contain:

````md
## Project Info
- name: <short representative name>
- description:
  - <bullet 1>
  - <bullet 2>
- codebook_version: <semver>

## Project Structure
```bash
<tree output>
```

### Descriptions
- <path>: <one-line objective description>
...

## Project Current Code
```<path>
<full file contents>
```

...

````

### 6) Versioning rule for `codebook_version`
- If the file is created for the first time: `1.0.0`
- If it already exists: bump PATCH by default (e.g., `1.0.0` -> `1.0.1`)
- Only bump MINOR/MAJOR if explicitly requested.

### 7) Size / binary / empty-file safety
- Skip binary files and very large files (default threshold: 512 KB or `max_text_file_bytes` from config) and add a note like:
  - `- <path>: skipped (binary or too large)`
- Empty/whitespace-only files:
  - Descriptions show `skipped (empty file)`
  - Code blocks are omitted (when `skip_empty_files=true`)

## How to run (recommended)
Generate the codebook:
```bash
python skills/repo-codebook-generator/scripts/generate_repo_codebook.py
```

This will:
- Ensure `docs/artifacts/` exists
- Ensure `docs/artifacts/repo_codebook.config.json` exists (create if missing)
- Produce `tree` output using `.gitignore` + built-in excludes + config excludes (best-effort)
- Generate/update the codebook with bumped patch version
- Include one-line per file + full code blocks (excluding empty/binary/too-large)