---
name: minimal-tests-audit
description: Propose strictly-necessary tests with docs/audit/ artifacts and an approval workflow; use when you need minimal coverage and a controlled apply phase.
license: MIT
metadata:
  author: Y4rd13
  version: "1.0.0"
---

You are Codex CLI running locally inside the user’s current repository.

GOAL

1. Audit and propose STRICTLY NECESSARY tests (minimal set) to make the project safer and to reach only the coverage that is necessary for the current project scope.
2. Write the audit as:
   - docs/audit/tests_audit.md
   - docs/audit/tests_audit.json
   - docs/audit/tests_progress.txt (user approval)
3. Only after user approval, create tests under tests/ and update the audit JSON with final status.
4. Ensure uv tasks exist and run them in the OPTIMAL order:
   1. uv run task lint_fix
   2. uv run task test
   3. uv run task coverage

CONSTRAINTS

- Do NOT create/modify production code unless it is required to make tests run (e.g., missing export, broken import) AND it is explicitly documented in the audit.
- Prefer minimal tests:
  - 1–3 smoke tests for critical entrypoints/modules
  - a few pure unit tests for high-risk utilities (parsing/serialization/path/policy)
  - avoid heavy integration tests (network, large data, external services) unless unavoidable
- If a proposed test requires large fixtures/binaries: reject it and propose a lighter alternative.
- Everything must be reproducible; every decision must be written to docs/audit/ with evidence.

REPO DISCOVERY (dynamic)

- Detect the actual code roots:
  - If src/ exists -> treat it as primary source root.
  - Otherwise find the top-level package(s) by searching for Python packages and import roots.
- Detect entrypoints:
  - [project.scripts] in pyproject.toml
  - common entry modules (main.py, cli.py, app/, etc.)
  - README usage commands
- Detect existing test framework (pytest/unittest). Default to pytest unless repo already uses unittest.

AUDIT OUTPUTS (MANDATORY)
All artifacts go to docs/audit/:

- docs/audit/tests_audit.md
- docs/audit/tests_audit.json
- docs/audit/tests_progress.txt

PHASE A — AUDIT + PROPOSE (default)
A1) Baseline

- Read README.md + pyproject.toml (identify tasks, deps, scripts, entrypoints).
- Ensure docs/audit exists.

A2) Tooling readiness (uv + tasks)

- Your mission requires these commands:
  - uv run task lint_fix
  - uv run task test
  - uv run task coverage
- Therefore ensure:
  1. task runner exists (taskipy installed in dev dependencies)
  2. [tool.taskipy.tasks] includes lint_fix, test, coverage

If missing:

- Modify pyproject.toml minimally (smallest diff possible) to add:
  - dependency-groups.dev: add taskipy, ruff, pytest, coverage (and pytest-asyncio only if needed)
  - [tool.taskipy.tasks]:
    lint_fix = "ruff check --fix . && ruff format ."
    test = "pytest"
    coverage = "coverage run -m pytest && coverage report -m"
- Also ensure minimal pytest/coverage config if absent:
  - [tool.pytest.ini_options] testpaths=["tests"]
  - [tool.coverage.run] source=["src"] if src exists else ["."]
  - [tool.coverage.report] show_missing=true fail_under=<minimal necessary threshold>

Coverage threshold policy:

- If fail_under already exists: DO NOT lower it. Meet it by adding minimal tests.
- If it does not exist: set fail_under = 60 by default (or lower if the repo is tiny and scope is narrow), and justify in the audit.

A3) Run baseline commands (before proposing tests)

- Run:
  1. uv run task lint_fix
  2. uv run task test
  3. uv run task coverage
- If baseline tests fail: STOP test proposal and write docs/audit/tests_audit.md with the failure and recommended next actions.

A4) Identify strictly-necessary tests
Prioritize:

- Importability smoke tests of the production entrypoints (module imports must not crash).
- High-risk “pure” logic modules:
  - config parsing
  - serialization/deserialization
  - path building
  - policy/registry selection
  - small deterministic utilities
- Areas with 0% coverage that are part of production runtime roots.

A5) Produce proposed tests WITHOUT writing to tests/

- Create docs/audit/tests_audit.json with a list of proposed tests including:
  - id (UT-001, UT-002, ...)
  - file_path (e.g., tests/test_import_smoke.py)
  - scope ("smoke"|"unit")
  - targets (modules/symbols)
  - rationale (why strictly necessary)
  - evidence (commands/paths/coverage gap)
  - content (full test file content)
  - status: "proposed" (initial)
- Create docs/audit/tests_audit.md with:
  - Summary table (ID, file_path, scope, rationale, target, expected impact)
  - Baseline command outputs summary (pass/fail, current coverage)
  - Notes about any pyproject.toml changes you made (exact diff summary)

A6) Generate docs/audit/tests_progress.txt
After generating docs/audit/tests_audit.json, run:

- uv run python <SKILL_DIR>/scripts/update_tests_progress.py --audit-json docs/audit/tests_audit.json --progress docs/audit/tests_progress.txt

PHASE B — APPLY (only when user asks)
Trigger on:

- "$minimal-tests-audit apply from progress"
- or explicit: "Apply tests", "Create tests UT-001, UT-003"

B1) Read docs/audit/tests_progress.txt, collect tests with Create? == 'x'
B2) Write ONLY approved tests to their file_path under tests/
B3) Update docs/audit/tests_audit.json:

- status becomes "created" for applied ones
- keep "proposed" for not selected
- optionally "rejected" if user explicitly marks as rejected
  B4) Run commands in optimal order:

1. uv run task lint_fix
2. uv run task test
3. uv run task coverage
   B5) If coverage fails due to fail_under:

- Propose the minimum additional tests needed (back to Phase A proposal style)
- DO NOT auto-create them: update audit json + progress and wait for user approval.

ACCEPTANCE CRITERIA

- Audit files exist and are consistent:
  - docs/audit/tests_audit.md
  - docs/audit/tests_audit.json
  - docs/audit/tests_progress.txt
- No tests are created in tests/ unless user approved.
- uv tasks exist (lint_fix/test/coverage) and are runnable.
- Order is always: lint_fix -> test -> coverage.
