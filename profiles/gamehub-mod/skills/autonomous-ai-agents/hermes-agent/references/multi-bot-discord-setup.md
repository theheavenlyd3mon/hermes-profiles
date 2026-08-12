# Multi-Bot Discord Setup — Profile Isolation Notes

## The .env Symlink Problem

**Symptom:** When adding Discord bot tokens to `~/.hermes/.env`, the change appears for all profiles — or pasting separate tokens results in duplicate/mangled entries.

**Cause:** Profile `.env` files at `~/.hermes/profiles/<name>/.env` are **symlinks** pointing to the central `~/.hermes/.env`. Editing "any profile's .env" edits all of them.

**Diagnosis:**
```bash
ls -la ~/.hermes/profiles/<name>/.env
# If it shows ".env -> ~/.hermes/.env", it's a symlink
```

**Fix — Per-Profile .env Files:**

1. Back up the existing `.env` (`.env.bak` exists from before symlink):
   ```bash
   ls ~/.hermes/profiles/<name>/.env.bak
   ```

2. Remove symlink, restore from backup:
   ```bash
   rm ~/.hermes/profiles/<name>/.env
   cp ~/.hermes/profiles/<name>/.env.bak ~/.hermes/profiles/<name>/.env
   ```

3. Add the profile-specific Discord token:
   ```bash
   echo "" >> ~/.hermes/profiles/<name>/.env
   echo "# Discord" >> ~/.hermes/profiles/<name>/.env
   echo "DISCORD_BOT_TOKEN=*** profile's bot token>" >> ~/.hermes/profiles/<name>/.env
   echo "DISCORD_ALLOWED_USERS=<your discord user id>" >> ~/.hermes/profiles/<name>/.env
   ```

4. Verify token length (should be 72 chars):
   ```bash
   python3 -c "
   with open('~/.hermes/profiles/<name>/.env') as f:
       for line in f:
           if line.startswith('DISCORD_BOT_TOKEN=***               token = line.strip().split('=', 1)[1]
               print(f'Token length: {len(token)} chars (should be 72)')
   "
   ```

**IMPORTANT:** Hermes DISPLAY masks credentials — `***` in terminal output does NOT mean the value is truncated. The actual stored value is complete. Always verify with python, not eyeballing terminal output.

## Multi-Bot Discord Architecture

Each Discord bot = one Hermes profile = one `DISCORD_BOT_TOKEN`. Tokens cannot be shared across profiles.

### Adding a New Discord Bot

1. **Discord Developer Portal** (manual browser steps):
   - New Application → name it → Bot tab → Add Bot
   - Enable: Message Content Intent + Server Members Intent
   - Reset Token → copy it
   - OAuth2 → URL Generator: scopes `bot` + `applications.commands`
   - Permissions: Send Messages, Read History, Embed Links, Attach Files, Slash Commands, Manage Channels, Add Reactions
   - Open invite URL → select server → Authorize

2. **Profile .env** (see symlink fix above)

3. **Config:** Verify `discord:` block exists in profile's `config.yaml` and `hermes-discord` is in the platforms toolset

4. **SOUL.md:** Add a `## Discord` section with identity and role description

5. **Install & start:**
   ```bash
   hermes gateway install --profile <name>
   hermes gateway list
   ```

### Free Model for All Bots

```bash
hermes config set model.default "deepseek/deepseek-v4-flash:free" --profile <name>
hermes config set model.provider nous --profile <name>
```

### Port Conflicts (Expected)

Only one gateway binds the API server port. Additional gateways log `api_server failed to connect` — this is non-blocking. Discord works without it.

### Key File Paths

| What | Path |
|------|------|
| Shared .env | `~/.hermes/.env` |
| Profile .env | `~/.hermes/profiles/<name>/.env` |
| Profile .env backup | `~/.hermes/profiles/<name>/.env.bak` |
| Profile config | `~/.hermes/profiles/<name>/config.yaml` |
| Gateway log | `~/.hermes/profiles/<name>/logs/gateway.log` |
| Gateway errors | `~/.hermes/profiles/<name>/logs/gateway.error.log` |
| LaunchAgent | `~/Library/LaunchAgents/ai.hermes.gateway-<name>.plist` |
| SOUL.md | `~/.hermes/profiles/<name>/SOUL.md` |
