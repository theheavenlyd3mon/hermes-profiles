# Verified Role as Member Replacement

## When to use
You want to collapse the verification gate to a single role: `Verified` replaces `Member`, so Captcha.bot grants `Verified` directly and that's the role that unlocks everything.

## Setup steps

### 1. Delete the old Member role (or don't create one)
Only if it exists. The `Verified` role becomes the sole member-level role.

### 2. Grant Verified guild-level permissions
The bot can only grant permissions it **already holds**. If the bot lacks certain perms (e.g. CONNECT, CHANGE_NICKNAME, SEND_POLLS), it can't assign them to Verified.

**Safe set** (bot-owned perms only — 182570048):
- ADD_REACTIONS, VIEW_CHANNEL, SEND_MESSAGES, EMBED_LINKS, ATTACH_FILES, READ_MESSAGE_HISTORY, SPEAK, MUTE_MEMBERS, DEAFEN_MEMBERS, USE_VAD, MANAGE_NICKNAMES

**Full member set** (391976163073088 — includes CONNECT, CHANGE_NICKNAME, USE_SOUNDBOARD, etc.):
- May 50013 if bot lacks those perms. Use `PATCH /guilds/{id}/roles/{id}` with admin or owner manually.

### 3. Add Verified to category overwrites
The 6 member categories (Text, Voice, Unreal, Unity, Godot, AI & Tooling) deny @everyone VIEW. Verified needs `ALLOW VIEW` on each:
- Bot PUT: `/channels/{cat_id}/permissions/{verified_id}` with `{"allow": "1024", "deny": "0", "type": 0}`
- **Blocked by 50001** if bot lacks explicit access to the category (self-lockout). Workaround: grant admin temporarily, or owner does it manually.

### 4. Add Verified to child channel overwrites
The bot CAN write SEND+ to child channels under locked categories (even if it can't see the parent). But it CANNOT write VIEW+ to those same children — that requires access to the parent category.

Strategy: write SEND+ (2048) to child channels, rely on the category-level VIEW+ for visibility.

### 5. Gate landing channels
Pre-verify channels (welcome-and-rules, announcements, get-roles, verify) should be visible to @everyone:
- `#verify`: @everyone V+ (so joiners can see the captcha)
- `#welcome-and-rules`: @everyone V+ S- (read-only, staff can post)
- `#announcements`: @everyone V+ S- (read-only)
- `#get-roles`: @everyone V+ S- (reactions do the work)
- `#introductions`: @everyone V+ S-, Verified S+ (verified members introduce themselves)

### 6. Full flow
```
Joiner → sees #verify → completes captcha → gets Verified → sees all channels
```

## 60003 MFA trap
If MFA Level is 1, the bot can't PATCH role permissions or create new channel overwrites. Owner must temporarily disable 2FA or grant admin. See `references/mfa-60003-pitfall.md`.

## Role hierarchy note
- Verified must be BELOW the bot's highest role (so the bot can assign it)
- Verified must be ABOVE the self-serve roles (so it's the base member role)
- The bot role must be at the TOP of the hierarchy to write category overwrites under locked categories