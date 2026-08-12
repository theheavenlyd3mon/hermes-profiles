#!/usr/bin/env python3
"""Patch discord_tool.py to add list_threads, list_archived_threads, delete_channel actions.

Run: python3 ~/.hermes/profiles/senna/skills/autonomous-ai-agents/hermes-agent/scripts/patch-discord-threads.py
"""

import sys

path = "~/.hermes/hermes-agent/tools/discord_tool.py"
with open(path) as f:
    code = f.read()

if "_list_threads" in code:
    print("Already patched! _list_threads found in discord_tool.py")
    sys.exit(0)

# 1. Add new functions before _add_role
new_funcs = '''
def _list_threads(token: str, guild_id: str, **kwargs: Any) -> str:
    """List all active threads in a guild."""
    data = _discord_request("GET", f"/guilds/{guild_id}/threads/active", token)
    threads = []
    for t in data.get("threads", []):
        meta = t.get("thread_metadata", {})
        threads.append({
            "id": t["id"],
            "name": t.get("name", ""),
            "parent_id": t.get("parent_id", ""),
            "type": _channel_type_name(t.get("type", 0)),
            "archived": meta.get("archived", False),
            "auto_archive_duration": meta.get("auto_archive_duration"),
            "message_count": t.get("message_count"),
            "member_count": t.get("member_count"),
            "status": "active",
        })
    return json.dumps({"threads": threads, "count": len(threads)})


def _list_archived_threads(token: str, channel_id: str, **kwargs: Any) -> str:
    """List archived threads in a specific channel (public and private)."""
    threads = []
    for kind in ("public", "private"):
        try:
            data = _discord_request(
                "GET", f"/channels/{channel_id}/threads/archived/{kind}", token,
            )
            for t in data.get("threads", []):
                meta = t.get("thread_metadata", {})
                threads.append({
                    "id": t["id"],
                    "name": t.get("name", ""),
                    "parent_id": t.get("parent_id", ""),
                    "type": _channel_type_name(t.get("type", 0)),
                    "archived": meta.get("archived", False),
                    "archive_timestamp": meta.get("archive_timestamp"),
                    "message_count": t.get("message_count"),
                    "status": f"archived-{kind}",
                })
        except DiscordAPIError:
            pass
    return json.dumps({"threads": threads, "count": len(threads)})


def _delete_channel(token: str, channel_id: str, **_kwargs: Any) -> str:
    """Delete a channel or thread by ID. Threads are just channels internally."""
    ch = _discord_request("DELETE", f"/channels/{channel_id}", token)
    name = ch.get("name", channel_id) if ch else channel_id
    return json.dumps({"success": True, "message": f"Channel/thread '{name}' ({channel_id}) deleted."})


'''

code = code.replace(
    'def _add_role(token: str, guild_id: str, user_id: str, role_id: str, **_kwargs: Any) -> str:',
    new_funcs + 'def _add_role(token: str, guild_id: str, user_id: str, role_id: str, **_kwargs: Any) -> str:',
)

# 2. Add to _ACTIONS dict
code = code.replace(
    '    "create_thread": _create_thread,\n    "add_role": _add_role,',
    '    "create_thread": _create_thread,\n    "list_threads": _list_threads,\n    "list_archived_threads": _list_archived_threads,\n    "delete_channel": _delete_channel,\n    "add_role": _add_role,',
)

# 3. Add to _ACTION_MANIFEST
code = code.replace(
    '    ("create_thread", "(channel_id, name)", "create a public thread; optional message_id anchor"),\n    ("add_role", "(guild_id, user_id, role_id)", "assign a role"),',
    '    ("create_thread", "(channel_id, name)", "create a public thread; optional message_id anchor"),\n    ("list_threads", "(guild_id)", "all active threads in a server"),\n    ("list_archived_threads", "(channel_id)", "archived threads for a specific channel"),\n    ("delete_channel", "(channel_id)", "delete a channel or thread"),\n    ("add_role", "(guild_id, user_id, role_id)", "assign a role"),',
)

# 4. Add to _REQUIRED_PARAMS
code = code.replace(
    '    "create_thread": ["channel_id", "name"],\n    "add_role": ["guild_id", "user_id", "role_id"],',
    '    "create_thread": ["channel_id", "name"],\n    "list_threads": ["guild_id"],\n    "list_archived_threads": ["channel_id"],\n    "delete_channel": ["channel_id"],\n    "add_role": ["guild_id", "user_id", "role_id"],',
)

# 5. Add to _ACTION_403_HINT
code = code.replace(
    '    "create_thread": (\n        "Bot lacks CREATE_PUBLIC_THREADS in this channel, or cannot view it."\n    ),\n    "add_role": (',
    '    "create_thread": (\n        "Bot lacks CREATE_PUBLIC_THREADS in this channel, or cannot view it."\n    ),\n    "list_threads": (\n        "Bot lacks permission to view threads in this guild."\n    ),\n    "list_archived_threads": (\n        "Bot lacks permission to view archived threads in this channel."\n    ),\n    "delete_channel": (\n        "Bot lacks MANAGE_CHANNELS or MANAGE_THREADS permission to delete this channel/thread."\n    ),\n    "add_role": (',
)

with open(path, 'w') as f:
    f.write(code)

print("✅ Patched discord_tool.py — added list_threads, list_archived_threads, delete_channel")
print("Restart the gateway: launchctl kickstart gui/$(id -u)/ai.hermes.gateway-senna")
