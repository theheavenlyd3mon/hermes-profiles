# Confidential report drop-box channel (#reports)

A low-friction way for members to surface issues without DMing a mod. Members can *post* a
report but cannot *read* others' reports (privacy); staff and the bot read everything.

## Overwrite recipe (channel-level)
On the `#reports` channel, add an `@everyone` permission overwrite:
- **Allow:** `VIEW_CHANNEL` (bit 10) + `SEND_MESSAGES` (bit 11)
- **Deny:** `READ_MESSAGE_HISTORY` (bit 16)

Result: a member sees the channel in the list and can send a message, but the message history
is hidden from them - they only see their own posts. Staff (and the bot, via its role) keep
full read because their role/position grants `READ_MESSAGE_HISTORY`.

### Bit math
- allow = (1<<10) | (1<<11) = 3072
- deny  = (1<<16)         = 65536

### curl (bot must have MANAGE_CHANNELS + be at role top - see muted-role-setup.md)
```bash
TOKEN=...; G=...; RID=<reports_channel_id>
curl -s -X PUT "https://discord.com/api/v10/channels/$RID/permissions/$G" \
  -H "Authorization: Bot $TOKEN" -H "Content-Type: application/json" \
  -d '{"type":0,"allow":"3072","deny":"65536"}'
```
(`$G` == guild id doubles as the @everyone role id.)

## Bot logging side
The bot (Gamehub-mod) reads `#reports` and can log each report to `#audit-review` / a thread
for human mods, then triage. Keep the channel itself member-post-only; never grant members
`READ_MESSAGE_HISTORY`. Do NOT make it staff-only to post - members must be able to send.

> ⚠️ **SILENT BLINDNESS TRAP (found 2026-07-13, cost a real debugging cycle):** the
> `@everyone` `READ_MESSAGE_HISTORY` **deny** also strips the **bot's own** base read of
> this channel. Discord applies the `@everyone` channel deny *after* base role grants, so
> even though the bot role grants `READ_MESSAGE_HISTORY` guild-wide, the channel deny wins
> and the bot fetches **0 messages** from `#reports` - it can *post* but never *read back*.
> Any watchdog that relies on reading `#reports` silently sees nothing. **Fix:** add an
> explicit **ALLOW** overwrite for the bot's own role on `#reports` granting
> `READ_MESSAGE_HISTORY` (bit 16) + `VIEW_CHANNEL` (bit 10). Members stay blind (their
> `@everyone` deny is untouched) - only the bot regains read. Without this, accept that the
> drop-box is blind to the bot.
