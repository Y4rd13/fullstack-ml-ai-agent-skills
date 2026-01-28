#!/usr/bin/env bash
set -euo pipefail

# "Generated/build/runtime artifacts" + repo hygiene exclusions.
# Uses tree's wildcard/glob matching (-I) with patterns separated by '|'.
IGNORE_PATTERN_BASE=".git|__pycache__|*.pyc|.venv|.env|.env.*|*.egg-info|.coverage|htmlcov|.mypy_cache|.ruff_cache|.pytest_cache|uv.lock|.python-version|.dockerignore|.gitignore|tests|docs/artifacts|repo_codebook.md|repo_codebook.config.json"

# Optional extra patterns (best-effort) passed by the Python generator:
# export IGNORE_PATTERN_EXTRA="data|data/*|out|out/*|*.pdf"
IGNORE_PATTERN="${IGNORE_PATTERN_BASE}"
if [[ -n "${IGNORE_PATTERN_EXTRA:-}" ]]; then
  IGNORE_PATTERN="${IGNORE_PATTERN}|${IGNORE_PATTERN_EXTRA}"
fi

# -a: include dotfiles/dirs (we still exclude via IGNORE_PATTERN)
# --gitignore: respect .gitignore rules
# -I: additional excludes via wildcard pattern
# -n: no color/escape sequences
# --dirsfirst: nicer structure output
tree -a --dirsfirst -n --gitignore -I "${IGNORE_PATTERN}"
