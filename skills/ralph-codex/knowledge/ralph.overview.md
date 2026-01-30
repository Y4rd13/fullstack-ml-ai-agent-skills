# Ralph overview (upstream behavior)

Ralph is a long-running “fresh agent per iteration” loop.

**State lives in files + git:**
- `prd.json` is the task backlog (ordered by priority, `passes: false/true`)
- `progress.txt` is the durable memory (patterns + per-story log)
- git history preserves the actual code changes

**Each iteration:**
1) Read PRD + progress
2) Ensure correct branch
3) Pick next failing story (highest priority)
4) Implement *one* story
5) Run quality checks
6) Commit, mark story as passing, append progress
7) If all passing → output `<promise>COMPLETE</promise>`
