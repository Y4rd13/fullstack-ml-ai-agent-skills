#!/usr/bin/env python3
"""
Apply user-approved tests from docs/audit/tests_progress.txt into tests/ using
docs/audit/tests_audit.json as source of truth.

- Writes only tests marked with Create? == 'x' (case-insensitive).
- Updates docs/audit/tests_audit.json statuses:
  - proposed -> created
- Does NOT delete anything unless explicitly requested in the progress Notes (keep safe by default).
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("tests_audit.json must be a JSON object")
    return data


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _parse_progress(progress_path: Path) -> dict[str, str]:
    """
    Returns {test_id: create_flag} where create_flag is raw string (e.g., 'x').
    """
    text = progress_path.read_text(encoding="utf-8")
    blocks: list[list[str]] = []
    buf: list[str] = []
    for line in text.splitlines():
        if line.strip() == "---":
            if buf:
                blocks.append(buf)
                buf = []
            continue
        buf.append(line)
    if buf:
        blocks.append(buf)

    def pick(lines: list[str], key: str) -> str:
        pat = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.*)\s*$")
        for ln in lines:
            m = pat.match(ln)
            if m:
                return m.group(1)
        return ""

    out: dict[str, str] = {}
    for block in blocks:
        tid = pick(block, "ID").strip()
        if not tid:
            continue
        create = pick(block, "Create?").strip()
        out[tid] = create
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-json", required=True)
    ap.add_argument("--progress", required=True)
    args = ap.parse_args()

    audit_path = Path(args.audit_json)
    progress_path = Path(args.progress)

    payload = _read_json(audit_path)
    proposed = payload.get("proposed_tests", [])
    if not isinstance(proposed, list):
        raise ValueError("tests_audit.json must contain a 'proposed_tests' list")

    selections = _parse_progress(progress_path)
    approved_ids = {tid for tid, flag in selections.items() if flag.lower() == "x"}

    created: list[str] = []
    for t in proposed:
        if not isinstance(t, dict):
            continue
        tid = str(t.get("id", "")).strip()
        if tid not in approved_ids:
            continue

        file_path = Path(str(t.get("file_path", "")).strip())
        content = str(t.get("content", ""))

        if not file_path.as_posix().startswith("tests/"):
            raise ValueError(f"Refusing to write outside tests/: {file_path}")

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content.rstrip() + "\n", encoding="utf-8")

        # Update status
        t["status"] = "created"
        created.append(tid)

    payload.setdefault("applied", {})
    payload["applied"]["created_ids"] = created
    _write_json(audit_path, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
