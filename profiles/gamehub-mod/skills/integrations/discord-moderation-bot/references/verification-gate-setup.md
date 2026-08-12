# Captcha.bot gate + Carl-Bot reaction roles — concrete setup (this server)

Model: **Captcha.bot** gates humans at the door, **enforcement-bot** does reaction-roles +
enforcement, **Gamehub-mod** is recommend-only eyes/notifier. These are the exact
steps that worked on The Agentic GameHub (guild `<id>`). Adapt IDs.

## Roles / channels created
- `Verified` role (perms `0`, not hoisted) — Captcha.bot grants post-captcha. id `<id>`
- `#verify` landing channel `<id>`, `#get-roles` `<id>`
  (both under Information category `<id>`)
- Self-serve roles (bottom of list, below enforcement-bot pos 4 so it can assign them):
  Engine `Unreal` `Unity` `Godot` `Other-Engine`; Discipline `Programmer` `Artist`
  `Designer` `Writer` `Hobbyist`; Ping-opt-in `AI-Agents` `Showcase-Alerts` `Event-Alerts`
- Captcha.bot role `<id>`; carl-bot role `<id>`

## Gate — channel visibility (owner does by hand in UI; see ordering trap)
For each member-facing category: `@everyone` Deny View Channels; `Verified` Allow
View Channels. Categories: Text Channels, Voice Channels, 🔧 Unreal/Unity/Godot, AI &
Tooling, 🛠 Dev. Staff stays private (already is). **Keep `@everyone` able to see**
`#welcome-and-rules`, `#get-roles`, `#verify`, `#announcements` or new members can't
read rules / do the captcha. Do NOT deny View at the Information *category* level.

Captcha.bot dashboard (`docs.captcha.bot` or its DMs): method = **web portal**;
role-to-grant = `Verified`.

## Pitfalls (gate)
- **Captcha.bot's listed invite int `268520470` LACKS `MANAGE_ROLES`.** Without it the
  bot cannot grant `Verified` and the gate **silently fails** (members stay locked /
  never verified). Grant `MANAGE_ROLES` manually at invite time.
- **Ordering / 50013 trap:** category `View Channel` overwrites need `MANAGE_CHANNELS` +
  the writing role at the **top** of the hierarchy. If you intend to **revert
  Gamehub-mod** (drop MANAGE_CHANNELS / move below mod-lead), do the overwrites **first**,
  or do them **by hand in the UI** (the skill-endorsed "do it by hand" path — no
  temp-promote). The bot cannot self-edit its own role (403) and must stay below mods.
- **enforcement-bot reaction roles need target roles BELOW enforcement-bot's position.** New roles
  default to the bottom (below enforcement-bot) — fine out of the box; never hoist a
  self-serve role above enforcement-bot or it can't assign it.
- **Audit the base `Member` role** after provisioning: it must NOT hold `MANAGE_ROLES` /
  `KICK` / `BAN`. A base member with `Manage Roles` can self-elevate — a real escalation
  hole that drifts in easily. Check whenever roles change.

## enforcement-bot reaction roles
Post the picker in `#get-roles` via `carl.gg` or `!rr make`. Engine + Discipline =
multi-select; Ping opt-in = opt-in (off by default). Map each emoji to role id from
`created_roles.json`. Target roles must sit below enforcement-bot's role position.

## Mod alert watchdog (Gamehub-mod side)
`scripts/mod_alert_watchdog.sh` reads `#reports` (bot needs read-back — see
`references/report-channel-dropbox.md` SILENT BLINDNESS TRAP fix) + the audit log and
POSTs a triage card to `#mod-ops` pinging both mod-lead + senior-mod. Run as `no_agent`
cron, deliver=local. First run baselines silently (no history replay). Verified
end-to-end this session: posted test report → card pinged both mods.
