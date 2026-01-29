You are Codex CLI running locally inside this repository. Your mission is to perform an EXHAUSTIVE dead-code audit (Python) and produce a reviewable report with evidence.

REPO CONTEXT (dynamic)

- Python project managed with uv (pyproject.toml + uv.lock)
- Detect code roots dynamically (common: src/, app/, packages/, services/, scripts/, tests/)
- Output folder for this audit: docs/audit/

PRIMARY OBJECTIVE
Find “dead code” candidates and hygiene issues with strong evidence:

1. Unused modules/files/classes/functions/constants
2. Unused imports and re-exports
3. Unreferenced CLI/scripts/entrypoints
4. Unused configuration options / feature flags
5. Unused dependencies (declared but not imported/used)
6. Unreachable code paths (never called, guarded by impossible conditions)
7. Stale/duplicated code (same logic repeated, one path unused)

IMPORTANT CONSTRAINTS

- Do NOT delete or refactor anything by default.
- Prefer evidence over guesses. For each dead-code claim, provide: (a) symbol/file, (b) reason, (c) concrete evidence (ripgrep results, call sites, entrypoints, dynamic-use analysis).
- Avoid scanning large binary/data artifacts. Focus analysis on detected roots + pyproject.toml. Ignore db/, out/, .venv/, node_modules/, and docs/ except docs/audit/.
- Treat dynamic usage as first-class: registries, importlib, getattr, pydantic/FastAPI reflection, **all**, side-effect imports.
  If something might be used dynamically, mark as “Needs manual confirmation” instead of “Dead”.

REPO TYPE DETECTION (PUBLISHED LIBRARY HEURISTIC)
Set PUBLISHED_LIBRARY=true if at least TWO of:

1. pyproject has [project] name + (version or dynamic) + build backend (setuptools/hatchling/poetry/pdm)
2. README mentions pip install / PyPI / pypi.org link
3. CI mentions publish/release/pypi/twine/wheel/sdist
4. metadata indicates distribution: classifiers, keywords, urls, license, etc.
   If uncertain, default to PUBLISHED_LIBRARY=true.

API SURFACE SAFETY RULE (PROMOTE RE-EXPORTS)
If PUBLISHED_LIBRARY=true:

- Anything in _**init**.py or only referenced via _**init**.py re-export (including **all**) MUST be “Needs manual confirmation”.
- Recommendation must include how to confirm downstream usage (search dependent repos / consumers).

WORKFLOW (execute fully) 0) Read README + pyproject; detect roots; set PUBLISHED_LIBRARY; document it.

1. Inventory packages/modules; identify API boundaries (**init**.py, **all**, registries).
2. Static mapping with rg (direct refs + module imports + dynamic signals); apply promotion rule.
3. Runtime signals (uv): run tests/coverage if available.
4. Dependency audit: pyproject deps vs imports.
5. Produce artifacts in docs/audit/:
   - docs/audit/audit.md
   - docs/audit/dead_code_audit.md
   - docs/audit/dead_code_audit.json

After generating dead_code_audit.json, run:

- uv run python <SKILL_DIR>/scripts/update_dead_code_progress.py --audit-json docs/audit/dead_code_audit.json --progress docs/audit/dead_code_progress.txt

  (Resolve <SKILL_DIR> from the skill path in context; use an absolute path.)

CANONICAL AUDIT DOC (docs/audit/audit.md) — REQUIRED FORMAT
[Same format rules as described in the skill.]

ACCEPTANCE CRITERIA

- No “dead” claim without evidence.
- Every candidate includes: confidence + risk + exact search evidence.
- Tests are run (or you clearly explain why not possible).
- You do not modify production code unless explicitly asked later.
- You keep going until ALL required files exist under docs/audit/.
