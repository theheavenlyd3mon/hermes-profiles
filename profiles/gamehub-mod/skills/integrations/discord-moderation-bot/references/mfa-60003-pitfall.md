# MFA (60003) / Two-Factor Required Pitfall

## Symptom
`{"message": "Two factor is required for this operation", "code": 60003}`

## Cause
The server has **MFA Level 1** enabled (`Server Settings → Safety Setup → Require 2FA for moderators`). When this is ON, the bot CANNOT perform:
- `PATCH /guilds/{id}/roles/{id}` that changes the `permissions` field (role permission edits)
- `PUT /channels/{id}/permissions/{overwrite_id}` that creates NEW permission overwrites

The bot CAN still do (even with MFA=1):
- `PATCH /roles` cosmetic changes (`name`, `mentionable`, `color`, `hoist`) — these do NOT trigger 2FA
- Editing EXISTING channel permission overwrites (changing the allow/deny on an overwrite that already exists)
- Message operations (delete, pin, etc.)
- READ operations

## Detection
Check `mfa_level` via:
```bash
curl -s -H "Authorization: Bot $TOKEN" "https://discord.com/api/v10/guilds/$GID?with_counts=true" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('mfa_level'))"
```
- `0` = MFA not required
- `1` = MFA required for moderation (60003 triggered)

## Workarounds (in order of preference)

### 1. Ask owner to temporarily disable 2FA
The fastest path. Owner toggles **Server Settings → Safety Setup → Require 2FA for moderators → OFF**, bot makes all changes, then owner toggles back ON.

### 2. Use admin temp-promote
If the owner grants the bot role **Administrator** temporarily, the 60003 is bypassed with the admin perms. Owner unchecks Administrator after changes.

### 3. Manual UI changes
Owner makes the role permission and channel overwrite changes manually in the Discord UI. No bot involvement.

## Role hierarchy interaction
When MFA=1, the **60003 fires before hierarchy checks** — you won't see 50013 or 50001, you'll see 60003 first. Only after MFA is satisfied do normal hierarchy/perm checks apply.

## Channels under @everyone-denied categories
Even with MFA=0, the bot gets 50001 "Missing Access" on categories where @everyone is denied VIEW and the bot has no explicit overwrite. The bot can READ child channels (via guild-level VIEW_CHANNEL) but CANNOT write any permission overwrite to them until the bot role has an explicit ALLOW VIEW on the parent category.