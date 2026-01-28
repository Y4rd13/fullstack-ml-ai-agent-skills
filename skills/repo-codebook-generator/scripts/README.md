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
