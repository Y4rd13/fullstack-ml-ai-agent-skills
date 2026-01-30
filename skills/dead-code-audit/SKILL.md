---
name: dead-code-audit
description: Exhaustively audit Python repos for dead code and dependency hygiene; use when you need evidence-backed removal candidates with docs/audit/ artifacts.
license: MIT
metadata:
  author: Y4rd13
  version: "1.0.0"
---

You are Codex CLI running locally in the user’s current repository.

SKILL INTENT

- This skill performs an evidence-first dead-code audit for Python repositories and writes a reviewable report.
- It also supports an optional “apply” phase where you remove ONLY items the user approves (via explicit IDs or by marking `x` in docs/audit/dead_code_progress.txt).

SKILL FORMAT NOTES

- This SKILL.md uses YAML front matter (`name`, `description`) as required by Codex skills. :contentReference[oaicite:1]{index=1}
- Codex injects only the skill’s name/description/path by default; the instruction body is injected only when explicitly invoked. :contentReference[oaicite:2]{index=2}

WHERE TO WRITE OUTPUTS (MANDATORY)
Write ALL audit artifacts under:

- docs/audit/audit.md (canonical, detailed)
- docs/audit/dead_code_audit.md (human summary)
- docs/audit/dead_code_audit.json (machine)
- docs/audit/dead_code_progress.txt (user approval workflow)

DEFAULT EXCLUSIONS
Avoid scanning large/binary/data folders unless necessary:

- Ignore: db/, out/, .venv/, dist/, build/, node_modules/, docs/ (except docs/audit/), **/\*.pdf, **/\*.png, etc.

UV REQUIREMENT

- The repo is expected to be managed with uv (pyproject.toml + uv.lock).
- Prefer running tests/coverage via uv tasks defined in pyproject.
- If uv is not available, do NOT “fake it”; instead, generate the static audit and clearly note what could not be run.

== MODES ==
A) AUDIT MODE (default)
B) APPLY MODE (explicit)

---

## NEW: REPO TYPE DETECTION (PUBLISHED LIBRARY HEURISTIC)

Goal: avoid breaking public API surfaces in publishable/distributed libraries.

Define a boolean: PUBLISHED_LIBRARY

Set PUBLISHED_LIBRARY=true if at least TWO of the following signals are present:

1. pyproject.toml has [project] with name AND (version OR dynamic version) AND a build-system backend (setuptools/hatchling/poetry/pdm).
2. README mentions "pip install" OR "PyPI" OR contains a pypi.org link.
3. CI/workflows mention publish/release (e.g., "pypi", "twine", "publish", "release", "build wheel", "sdist").
4. Project metadata suggests distribution: classifiers, keywords, project.urls, license fields, long_description/readme, etc.

If uncertain, default to PUBLISHED_LIBRARY=true (conservative).

---

## NEW: API SURFACE SAFETY RULE (PROMOTE RE-EXPORTS)

If PUBLISHED_LIBRARY=true:

- ANY finding that is:
  a) defined in any _**init**.py (package or subpackage), OR
  b) only referenced via _**init**.py re-export (e.g., imported into **init**.py, listed in **all**, star exports),
  MUST be classified as “Needs manual confirmation” (NOT “Safe removal”), even if it has zero in-repo call sites.
- Rationale: it may be public API used by downstream consumers, not by this repo itself.
- In the audit.md, explicitly note this rule in Methodology and in the per-item Recommendation include:
  "Confirm downstream usage: search dependent repos / pip consumers / internal packages before removal."

If PUBLISHED_LIBRARY=false:

- You may classify re-export-only items as dead only with exceptionally strong evidence (still prefer “manual confirmation”).

---

## AUDIT MODE — REQUIRED WORKFLOW (execute fully)

0. Prep

- Ensure docs/audit exists (create if needed).
- Read README.md and pyproject.toml to find entrypoints, tasks, scripts, console scripts.
- Detect code roots dynamically (do not assume src/guardrail):
  - likely roots: src/, app/, packages/, services/, scripts/, tests/
- Run REPO TYPE DETECTION and set PUBLISHED_LIBRARY accordingly (document it in audit.md).

1. Inventory

- Enumerate top-level python packages/modules (and key subpackages).
- Identify public API boundaries:
  - **init**.py re-exports
  - **all**
  - registries / plugin discovery
- Identify leaf modules likely unused.

2. Evidence-first reference mapping

- Use ripgrep to find imports/usages across the repo roots.
- For each candidate file/symbol:
  - direct references (SymbolName)
  - module imports (import x / from x import y)
  - dynamic usage signals: importlib, getattr, registry patterns, plugin discovery, **all**, side-effect imports
- Apply the API SURFACE SAFETY RULE when PUBLISHED_LIBRARY=true.

3. Runtime signals (uv)

- Discover the correct uv commands from pyproject (tasks).
- Run the test suite with uv (and coverage if available).
- Capture pass/fail and note low-coverage modules.

4. Dependency hygiene

- Cross-check pyproject dependencies vs in-repo imports (src/scripts/tests).
- Mark “definitely unused” vs “maybe unused (plugins/extras)” depending on evidence.

5. Write artifacts (MANDATORY)
   Create:
1. docs/audit/audit.md (canonical, strict format)
1. docs/audit/dead_code_audit.md (summary format)
1. docs/audit/dead_code_audit.json (schema below)

After generating docs/audit/dead_code_audit.json, run:

- uv run python <SKILL_DIR>/scripts/update_dead_code_progress.py --audit-json docs/audit/dead_code_audit.json --progress docs/audit/dead_code_progress.txt

Where:

- <SKILL_DIR> = the directory containing this SKILL.md (resolve via the skill path available in context; use an absolute path when running the command).

6. Acceptance criteria

- No “dead” claim without evidence.
- Every candidate includes: confidence + risk + exact evidence.
- No production-code modifications in audit mode.

---

## CANONICAL AUDIT DOC — docs/audit/audit.md (REQUIRED FORMAT)

- Title: "Dead Code & Repo Hygiene Audit"
- Header block (bullets):
  - Repo: <repo name or path>
  - Generated at: <ISO datetime>
  - Scope: <detected roots e.g., src/, scripts/, tests/, pyproject.toml>
  - Exclusions: <folders>
  - How to reproduce: exact commands executed (copy-paste)

- Section 1: Methodology
- Section 2: Findings Summary (table)
  Categories:
  - Safe removal (high confidence)
  - Needs manual confirmation
  - Dependency findings
  - Not dead but problematic

- Section 3: Safe Removal Candidates (table columns)
  ID | Item | Type | Location | Why it looks dead | Evidence (commands + results snippets) | Confidence (0-1) | Risk (L/M/H) | Recommendation

- Section 4: Needs Manual Confirmation (same table)
  Recommendations MUST include “how to confirm”.

- Section 5: Dependency Findings (table)
  Dependency | Declared in | Observed imports (paths) | Confidence | Recommendation

- Section 6: Not Dead, But Problematic
- Section 7: Appendix — Evidence Log
  - Commands executed
  - Key rg searches
  - Test output summary

FEW-SHOT SAMPLE — INCLUDE THIS BLOCK VERBATIM, then fill real findings below it
Example finding row (illustrative only; replace with real ones after the example block):
| ID | Item | Type | Location | Why it looks dead | Evidence (commands + results snippets) | Confidence (0-1) | Risk (L/M/H) | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DR-001 | path/to/module.py:some_helper() | function | path/to/module.py | No imports/call sites found in src/scripts/tests; not referenced by registry | rg -n "some_helper" src scripts tests -> (no matches); rg -n "from package.module" src scripts tests -> (no matches) | 0.92 | Low | Mark for removal after confirming no dynamic import; run full tests + grep in CI |

---

## SUMMARY DOC — docs/audit/dead_code_audit.md (REQUIRED FORMAT)

A) Executive summary (5–10 bullets)
B) Safe removal candidates (table)
C) Needs manual confirmation (table)
D) Not dead, but problematic (bullets)
E) Dependency findings (table)
F) Suggested follow-up plan (checklist)

---

## JSON — docs/audit/dead_code_audit.json (REQUIRED SHAPE)

{
"generated_at": "...",
"repo_roots": ["..."],
"safe_removal_candidates": [
{
"id": "DR-001",
"type": "file|module|class|function|constant|dependency",
"name": "...",
"path": "...",
"confidence": 0.0,
"evidence": ["..."],
"risk": "low|medium|high",
"recommendation": "..."
}
],
"needs_manual_confirmation": [
{
"id": "MC-001",
"type": "...",
"name": "...",
"path": "...",
"confidence": 0.0,
"evidence": ["..."],
"risk": "low|medium|high",
"recommendation": "..."
}
],
"dependency_findings": [
{
"id": "DEP-001",
"type": "dependency",
"name": "...",
"path": "pyproject.toml",
"confidence": 0.0,
"evidence": ["..."],
"risk": "low|medium|high",
"recommendation": "..."
}
],
"notes": ["..."]
}

---

## APPLY MODE — REQUIRED WORKFLOW (only when explicitly asked)

INPUTS USER MAY PROVIDE

1. Inline:
   Remove: DR-001, DR-002
2. Inline with extra checks:
   Remove:
   - MC-001: rg -n "lorem_ipsum" .
   - Dependency httpx: rg -n "httpx" .
     More instructions...
3. Progress file:
   - docs/audit/dead_code_progress.txt (user marks `x` in Remove?)

RULES

- Remove ONLY what the user approved.
- Before deleting each item:
  - Re-run the evidence checks (rg + entrypoint review) and confirm no dynamic usage.
  - If uncertainty remains, stop and ask for explicit confirmation (or leave it).
- After changes:
  - Run uv-based lint/test tasks if present (discover from pyproject).
  - Summarize changes + show what was removed + where.
- Never delete files outside the repo or touch large data artifacts.

When user says:

- “$dead-code-audit apply from progress”
  You must:
- Read docs/audit/dead_code_progress.txt
- Collect items with Remove? == 'x' (case-insensitive)
- Apply removals safely and update:
  - docs/audit/audit.md (add an “Applied changes” section)
  - docs/audit/dead_code_audit.json (mark removed items with a note or move to a new field if you prefer)
  - docs/audit/dead_code_progress.txt (preserve Notes; optionally mark as DONE)

NOW START when invoked.
