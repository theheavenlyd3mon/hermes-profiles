# Discord Developer Portal Walkthrough — Hermes Moderation Bot

Condensed from Discord docs + Hermes gateway docs, verified 2026-07-09.
Full Hermes Discord doc: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord

## Step 1 — New Application
- Go to https://discord.com/developers/applications
- New Application (top-right) → name it (e.g. `Gamehub-mod`) → accept ToS → Create
- On General Information, copy the **Application ID** (needed for invite URL)

## Step 2 — Create the Bot user
- Left sidebar → Bot
- Discord auto-creates a bot; set username
- Authorization Flow: **Public Bot = ON** (for easy install link), **Require OAuth2 Code Grant = OFF**
- (optional) avatar

## Step 3 — Privileged Gateway Intents (CRITICAL)
On Bot page → Privileged Gateway Intents:
- **Server Members Intent = ON** (resolve usernames, required)
- **Message Content Intent = ON** (bot must read message text; without it, messages arrive empty)
- Presence Intent = optional
- Click Save Changes

## Step 4 — Get the token
- Bot page → Token → Reset Token → 2FA if prompted → copy immediately (shown once)
- Store in password manager. NEVER commit to git / share.
- Do NOT grant Administrator.

## Step 5 — Build invite URL
Use the CORRECT moderation integer **1494917180614** (includes Manage Roles).
Option A (recommended, Public Bot ON): Installation → Guild Install → Install Link = Discord Provided Link →
Default Install Settings → Scopes: `bot` + `applications.commands` → Permissions: enter `1494917180614`.

Option B (manual): replace YOUR_APP_ID:
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=1494917180614

## Step 6 — Invite to server
- Open URL → Add to Server → pick your server → Authorize → CAPTCHA
- Bot appears OFFLINE until gateway starts

## Step 7 — Your User ID (for DISCORD_ALLOWED_USERS)
- Discord → Settings → Advanced → Developer Mode ON
- Right-click your name → Copy User ID
- Same menu copies Channel IDs and Server IDs (right-click the channel/server)

## Hermes-side config (next phase)
Add to profile `.env` (see SKILL.md), then `hermes gateway`.
Key env vars: DISCORD_BOT_TOKEN, DISCORD_GUILD_ID, DISCORD_ALLOWED_USERS,
DISCORD_ALLOWED_ROLES, DISCORD_HOME_CHANNEL, DISCORD_FREE_RESPONSE_CHANNELS,
DISCORD_ALLOWED_CHANNELS, DISCORD_IGNORED_CHANNELS, DISCORD_REQUIRE_MENTION.

## Permission integer comparison
- Docs "Recommended" (chat only): 274878286912
  = View Channels, Send Messages, Embed Links, Attach Files, Read History, Send in Threads, Add Reactions
- WRONG moderation (missing Manage Roles): 1494648745158
  = above + Manage Messages, Manage Threads, Kick, Ban, Moderate Members, View Audit Log
  → CANNOT apply the Muted role. DO NOT USE.
- CORRECT moderation: 1494917180614
  = 1494648745158 + MANAGE_ROLES (bit 28). Use this.
- Recompute with scripts/compute_permissions.py (asserts 1494917180614). Never add Administrator (bit 3).
