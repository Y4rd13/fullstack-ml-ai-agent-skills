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
# Skill paths (stable even when installed under ~/.codex/skills)
# --------------------------------------------------------------------------------------
_THIS_FILE = Path(__file__).resolve()
_SCRIPTS_DIR = _THIS_FILE.parent
_SKILL_ROOT = _SCRIPTS_DIR.parent  # repo-codebook-generator/


# --------------------------------------------------------------------------------------
# Template / scripts owned by the skill
# --------------------------------------------------------------------------------------
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
            notes="Add patterns under ignore_globs_extra to exclude more paths.",
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


def _normalize_glob(pat: str) -> str:
    pat = pat.strip()
    if pat.startswith("./"):
        pat = pat[2:]
    return pat


def _resolve_repo_root(repo_root_arg: str | None) -> Path:
    # Priority:
    # 1) CLI --repo-root
    # 2) env REPO_CODEBOOK_REPO_ROOT
    # 3) current working directory
    if repo_root_arg:
        return Path(repo_root_arg).expanduser().resolve()

    env = os.environ.get("REPO_CODEBOOK_REPO_ROOT")
    if env:
        return Path(env).expanduser().resolve()

    return Path.cwd().resolve()


def _paths_for_repo(repo_root: Path) -> tuple[Path, Path]:
    output_path = repo_root / "docs/artifacts/repo_codebook.md"
    config_path = repo_root / "docs/artifacts/repo_codebook.config.json"
    return output_path, config_path


def _load_config(config_path: Path) -> CodebookConfig:
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if not config_path.exists():
        cfg = CodebookConfig.default()
        _save_config(config_path, cfg)
        return cfg

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        cfg = CodebookConfig.default()
        _save_config(config_path, cfg)
        return cfg

    return CodebookConfig(
        version=int(data.get("version", 1)),
        ignore_globs_extra=list(data.get("ignore_globs_extra", [])),
        skip_empty_files=bool(data.get("skip_empty_files", True)),
        max_text_file_bytes=int(data.get("max_text_file_bytes", DEFAULT_MAX_TEXT_FILE_BYTES)),
        notes=data.get("notes"),
    )


def _save_config(config_path: Path, cfg: CodebookConfig) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
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


def _merge_exclude_globs(cfg: CodebookConfig) -> set[str]:
    extra = {_normalize_glob(p) for p in cfg.ignore_globs_extra if p and p.strip()}
    return set(BUILTIN_EXCLUDE_GLOBS) | extra


def _glob_to_tree_pattern(glob_pat: str) -> str:
    # Best-effort conversion from glob to `tree -I` expression.
    p = _normalize_glob(glob_pat)
    if "|" in p:
        return ""

    p = p.replace("**", "*")

    if p.endswith("/*"):
        base = p[:-2]
        return f"{base}|{base}/*"

    if p.endswith("/"):
        base = p.rstrip("/")
        return f"{base}|{base}/*"

    return p


def _tree_extra_ignore_expr(cfg: CodebookConfig) -> str:
    flat: list[str] = []
    for g in cfg.ignore_globs_extra:
        t = _glob_to_tree_pattern(g)
        if t:
            flat.extend([x for x in t.split("|") if x])

    seen: set[str] = set()
    out: list[str] = []
    for x in flat:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return "|".join(out)


def _should_exclude(rel_path: Path, *, exclude_globs: set[str]) -> bool:
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


def _project_info(repo_root: Path) -> ProjectInfo:
    repo_name = repo_root.name

    bullets: list[str] = []
    readme = repo_root / "README.md"
    if readme.exists():
        lines = [ln.strip() for ln in readme.read_text(encoding="utf-8", errors="ignore").splitlines()]
        for ln in lines:
            if ln and not ln.startswith("#") and len(bullets) < 3:
                bullets.append(f"- {ln[:120]}")

    if not bullets:
        bullets = ["- Repository codebase (generated codebook)."]

    return ProjectInfo(name=repo_name, description_bullets=bullets)


def _tree_output(repo_root: Path, cfg: CodebookConfig) -> str:
    # Preferred: tree via the skill's script (respects .gitignore).
    if shutil.which("tree") and TREE_SCRIPT.exists():
        try:
            extra_expr = _tree_extra_ignore_expr(cfg)
            env = {"IGNORE_PATTERN_EXTRA": extra_expr} if extra_expr else None
            return _run(["bash", str(TREE_SCRIPT)], cwd=repo_root, env=env)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    return _find_output(repo_root, cfg)


def _find_output(repo_root: Path, cfg: CodebookConfig) -> str:
    exclude_globs = _merge_exclude_globs(cfg)

    if shutil.which("find"):
        try:
            raw = _run(["find", ".", "-print"], cwd=repo_root)
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
    for root, dirs, files in os.walk(repo_root):
        rel_root = Path(root).resolve().relative_to(repo_root)

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


def _file_list(repo_root: Path, cfg: CodebookConfig) -> list[Path]:
    exclude_globs = _merge_exclude_globs(cfg)

    raw = _run(["git", "ls-files", "-co", "--exclude-standard"], cwd=repo_root)
    files = [Path(p) for p in raw.splitlines() if p.strip()]

    filtered: list[Path] = []
    for rel in files:
        if _should_exclude(rel, exclude_globs=exclude_globs):
            continue
        abs_path = repo_root / rel
        if not abs_path.exists() or abs_path.is_dir():
            continue
        filtered.append(rel)

    return sorted(filtered, key=lambda x: x.as_posix())


def _one_line_description(repo_root: Path, rel_path: Path, *, cfg: CodebookConfig) -> str:
    abs_path = repo_root / rel_path

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


def _render_descriptions(repo_root: Path, paths: list[Path], *, cfg: CodebookConfig) -> str:
    lines = [f"- `{p.as_posix()}`: {_one_line_description(repo_root, p, cfg=cfg)}" for p in paths]
    return "\n".join(lines)


def _render_code_blocks(repo_root: Path, paths: list[Path], *, cfg: CodebookConfig) -> str:
    blocks: list[str] = []

    for rel in paths:
        abs_path = repo_root / rel

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


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a versioned repository codebook artifact.")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root to document. Defaults to $REPO_CODEBOOK_REPO_ROOT or current working directory.",
    )
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

    repo_root = _resolve_repo_root(args.repo_root)
    output_path, config_path = _paths_for_repo(repo_root)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    cfg = _load_config(config_path)
    cfg2 = _apply_config_mutations(cfg, args)
    if cfg2 != cfg:
        _save_config(config_path, cfg2)

    if args.config_only:
        return 0

    existing = output_path.read_text(encoding="utf-8") if output_path.exists() else None
    version = _bump_patch_version(existing)

    info = _project_info(repo_root)
    tree_out = _tree_output(repo_root, cfg2)
    paths = _file_list(repo_root, cfg2)

    tmpl = TEMPLATE_PATH.read_text(encoding="utf-8")
    out = tmpl
    out = out.replace("__PROJECT_NAME__", info.name)
    out = out.replace("__PROJECT_DESCRIPTION_BULLETS__", "\n".join(info.description_bullets))
    out = out.replace("__CODEBOOK_VERSION__", version)
    out = out.replace("__TREE_OUTPUT__", tree_out)
    out = out.replace("__FILE_DESCRIPTIONS__", _render_descriptions(repo_root, paths, cfg=cfg2))
    out = out.replace("__FILE_CODE_BLOCKS__", _render_code_blocks(repo_root, paths, cfg=cfg2))

    output_path.write_text(out + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
