---
name: fastapi-architect
description: Scaffold, review, or refactor FastAPI services using uv, a src/ layout, versioned routers (/v1, /v2), and singleton external clients under src/services/clients.
---

# FastAPI + uv Blueprint Skill

## When to use
Use this skill when the user asks to:
- Create a new FastAPI service with best practices (uv + src/ layout + Dockerfile).
- Refactor an existing FastAPI codebase into a clean, versioned API layout.
- Enforce consistent conventions: settings via pydantic-settings, structured logging, thin endpoints, and singleton external clients.

## Non-goals
- Do not invent domain/business logic.
- Do not add heavy abstractions or excessive comments.
- Do not introduce new frameworks unless required.

## Core standards (must follow)
1. Project uses **uv** and defines `pyproject.toml`.
2. Code lives under `src/` and is importable with `PYTHONPATH=/app/src` (Docker) and standard tooling.
3. API versioning is explicit in `src/main.py`:
   - `app.include_router(<router>, prefix="/v1", tags=[...])`
   - optionally `/v2` as well.
4. External clients go in `src/services/clients/` and **always use a singleton pattern**.
5. Utilities (small helpers) go in `src/utils/`.
6. Comments are **only the essentials** and **in English**.

## Workflow
### A) If the user does NOT have a project yet (scaffold)
1. Create the project using the scaffold script:
   - `uv run python {baseDir}/scripts/scaffold_fastapi_uv.py --project-dir <path> --service-name <name> --app-title "<title>"`
2. Then in the new project directory:
   - `uv sync`
   - `uv run task lint_fix`
   - `uv run task test`
3. Provide the user with:
   - How to run locally: `uv run uvicorn main:app --host 0.0.0.0 --port 8000 --app-dir src`
   - How to run Docker.

### B) If the user ALREADY has a project (audit + plan + refactor)
1. Run:
   - `uv run python {baseDir}/scripts/audit_fastapi_project.py --project-dir <path>`
2. Produce an **objective, numbered** plan:
   - What to move/rename
   - What to add/remove
   - What to fix (imports, routers, settings, clients, tests)
3. Apply changes incrementally:
   - Keep diffs small
   - Update imports
   - Ensure `/v1` routing works
4. Finish with quality gates:
   - `uv run task lint_fix`
   - `uv run task test`

## Singleton clients (required)
- Implement singleton clients in `src/services/clients/*`.
- Prefer an `@lru_cache` factory to guarantee one instance per process.
- Close clients on shutdown using FastAPI `lifespan`.

## Deliverables checklist
- `pyproject.toml` with minimal runtime deps + dev tooling.
- `src/main.py` with `/v1` (and optionally `/v2`) routing.
- `src/core/config.py` using `pydantic-settings`.
- `src/core/log_config.py` + `src/core/logger_func.py`.
- `src/api/deps.py` for shared dependencies.
- `src/services/clients/` with singleton example (httpx).
- `tests/` with a basic health test.
- Dockerfile using uv.

## Notes
- Use `fastapi[standard]` unless the user explicitly requests otherwise.
- Prefer FastAPI `lifespan` to manage startup/shutdown resources.
