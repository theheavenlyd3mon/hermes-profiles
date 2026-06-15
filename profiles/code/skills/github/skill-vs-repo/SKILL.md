---
name: skill-vs-repo
description: Distinguish Hermes skills from regular GitHub repos and know how to install each correctly.
version: 1.0.0
---

# Skill vs. Repo — Installation Guide

## The Pitfall

Not every NousResearch (or other) repository is a Hermes **skill**. Many repos are standalone tools, libraries, or projects that have no `SKILL.md` file and will not appear in the Hermes skills section.

## How to Tell

| Feature | Hermes Skill | Regular Repo/Tool |
|---------|-------------|-------------------|
| Contains `SKILL.md` | ✅ Yes | ❌ No |
| Lives in `~/.hermes/skills/` | ✅ Yes | ❌ No |
| Loaded via `/skill name` | ✅ Yes | ❌ No |
| Installed via `git clone` into `~/.hermes/skills/<category>/<name>/` | ✅ Yes | N/A |
| Installed via `pip install` or run as a project | ❌ No | ✅ Yes |

## Example: `hermes-agent-self-evolution`

This repo is a **standalone Python tool**, not a skill. It optimizes Hermes skills but is not one itself.

**Correct installation:**
```bash
cd ~
git clone https://github.com/NousResearch/hermes-agent-self-evolution.git
cd hermes-agent-self-evolution
pip install -e ".[dev]"
export HERMES_AGENT_REPO=~/.hermes/hermes-agent
```

**If you want quick Hermes access**, create a wrapper skill manually:
```bash
mkdir -p ~/.hermes/skills/self-evolution
cat > ~/.hermes/skills/self-evolution/SKILL.md << 'EOF'
---
name: self-evolution
description: Wrapper for the hermes-agent-self-evolution tool
---

Run from ~/hermes-agent-self-evolution:

```bash
python -m evolution.skills.evolve_skill --skill <name> --iterations 10 --eval-source synthetic
```
EOF
```

## Quick Check

Before telling a user to load a repo as a skill, verify it contains a `SKILL.md` at its root or in a subfolder meant for skills.
