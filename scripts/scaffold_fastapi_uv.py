from __future__ import annotations

import argparse
from pathlib import Path


def _read_template(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_file(path: Path, content: str, *, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")


def _touch_init(dir_path: Path) -> None:
    dir_path.mkdir(parents=True, exist_ok=True)
    init_file = dir_path / "__init__.py"
    if not init_file.exists():
        init_file.write_text("", encoding="utf-8")


def _apply_replacements(content: str, repl: dict[str, str]) -> str:
    for k, v in repl.items():
        content = content.replace(k, v)
    return content


def scaffold(project_dir: Path, service_name: str, app_title: str, python_version: str, overwrite: bool) -> None:
    base = project_dir.resolve()
    templates = Path(__file__).resolve().parents[1] / "assets" / "templates"

    repl = {
        "__SERVICE_NAME__": service_name,
        "__APP_TITLE__": app_title,
        "__PYTHON_VERSION__": python_version,
    }

    _write_file(base / "pyproject.toml", _apply_replacements(_read_template(templates / "pyproject.toml.tmpl"), repl), overwrite=overwrite)
    _write_file(base / ".python-version", _apply_replacements(_read_template(templates / "python-version.tmpl"), repl), overwrite=overwrite)
    _write_file(base / "Dockerfile", _apply_replacements(_read_template(templates / "Dockerfile.tmpl"), repl), overwrite=overwrite)
    _write_file(base / "README.md", _apply_replacements(_read_template(templates / "README.md.tmpl"), repl), overwrite=overwrite)
    _write_file(base / ".env.example", _apply_replacements(_read_template(templates / "env.example.tmpl"), repl), overwrite=overwrite)

    _touch_init(base / "src")
    _touch_init(base / "src" / "core")
    _touch_init(base / "src" / "api")
    _touch_init(base / "src" / "api" / "v1")
    _touch_init(base / "src" / "api" / "v1" / "endpoints")
    _touch_init(base / "src" / "api" / "v2")
    _touch_init(base / "src" / "schemas")
    _touch_init(base / "src" / "services")
    _touch_init(base / "src" / "services" / "clients")
    _touch_init(base / "src" / "utils")

    _write_file(base / "src" / "main.py", _apply_replacements(_read_template(templates / "src_main.py.tmpl"), repl), overwrite=overwrite)
    _write_file(base / "src" / "core" / "config.py", _apply_replacements(_read_template(templates / "src_core_config.py.tmpl"), repl), overwrite=overwrite)
    _write_file(base / "src" / "core" / "log_config.py", _apply_replacements(_read_template(templates / "src_core_log_config.py.tmpl"), repl), overwrite=overwrite)
    _write_file(base / "src" / "core" / "logger_func.py", _apply_replacements(_read_template(templates / "src_core_logger_func.py.tmpl"), repl), overwrite=overwrite)
    _write_file(base / "src" / "core" / "errors.py", _apply_replacements(_read_template(templates / "src_core_errors.py.tmpl"), repl), overwrite=overwrite)

    _write_file(base / "src" / "api" / "deps.py", _apply_replacements(_read_template(templates / "src_api_deps.py.tmpl"), repl), overwrite=overwrite)
    _write_file(base / "src" / "api" / "v1" / "router.py", _apply_replacements(_read_template(templates / "src_api_v1_router.py.tmpl"), repl), overwrite=overwrite)
    _write_file(base / "src" / "api" / "v1" / "endpoints" / "health.py", _apply_replacements(_read_template(templates / "src_api_v1_health.py.tmpl"), repl), overwrite=overwrite)

    _write_file(
        base / "src" / "services" / "clients" / "httpx_client.py",
        _apply_replacements(_read_template(templates / "src_services_clients_httpx.py.tmpl"), repl),
        overwrite=overwrite,
    )

    _touch_init(base / "tests")
    _write_file(base / "tests" / "test_health.py", _apply_replacements(_read_template(templates / "tests_test_health.py.tmpl"), repl), overwrite=overwrite)

    print(f"Scaffold complete: {base}")
    print("Next steps:")
    print(f"  cd {base}")
    print("  uv sync")
    print("  uv run task lint_fix")
    print("  uv run task test")
    print('  uv run uvicorn main:app --host 0.0.0.0 --port 8000 --app-dir src')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--service-name", required=True)
    parser.add_argument("--app-title", required=True)
    parser.add_argument("--python-version", default="3.14.2")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    scaffold(
        project_dir=Path(args.project_dir),
        service_name=args.service_name,
        app_title=args.app_title,
        python_version=args.python_version,
        overwrite=bool(args.overwrite),
    )


if __name__ == "__main__":
    main()
