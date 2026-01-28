from __future__ import annotations

import argparse
import json
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
CONFIG_PATH = _REPO_ROOT / "docs/artifacts/repo_codebook.config.json"
TEMPLATE_PATH = _SKILL_ROOT / "assets/templates/repo_codebook.md.tmpl"
TREE_SCRIPT = _SKILL_ROOT / "scripts/get_tree.sh"


# --------------------------------------------------------------------------------------
# Built-in exclusions (in addition to .gitignore)
# --------------------------------------------------------------------------------------
BUILTIN_EXCLUDE_COMPONENTS = {
    ".git",
    "__pycache__",
    ".venv",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "htmlcov",
    "tests",
}

BUILTIN_EXCLUDE_GLOBS: set[str] = {
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
    "docs/artifacts/repo_codebook.config.json",
}

DEFAULT_MAX_TEXT_FILE_BYTES = 512 * 1024  # 512 KB

_VERSION_RE = re.compile(r"^- codebook_version:\s*([0-9]+)\.([0-9]+)\.([0-9]+)\s*$", re.MULTILINE)

_VERSION_RE = re.compile(r"^- codebook_version:\s*([0-9]+)\.([0-9]+)\.([0-9]+)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class ProjectInfo:
    name: str
    description_bullets: list[str]


@dataclass(frozen=True)
class CodebookConfig:
    version: int
    ignore_globs_extra: list[str]
    skip_empty_files: bool
    max_text_file_bytes: int
    notes: str | None = None

    @staticmethod
    def default() -> CodebookConfig:
        return CodebookConfig(
            version=1,
            ignore_globs_extra=[],
            skip_empty_files=True,
            max_text_file_bytes=DEFAULT_MAX_TEXT_FILE_BYTES,
            notes=None,
        )


def _run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> str:
    res = subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=(os.environ | (env or {})),
    )
    return res.stdout.rstrip("\n")


def _load_config() -> CodebookConfig:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not CONFIG_PATH.exists():
        cfg = CodebookConfig.default()
        _save_config(cfg)
        return cfg

    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        cfg = CodebookConfig.default()
        _save_config(cfg)
        return cfg

    return CodebookConfig(
        version=int(data.get("version", 1)),
        ignore_globs_extra=list(data.get("ignore_globs_extra", [])),
        skip_empty_files=bool(data.get("skip_empty_files", True)),
        max_text_file_bytes=int(data.get("max_text_file_bytes", DEFAULT_MAX_TEXT_FILE_BYTES)),
        notes=data.get("notes"),
    )


def _save_config(cfg: CodebookConfig) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(
            {
                "version": cfg.version,
                "ignore_globs_extra": cfg.ignore_globs_extra,
                "skip_empty_files": cfg.skip_empty_files,
                "max_text_file_bytes": cfg.max_text_file_bytes,
                "notes": cfg.notes,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _normalize_glob(pat: str) -> str:
    pat = pat.strip()
    if pat.startswith("./"):
        pat = pat[2:]
    return pat


def _merge_exclude_globs(cfg: CodebookConfig) -> set[str]:
    extra = {_normalize_glob(p) for p in cfg.ignore_globs_extra if p and p.strip()}
    return set(BUILTIN_EXCLUDE_GLOBS) | extra


def _glob_to_tree_pattern(glob_pat: str) -> str:
    # Best-effort conversion from glob to `tree -I` pattern list.
    # tree's matching is simpler than full glob; we aim for practical excludes.
    p = _normalize_glob(glob_pat)
    if "|" in p:
        # Prevent breaking the tree expression; treat as literal by skipping.
        return ""

    # Convert ** to * (tree doesn't reliably support **)
    p = p.replace("**", "*")

    # If pattern looks like a directory recursion, include both dir and dir/*
    if p.endswith("/*"):
        base = p[:-2]
        return f"{base}|{base}/*"

    if p.endswith("/"):
        base = p.rstrip("/")
        return f"{base}|{base}/*"

    # If pattern ends with "/*" already handled; if ends with "*/" keep.
    if p.endswith("/*"):
        return p

    # For "data/*" style, keep as-is
    return p


def _tree_extra_ignore_expr(cfg: CodebookConfig) -> str:
    pats: list[str] = []
    for g in cfg.ignore_globs_extra:
        t = _glob_to_tree_pattern(g)
        if t:
            pats.append(t)
    # Flatten "a|b" entries by splitting and rejoining
    flat: list[str] = []
    for item in pats:
        flat.extend([x for x in item.split("|") if x])
    # De-dup while preserving order
    seen: set[str] = set()
    out: list[str] = []
    for x in flat:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return "|".join(out)


def _should_exclude(rel_path: Path, *, exclude_globs: set[str]) -> bool:
    # Avoid self-inclusion recursion
    if rel_path.parts[:2] == ("docs", "artifacts"):
        return True

    if any(part in BUILTIN_EXCLUDE_COMPONENTS for part in rel_path.parts):
        return True

    p = rel_path.as_posix()
    return any(fnmatch(p, pat) for pat in exclude_globs)


def _is_binary_or_too_large(abs_path: Path, *, max_bytes: int) -> bool:
    try:
        size = abs_path.stat().st_size
    except OSError:
        return True

    if size > max_bytes:
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


def _tree_output(cfg: CodebookConfig) -> str:
    # Preferred: tree via the skill's script (respects .gitignore).
    if shutil.which("tree") and TREE_SCRIPT.exists():
        try:
            extra_expr = _tree_extra_ignore_expr(cfg)
            env = {"IGNORE_PATTERN_EXTRA": extra_expr} if extra_expr else None
            return _run(["bash", str(TREE_SCRIPT)], cwd=_REPO_ROOT, env=env)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # Fallback: use find (best-effort). Note: may not replicate .gitignore perfectly.
    return _find_output(cfg)


def _find_output(cfg: CodebookConfig) -> str:
    exclude_globs = _merge_exclude_globs(cfg)

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
                if _should_exclude(rel_path, exclude_globs=exclude_globs):
                    continue
                lines.append(f"./{rel}")
            return "\n".join(sorted(set(lines)))
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    collected: list[str] = ["./"]
    for root, dirs, files in os.walk(_REPO_ROOT):
        rel_root = Path(root).resolve().relative_to(_REPO_ROOT)

        kept_dirs: list[str] = []
        for d in dirs:
            rel_dir = (rel_root / d) if rel_root != Path(".") else Path(d)
            if _should_exclude(rel_dir, exclude_globs=exclude_globs):
                continue
            kept_dirs.append(d)
        dirs[:] = kept_dirs

        for f in files:
            rel_file = (rel_root / f) if rel_root != Path(".") else Path(f)
            if _should_exclude(rel_file, exclude_globs=exclude_globs):
                continue
            collected.append(f"./{rel_file.as_posix()}")

    return "\n".join(sorted(set(collected)))


def _file_list(cfg: CodebookConfig) -> list[Path]:
    exclude_globs = _merge_exclude_globs(cfg)

    raw = _run(["git", "ls-files", "-co", "--exclude-standard"], cwd=_REPO_ROOT)
    files = [Path(p) for p in raw.splitlines() if p.strip()]

    filtered: list[Path] = []
    for rel in files:
        if _should_exclude(rel, exclude_globs=exclude_globs):
            continue
        abs_path = _REPO_ROOT / rel
        if not abs_path.exists() or abs_path.is_dir():
            continue
        filtered.append(rel)

    return sorted(filtered, key=lambda x: x.as_posix())


def _one_line_description(rel_path: Path, *, cfg: CodebookConfig) -> str:
    abs_path = _REPO_ROOT / rel_path

    if cfg.skip_empty_files and _is_effectively_empty(abs_path):
        return "skipped (empty file)"

    if _is_binary_or_too_large(abs_path, max_bytes=cfg.max_text_file_bytes):
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


def _render_descriptions(paths: list[Path], *, cfg: CodebookConfig) -> str:
    lines = [f"- `{p.as_posix()}`: {_one_line_description(p, cfg=cfg)}" for p in paths]
    return "\n".join(lines)


def _render_code_blocks(paths: list[Path], *, cfg: CodebookConfig) -> str:
    blocks: list[str] = []

    for rel in paths:
        abs_path = _REPO_ROOT / rel

        if cfg.skip_empty_files and _is_effectively_empty(abs_path):
            continue

        if _is_binary_or_too_large(abs_path, max_bytes=cfg.max_text_file_bytes):
            blocks.append(f"- `{rel.as_posix()}`: skipped (binary or too large)\n")
            continue

        content = abs_path.read_text(encoding="utf-8")
        fence = f"```{rel.as_posix()}".rstrip()
        blocks.append(f"{fence}\n{content}\n```\n")

    return "\n".join(blocks).rstrip()


def _apply_config_mutations(cfg: CodebookConfig, args: argparse.Namespace) -> CodebookConfig:
    ignore = list(cfg.ignore_globs_extra)

    if args.add_ignore:
        for p in args.add_ignore:
            p = _normalize_glob(p)
            if p and p not in ignore:
                ignore.append(p)

    if args.remove_ignore:
        remove = {_normalize_glob(p) for p in args.remove_ignore}
        ignore = [p for p in ignore if p not in remove]

    max_bytes = cfg.max_text_file_bytes
    if args.max_text_file_bytes is not None:
        max_bytes = int(args.max_text_file_bytes)

    skip_empty = cfg.skip_empty_files
    if args.skip_empty_files is not None:
        skip_empty = bool(args.skip_empty_files)

    return CodebookConfig(
        version=cfg.version,
        ignore_globs_extra=ignore,
        skip_empty_files=skip_empty,
        max_text_file_bytes=max_bytes,
        notes=cfg.notes,
    )


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
    parser = argparse.ArgumentParser(description="Generate a versioned repository codebook artifact.")
    parser.add_argument("--add-ignore", action="append", default=None, help="Add an extra ignore glob (persistent).")
    parser.add_argument(
        "--remove-ignore", action="append", default=None, help="Remove an ignore glob from the persistent config."
    )
    parser.add_argument("--max-text-file-bytes", type=int, default=None, help="Override max text file size (bytes).")
    parser.add_argument(
        "--skip-empty-files",
        type=lambda x: x.lower() in {"1", "true", "yes", "y"},
        default=None,
        help="Override skipping empty/whitespace-only files (true/false).",
    )
    parser.add_argument(
        "--config-only",
        action="store_true",
        help="Only update/save config (do not generate the codebook).",
    )
    args = parser.parse_args()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    cfg = _load_config()
    cfg2 = _apply_config_mutations(cfg, args)

    if cfg2 != cfg:
        _save_config(cfg2)

    if args.config_only:
        return 0

    existing = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else None
    version = _bump_patch_version(existing)

    info = _project_info()
    tree_out = _tree_output(cfg2)
    paths = _file_list(cfg2)

    tmpl = TEMPLATE_PATH.read_text(encoding="utf-8")
    out = tmpl
    out = out.replace("__PROJECT_NAME__", info.name)
    out = out.replace("__PROJECT_DESCRIPTION_BULLETS__", "\n".join(info.description_bullets))
    out = out.replace("__CODEBOOK_VERSION__", version)
    out = out.replace("__TREE_OUTPUT__", tree_out)
    out = out.replace("__FILE_DESCRIPTIONS__", _render_descriptions(paths, cfg=cfg2))
    out = out.replace("__FILE_CODE_BLOCKS__", _render_code_blocks(paths, cfg=cfg2))

    OUTPUT_PATH.write_text(out + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
