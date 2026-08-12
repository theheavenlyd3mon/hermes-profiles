#!/usr/bin/env python3
"""Write the `Muted` DENY overwrite to every member-facing text/announcement channel.

CORRECTED (see references/muted-role-setup.md, pitfall #3):
- Reads the REAL token from the profile .env. (The previous version hardcoded
  `Authorization: Bot ***` and silently never ran.)
- Denies ONLY perms the bot role actually holds: SEND_MESSAGES (11),
  SEND_MESSAGES_IN_THREADS (38), ADD_REACTIONS (6). Denying CONNECT (20) / SPEAK (21)
  -- voice perms the bot LACKS -- returns 50013 on a NEW overwrite, because Discord
  forbids a non-admin role from denying a permission it doesn't hold. (Editing an
  existing overwrite is exempt, which is why the 2 categories that already had Muted
  overwrites "succeeded" with the full deny while the rest 50013'd.)
- Written PER-CHANNEL (not category). Fresh category overwrites hit the same 50013 on
  create with the bot's perm set; per-channel with the safe set works reliably. A
  pre-existing category deny is still fine (it's an edit), but for a clean first run,
  per-channel with the safe set is what lands.
- Skips Staff channels so the bot can never silence staff.

Prereq (one-time, revert after): the bot's role must hold MANAGE_CHANNELS AND sit at the
guild's TOP position, else Discord returns 50013. The scoped int 1494917180614 lacks
MANAGE_CHANNELS -- add it temporarily, run, then drop it and drag the role back below
Moderator. The bot keeps MANAGE_ROLES so it can still apply/remove Muted afterward.

Usage: python3 scripts/apply_muted_overwrites.py
"""
import os, json, subprocess

ENV = os.path.expanduser("~/.hermes/profiles/gamehub-mod/.env")
MUTED_ROLE_ID = "<id>"
STAFF = {"<id>", "<id>"}  # mod-ops, audit-review

BITS = {
    "VIEW_CHANNEL": 10, "SEND_MESSAGES": 11, "EMBED_LINKS": 14, "ATTACH_FILES": 15,
    "READ_MESSAGE_HISTORY": 16, "ADD_REACTIONS": 6, "SEND_MESSAGES_IN_THREADS": 38,
    "CONNECT": 20, "SPEAK": 21, "MENTION_EVERYONE": 17, "MANAGE_MESSAGES": 13,
    "MANAGE_CHANNELS": 4, "MANAGE_ROLES": 28,
}


def api(method, path, body=None):
    cmd = ["curl", "-s", "-m", "25", "-X", method,
           "-H", f"Authorization: Bot {TOKEN}",
           "-H", "Accept: application/json",
           "-H", "Content-Type: application/json"]
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    cmd.append("https://discord.com/api/v10" + path)
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(r.stdout) if r.stdout.strip() else {"status": "ok(204)"}


vals = {}
for line in open(ENV, encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, _, v = line.partition("=")
    vals[k.strip()] = v.strip().strip('"').strip("'")

TOKEN = vals["DISCORD_BOT_TOKEN"]
G = vals["DISCORD_GUILD_ID"]

me = api("GET", "/users/@me")
bot_id = me["id"]
guild = api("GET", f"/guilds/{G}")
bot_member = api("GET", f"/guilds/{G}/members/{bot_id}")
bot_role_ids = bot_member.get("roles", [])
roles = {r["id"]: r for r in guild["roles"]}
bot_perms = 0
for rid in bot_role_ids:
    bot_perms |= int(roles[rid]["permissions"])
bot_top = max((roles[rid]["position"] for rid in bot_role_ids), default=0)
guild_top = max((r["position"] for r in guild["roles"]), default=0)

if not (bot_perms & (1 << BITS["MANAGE_CHANNELS"])):
    raise SystemExit("ABORT: bot lacks MANAGE_CHANNELS -- temp-promote its role (add the flag), then retry.")
if bot_top != guild_top:
    raise SystemExit("ABORT: bot role not at guild TOP -- drag Gamehub-mod above senior-mod, then retry.")

# SAFE deny set: only perms the bot holds. (No CONNECT/SPEAK -> would 50013 on new overwrite.)
DENY_NAMES = ["SEND_MESSAGES", "SEND_MESSAGES_IN_THREADS", "ADD_REACTIONS"]
deny = sum(1 << BITS[n] for n in DENY_NAMES)
print(f"Muted DENY bits = {deny} ({DENY_NAMES})  [excludes MENTION_EVERYONE + CONNECT + SPEAK]")

chs = api("GET", f"/guilds/{G}/channels")
member_ch = [c for c in chs if c["type"] in (0, 5) and c["id"] not in STAFF]
print(f"Applying Muted deny to {len(member_ch)} member text/announcement channels:")
failed = []
for c in member_ch:
    res = api("PUT", f"/channels/{c['id']}/permissions/{MUTED_ROLE_ID}",
              {"type": 0, "allow": "0", "deny": str(deny)})
    ok = res.get("status") == "ok(204)"
    print(f"  {'OK ' if ok else 'BAD'} {c.get('name'):<22} -> {res}")
    if not ok:
        failed.append(c.get("name"))

print("\nFailed:", failed or "NONE")
print("DONE. Revert MANAGE_CHANNELS + role position, then run scripts/inspect_muted.py to confirm 0 gaps.")
