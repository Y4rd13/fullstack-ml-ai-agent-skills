#!/usr/bin/env python3
"""
Scaffold Ralph loop files for Codex CLI into a target repository.

This script copies templates from this skill into the repository root:
- ralph.sh
- prompt.md
- AGENTS.md
- progress.txt
- prd.json.example
- .codex/rules/ralph.rules

Usage:
  python3 scaffold_ralph_codex.py
  python3 scaffold_ralph_codex.py --repo-root /path/to/repo
  python3 scaffold_ralph_codex.py --force

Notes:
- By default, existing files are NOT overwritten (safe).
- Use --force to overwrite scaffolded files.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import logging
import stat
from pathlib import Path


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str, force: bool) -> bool:
    """Write content to path. Returns True if written, False if skipped."""
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def _make_executable(path: Path) -> None:
    try:
        st = path.stat()
        path.chmod(st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError:
        pass


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="Scaffold Ralph loop files for Codex CLI.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root where files will be scaffolded (default: current working directory).",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing scaffolded files.")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be written, but do not write files.")
    args = parser.parse_args()

    repo_root: Path = args.repo_root.resolve()
    force: bool = args.force
    dry_run: bool = args.dry_run

    script_dir = Path(__file__).resolve().parent
    template_dir = (script_dir.parent / "assets" / "templates").resolve()

    templates = {
        "ralph.sh.tmpl": repo_root / "ralph.sh",
        "prompt.md.tmpl": repo_root / "prompt.md",
        "CODEX.md.tmpl": repo_root / "CODEX.md",
        "AGENTS.md.tmpl": repo_root / "AGENTS.md",
        "progress.txt.tmpl": repo_root / "progress.txt",
        "prd.json.example.tmpl": repo_root / "prd.json.example",
        "ralph.rules.tmpl": repo_root / ".codex" / "rules" / "ralph.rules",
    }

    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")

    started_at = _dt.datetime.now().isoformat(timespec="seconds")

    written: list[str] = []
    skipped: list[str] = []

    if not dry_run:
        (repo_root / "archive").mkdir(parents=True, exist_ok=True)

    for tmpl_name, dest_path in templates.items():
        tmpl_path = template_dir / tmpl_name
        if not tmpl_path.exists():
            raise FileNotFoundError(f"Missing template: {tmpl_path}")

        content = _read_text(tmpl_path)
        if tmpl_name == "progress.txt.tmpl":
            content = content.replace("{{STARTED_AT}}", started_at)

        if dry_run:
            logger.info("[DRY RUN] Would write: %s", dest_path)
            continue

        did_write = _write_text(dest_path, content, force=force)
        if did_write:
            written.append(str(dest_path))
        else:
            skipped.append(str(dest_path))

        if dest_path.name == "ralph.sh" and did_write:
            _make_executable(dest_path)

    if not dry_run:
        logger.info("\nRalph scaffold complete.")
        if written:
            logger.info("Written:")
            for p in written:
                logger.info("  - %s", p)
        if skipped:
            logger.info("Skipped (already exists; use --force to overwrite):")
            for p in skipped:
                logger.info("  - %s", p)

        logger.info("\nNext steps:")
        logger.info("  1) Copy prd.json.example -> prd.json and edit stories.")
        logger.info("  2) Run: chmod +x ./ralph.sh && ./ralph.sh 10")
        logger.info("  3) Keep stories small: one story per iteration.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
