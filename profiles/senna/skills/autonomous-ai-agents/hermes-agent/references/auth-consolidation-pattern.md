# Auth.json Consolidation: Root → Profile Symlinks

## Problem

OAuth-based providers (Nous Portal, OpenAI Codex, GitHub Copilot) store credentials in each profile's `auth.json`. When you authenticate via `hermes login --provider nous` inside one profile, the resulting token lives only in that profile's credential pool. Other profiles — especially the team profiles spawned by Kanban (architect, coder, debugger, reviewer, etc.) — have **empty credential pools** and no `auth.json` at all (just an empty `auth.lock` mutex file).

This causes Kanban workers spawned under those profiles to fail immediately with `protocol_violation` — they attempt to authenticate, find no credentials, and exit cleanly without completing.

## Solution: Symlink auth.json to Root

Mirrors the existing plugins symlink pattern (`~/.hermes/profiles/<name>/plugins/` → `~/.hermes/plugins/`). Move the canonical auth.json to `~/.hermes/` and symlink each profile to it.

### Step-by-step

```bash
# 1. Pick the source profile that has the working OAuth token
#    (e.g. the one where you ran `hermes login --provider nous`)
SOURCE=senna

# 2. Copy to root (canonical source)
cp ~/.hermes/profiles/$SOURCE/auth.json ~/.hermes/auth.json

# 3. Backup and symlink the source profile
mv ~/.hermes/profiles/$SOURCE/auth.json ~/.hermes/profiles/$SOURCE/auth.json.bak
ln -s ~/.hermes/auth.json ~/.hermes/profiles/$SOURCE/auth.json

# 4. Symlink all other profiles to the same root file
for p in architect coder debugger reviewer data-analyst devops foreman researcher secretary security; do
  ln -s ~/.hermes/auth.json ~/.hermes/profiles/$p/auth.json 2>/dev/null || true
done

# 5. Verify
for p in senna architect coder debugger reviewer; do
  echo "$p -> $(readlink ~/.hermes/profiles/$p/auth.json 2>/dev/null || echo MISSING)"
done
```

### Verification

```bash
# Check all profiles have the symlink
for p in ~/.hermes/profiles/*/; do
  name=$(basename "$p")
  target=$(readlink "$p/auth.json" 2>/dev/null)
  [ -n "$target" ] && echo "  ✓ $name -> $target" || echo "  ✗ $name no auth.json symlink"
done

# Confirm root copy has content
wc -c ~/.hermes/auth.json

# Quick auth test on a team profile
hermes -p architect auth list nous
```

### What stays per-profile

- `auth.lock` files — 0-byte mutexes for concurrent access. These should remain per-profile. If they're symlinked too, all profiles share a single lock, which serializes all auth writes across every profile. This is usually not a concern in practice (auth.json is read-heavy, written only during OAuth refresh or `hermes auth add`), but keeping separate locks avoids potential contention.

### Diagnostics: check if this applies

```bash
# Check which profiles have auth.json vs just auth.lock
for p in ~/.hermes/profiles/*/; do
  name=$(basename "$p")
  has_json=$(test -f "$p/auth.json" && echo "yes" || echo "no")
  has_lock=$(test -f "$p/auth.lock" && echo "yes" || echo "no")
  is_link=$(test -L "$p/auth.json" && echo " (symlink)" || echo "")
  echo "$name: auth.json=$has_json$is_link auth.lock=$has_lock"
done
```

A profile with `auth.json=no, auth.lock=yes` indicates an empty credential pool — the profile has no provider credentials at all.

### Relationship to other consolidation patterns

| Pattern | Canonical Source | Profile Access |
|---------|-----------------|----------------|
| API keys | `~/.hermes/.env` (root) | Profile `.env` overrides (loads second) |
| OAuth tokens | `~/.hermes/auth.json` (root) | Profile `auth.json` symlinks to root |
| Plugins | `~/.hermes/plugins/` | Profile `plugins/` symlinked to root |
| Gateway config | `~/.hermes/config.yaml` + root `.env` | Profile gateway runs as sticky default |

All four follow the same principle: **one canonical source, accessed by all profiles**.
