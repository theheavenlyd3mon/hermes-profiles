# Discord Multi-Bot Setup Reference

## Architecture

Each Discord bot = one Hermes profile = one Discord Developer Portal application = one unique token.

```
Discord Server
+-- @Hermes Senna (coordinator)     <- senna profile, DISCORD_BOT_TOKEN
+-- @Hermes Researcher              <- researcher profile
+-- @Hermes Secretary               <- secretary profile
+-- @Hermes Coder                   <- coder profile
+-- @Hermes Architect               <- architect profile
+-- @Hermes Foreman                 <- foreman profile
+-- @Hermes Graphics                <- designer profile (auto_thread: false)
```

## Setup Checklist Per Bot

1. **Discord Developer Portal** - New Application -> name it -> Bot tab -> Add Bot
2. **Privileged Gateway Intents** - enable Message Content + Server Members
3. **Reset Token** - copy immediately (shown once)
4. **OAuth2 URL Generator** - scopes: bot, applications.commands; permissions: Send Messages, Read History, Embed Links, Attach Files, Use Slash Commands, Manage Channels, Add Reactions
5. **Invite URL** - open in browser, select server, Authorize
6. **Profile .env** - break symlink, write unique token
7. **config.yaml** - discord: block with require_mention: true
8. **Launch gateway** - launchctl kickstart or manual start
9. **Verify** - check gateway.log for "Connected as <botname>"

**⚠️ Message Content Intent — The #1 Failure**: If the gateway log shows `discord connect timed out after 30s` and keeps retrying, the bot's Message Content Intent is not enabled in the Developer Portal. This is the most common onboarding failure. Fix: Developer Portal → Bot → Privileged Gateway Intents → enable Message Content Intent + Server Members Intent → Save → restart gateway.

## Breaking .env Symlink & Writing Unique Token

Profiles from `hermes profile create` have .env symlinked to ~/.hermes/.env.
For multi-bot Discord, each profile needs its own .env with its own token.

```python
import re, os

tokens = {
    'coder':     'PASTE_TOKEN_1',
    'architect': 'PASTE_TOKEN_2',
    'foreman':   'PASTE_TOKEN_3',
}

for profile, token in tokens.items():
    env_path = os.path.expanduser(f'~/.hermes/profiles/{profile}/.env')
    # Break symlink if present, copy shared .env as base
    if os.path.islink(env_path):
        os.remove(env_path)
        shared = os.path.expanduser('~/.hermes/.env')
        with open(shared, 'r') as f:
            content = f.read()
        with open(env_path, 'w') as f:
            f.write(content)
    # Replace token
    with open(env_path, 'r') as f:
        content = f.read()
    content = re.sub(r'^DISCORD_BOT_TOKEN=.*', f'DISCORD_BOT_TOKEN={token}', content, flags=re.MULTILINE)
    with open(env_path, 'w') as f:
        f.write(content)
    print(f'{profile}: done')
```

**CRITICAL:** Tokens are masked at read time by Hermes' credential layer.
You CANNOT verify token values via grep or read_file.
The only reliable verification is the gateway log showing "Connected as <botname>".

## Creating a Channel via Discord API

Use an existing bot's token to create channels for new bots:

```bash
# Get existing bot token
TOKEN=$(cat ~/.hermes/profiles/senna/.env | grep DISCORD_BOT_TOKEN | cut -d= -f2)

# Create text channel
curl -s -X POST \
  -H "Authorization: Bot $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"design-studio","type":0,"topic":"Designer bot — UI/graphics/image generation"}' \
  https://discord.com/api/v10/guilds/<id>/channels
# Returns: {"id":"<new-channel-id>","name":"design-studio",...}
```

## Common Pitfalls

### 401 Unauthorized / LoginFailure
- Token was regenerated in Developer Portal (Reset Token invalidates old one)
- Copy-paste truncated the token (tokens are ~72 bytes)
- Solution: Reset token again, copy carefully, update .env, restart gateway

### Discord Connect Timeout (30s)
- **Message Content Intent** not enabled in Developer Portal
- Bot connects to gateway but never receives READY event
- Fix: Developer Portal → Bot → Privileged Gateway Intents → enable Message Content + Server Members
- Restart gateway after enabling

### Port 8642 Already in Use
- Multiple gateways with api_server all try to bind port 8642
- Non-fatal for Discord - Discord still connects
- Fix: Disable api_server in config.yaml or assign unique ports

### require_mention Setting
- With multiple bots in same server, set require_mention: true
- Without this, every bot responds to every message

### auto_thread: false for Direct-Reply Bots
- Most bots use `auto_thread: true` (creates threads for conversations)
- Some bots (like designer) use `auto_thread: false` for quick in-channel iteration
- Tradeoff: conversations are visible to everyone, no thread isolation
- When to use: creative/visual bots, quick-reference bots, any bot where threading adds friction

### Gateway Restart
- Launchd-managed: launchctl kickstart -k ai.hermes.gateway-<name>
- Manual: kill existing, then background=true in terminal tool
- Never use nohup in foreground terminal mode

## Channel Structure (Current - Server <id>)

```
#your-orchestrator-channel         - @Senna, coordinator (ID: <channel-id>)
#research-lab     - @Researcher (ID: <channel-id>)
#engineering      - @Coder (ID: <channel-id>)
#architecture     - @Architect (ID: <channel-id>)
#writing-desk     - @Secretary (ID: <channel-id>)
#operations       - @Foreman (ID: <channel-id>)
#market-intel     - @Oracle (ID: <channel-id>)
#design-studio    - @Designer (ID: <channel-id>) — auto_thread: false
#bot-ops          - testing, cron outputs (ID: <channel-id>)
```

## Launchd Persistence (Modern macOS)

**Do NOT use `launchctl load`** — deprecated, fails with I/O error.

**Correct approach:**
1. Write plist to real `~/Library/LaunchAgents/` (NOT sandboxed path)
2. `launchctl bootstrap gui/501 <absolute-path-to-plist>`
3. `launchctl kickstart -k gui/501/<label>` to restart

**Pitfall:** Shell heredocs and `write_file` tool write to sandboxed paths. Verify plist location with `ls -la ~/Library/LaunchAgents/`.

**Minimal plist** (replace `<name>` with profile name):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>ai.hermes.gateway-<name></string>
    <key>ProgramArguments</key>
    <array>
        <string>~/.hermes/profiles/senna/hermes-agent/venv/bin/python</string>
        <string>-m</string><string>hermes_cli.main</string>
        <string>--profile</string><string><name></string>
        <string>gateway</string><string>run</string><string>--replace</string>
    </array>
    <key>WorkingDirectory</key><string>~/.hermes/profiles/senna/hermes-agent</string>
    <key>StandardOutPath</key><string>~/.hermes/profiles/<name>/logs/gateway.log</string>
    <key>StandardErrorPath</key><string>~/.hermes/profiles/<name>/logs/gateway.error.log</string>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
</dict>
</plist>
```

## Token Writing Technique (Critical)

**The `write_file` tool and shell heredocs both interpret special sequences, truncating tokens.** Discord bot tokens contain dots and get truncated.

**Reliable method — use Python directly:**
```bash
python3 << 'PYEOF'
import os, re

token = 'YOUR_TOKEN_HERE'  # paste directly, no shell escaping
env_path = os.path.expanduser('~/.hermes/profiles/<profile>/.env')

# Break symlink if present
if os.path.islink(env_path):
    os.remove(env_path)
    with open(os.path.expanduser('~/.hermes/.env'), 'r') as f:
        base = f.read()
    with open(env_path, 'w') as f:
        f.write(base)

# Write token
with open(env_path, 'r') as f:
    content = f.read()
content = re.sub(r'^DISCORD_BOT_TOKEN=.*', f'DISCORD_BOT_TOKEN={token}', content, flags=re.MULTILINE)
with open(env_path, 'w') as f:
    f.write(content)

# Verify length
with open(env_path, 'rb') as f:
    raw = f.read()
idx = raw.find(b'DISCORD_BOT_TOKEN')
val = raw[idx+20:raw.find(b'\n', idx+20)]
print(f'Token length: {len(val)} bytes')  # Should be ~72
PYEOF
```

**CRITICAL:** Tokens are masked at read time. Only verify via gateway log "Connected as <botname>".
