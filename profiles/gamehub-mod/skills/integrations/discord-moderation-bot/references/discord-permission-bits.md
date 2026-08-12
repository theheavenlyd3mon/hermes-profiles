# Discord Permission Bit Table (canonical) + decode recipe

Use this table to decode a role's `permissions` integer. The #1 cause of
**confidently-wrong** moderation conclusions is decoding with an incomplete or
mislabeled bit mapping. (This bit the bot role `1494917180614` and briefly
claimed BAN/KICK were OFF — they are ON. The decode script had omitted
`MODERATE_MEMBERS` and mislabeled bits.) Always decode against THIS table.

## Canonical bit positions (stable, well-known)
```
 0 CREATE_INSTANT_INVITE     1 KICK_MEMBERS          2 BAN_MEMBERS
 3 ADMINISTRATOR             4 MANAGE_CHANNELS       5 MANAGE_GUILD
 6 ADD_REACTIONS             7 VIEW_AUDIT_LOG        8 PRIORITY_SPEAKER
 9 STREAM                   10 VIEW_CHANNEL         11 SEND_MESSAGES
12 SEND_TTS_MESSAGES        13 MANAGE_MESSAGES      14 EMBED_LINKS
15 ATTACH_FILES             16 READ_MESSAGE_HISTORY 17 MENTION_EVERYONE
18 USE_EXTERNAL_EMOJIS      19 VIEW_GUILD_INSIGHTS  20 CONNECT
21 SPEAK                    22 MUTE_MEMBERS         23 DEAFEN_MEMBERS
24 MOVE_MEMBERS             25 USE_VOICE_ACTIVITY   26 CHANGE_NICKNAME
27 MANAGE_NICKNAMES         28 MANAGE_ROLES         29 MANAGE_WEBHOOKS
30 MANAGE_GUILD_EXPRESSIONS (was MANAGE_EMOJIS_AND_STICKERS)
31 USE_APPLICATION_COMMANDS 32 REQUEST_TO_SPEAK
34 MANAGE_THREADS           35 USE_PUBLIC_THREADS   36 USE_PRIVATE_THREADS
37 USE_EXTERNAL_STICKERS    38 VIEW_MONETIZATION    39 USE_SOUNDBOARD
40 MODERATE_MEMBERS (Timeout Members)  [bit was CREATE_EVENTS in old docs]
41 CREATE_EVENTS             42 SEND_VOICE_MESSAGES  43 SEND_POLLS
44 USE_EXTERNAL_APPS
```
> Naming drift note: bit 40 is `MODERATE_MEMBERS` in the current API (renamed
> from `CREATE_EVENTS`). Don't trust an old table that maps 40 -> CREATE_EVENTS
> and then concludes "no timeout perm" — the bit is set, it just got renamed.

## Known integers for this server
- `1494917180614` — bot's `Gamehub-mod` role (scoped mod). Sets: BAN(2),
  KICK(1), MANAGE_ROLES(28), MANAGE_MESSAGES(13), VIEW_AUDIT_LOG(7),
  MODERATE_MEMBERS(40), MANAGE_THREADS(34), SEND/EMBED/ATTACH/REACTIONS/
  VIEW/READ/THREADS. **LACKS**: MANAGE_CHANNELS(4), MANAGE_WEBHOOKS(29),
  ADMINISTRATOR(3).
- `1494917180608` — optional least-privilege tightening: drops BAN(2)+KICK(1),
  **keeps MANAGE_ROLES(28)**. Manual UI edit only (bot can't self-edit -> 403).
- `274878286912` — Discord docs' "Recommended" — CHAT ONLY. Lacks Manage
  Messages / Manage Roles / Kick / Ban / Moderate / View Audit Log. Wrong for a
  mod bot.

## Decode recipe (curl + python — NOT urllib, which hits Cloudflare 1010)
```bash
TOKEN=$(grep -E '^DISCORD_BOT_TOKEN=' ~/.hermes/profiles/<profile>/.env | cut -d= -f2-)
G=<guild_id>
curl -s -m 20 -H "Authorization: Bot $TOKEN" "https://discord.com/api/v10/guilds/$G/roles" \
 | python3 -c '
import sys,json
roles=json.load(sys.stdin)
BITS={0:"CREATE_INSTANT_INVITE",1:"KICK_MEMBERS",2:"BAN_MEMBERS",3:"ADMINISTRATOR",
4:"MANAGE_CHANNELS",5:"MANAGE_GUILD",6:"ADD_REACTIONS",7:"VIEW_AUDIT_LOG",
10:"VIEW_CHANNEL",11:"SEND_MESSAGES",13:"MANAGE_MESSAGES",14:"EMBED_LINKS",
15:"ATTACH_FILES",16:"READ_MESSAGE_HISTORY",17:"MENTION_EVERYONE",
21:"SPEAK",28:"MANAGE_ROLES",29:"MANAGE_WEBHOOKS",34:"MANAGE_THREADS",
35:"USE_PUBLIC_THREADS",36:"USE_PRIVATE_THREADS",40:"MODERATE_MEMBERS"}
for r in roles:
    if r["name"]=="Gamehub-mod":
        p=int(r["permissions"])
        print("perm int =",p)
        for bit,name in sorted(BITS.items()):
            print(f"  {name:22} = {bool(p&(1<<bit))}")
'
```
Test each NEEDED bit individually with `(p >> bit) & 1`. Never infer a
permission's state from a bit that is absent from your mapping.
