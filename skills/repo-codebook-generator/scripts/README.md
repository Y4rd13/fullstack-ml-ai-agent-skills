# repo-codebook-generator scripts

## Generate repo codebook

From the repository root:

```bash
uv run python ~/.codex/skills/repo-codebook-generator/scripts/generate_repo_codebook.py --repo-root "$PWD"
```

Or from the skill directory:

```bash
cd skills/repo-codebook-generator
uv run python scripts/generate_repo_codebook.py --repo-root "$PWD"
```

### Requirements
- `git`
- `uv`
- `tree` (recommended; the script falls back to `find` if `tree` is missing)

### Output
- `docs/artifacts/repo_codebook.md`
- `docs/artifacts/repo_codebook.config.json`

## Persistent ignore rules (recommended)

The generator maintains a stateful config file:
- `docs/artifacts/repo_codebook.config.json`

### Add extra ignore patterns
```bash
uv run python ~/.codex/skills/repo-codebook-generator/scripts/generate_repo_codebook.py --add-ignore "data/**" --add-ignore "*.pdf" --repo-root "$PWD"
```

### Remove ignore patterns
```bash
uv run python ~/.codex/skills/repo-codebook-generator/scripts/generate_repo_codebook.py --remove-ignore "*.pdf" --repo-root "$PWD"
```

### Notes
- Extra ignore patterns are applied in addition to `.gitignore`.
- The tree view applies extra patterns best-effort (converted to a `tree -I` expression).