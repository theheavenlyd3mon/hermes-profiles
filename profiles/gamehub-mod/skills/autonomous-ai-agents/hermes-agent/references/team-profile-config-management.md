# Team Profile Configuration Management

> What you get when you clone 9+ profiles from the same template and want to keep shared settings (browser, web search, credentials) in sync without breaking profile-specific config.

## Architecture Pattern

The canonical Hermes multi-profile setup for the 10-agent team (architect, coder, data-analyst, debugger, devops, foreman, researcher, reviewer, secretary, security) follows a **layered symlink + batch-apply** pattern:

| Resource | Strategy | Detail |
|----------|----------|--------|
| `.env` | **Symlink → root** | Each profile's `.env` is a symlink to `~/.hermes/.env`. One canonical source for all API keys. |
| `auth.json` | **Symlink → root** | Each profile's `auth.json` is a symlink to `~/.hermes/auth.json`. One canonical source for OAuth tokens. |
| `plugins/` dir | **Per-profile dir** (or symlink → global) | By default, each profile has its own `plugins/` directory. For unified setups, see Option C (symlink to `~/.hermes/plugins/`). |
| `config.yaml` | **Per-profile file** | MUST be per-profile because models, toolsets, personalities, and browser configs diverge. Shared settings require batch-apply. |

## Central Finding: All 9 Team Profiles Are Identical Clones

When you run `hermes profile list`, the profiles exist. When you inspect them, they share:

- **Model**: `deepseek/deepseek-v4-pro` via Nous provider (identical across all 9)
- **Toolsets**: Only `hermes-cli` enabled (browser, vision, web, etc. are ALL off by default)
- **Browser section**: Present in every config.yaml, but `cloud_provider` is unset — all are set up for local Chromium only
- **`.env`**: All symlinked to `~/.hermes/.env` (already consolidated)
- **`auth.json`**: All symlinked to `~/.hermes/auth.json` (already consolidated)
- **`plugins/`**: Real directories with 1 item each — NOT symlinked to global

The only differences between profiles are their `SOUL.md` (role personality) and their `skills/` directory contents (different skills per role).

## When to Apply Shared Settings

Common shared-settings operations that need batch-apply:

1. **`cloud_provider: browserbase`** — adding Browserbase to all profiles that need browser automation
2. **`engine: auto`** — setting browser engine type
3. **`toolsets` defaults** — enabling basic tools across profiles (e.g., `search`, `web`)
4. **`delegation.provider` / `delegation.model`** — subagent delegation model
5. **`auxiliary.vision.provider`** — vision provider for screenshots

## Batch-Apply Pattern (config.yaml)

Use sed loops. Each profile's config.yaml has the same structure because they were created from the same template.

### Adding `cloud_provider: browserbase` to all profiles

```bash
for p in architect coder data-analyst debugger devops foreman researcher reviewer secretary security; do
  f="~/.hermes/profiles/$p/config.yaml"
  # Check if cloud_provider already exists
  if ! grep -q cloud_provider "$f" 2>/dev/null; then
    sed -i '' 's/^browser:/browser:\n  engine: auto\n  cloud_provider: browserbase/' "$f"
  fi
done
```

### Changing model across all profiles

```bash
for p in architect coder data-analyst debugger devops foreman researcher reviewer secretary security; do
  sed -i '' 's|default: <old-model>|default: <new-model>|g' "~/.hermes/profiles/$p/config.yaml"
done
```

### Enabling browser toolset across all profiles

```bash
for p in architect coder data-analyst debugger devops foreman researcher reviewer secretary security; do
  hermes --profile "$p" tools enable browser
done
```

### Adding a tools dependency (e.g., search tool)

Not all config.yaml editors support `hermes config set section.key` for nested lists. Use sed or patch the `toolsets:` list directly.

## Why NOT to Symlink config.yaml

1. **Update breaks the symlink**: `hermes config edit`, `hermes config migrate`, and profile creation all rewrite config.yaml as a flat file. The symlink is silently replaced.
2. **Profiles should diverge**: Architect may use a different model than coder. Researcher may need browser tools but security may not. Symlinking locks them together.
3. **One profile misconfiguration poisons all**: If one profile's config gets corrupted, the symlink propagates the corruption to every profile.

The exception: if you truly want ALL profiles to be identical (including model and toolsets), symlink works. But that defeats the purpose of specialist profiles.

## Skills Audit: Comparing Skills Across Profiles

Skills are often the main discriminator between profiles (more than model, tools, or env). Quick methodology to compare:

```bash
# List skills per profile (just category names)
for p in architect coder debugger reviewer foreman secretary devops security data-analyst researcher; do
  echo "$p: $(ls ~/.hermes/profiles/$p/skills/ | grep -v '^\.' | tr '\n' ' ')"
done

# Full hierarchical listing
for p in architect coder researcher; do
  echo "=== $p ==="
  ls ~/.hermes/profiles/$p/skills/*/ -d 2>/dev/null | sed 's|.*/skills/||' | sed 's|/||'
done

# Count skills per profile
for p in architect coder debugger reviewer foreman secretary devops security data-analyst researcher; do
  count=$(ls -d ~/.hermes/profiles/$p/skills/*/ 2>/dev/null | wc -l)
  echo "$p: $count skill categories"
done
```

**Common finding — homogeneous clones:** When all profiles share the same skill catalog (e.g., all 23 same categories), only SOUL.md differentiates them. The original team design doc may specify role-specific pruning that was never applied. Flag this to the user.

**To check if skills were actually pruned as intended:**

```bash
# Compare two profiles for differences
diff <(ls ~/.hermes/profiles/architect/skills/ | grep -v '^\.' | sort) \
     <(ls ~/.hermes/profiles/coder/skills/ | grep -v '^\.' | sort)

# Or list what's unique per profile
for p in architect coder researcher secretary security; do
  echo "=== Unique to $p ==="
  for other in architect coder researcher secretary security; do
    [ "$p" = "$other" ] && continue
    comm -23 \
      <(ls ~/.hermes/profiles/$p/skills/ | grep -v '^\.' | sort) \
      <(ls ~/.hermes/profiles/$other/skills/ | grep -v '^\.' | sort)
  done | sort -u
done
```

**Senna comparison** — Senna (the default profile) often has more skills than team profiles:
```bash
echo "In senna but not in team profiles:"
comm -23 \
  <(ls ~/.hermes/profiles/senna/skills/ | grep -v '^\.' | sort) \
  <(ls ~/.hermes/profiles/architect/skills/ | grep -v '^\.' | sort)
```

## Audit Commands

Quick audit of shared config across all team profiles:

```bash
# Browser cloud_provider
grep cloud_provider ~/.hermes/profiles/*/config.yaml

# Models
grep 'default:' ~/.hermes/profiles/*/config.yaml

# Toolsets
grep -A22 '^toolsets:' ~/.hermes/profiles/*/config.yaml | grep -E '^- |^--'

# .env symlinks
for p in architect coder data-analyst debugger devops foreman researcher reviewer secretary security; do
  f="~/.hermes/profiles/$p/.env"
  if [ -L "$f" ]; then echo "$p -> $(readlink "$f")"; else echo "$p: $(file "$f" | cut -d: -f2)"; fi
done

# auth.json symlinks
for p in architect coder data-analyst debugger devops foreman researcher reviewer secretary security; do
  f="~/.hermes/profiles/$p/auth.json"
  if [ -L "$f" ]; then echo "$p -> $(readlink "$f")"; else echo "$p: $(file "$f" | cut -d: -f2)"; fi
done

# plugins/ dir type
for p in architect coder data-analyst debugger devops foreman researcher reviewer secretary security; do
  d="~/.hermes/profiles/$p/plugins"
  if [ -L "$d" ]; then echo "$p -> $(readlink "$d")"; else echo "$p: real dir ($(ls "$d" 2>/dev/null | wc -w) items)"; fi
done
```

## Pitfalls

- **Absolute paths required in profile context**: Inside a Hermes profile, `~` may resolve differently. Always use `~/.hermes/profiles/...` in scripts and batch loops.
- **Don't override root variables in profile .env files**: If a profile `.env` has a key that also exists in root `.env`, the profile value wins. This causes silent breakage (e.g., profile `.env` sets `OBSIDIAN_VAULT_PATH` to a sandboxed path, overriding the correct root value).
- **Tools enable is per-profile and per-platform**: `hermes --profile researcher tools enable browser` only enables it for the CLI platform. If the profile runs via gateway (Telegram, etc.), you may need to enable it per platform.
- **Tools enable requires `/reset` or new session**: Tool changes are snapshotted at session start. They don't take effect mid-conversation.
