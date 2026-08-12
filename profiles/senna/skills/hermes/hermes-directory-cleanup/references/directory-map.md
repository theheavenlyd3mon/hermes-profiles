# Hermes Directory Map — May 2026

Complete structural map of `~/.hermes/` on a macOS senna-profile installation. Use this when you need to find something and aren't sure which path is real.

## The Path Resolution Trap

When a Hermes profile runs, it sets `HOME` to its own sandboxed directory:

```
HERMES_HOME = /Users/<user>/.hermes/profiles/<name>
HOME        = /Users/<user>/.hermes/profiles/<name>/home
```

This means from INSIDE a profile session:
- `~` resolves to `/Users/<user>/.hermes/profiles/<name>/home/`
- `~/.hermes` resolves to `.../<name>/home/.hermes/` (the NESTED copy, mostly empty)
- `find ~`, `ls ~`, `cat ~/.hermes/config.yaml` all show NESTED data, NOT the real files

**Rule: Always use absolute paths starting with `/Users/<user>/.hermes/` when referencing hermes directories.**

Check `HOME` and `HERMES_HOME` env vars to confirm what's active:
```bash
echo "HOME=$HOME HERMES_HOME=$HERMES_HOME"
```

## Real Directory Structure

All paths below are absolute from `/Users/<user>/.hermes/`.

### Config & Identity (root level)

| File | Purpose |
|------|---------|
| `config.yaml` | Main config — toolsets, mcp_servers, cron, platforms |
| `SOUL.md` | Default persona |
| `.env` | API keys (never commit) |
| `active_profile` | Which profile is active |
| `.install_method` | How hermes was installed |
| `auth.json` / `auth.lock` | Auth tokens |
| `.hermes_history` | CLI history |
| `gateway_state.json` | Gateway runtime state |
| `channel_directory.json` | Channel-to-profile mappings |
| `models.json` | Model catalog |
| `model-pricing-snapshot.json` | Pricing cache |
| `context_length_cache.yaml` | Context length cache |
| `processes.json` / `tasks.json` | Process/task state |
| `.clean_shutdown` | Shutdown marker |

### Databases

| File | Purpose |
|------|---------|
| `state.db` (+wal, +shm) | Main state DB |
| `scheduler.db` | Cron scheduler |
| `kanban.db` (+wal, +shm) | Kanban board state |
| `mnemosyne/data/mnemosyne.db` | Memory/vector DB |

### Hermes Agent Source

`hermes-agent/` — Full source checkout (cli.py, run_agent.py, agent/, tools/, gateway/, plugins/, etc.)
- This is the CLI backbone. `~/.local/bin/hermes` depends on it.
- NEVER delete or move this directory.

### Profiles

```
profiles/
  <name>/               -- Profile root
    skills/             -- Profile-specific skills
    skins/              -- Profile-specific skins
    logs/               -- Profile logs
    scripts/            -- Profile scripts
    home/.hermes/       -- Sandboxed HOME (nested .hermes, mostly empty copies)
```

### Skills (default/root profile)

`skills/` — 100+ skills across 30+ categories. Major groups:
- `apple/` — Notes, Reminders, FindMy, iMessage, computer-use
- `autonomous-ai-agents/` — Claude Code, Codex, Hermes Agent, Kanban
- `creative/` — ASCII art, diagrams, video, design, music (20+ subskills)
- `data-science/` — Jupyter kernel
- `devops/` — Kanban orchestrator, webhooks, Docker, cron
- `email/` — Himalaya
- `gaming/` — Minecraft, Pokemon
- `github/` — PR, issues, code review, auth (6 subskills)
- `hermes/` — Plugin setup, run-webui
- `mlops/` — Training, inference, evaluation, research (10+ subskills)
- `note-taking/` — Obsidian
- `productivity/` — Notion (10+ subskills), Airtable, Google, Linear, PDF
- `red-teaming/` — Godmode
- `research/` — ArXiv, blogwatcher, polymarket
- `smart-home/` — OpenHue, smart-mirror
- `social-media/` — X/Twitter (xurl)
- `software-development/` — Debugging, TDD, planning, Three.js (20+ subskills)
- `team-wiki/` — Setup, ingest, maintain, sync
- `yuanbao/` — Yuanbao groups
- `unreal-engine/` — 26 UE skills (in senna profile, not root)
- `.archive/` — 13 deprecated/pruned skills
- + 20 book/strategy skills (lean-startup, crossing-the-chasm, etc.)

### Plugins

`plugins/hermes-lcm/` — LCM plugin (35 files: tools.py, dag.py, store.py, etc.)

### Tools & Binaries

| Path | Content |
|------|---------|
| `bin/tirith` | Tirith binary (11 MB) |
| `herm/tui.json` | TUI config |

### Applications

| Path | Content |
|------|---------|
| `webui/` | WebUI sessions |
| `webui-mvp/` | WebUI MVP run history |

**Removed (2026-05-28):**
- `hermes-office/` — Claw3D/OpenClaw frontend. Deleted (1 GB). Project no longer in use.
- `~/hermes-solar-system/` — Three.js solar system experiment. Deleted local, GitHub repo archived.

### Data & State

| Path | Content |
|------|---------|
| `kanban/workspaces/` | 16 kanban workspace dirs (task boards) |
| `plans/` | Plan markdown files |
| `pastes/` | (usually empty) |
| `sessions/` | (usually empty at root; profiles have their own) |
| `memories/` | (usually empty at root) |
| `shared/nous_auth.json` | Nous auth tokens |
| `shared-brain/pgdata/` | PostgreSQL data (shared brain DB) |
| `secretary/` | curation-cron, curation-weekly.sh |
| `mnemosyne/models/` | TinyLlama GGUF model (~638 MB) |
| `cache/fastembed/` | Embedding model cache |
| `image_cache/` | Generated images |
| `audio_cache/` | TTS audio |
| `sandboxes/singularity/` | Singularity sandbox |
| `archive/` | Archived configs (config.yaml, auth.json) |

### Scripts & Security

| Path | Content |
|------|---------|
| `scripts/` | supply-chain-scan.sh, kanban-gate.sh, model-pricing-watcher.py, plugin-update-check.sh, gitradar-run.sh |
| `profiles/<name>/scripts/` | Same scripts (profile-level, cron resolves here) |
| `security/` | MORNING_CHECKLIST.sh, harden script, SECURITY_POLICY.md |
| `hooks/` | (usually empty) |
| `pairing/` | (usually empty) |

**Scripts sync note (2026-05-28):** Cron scripts should exist in BOTH
`~/.hermes/scripts/` (global) and `~/.hermes/profiles/senna/scripts/` (profile).
The cron system resolves relative script names from the profile scripts dir.
After `hermes update` or profile migration, verify all scripts exist in both locations.

### External Paths (env vars)

| Var | Path | Content |
|-----|------|---------|
| `WIKI_PATH` | `~/Hermes Vault/Hermes/LLM-Wiki` | LLM Wiki |
| `OBSIDIAN_VAULT` | `~/Hermes Vault/Hermes` | Obsidian vault |
| `FABRIC_DIR` | `~/Hermes Vault/Hermes/icarus` | Icarus fabric |
| `SHARED_VAULT` | `~/.hermes/shared/team-vault` | Shared team vault |

### Backup Repo

`~/Hermes/` — Git repo (github.com/<your-github-username>/Hermes.git)
- `senna-profile/` — Full backup of senna profile data + skills
- `backup.sh` / `restore.sh` — Backup/restore scripts
