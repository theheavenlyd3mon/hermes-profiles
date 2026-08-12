#!/usr/bin/env python3
"""Print the bot's highest role position vs the guild top (50013 hierarchy pre-check).

Discord returns HTTP 50013 on `PUT .../permissions/{Muted}` unless the bot's highest role
is at the TOP of the role list. Run this BEFORE apply_muted_overwrites.py: if
`bot_top != guild_top`, the write will fail and you must temp-promote the bot role first.

Reads DISCORD_BOT_TOKEN / DISCORD_GUILD_ID from the profile .env. Uses curl (urllib is
Cloudflare-1010'd). Prints all roles by position so you can see exactly where the bot sits.

Usage: python3 scripts/check_bot_pos.py
"""
import os
import json
import subprocess

ENV = os.path.expanduser("~/.hermes/profiles/gamehub-mod/.env")

def api(method, path):
    cmd = ["curl", "-s", "-m", "20", "-X", method,
           "-H", f"Authorization: Bot {TOKEN}",
           "-H", "Accept: application/json",
           f"https://discord.com/api/v10{path}"]
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

me = api("GET", "/users/@me")
bot_id = me["id"]
guild = api("GET", f"/guilds/{G}")
roles = {r["id"]: r for r in guild["roles"]}
bm = api("GET", f"/guilds/{G}/members/{bot_id}")
bot_role_ids = bm.get("roles", [])
print("Bot roles (name @ pos):")
for r in bot_role_ids:
    print(f"   {roles[r]['name']} @ {roles[r]['position']}")
bot_top = max(roles[r]["position"] for r in bot_role_ids)
guild_top = max(r["position"] for r in guild["roles"])
print(f"\nBot highest role position: {bot_top}")
print(f"Guild top position:        {guild_top}")
print("RESULT:", "OK — bot at top, writes allowed" if bot_top == guild_top
      else "BLOCKED — temp-promote bot role to top, then retry")
print("\nAll roles high->low:")
for r in sorted(guild["roles"], key=lambda x: x["position"], reverse=True):
    tag = " <<BOT" if r["id"] in bot_role_ids else ""
    print(f"   pos={r['position']:<3} {r['name']}{tag}")
