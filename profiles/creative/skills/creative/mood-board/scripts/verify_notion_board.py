#!/usr/bin/env python3
"""Verify a Notion mood-board page: title/icon/cover, block tree, image count.

Usage: NOTION_API_KEY=ntn_... python3 verify_notion_board.py <page_id>
Falls back to reading the key from the creative profile dotenv.
"""
import json, os, sys, urllib.request

PAGE_ID = sys.argv[1]
KEY = os.environ.get("NOTION_API_KEY") or next(
    l.split("=", 1)[1].strip()
    for l in open(os.path.expanduser("/Users/noctis/.hermes/profiles/creative/.env"))
    if l.startswith("NOTION_API_KEY="))
HDRS = {"Authorization": f"Bearer {KEY}", "Notion-Version": "2025-09-03"}


def get(path):
    req = urllib.request.Request(f"https://api.notion.com/v1/{path}", headers=HDRS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


page = get(f"pages/{PAGE_ID}")
title = "".join(t["plain_text"] for t in page["properties"]["title"]["title"])
print("TITLE:", title)
print("ICON:", page.get("icon"), "| COVER:", (page.get("cover") or {}).get("type"))

images = 0
for b in get(f"blocks/{PAGE_ID}/children?page_size=100")["results"]:
    t = b["type"]
    if t == "column_list":
        for col in get(f"blocks/{b['id']}/children")["results"]:
            items = get(f"blocks/{col['id']}/children")["results"]
            types = [i["type"] for i in items]
            images += types.count("image")
            print(f"  column -> {types}")
    else:
        rt = b.get(t, {}).get("rich_text", [])
        txt = "".join(x["plain_text"] for x in rt)[:70] if rt else ""
        print(f"{t:22} {txt}")
print("TOTAL IMAGES EMBEDDED:", images)
