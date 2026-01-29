# dead-code-audit (Codex Skill)

Exhaustive dead-code + dependency hygiene audit for Python repositories (uv-based), producing reviewable artifacts under `docs/audit/`.

## Outputs (written to the target repo)

- `docs/audit/audit.md` (canonical, detailed)
- `docs/audit/dead_code_audit.md` (summary)
- `docs/audit/dead_code_audit.json` (machine-readable)
- `docs/audit/dead_code_progress.txt` (user-approved removals workflow)

## Usage

In Codex CLI, invoke:

- `$dead-code-audit` to run the audit.
- `$dead-code-audit apply from progress` after marking `x` in `docs/audit/dead_code_progress.txt`.

## Notes

- Evidence-first: no “dead” claim without rg/test/entrypoint evidence.
- Dynamic usage is treated as first-class: registries, **all**, re-exports, importlib, getattr, plugin discovery.
- Uses uv for tests/coverage when available.
