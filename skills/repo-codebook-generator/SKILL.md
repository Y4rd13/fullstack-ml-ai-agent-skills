---
name: repo-codebook-generator
description: Generate a repository codebook (structure, one-line file descriptions, full source) while respecting .gitignore; use for audits, onboarding, or snapshot documentation.
license: MIT
metadata:
  author: Y4rd13
  version: "1.0.0"
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
- Behavior: created automatically on first run if missing (bootstrapped from the skill template when available).

### Config fields
- `version`: config schema version (integer).
- `codebook_version`: last generated codebook version (semver string, e.g., `1.0.7`). Used to persist versioning even if `repo_codebook.md` is deleted.
- `ignore_globs_extra`: additional glob patterns to exclude (e.g., `data/**`, `*.pdf`).
- `skip_empty_files`: if true, empty/whitespace-only files are omitted from the code section.
- `max_text_file_bytes`: maximum size for text files to include (bytes).

## How to run (recommended)
Run from the repository root you want to document:

```bash
uv run python ~/.codex/skills/repo-codebook-generator/scripts/generate_repo_codebook.py --repo-root "$PWD"
```

### Non-interactive mode (CI / automation)
To skip prompts and generate immediately:

```bash
uv run python ~/.codex/skills/repo-codebook-generator/scripts/generate_repo_codebook.py --repo-root "$PWD" --non-interactive
```

### Manage ignores (recommended)
Add patterns:
```bash
uv run python ~/.codex/skills/repo-codebook-generator/scripts/generate_repo_codebook.py --repo-root "$PWD" --add-ignore "data/**" --add-ignore "*.pdf"
```

Remove patterns:
```bash
uv run python ~/.codex/skills/repo-codebook-generator/scripts/generate_repo_codebook.py --repo-root "$PWD" --remove-ignore "*.pdf"
```

Update config only (no generation):
```bash
uv run python ~/.codex/skills/repo-codebook-generator/scripts/generate_repo_codebook.py --repo-root "$PWD"  --config-only --add-ignore "out/**"
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
- persisted `codebook_version` (for version continuity)

### 3) Interactive preflight (before generation)
By default (when running in a TTY), the generator runs an interactive preflight **before** writing `docs/artifacts/repo_codebook.md`:

1) Print an "Ignore Summary" showing:
   - Layer 1: `.gitignore` / git excludes behavior
   - Layer 2: built-in excludes (components + globs)
   - Layer 3: current `ignore_globs_extra` from config

2) Prompt with enumerated choices:
   1. Add more files/folders/patterns to ignore (persistent)
   2. Continue without changes

3) If the user chooses **1**, accept multiple entries (one per line; empty line ends).
   - Directories are canonicalized and persisted as `dir/**` (ignore the directory and all descendants)
   - Globs like `*.pdf` are kept as-is

4) After saving, print what was added and show the full `ignore_globs_extra` list.

5) Prompt again:
   1. Generate `repo_codebook.md` now
   2. Add more ignores (loops back)

Note:
- Use `--non-interactive` to disable prompts (CI / automation).

### 4) Generate project structure (tree) respecting `.gitignore`
Preferred: use `tree --gitignore` plus extra excludes via `-I`.

Recommended command (no colors, include dot dirs, directories first):
```bash
bash skills/repo-codebook-generator/scripts/get_tree.sh
```

Notes:
- `--gitignore` ensures `.gitignore` rules are applied.
- Extra ignores from config are applied best-effort (converted to a `tree -I` expression via `IGNORE_PATTERN_EXTRA`).
- If `tree` is not installed, the generator falls back to a `find`-based listing (best-effort).

### 5) Build the file list to document (matching tree semantics)
Use Git as the source of truth for "not ignored":
- `git ls-files -co --exclude-standard`

Then apply:
- built-in excludes
- persistent `ignore_globs_extra` from config

Directory semantics:
- Directory-like ignore entries are expanded to exclude both the directory itself and all descendants (e.g., `data` -> `data` and `data/**`) so directory pruning works correctly.

### 6) Write / update `docs/artifacts/repo_codebook.md`
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

### 7) Versioning rule for `codebook_version`
- If the file is created for the first time: `1.0.0`
- If it already exists: bump PATCH by default (e.g., `1.0.0` -> `1.0.1`)
- If `repo_codebook.md` is missing but config contains `codebook_version`, bump PATCH from config to preserve continuity
- Only bump MINOR/MAJOR if explicitly requested.
- After successful generation, persist the new `codebook_version` into `docs/artifacts/repo_codebook.config.json`.

### 8) Size / binary / empty-file safety
- Skip binary files and very large files (default threshold: 512 KB or `max_text_file_bytes` from config) and add a note like:
  - `- <path>: skipped (binary or too large)`
- Empty/whitespace-only files:
  - Descriptions show `skipped (empty file)`
  - Code blocks are omitted (when `skip_empty_files=true`)

## How to run (recommended)
Generate the codebook:
```bash
uv run python ~/.codex/skills/repo-codebook-generator/scripts/generate_repo_codebook.py --repo-root "$PWD"
```

This will:
- Ensure `docs/artifacts/` exists
- Ensure `docs/artifacts/repo_codebook.config.json` exists (create if missing, bootstrapped from template when possible)
- Run an interactive ignore preflight (unless `--non-interactive` is used)
- Produce `tree` output using `.gitignore` + built-in excludes + config excludes (best-effort)
- Generate/update the codebook with bumped patch version (persisted in config for continuity)
- Include one-line per file + full code blocks (excluding empty/binary/too-large)
