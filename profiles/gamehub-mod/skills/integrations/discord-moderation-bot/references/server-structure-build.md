# Server Structure Build Steps (human-done)

A Hermes mod bot **cannot create channels or categories** — the installed Discord
tool has no `create_channel` action (only `create_thread`, which makes threads
inside an existing channel), and the bot deliberately lacks `MANAGE_CHANNELS`.
So a human builds the structure in the Discord UI first; the bot only operates
within it. Steps below are the bare minimum for a scoped staff mod bot.

## 1. Bot role perms
Set the bot's Discord role to **1494917180614** (scoped, no Admin, includes
Manage Roles). Re-invite with `permissions=1494917180614`, or manually toggle:
View Channels, Send Messages, Send in Threads, Create Public/Private Threads,
Embed Links, Attach Files, Add Reactions, Read History, Manage Messages,
Manage Threads, **Manage Roles**, Kick, Ban, Moderate Members, View Audit Log.
Position the bot role **above** `Muted` but **below** `Moderator`.

## 2. `Moderator` role
Create `Moderator` (in this session named `Gamehub-mod`); position it **above**
the bot role. Assign to you + human mods. This is the value for
`DISCORD_ALLOWED_ROLES`.

## 3. `Muted` role (enforcement lever)
Create `Muted`; in Permissions set **deny**: Send Messages, Send in Threads,
Add Reactions, Connect, Speak. Position it **BELOW** the bot role (so the bot can
apply/remove it and cannot touch `Moderator`). Note: a per-role allow overrides a
deny — only mute regular members, never mods.

## 4. Staff category + 3 channels
Under a `STAFF` category, create:
- `#mod-ops` — bot home + free-response (mention-free). `@everyone` deny send;
  `Moderator` + bot allow.
- `#audit-review` — triage/audit summaries. Same permission pattern.
- `#announcements` — **post-target-only**, whole server reads. `@everyone` deny
  send; `Moderator` + bot allow. Keep it OUT of `DISCORD_ALLOWED_CHANNELS`.

## 5. Hand back to the agent
Once the structure exists, the agent: starts the gateway, runs
`scripts/discord_introspect.sh` to read the **real channel/role IDs** via the
bot token (no manual ID copying — see `references/discord-api-introspection.md`
for why curl, not urllib). Then writes the 4 scoping vars into the profile
`.env`, strips `delete_channel` from `server_actions`, restarts the gateway, and
confirms via `profiles/<profile>/logs/gateway.log`.
