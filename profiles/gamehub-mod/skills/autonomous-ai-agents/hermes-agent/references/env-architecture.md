# .env Architecture: Root vs Profile API Keys

## Loading order

Hermes loads **two** `.env` files at startup, in order:

1. **Root**: `~/.hermes/.env` — global defaults, shared across all profiles
2. **Profile**: `~/.hermes/profiles/<name>/.env` — profile-specific overrides

Profile values **win** over root values when the same key is defined in both. This
means root `.env` functions as a fallback — a key in root is available to every
profile unless that profile explicitly overrides it.

## When to use each

| Location | Purpose | Example |
|----------|---------|---------|
| `~/.hermes/.env` | **Canonical source** — all keys live here unless overridden | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`, `OPENROUTER_API_KEY`, `GITHUB_TOKEN`, `DEEPSEEK_API_KEY`, common timeout/port config |
| `~/.hermes/profiles/senna/.env` | Overrides only — for keys that genuinely differ per-profile | Profile-scoped `OBSIDIAN_VAULT_PATH`, `FABRIC_DIR`, provider keys only Senna uses |

## Rule of thumb: root is the canonical source

**Prefer root `.env` for everything.** Profile `.env` is for overrides — keys
whose value genuinely differs per profile (e.g., `OBSIDIAN_VAULT_PATH` pointing
to a different vault). If a key has the same value across all profiles, it
belongs in root only.

This mirrors the plugins pattern: the canonical source is in `~/.hermes/` and
profiles symlink to it. Same logic for `.env` — root is the single source of
truth, profile overrides are the exception.

### When NOT to use a profile override

**Platform keys (e.g., `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`):**
These used to be recommended for profile `.env` because \"only that profile's
gateway uses them.\" In practice, this creates a two-gateway problem: the
default profile's gateway runs but can't serve Telegram, and the profile
gateway sits idle. The fix is to **move platform keys to root `.env` and make
the working profile the default** (`hermes profile use <name>`). This way:
- One gateway process (clean, no confusion)
- `hermes gateway start` \"just works\"
- The old default profile's gateway can be stopped

For the full consolidation workflow, see the Gateway Consolidation section
in the parent `hermes-agent/skills/SKILL.md`.

**Do not put a key in a profile `.env` unless actual profile isolation is
needed** — e.g., Senna talks to Telegram, Foreman talks to Slack — and they
need different gateways. If you only use one profile's gateway, put everything
in root.

**Multi-bot Discord exception:** When running multiple profiles as separate
Discord bots, each profile needs its own `DISCORD_BOT_TOKEN` in its profile
`.env`. The root `.env` token is shared by default; profile `.env` overrides
it. See `references/discord-multi-bot-setup.md` for the full pattern.

## How to verify which .env is active

Run `hermes config`. The output shows:

```
◆ Paths
  Secrets:      ~/.hermes/profiles/senna/.env
```

This is the **effective** `.env` the current session loaded. The root `.env` is
not listed here — it's pre-loaded before the profile.

## The archive/ directory trap

`~/.hermes/archive/` holds **state snapshots**, not config. Never place or edit
API keys in `~/.hermes/archive/.env`. Snapshot `.env` files exist for rollback
audit only.

## Secure key addition workflow

When the user wants to add a new API key without exposing it in chat:

```bash
# 1. Use read -s to type the key directly in the terminal
#    (nothing appears on screen or in chat history)
read -s NEW_KEY_NAME
echo "NEW_KEY_NAME=$NEW_KEY_NAME" >> ~/.hermes/.env

# 2. Verify it was written correctly (masked)
grep "^NEW_KEY_NAME" ~/.hermes/.env

# 3. Confirm Hermes picks it up
hermes config
# Check "Secrets:" path points to the correct .env
```

**Important:** The `read -s` command above does NOT echo the typed value — no
keystrokes appear in the terminal history or in Hermes's tool output. This is
the recommended pattern for secret entry.

**Which .env to write to:**
- If the key should be shared across all profiles → write to `~/.hermes/.env`
- If the key is profile-specific → write to `~/.hermes/profiles/<name>/.env`
- Check `hermes config` for "Secrets:" path to confirm which `.env` is active

## Consolidation: removing duplicate keys

When you have the same key populated in both root and profile `.env`, the
profile value wins (shadows the root). To consolidate:

```bash
# 1. Check for duplicates
comm -12 \
  <(grep "=" ~/.hermes/.env | grep -v "^#" | grep -v "^$" | cut -d= -f1 | sort -u) \
  <(grep "=" ~/.hermes/profiles/senna/.env | grep -v "^#" | grep -v "^$" | cut -d= -f1 | sort -u)

# 2. For keys with the SAME value in both, remove from profile .env
#    (root will provide the value — that's the single canonical source)
cp .env .env.bak                                        # backup first
sed -i '' '/^OPENROUTER_API_KEY=.*/d' .env              # remove duplicate

# 3. Verify removal
grep "^OPENROUTER_API_KEY\|^GITHUB_TOKEN" .env || echo "Clean — no duplicates"

# 4. For keys with DIFFERENT values, keep both intentionally
#    (e.g., OBSIDIAN_VAULT_PATH pointing to different vaults)
```

**Important:** Do NOT remove keys that have DIFFERENT values in root vs profile
(like `OBSIDIAN_VAULT_PATH` or `FABRIC_DIR`). Those differences are intentional
and serve profile isolation.

**For platform keys (Telegram, Discord, etc.):** If they live in a profile `.env`
and the root has them commented out, consider the gateway consolidation workflow
instead (see the Gateway Consolidation section in `hermes-agent/SKILL.md`).
The pattern is: move the keys to root `.env`, make the working profile the default,
stop the old default gateway. This eliminates the two-gateway problem.

## Provider setup + .env workflow

Complete flow for adding a new model provider (e.g., DeepSeek):

```bash
# 1. Add API key to root .env (secure, via read -s)
echo "DEEPSEEK_API_KEY=$KEY" >> ~/.hermes/.env

# 2. Run hermes model (interactive — requires terminal)
hermes model
# Select provider → DeepSeek
# Enter base URL → https://api.deepseek.com
# Select model → deepseek-v4-flash or deepseek-v4-pro

# 3. Verify configuration
hermes config | grep -A3 "Model:"
# Should show: {'default': 'deepseek-v4-*', 'provider': 'deepseek', 'base_url': '...'}

# 4. Quick connectivity test
hermes chat -q "Hi"
```

The provider selection is stored in the profile's `config.yaml` (under `model:`),
not in `.env`. The `.env` holds only the secret — `config.yaml` holds which
provider/model uses it.

## Pitfalls

### 1. Duplicate keys with different values

If root has `OBSIDIAN_VAULT_PATH=~/Hermes Vault/Hermes` and the
profile has `OBSIDIAN_VAULT_PATH=~/.hermes/profiles/senna/vault`,
the profile value wins. This is intentional — profiles can point at different
vaults — but it must be deliberate. Always check both files when debugging
path-dependent features (Icarus, GBrain, Obsidian integration).

### 2. Big templates in every .env

The default `.env` template is ~420 lines of commented documentation. When both
root and profile `.env` are created from the same template, they're identical
except for the handful of uncommented key=value lines. This is normal — the
template comments aren't loaded as variables; only the uncommented `KEY=val`
lines matter.

### 3. Adding a key to the wrong file

**Scenario**: Adding `DEEPSEEK_API_KEY` to root but Senna's profile `.env` 
already has it. Since the profile wins, the root value is shadowed. If you're
rotating keys, update both or pick one file as canonical and remove the
duplicate from the other.

**Verification:** After adding a key, check `hermes config` → "Secrets:" path
to confirm which `.env` is loaded, then check that file for the key.

### 4. Nested home/.hermes/ directory quirk

The profile directory may contain a `home/.hermes/` subdirectory (created by
profile sandboxing). This creates a recursive directory structure where
`~/.hermes/profiles/senna/home/.hermes/` mirrors `~/.hermes/`. `.env` files in
this nested path can cause confusion — the root and profile `.env` at the
canonical paths are what Hermes actually loads, not the nested copies.

When searching for `.env` files, use absolute paths or filter out known
nested/home paths:

```bash
find ~/.hermes -name ".env" -not -path "*/home/*" -not -path "*/state-snapshots/*"
```

### 5. Secrets security

Hermes loads `.env` files from disk at startup. The files are plaintext on disk.
For additional security:
- Restrict file permissions: `chmod 600 ~/.hermes/.env ~/.hermes/profiles/*/.env`
- Or use `security.redact_secrets: true` in config.yaml to mask secrets from
  tool output and conversation logs

## Quick audit checklist

When diagnosing key-related issues:

```bash
# Check which .env is active
hermes config | grep "Secrets:"

# Check which keys each .env defines
grep "=" ~/.hermes/.env | grep -v "^#" | grep -v "^$"
grep "=" ~/.hermes/profiles/senna/.env | grep -v "^#" | grep -v "^$"

# Find duplicate keys across both files
comm -12 \
  <(grep "=" ~/.hermes/.env | grep -v "^#" | grep -v "^$" | cut -d= -f1 | sort -u) \
  <(grep "=" ~/.hermes/profiles/senna/.env | grep -v "^#" | grep -v "^$" | cut -d= -f1 | sort -u)

# Check for any profile .env files with keys
for f in ~/.hermes/profiles/*/.env; do
  [ -s "$f" ] && echo "$f: $(grep -c "=" "$f") lines" || true
done

# Verify file permissions are locked down
ls -la ~/.hermes/.env ~/.hermes/profiles/senna/.env
```
