# MFA Level 1 (60003) — Bot Operation Limits

## When to read this
- A `PUT /channels/{id}/permissions/{role_id}` or `PATCH /guilds/{id}/roles/{role_id}` returns `60003 "Two factor is required for this operation"`.
- The server owner enabled MFA for moderation (Server Settings → Safety → Require 2FA for moderation = ON → `mfa_level=1`).
- You need to decide whether the bot can still make a specific change.

## What 60003 means
Discord error code 60003 = "Two factor is required for this operation". The server has `mfa_level=1` (or higher). The bot is a service account — it has no authenticator, no phone, no TOTP seed. It **cannot pass 2FA** for any endpoint that requires it.

## What the bot CAN still do (with MFA=1)

| Operation | Endpoint | Works? | Evidence |
|---|---|---|---|
| Role name change | `PATCH /roles/{id}` | **Yes** (HTTP 200) | Changing Verified role name succeeded |
| Role color change | `PATCH /roles/{id}` | **Yes** (HTTP 200) | Changing color succeeded |
| Role mentionable flag | `PATCH /roles/{id}` | **Yes** (HTTP 200) | All 12 self-serve roles flipped to `mentionable: true` |
| Role hoist toggle | `PATCH /roles/{id}` | **Likely** | Untested but follows same pattern as name/color |
| Channel perm overwrite (on accessible channel) | `PUT /channels/{id}/permissions/{role}` | **Yes** (HTTP 204) | `#verify` @everyone ALLOW VIEW succeeded; `#reports` @everyone DENY VIEW + Verified ALLOW VIEW+SEND succeeded |
| Delete message | Hermes toolset `delete_message` | **Yes** | Non-2FA endpoint |
| Add/remove role | Hermes toolset `add_role`/`remove_role` | **Yes** | Non-2FA endpoint |

## What the bot CANNOT do (with MFA=1)

| Operation | Endpoint | Fails? | Evidence |
|---|---|---|---|
| Change role `permissions` field | `PATCH /roles/{id}` with `permissions` key | **60003** | Any non-zero permissions value triggered 60003; even `{"permissions":"0"}` rolled back the same way |
| Channel perm overwrite on child under @everyone-denied category | `PUT /channels/{id}/permissions/{role}` | **60003** | All 14 child channels under Text/Voice/Unreal/Unity/Godot/AI categories returned 60003 |
| Category perm overwrite on @everyone-denied category | `PUT /channels/{id}/permissions/{role}` | **50001** (separate issue) | Categories blocked by @everyone VIEW- self-lockout, not 60003 |

## The 60003 trigger pattern (critical nuance)

60003 does NOT fire on every channel write. It fires specifically on channels where the **parent category denies @everyone VIEW** and the bot role has **no explicit ALLOW VIEW override** on that category. Here's the exact pattern observed:

| Channel | Parent | @everyone VIEW on cat? | Bot role explicit on cat? | Result |
|---|---|---|---|---|
| `#verify` | Information | No deny (no overwrite) | No explicit allow needed | **HTTP 204** ✅ |
| `#reports` | Staff | @everyone VIEW- | Bot has explicit ALLOW VIEW | **HTTP 204** ✅ |
| `#general` | Text Channels | @everyone VIEW- | No explicit allow | **60003** ❌ |
| `unreal-general` | Unreal Engine | @everyone VIEW- | No explicit allow | **60003** ❌ |

**Why the difference?** The bot's role at the guild level has `VIEW_CHANNEL` (bit 10). That lets the bot *read* the channel's metadata via the API. But when the bot tries to *write* a permission overwrite on a channel whose parent category denies @everyone VIEW, Discord's MFA check fires. The theory: MFA is required when the operation affects a channel that requires elevated privileges to access, and the 2FA gate on the write is a safety check.

## MFA=0 post-toggle behavior (what changes)

When the owner disables MFA (`mfa_level=0`), the bot still cannot write to every
channel. The 60003 errors disappear, but two other error types may surface:

| Error after MFA=0 | What it means | Common channels |
|---|---|---|
| `50001 Missing Access` | Category self-lockout persists — the bot can't see the category at all because `@everyone` is denied VIEW and the bot role has no explicit allow. | Text/Voice/Unreal/Unity/Godot/AI **categories** |
| `50013 Missing Permissions` | The bot can see the channel but the `permissions` integer includes bits the bot doesn't hold (see SKILL.md "bot can only grant perms it holds" pitfall). | Role PATCH with full member perms; channel PUT overwrite with VIEW on channels under locked cats |

**Pattern observed in practice (MFA=0, one session):**
- `PATCH /roles/Verified` with `permissions="1024"` (VIEW_CHANNEL only) → **HTTP 200** ✅
- `PATCH /roles/Verified` with `permissions="391976163073088"` (full member set) → **50013** ❌
- `PUT /channels/unreal-general/permissions/Verified` with `allow="2048"` (SEND only) → **HTTP 204** ✅
- `PUT /channels/unreal-general/permissions/Verified` with `allow="3072"` (VIEW+SEND) → **50013** ❌
- `PUT /channels/Text-Channels-Category/permissions/Verified` (category itself) → **50001** ❌

So turning MFA off alone is NOT enough to let the bot do everything. The bot still
needs:
1. The bot role dragged to the **top of the role hierarchy** to write category
   overwrites (the temp-promote workaround from the Muted overwrite recipe), OR
2. The owner to add category-level overwrites manually in the UI even with MFA
   off, because the bot can't reach those categories (50001).

## Workarounds

1. **Owner disables MFA temporarily** (`mfa_level=0`): Server Settings → Safety → Require 2FA for moderation → OFF. Make the bot changes. Re-enable MFA. This is the cleanest path.

2. **Owner does the changes in the UI**: For a few targeted changes, the owner can do them manually faster than the toggles:
   - Set Verified role permissions (Server Settings → Roles → Verified → toggle on: View Channels, Send Messages, Embed Links, Attach Files, Read Message History, Add Reactions, Connect, Speak, Use Voice Activity, Change Nickname)
   - Add Verified to category allow lists (Edit Category → Permissions → + Verified → Allow View Channel) for each of: Text Channels, Voice Channels, Unreal Engine, Unity, Godot, AI & Tooling

3. **Bot role gets explicit ALLOW VIEW on locked-out categories**: The owner adds Gamehub-mod's role to the member categories with ALLOW VIEW. This eliminates the 50001 self-lockout. Then retry the bot writes — they may still 60003 (MFA is the primary blocker), but at least error messages become clearer.

## Symptom checklist

If you're getting a 403 and aren't sure which code:

```bash
# Check server mfa_level
curl -s -H "Authorization: Bot $TOKEN" \
  "https://discord.com/api/v10/guilds/$GID?with_counts=true" \
  | python3 -c "import sys,json; g=json.load(sys.stdin); print('mfa_level:',g.get('mfa_level'))"

# 0 = no 2FA requirement → 60003 should not fire
# 1 = 2FA required for moderation → 60003 will fire on perm changes
# 2 = 2FA required for all → everything blocked
```

If mfa_level=1 and you're getting 60003 on a channel write, check whether the parent category has an `@everyone` VIEW- overwrite and whether the bot role has an explicit overwrite on that category.