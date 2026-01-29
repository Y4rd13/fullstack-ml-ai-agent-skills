This skill proposes minimal, strictly-necessary tests.
It must:

- detect code roots and entrypoints dynamically,
- run uv tasks in order (lint_fix -> test -> coverage),
- propose tests in docs/audit/ without creating them until user approval,
- keep an auditable JSON ledger including full test file contents.
