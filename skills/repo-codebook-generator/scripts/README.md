# repo-codebook-generator scripts

## Generate repo codebook

From the repository root:

```bash
python skills/repo-codebook-generator/scripts/generate_repo_codebook.py
```

Or from the skill directory:

```bash
cd skills/repo-codebook-generator
python scripts/generate_repo_codebook.py
```

### Requirements
- `git`
- `tree` (recommended; the script falls back to `find` if `tree` is missing)

### Output
- `docs/artifacts/repo_codebook.md`

## Persistent ignore rules (recommended)

The generator maintains a stateful config file:
- `docs/artifacts/repo_codebook.config.json`

### Add extra ignore patterns
```bash
python skills/repo-codebook-generator/scripts/generate_repo_codebook.py --add-ignore "data/**" --add-ignore "*.pdf"
```

### Remove ignore patterns
```bash
python skills/repo-codebook-generator/scripts/generate_repo_codebook.py --remove-ignore "*.pdf"
```

### Notes
- Extra ignore patterns are applied in addition to `.gitignore`.
- The tree view applies extra patterns best-effort (converted to a `tree -I` expression).
