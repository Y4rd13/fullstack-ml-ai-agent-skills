# minimal-tests-audit (Codex Skill)

Proposes strictly-necessary unit tests with an audit (MD+JSON) under `docs/audit/`,
lets the user approve via `docs/audit/tests_progress.txt`, applies selected tests into `tests/`,
then runs uv tasks in optimal order.

## Outputs

- docs/audit/tests_audit.md
- docs/audit/tests_audit.json
- docs/audit/tests_progress.txt

## Usage (Codex)

- Run audit/proposal:
  - $minimal-tests-audit
- Approve tests:
  - edit docs/audit/tests_progress.txt (mark `Create?: x`)
- Apply:
  - $minimal-tests-audit apply from progress
