---
name: ralph-codex
description: Scaffold a Ralph-style autonomous agent loop (from snarktank/ralph) into a repo, adapted for OpenAI Codex CLI. Triggers on: ralph codex, scaffold ralph, autonomous loop, prd.json loop.
user-invocable: true
---

# ralph-codex

## The Job

Scaffold the Ralph loop into an existing repo under `./ralph/`, including:

- `ralph.sh`, `prompt.md`, `CODEX.md`, `prd.json.example`, `progress.txt`
- `.codex/rules/ralph.rules`

## How to run

After scaffolding:

1. Copy `prd.json.example` → `prd.json` and fill in your stories.
2. Run:

```bash
cd ralph
./ralph.sh --tool codex 20
```

## Notes

- The loop is intentionally simple: one story per iteration, progress stored in `progress.txt`, completion signaled by `<promise>COMPLETE</promise>`.
- Codex is invoked in non-interactive mode via `codex exec --full-auto` (see `ralph.sh`).
