from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path

# --------------------------------------------------------------------------------------
# Path resolution
# --------------------------------------------------------------------------------------
_THIS_FILE = Path(__file__).resolve()
_SCRIPTS_DIR = _THIS_FILE.parent
_SKILL_ROOT = _SCRIPTS_DIR.parent  # skills/repo-codebook-generator
_REPO_ROOT = _SKILL_ROOT.parent.parent  # repo root

OUTPUT_PATH = _REPO_ROOT / "docs/artifacts/repo_codebook.md"
TEMPLATE_PATH = _SKILL_ROOT / "assets/templates/repo_codebook.md.tmpl"
TREE_SCRIPT = _SKILL_ROOT / "scripts/get_tree.sh"


# --------------------------------------------------------------------------------------
# Exclusions (in addition to .gitignore)
# --------------------------------------------------------------------------------------
EXCLUDE_GLOBS = {
    "*.pyc",
    "*.egg-info",
    ".env",
    ".env.*",
    ".coverage",
    "uv.lock",
    ".python-version",
    ".dockerignore",
    ".gitignore",
    "docs/artifacts/*",
    "docs/artifacts/repo_codebook.md",
}

MAX_TEXT_FILE_BYTES = 512 * 1024  # 512 KB

_VERSION_RE = re.compile(r"^- codebook_version:\s*([0-9]+)\.([0-9]+)\.([0-9]+)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class ProjectInfo:
    name: str
    description_bullets: list[str]


def _run(cmd: list[str], *, cwd: Path) -> str:
    res = subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=str(cwd))
    return res.stdout.rstrip("\n")


def _should_exclude(rel_path: Path) -> bool:
    # Exclude docs/artifacts (avoid self-inclusion recursion)
    if rel_path.parts[:2] == ("docs", "artifacts"):
        return True

    # Exclude common generated/build/runtime artifacts and repo noise
    if any(
        part
        in {
            ".git",
            "__pycache__",
            ".venv",
            ".mypy_cache",
            ".ruff_cache",
            ".pytest_cache",
            "htmlcov",
            "tests",
        }
        for part in rel_path.parts
    ):
        return True

    p = rel_path.as_posix()
    return any(fnmatch(p, pat) for pat in EXCLUDE_GLOBS)


def _is_binary_or_too_large(abs_path: Path) -> bool:
    try:
        size = abs_path.stat().st_size
    except OSError:
        return True

    if size > MAX_TEXT_FILE_BYTES:
        return True

    try:
        abs_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return True

    return False


def _is_effectively_empty(abs_path: Path) -> bool:
    try:
        if abs_path.stat().st_size == 0:
            return True
    except OSError:
        return False

    try:
        txt = abs_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False

    return txt.strip() == ""


def _bump_patch_version(existing: str | None) -> str:
    if not existing:
        return "1.0.0"

    m = _VERSION_RE.search(existing)
    if not m:
        return "1.0.0"

    major, minor, patch = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return f"{major}.{minor}.{patch + 1}"


def _project_info() -> ProjectInfo:
    repo_name = _REPO_ROOT.name

    bullets: list[str] = []
    readme = _REPO_ROOT / "README.md"
    if readme.exists():
        lines = [ln.strip() for ln in readme.read_text(encoding="utf-8", errors="ignore").splitlines()]
        for ln in lines:
            if ln and not ln.startswith("#") and len(bullets) < 3:
                bullets.append(f"- {ln[:120]}")

    if not bullets:
        bullets = ["- Repository codebase (generated codebook)."]

    return ProjectInfo(name=repo_name, description_bullets=bullets)


def _tree_output() -> str:
    # Preferred: tree via the skill's script (respects .gitignore).
    if shutil.which("tree") and TREE_SCRIPT.exists():
        try:
            return _run(["bash", str(TREE_SCRIPT)], cwd=_REPO_ROOT)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # Fallback: use find (best-effort). Note: may not replicate .gitignore perfectly.
    return _find_output()


def _find_output() -> str:
    # If find is available, use it; otherwise walk the filesystem in Python.
    if shutil.which("find"):
        try:
            raw = _run(["find", ".", "-print"], cwd=_REPO_ROOT)
            lines: list[str] = ["./"]
            for ln in raw.splitlines():
                ln = ln.strip()
                if not ln or ln == ".":
                    continue
                rel = ln.lstrip("./")
                rel_path = Path(rel)
                if _should_exclude(rel_path):
                    continue
                lines.append(f"./{rel}")
            return "\n".join(sorted(set(lines)))
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    collected: list[str] = ["./"]
    for root, dirs, files in os.walk(_REPO_ROOT):
        rel_root = Path(root).resolve().relative_to(_REPO_ROOT)

        # Prune excluded directories
        kept_dirs: list[str] = []
        for d in dirs:
            rel_dir = (rel_root / d) if rel_root != Path(".") else Path(d)
            if _should_exclude(rel_dir):
                continue
            kept_dirs.append(d)
        dirs[:] = kept_dirs

        for f in files:
            rel_file = (rel_root / f) if rel_root != Path(".") else Path(f)
            if _should_exclude(rel_file):
                continue
            collected.append(f"./{rel_file.as_posix()}")

    return "\n".join(sorted(set(collected)))


def _file_list() -> list[Path]:
    # Tracked + untracked (not ignored), respecting .gitignore via --exclude-standard.
    raw = _run(["git", "ls-files", "-co", "--exclude-standard"], cwd=_REPO_ROOT)
    files = [Path(p) for p in raw.splitlines() if p.strip()]

    filtered: list[Path] = []
    for rel in files:
        if _should_exclude(rel):
            continue
        abs_path = _REPO_ROOT / rel
        if not abs_path.exists() or abs_path.is_dir():
            continue
        filtered.append(rel)

    return sorted(filtered, key=lambda x: x.as_posix())


def _one_line_description(rel_path: Path) -> str:
    abs_path = _REPO_ROOT / rel_path

    if _is_effectively_empty(abs_path):
        return "skipped (empty file)"

    if _is_binary_or_too_large(abs_path):
        return "skipped (binary or too large)"

    try:
        text = abs_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return "Unreadable file."

    triple_dq = '"' * 3
    triple_sq = "'" * 3

    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith(triple_dq) or s.startswith(triple_sq):
            continue
        return s[:140]

    return "Empty file."


def _render_descriptions(paths: list[Path]) -> str:
    lines = [f"- `{p.as_posix()}`: {_one_line_description(p)}" for p in paths]
    return "\n".join(lines)


def _render_code_blocks(paths: list[Path]) -> str:
    blocks: list[str] = []

    for rel in paths:
        abs_path = _REPO_ROOT / rel

        if _is_effectively_empty(abs_path):
            continue

        if _is_binary_or_too_large(abs_path):
            blocks.append(f"- `{rel.as_posix()}`: skipped (binary or too large)\n")
            continue

        content = abs_path.read_text(encoding="utf-8")
        fence = f"```{rel.as_posix()}".rstrip()
        blocks.append(f"{fence}\n{content}\n```\n")

    return "\n".join(blocks).rstrip()


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    existing = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else None
    version = _bump_patch_version(existing)

    info = _project_info()
    tree_out = _tree_output()
    paths = _file_list()

    tmpl = TEMPLATE_PATH.read_text(encoding="utf-8")
    out = tmpl
    out = out.replace("__PROJECT_NAME__", info.name)
    out = out.replace("__PROJECT_DESCRIPTION_BULLETS__", "\n".join(info.description_bullets))
    out = out.replace("__CODEBOOK_VERSION__", version)
    out = out.replace("__TREE_OUTPUT__", tree_out)
    out = out.replace("__FILE_DESCRIPTIONS__", _render_descriptions(paths))
    out = out.replace("__FILE_CODE_BLOCKS__", _render_code_blocks(paths))

    OUTPUT_PATH.write_text(out + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
