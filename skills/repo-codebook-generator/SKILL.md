---
name: repo-codebook-generator
description: Generates a single repository "codebook" artifact (structure + one-line file descriptions + full source) respecting .gitignore and excluding non-source artifacts.
license: MIT
---

This skill is a boundary/artifact generator. It produces a single, versioned repository snapshot document.

## Output artifact
- Path: `docs/artifacts/repo_codebook.md`
- Rationale: this is a generated documentation artifact, not production source.

## Non-negotiables
- Do NOT include secrets or env files (e.g., `.env`, `.env.*`).
- Exclude generated/build/runtime artifacts and other non-source noise.
- File descriptions must be 1 line max, objective, and accurate.
- If you add comments to code while generating/fixing: ONLY essential comments, in ENGLISH.

## What counts as "generated/build/runtime artifacts"
Common examples: `.env`, `.venv`, `__pycache__`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `*.egg-info`, `.coverage`, `htmlcov`, lockfiles, etc.

## Steps (must follow in order)

### 1) Ensure output directory exists
Create:
- `docs/artifacts/`

### 2) Generate project structure via tree (respecting .gitignore)
Use `tree` with `--gitignore` to filter ignored files/dirs. (`tree --gitignore` uses `.gitignore` rules.)  
Also exclude additional patterns via `-I` using wildcards separated by `|`.

Recommended command (no colors, include dot dirs, directories first):
```bash
bash scripts/get_tree.sh
````

Notes:

* `--gitignore` ensures `.gitignore` rules are applied.
* `-I` is used to exclude extra patterns (wildcards/globs).

### 3) Build the file list to document (matching tree semantics)

Use Git as the source of truth for "not ignored":

* `git ls-files -co --exclude-standard`
  Then apply the same extra excludes as in the tree ignore pattern.

### 4) Write / update `docs/artifacts/repo_codebook.md`

The document must contain:

````md
## Project Info
- name: <short representative name>
- description:
  - <bullet 1>
  - <bullet 2>
- all_docs_version: <semver>

## Project Structure
<tree output>

### Descriptions
- <path>: <one-line objective description>
...

## Project Current Code
```<path>
<full file contents>
```

...

````

### 5) Versioning rule for `all_docs_version`
- If the file is created for the first time: `1.0.0`
- If it already exists: bump PATCH by default (e.g., `1.0.0` -> `1.0.1`)
- Only bump MINOR/MAJOR if explicitly requested.

### 6) Size / binary safety
- Skip binary files and very large files (default threshold: 512 KB) and add a note like:
  - `- <path>: skipped (binary or too large)`
- Prefer documenting source code and config.

## How to run (recommended)
```bash
python scripts/generate_repo_codebook.py
```

This will:

* Create `docs/artifacts/` if missing
* Produce `tree` output using gitignore + extra excludes
* Generate/update the codebook with bumped patch version
* Include one-line per file + full code blocks