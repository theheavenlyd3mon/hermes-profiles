# Discord Fleet Repair Playbook

## Symptom

Post-17-profile-redesign audit shows one bot (senna) is Discord-active; every other specialist profile is running a gateway but has no Discord presence.

## Root-Cause Pattern

The rename/merge path can leave the new profile `.env` with a truncated or missing `DISCORD_BOT_TOKEN`. The gateway then boots normally (no auth check at platform-adapter startup until after connection), but the bot never authenticates. Related drift:

- `API_SERVER_ENABLED=true` left in specialist profiles.
- `free_response_channels` pointing at senna’s hub channels instead of the bot’s home channel.
- `DISCORD_HOME_CHANNEL` undefined after copy-paste.

## Minimal Repair Sequence

1. **Give the bot a real token**
   - Inherit old token (same token source, different profile) OR create new Application in Discord Developer Portal.
   - Always verify: `curl -s https://discord.com/api/v10/users/@me -H "Authorization: Bot $TOKEN"`
   - Write to `<profile>/.env` as `DISCORD_BOT_TOKEN=` plus `DISCORD_HOME_CHANNEL=<channel-id>` and `DISCORD_ALLOWED_USERS=<user-id>`.

2. **Add authoritative discord config**
   - Use the bot’s actual home channel ID in `free_response_channels`.
   - Fleet-wide standard: `auto_thread: true`, `thread_require_mention: true`, `history_backfill: true`, `reactions: true`.
   - `allowed_channels: ''` unless intentional channel whitelist is needed.

3. **Disable API server on specialists**
   - Remove `API_SERVER_ENABLED=` from `.env`.
   - Avoid `hermes config set platforms.api_server.enabled false` when a `platforms:` block already exists; use `patch` directly to merge or blank the block.

4. **Restart the gateway**
   - `hermes --profile <name> gateway restart` or kill/respawn.
   - Verify “Connected as <bot username>” in `logs/gateway.log` within 10 s.

## Migration Token Map

```
code ← coder
creative ← designer
research ← researcher
finance ← oracle
knowledge ← secretary
infra ← foreman
security ← architect
```

If profile rename dropped a token: source it from the predecessor profile’s `.env` and verify before restarting.

## What Good Looks Like

- `DISCORD_BOT_TOKEN` present and HTTP-verifies as the expected bot user.
- `discord:` section present with at least `require_mention`, `auto_thread`, `thread_require_mention`, `free_response_channels`.
- One home channel only for specialists; coordinator may list multiple.
- `API_SERVER_ENABLED` absent from all non-coordinator profiles.
- Log tail ends with Discord “Connected as …”

Getting here often requires three profiles in one batch: **token + discord config + api_server cleanup**.