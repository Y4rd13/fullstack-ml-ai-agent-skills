# 🧠⚙️ Fullstack ML/AI Agent Skills

A **multi-skill repository** for **Codex CLI** and **Claude Code** covering **Fullstack + ML/AI Engineering** workflows (FastAPI, Python best practices, MLOps blueprints, evals, etc.).

- ✅ Skills follow the **Open Agent Skills** layout (`SKILL.md`, optional `scripts/`, `assets/`, `references/`)
- ✅ Designed for **repeatable, production-minded workflows**
- ✅ Repo-level CI validates skills + runs Ruff checks
- ✅ After any major change: **run `uv run task lint_fix`**

---

## 📦 What’s inside

Current skills (folder = skill name):

- `skills/fastapi-architect` — Scaffold/audit/refactor FastAPI services (uv + src/ layout + versioned routers)
- `skills/python-best-practices` — Python conventions, structure, and quality gates
- `skills/llm-evals-toolkit` — Evaluation helpers/patterns for LLM workflows
- `skills/mlops-blueprints` — MLOps templates and operational patterns

> Each skill is self-contained and has its own `SKILL.md` (with YAML frontmatter: `name`, `description`).

---

## 🗂️ Repository layout

```txt
fullstack-ml-ai-agent-skills/
├─ .github/workflows/ci.yml
├─ pyproject.toml
├─ uv.lock
├─ skills/
│  ├─ fastapi-architect/
│  │  ├─ SKILL.md
│  │  ├─ scripts/
│  │  ├─ assets/
│  │  └─ references/
│  ├─ python-best-practices/
│  ├─ llm-evals-toolkit/
│  └─ mlops-blueprints/
└─ LICENSE
````

---

## ✅ Install for Codex CLI

Codex loads skills from (among other places) your **user skill directory** `~/.codex/skills` and also supports **symlinked skill folders**.
Recommended approach: **clone this repo once** and **symlink individual skills** into `~/.codex/skills`.

### 1) Clone this repo (single source of truth)

```bash
mkdir -p ~/repos
cd ~/repos
git clone https://github.com/Y4rd13/fullstack-ml-ai-agent-skills.git
```

### 2) Symlink skills into Codex user skills folder

```bash
mkdir -p ~/.codex/skills
```

Symlink each skill you want:

```bash
ln -s ~/repos/fullstack-ml-ai-agent-skills/skills/fastapi-architect ~/.codex/skills/fastapi-architect
```

```bash
ln -s ~/repos/fullstack-ml-ai-agent-skills/skills/python-best-practices ~/.codex/skills/python-best-practices
```

```bash
ln -s ~/repos/fullstack-ml-ai-agent-skills/skills/llm-evals-toolkit ~/.codex/skills/llm-evals-toolkit
```

```bash
ln -s ~/repos/fullstack-ml-ai-agent-skills/skills/mlops-blueprints ~/.codex/skills/mlops-blueprints
```

### 3) Restart Codex CLI

Close and reopen your Codex CLI so it re-scans `~/.codex/skills`.

### 4) Use skills in Codex

* List/select skills: use `/skills` or start typing `$`
* Then invoke explicitly (example):

  * `$fastapi-architect scaffold a new service in ~/projects/my-api`
* Or just ask normally and Codex may apply the skill implicitly if it matches.

---

## ✅ Install for Claude Code

Claude Code discovers skills from `.claude/skills/` (including **nested discovery** in subdirectories for monorepos).
Recommended approach: **symlink individual skills** into `~/.claude/skills`.

### 1) Create Claude skills folder

```bash
mkdir -p ~/.claude/skills
```

### 2) Symlink skills into Claude

```bash
ln -s ~/repos/fullstack-ml-ai-agent-skills/skills/fastapi-architect ~/.claude/skills/fastapi-architect
```

```bash
ln -s ~/repos/fullstack-ml-ai-agent-skills/skills/python-best-practices ~/.claude/skills/python-best-practices
```

```bash
ln -s ~/repos/fullstack-ml-ai-agent-skills/skills/llm-evals-toolkit ~/.claude/skills/llm-evals-toolkit
```

```bash
ln -s ~/repos/fullstack-ml-ai-agent-skills/skills/mlops-blueprints ~/.claude/skills/mlops-blueprints
```

### 3) Restart Claude Code

Restart Claude Code so it re-discovers skills.

### 4) Use skills in Claude Code

* Invoke explicitly using the skill name (example):

  * `/fastapi-architect`
* Or ask Claude to apply the skill by name in your request.

---

## 🔁 Updating skills

Because you symlinked from a single repo clone:

```bash
cd ~/repos/fullstack-ml-ai-agent-skills
git pull
```

---

## 🧪 Development & quality gates (this repo)

This repo is intentionally minimal: it validates `SKILL.md` frontmatter and runs Ruff.

### Setup

```bash
uv sync
```

### Lint

```bash
uv run task lint
```

### Auto-fix (required after major changes)

```bash
uv run task lint_fix
```

---

## 🤝 Contributing

1. Create a feature branch
2. Keep diffs small and focused
3. If you add a new skill:

   * Add `skills/<skill-name>/SKILL.md` with frontmatter:

     * `name: <skill-name>`
     * `description: <what it does>`
   * Add optional `scripts/`, `assets/`, `references/` as needed
4. Run:

   * `uv run task lint_fix`
   * (then open a PR)

---

## 🛡️ License

See `LICENSE`.

---

## 🔗 References

* Codex Agent Skills docs: [https://developers.openai.com/codex/skills/](https://developers.openai.com/codex/skills/)
* Claude Code Skills docs: [https://code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)
* Open Agent Skills standard: [https://agentskills.io](https://agentskills.io)