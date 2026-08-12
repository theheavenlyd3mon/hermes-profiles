#!/usr/bin/env python3
"""X landscape sweep: summarize recent posts across N queries with minimal context cost.

Edit QUERIES for the niche, then run:
    python3 x_landscape_sweep.py [results_per_query]   # default 12

Read-only: only calls `xurl search`. Never posts, replies, or likes.
Requires xurl CLI with OAuth configured (`xurl auth status` must show a token).
"""
import json
import subprocess
import sys

# (label, xurl search query) — edit per niche. Use OR groups and -is:retweet to reduce noise.
QUERIES = [
    ("hermes_agent", '"Hermes agent" OR NousResearch OR "Nous Hermes"'),
    ("local_llm", '"local LLM" OR "local models" OR ollama OR llama.cpp'),
    ("model_release", 'Qwen3.8 OR "Kimi K3" OR "MiniMax H3"'),
    ("open_weights", '"open source AI" OR "open weights" OR "open-weight"'),
    ("community", '"build in public" OR "buildinpublic" -is:retweet'),
]


def run(q, n):
    try:
        out = subprocess.run(
            ["xurl", "search", q, "-n", str(n)],
            capture_output=True, text=True, timeout=60,
        ).stdout
        return json.loads(out)
    except Exception as e:
        return {"error": str(e)}


def fmt(post):
    t = (post.get("text") or "").replace("\n", " ")[:220]
    m = post.get("public_metrics") or {}
    return f"♥{m.get('like_count', 0)} 🔁{m.get('retweet_count', 0)} | {t}"


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    for label, q in QUERIES:
        print(f"\n{'=' * 70}\n### {label}: {q}\n{'=' * 70}")
        data = run(q, n)
        if "error" in data:
            print("  ERROR:", data["error"])
            continue
        posts = data.get("data") or data.get("posts") or (data if isinstance(data, list) else [])
        if not posts:
            print("  (no results)")
            continue
        for p in posts[:n]:
            print(fmt(p))


if __name__ == "__main__":
    main()
