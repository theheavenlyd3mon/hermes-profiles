---
name: hermes-backup-repo
description: "Disaster-recovery backup and restore for the Senna Hermes profile — config, skills, memory DBs, plugins, and home dotfiles pushed to a private GitHub repo."
version: 1.0.0
author: Senna
platforms: [macos, linux]
metadata:
  hermes:
    tags: [hermes, backup, restore, disaster-recovery, git]
    related_skills: []
---

# Hermes Backup Repo — Disaster Recovery

## WHAT

The Senna profile's entire state (config, skills, plugins, memory databases, key dotfiles) is backed up to a private GitHub repo: **`<your-github-username>/Hermes`** (cloned at `~/Hermes/`).

Secrets (`.env`, `auth.json`) are **never** committed — the restore script prompts for them.

Two scripts in the repo root:
- **`backup.sh`** — snapshots current state into `senna-profile/`
- **`restore.sh`** — recovers from `senna-profile/` onto a fresh machine

## TRIGGER CONDITIONS

Use this skill when:
- User says "backup", "backup my Hermes", "backup repo", "backup the profile"
- User says "restore", "recover", "disaster recovery"
- User asks about the Hermes backup strategy or where their config is backed up
- User asks about secrets policy for the backup repo
- You've made significant changes to the profile (new skills, config changes) and want to snapshot
- User mentions crash/recovery/fresh install scenario

## REPO STRUCTURE

```
~/Hermes/
├── README.md
├── backup.sh              # Snapshot script (run regularly)
├── restore.sh             # Recovery script (run on fresh machine)
├── senna-profile/
│   ├── .backup-manifest.txt    # Documents what's included/excluded
│   ├── config/
│   │   ├── config.yaml
│   │   ├── SOUL.md
│   │   ├── channel_directory.json
│   │   ├── .icarus-state.json
│   │   └── gateway_state.json
│   ├── skills/                 # Full copy of all profile skills
│   ├── plugins/                # plugin.yaml metadata only (not plugin code)
│   ├── memory/
│   │   ├── mnemosyne/data.tar.gz    # Compressed (~4 MB from 650 MB raw)
│   │   ├── ~~state.db.tar.gz~~      # EXCLUDED — 192 MB compressed, exceeds GitHub 100 MB limit
│   │   ├── lcm.db.tar.gz            # Compressed
│   │   ├── kanban.db.tar.gz
│   │   └── response_store.db.tar.gz
│   ├── home/                  # .zshrc, .gitconfig, gbrain_setup_status.json
│   ├── scripts/               # kanban-gate, security scanner, etc.
│   └── vault/                 # Obsidian-style vault notes
```

## BACKUP PROCEDURE

```bash
cd ~/Hermes
./backup.sh                     # Collects state into senna-profile/
git add -A                      # Stage everything
git commit -m "backup $(date +%Y%m%d)"
git push
```

The backup script handles:
- **Config files** — direct copy from `~/.hermes/profiles/senna/`
- **Skills** — rsync with delete (mirrors current state)
- **Plugins** — copies `plugin.yaml` metadata only
- **Memory DBs** — compressed via `tar czf` to stay under GitHub's 100 MB file limit
- **Mnemosyne** — compressed, excluding stale GGUF model files (~650 MB → ~4 MB)
- **Home dotfiles** — `.zshrc`, `.gitconfig`, gbrain status
- **Scripts** — security helpers, kanban gate
- **Vault** — any notes in the profile vault directory

## WHAT'S EXCLUDED (never in repo)

| Category | Reason |
|----------|--------|
| `.env`, `auth.json` | **Secrets** — prompted at restore time |
| `sessions/`, `logs/`, `cache/` | Ephemeral / too large |
| `checkpoints/`, `state-snapshots/` | Recreatable |
| `venv/`, `.venv/`, `node_modules/` | Reinstalled |
| `hermes-agent/` | Re-cloned from upstream |

## SECRETS POLICY

Secrets are **never** committed to the repo. At restore time, the user is prompted:
1. Path to their `.env` file (or creates one manually)
2. Path to `auth.json` (or lets Hermes regenerate it)

## RESTORE PROCEDURE (fresh machine)

```bash
# 1. Install Hermes Agent
# 2. Clone the backup repo
git clone https://github.com/<your-github-username>/Hermes.git

# 3. Run restore script
cd Hermes
./restore.sh [--profile senna] [--dry-run]

# 4. Follow prompts for secrets (.env + auth.json)
# 5. Start Hermes:  hermes
# 6. Verify skills: /skills
```

## PATH NOTE

The shell's `$HOME` resolves to `~/.hermes/profiles/senna/home/` (not `~/`). The backup script uses explicit absolute paths:
- `HERMES_ROOT="~/.hermes"`
- `PROFILE_DIR="$HERMES_ROOT/profiles/senna"`
- `HOME_DIR="$PROFILE_DIR/home"`

## VERIFYING A BACKUP

After running backup.sh + git push, verify:
```bash
cd ~/Hermes && git log --oneline -1
# Should show: backup YYYYMMDD-HHMMSS
```

## PITFALLS

- **GitHub 100 MB file limit** — SQLite DBs are compressed via `tar czf` before committing. If a DB grows past ~100 MB compressed, it won't push. In that case, split into chunks or use Git LFS.
- **$HOME resolution** — The shell's `$HOME` is `~/.hermes/profiles/senna/home/`, so `~/` resolves through the profile symlink. Always use absolute paths.
- **Old large files in git history** — If an uncompressed DB was accidentally committed, force-push from clean history won't work if it's still in a prior commit. Use `git reset --soft <clean-sha>` to strip large blobs from history.
- **Force push** — Since this is a single-user repo, force-pushing to clean history is safe, but make sure your local state is complete first.
- **state.db is the largest** — At ~182 MB raw / ~78 MB compressed. This is the primary candidate for Git LFS if it grows further.
