---
name: ralph-codex
description: Scaffold a Ralph-style autonomous loop for Codex CLI (ralph.sh + prd.json/progress + rules). Use when you want iterative 1-story-per-iteration coding.
user-invocable: true
---

# Ralph for Codex CLI

## The job

1. Scaffold Ralph files into the current repository root:

- `ralph.sh`
- `prompt.md`
- `AGENTS.md`
- `progress.txt`
- `prd.json.example`
- `.codex/rules/ralph.rules`

2. Do NOT implement product work. Only scaffold the loop and templates.

## How to run (after scaffolding)

- Copy `prd.json.example` to `prd.json` and edit it.
- Run:

```bash
chmod +x ./ralph.sh
./ralph.sh 10
```

## Implementation instructions (do this now)

Run the scaffold script from this skill:

```bash
uv run ~/.codex/skills/ralph-codex/scripts/scaffold_ralph_codex.py
```

If the user installed this skill repo-scoped instead, the path will be:

```bash
uv run .codex/skills/ralph-codex/scripts/scaffold_ralph_codex.py
```

## Output requirements

- Keep diffs minimal
- Do not add extra tooling
- Ensure generated files match templates exactly
