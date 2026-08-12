# Onboarding content & third-party bot integration

Condensed knowledge for the two community-management jobs the mod bot doesn't
do itself: publishing the welcome/rules copy, and picking + wiring third-party
bots (verification gate, reaction roles).

## 1. Third-party bot permission comparison (real decoded integers)

Decoded from each bot's default Discord invite `permissions` integer. Bit map:
1=KICK, 2=BAN, 3=ADMINISTRATOR, 4=MANAGE_CHANNELS, 7=VIEW_AUDIT_LOG, 9=MANAGE_ROLES,
10=MANAGE_WEBHOOKS, 11=MANAGE_EMOJIS_AND_STICKERS, 13=MANAGE_THREADS, 16=VIEW_CHANNEL,
17=SEND_MESSAGES, 20=READ_MESSAGE_HISTORY, 23=MENTION_EVERYONE.

| Bot | Use | Servers | Int | Admin? | Notes |
|---|---|---|---|---|---|
| **MEE6** | Leveling, automod, welcome, alerts, giveaways | 21.5M | `296150887519` (24 bits) | **YES** | Over-permissioned; gate-relevant features paywalled |
| **enforcement-bot** | Reaction roles, autoroles, logging, starboard, custom cmds | 14.7M | `66321471` (18 bits) | **YES** | Lighter; free features; lacks MANAGE_ROLES in default int |
| **Captcha.bot** | Verification gate (captcha before talk) | 576K | `268520470` (7 bits) | **NO** | KICK, BAN, MANAGE_CHANNELS, MANAGE_WEBHOOKS, MANAGE_EMOJIS_AND_STICKERS, VIEW_CHANNEL, CONNECT |
| **Hydra** | Welcome images, reaction roles, social engagement | 6.2M | `37088600` (12 bits) | **YES** | Over-permissioned |

**Takeaway:** 3 of 4 request Administrator by default. Only Captcha.bot is
least-privilege. Rule for ALL of them: **uncheck Administrator at invite**, grant
only the bits the feature needs.

## 2. Recommended onboarding flow (this server)

```
join
  → Captcha.bot gate (prove human) → grants Verified role
  → land in #welcome-and-rules (read welcome + pinned rules)
  → enforcement-bot reaction-role picker → member self-sorts into engine/discipline/ping roles
  → (Gamehub-mod runs moderation/triage/announcements in the background)
```

Captcha.bot and enforcement-bot don't overlap; neither touches Gamehub-mod's job.

## 3. enforcement-bot reaction-role set (proposed)

Open server — roles are identity + opt-in pings, NOT channel locks (locking
would require restructuring every channel and fights the Captcha gate).

| Group | Roles | Select |
|---|---|---|
| Engine | @Unreal · @Unity · @Godot · @Other-Engine | multi |
| Discipline | @Programmer · @Artist · @Designer · @Writer · @Hobbyist | multi |
| Ping opt-in | @AI-Agents · @Showcase-Alerts · @Event-Alerts | opt-in |

Open questions to confirm with owner: which roles to keep (could drop
@Writer/@Designer), where the picker lives (#get-roles channel vs folded into
#welcome-and-rules), and whether the welcome is a channel embed or a DM.

## 3b. Wiring the reaction roles — automation boundary (critical)

The Discord mod bot (Hermes/Gamehub-mod) can CREATE the self-serve roles and the
picker channel via the API, but it CANNOT bind emoji → role. That binding lives
in enforcement-bot's own backend and is reached ONLY by:

- the **carl.gg dashboard** (https://carl.gg, log in with Discord, select the
  server) — requires the OWNER's Discord session, which the agent does not have;
  or
- enforcement-bot's in-server **`!rr` commands**, which need a human with enforcement-bot
  perms (not the agent — another bot's token can't write enforcement-bot's backend).
  **The real "add many" command is `!rr addmany <msg_id> <emoji> <@role>`:**
  type the first pair, then press **Shift+Enter** between each subsequent
  emoji/role pair, then Enter to send the whole block. **There is NO
  `!rr mode multiple` command** — that is a myth and was the cause of a
  "Carl isn't working" session. Carl's default reaction-role *type* is `normal`,
  which already lets members pick MANY roles; `!rr unique <msg>` would RESTRICT
  to one and must NOT be used for a multi-select self-serve menu. If reactions
  don't appear after `!rr addmany`, run `!rr fix` (re-adds missing reactions).
  For the dashboard path, carl.gg has a "Single role" toggle per group — leave
  it OFF for multi-select.

Another bot's token cannot write enforcement-bot's config. If you try to "finish"
reaction roles via the Discord API you will dead-end — instead hand the owner a
paste-ready emoji→role→ID map and let them do the click. This is a manual owner
step, not an automation gap. Verify the roles + picker channel already exist
first (read-only `GET /guilds/{id}/roles` + `GET /channels/{id}`), then stop.

**carl.gg steps (canonical):** sidebar → Reaction Roles → Create new → channel =
picker channel → mode = Embed → add one group per category, leave "Single role"
OFF for multi-select → add emoji+role rows → save (enforcement-bot posts embed + adds
reactions).

**Hierarchy gotcha:** enforcement-bot can only hand out roles BENEATH its own highest
role. Its role must sit ABOVE every self-serve role it manages and BELOW staff
(mod-lead/senior-mod). A too-low enforcement-bot role silently fails to grant roles.

**Don't confuse with Autorole:** enforcement-bot's Autorole feature (posts an
"Autorole added" message) grants a role on JOIN — it is NOT the reaction picker.
Check the picker channel for a stray Autorole message that could double-grant.

## 4. Exact least-privilege invite perms

**Captcha.bot** — default int `268520470` lacks MANAGE_ROLES (needed to grant
Verified). At invite: keep admin OFF, ensure `MANAGE_CHANNELS` + `MANAGE_ROLES`
are ticked. Invite URL (from discordbotlist):
`https://discord.com/oauth2/authorize?client_id=<id>&scope=bot+applications.commands&permissions=268520470&redirect_uri=https%3A%2F%2Fservercaptchabot.xyz%2Fsupport&response_type=code`
Docs: `https://docs.captcha.bot/`. Use **web-verification** method (harder to bypass than image).

**enforcement-bot** — default int `66321471` requests Administrator. At invite:
**uncheck Administrator**, grant: MANAGE_ROLES, VIEW_CHANNEL, SEND_MESSAGES,
EMBED_LINKS, READ_MESSAGE_HISTORY, ADD_REACTIONS, MANAGE_MESSAGES. Skip
MANAGE_CHANNELS / MANAGE_WEBHOOKS / BAN / KICK. Position its role below mod-lead
and senior-mod (and below Gamehub-mod once the bot-perm drift is reverted),
above the engine/discipline roles it manages (a bot can only hand out roles
beneath its own highest role).

## 5. Pin 50013 fix (rules post won't pin)

Symptom: `PUT /channels/{id}/pins/{msg}` → `{"message":"Missing Permissions","code":50013}`.
Cause: a channel-level permission overwrite on `#welcome-and-rules` strips
`MANAGE_MESSAGES` from the bot role, even though the guild-wide role flag has it.
Fix (pick one):
- **UI re-pin (zero risk, recommended):** right-click the rules message → Pin.
- **Allow override:** add a per-channel *allow* overwrite for `MANAGE_MESSAGES`
  on `#welcome-and-rules` for the bot role (bot holds MANAGE_CHANNELS from the
  drift, so it can write this itself — but per owner preference, confirm before
  any perm write).

## 6. Repetition-review checklist (run BEFORE posting)

- No repeated sentence opener across consecutive rules (e.g. "Keep it…" ×3).
- No word repeated 3+× in one block ("build", "that's", "cool").
- Vary sentence length; avoid all-rules-same-structure.
- Em-dash and emoji-decoration kept minimal (humanizer pass handles most).
- For Discord delivery: split into short labeled blocks, not one wall.

## 7. Posting mechanics

- Toolset has NO `send_message`/`create_message` (Capabilities reality check).
- POST via curl with bot token; read token from profile `.env`; never print it.
- Set `"allowed_mentions": {"parse": [], "replied_user": false}` so the bot
  never pings `@everyone`/`@role`.
- urllib hits Discord's Cloudflare 1010 block — use curl.
- Post order: welcome, then rules (pin), then channel openers; delete the
  superseded old pinned rules message last.
