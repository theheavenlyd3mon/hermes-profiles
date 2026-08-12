# Launchd Service Registration — Modern macOS

## The Working Method (2026-05-26)

On modern macOS (10.10+), `launchctl load` is deprecated and `launchctl bootstrap gui/501 <plist>` fails with "Input/output error" if any process from the old service is still running. The reliable method:

```bash
# Step 1: Kill any running gateway process for this profile
pkill -f "profile <name> gateway" 2>/dev/null
sleep 2

# Step 2: Enable the service (registers the plist with launchd)
launchctl enable gui/$(id -u)/ai.hermes.gateway-<name>

# Step 3: Start/restart it
launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway-<name>
```

**Why this works:** `enable` registers the plist without trying to start it. `kickstart -k` sends SIGTERM to any existing instance and starts fresh. No bootstrap I/O errors.

**Plist location:** `~/Library/LaunchAgents/ai.hermes.gateway-<name>.plist`
**Label must match filename** (without `.plist`).

## Plist Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.hermes.gateway-<name></string>
    <key>ProgramArguments</key>
    <array>
        <string>~/.hermes/profiles/senna/hermes-agent/venv/bin/python</string>
        <string>-m</string>
        <string>hermes_cli.main</string>
        <string>--profile</string>
        <string><name></string>
        <string>gateway</string>
        <string>run</string>
        <string>--replace</string>
    </array>
    <key>WorkingDirectory</key>
    <string>~/.hermes/profiles/senna/hermes-agent</string>
    <key>StandardOutPath</key>
    <string>~/.hermes/profiles/<name>/logs/gateway.log</string>
    <key>StandardErrorPath</key>
    <string>~/.hermes/profiles/<name>/logs/gateway.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

## Multi-Gateway Port Strategy

When running 5+ Discord bot gateways, each with `api_server` enabled, they all try to bind port 8642 and fail with "Port 8642 already in use" errors. **Fix: Disable `api_server` for bot-only profiles.** Only the coordinator gateway (Senna) needs it.

```yaml
# In each bot profile's config.yaml
platforms:
  api_server:
    enabled: false
```

Verify: `lsof -i :8642` should show exactly one PID (Senna).

## Telegram Disable

Telegram auto-enables when `TELEGRAM_BOT_TOKEN` env var is present — even if you only want Discord. To disable: comment out `TELEGRAM_BOT_TOKEN` in `.env`, or set `telegram: enabled: false` in `config.yaml`.

**Failure scenario:** Discord-only setup but `TELEGRAM_BOT_TOKEN` still set → gateway tries Telegram, token already in use by another gateway → exit → launchd KeepAlive restart → infinite loop.
