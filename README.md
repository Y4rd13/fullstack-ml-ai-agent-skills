# 🏗️ FastAPI Architect Skills

A **Codex CLI skill** that helps you **scaffold, audit, and refactor** FastAPI services using **uv**, a clean **`src/` layout**, **versioned routers** (`/v1`, `/v2`), and **singleton external clients** under `src/services/clients`.

[x] Opinionated, production-ready defaults
[x] Minimal, essential English comments only
[x] Built to keep endpoints thin and business logic in services
[x] Designed for teams that want consistent project structure and quality gates

---

## ✨ What this skill does

### 🧱 Scaffold a new FastAPI service

Generates a ready-to-run project with:

* `uv` + `pyproject.toml`
* `src/` package layout
* API versioning (`/v1` ready)
* `pydantic-settings` configuration
* Structured logging template
* Singleton `httpx` client (`src/services/clients`)
* Health endpoint + test
* Dockerfile built around `uv`

### 🔍 Audit an existing FastAPI service

Produces an **objective, numbered plan** with:

* Missing files/folders vs the blueprint
* Router versioning checks (`/v1`, `/v2`)
* Singleton client heuristics (`src/services/clients`)
* Final quality-gate recommendations (lint + tests)

---

## 📁 Repository layout

This repo is meant to be copied into your Codex skills directory:

```
fastapi-architect/
├─ SKILL.md
├─ scripts/
│  ├─ scaffold_fastapi_uv.py
│  └─ audit_fastapi_project.py
├─ references/
│  ├─ fastapi_notes.md
│  └─ uv_notes.md
└─ assets/
   └─ templates/
      ├─ pyproject.toml.tmpl
      ├─ Dockerfile.tmpl
      ├─ README.md.tmpl
      ├─ env.example.tmpl
      ├─ python-version.tmpl
      ├─ src_main.py.tmpl
      ├─ src_core_config.py.tmpl
      ├─ src_core_log_config.py.tmpl
      ├─ src_core_logger_func.py.tmpl
      ├─ src_core_errors.py.tmpl
      ├─ src_api_deps.py.tmpl
      ├─ src_api_v1_router.py.tmpl
      ├─ src_api_v1_health.py.tmpl
      ├─ src_services_clients_httpx.py.tmpl
      └─ tests_test_health.py.tmpl
```

---

## ✅ Output project structure (scaffold result)

When you scaffold a project, you get:

```
<project>/
├─ pyproject.toml
├─ .python-version
├─ Dockerfile
├─ README.md
├─ .env.example
├─ src/
│  ├─ __init__.py
│  ├─ main.py                       # FastAPI entrypoint (includes /v1, /v2 routers here)
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ config.py                  # Settings (pydantic-settings)
│  │  ├─ log_config.py              # Logging config
│  │  ├─ logger_func.py             # Logger init
│  │  └─ errors.py                  # Minimal app-level exceptions
│  ├─ api/
│  │  ├─ __init__.py
│  │  ├─ deps.py                    # Shared dependencies
│  │  ├─ v1/
│  │  │  ├─ __init__.py
│  │  │  ├─ router.py               # v1 router aggregator
│  │  │  └─ endpoints/
│  │  │     ├─ __init__.py
│  │  │     └─ health.py            # /v1/health
│  │  └─ v2/
│  │     └─ __init__.py             # (placeholder by default)
│  ├─ schemas/
│  │  └─ __init__.py
│  ├─ services/
│  │  ├─ __init__.py
│  │  └─ clients/
│  │     ├─ __init__.py
│  │     └─ httpx_client.py         # singleton factory
│  └─ utils/
│     └─ __init__.py
└─ tests/
   ├─ __init__.py
   └─ test_health.py
```

📌 Note: `/v2` is created as a placeholder directory by default. If you want `/v2` fully scaffolded (router + endpoints + include in `main.py`), add templates and update the scaffold script accordingly.

---

## 🛠️ Installation

### Option A — Clone into Codex skills folder

1. Create the skills directory:

* `~/.codex/skills/`

2. Clone:

* `git clone <YOUR_REPO_URL> ~/.codex/skills/fastapi-architect`

3. Restart Codex CLI so it discovers the new skill.

### Option B — Download ZIP

1. Download this repo as a ZIP
2. Extract it to:

* `~/.codex/skills/fastapi-architect`

3. Restart Codex CLI.

---

## 🚀 Usage

### 🧱 Scaffold a new FastAPI service

Run the scaffold script with `uv`:

* `uv run python scripts/scaffold_fastapi_uv.py --project-dir <path> --service-name <name> --app-title "<title>"`

Example:

* `uv run python scripts/scaffold_fastapi_uv.py --project-dir ~/projects/my-api --service-name my-api --app-title "My API"`

Then inside the generated project:

* `uv sync`
* `uv run task lint_fix`
* `uv run task test`
* `uv run uvicorn main:app --host 0.0.0.0 --port 8000 --app-dir src`

### 🔍 Audit an existing FastAPI project

* `uv run python scripts/audit_fastapi_project.py --project-dir <path>`

Example:

* `uv run python scripts/audit_fastapi_project.py --project-dir .`

---

## 📐 Design principles (opinionated rules)

✅ **Versioned APIs**

* Routers must be included via `prefix="/v1"` (and optionally `/v2`) in `src/main.py`.

✅ **Thin endpoints**

* Endpoints should be minimal orchestration.
* Business logic goes into `src/services/`.

✅ **Singleton external clients**

* External clients live in `src/services/clients/`.
* Always use a singleton factory (default uses `@lru_cache`).
* Close clients via FastAPI `lifespan`.

✅ **Utilities in `src/utils`**

* Keep helpers small and focused.

✅ **Essential comments only (English)**

* No verbose commentary.
* Only include the minimum that improves correctness/maintainability.

---

## 🧪 Quality gates

The scaffolded project includes Taskipy tasks:

* Lint & type-check:

  * `uv run task lint`

* Auto-fix:

  * `uv run task lint_fix`

* Tests:

  * `uv run task test`

---

## 🐳 Docker

The scaffold includes a uv-based Dockerfile. Build & run:

* `docker build -t <service-name> .`
* `docker run --rm -p 8000:8000 <service-name>`

---

## 🧩 Extending the skill

Common improvements you might add:

* ✅ Fully scaffold `/v2` (router + endpoints + include in `main.py`)
* ✅ Add `pre-commit` hooks (ruff/black/mypy)
* ✅ Add structured JSON logging for Loki/ELK
* ✅ Add DB client singletons (Postgres/Redis) templates
* ✅ Add CI workflow for linting templates and scripts

---

## 📚 References

* FastAPI Documentation (project structure, APIRouter, lifespan, settings patterns)
* OpenAI Codex Skills documentation (skill layout, SKILL.md conventions)
* uv documentation (dependency management + Docker patterns)

---

## 🤝 Contributing

PRs are welcome! Suggested contribution flow:

1. Create a feature branch
2. Keep diffs small and focused
3. Update templates + scripts together
4. Add/adjust tests if you change generated behavior

---

## 📜 License

Pick a license (MIT is a common default) and add it as `LICENSE` in the repo.