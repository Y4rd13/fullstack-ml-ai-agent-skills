"""
Generate / update docs/audit/dead_code_progress.txt from docs/audit/dead_code_audit.json.

- Preserves user decisions:
  - Remove? (x)
  - Notes
- Writes one block per audit item, delimited by '---', matching the skill template.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HEADER = """# Dead Code Progress — User Selection

How to use:
1) Mark `x` in the `Remove?` column for items you approve to delete.
2) Add context in `Notes` if needed (e.g., "external API - do not remove").
3) Then ask Codex:
   - $dead-code-audit apply from progress

Table columns:
- `Remove?`: put `x` to approve removal
- `Notes`: free text
"""


@dataclass(frozen=True)
class ProgressEntry:
    id: str
    category: str
    remove: str
    notes: str


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("dead_code_audit.json must be a JSON object")
    return data


def _norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _join_evidence(ev: Any) -> str:
    if not ev:
        return ""
    if isinstance(ev, list):
        return _norm_ws("; ".join(str(x) for x in ev))
    return _norm_ws(str(ev))


def _parse_progress(progress_path: Path) -> dict[str, ProgressEntry]:
    """
    Parse progress blocks delimited by lines containing only '---'.
    Expected lines: 'Key: value' (value may be empty).
    Only preserves: ID, Remove?, Notes.
    """
    if not progress_path.exists():
        return {}

    text = progress_path.read_text(encoding="utf-8")
    parts = []
    buf: list[str] = []
    for line in text.splitlines():
        if line.strip() == "---":
            if buf:
                parts.append(buf)
                buf = []
            continue
        buf.append(line)
    if buf:
        parts.append(buf)

    saved: dict[str, ProgressEntry] = {}

    def pick(lines: list[str], key: str) -> str:
        # Match 'Key: ...' (allow extra spaces)
        pat = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.*)\s*$")
        for ln in lines:
            m = pat.match(ln)
            if m:
                return m.group(1)
        return ""

    for block in parts:
        entry_id = pick(block, "ID")
        if not entry_id:
            continue
        remove = pick(block, "Remove?")
        notes = pick(block, "Notes")
        cat = pick(block, "Category")
        saved[entry_id.strip()] = ProgressEntry(
            id=entry_id.strip(),
            category=cat.strip(),
            remove=remove.strip(),
            notes=notes.rstrip(),
        )

    return saved


def _iter_items(payload: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    """
    Yields (category, item) for all lists in the audit JSON we care about.
    """
    mappings = [
        ("Safe removal (high confidence)", payload.get("safe_removal_candidates", [])),
        ("Needs manual confirmation", payload.get("needs_manual_confirmation", [])),
        ("Dependency findings", payload.get("dependency_findings", payload.get("dependency_findings", []))),
    ]

    for category, items in mappings:
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict):
                yield category, item


def _format_block(
    *,
    item_id: str,
    category: str,
    remove: str,
    name: str,
    typ: str,
    path: str,
    why: str,
    evidence: str,
    confidence: str,
    risk: str,
    recommendation: str,
    notes: str,
) -> str:
    # Keep everything single-line-ish where possible (evidence can be long).
    return "\n".join(
        [
            "---",
            f"ID: {item_id}",
            f"Category: {category}",
            f"Remove?: {remove}",
            f"Item: {_norm_ws(name)}",
            f"Type: {_norm_ws(typ)}",
            f"Location: {_norm_ws(path)}",
            f"Why it looks dead: {_norm_ws(why)}",
            f"Evidence (commands + results snippets): {_norm_ws(evidence)}",
            f"Confidence (0-1): {_norm_ws(confidence)}",
            f"Risk (L/M/H): {_norm_ws(risk)}",
            f"Recommendation: {_norm_ws(recommendation)}",
            f"Notes: {notes}".rstrip(),
            "---",
            "",
        ]
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-json", required=True, help="Path to docs/audit/dead_code_audit.json")
    ap.add_argument("--progress", required=True, help="Path to docs/audit/dead_code_progress.txt")
    args = ap.parse_args()

    audit_path = Path(args.audit_json)
    progress_path = Path(args.progress)

    payload = _read_json(audit_path)
    existing = _parse_progress(progress_path)

    out_blocks: list[str] = [HEADER.rstrip(), ""]

    for category, item in _iter_items(payload):
        item_id = str(item.get("id", "")).strip()
        if not item_id:
            # If IDs are missing, we cannot safely preserve user choices.
            # Keep deterministic fallback: skip, and force user to regenerate audit with IDs.
            raise ValueError(
                f"Missing 'id' for item in category '{category}'. "
                "Regenerate docs/audit/dead_code_audit.json with stable IDs (DR-xxx / MC-xxx / DEP-xxx)."
            )

        prev = existing.get(item_id)
        remove = prev.remove if prev else ""
        notes = prev.notes if prev else ""

        name = str(item.get("name", "")).strip()
        typ = str(item.get("type", "")).strip()
        path = str(item.get("path", "")).strip()
        confidence = str(item.get("confidence", "")).strip()
        risk = str(item.get("risk", "")).strip()
        recommendation = str(item.get("recommendation", "")).strip()

        # "why" is not mandatory in JSON; use heuristic fallback
        why = (
            str(item.get("why", "")).strip() or "Unreferenced in repo roots (per audit evidence); verify dynamic usage."
        )

        evidence = _join_evidence(item.get("evidence", []))

        out_blocks.append(
            _format_block(
                item_id=item_id,
                category=category,
                remove=remove,
                name=name or item_id,
                typ=typ,
                path=path,
                why=why,
                evidence=evidence,
                confidence=confidence,
                risk=risk,
                recommendation=recommendation,
                notes=notes,
            )
        )

    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.write_text("\n".join(out_blocks).rstrip() + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
