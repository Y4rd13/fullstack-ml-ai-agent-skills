#!/usr/bin/env python3
"""
Generate / update docs/audit/tests_progress.txt from docs/audit/tests_audit.json.

- Preserves user choices:
  - Create? (x)
  - Notes

No external deps. Uses only stdlib.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HEADER = """# Minimal Tests Progress — User Selection

How to use:
1) Mark `x` in the `Create?` field for tests you approve to create under tests/.
2) Add context in `Notes` if needed (e.g., "Not needed for current scope").
3) Then ask Codex:
   - $minimal-tests-audit apply from progress
"""


@dataclass(frozen=True)
class SavedChoice:
    test_id: str
    create: str
    notes: str


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("tests_audit.json must be a JSON object")
    return data


def _parse_existing(progress_path: Path) -> dict[str, SavedChoice]:
    if not progress_path.exists():
        return {}

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

    saved: dict[str, SavedChoice] = {}
    for block in blocks:
        tid = pick(block, "ID").strip()
        if not tid:
            continue
        create = pick(block, "Create?").strip()
        notes = pick(block, "Notes")
        saved[tid] = SavedChoice(test_id=tid, create=create, notes=notes.rstrip())
    return saved


def _norm(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


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

    saved = _parse_existing(progress_path)

    out: list[str] = [HEADER.rstrip(), ""]
    for t in proposed:
        if not isinstance(t, dict):
            continue
        tid = _norm(t.get("id"))
        if not tid:
            raise ValueError("Every proposed test must have a stable 'id' (e.g., UT-001).")

        prev = saved.get(tid)
        create = prev.create if prev else ""
        notes = prev.notes if prev else ""

        targets = t.get("targets", [])
        if not isinstance(targets, list):
            targets = [targets]
        targets_str = _norm(", ".join(str(v) for v in targets))

        evidence = t.get("evidence", [])
        if not isinstance(evidence, list):
            evidence = [evidence]
        evidence_str = _norm("; ".join(str(v) for v in evidence))

        out.extend(
            [
                "---",
                f"ID: {tid}",
                f"Create?: {create}",
                f"File path: {_norm(t.get('file_path'))}",
                f"Scope: {_norm(t.get('scope'))}",
                f"Targets: {targets_str}",
                f"Rationale: {_norm(t.get('rationale'))}",
                f"Evidence: {evidence_str}",
                f"Notes: {notes}".rstrip(),
                "---",
                "",
            ]
        )

    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
