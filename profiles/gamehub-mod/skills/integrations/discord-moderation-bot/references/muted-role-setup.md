# Muted role setup — the part that actually silences members

Positioning the `Muted` role above `@everyone` is necessary but **not sufficient**. Discord
roles can only **grant** permissions; they cannot deny. To make muting work you must add a
**per-channel permission overwrite** on the `Muted` role that **denies** sending/reactions.

## Why position alone fails
A role *deny* only outranks an *allow* from an equal-or-ower role. `@everyone` grants
`Send Messages`. If `Muted` sits below `@everyone`, the member's base Send *allow* wins ->
muting does nothing (silent failure). Even when `Muted` is correctly positioned above
`@everyone`, the **role grants nothing that stops sending** — there is no "deny Send" a role
can carry. The deny must live on the **channel overwrite**.

## Overwrite recipe — CATEGORY level (preferred)
Write the deny on the **category**, not each channel. A category overwrite CASCADES to
every child channel that has **no own** `Muted` overwrite. For the standard layout, set the
deny on just two categories (the text-channels category + the info/announcements category)
and every member channel underneath inherits it. Staff category is left alone — you never
want the bot able to silence staff.

Edit Channel/Category → Permissions → + Add `Muted`, then set **X Deny** on:
- Send Messages
- Send Messages in Threads
- Add Reactions
- Connect (voice)
- Speak (voice)
- **Do NOT deny `Mention Everyone`** (see the 50013 trap below — denying it fails even for
  a top-positioned bot, and a muted member can't talk anyway).

### Cascade gotcha
If a child channel already has a **stale empty** `Muted` overwrite (deny=0), the category
deny does NOT reach it. `scripts/inspect_muted.py` shows that child as `deny=(none)` with
`via channel`. Fix: `DELETE /channels/{child}/permissions/{Muted}` so it inherits the
category, then re-run `inspect_muted.py`.

## The bot usually can't write these itself (Discord 50013)
`PUT /channels/{id}/permissions/{MUTED_ROLE_ID}` returns `50013 Missing Permissions` for TWO
independent reasons — diagnose which:

1. **Hierarchy (real):** the bot's highest role is not at the top. Even with `MANAGE_CHANNELS`
   *flag* reading True, Discord rejects the write. Confirm with `scripts/check_bot_pos.py` —
   if `bot_top != guild_top`, it will fail.
   **Workaround:** drag the bot's role to the **top** (above `Moderator`), run
   `scripts/apply_muted_overwrites.py` (curl-based, **category-level**, skips staff), drag it
   back below `Moderator`. One-time; keeps least privilege normally.
2. **`MENTION_EVERYONE` in the deny (the silent trap):** even with the bot role at the TOP,
   a deny including `MENTION_EVERYONE` (bit 17) returns 50013 — the bot isn't the server
   owner and Discord refuses a non-owner from denying @everyone mention. This was the actual
   blocker even after promoting the role. **Always exclude `MENTION_EVERYONE`.**

### Or do it by hand
Repeat the category (or per-channel) overwrite recipe in the UI. No temp-promote needed.

## After setup
- **Remove `MANAGE_CHANNELS`** from the bot's role (it's excluded from the `1494917180614`
  integer; only added manually for the one-time write). Keep `MANAGE_ROLES` so the bot can
  still apply/remove `Muted`.
- Verify with `scripts/inspect_muted.py` — it lists each channel and its `Muted` deny set,
  flagging channels that still need an overwrite.
- End-to-end proof: apply `Muted` to a throwaway account, confirm it **cannot** send in a
  member channel, then remove the role.

## Verify before writing (guarded run)
`PUT /channels/{id}/permissions/{MUTED}` 50013s for **two independent reasons** — check
BOTH before attempting writes:
1. **Flag:** the bot role must carry `MANAGE_CHANNELS`.
2. **Hierarchy:** the bot's highest role must sit at the **TOP** of the role list (above the
   top mod role). The flag alone is NOT enough — a bot with `MANAGE_CHANNELS` but sitting
   below `Moderator` still gets `50013`.
`scripts/apply_muted_overwrites.py` asserts both (`bot_perms & MANAGE_CHANNELS` AND
`bot_top == guild_top`) and **exits before writing** if either fails, so a half-applied run
never burns you. Manual sequence: grant `MANAGE_CHANNELS` → drag bot role to top → run →
drag it back below `Moderator`.

## Bonus: confidential report drop-box channel
A member-facing `#reports` channel where members can **post but not read** others' reports
keeps moderation discoverable without forcing DMs. Overwrite recipe:
allow `VIEW_CHANNEL` + `SEND_MESSAGES`, **deny `READ_MESSAGE_HISTORY`** for `@everyone`
(members see the channel exists and can send, but can't read prior reports). Staff + the bot
retain normal read. Full recipe and staff-visibility notes:
`references/report-channel-dropbox.md`.
