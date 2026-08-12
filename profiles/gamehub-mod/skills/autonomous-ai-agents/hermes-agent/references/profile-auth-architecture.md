# Profile Credential Pool Architecture

## How Hermes stores auth per profile

Each profile has its own isolated credential pool. The auth system uses two files per profile:

| File | Purpose |
|------|---------|
| `~/.hermes/profiles/<name>/auth.json` | Credential store — OAuth tokens, API keys registered via `hermes auth add`, credential pool JSON |
| `~/.hermes/profiles/<name>/auth.lock` | File-based mutex (0 bytes) — prevents concurrent writes to auth.json |

**Key insight:** These are **per-profile**, not shared. OAuth tokens obtained via `hermes login --provider nous` from within the **Senna** profile are stored only in Senna's `auth.json`. Team profiles (architect, coder, debugger, reviewer) have their own directories — starting with no `auth.json` at all (just an empty `auth.lock`).

### How to detect empty credential pools

```bash
for p in architect coder debugger reviewer senna; do
  files=$(ls ~/.hermes/profiles/$p/auth.* 2>/dev/null | tr '\n' ' ')
  echo "$p: $files"
done
```

A profile with only `auth.lock` (0 bytes) and no `auth.json` has no credential pool. Workers spawned under that profile will fail authentication for any provider that requires OAuth or a registered credential.

### Checking what's in a profile's credential pool

```bash
# List all registered credentials
hermes auth list

# Check a specific provider
hermes auth list nous

# Inspect the raw auth file
cat ~/.hermes/profiles/<profile>/auth.json
```

The `hermes auth list` command runs in the **current profile's context**. To check another profile's pool, use `hermes -p <profile> auth list`.

## The symlink pattern (single source of truth)

If you use a profile-based multi-agent setup (architect, coder, debugger, reviewer — each with their own kanban-assigned work), each worker spawns against that profile and reads **that profile's** `auth.json`. Without sharing, you must either:

1. Run `hermes login --provider <name>` N times (once per profile)
2. Copy `auth.json` to each profile directory
3. **Symlink** — put the canonical copy at root, symlink from every profile

Option 3 mirrors the plugins symlink pattern (`~/.hermes/profiles/<name>/plugins/` → `~/.hermes/plugins/`). It's the user's preferred approach for this setup.

### Setup

```bash
# 1. Copy canonical auth.json to root
cp ~/.hermes/profiles/<source-profile>/auth.json ~/.hermes/auth.json

# 2. Replace the source profile's copy with a symlink (backup first)
mv ~/.hermes/profiles/<source-profile>/auth.json \
   ~/.hermes/profiles/<source-profile>/auth.json.bak
ln -s ~/.hermes/auth.json ~/.hermes/profiles/<source-profile>/auth.json

# 3. Create symlinks in all team profiles
for p in architect coder debugger reviewer; do
  ln -s ~/.hermes/auth.json ~/.hermes/profiles/$p/auth.json
done

# 4. Verify
for p in architect coder debugger reviewer senna; do
  target=$(readlink ~/.hermes/profiles/$p/auth.json 2>/dev/null)
  echo "$p -> $target"
done
```

All profiles now read and write to the same canonical `auth.json` at `~/.hermes/auth.json`. Any profile that obtains a new OAuth token (via `hermes login`) updates the shared file.

### The auth.lock files remain per-profile

The `auth.lock` files (0-byte mutexes) stay local to each profile directory — they coordinate write access within a single profile's process. They don't need to be symlinked because they're just locks, not data.

### When to choose which approach

| Approach | When | Drawback |
|----------|------|----------|
| Copy auth.json | One-off fix, profiles don't change | Stale if source profile re-authenticates |
| Per-profile `hermes login` | Clean isolation, each profile has its own scope | Tedious with many profiles |
| **Symlink (recommended)** | Multi-profile setups where credentials should be unified | All profiles share the same token — re-auth affects all |

## Verifying the fix after credential setup

After setting up credentials (by any method), verify a kanban task can actually run:

```bash
# 1. Check what your credentials look like
hermes -p architect auth list nous   # should show the credential

# 2. Unblock any stuck tasks
hermes kanban list | grep blocked
hermes kanban unblock t_<task_id> [t_<task_id2> ...]

# 3. Dispatch
hermes kanban dispatch

# 4. Verify no crashes
hermes kanban list   # should not show "blocked" for these tasks
```
