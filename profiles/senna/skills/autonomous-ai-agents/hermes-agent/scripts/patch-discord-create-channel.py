#!/usr/bin/env python3
"""Add create_channel action to discord_tool.py.

Run: python3 ~/.hermes/profiles/senna/skills/autonomous-ai-agents/hermes-agent/scripts/patch-discord-create-channel.py
Then: launchctl kickstart gui/$(id -u)/ai.hermes.gateway-senna
"""

import sys

path = "~/.hermes/hermes-agent/tools/discord_tool.py"
with open(path) as f:
    code = f.read()

if "_create_channel" in code:
    print("Already patched! _create_channel found in discord_tool.py")
    sys.exit(0)

# 1. Add _create_channel function before _add_role
new_func = '''
def _create_channel(
    token: str, guild_id: str, name: str,
    channel_type: int = 0,
    topic: str = "",
    parent_id: str = "",
    **_kwargs: Any,
) -> str:
    """Create a channel or category in a guild. type: 0=text, 2=voice, 4=category, 5=announcement, 15=forum."""
    body: Dict[str, Any] = {"name": name, "type": channel_type}
    if topic:
        body["topic"] = topic
    if parent_id:
        body["parent_id"] = parent_id
    ch = _discord_request("POST", f"/guilds/{guild_id}/channels", token, body=body)
    return json.dumps({
        "success": True,
        "channel_id": ch["id"],
        "name": ch.get("name"),
        "type": _channel_type_name(ch.get("type", 0)),
    })


'''

code = code.replace(
    'def _add_role(token: str, guild_id: str, user_id: str, role_id: str, **_kwargs: Any) -> str:',
    new_func + 'def _add_role(token: str, guild_id: str, user_id: str, role_id: str, **_kwargs: Any) -> str:',
)

# 2. Add to _ACTIONS dict
code = code.replace(
    '    "delete_channel": _delete_channel,\n    "add_role": _add_role,',
    '    "delete_channel": _delete_channel,\n    "create_channel": _create_channel,\n    "add_role": _add_role,',
)

# 3. Add to _ACTION_MANIFEST
code = code.replace(
    '    ("delete_channel", "(channel_id)", "delete a channel or thread"),\n    ("add_role", "(guild_id, user_id, role_id)", "assign a role"),',
    '    ("delete_channel", "(channel_id)", "delete a channel or thread"),\n    ("create_channel", "(guild_id, name)", "create a channel or category; type: 0=text, 2=voice, 4=category"),\n    ("add_role", "(guild_id, user_id, role_id)", "assign a role"),',
)

# 4. Add to _REQUIRED_PARAMS
code = code.replace(
    '    "delete_channel": ["channel_id"],\n    "add_role": ["guild_id", "user_id", "role_id"],',
    '    "delete_channel": ["channel_id"],\n    "create_channel": ["guild_id", "name"],\n    "add_role": ["guild_id", "user_id", "role_id"],',
)

# 5. Add to _ACTION_403_HINT
code = code.replace(
    '    "delete_channel": (\n        "Bot lacks MANAGE_CHANNELS or MANAGE_THREADS permission to delete this channel/thread."\n    ),\n    "add_role": (',
    '    "delete_channel": (\n        "Bot lacks MANAGE_CHANNELS or MANAGE_THREADS permission to delete this channel/thread."\n    ),\n    "create_channel": (\n        "Bot lacks MANAGE_CHANNELS permission to create channels in this guild."\n    ),\n    "add_role": (',
)

# 6. Add channel_type and parent_id to schema properties
code = code.replace(
    '        "auto_archive_duration": {\n            "type": "integer",\n            "enum": [60, 1440, 4320, 10080],\n            "description": "Thread archive duration in minutes (create_thread, default 1440).",\n        },\n    }',
    '        "auto_archive_duration": {\n            "type": "integer",\n            "enum": [60, 1440, 4320, 10080],\n            "description": "Thread archive duration in minutes (create_thread, default 1440).",\n        },\n        "channel_type": {\n            "type": "integer",\n            "description": "Channel type for create_channel: 0=text, 2=voice, 4=category, 5=announcement, 15=forum.",\n        },\n        "parent_id": {\n            "type": "string",\n            "description": "Parent category ID for create_channel.",\n        },\n        "topic": {\n            "type": "string",\n            "description": "Channel topic for create_channel.",\n        },\n    }',
)

# 7. Add to _HANDLER_DEFAULTS
code = code.replace(
    '"limit": 50, "before": "", "after": "", "auto_archive_duration": 1440,',
    '"limit": 50, "before": "", "after": "", "auto_archive_duration": 1440, "channel_type": 0, "parent_id": "", "topic": "",',
)

# 8. Add to _run_discord_action local_vars
code = code.replace(
    '    local_vars = {\n        "guild_id": guild_id,\n        "channel_id": channel_id,\n        "user_id": user_id,\n        "role_id": role_id,\n        "message_id": message_id,\n        "query": query,\n        "name": name,\n    }',
    '    local_vars = {\n        "guild_id": guild_id,\n        "channel_id": channel_id,\n        "user_id": user_id,\n        "role_id": role_id,\n        "message_id": message_id,\n        "query": query,\n        "name": name,\n        "channel_type": channel_type,\n        "parent_id": parent_id,\n        "topic": topic,\n    }',
)

# 9. Add new params to handler signature
code = code.replace(
    '    auto_archive_duration: int = 1440,\n) -> str:\n    """Shared handler logic for both discord tools."""',
    '    auto_archive_duration: int = 1440,\n    channel_type: int = 0,\n    parent_id: str = "",\n    topic: str = "",\n) -> str:\n    """Shared handler logic for both discord tools."""',
)

# 10. Pass new params to action_fn
code = code.replace(
    '        auto_archive_duration=auto_archive_duration,\n    )',
    '        auto_archive_duration=auto_archive_duration,\n        channel_type=channel_type,\n        parent_id=parent_id,\n        topic=topic,\n    )',
)

with open(path, 'w') as f:
    f.write(code)

print("✅ Patched discord_tool.py — added create_channel action")
print("Restart the gateway: launchctl kickstart gui/$(id -u)/ai.hermes.gateway-senna")
