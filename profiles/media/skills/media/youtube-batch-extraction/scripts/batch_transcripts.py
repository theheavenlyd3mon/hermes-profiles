#!/usr/bin/env python3
"""Batch YouTube playlist → .md transcripts with checkpoint/resume and rate limiting."""

from __future__ import annotations

import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

def sanitize_filename(name: str) -> str:
    if not name:
        return "Untitled"
    name = re.sub(r'[\\/*?:"<>|]', "", name).replace(" ", "_").strip("._")
    return name[:120] if len(name) > 120 else name

def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    h, m = divmod(total, 3600)
    m, s = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"

def get_playlist_entries(ytdlp: str, playlist_url: str) -> list[dict]:
    cmd = [ytdlp, "--flat-playlist", "--dump-single-json", "--no-warnings", playlist_url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"yt-dlp failed: {r.stderr}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(r.stdout)
    return [{"id": e.get("id") or e.get("url","").split("v=")[-1].split("&")[0],
             "title": e.get("title") or "Untitled",
             "url": e.get("url") or f"https://youtube.com/watch?v={e.get('id')}"}
            for e in data.get("entries", [])]

def fetch_transcript(ytdlp: str, video_id: str):
    """Try youtube-transcript-api first, then yt-dlp as fallback."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        return [{"text": s.text, "start": s.start, "duration": s.duration}
                for s in api.fetch(video_id)]
    except Exception:
        pass

    # yt-dlp fallback (android client often gets auto-captions)
    try:
        cmd = [ytdlp, "--skip-download", "--write-auto-subs", "--sub-lang", "en",
               "--sub-format", "vtt", "--extractor-args", "youtube:player_client=android",
               "-o", f"/tmp/yt_sub_{video_id}", f"https://youtube.com/watch?v={video_id}"]
        subprocess.run(cmd, capture_output=True, timeout=30)
        vtt_path = f"/tmp/yt_sub_{video_id}.en.vtt"
        if os.path.exists(vtt_path):
            segments = []
            for line in open(vtt_path):
                m = re.match(r"(\d+):(\d+):(\d+)\.(\d+)\s+-->", line)
                if m:
                    h, mi, s, ms = int(m[1]), int(m[2]), int(m[3]), int(m[4])
                    segments.append({"start": h*3600+mi*60+s+ms/1000, "text": "", "duration": 0})
                elif segments and line.strip() and not line.startswith("WEBVTT"):
                    segments[-1]["text"] += line.strip() + " "
            os.unlink(vtt_path)
            if segments:
                return segments
    except Exception:
        pass
    return None

def build_markdown(video: dict, segments: list[dict]) -> str:
    total = segments[-1]["start"] + segments[-1]["duration"] if segments else 0
    lines = [f"- [**{format_timestamp(s['start'])}**] {s['text']}" for s in segments]
    safe_title = video['title'].replace('"', "'")
    return f"""---
title: "{safe_title}"
source: "{video['url']}"
video_id: "{video['id']}"
duration: "{format_timestamp(total)}"
type: "youtube-transcript"
tags: [youtube, tutorial, transcript]
---

# {video['title']}

**URL:** {video['url']}
**Duration:** {format_timestamp(total)}
**Segments:** {len(segments)}

## Transcript

{chr(10).join(lines)}
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--outdir", "-o", default=os.path.expanduser("~/Documents/YouTube-Transcripts"))
    parser.add_argument("--delay", "-d", type=float, default=8)
    parser.add_argument("--skip-existing", action="store_true", default=True)
    args = parser.parse_args()

    ytdlp = os.path.expanduser("~/.hermes/hermes-agent/venv/bin/yt-dlp")

    print("Fetching playlist metadata…", file=sys.stderr)
    videos = get_playlist_entries(ytdlp, args.url)
    print(f"Found {len(videos)} videos.", file=sys.stderr)

    # Get playlist title
    playlist_title = "YouTube-Playlist"
    try:
        cmd = [ytdlp, "--flat-playlist", "--dump-single-json", "--no-warnings", args.url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            t = json.loads(r.stdout).get("title", "")
            if t:
                playlist_title = t
    except Exception:
        pass

    outdir = Path(args.outdir) / sanitize_filename(playlist_title)
    outdir.mkdir(parents=True, exist_ok=True)
    print(f"Output: {outdir}", file=sys.stderr)

    ok = skipped = failed = 0
    for i, v in enumerate(videos, 1):
        fname = outdir / f"{sanitize_filename(v['title'])}.md"

        # Skip if exists
        if args.skip_existing and fname.exists():
            print(f"[{i}/{len(videos)}] ⏩ already exists", file=sys.stderr)
            skipped += 1
            continue

        print(f"[{i}/{len(videos)}] {v['title'][:80]}… ", end="", file=sys.stderr, flush=True)
        seg = fetch_transcript(ytdlp, v["id"])
        if not seg:
            print("⏭️  no transcript", file=sys.stderr)
            failed += 1
            continue

        fname.write_text(build_markdown(v, seg), encoding="utf-8")
        print(f"✅  {len(seg)} segments", file=sys.stderr)
        ok += 1
        if i < len(videos):
            time.sleep(args.delay)

    print(f"\nDone. ✅ {ok}  ⏭️ {skipped}  ❌ {failed}  (of {len(videos)})", file=sys.stderr)

if __name__ == "__main__":
    main()
