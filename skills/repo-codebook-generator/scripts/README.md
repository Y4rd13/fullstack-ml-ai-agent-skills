# repo-codebook-generator scripts

## Generate repo codebook

Run from the repository root you want to document:

```bash
uv run python ~/.codex/skills/repo-codebook-generator/scripts/generate_repo_codebook.py --repo-root "$PWD"
```

Or run from inside the skill directory (pointing `--repo-root` to the target repo):

```bash
cd skills/repo-codebook-generator
uv run python scripts/generate_repo_codebook.py --repo-root "$PWD"
```

### Requirements
- `git`
- `uv`
- `tree` (recommended; the script falls back to `find` if `tree` is missing)

### Output
- Codebook: `docs/artifacts/repo_codebook.md`
- Persistent config (state): `docs/artifacts/repo_codebook.config.json`

---

## Interactive preflight (default)

By default, when running in a TTY (interactive terminal), the generator runs an **interactive preflight** before writing `repo_codebook.md`:

1) Prints an "Ignore Summary" showing what will be excluded:
   - Layer 1: `.gitignore` / standard git excludes (respected via `git ls-files --exclude-standard` and `tree --gitignore`)
   - Layer 2: built-in excludes (skill hygiene)
   - Layer 3: persistent config excludes (`ignore_globs_extra`)

2) Prompts with enumerated options:
   1. Add more files/folders/patterns to ignore (persistent)
   2. Continue without changes

3) If you choose **1**, you can enter multiple paths/patterns (one per line; empty line finishes).
   - Directories are canonicalized and persisted as `dir/**` (ignore the directory and all descendants)
   - Globs like `*.pdf` are kept as-is

4) After saving, it prints what was added and shows the full `ignore_globs_extra` list.

5) Prompts again:
   1. Generate `repo_codebook.md` now
   2. Add more ignores (loops back)

### Disable prompts (CI / automation)

To skip the interactive preflight:

```bash
uv run python ~/.codex/skills/repo-codebook-generator/scripts/generate_repo_codebook.py --repo-root "$PWD" --non-interactive
```

---

## Persistent config

The generator maintains a stateful config file:
- `docs/artifacts/repo_codebook.config.json`

### Config fields
- `version`: config schema version (integer)
- `codebook_version`: last generated codebook version (semver string, e.g. `1.0.7`) used for version persistence even if `repo_codebook.md` is deleted
- `ignore_globs_extra`: additional glob patterns to exclude (e.g., `data/**`, `*.pdf`)
- `skip_empty_files`: if true, empty/whitespace-only files are omitted from the code section
- `max_text_file_bytes`: maximum size for text files to include (bytes)
- `notes`: optional human note

### Add extra ignore patterns (persistent)

```bash
uv run python ~/.codex/skills/repo-codebook-generator/scripts/generate_repo_codebook.py --repo-root "$PWD" --add-ignore "data/**" --add-ignore "*.pdf"
```

### Remove ignore patterns (persistent)

```bash
uv run python ~/.codex/skills/repo-codebook-generator/scripts/generate_repo_codebook.py --repo-root "$PWD" --remove-ignore "*.pdf"
```

### Update config only (no generation)

```bash
uv run python ~/.codex/skills/repo-codebook-generator/scripts/generate_repo_codebook.py --repo-root "$PWD" --config-only --add-ignore "out/**"
```

---

## Notes
- Extra ignore patterns are applied in addition to `.gitignore`.
- Directory-like ignores are expanded to ignore both the directory itself and all descendants (e.g., `data` -> `data` and `data/**`) to ensure directory pruning works correctly.
- `tree` view applies extra patterns best-effort (converted to a `tree -I` expression).
