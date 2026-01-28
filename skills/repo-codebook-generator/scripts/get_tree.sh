#!/usr/bin/env bash
set -euo pipefail

# "Generated/build/runtime artifacts" + repo hygiene exclusions.
# Uses tree's wildcard/glob matching (-I) with patterns separated by '|'.
IGNORE_PATTERN=".git|__pycache__|*.pyc|.venv|.env|.env.*|*.egg-info|.coverage|htmlcov|.mypy_cache|.ruff_cache|.pytest_cache|uv.lock|.python-version|.dockerignore|.gitignore|tests|docs/artifacts|repo_codebook.md"

# -a: include dotfiles/dirs (we still exclude via IGNORE_PATTERN)
# --gitignore: respect .gitignore rules
# -I: additional excludes via wildcard pattern
# -n: no color/escape sequences
# --dirsfirst: nicer structure output
tree -a --dirsfirst -n --gitignore -I "${IGNORE_PATTERN}"