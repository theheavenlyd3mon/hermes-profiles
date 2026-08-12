# Hermes Profile Backup & Disaster Recovery

Session-derived: 2026-05-15, Senna profile, macOS 15.6. User maintains a private
backup repo at `<your-github-username>/Hermes` for disaster recovery.

## Backup Philosophy

- **Secrets NEVER go in the repo** — `.env` and `auth.json` are prompted at
  restore time or injected via GitHub Secrets. Private repo ≠ safe for secrets;
  git history is permanent, account compromise is possible, and accidental-public
  mistakes happen.
- **Upstream code is NOT backed up** — `hermes-agent/` is re-cloned on a fresh
  machine. Only user-created/customized files go in the backup.
- **Virtual environments and caches are excluded** — venvs, node_modules, logs,
  sessions, caches are all ephemeral.

## What to Back Up

| Category | Path | Purpose |
|----------|------|---------|
| Config | `profiles/senna/config.yaml` | Model, plugins, tools, skin settings |
| SOUL | `profiles/senna/SOUL.md` | Persona definition |
| Channel dir | `profiles/senna/channel_directory.json` | Platform routing |
| Gateway state | `profiles/senna/gateway_state.json` | Platform connection state |
| Skills | `profiles/senna/skills/` | All user-created + learned skills |
| Plugin configs | `profiles/senna/plugins/*/plugin.yaml` | Plugin metadata (not code) |
| Mnemosyne | `~/.hermes/mnemosyne/` | Durable memory (~650 MB raw, compresses to ~4 MB) |
| State DB | `profiles/senna/state.db` | Session state (182 MB raw → 78 MB gzipped) |
| LCM DB | `profiles/senna/lcm.db` | Conversation memory |
| Kanban DB | `profiles/senna/kanban.db` | Multi-agent task board |
| Response store | `profiles/senna/response_store.db` | Cached responses |
| Dotfiles | `profiles/senna/home/.zshrc`, `.gitconfig` | Shell preferences |
| Scripts | `profiles/senna/scripts/` | Profile-specific helper scripts |

## What to Exclude

- `.env`, `auth.json` — secrets, never in git
- `sessions/`, `logs/`, `cache/`, `audio_cache/`, `image_cache/` — ephemeral
- `checkpoints/`, `state-snapshots/` — recreatable
- `venv/`, `.venv/`, `node_modules/` — reinstalled
- `hermes-agent/` — re-cloned from upstream

## Git File Size Strategy

GitHub enforces a **100 MB hard file limit** per file (50 MB recommended).
Large SQLite databases must be compressed:

- **state.db** (~182 MB) → `state.db.tar.gz` (~78 MB) — fits under 100 MB limit
- **Mnemosyne directory** (~650 MB) → `mnemosyne/data.tar.gz` (~4 MB) — excellent
  text compression

Use `tar czf` for compression:

```bash
tar czf target.tar.gz -C /path/to/dir filename.db
```

## The `$HOME` Symlink Trap

Inside a profile cron context or subshell, `$HOME` may resolve to
`~/.hermes/profiles/senna/home/` rather than `~/`.
This means `~/.hermes` resolves to the **nested legacy copy** at
`profiles/senna/home/.hermes/`, not the real Hermes root.

**Fix:** Always use absolute paths (`~/.hermes/`) in scripts that
run in profile cron contexts. Never rely on `$HOME/.hermes` or `~/.hermes`.

## Restore Workflow

On a fresh machine:

1. Install hermes-agent
2. Clone the backup repo
3. Run `./restore.sh` — it unpacks config, skills, plugins, and memories
4. Provide `.env` and `auth.json` when prompted (secrets are NOT in the repo)
5. Start Hermes and verify

## Recovery from Accidental Large-File Commit

If a file > 100 MB is accidentally committed and push is rejected, the approach
used is to reset to a clean initial commit and force-push:

```bash
git reset --soft <initial-commit-hash>
# Now add only the correctly-compressed files (not the large raw DBs)
git add -A
git commit -m "corrected backup"
git push --force
```

This rewrites history — safe only on single-user private repos where no one
else has pulled the dirty commits.
