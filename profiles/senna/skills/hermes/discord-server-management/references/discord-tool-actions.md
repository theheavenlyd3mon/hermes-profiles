# Discord Tool Actions — Full Inventory

Source: `tools/discord_tool.py` in hermes-agent.

## The Two Tools

| Tool | Registration | Actions |
|------|-------------|---------|
| `discord` (core) | `_CORE_ACTION_NAMES` | fetch_messages, search_members, create_thread |
| `discord_admin` | `_ADMIN_ACTION_NAMES` | all 15 remaining actions |

Both are registered in `toolsets.py` under the `hermes-discord` bundle and the standalone `discord_admin` toolset.

## Full Action List (18 actions)

### Core Actions (discord tool)

| Action | Params | Intent Gate | Description |
|--------|--------|-------------|-------------|
| `fetch_messages` | `(channel_id, before?, after?, limit?)` | MESSAGE_CONTENT (for text) | Recent messages; returns metadata only without intent |
| `search_members` | `(guild_id, query, limit?)` | GUILD_MEMBERS | Find members by name prefix |
| `create_thread` | `(channel_id, name, message_id?)` | — | Create a public thread; optional anchor message |

### Admin Actions (discord_admin tool)

| Action | Params | Intent Gate | Description |
|--------|--------|-------------|-------------|
| `list_guilds` | `()` | — | Servers the bot is in |
| `server_info` | `(guild_id)` | — | Server details + member counts |
| `list_channels` | `(guild_id)` | — | All channels grouped by category |
| `channel_info` | `(channel_id)` | — | Single channel details |
| `list_roles` | `(guild_id)` | — | Roles sorted by position |
| `member_info` | `(guild_id, user_id)` | GUILD_MEMBERS | Lookup a specific member |
| `list_pins` | `(channel_id)` | MESSAGE_CONTENT (for text) | Pinned messages |
| `pin_message` | `(channel_id, message_id)` | — | Pin a message |
| `unpin_message` | `(channel_id, message_id)` | — | Unpin a message |
| `delete_message` | `(channel_id, message_id)` | — | Delete a message |
| `create_thread` | `(channel_id, name, message_id?)` | — | Create a public thread; optional anchor message |
| `list_threads` | `(guild_id)` | — | All active threads in a server |
| `list_archived_threads` | `(channel_id)` | — | Archived threads for a specific channel (public + private) |
| `delete_channel` | `(channel_id)` | — | Delete a channel or thread (threads are channels internally) |
| `add_role` | `(guild_id, user_id, role_id)` | — | Assign a role |
| `remove_role` | `(guild_id, user_id, role_id)` | — | Remove a role |

## Intent Gating

Two privileged intents control what data the tools can access:

| Intent | Gates | Without it |
|--------|-------|------------|
| `GUILD_MEMBERS` | `member_info`, `search_members` | Actions hidden from tool schema entirely |
| `MESSAGE_CONTENT` | `fetch_messages`, `list_pins` | Returns metadata only (author, timestamps, attachments, reactions) — `content` is empty for non-DM/non-mention messages |

Enable in: Discord Developer Portal → Bot → Privileged Gateway Intents.

## server_actions Config

```yaml
discord:
  server_actions: 'list_guilds,server_info,list_channels,...'  # comma-separated whitelist
```

- Empty/unset = all intent-available actions are exposed
- Set = only listed actions are available (unknown names dropped with log warning)
- Per-guild permissions (MANAGE_CHANNELS etc.) are NOT pre-checked — Discord returns 403 at call time

## Thread & Channel Management

The discord tool now supports thread and channel management:

| Action | Description |
|--------|-------------|
| `list_threads` | List all active threads in a guild (by guild_id) |
| `list_archived_threads` | List archived threads in a specific channel (public + private) |
| `delete_channel` | Delete a channel or thread (threads are channels internally) |
| `create_thread` | Create a public thread, optionally anchored to a message |

**Workflow for cleaning up threads:**
```
list_threads(guild_id) → get thread IDs → delete_channel(thread_id)
```

**⚠️ Pitfall**: `delete_channel` deletes the ENTIRE thread/channel. `delete_message` deletes a single message. To remove a thread, use `delete_channel`, not `delete_message`.

**⚠️ server_actions whitelist**: These actions must be in the `server_actions` config to be available. The full 18-action whitelist:
```yaml
discord:
  server_actions: 'list_guilds,server_info,list_channels,channel_info,list_roles,member_info,search_members,fetch_messages,list_pins,pin_message,unpin_message,delete_message,create_thread,list_threads,list_archived_threads,delete_channel,add_role,remove_role'
```

## Discord Re-Invite Workflow

When changing bot permissions (e.g. adding MANAGE_CHANNELS):

1. Go to Discord Developer Portal → your app → Installation
2. Under "Guild Install" → Permissions, check the new permissions
3. Copy the generated OAuth2 URL
4. Open the URL in browser → select your server → Authorize
5. The bot's permissions update in the server (no restart needed)
6. Restart the gateway to pick up any config changes

**Required permissions for full discord_admin support:**
- View Channels, Send Messages, Read Message History (basic)
- Manage Messages (delete_message, pin/unpin)
- Manage Channels (edit_channel, if implemented)
- Manage Threads (list_threads, delete_thread, if implemented)
- Manage Roles (add_role, remove_role)
- Create Public Threads (create_thread)

## Debugging: Discord Tools Not Working

Checklist when discord tools fail or aren't available:

1. **platform_toolsets** — Is `discord` and/or `discord_admin` listed under `discord:` in config.yaml?
   ```bash
   grep -A20 'platform_toolsets:' ~/.hermes/profiles/<name>/config.yaml | grep discord
   ```

2. **server_actions** — Is the desired action whitelisted?
   ```bash
   grep 'server_actions:' ~/.hermes/profiles/<name>/config.yaml
   ```

3. **Bot permissions** — Does the bot have the required Discord server permissions?
   - Check in Discord Server Settings → Roles → bot role
   - Or re-invite with updated OAuth2 URL (see workflow above)

4. **Privileged intents** — Are GUILD_MEMBERS and MESSAGE_CONTENT enabled?
   - Discord Developer Portal → Bot → Privileged Gateway Intents
   - Without MESSAGE_CONTENT, fetch_messages returns empty content
   - Without GUILD_MEMBERS, member_info/search_members are hidden from schema

5. **Token validity** — Is the bot token still valid?
   ```bash
   grep 'Connected as' ~/.hermes/profiles/<name>/logs/gateway.log | tail -1
   ```

6. **Gateway restart** — Config changes require gateway restart
   ```bash
   kill $(pgrep -f "profile <name> gateway") && sleep 3
   # Verify new process started
   pgrep -f "profile <name> gateway"
   ```
