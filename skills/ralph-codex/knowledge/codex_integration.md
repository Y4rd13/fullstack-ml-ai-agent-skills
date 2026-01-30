# Codex integration notes

This skill runs Codex CLI using **non-interactive mode** (`codex exec`) so it can be driven from a bash loop.

Default mode:
- `codex exec --full-auto ...` (autonomous, but still respects sandbox/approvals depending on your config)

Optional mode:
- Set `RALPH_CODEX_YOLO=1` to run with `--yolo` (equivalent to bypass approvals and sandbox). Use only in a controlled environment.

Implementation detail:
- `ralph.sh` uses `--output-last-message` to capture the final agent message and detect `<promise>COMPLETE</promise>` reliably.
- Put repo-specific “allow/deny” rules in `.codex/rules/ralph.rules`.
