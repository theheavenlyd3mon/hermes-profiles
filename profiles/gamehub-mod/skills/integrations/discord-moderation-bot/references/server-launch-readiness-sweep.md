# Server launch readiness sweep

Reusable pre-launch audit for a Discord community server. Run it with the mod
bot's token via `curl` (NOT urllib — Discord's Cloudflare 1010 blocks Python
TLS) and decode everything against `references/discord-permission-bits.md`
before reporting. The sweep below is what caught three real blockers on
The Agentic GameHub before it went public.

## What to pull (curl, token from profile .env)

```bash
TOKEN=$(grep -E '^(DISCORD_TOKEN|DISCORD_BOT_TOKEN)=' ~/.hermes/profiles/gamehub-mod/.env | head -1 | cut -d= -f2-)
TOKEN=$(echo "$TOKEN" | sed -E "s/^[\"']//; s/[\"']$//")
G=<id>
curl -s -H "Authorization: Bot $TOKEN" "https://discord.com/api/v10/guilds/$G?with_counts=true" -o /tmp/g.json
curl -s -H "Authorization: Bot $TOKEN" "https://discord.com/api/v10/guilds/$G/roles" -o /tmp/r.json
curl -s -H "Authorization: Bot $TOKEN" "https://discord.com/api/v10/guilds/$G/channels" -o /tmp/c.json
# verify a specific bot is actually present (200 + bot:true), not just in role list
curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bot $TOKEN" "https://discord.com/api/v10/guilds/$G/members/<CARL_APP_ID>"
# member list (proves Guild Members intent works)
curl -s -H "Authorization: Bot $TOKEN" "https://discord.com/api/v10/guilds/$G/members?limit=3" -o /tmp/mem.json
# channel message content (rules/welcome/verify state)
curl -s -H "Authorization: Bot $TOKEN" "https://discord.com/api/v10/channels/<CHAN_ID>/messages?limit=3" -o /tmp/chan.json
# existing invites
curl -s -H "Authorization: Bot $TOKEN" "https://discord.com/api/v10/guilds/$G/invites" -o /tmp/inv.json
```

Decode the guild `verification_level`, `explicit_content_filter`, `mfa_level`,
`features` (is `COMMUNITY` present?), and every key role's `permissions` int
with the full BITS dict. Channel `permission_overwrites` tell you what each
role can/can't do per channel.

## The 8-point checklist

1. **Reaction roles live?** Find the enforcement-bot menu message; confirm all emoji to role
   pairs exist with reactions attached (count=1 = bot's own seed reaction).
   This is what proved the `!rr addmany` run actually worked.
2. **Verification gate present & wired?** A `#verify` channel that's EMPTY = no
   gate. `verification_level=2` (5-min account age) is NOT a real human check.
   Need a Captcha.bot flow or native Membership Screening (requires Community).
3. **Explicit content filter** — `0` = OFF (NSFW unscanned). Recommend `1` or `2`
   before public invites.
4. **Moderator MFA** — `mfa_level=0` = mods not forced to 2FA. Recommend `1`.
5. **Bot-role perm drift** — the mod bot's role must sit BELOW human mods and
   NOT hold BAN/KICK/MANAGE_CHANNELS (charter: max self-action is Muted). Decode
   its `permissions` int; if it's at the top with dangerous bits, flag it as a
   manual UI revert (bot can't self-edit; see permission pitfalls).
6. **Member role hole** — confirm `Member`/`@everyone` do NOT carry MANAGE_ROLES
   or other dangerous bits (a prior finding that turned out already fixed).
7. **Muted role effective** — position above `@everyone` AND per-channel DENY
   overwrites present (see muted-role-setup.md). Verify, don't assume.
8. **Community features** — if `features` lacks `COMMUNITY`, native rules gate
   + discovery are unavailable; `GET /guilds/{id}/membership-screening` 404s
   (not a token error).

## Owner-only actions (cannot be done by the bot)

Verification gate setup (Captcha.bot dashboard / Community enable),
explicit-content-filter + mod-MFA toggles, and bot-role perm/position reverts
all require the owner in Server Settings. The sweep SURFACES them with exact
evidence + a step checklist; it does not (and cannot) execute them.

## Hits from the real sweep (The Agentic GameHub, 2026-07-13)

- Reaction roles: all 12 pairs live on msg `<id>`.
- Verification: `#verify` empty, `verification_level=2` only -> blocker.
- Content filter: `0` (OFF). Mod MFA: `0` (OFF).
- Bot drift: Gamehub-mod role at position 20 (highest) with
  BAN/KICK/MANAGE_CHANNELS/MANAGE_ROLES — charter violation, needs revert.
- Member hole: already fixed (exact decode showed no MANAGE_ROLES).
- Invites: two with no max-uses/expiry — tighten at launch.
