# Discord Permission Bitfields

Use these values with Discord's permission overwrite API.

## Common Permission Flags

| Permission | Value | Description |
|-----------|-------|-------------|
| CREATE_INSTANT_INVITE | 0x0000000001 | 1 |
| KICK_MEMBERS | 0x0000000002 | 2 |
| BAN_MEMBERS | 0x0000000004 | 4 |
| ADMINISTRATOR | 0x0000000008 | 8 |
| MANAGE_CHANNELS | 0x0000000010 | 16 |
| MANAGE_GUILD | 0x0000000020 | 32 |
| ADD_REACTIONS | 0x0000000040 | 64 |
| VIEW_AUDIT_LOG | 0x0000000080 | 128 |
| PRIORITY_SPEAKER | 0x0000000100 | 256 |
| STREAM | 0x0000000200 | 512 |
| VIEW_CHANNEL | 0x0000000400 | **1024** |
| SEND_MESSAGES | 0x0000000800 | **2048** |
| SEND_TTS_MESSAGES | 0x0000001000 | 4096 |
| MANAGE_MESSAGES | 0x0000002000 | **8192** (0x2000) |
| EMBED_LINKS | 0x0000004000 | 16384 |
| ATTACH_FILES | 0x0000008000 | 32768 |
| READ_MESSAGE_HISTORY | 0x0000010000 | **65536** (0x10000) |
| MENTION_EVERYONE | 0x0000020000 | 131072 |
| USE_EXTERNAL_EMOJIS | 0x0000040000 | 262144 |
| CONNECT | 0x0010000000 | 1048576 |
| SPEAK | 0x0020000000 | 2097152 |
| MUTE_MEMBERS | 0x0040000000 | 4194304 |
| DEAFEN_MEMBERS | 0x0080000000 | 8388608 |
| MOVE_MEMBERS | 0x0100000000 | 16777216 |
| USE_VAD | 0x0200000000 | 33554432 |
| CHANGE_NICKNAME | 0x0400000000 | 67108864 |
| MANAGE_NICKNAMES | 0x0800000000 | 134217728 |
| MANAGE_ROLES | 0x1000000000 | 268435456 |
| MANAGE_WEBHOOKS | 0x2000000000 | 536870912 |
| MANAGE_EMOJIS_AND_STICKERS | 0x4000000000 | 1073741824 |
| USE_APPLICATION_COMMANDS | 0x8000000000 | 2147483648 |
| MANAGE_THREADS | 0x040000000000 | 17179869184 |
| CREATE_PUBLIC_THREADS | 0x080000000000 | 34359738368 |
| CREATE_PRIVATE_THREADS | 0x100000000000 | 68719476736 |
| USE_EXTERNAL_STICKERS | 0x200000000000 | 137438953472 |
| SEND_MESSAGES_IN_THREADS | 0x400000000000 | 274877906944 |
| USE_EMBEDDED_ACTIVITIES | 0x800000000000 | 549755813888 |
| MODERATE_MEMBERS | 0x0100000000000 | 1099511627776 |

## Common Combined Masks

**Specialist bot channel access** (read + write + manage):
```
VIEW_CHANNEL     = 1024
SEND_MESSAGES    = 2048
READ_HISTORY     = 65536
MANAGE_MESSAGES  = 8192
MANAGE_THREADS   = 17179869184
─────────────────────────────────
TOTAL            = 17179887640
```

**Public channel access** (anyone can read/write):
```
VIEW_CHANNEL     = 1024
SEND_MESSAGES    = 2048
READ_HISTORY     = 65536
─────────────────────────────────
TOTAL            = 68608
```

**Deny @everyone** (make channel private):
```
VIEW_CHANNEL     = 1024
SEND_MESSAGES    = 2048
READ_HISTORY     = 65536
─────────────────────────────────
TOTAL            = 68608  (use as `deny` value)
```

## API Usage

```python
# Set @everyone to denied (type=0 = role)
api_call('PUT', f'/channels/{ch_id}/permissions/{GUILD_ID}',
         {'type': 0, 'deny': str(VIEW_SEND_READ)})

# Allow a bot (type=1 = member)
api_call('PUT', f'/channels/{ch_id}/permissions/{bot_id}',
         {'type': 1, 'allow': str(FULL_ACCESS)})

# Allow a user
api_call('PUT', f'/channels/{ch_id}/permissions/{user_id}',
         {'type': 1, 'allow': str(FULL_ACCESS)})
```

Note: Permission values must be sent as **strings**, not integers, because Discord uses 64-bit integers and some bit combinations exceed JavaScript's safe integer range even though Python handles them fine.