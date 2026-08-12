# Multi-Bot Discord Setup: Separate Tokens per Profile

## When to use this pattern

Use this when running multiple Hermes profiles as separate Discord bots in the same server. Each profile needs its own Discord bot application with its own token.

## Architecture

```
Discord Server
├── @SennaBot        → senna profile    → gateway (PID X)
├── @ResearcherBot   → researcher profile → gateway (PID Y)
├── @SecretaryBot    → secretary profile  → gateway (PID Z)
└── ...
```

Each bot = one Discord Developer Application + one `DISCORD_BOT_TOKEN` + one Hermes gateway process.

## Why separate tokens?

One Discord bot token = one bot identity. Two profiles sharing the same token would both respond as the same bot, causing duplicate/conflicting replies. Each profile needs its own token so it appears as a distinct bot user in the server.

## Setting up each bot

For EACH profile you want as a separate bot:

1. Go to https://discord.com/developers/applications
2. **New Application** → name it (e.g., "Hermes Researcher")
3. **Bot** tab → **Add Bot** → **Reset Token** → copy the token
4. **Privileged Gateway Intents** → enable:
   - ✅ Message Content Intent
   - ✅ Server Members Intent
5. **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Permissions: Send Messages, Read Message History, Embed Links, Attach Files, Use Slash Commands, Manage Channels, Add Reactions
6. Open the invite URL → select your server → Authorize

## Token placement: profile `.env` overrides root

The `.env` loading order is:
1. `~/.hermes/.env` — root (shared defaults)
2. `~/.hermes/profiles/<name>/.env` — profile (overrides root)

**For multi-bot, put each profile's `DISCORD_BOT_TOKEN` in that profile's `.env`, NOT in root.**

If root `.env` has `DISCORD_BOT_TOKEN=AAA` and researcher `.env` has `DISCORD_BOT_TOKEN=BBB`, the researcher profile uses BBB (profile wins). This lets each profile have its own token.

### Verify no root override conflict

```bash
# Check root .env for DISCORD_BOT_TOKEN
grep "^DISCORD_BOT_TOKEN" ~/.hermes/.env

# Check profile .env
grep "^DISCORD_BOT_TOKEN" ~/.hermes/profiles/researcher/.env
```

If root has an unmasked `DISCORD_BOT_TOKEN`, it becomes the default for profiles that don't override it. For multi-bot, either:
- Remove it from root (each profile supplies its own), OR
- Keep it as the "main" bot token and have only the additional profiles override it.

## Profile `.env` structure for multi-bot

`~/.hermes/profiles/researcher/.env`:
```bash
DISCORD_BOT_TOKEN=<this bot's token>
DISCORD_ALLOWED_USERS=968599126101098547
# No need to repeat OPENROUTER_API_KEY etc. — inherits from root
```

## Debugging: token collision

**Symptom**: Two bots respond to the same message, or the wrong bot responds.

**Cause**: Two profiles sharing the same `DISCORD_BOT_TOKEN` (likely both reading from root `.env`).

**Fix**:
```bash
# Check which token each profile sees
for f in ~/.hermes/profiles/*/.env; do
  [ -f "$f" ] && echo "=== $f ===" && grep "^DISCORD_BOT_TOKEN" "$f"
done
```

Each profile should show a DIFFERENT token. If two show the same token, that's the problem.

## Starting multiple gateways

Each profile runs its own gateway process:

```bash
# Check all gateway statuses
hermes gateway list

# Start a specific profile's gateway
hermes --profile researcher gateway start
```

Verify all are running:
```bash
hermes gateway list
```

## Common pitfalls

### 1. Forgetting to enable Message Content Intent
Bot joins server but never responds. Fix: Developer Portal → Bot → enable Message Content Intent.

### 2. Forgetting Manage Channels permission
Bot can't create/edit channels. Fix: OAuth2 URL Generator → enable Manage Channels permission → re-invite bot.

### 3. All bots respond to every message
If `require_mention` is false and multiple bots share a channel, they all respond. Fix: Set `require_mention: true` in each profile's `config.yaml` discord section, and @mention the specific bot you want.

### 4. Profile `.env` doesn't exist yet
If `~/.hermes/profiles/<name>/.env` doesn't exist, create it:
```bash
touch ~/.hermes/profiles/researcher/.env
echo "DISCORD_BOT_TOKEN=<token>" >> ~/.hermes/profiles/researcher/.env
```

### 5. Token in wrong `.env`
If you edit root `.env` thinking it's profile-specific, all profiles get that token. Always verify which `.env` file you're editing.

## Channel management

For bots that need to create/edit Discord channels, use curl + Discord API. Each bot needs `MANAGE_CHANNELS` permission and `DISCORD_GUILD_ID` in its profile `.env`.
