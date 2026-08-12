---
name: discord-moderation-bot
description: Configure Hermes Agent as a Discord moderation / community-management bot. Covers Dev Portal app+bot creation, the correct SCOPED permission integer for moderation (NOT the docs' chat-only default), and gateway .env scoping (home channel, allowed/ignored channels, allowed roles). Also answers "what Discord skills are available?" → there are none; Discord is gateway config, not a downloadable skill.
---

# Discord Moderation Bot (Hermes Agent)

## When to use
- User wants a Hermes-powered Discord bot for moderation, community management, or staff tooling.
- User asks "what Discord skills / plugins are available for Discord?" or "how do I add you as a Discord bot?"
- You are wiring up `~/.hermes/.env` + a Dev Portal app so Hermes runs as a guild bot.

## Key fact — Discord is gateway config, NOT a skill
There is **no downloadable Discord skill** in Hermes or the agentskills.io registry (a registry search for "discord" returns 0 results). Discord support is built into the **messaging gateway**. You configure it via:
- `~/.hermes/.env` (or a profile `.env`, e.g. `~/.hermes/profiles/<profile>/.env`) — credentials + toggles
- `~/.hermes/config.yaml` — structured `discord:` section
- The **Discord Developer Portal** — the bot app, token, privileged intents, and invite permissions

Docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord

So when the user asks "what skills do you need for Discord," the answer is: **none to install** — you create a bot app and set env vars. Do not burn a session searching the skills registry for "discord."

## Workflow (condensed)
Full step-by-step: see `references/dev-portal-walkthrough.md`.

1. Dev Portal → New Application → name it (e.g. `GameHubMod`).
2. Bot tab → Public Bot ON, Require OAuth2 Code Grant OFF. Set username.
3. **Privileged Gateway Intents**: enable **Server Members Intent** + **Message Content Intent**. Without Message Content Intent the bot receives empty message text — the #1 cause of "online but won't respond."
4. Reset Token → copy (shown once, store securely). **Do NOT grant Administrator** — scope via invite perms instead.
5. Build invite: Installation tab (Guild Install, scopes `bot`+`applications.commands`) OR manual URL:
   `https://discord.com/oauth2/authorize?client_id=APP_ID&scope=bot+applications.commands&permissions=PERM_INT`
6. Invite to server (you need Manage Server).
7. Copy your Discord User ID (Developer Mode → right-click self → Copy User ID).
8. Add env vars (below), then start the gateway (`hermes gateway`) or run `hermes gateway setup` interactively.

## Permission integer — moderation, not chat-only
The docs' "Recommended" integer `274878286912` is for **chatting only** — it lacks Manage Messages, Kick/Ban, Moderate Members (timeout), and View Audit Log. A moderation bot needs those.

**Use `1494917180614`** for a scoped moderation bot (no Administrator, no `MANAGE_CHANNELS`, no `MANAGE_WEBHOOKS`). It grants: View Channels, Send Messages, Send in Threads, Embed Links, Attach Files, Add Reactions, Read History, Manage Messages, Manage Threads, **Manage Roles**, Kick, Ban, **Moderate Members (timeout)**, View Audit Log.

> ⚠️ **Decode-trap guard:** Discord bit *labels* drift (bit 40 is `MODERATE_MEMBERS`
> now, was `CREATE_EVENTS` in old docs). Decode against the canonical table in
> `references/discord-permission-bits.md` and test each NEEDED bit via
> `(p >> bit) & 1` before reporting a permission's state. In this session a decode
> script with a mislabeled bit map wrongly claimed BAN/KICK were OFF (they are ON)
> — verify, don't extrapolate. Practical effect of this integer: the Discord
> *permission* MODERATE_MEMBERS (bit 40) IS present, but the installed Hermes
> *tool* exposes no `timeout_member` action, so enforcement still goes through the
> `Muted` role; and `MANAGE_CHANNELS` (bit 4) is absent, so the bot cannot create
> channels — build structure in the UI.

> ✅ **Correct integer: `1494917180614`** (includes `MANAGE_ROLES`, bit 28). The earlier `1494648745158` was missing Manage Roles, so the bot could not apply the `Muted` role. The `scripts/compute_permissions.py` PERMS list now asserts this exact value — run it to verify.

To recompute or tune for your server, run `scripts/compute_permissions.py` (edit the `PERMS` list). Never include Administrator (bit 3) for a least-privilege mod bot.

## Gateway .env scoping for a moderation bot
Add these to the profile `.env` (replace IDs with the real ones):

```bash
DISCORD_BOT_TOKEN=...                       # from Dev Portal step 4
DISCORD_GUILD_ID=...                         # server ID (Developer Mode → Copy Server ID)
DISCORD_ALLOWED_USERS=YOUR_USER_ID          # comma-separated; you + other human mods
DISCORD_ALLOWED_ROLES=MOD_ROLE_ID           # any member with this role is authorized (OR with users)
DISCORD_HOME_CHANNEL=MOD_OPS_CHAN_ID        # proactive msgs (cron) land here
DISCORD_FREE_RESPONSE_CHANNELS=MOD_OPS_CHAN_ID   # bot answers freely in staff channel
DISCORD_ALLOWED_CHANNELS=MOD_OPS_ID,AUDIT_REVIEW_ID  # lock scope — do NOT add #announcements here (post-target-only)
DISCORD_IGNORED_CHANNELS=GENERAL_ID,SHOWCASE_ID,ENGINE_IDS           # defense-in-depth
DISCORD_REQUIRE_MENTION=true                 # default; quiet outside free-response/mention
```

Notes:
- `DISCORD_ALLOWED_ROLES` is an **authorization allow-list** ("any human wearing this role may command the bot"), NOT a Discord hierarchy setting. The bot does **not** receive the mod role, and mods do **not** get a special permission — authorization is orthogonal to role *position*. Mods stay above the bot purely via the **role hierarchy** you set in Server Settings (bot role below `Moderator`), which is what prevents the bot from ever muting/removing a mod. The two concepts are independent; don't conflate them. New mods get bot access the moment you assign them the role — no config push.
- `DISCORD_ALLOWED_CHANNELS` + `DISCORD_IGNORED_CHANNELS` together keep the bot out of member-facing channels it shouldn't read/act in.
- `DISCORD_FREE_RESPONSE_CHANNELS` makes the staff channel mention-free (per a mod bot's spec where it lives in #mod-ops).
- **`#announcements` stays OUT of `DISCORD_ALLOWED_CHANNELS`** — it is a *post-target-only* channel (bot sends approved text there, triggered from a `#mod-ops` command). If added to ALLOWED_CHANNELS the bot will field member @mentions in the broadcast channel. The bot's role still has View+Send on it so it can post.
- Env vars override `config.yaml` `discord:` values when both are set.

Full env-var table + `config.yaml` `discord:` block: Discord docs "Configuration Reference" section.

## Capabilities reality check (this Hermes build)
The installed Hermes Discord tool (`tools/discord_tool.py`) implements only these `server_actions`:
`list_guilds, server_info, list_channels, channel_info, list_roles, member_info, search_members, fetch_messages, list_pins, pin_message, unpin_message, delete_message, create_thread, add_role, remove_role`.

There is **no** native `timeout_member`, `kick_member`, `ban_member`, `get_audit_log`, **or `send_message`/`create_message`**. The bot can read and moderate but **cannot post** through the toolset. To publish text (rules posts, announcements, periodic digests, anomaly alerts), POST via the bot token with `curl` — see the *Periodic digests / alerts* section below. A "moderation bot" here enforces policy via:
- **Message deletion** (`delete_message`) for rule-breaking posts.
- **A `Muted` role** applied/removed with `add_role` / `remove_role` — the practical timeout. **Two conditions BOTH required for it to actually silence anyone:**
  1. **Position:** `Muted` MUST sit **above** `@everyone`/`Member` (and below the bot's own role + `Moderator`). A role *deny* only outranks an *allow* from an equal-or-lower role — if `Muted` sits **below** `@everyone`, members' base Send *allow* wins and muting **silences no one** (silent failure).
  2. **DENY overwrites (the part most people miss):** Discord roles can ONLY **grant** permissions — they cannot deny. Position alone does NOT mute. You must add a **permission overwrite** on the `Muted` role. **The bot can only deny perms it actually HOLDS** — use the safe set `SEND_MESSAGES` + `SEND_MESSAGES_IN_THREADS` + `ADD_REACTIONS` (the `Gamehub-mod` role lacks `CONNECT`/`SPEAK`, so denying them 50013s on a NEW overwrite). **Do NOT deny `Mention Everyone`** (50013 even at top position). Without these overwrites, `@everyone` still grants Send and a muted member keeps posting.
  - **Write PER-CHANNEL (not category) via the corrected `scripts/apply_muted_overwrites.py`.** A fresh *category-level* overwrite also 50013s on create (see cause #3 in `references/muted-role-setup.md`); per-channel with the safe deny set lands reliably on every member channel. A pre-existing category deny is fine (it's an edit and cascades), but for a clean first run use the script. Staff category is skipped so the bot can never silence staff.
  - **Verify with `scripts/inspect_muted.py`** — it reports EFFECTIVE silence (own overwrite OR inherited from the parent category), so cascaded category denies show as silenced even when the child has "no overwrite". **Set up the overwrites via `references/muted-role-setup.md`** (recipe + `50013` diagnosis + temp-promote walkthrough + cascade gotcha + cause #3).
  Position the **bot's own role above `Muted`** (so it can apply/remove it) but **below `Moderator`** (so it can never touch a mod). Then run a live test: apply `Muted` to a throwaway account and confirm it loses Send in a member channel.
- **Threads + pins** for triage and notices.
- **Read ops** for triage/report context.
- **POST via the bot token (curl)** for anything the toolset can't do natively — see below.

### Periodic digests / alerts (the `no_agent` cron + curl-POST pattern)

Because there is **no `send_message` action and no scheduler**, the standard way to
push periodic content (audit-log digests, anomaly alerts, role-rotation notices) is a
**`no_agent` cron job** that runs a bash script which reads the bot token from the
profile `.env` and POSTs to Discord with `curl`. See `references/audit-watch-digest.md`
(full pattern, registration, testing) and `scripts/audit_watch.sh` (ready template —
fill in `GUILD` / channel / role IDs + the alert mention). Key points:
- `deliver=local` + `no_agent=true` → the script POSTs itself and stays **silent when
  nothing is new** (watchdog pattern; Discord stays clean between events).
- Diff a state file (`last_id`) so each run reports only new audit entries.
- **First run must baseline only** (write `last_id`, post nothing) — otherwise you
  spam a 100-event burst on install.
- Test by force-resetting the state file to `{"last_id":"0"}`, running once (verifies
  the POST path), then deleting the test message and resetting the baseline.

Bans, role changes above the bot's own, and ambiguous calls are **escalated to human mods** in the staff channel. Grant the bot role the broader scoped perms (`1494917180614` — includes Manage Roles) anyway so a future tool build or manual action can use them, but do not expect native timeout/ban from this build.

## Pitfalls
- **Don't assume an existing token is for this bot.** A `.env` may contain a `DISCORD_BOT_TOKEN` from an unrelated app. Verify with the user before reusing; a fresh app is often cleaner. (This session: a pre-existing token was "for a different thing.")
- **Use the CORRECT scoped perm integer `1494917180614`** (includes Manage Roles). The earlier `1494648745158` was missing Manage Roles — without it the bot cannot apply the `Muted` role. The docs' default `274878286912` is chat-only (lacks Manage Messages / Manage Roles / Kick / Ban / Moderate / View Audit Log). NOTE: even with those perms, the *installed Hermes Discord tool* only implements read + `delete_message` + `pin/unpin` + `create_thread` + `add/remove_role` (see Capabilities reality check). Enforcement is via a **Muted role** + message deletion; escalate bans to human mods.
- **Never grant Administrator** to the bot app/role. Use the scoped integer; least privilege.
- **The bot cannot create channels.** There is no `create_channel` action (only `create_thread`, which makes threads inside an existing channel), and `MANAGE_CHANNELS` is deliberately excluded from the perm integer. A human must build the category + channels + roles in the Discord UI; see `references/server-structure-build.md` for the exact steps. The bot only operates within that structure.
- **Profile vs global .env**: under a Hermes profile (e.g. `gamehub-mod`), the relevant file is `~/.hermes/profiles/<profile>/.env`, not the global one. Check both; profile values drive that profile's sessions.
- **Read real channel/role IDs via `curl`, NOT by hand-copying** — see `references/discord-api-introspection.md` for the working commands (guild → channels → roles, sorted by `position`). Pull the token from the profile `.env`, then set `DISCORD_GUILD_ID`, `DISCORD_ALLOWED_ROLES`, and channel IDs from the output.
- **Use `curl`, NOT Python `urllib`, for any raw Discord REST call.** Discord's Cloudflare WAF returns HTTP 403 **Error 1010** ("Access denied based on browser signature") to `urllib`/many Python stacks even with a valid token. `curl` passes. This 1010 is a *probe artifact only* — the real gateway client connects fine (so `gateway.log` showing "✓ discord connected" proves the token is valid). Don't misread a 1010 probe failure as a bad token.
- **`gateway_state.json` is often stale** ("stopped", old PID) while the gateway is live. Source of truth for connection is `profiles/<profile>/logs/gateway.log` — look for `Connecting to discord...`, `[Discord] Connected as NAME#XXXX`, `✓ discord connected`.
- **`DISCORD_GUILD_ID` can be empty yet the gateway still connects** (token alone logs in), but `discord_admin` actions needing `guild_id` won't resolve — always set it. `platforms.discord.enabled: false` in config.yaml sits under `display.runtime_footer` (cosmetic footer toggle), NOT the adapter switch — don't misread it as "Discord disabled."
- **`config.yaml` edits must go through `hermes config`, not direct file writes.** A `patch`/`write_file` on config.yaml is refused by a security guardrail: `Refusing to write to Hermes config file ... use 'hermes config' instead.` Use e.g. `hermes config set discord.server_actions "list_guilds,..."`. `.env` may be edited directly (prefer an idempotent script over hand-edits to avoid duplicate keys).
- **Roles created via slash-command sync show as `BOT-MANAGED`.** When you create a `Moderator`/`Muted` role through the bot or it auto-syncs commands, Discord marks them `managed: true` and lists them under the bot. That's expected — the introspection script tags them `BOT-MANAGED`. Position them by hand in Server Settings → Roles regardless of the tag.
- **`hermes config` has NO `get` subcommand** — inspect with `hermes config show` / `hermes config check`. And the gateway's local API port is set via **`platforms.api_server.extra.port`**, NOT `platforms.api_server.port`. `config set platforms.api_server.port N` writes a *dead sibling key* the gateway ignores (it still binds the old port → `Port 8645 already in use`). When two Hermes profiles run on one machine their `api_server` collides on 8645 by default — give the second profile a free port (e.g. 8650) via `extra.port`.
- **Draft, don't write blindly**: user wants to review `.env` changes (with placeholders for IDs) and approve before you write. Present a redacted snippet first.
- **Bot-role perm/position DRIFT after a temp-promote (security — verify & revert).** The one-time promote you do to write `Muted` overwrites or create channels can be left in place, leaving the bot role ABOVE human mods and holding BAN/KICK/MANAGE_CHANNELS. Incident this session: `Gamehub-mod` ended at **position 6 (above senior-mod 5 / mod-lead 4)** with perm int **`1494917180630`** (BAN+KICK+MANAGE_CHANNELS ON). Charter wants the bot BELOW mods and WITHOUT BAN/KICK. **Fix (you, in UI — bot can't self-edit):** drag the role back below `mod-lead`/`Moderator`; strip BAN(`bit 2`)/KICK(`bit 1`)/MANAGE_CHANNELS(`bit 4`) → target `1494917180608` (keeps `MANAGE_ROLES` `bit 28` so it can still apply/remove `Muted`). Decode the live integer with `references/discord-permission-bits.md` BEFORE assuming least privilege still holds; re-check after any promote.
- **`GET /guilds/{id}/membership-screening` 404s until the server is a Community server.** If `GET /guilds/{id}` shows `features` does NOT include `COMMUNITY`, that endpoint returns `404 Not Found` — NOT a token/perm error. Native rules-accept gating (Membership Screening) requires enabling Community first (Server Settings → Enable Community). Don't confuse it with the bot lacking access.
- **Deliver Discord content drafts as SEPARATE, clearly-labeled SHORT blocks, not one long message.** When handing the owner multiple artifacts (welcome post + rules block + #introductions opener), Discord splits/collapses a single long message so the user can't easily find or review each part. Post each as its own short, headed block (e.g. '① WELCOME', '② RULES', '③ INTRODUCTIONS'). Also offer to write drafts to a local `.md` file for outside-chat editing when the user struggles to read them in-chat. (User feedback this session: 'I can't see where it is to read it in our chat.')

- **The `Muted` DENY overwrites are normally a manual (or temp-promote) step — the bot usually cannot write them via API.** Three distinct `50013 Missing Permissions` failure modes:
  1. **Hierarchy block (real):** even with `MANAGE_CHANNELS` *flag* reading True, `PUT /channels/{id}/permissions/{Muted}` is rejected unless the bot's highest role is at the **TOP** of the role list (above the channel's controlling context). Confirm with `scripts/check_bot_pos.py` — if `bot_top != guild_top`, Discord will 50013. **Workaround:** temporarily drag the bot role to the top, run `scripts/apply_muted_overwrites.py` (curl-based, **per-channel**, skips Staff), then drag it back below `Moderator`.
  2. **`MENTION_EVERYONE` in the deny set (silent trap):** even with the bot role at the TOP, a deny that includes `MENTION_EVERYONE` (bit 17) returns 50013 because the bot is not the server owner and Discord refuses a non-owner from denying @everyone mention. **Always exclude `MENTION_EVERYONE`** from the deny — a muted member can't talk anyway, so the loss is cosmetic.
  3. **Denying a permission the bot role does NOT hold (the silent *create* trap):** Discord lets a non-admin role *edit* an existing overwrite freely, but **creating a NEW overwrite** that denies any permission the role itself lacks returns `50013`. The `Gamehub-mod` role (`1494917180614`, or `...0630` while MANAGE_CHANNELS is temporarily added) does NOT have `CONNECT` (bit 20) or `SPEAK` (bit 21). So a Muted deny that includes voice perms fails on every channel/category that has **no pre-existing** Muted overwrite — even with the bot at the top. **Symptom seen in practice:** the 2 categories that already had Muted overwrites succeeded (they were *edits*), the other 5 categories 50013'd (they needed *new* overwrites). A probe confirmed the bot CAN create an empty overwrite and CAN edit, so the discriminator is the denied bits, not "can't create at all." **Fix:** deny ONLY perms the bot holds — `SEND_MESSAGES` (11) + `SEND_MESSAGES_IN_THREADS` (38) + `ADD_REACTIONS` (6). That silences text completely and creates cleanly on every channel. **Voice muting cannot be done by the bot** — if you want muted members unable to speak in voice, deny `CONNECT`/`SPEAK` by hand in the UI (you hold those perms as owner); the bot can't. The corrected `scripts/apply_muted_overwrites.py` uses this safe set and writes per-channel.
  - **Category cascade gotcha:** if a child channel has a *stale empty* `Muted` overwrite, the category deny does NOT reach it. `inspect_muted.py` now reports EFFECTIVE silence (own OR inherited), so a child with no own overwrite still shows as silenced if its parent has the deny.
  - **Manual alternative:** Edit Channel → Permissions → + `Muted` → deny Send/Threads/Reactions (NOT Connect/Speak unless you are owner, NOT Mention Everyone).
  - **Remove `MANAGE_CHANNELS` from the bot's role after setup** — it is deliberately excluded from the `1494917180614` integer; the user added it manually for the one-time write. Keep only `MANAGE_ROLES` so the bot can still apply/remove `Muted`.
- **Reusable support files for this skill:** `references/discord-permission-bits.md` (CANONICAL bit table + per-server integers + curl/decode recipe — decode against this BEFORE reporting any perm state), `references/mfa-60003-pitfall.md` (60003 "Two factor required" — symptom, detection, workarounds; also covers 50001 vs 50013 vs 60003 error-code triage), `references/verified-role-gate-setup.md` (Verified as Member replacement — permission flow, bot-grantable vs owner-set perms, channel-level VIEW/SEND distinction), `scripts/inspect_muted.py` (verify effective Muted silence — own OR inherited from parent category; reads real token), `scripts/check_bot_pos.py` (print bot's highest role position vs guild top — run BEFORE writing overwrites; a non-top bot gets 50013), `scripts/apply_muted_overwrites.py` (per-channel deny write with the SAFE set — needs bot role temp-promoted, reads real token), `scripts/audit_watch.sh` (silent `no_agent` cron watchdog that POSTs audit digests/alerts via curl), `references/muted-role-setup.md` (overwrite recipe + 3× 50013 diagnosis + cascade gotcha + temp-promote walkthrough), `references/discord-api-introspection.md` (curl-based guild/channel/role reads), `references/server-structure-build.md` (build the category + channels + roles in the UI), `references/audit-watch-digest.md` (periodic digest/alert pattern + cron registration + test recipe), `references/reports-dropbox.md` (confidential `#reports` drop-box recipe), `references/server-launch-readiness-sweep.md` (8-point pre-public launch audit: reaction roles live?, verification gate wired, content filter, mod MFA, bot-perm drift, Member hole, Muted effective, Community features — plus the curl pull + BITS decode recipe), `references/verification-captcha.md` (Captcha.bot invite/setup + native Membership Screening note + gate-channel layout pattern), `references/verification-gate-setup.md` (this server's concrete Captcha.bot + enforcement-bot recipe: Verified role, #verify/#get-roles, gate-channel visibility overwrites, and the 4 gate pitfalls incl. Captcha.bot's missing MANAGE_ROLES + ordering/50013 trap), `references/mod-alert-watchdog.md` (recommend-only enforcement ladder + watchdog recipe + 5 pitfalls incl. the #reports blind-spot), `scripts/mod_alert_watchdog.sh` (runnable POSIX watchdog — baseline-first, temp-file JSON POST, pings both mod roles), `templates/rules-post.md` (pinned rules post for #welcome-and-rules), `templates/welcome-rules-intros.md` (known-good welcome + 12-rule + #introductions drafts, already posted — copy & modify). Also see `references/onboarding-content-and-third-party-bots.md` (third-party bot permission comparison with decoded invite integers, enforcement-bot reaction-role set + **3b automation boundary / carl.gg wiring / hierarchy + autorole gotchas**, least-privilege invite perms, publishing/pinning sequence).

### Permission pitfalls (403 variants) — bot edits to itself/role hierarchy
- **DECODE-TRAP FIRST (silent wrong answers):** Never report a role's permissions
  without decoding against the **canonical bit table** in
  `references/discord-permission-bits.md`. A decode script with an incomplete or
  mislabeled mapping produces *confidently wrong* conclusions (e.g. claiming
  BAN/KICK were OFF at `1494917180614` when they are ON; or probing bit 40 and
  concluding "no timeout" because an old table maps 40→CREATE_EVENTS instead of
  MODERATE_MEMBERS). Decode with the full BITS dict in that reference and test
  each NEEDED bit individually via `(p >> bit) & 1`. After decoding,
  **re-state only what the bits prove** — do not extrapolate.
- **User preference — try the action, then report blockers.** The owner wants the bot
  to ATTEMPT role/permission changes (e.g. "you change the permissions on the verified
  role") rather than pre-emptively explaining why something might fail. When blocked:
  try the API call, show the error code, then explain the workaround. Never deliver a
  status report of what's blocked without having attempted the action first. The one
  exception: the bot must never attempt to edit its own role via API (PATCH
  /roles/{bot_role}) — that always returns 50013, and it's a permanent constraint
  (Discord forbids a role from modifying itself).
- **The bot CANNOT edit its own role via API.** `PATCH /guilds/{id}/roles/{bot_role}`
  returns `403 Missing Permissions (50013)` even when the role flag shows the intent —
  Discord forbids a role from modifying itself or any role above it. So: **tightening
  the bot's own permissions (dropping BAN/KICK/etc.) must be done in the Discord UI**,
  not by the bot. Recommended least-privilege integer for this server is
  `1494917180608` (drops BAN `bit 2` + KICK `bit 1`; **keeps `MANAGE_ROLES` `bit 28`**
  so the bot can still apply/remove `Muted`). When decoding perms, read the role's
  `permissions` int via curl (`urllib` → 1010, see above) and test bits with
  `(perms >> bit) & 1`.
- **Error code triage — distinguish 50001 vs 50013 vs 60003.** All three return HTTP
  403 but mean different things and demand different responses:
  | Code | Meaning | Cause | What to do |
  |---|---|---|---|
  | `50001` | Missing Access | Bot can't see the channel (self-lockout from `@everyone` VIEW- on category/channel without explicit bot-role override). | Work around it — write to child channels instead, or ask the user to add bot-role ALLOW VIEW to the locked-out channel. |
  | `50013` | Missing Permissions | Bot can see the channel but lacks a specific permission bit (MANAGE_ROLES, MANAGE_CHANNELS, etc.), OR the denied perm isn't in the bot's own role, OR the endpoint requires role-hierarchy dominance. | Check the bot's permission integer against the canonical bit table. Temp-promote if hierarchy is the issue (drag to top, do the write, drag back down). |
  | `60003` | Two factor required | Server MFA Level is 1 (requires 2FA for moderation actions). Bot has no 2FA. | **Blocked until the owner disables MFA** (mfa_level=0) or does the action manually in the UI. The bot can still do cosmetic role edits (name, color, mentionable) and write permission overwrites on *accessible* channels under *accessible* categories — but even those may 60003 when the target channel is under a category that denies `@everyone` VIEW. |
  - **Real distinction seen in practice:** `#verify` (under Information cat — no @everyone deny) → PUT overwrite succeeded HTTP 204. `#reports` (under Staff cat — bot role has explicit ALLOW VIEW) → PUT overwrite succeeded HTTP 204. Child channels under Text/Voice/Unreal/Unity/Godot/AI categories (where @everyone is denied VIEW and the bot role has no explicit allow) → PUT overwrite returned **60003**, not 50001. So the MFA check happens even on channels the bot could reach — the @everyone deny on the parent category gates access, and the 60003 fires on the attempt.
  → See `references/mfa-blocked-ops.md` for the full pattern, symptom checklist, and workarounds.

- **The bot can only grant permissions it already holds to other roles.** When
  PATCHing a role's `permissions` field, Discord returns `50013` if the integer
  includes any bit the bot's own role lacks — even when the bot has `MANAGE_ROLES`
  (bit 28). This is a server-enforced constraint, not a hierarchy issue. Pattern
  observed in practice:
  - `PATCH /roles/Verified` with `permissions="1024"` (VIEW_CHANNEL only — bot has it) → **HTTP 200** ✅
  - `PATCH /roles/Verified` with `permissions="391976163073088"` (full member set incl. CONNECT, CHANGE_NICKNAME, SEND_POLLS — bot lacks those) → **50013** ❌
  - The bot's own role integer can be read via `curl`; only bits set in that integer
    can be granted to other roles. To find which bits the bot can grant, decode the
    bot role's `permissions` integer against the canonical table in
    `references/discord-permission-bits.md`, then include only those bits in the
    target role's permissions.
  - **Workaround:** the owner sets the missing permissions manually in the UI
    (Server Settings → Roles → target role → toggle on the missing perms). The bot
    sets the subset it holds, then the owner adds the rest.

- **SEND vs VIEW distinction on channel overwrites under locked categories.** The bot
  can write `SEND_MESSAGES` (bit 11) to child channels under categories where
  `@everyone` is denied VIEW, but CANNOT write `VIEW_CHANNEL` (bit 10) to those same
  channels. Pattern:
  - `PUT /channels/unreal-general/permissions/Verified` with `allow="2048"` (SEND
    only) → **HTTP 204** ✅
  - `PUT /channels/unreal-general/permissions/Verified` with `allow="3072"`
    (VIEW+SEND) → **50013** ❌
  - **Why:** SEND is a message-level permission that doesn't require the bot to see
    the channel's parent category. VIEW requires the bot to have visibility into the
    containing category, which it doesn't when `@everyone` is denied VIEW there and
    the bot role has no explicit allow.
  - **Practical rule:** to grant VIEW to a role on channels under locked categories,
    write the overwrite to the **category** (if the bot can reach it) or ask the owner
    to add it in the UI. The bot can only grant SEND-level perms on those channels
    via the API.
- **Pinning can 403 even when the role HAS `MANAGE_MESSAGES`.** If a **channel-level
  permission override** denies/omits `MANAGE_MESSAGES` on that specific channel, the
  `PUT /channels/{id}/pins/{msg}` returns 403. The role flag is necessary but not
  sufficient — a per-channel override can strip it. Fix: pin in the UI, or add a
  per-channel allow override for the bot role. (The bot's *role* had MANAGE_MESSAGES;
  the `#welcome-and-rules` channel override was the blocker.)
- **Prefer `curl`, not Python `urllib`, even for reads** — the Cloudflare 1010 block
  hits `urllib` (and `execute_code`'s urllib) too. `curl` is the reliable path for
  every raw Discord REST call in this environment.
- **Audit-log `action_type` label map — verify against the official enum.** Discord's real enum: 13/14/15 = CHANNEL_OVERWRITE_CREATE/UPDATE/DELETE, 74/75 = MESSAGE_PIN/MESSAGE_UNPIN. A hand-written LABELS map once said 14="Channel unpinned msg", so the watchdog posted a permission-overwrite edit as an "unpin" and confused the owner ("what message did I unpin?" — answer: none). Before trusting any digest label, cross-check the entry's `action_type` against https://discord.com/developers/docs/resources/audit-log#audit-log-entry-object-audit-log-events.
- **Shipped `scripts/apply_muted_overwrites.py` + `scripts/inspect_muted.py` had TWO bugs (FIXED):** they hardcoded `Authorization: Bot ***` (so never actually ran against the real token) and the apply script used the full deny set incl. `MENTION_EVERYONE` + voice perms (50013). Both now (a) read the REAL token from the profile `.env`, (b) `apply_muted_overwrites.py` denies ONLY `SEND_MESSAGES`+`SEND_MESSAGES_IN_THREADS`+`ADD_REACTIONS` and writes per-channel, and (c) `inspect_muted.py` reports EFFECTIVE silence (own overwrite OR inherited from parent category). See `references/reports-dropbox.md` (confidential `#reports` channel recipe) and `templates/rules-post.md` (pinned rules post).

### Staff/escalation conventions (this server)
- **Alerts ping BOTH mod roles (decided 2026-07-13):** mod-lead (`<@mod-role>`)
  AND senior-mod (`<@mod-role>`). Any Tier-1+ action or any `#reports`
  submission triggers a triage card in `#mod-ops` pinging both. (Earlier stance was
  "owner only, not mod-lead" — corrected this session when the owner said "espada or myself
  get pinged.") The owner changes ping targets if needed.
- **Recommend-only enforcement ladder (this server).** Gamehub-mod is the ANALYST + NOTIFIER
  and never enforces beyond applying the `Muted` role (Tier 1, its max self-action). It
  NEVER kicks or bans. enforcement-bot is the enforcement HANDS (mute/kick/ban per owner-configured
  rules; can defer to #mod-ops). Human mods decide Tier 2. Full ladder + watchdog pitfalls
  in `references/mod-alert-watchdog.md`; runnable script in `scripts/mod_alert_watchdog.sh`.
  This keeps the charter intact (no bot-initiated ban without human go-ahead) while still
  giving mods a near-real-time ping the moment anything fires.
- **Discuss channel/category structure with the owner BEFORE building it.** The bot
  cannot create channels anyway (`MANAGE_CHANNELS` is excluded), but even the *plan*
  should be agreed first: propose a layout (e.g. per-engine categories Unreal/Unity/
  Godot, each with general/showcase/help, plus a single `#ai-agents` channel under an
  "AI & Tooling" category), get sign-off, then have the human build it in the UI.
- **Confidential `#reports` drop-box** (members post, cannot read others' reports): overwrite
  recipe in `references/report-channel-dropbox.md`. The bot reads it and logs to staff for
  triage. Build in the UI (or via temp-promoted bot); see that reference.

## Onboarding content & third-party bots
Beyond the mod bot, community management covers the **welcome/rules copy** members read and **third-party bots** that fill gaps (verification gate, self-serve reaction roles). Full detail (decoded permission table, enforcement-bot role set, invite perms, post script) in `references/onboarding-content-and-third-party-bots.md`; known-good posted copy in `templates/welcome-rules-intros.md`.

**Welcome/rules publish sequence (do NOT skip):**
1. **Draft** welcome (orientation + channel map), rules, and channel openers (#introductions) as separate pieces.
2. **Humanize** each with the `humanizer` skill (strips AI-isms, adds voice).
3. **Repetition review (mandatory):** catch repeated openers ("Keep it…" ×3) and repeated words ("build"/"that's" ×4); rephrase. Long rule lists drift into parallel phrasing.
4. **Preview as SEPARATE short labeled blocks** (① WELCOME ② RULES ③ INTRO). A single long message collapses in Discord.
5. **Post via the bot token (curl), not the toolset** — no `send_message`/`create_message` action. Read token from profile `.env`; set `allowed_mentions` empty so the bot never pings @everyone/@role.
6. **Pin the rules** (`PUT /channels/{id}/pins/{msg_id}`). 403/50013 if a **channel-level override strips MANAGE_MESSAGES** from the bot role — fix by re-pinning in the UI (zero risk) or adding a per-channel allow override.
7. **Delete the superseded old post** so newcomers don't read stale rules.

**Third-party bots — one hard rule: never grant Administrator.** MEE6 / enforcement-bot / Hydra all request it by default (full server control, incl. banning you). At invite, **uncheck Administrator**; grant only needed bits (MANAGE_ROLES + MANAGE_MESSAGES + VIEW/SEND/EMBED/ADD_REACTIONS/READ). Position the bot role below human mods but above the cosmetic roles it manages (a bot can only hand out roles beneath its own highest role). Division for this server: **Captcha.bot** = verification gate (least-privilege, no admin; web-verification method); **enforcement-bot** = reaction/autoroles/starboard (free, lighter than MEE6); **Gamehub-mod** = moderation/triage/announcements only. MEE6 not recommended here (over-permissioned, paywalled gate features). See the reference for decoded permission integers and the enforcement-bot role set.

## Drafting the welcome / rules copy (humanizer pass)

When writing the orientation post, rules, and channel openers, chain the **`humanizer`**
skill and run its 29-pattern pass before posting. It strips AI-isms (em-dash overuse, rule-of-three,
"vibrant/pivotal/crucial", copula avoidance) and adds real voice, so the copy reads
like a person wrote it, not a bot.

**Humanizer availability:** it ships bundled under `~/.hermes/hermes-agent/skills/creative/humanizer`
and was also installed to THIS profile at
`~/.hermes/profiles/gamehub-mod/skills/creative/humanizer/` (copied from the default
`~/.hermes/skills/creative/humanizer/`). If a future session reports "humanizer not found,"
re-copy it from the default profile's `skills/creative/humanizer/` directory. The skill's
SKILL.md carries the full 29-pattern checklist; apply it to drafted copy, then do the
mandatory **repetition review** (catch repeated openers / repeated words), then preview as
SEPARATE short labeled blocks (① WELCOME ② RULES ③ INTRO) because Discord collapses a
single long message.

**enforcement-bot reaction-role copy tie-in:** the menu's emoji→role bullets in the welcome
post must map 1:1 to the actual `!rr addmany` pairs (see `references/onboarding-content-and-third-party-bots.md`
3b). There is NO `!rr mode multiple` command — multi-select is Carl's default `normal` type.


**Recommend-only enforcement ladder** (this server, owner-approved 2026-07-13) — Hermes
is the eyes/notifier; enforcement-bot is the hands; humans decide. Encoded in SOUL.md +
`scripts/enforcement_policy.md`:
- Tier 0 (soft): minor slip → bot deletes + note. No ping.
- Tier 1 (Muted): repeat/spam → bot applies Muted role (MAX self-action), logs. Ping after.
- Tier 2 (recommend ban): harassment / IP theft / raid → triage card + evidence in #mod-ops, pings mods, WAITS for human.
- Tier 3 (auto-ban carve-out): unambiguous automation → enforcement-bot bans + dumps evidence; Hermes pings mods. Hermes itself NEVER bans.
Watchdog: `scripts/mod_alert_watchdog.sh` (baseline-first, pings BOTH mod-lead + Head
Captain on any Tier-1+ / #reports event). Pitfalls: `references/discord-alert-pitfalls.md`.

## Verification
- `hermes gateway` → bot shows online in Discord within seconds.
- Send a DM or @mention in a scoped channel → bot responds.
- Test a timeout/moderate action only where policy permits; escalate bans to human mods.
- Check `profiles/<profile>/logs/gateway.log` for `Connecting to discord...` / `[Discord] Connected as NAME#XXXX` / `✓ discord connected` — **not** `gateway_state.json`, which is often stale.
