# Auth.json Symlink Pattern

> Sharing OAuth credential pools across all Hermes profiles via a single canonical auth.json at root, with per-profile symlinks.

## Problem

Each Hermes profile has an **isolated credential pool** stored in its own `auth.json` file. When you run `hermes login --provider nous` under the `senna` profile, the OAuth token is stored only in `~/.hermes/profiles/senna/auth.json`. Other profiles (`architect`, `coder`, `debugger`, etc.) have their own credential pools that start **empty** — just a 0-byte `auth.lock` file.

When a kanban worker spawns under a team profile (e.g. `architect`), it checks **its own credential pool** for the provider token, finds nothing, fails to authenticate, and exits cleanly (rc=0) without calling `kanban_complete` or `kanban_block`. The dispatcher marks this as a **protocol_violation**.

The same issue affects any profile-based automation: cron jobs, gateway workers, direct CLI use with `-p <profile>`.

## Pattern: Symlink auth.json to Root

Mirrors the plugins-symlink pattern — one canonical source at `~/.hermes/`, all profiles point to it.

### Setup

```bash
# 1. Copy the canonical auth.json from the profile that has the OAuth token to root
cp ~/.hermes/profiles/senna/auth.json ~/.hermes/auth.json

# 2. Replace the source profile's auth.json with a symlink (keep a backup)
mv ~/.hermes/profiles/senna/auth.json ~/.hermes/profiles/senna/auth.json.bak
ln -s ~/.hermes/auth.json ~/.hermes/profiles/senna/auth.json

# 3. Create symlinks for ALL other profiles that need credential access
for p in architect coder debugger reviewer data-analyst devops foreman \
         researcher secretary security; do
  ln -s ~/.hermes/auth.json ~/.hermes/profiles/$p/auth.json
done
```

### Verification

```bash
# Check every profile's auth.json resolves to the same canonical file
for p in senna architect coder debugger reviewer; do
  target=$(readlink ~/.hermes/profiles/$p/auth.json 2>/dev/null || echo "MISSING")
  echo "$p -> $target"
done

# Confirm the canonical file has content
wc -c ~/.hermes/auth.json

# Test token access from a team profile
hermes -p architect auth list nous
```

### Recovery: Kanban Workers That Already Crashed

After setting up the symlinks, unblock any affected tasks and dispatch:

```bash
# Unblock (not reclaim — these are already blocked/gave_up, not running)
hermes kanban unblock <task_id_1> <task_id_2> <task_id_3>

# Dispatch fresh workers
hermes kanban dispatch
```

See the `kanban-orchestrator` skill's "Subclass A: Provider / credential mismatch" section for the full diagnosis and recovery flow.

## Why This Works

- **Root `.env` is single source of truth for API keys** → this pattern extends the same philosophy to OAuth tokens
- **Auth changes apply everywhere** — if you re-authenticate (`hermes login --provider nous`) from any profile, the token updates in the shared file
- **No more "no auth.json" failures** — new profiles automatically inherit credentials if symlinked
- **Minimal maintenance** — one file to backup, one file to audit

## Pitfalls

- **Lock contention** — `auth.lock` files remain per-profile (they're simple file mutexes). If a credential pool write happens simultaneously from two profiles, the last writer wins. In practice, credential pools are read-heavy (every API call checks tokens) and write-rare (OAuth refresh, `hermes auth add`), so contention is negligible.
- **Upgrade risk** — if a future Hermes version rewrites `auth.json` under a profile directory (not recommended but possible), it would replace the symlink with a regular file. Detect this with: `find ~/.hermes/profiles/*/auth.json -type f -not -xtype l` and re-apply the symlink.
- **Profile sandboxing** — the `~` resolution quirk on macOS means commands run from within a profile context may resolve `~/.hermes/auth.json` to a sandboxed path. Use absolute paths (`/Users/<you>/.hermes/auth.json`) in any automation or recovery scripts that run inside a profile workspace.

## Related

- Plugins symlink pattern: `hermes-agent` skill (profile plugins dir → global plugins dir)
- Kanban protocol-violation diagnosis: `kanban-orchestrator` skill, "Subclass A: Provider / credential mismatch"
- Env architecture (root .env vs profile .env): `references/env-architecture.md`
