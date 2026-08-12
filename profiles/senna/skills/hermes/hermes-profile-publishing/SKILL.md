---
name: hermes-profile-publishing
description: Package Hermes profiles for public sharing — sanitize personal info, create per-profile READMEs, build repo structure, handle third-party skill licensing, and push to GitHub. Use when the user says "share my profiles", "publish profiles to GitHub", "make a profile repo", or "clean profiles for public use".
version: 1.1.0
author: Senna / Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [profiles, publishing, github, sharing, sanitization]
    related_skills: [hermes-profile-migration, hermes-soul-authoring, hermes-github-push, beginner-friendly-writeup]
---

# Hermes Profile Publishing

Package private Hermes profiles for public consumption on GitHub. Covers sanitization, repo structure, README generation, skill curation, and licensing checks.

## When to Use

- User wants to share profiles publicly on GitHub
- User says "publish my profiles", "make a profile repo", "share my setup"
- Creating a showcase repo of Hermes profiles for others to use
- After a profile migration, when the user wants to share the result

## Prerequisites

- Profiles already exist and work (`~/.hermes/profiles/<name>/`)
- SOUL.md files are finalized
- Skills are installed per profile

## Workflow

### Step 1: Plan the Scope

Ask or confirm:
- Which profiles to include (all? just domain profiles? just flagship?)
- Whether to include skills (adds significant size)
- Whether to include guides (research-profile-guide.md style walkthroughs)
- Public, private, or internal-only repo

### Step 1.5: Mirror an Existing Repo from Live Profiles

If the user already has a GitHub mirror and wants to refresh it from `~/.hermes/profiles/`:
- Copy only intended profiles into the repo.
- Strip runtime artifacts before committing.
- Identify local-only profiles (for example: `educate`) and treat them as specialized/non-portable.
- See `references/profile-repo-mirror.md` for the exact copy, cleanup, and verify sequence.

### Step 2: Create Repo Structure

```
<repo-name>/
  README.md                      — Landing page with quick start
  .gitignore                     — Exclude runtime artifacts
  guides/
    <profile>-profile-guide.md   — Optional detailed setup guides
  profiles/
    <name>/
      SOUL.md                    — Agent identity (sanitized)
      README.md                  — What it does, when to use, skills, config
      skills/                    — Domain-specific skills (sanitized)
```

### Step 3: Sanitize SOUL.md Files

**Write from scratch, don't clean.** SOUL.md files with personal references are faster to rewrite generically than to patch.

What to strip/replace:
- `Report→Senna` → `Report→Orchestrator`
- `Channel=#xxx` Discord references → remove or generalize
- `Workspace=dir:~/...` → remove or use `~/path`
- `workspace=~` → remove
- Hardware references (your GPU) → "your GPU" or remove
- Personal cron schedules → keep if generic, remove if personal
- `Board=main` → keep (it's a convention, not personal)
- PersRubric → keep (defines agent behavior, not personal data)

What to KEEP (these are the value):
- Personality rubric (PersRubric) — defines how the agent thinks
- Routing logic — the methodology
- Quality gates — the standards
- AVOID section — anti-patterns
- STYLE section — communication style

### Step 4: Copy and Curate Skills

**Skills need in-place scrubbing, not rewriting.**

Copy skills from each profile's `skills/` directory. Skip generic infrastructure skills that every profile shares:
- `autonomous-ai-agents/claude-code`
- `autonomous-ai-agents/codex`
- `autonomous-ai-agents/hermes-agent`
- `autonomous-ai-agents/opencode`
- `devops/kanban-orchestrator`
- `devops/kanban-worker`
- `creative/touchdesigner-mcp`
- `software-development/hermes-agent-skill-authoring`

#### Live Profile vs Repo Profile Divergence

**The live profile and the repo profile are intentionally different.** The live one has personal tools; the repo one is curated for general use. Don't try to sync them.

**Curation framework — three categories:**

| Category | Action | Examples |
|----------|--------|----------|
| **Always include** | Ship in repo | Domain skills (github, docker, arxiv), framework/methodology (TDD, clean-code), general tool integrations |
| **Consider removing** | Personal/niche | Platform-specific (apple/* excludes Windows/Linux), internal tooling (dogfood, iknowkungfu-contrib), personal infrastructure (yuanbao) |
| **Consider keeping** | General-purpose even if user doesn't use them | Notion API skills in knowledge profile (useful for Notion users), niche domain skills (UE5, game-dev — useful for that community) |

**Orchestrator profiles need aggressive curation.** The top orchestrator (senna) inherits skills from ALL domains — 200+ is normal for the live profile but bloated for a public repo. Strip domain-specific skills from the public orchestrator; users will install those on their domain profiles.

**Key decision:** Does this skill help someone who ISN'T me? If yes, keep it. If it only helps with MY specific setup, remove it from the repo (but keep it on the live profile).

### Step 5: Deep Sanitize Skills (Multi-Pass)

**⚠️ CRITICAL: Python `str.replace()` misses edge cases. Use `sed` for path scrubbing.**

Skill files contain personal references in code examples, path templates, and prose. These are easy to miss.

**Pass 1 — Obvious paths (sed):**
```bash
find profiles -name '*.md' -type f -exec sed -i '' \
  -e 's|~|~|g' \
  -e 's|~|~|g' \
  {} \;
```

**Pass 2 — Username references (sed):**
```bash
find profiles -name '*.md' -type f -exec sed -i '' \
  -e 's|`<user>`|`<user>`|g' \
  -e 's|of the |of the |g' \
  -e 's|MAIN ACCOUNT (<user>)|MAIN ACCOUNT (<user>)|g' \
  -e 's|agent:<user>|agent:<user>|g' \
  {} \;
```

**Pass 3 — Context-specific (manual):**
- GitHub usernames: `<your-github-username>` → `<your-github-username>`
- Project-specific paths: `~/Unreal-Engine-Obsidian` → `~/obsidian-vault`
- Discord server IDs → generic placeholders

**Pass 4 — Verification (grep):**
```bash
# Must return CLEAN
grep -r '<user>\|<your-actual-username>' profiles/ --include='*.md' -l

# Check for personal paths
grep -rn '/Users/' profiles/ --include='*.md' | grep -v '<you>\|<user>\|name/\|\*/'
```

**Preserve these (they're already generic):**
- `/Users/$USER/` — shell variable, correct
- `/Users/<you>/` — generic placeholder
- `/Users/name/` — generic placeholder
- `/Users/*/` — glob pattern in examples

### Step 6: Create Per-Profile READMEs

Each profile directory gets a README.md with:

```markdown
# <Profile Name> — <Role>

<1-2 sentence description>

## When to Use
- Bullet list of triggers

## How It Works
\```
Input → Process → Output
\```

## Skills (<N> total)
- **skill-name** — what it does
- Plus <N-M> more

## Personality
<1-2 sentences on communication style>

## Configuration
\```yaml
model: <recommended model>
max_turns: <N>
reasoning_effort: <level>
\```

## SOUL.md
See [SOUL.md](SOUL.md) for the full agent definition.
```

### Step 7: Create Main README

Landing page with:
- What's in the repo (profile list with 1-line descriptions)
- Quick start (5-step: pick → create → copy SOUL → copy skills → configure → run)
- Multi-agent fleet explanation
- Orchestrator vs Worker table
- Customization guidance
- What's NOT in the repo (personal data, runtime state)
- License

### Step 8: Create .gitignore

```
*.db
*.db-wal
*.db-shm
*.log
*.lock
*.jsonl
*.json
.DS_Store
Thumbs.db
.env
*.env
gateway_state.json
channel_directory.json
.icarus-*
.skills_prompt_snapshot.json
.hermes_history
.vscode/
.idea/
*.swp
*.swo
```

### Step 9: Third-Party Skill Licensing

**⚠️ Check licenses before publishing.** Skills from external collections may have redistribution restrictions.

**Known licenses:**
- **Anthropic Cybersecurity Skills** — Apache 2.0. Author: Mahipal (mukul975). Repo: github.com/mukul975/Anthropic-Cybersecurity-Skills. Fully permissive: redistribute, modify, commercial use. Requirements: include LICENSE file, keep attribution.
- Magnus skills — check origin individually
- Community skills — check individual licenses

**Always do:**
1. Copy the LICENSE file into the skill directory in the repo (don't just mention it)
2. Add attribution to the main README under "Third-Party Skills"
3. Include CITATION.cff info if present

### Step 10: Commit and Push

```bash
cd <repo>
git init
git add -A
git commit -m "Initial commit: <N> profiles with SOUL.md and skills

Profiles: <list>
Includes: <N> SOUL.md files, <N> READMEs, <N> skills, guides
All personal info sanitized."

# Set git identity
git config user.name "<username>"
git config user.email "<email>"

# Create and push
gh repo create <repo-name> --public --source=. --push
```

## Pitfalls

- **Python str.replace() misses path variants.** Paths appear in many forms: `~`, `` `<user>` ``, `<user> (in your case)`, `of the `. Use `sed` with regex patterns for bulk cleanup, not Python string matching.
- **Multi-pass is required.** Single-pass cleanup always misses something. The 4-pass workflow (paths → usernames → context-specific → grep-verify) catches 99%.
- **Generic placeholders already exist.** Some skill files already use `/Users/$USER/`, `/Users/<you>/`, or `/Users/name/`. These are correct — don't "fix" them.
- **Orchestrator profiles inherit everything.** Senna/the top orchestrator will have 200+ skills because it needs to know about all domains. For the LIVE profile this is fine. For the REPO, curate aggressively — strip domain-specific skills from the public orchestrator; users will install those on their domain profiles.
- **Orchestrator bloat is the #1 curation mistake.** A public orchestrator with 200+ skills overwhelms newcomers. Keep orchestration skills (hermes/*, devops/*, github/*, software-development/*) and strip domain specifics (creative/*, mlops/*, unreal-engine/*, gaming/*, financial-markets/*).
- **Notion/productivity skills are a judgment call.** The user may not use Notion, but general-purpose Notion API skills are useful for others. Default to keeping them in knowledge/productivity profiles, removing from orchestrator profiles.
- **Third-party skills need license files IN the repo.** Don't just mention the license — copy the actual LICENSE file into the skill directory.
- **Git identity leaks from system auto-detect.** Set `git config user.name/email` before committing. The default picks up the macOS login name which is personal info.
- **Don't include runtime artifacts.** .db files, logs, .env, gateway_state.json, channel_directory.json — all get gitignored.
- **SOUL.md cleanup ≠ SOUL.md rewrite.** For public sharing, rewrite SOUL.md from scratch with generic placeholders. Trying to patch personal references out of a working SOUL.md is slower and error-prone.
- **Skill counts matter for READMEs.** Count skills per profile for the README. Users want to know what they're getting.
- **Cyber-blue variants need READMEs.** If splitting the public `cyber-blue` into local variants like `cyber-blue-cloud`, `-compliance`, `-forensics`, and `-soc`, add a README to each or they render as empty shells in the repo.
- **Remove config.yaml from specialized variants unless intentionally documented.** Config belongs in the live profile, not in published profile repos.
- **Keep `Anthropic-Cybersecurity-Skills` for profile-specific cyber use cases.** It is core capability, not bulk bloat. For `cyber-red` and `cyber-blue-*` specializations, keep the matching `Anthropic-Cybersecurity-Skills` revision when mirroring/publishing.
- **Keep only minimal default skills on generic profiles.** Default skill categories like `apple`, `mlops`, `github`, `software-development`, etc. are bloat unless the profile has no specialization-specific skills.

## References

- `references/sanitization-patterns.md` — Proven sed/grep patterns for stripping personal info
- `references/profile-curation-framework.md` — Decision framework for what to include in public vs live profiles
- `references/skill-split-rules.md` — How to decide which skill bundles to keep or strip for cyber-* profiles
- `templates/profile-readme-template.md` — Copy-paste README template per profile

## Template: Per-Profile README

See `templates/profile-readme-template.md` for a copy-paste starting point.
