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
- If you want to add a tool dependency (e.g., vulture/pyright/ruff plugins), DO NOT do it automatically. Instead propose it as an optional step with pros/cons and exact commands.
- Avoid scanning large binary/data artifacts. Focus analysis on detected roots + pyproject.toml. Ignore db/, out/, .venv/, node_modules/, and docs/ except docs/audit/.
- Treat “dynamic usage” as first-class: registries, importlib, getattr, pydantic/FastAPI reflection, **all**, side-effect imports. If something might be used dynamically, mark as “Needs manual confirmation” instead of “Dead”.

WORKFLOW (execute fully)
Step 0 — Baseline understanding

- Read README.md and pyproject.toml to identify official entrypoints, tasks, scripts, and runtime commands.
- Identify any console scripts / tool entrypoints declared in pyproject.
- Identify production “roots” (what actually runs).

Step 1 — Build an inventory

- Enumerate top-level packages/modules under the detected source roots.
- Note modules that look like public API boundaries (e.g., **init**.py re-exports, **all**).
- Identify candidate “leaf” modules that might be unused.

Step 2 — Static reference mapping (evidence-first)

- Use ripgrep to find imports/usages across detected roots.
- For each candidate file/symbol:
  - Search direct references (rg -n "SymbolName" <roots>)
  - Search module imports (rg -n "from pkg\\.x import" / "import pkg\\.x")
  - Search string-based/dynamic uses ("importlib", "registry", "getattr", "**all**", "entrypoint", "load\_")

Step 3 — Runtime verification signals (uv)

- Run tests with uv using the repo’s tasks (discover from pyproject).
- If feasible, run coverage and note persistently unexecuted modules/lines.
- If there is a repo hygiene script, run it and include results.

Step 4 — Dependency hygiene (pyproject audit)

- Inspect dependencies in pyproject.toml.
- Cross-check imports across roots to find deps that appear unused.
- Flag “maybe unused” vs “definitely unused”.

Step 5 — Produce the audit deliverables (docs/audit/)
Create THREE files:

1. docs/audit/audit.md (canonical, strict format + few-shot example block)
2. docs/audit/dead_code_audit.md (human-friendly summary)
3. docs/audit/dead_code_audit.json (machine-friendly)

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
