# 🧠 Fullstack ML/AI Agent Skills

A **multi-skill repository** for **Codex CLI** and **Claude Code**: reusable, task-focused “agent skills” that package **instructions**, **optional scripts**, and **supporting assets** so an agent can follow repeatable workflows reliably. :contentReference[oaicite:0]{index=0}

---

## 🧱 Skill structure

This repository is organized as a **skill catalog** under `./skills/`, where each folder is a standalone skill:

```text
fullstack-ml-ai-agent-skills/
└─ skills/
   ├─ fastapi-architect/
   │  ├─ SKILL.md
   │  ├─ scripts/
   │  ├─ assets/         
   │  └─ references/     
   ├─ python-best-practices/
   │  └─ SKILL.md
   ├─ mlops-blueprints/
   │  └─ SKILL.md
   └─ llm-evals-toolkit/
      └─ SKILL.md
````

---

## ✅ Use when

* You want **repeatable engineering workflows** (scaffolding, auditing, refactoring, designing architectures).
* You need **consistent conventions** across projects/teams (naming, structure, patterns).
* You want the agent to apply **domain-specific expertise** (FastAPI structure, MLOps patterns, LLM evaluation routines).
* You need reusable **templates + scripts** that keep instructions concise and outcomes consistent.

---

## 🗂️ Categories covered

* **Backend / APIs** (FastAPI, service architecture, versioning, conventions)
* **Python engineering** (project structure, style, maintainability)
* **MLOps** (blueprints, operational patterns, deployment-oriented practices)
* **LLM evaluation** (evaluation workflows, judge patterns, experiment hygiene)

---

## ✨ Features

* **Multi-skill catalog**: one repo, many independent skills
* **Open standard** skill format for portability across tools
* **Progressive disclosure**: instructions + references/assets/scripts loaded only when needed (tool-dependent)
* **Composable**: skills can be used alone or combined (e.g., FastAPI + Python best practices)

---

## ⚙️ How it works

1. Each skill exposes a **name + description** via `SKILL.md` frontmatter so the agent can decide when to use it. 
2. The agent loads the **full instructions** from `SKILL.md` when the skill is invoked (explicitly or implicitly). 
3. If present, the agent can also leverage:

   * `references/` for deeper documentation
   * `assets/` for templates/resources
   * `scripts/` for executable helpers (depending on tool/runtime permissions) 

---

## 📦 Installation (Codex CLI + Claude Code)

> This repo is a **catalog**. You typically “install” a skill by placing (or symlinking) the **skill folder** where your tool loads skills.

### Codex CLI (user-scoped)

Codex supports user skills under `~/.codex/skills` and supports symlinked skill folders. 

```bash
mkdir -p ~/.codex/skills
```

```bash
git clone https://github.com/Y4rd13/fullstack-ml-ai-agent-skills.git ~/my-skills/fullstack-ml-ai-agent-skills
```

```bash
ln -s ~/my-skills/fullstack-ml-ai-agent-skills/skills/fastapi-architect ~/.codex/skills/fastapi-architect

ln -s ~/my-skills/fullstack-ml-ai-agent-skills/skills/python-best-practices ~/.codex/skills/python-best-practices

ln -s ~/my-skills/fullstack-ml-ai-agent-skills/skills/mlops-blueprints ~/.codex/skills/mlops-blueprints

ln -s ~/my-skills/fullstack-ml-ai-agent-skills/skills/llm-evals-toolkit ~/.codex/skills/llm-evals-toolkit
```

### Claude Code (personal-scoped)

Claude Code supports personal skills under `~/.claude/skills/<skill-name>/SKILL.md` and also discovers nested `.claude/skills` directories in projects/monorepos.

```bash
mkdir -p ~/.claude/skills
```

```bash
ln -s ~/my-skills/fullstack-ml-ai-agent-skills/skills/fastapi-architect ~/.claude/skills/fastapi-architect

ln -s ~/my-skills/fullstack-ml-ai-agent-skills/skills/python-best-practices ~/.claude/skills/python-best-practices

ln -s ~/my-skills/fullstack-ml-ai-agent-skills/skills/mlops-blueprints ~/.claude/skills/mlops-blueprints

ln -s ~/my-skills/fullstack-ml-ai-agent-skills/skills/llm-evals-toolkit ~/.claude/skills/llm-evals-toolkit
```

---

## ▶️ Usage

### Codex CLI

* Use `/skills` or type `$` to select a skill for explicit invocation. 

Examples:

```text
$fastapi-architect scaffold a new FastAPI service with src/ layout and versioned routers
```

```text
$python-best-practices review this module for maintainability and propose refactors
```

### Claude Code

* Invoke skills directly as slash commands: `/skill-name ...` 

Examples:

```text
/fastapi-architect audit this FastAPI project and propose an objective refactor plan
```

```text
/llm-evals-toolkit propose an eval plan for my RAG pipeline with metrics and test cases
```

---

## 🤝 Contributions

Contributions are welcome.

* Add improvements as small, focused PRs
* Keep skills self-contained (each under `skills/<skill-name>/`)
* Prefer clear instructions in `SKILL.md` and put bulk material in `references/` or `assets/`

---

## 📄 License

MIT — see `LICENSE`.