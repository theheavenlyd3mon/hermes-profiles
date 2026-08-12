# Verification & Captcha Gating (Discord) — knowledge bank

Condensed from research done while setting up gating for The Agentic GameHub
(game-dev + LLM/agent community). Not a mirror of upstream docs — just the
decision-relevant facts and the invite/layout recipe.

## Server Captcha Bot (Captcha.bot) — recommended external gate
- Listing: https://discordbotlist.com/bots/server-captcha-bot
- Invite (from listing): `https://discord.com/oauth2/authorize?client_id=<id>&scope=bot+applications.commands&permissions=268520470`
- Setup docs: https://docs.captcha.bot/
- Client ID: `<id>`. ~576K servers; "largest / battle-tested verification bot."
- Two verify methods: **web portal** (DM-based, much harder for bots to bypass — RECOMMENDED) and image captcha.
- What it does: requires a captcha before a member can talk; alt detection; anti-raid / phishing defense.

### Fit with our stack
- Independent of `Gamehub-mod`. Needs `Manage Roles` + `Manage Channels` to gate. No conflict with the `Muted` role (different mechanism — Captcha.bot grants a `Verified` role; we silence via `Muted`).
- **Gate-channel pattern (plan with owner BEFORE clicking invite):** new members arrive "unverified" — no `Verified` role → can only SEE a landing channel (`#welcome-and-rules`) + a `#verify` channel. After captcha, Captcha.bot grants `Verified`, unlocking the rest. Concretely: restructure member-facing channels so `@everyone` has **View Channel DENY** and only the `Verified` role (and staff) has View + Send. This is a structural change to every member channel's overwrites — agree the layout first, then apply.
- Pairs with (does NOT replace) `verification_level` (ours = 2, verified email).

## Native alternative: Discord Community + Membership Screening
- Enabling **Community** (Server Settings → Enable Community) unlocks:
  - **Membership Screening** — a rules-accept checkbox gate (no captcha). Endpoint `GET /guilds/{id}/membership-screening` returns `404` until Community is ON (server `features` includes `COMMUNITY`). Don't mistake the 404 for a token/perm error.
  - Announcement-channel subscriptions, Server Insights (at 500 members).
- Weaker than Captcha.bot but free / native. Consider later for the extras.

## Other verification bots (DiscordBotList, for reference only)
Arcane, Conquest, Appy, Captcha.bot, xNico — ranked by live votes / server count.

## Research sources used
- Zapier — how to build a Discord welcome experience (separate the warm welcome from the rules; quick-start steps; channel guide; self-serve intros with a template raise participation).
- Discord official Game-Dev Community guide (docs.discord.com) — read-only vs community vs admin channels; start minimal; Community unlocks onboarding / screening / insights.
