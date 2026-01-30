# ralph-codex

Scaffolds a “Ralph Wiggum”-style autonomous loop for **OpenAI Codex CLI**:

- `ralph.sh` runs `codex exec` repeatedly (one iteration = one fresh agent session).
- “Memory” persists via `progress.txt`, `prd.json`, and git history.
- Exactly **one user story per iteration** (highest priority where `passes=false`).

---

## What this installs into a target repo

It creates (or overwrites only when you choose) the following at the **repo root**:

- `ralph.sh` — the long-running loop runner (Codex by default; optional amp/claude compatibility)
- `prompt.md` — instructions used by each Codex iteration
- `AGENTS.md` — durable repo conventions and Ralph overview
- `progress.txt` — append-only progress + “Codebase Patterns” at the top
- `prd.json.example` — example PRD JSON format
- `archive/` — previous runs archived here on branch change
- `.codex/rules/ralph.rules` — safety rules for dangerous commands

Then you copy `prd.json.example` → `prd.json` and edit the stories.

---

## Codex “skill locations” (official)

Codex loads skills from:

- **Repo-scoped:** `.codex/skills/<skill-name>/`
- **User-scoped:** `~/.codex/skills/<skill-name>/`

Your repository is a skills catalog under `skills/`. To make Codex see this skill, use a symlink.

### Option A — User-scoped (recommended for a catalog repo)

From the **skills catalog repo** root:

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/skills/ralph-codex" ~/.codex/skills/ralph-codex
```

### Option B — Repo-scoped (for a single project repo)

Copy the folder into:

```bash
mkdir -p .codex/skills
cp -R path/to/skills/ralph-codex .codex/skills/ralph-codex
```

---

## Install Ralph into a target repo

Go to the **target repo** (the repo you want Ralph to operate on), then run:

```bash
uv run ~/.codex/skills/ralph-codex/scripts/scaffold_ralph_codex.py
```

If you installed repo-scoped instead:

```bash
uv run .codex/skills/ralph-codex/scripts/scaffold_ralph_codex.py
```

This will scaffold the Ralph loop files into that repo root.

---

## Configure: create `prd.json`

In the target repo:

```bash
cp prd.json.example prd.json
# edit prd.json to your feature stories
```

**Rule #1:** each story must be small enough to complete in one iteration.

---

## Run

In the target repo:

```bash
chmod +x ./ralph.sh
./ralph.sh 10
```

### Optional flags

- Choose tool:
  - `./ralph.sh --tool codex 10`
  - `./ralph.sh --tool amp 10`
  - `./ralph.sh --tool claude 10`
- Choose mode:
  - `./ralph.sh --mode full-auto 10` (default, safer)
  - `./ralph.sh --mode yolo 10` (dangerous: bypass approvals and sandbox)

---

## Notes on safety

- Default mode uses Codex `--full-auto` (autonomous, but still safer defaults).
- YOLO mode exists, but it is intentionally not the default.
- `.codex/rules/ralph.rules` blocks obvious dangerous commands (e.g., `rm`, `sudo`, `ssh`) and prompts for network fetches.

---

## What “done” looks like

Ralph exits successfully when the agent outputs:

```xml
<promise>COMPLETE</promise>
```

This should only happen when **all** stories in `prd.json` have `passes: true`.
