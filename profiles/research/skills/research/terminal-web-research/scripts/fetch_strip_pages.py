#!/usr/bin/env python3
"""Bulk-fetch web pages with curl (parallel), then strip HTML to text.

Reads a slug->URL mapping (inline dict or JSON file passed as argv[1]),
fetches each page with retries, saves pages/<slug>.html and pages/<slug>.txt.
Treats files < MIN_SIZE bytes as failed fetches (challenge/404/JS shells are
typically 5-15KB; real article pages are usually 100KB-1.8MB).

Usage:
    python3 fetch_strip_pages.py [mapping.json]
        mapping.json: {"slug": "https://...", ...}  (optional; edit EPISODES below instead)
"""
import subprocess, os, re, html, sys, json, concurrent.futures

PAGES = "pages"
MIN_SIZE = 20000  # bytes; below this = suspected block/error shell
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# slug -> URL. Override with a JSON file: {"slug": "https://..."}
EPISODES = {
    "example": "https://example.com/",
}

def fetch_one(item):
    slug, url = item
    os.makedirs(PAGES, exist_ok=True)
    out = os.path.join(PAGES, slug + ".html")
    if os.path.exists(out) and os.path.getsize(out) > MIN_SIZE:
        return slug, "cached", os.path.getsize(out)
    for _ in range(3):
        subprocess.run(["curl", "-sSL", "--max-time", "40", "-A", UA, url, "-o", out],
                       capture_output=True, text=True)
        if os.path.exists(out) and os.path.getsize(out) > MIN_SIZE:
            return slug, "ok", os.path.getsize(out)
    return slug, "FAIL", (os.path.getsize(out) if os.path.exists(out) else 0)

def strip_file(slug):
    p = os.path.join(PAGES, slug + ".html")
    if not os.path.exists(p):
        return
    raw = open(p, encoding="utf-8", errors="ignore").read()
    txt = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(re.sub(r"\s+", " ", txt))
    open(os.path.join(PAGES, slug + ".txt"), "w").write(txt)

if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        EPISODES.update(json.load(open(sys.argv[1])))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for slug, status, size in ex.map(fetch_one, EPISODES.items()):
            print(f"{status:8s} {size:9d} {slug}")
    for slug in EPISODES:
        strip_file(slug)
    print("STRIP DONE")
