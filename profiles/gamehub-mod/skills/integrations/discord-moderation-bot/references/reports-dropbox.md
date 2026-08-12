# Reports drop-box channel (confidential post-only)

A member-facing channel where anyone can leave a report but cannot read other people's
reports. Staff + the bot can read. Used as `#reports` in The Agentic GameHub.

## Permission overwrite on @everyone (role id == guild id)
- allow = VIEW_CHANNEL (bit 10) + SEND_MESSAGES (bit 11) = 3072
- deny  = READ_MESSAGE_HISTORY (bit 16) = 65536

Effect: members can SEE the channel exists and POST into it, but cannot READ message history
(so they can't read other people's reports). The `Member` role grants READ_MESSAGE_HISTORY at
guild level, but a channel-level @everyone DENY overrides the base grant in Discord's
precedence, so members still can't read back. Staff roles (mod-lead, senior-mod) and the bot
inherit read access from the Staff category the channel lives in.

## Bot side (report logging)
The bot (Gamehub-mod) has View + Read History on #reports, so it can `fetch_messages` there,
summarize each new report into #mod-ops / #audit-review, and keep a running log for human
mods. It must NOT echo report contents into any member-facing channel. One message per report;
the bot keys off messages it hasn't seen (track last-seen message id in a state file).

This is the ONLY channel members can post to but not read — a deliberate confidential drop-box.
