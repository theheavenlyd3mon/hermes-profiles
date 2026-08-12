#!/usr/bin/env python3
"""Verify which channels have a working `Muted` DENY overwrite (own OR inherited from category).

CORRECTED: reads the REAL token from the profile .env (the previous version hardcoded
`Authorization: Bot ***` and silently never ran). Computes EFFECTIVE silence = the channel's
own Muted overwrite deny OR a deny inherited from its parent category, since a category deny
cascades to children that have no own overwrite. This catches the common case where
#general / #announcements show "no overwrite" but are actually silenced via the parent.

Usage: python3 scripts/inspect_muted.py
"""
import os, json, subprocess

ENV = os.path.expanduser("~/.hermes/profiles/gamehub-mod/.env")
MUTED_ROLE_ID = "<id>"
STAFF = {"<id>", "<id>"}  # mod-ops, audit-review

BITS = {
    "VIEW_CHANNEL": 10, "SEND_MESSAGES": 11, "EMBED_LINKS": 14, "ATTACH_FILES": 15,
    "READ_MESSAGE_HISTORY": 16, "ADD_REACTIONS": 6, "SEND_MESSAGES_IN_THREADS": 38,
    "CONNECT": 20, "SPEAK": 21,
}


def api(method, path):
    cmd = ["curl", "-s", "-m", "25", "-X", method,
           "-H", f"Authorization: Bot {TOKEN}",
           "-H", "Accept: application/json"]
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(r.stdout) if r.stdout.strip() else {}


vals = {}
for line in open(ENV, encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, _, v = line.partition("=")
    vals[k.strip()] = v.strip().strip('"').strip("'")
TOKEN = vals["DISCORD_BOT_TOKEN"]
G = vals["DISCORD_GUILD_ID"]

cats = api("GET", f"/guilds/{G}/channels")
cat_by_id = {c["id"]: c for c in cats if c["type"] == 4}


def effective_deny(channel):
    own = [o for o in channel.get("permission_overwrites", []) if o["id"] == MUTED_ROLE_ID]
    if own:
        return int(own[0]["deny"]), "own"
    pid = channel.get("parent_id")
    if pid and pid in cat_by_id:
        pov = [o for o in cat_by_id[pid].get("permission_overwrites", []) if o["id"] == MUTED_ROLE_ID]
        if pov:
            return int(pov[0]["deny"]), f"inherit:{cat_by_id[pid].get('name')}"
    return 0, "NONE"


text = [c for c in cats if c["type"] in (0, 5)]
print(f"Checking {len(text)} text/announcement channels for EFFECTIVE Muted silence:\n")
needs_fix = []
for c in text:
    d, src = effective_deny(c)
    silenced = bool(d & (1 << BITS["SEND_MESSAGES"])) and bool(d & (1 << BITS["ADD_REACTIONS"]))
    name = c.get("name")
    print(f"  [{'OK ' if silenced else 'BAD'}] {name:<22} deny_bits={d} ({src})")
    if not silenced:
        needs_fix.append(name)
needs_fix = [n for n in needs_fix if n not in STAFF]
print(f"\nMember channels NOT silenced: {needs_fix or 'NONE ✅'}")
