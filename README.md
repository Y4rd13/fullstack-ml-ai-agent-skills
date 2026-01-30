# Fullstack ML/AI Agent Skills

A multi-skill repository for Codex CLI and Claude Code. Each skill is a self-contained, task-focused workflow that packages instructions plus optional scripts/assets so agents can execute repeatable processes.

## Skills

- dead-code-audit: Evidence-first dead-code + dependency hygiene audit for Python repos with reviewable docs/audit/ artifacts.
- fastapi-architect: Scaffold, review, or refactor FastAPI services using uv, a src/ layout, versioned routers, and optional singleton clients.
- llm-evals-toolkit: Build LLM evaluation workflows and experiment hygiene guidance.
- minimal-tests-audit: Propose minimal, strictly-necessary tests with audit/progress files and an optional apply phase.
- mlops-blueprints: Generate MLOps blueprints and operational patterns for ML systems.
- python-best-practices: Apply production-grade Python standards for structure, typing, docs, tests, uv+taskipy+ruff tooling, CI gates, security, and performance.
- ralph-codex: Scaffold a Ralph-style autonomous agent loop adapted for OpenAI Codex CLI.
- repo-codebook-generator: Produce a repository codebook (structure, one-line file descriptions, and full source) while respecting .gitignore.

## Repository structure

Skills live under skills/<skill-name>/. Each skill is standalone and typically includes:

- SKILL.md (required)
- scripts/ (optional)
- assets/ (optional)
- references/ (optional)
- knowledge/ (optional)

## Requirements

- Python >= 3.12
- uv (recommended for running tasks)

## Development

- Lint (check):
  - uv run task lint
- Lint (fix):
  - uv run task lint_fix
- Format:
  - uv run task format

## Installation

This repo is a catalog. Install a skill by placing (or symlinking) the skill folder where your tool loads skills.

Codex CLI (user-scoped):

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/skills/fastapi-architect" ~/.codex/skills/fastapi-architect
```

Claude Code (personal-scoped):

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skills/fastapi-architect" ~/.claude/skills/fastapi-architect
```

Repeat for any other skills you want to install.

## Usage

Codex CLI (examples):

```text
$fastapi-architect scaffold a new FastAPI service with src/ layout and versioned routers
$python-best-practices review this module for maintainability and propose refactors
$ralph-codex scaffold a ralph loop into this repo
```

Claude Code (examples):

```text
/fastapi-architect audit this FastAPI project and propose an objective refactor plan
/llm-evals-toolkit propose an eval plan for my RAG pipeline with metrics and test cases
```

## Contributing

Small, focused PRs are welcome. Keep skills self-contained under skills/<skill-name>/.

## License

See LICENSE.
