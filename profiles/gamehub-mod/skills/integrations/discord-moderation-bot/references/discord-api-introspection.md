# Discord API introspection (curl)

Use **curl** for raw Discord REST calls. Python `urllib` gets Cloudflare
**HTTP 1010** ("Access denied based on browser signature") even with a valid
token — but the real Hermes gateway client connects fine, so a 1010 probe
failure is NOT proof of a bad token. `curl` uses a different TLS fingerprint
and passes.

## List the guilds a bot is in (find DISCORD_GUILD_ID)
```bash
TOKEN=$(grep -E '^DISCORD_BOT_TOKEN=' ~/.hermes/profiles/<profile>/.env | head -1 | cut -d= -f2-)
curl -s -m 20 -H "Authorization: Bot $TOKEN" -H "Accept: application/json" \
  "https://discord.com/api/v10/users/@me/guilds"
```

## Channels + roles of a guild G
```bash
G=<id>   # replace with the real guild id
curl -s -m 20 -H "Authorization: Bot $TOKEN" "https://discord.com/api/v10/guilds/$G/channels"
curl -s -m 20 -H "Authorization: Bot $TOKEN" "https://discord.com/api/v10/guilds/$G/roles"
```

## Reading the role hierarchy (critical for Muted enforcement)
- Sort roles by `position` **descending** — top of the list = highest power.
  The JSON array index is NOT the position; trust the `position` integer.
- A role **deny** only outranks an **allow** from an equal-or-lower role. So
  `Muted` MUST sit **above** `@everyone`/`Member` or muting silences nobody.
- The bot's own role must sit **above `Muted`** (can apply/remove it) but
  **below `Moderator`** (can never touch a mod).
- `managed: true` = role was created by / for a bot (slash-command sync).
  Expected; position it by hand regardless.

## From output → .env
Set `DISCORD_GUILD_ID=$G`, `DISCORD_ALLOWED_ROLES=<human-mod-role-id>`
(NOT the bot's own role), `DISCORD_FREE_RESPONSE_CHANNELS`/`DISCORD_ALLOWED_CHANNELS`
= staff channel ids, `DISCORD_IGNORED_CHANNELS` = member channel ids.
