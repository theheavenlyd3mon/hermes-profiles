# .env Layering Architecture

Hermes uses a **two-tier `.env` system**: a root shared file and optional per-profile overrides.

## Structure

```
~/.hermes/.env                        ← Root (shared, ~186 keys)
~/.hermes/profiles/<name>/.env        ← Profile-specific (1-4 keys typically)
```

## How It Works

1. **Root `~/.hermes/.env`** is the canonical source of shared API keys, tokens, and paths.
   - Contains keys like: `OPENROUTER_API_KEY`, `GITHUB_TOKEN`, `HF_TOKEN`, `FAL_KEY`, `GROQ_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `BRAVE_API_KEY`, `NOTION_API_KEY`, `NVIDIA_API_KEY`, `ALPHA_VANTAGE_API_KEY`, `AI_TRADER_API_KEY`, `OBSIDIAN_VAULT_PATH`, `SHARED_FABRIC_DIR`, `SHARED_VAULT_PATH`, terminal/browser config, and provider-specific base URLs.
   - This file is loaded by the Hermes runtime and cascades to all profiles.

2. **Profile `.env`** files contain **profile-specific overrides or additions**.
   - Common pattern: Xiaomi MiMo profiles have `XIAOMI_API_KEY` + `XIAOMI_BASE_URL` (+ possibly `XIAOMI_MODEL`) in their profile `.env` because that provider is only used by certain profiles.
   - Some profiles have a minimal `.env` with just `OPENROUTER_API_KEY` — these are **redundant copies** of the root key and could be cleaned up.

## Profile .env Patterns (as of 2026-06)

| Pattern | Keys | Profiles |
|---------|------|----------|
| Xiaomi MiMo (4 keys) | `XIAOMI_API_KEY`, `XIAOMI_BASE_URL`, + 2 others | senna, code, creative, finance, infra, research, security |
| Xiaomi only (2 keys) | `XIAOMI_API_KEY`, `XIAOMI_BASE_URL` | cyber-blue (×5), cyber-red, mlops, ue5 |
| OpenRouter only (1 key) | `OPENROUTER_API_KEY` | business, communication, homelab, media, social |
| Mixed (3 keys) | varies | knowledge |

## Pitfalls

### `test -f` can fail on root `.env` even when it exists

The Hermes terminal tool (especially inside `execute_code`'s `terminal()` wrapper) may not correctly resolve `~/.hermes/.env` with `test -f`. Use absolute paths:

```bash
# WRONG — may report false negative
test -f ~/.hermes/.env && echo "exists" || echo "missing"

# RIGHT — use absolute path
test -f /Users/$USER/.hermes/.env && echo "exists" || echo "missing"

# Or just check with grep
grep -c '=' /Users/$USER/.hermes/.env
```

### Profile `.env` overrides root for same key

If a profile `.env` defines the same key as root, the **profile value wins**. This is intentional for provider-specific overrides (e.g., different `OPENROUTER_API_KEY` for a specific profile) but can cause confusion if accidental.

### Don't archive root `.env` without checking profile dependencies

Some profiles may rely on root `.env` for keys they don't define locally. Archiving root breaks those profiles silently (401 errors, missing tokens).

## Verification

```bash
# Count root keys
grep -cE '^[A-Z_]+=' /Users/$USER/.hermes/.env

# List root key names
grep -oE '^[A-Z_]+(?==)' /Users/$USER/.hermes/.env | sort

# Compare profile keys against root (find redundancies)
for d in /Users/$USER/.hermes/profiles/*/; do
  p=$(basename "$d")
  f="$d/.env"
  [ -f "$f" ] || continue
  while IFS='=' read -r key val; do
    [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
    if grep -q "^${key}=" /Users/$USER/.hermes/.env 2>/dev/null; then
      echo "REDUNDANT: $p/$key (also in root)"
    else
      echo "PROFILE-ONLY: $p/$key"
    fi
  done < <(grep -E '^[A-Z_]+=' "$f")
done
```
