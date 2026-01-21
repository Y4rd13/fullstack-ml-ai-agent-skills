from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable


REQUIRED_PATHS = [
    "pyproject.toml",
    "src/main.py",
    "src/core/config.py",
    "src/services/clients",
    "src/utils",
    "tests",
]


def _exists(base: Path, rel: str) -> bool:
    return (base / rel).exists()


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _find_include_router_versions(main_py: str) -> dict[str, bool]:
    return {
        "v1": bool(re.search(r'include_router\(.+prefix\s*=\s*["\']\/v1["\']', main_py)),
        "v2": bool(re.search(r'include_router\(.+prefix\s*=\s*["\']\/v2["\']', main_py)),
    }


def _iter_py_files(base: Path) -> Iterable[Path]:
    for p in base.rglob("*.py"):
        if any(part.startswith(".") for part in p.parts):
            continue
        yield p


def _client_singleton_heuristic(client_dir: Path) -> list[str]:
    findings: list[str] = []
    if not client_dir.exists():
        return ["Missing src/services/clients directory (required)."]

    py_files = list(client_dir.glob("*.py"))
    if not py_files:
        findings.append("No client modules found under src/services/clients (add singletons here).")
        return findings

    for f in py_files:
        text = _read_text(f)
        if "@lru_cache" not in text and "Singleton" not in text and "_instance" not in text:
            findings.append(f"Client module may not be singleton: {f.as_posix()} (expected @lru_cache factory or equivalent).")
    return findings


def audit(project_dir: Path) -> str:
    base = project_dir.resolve()

    report: list[str] = []
    report.append("# FastAPI Project Audit")
    report.append(f"Project: `{base}`")
    report.append("")

    report.append("## 1) Required structure")
    missing = [p for p in REQUIRED_PATHS if not _exists(base, p)]
    if missing:
        report.append("Missing:")
        for p in missing:
            report.append(f"- {p}")
    else:
        report.append("OK: required paths exist.")
    report.append("")

    report.append("## 2) API versioning in src/main.py")
    main_py_path = base / "src" / "main.py"
    main_text = _read_text(main_py_path)
    versions = _find_include_router_versions(main_text)
    report.append(f"- /v1 routers included: {versions['v1']}")
    report.append(f"- /v2 routers included: {versions['v2']}")
    report.append("")

    report.append("## 3) Singleton external clients")
    client_findings = _client_singleton_heuristic(base / "src" / "services" / "clients")
    if client_findings:
        report.append("Findings:")
        for f in client_findings:
            report.append(f"- {f}")
    else:
        report.append("OK: client singletons look reasonable.")
    report.append("")

    report.append("## 4) Quick refactor plan (objective)")
    plan: list[str] = []
    i = 1
    for p in missing:
        plan.append(f"{i}. Create `{p}` according to the blueprint structure.")
        i += 1
    if not versions["v1"]:
        plan.append(f"{i}. Update `src/main.py` to include routers with `prefix='/v1'` and explicit tags.")
        i += 1
    if client_findings:
        plan.append(f"{i}. Ensure all external clients live in `src/services/clients/` and use a singleton factory (e.g., `@lru_cache`).")
        i += 1
    plan.append(f"{i}. Run quality gates: `uv run task lint_fix` then `uv run task test`.")
    report.extend(plan)
    report.append("")

    return "\n".join(report)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()
    print(audit(Path(args.project_dir)))


if __name__ == "__main__":
    main()
