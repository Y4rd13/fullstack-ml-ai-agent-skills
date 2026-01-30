# ralph-codex (skill)

Port of the core Ralph loop from `snarktank/ralph` (MIT) adapted to run with **OpenAI Codex CLI** while reusing as much of the original structure/files as possible.

## What this scaffolds into your repo

Creates `./ralph/` with:

- `ralph.sh` (loop runner) — supports `--tool amp|CODEX|codex`
- `prompt.md` — the canonical Ralph instructions (used by Amp and Codex)
- `CODEX.md` — the canonical Ralph instructions for CODEX Code
- `prd.json.example` — example PRD format
- `progress.txt` — progress log
- `.codex/rules/ralph.rules` — suggested Codex rules for safer automation

## Usage

1. Scaffold into a repo:

```bash
uv run python skills/ralph-codex/scripts/scaffold_ralph_codex.py --repo-root .
```

2. Create `ralph/prd.json` (copy from `prd.json.example` and edit).

3. Run:

```bash
cd ralph
./ralph.sh --tool codex 20
```

### Optional: “YOLO” Codex mode

If you truly want zero approvals + no sandbox:

```bash
RALPH_CODEX_YOLO=1 ./ralph.sh --tool codex 20
```

## Notes on reuse

The following are carried over (or minimally edited) from upstream Ralph:

- `ralph.sh` structure, archiving behavior, loop semantics
- `prompt.md` task contract + progress conventions
- `CODEX.md` conventions
- `prd.json.example` schema

Only the Codex execution path (and small wording tweaks where tool-specific) are new.

## License / attribution

Upstream project: `snarktank/ralph` (MIT). This skill includes adapted copies of its templates and retains the MIT license spirit of reuse; keep attribution in downstream distributions.
