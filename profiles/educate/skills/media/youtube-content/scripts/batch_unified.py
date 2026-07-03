#!/usr/bin/env python3
"""Unified YouTube content fetcher.
Tries raw transcript first, falls back to page-scraped summary.
Reads URL files (video_id|title), saves as markdown with checkpoint/resume."""

from __future__ import annotations
import argparse, json, os, re, subprocess, sys, time, html
from pathlib import Path
from typing import Optional

TRANSCRIPT_DIR = Path("/Users/noctis/Documents/YouTube-Transcripts")
CHECKPOINT_FILE = ".checkpoint.json"

def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:\"<>|]', "", name).replace(" ", "_").strip("._")
    return name[:120] if len(name) > 120 else name

def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    h, m = divmod(total, 3600)
    m, s = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"

def load_checkpoint(outdir: Path) -> dict:
    cp = outdir / CHECKPOINT_FILE
    if cp.exists():
        try:
            data = json.loads(cp.read_text())
            done = data.get("done", {})
            if isinstance(done, list):
                done = {vid: "transcript" for vid in done}
                data["done"] = done
            return data
        except:
            return {"done": {}, "failed": []}
    return {"done": {}, "failed": []}

def save_checkpoint(outdir: Path, cp: dict):
    (outdir / CHECKPOINT_FILE).write_text(json.dumps(cp, indent=2))

def fetch_transcript(video_id: str) -> Optional[list[dict]]:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        return [{"start": s.start, "text": s.text} for s in transcript.snippets]
    except Exception:
        return None

def fetch_summary_via_curl(video_id: str) -> Optional[str]:
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        r = subprocess.run(['curl', '-s', '-L', '--max-time', '30',
            '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            url], capture_output=True, text=True, timeout=45)
        if not r.stdout:
            return None
        title_match = re.search(r'"title":"(.*?)"', r.stdout)
        title = html.unescape(title_match.group(1)) if title_match else "Unknown"
        desc_match = re.search(r'"shortDescription":"(.*?)"', r.stdout, re.DOTALL)
        desc = html.unescape(desc_match.group(1)) if desc_match else ""
        chapters = []
        for m in re.finditer(r'(\d+:\d+(?::\d+)?)\s*[-–—]\s*(.+)', desc):
            chapters.append(f"- **{m.group(1)}** — {m.group(2).strip()}")
        channel_match = re.search(r'"ownerChannelName":"(.*?)"', r.stdout)
        channel = html.unescape(channel_match.group(1)) if channel_match else "Unknown"
        dur_match = re.search(r'"lengthSeconds":"(\d+)"', r.stdout)
        if dur_match:
            secs = int(dur_match.group(1))
            mins, secs = divmod(secs, 60)
            duration = f"{mins}:{secs:02d}"
        else:
            duration = "Unknown"
        summary = f"""---
title: "{title}"
source: "https://www.youtube.com/watch?v={video_id}"
video_id: "{video_id}"
type: "youtube-summary"
channel: "{channel}"
duration: "{duration}"
tags: [youtube, tutorial, summary]
---

# {title}

**URL:** https://www.youtube.com/watch?v={video_id}
**Channel:** {channel}
**Duration:** {duration}

## Description

{desc[:3000] if desc else '(No description available)'}

"""
        if chapters:
            summary += f"""## Chapters

{chr(10).join(chapters)}
"""
        return summary
    except Exception as e:
        print(f"  Summary error: {e}", file=sys.stderr)
        return None

def build_transcript_markdown(title: str, video_id: str, segments: list[dict]) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}"
    lines = [f"- [**{format_timestamp(s['start'])}**] {s['text']}" for s in segments]
    return f"""---
title: "{title}"
source: "{url}"
video_id: "{video_id}"
type: "youtube-transcript"
tags: [youtube, tutorial, transcript]
---

# {title}

**URL:** {url}
**Segments:** {len(segments)}

## Transcript

{chr(10).join(lines)}
"""

def load_urls(url_file: Path) -> list[dict]:
    videos = []
    for line in url_file.read_text().strip().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split('|', 1)
        if len(parts) == 2:
            videos.append({"id": parts[0].strip(), "title": parts[1].strip()})
        else:
            vid = line.split("v=")[-1].split("&")[0] if "v=" in line else line
            videos.append({"id": vid, "title": vid})
    return videos

def process_playlist(url_file: Path, outdir: Path, delay: float = 15.0,
                     start: int = 0, limit: int = 0, summary_delay: float = 5.0):
    all_videos = load_urls(url_file)
    outdir.mkdir(parents=True, exist_ok=True)
    cp = load_checkpoint(outdir)
    done_map = cp.get("done", {})
    videos = all_videos[start:]
    if limit > 0:
        videos = videos[:limit]
    remaining = [v for v in videos if v['id'] not in done_map]
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Playlist: {outdir.name}", file=sys.stderr)
    print(f"Total: {len(all_videos)}, Processing: {len(videos)}, Remaining: {len(remaining)}", file=sys.stderr)
    print(f"Output: {outdir}", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)

    ok_transcript = ok_summary = skipped = failed = 0
    for i, v in enumerate(videos, 1):
        if v["id"] in done_map:
            skipped += 1
            continue
        fname = sanitize_filename(v["title"])
        fpath = outdir / f"{fname}.md"
        if fpath.exists() and fpath.stat().st_size > 5000:
            done_map[v["id"]] = "transcript"
            skipped += 1
            continue
        print(f"[{i}/{len(videos)}] {v['title'][:60]}… ", end="", file=sys.stderr, flush=True)
        segments = fetch_transcript(v["id"])
        if segments:
            fpath.write_text(build_transcript_markdown(v["title"], v["id"], segments), encoding="utf-8")
            size_kb = fpath.stat().st_size / 1024
            print(f"📝 transcript {len(segments)} seg, {size_kb:.0f}KB", file=sys.stderr)
            done_map[v["id"]] = "transcript"
            ok_transcript += 1
            time.sleep(delay)
        else:
            summary = fetch_summary_via_curl(v["id"])
            if summary:
                fpath.write_text(summary, encoding="utf-8")
                size_kb = fpath.stat().st_size / 1024
                print(f"📋 summary {size_kb:.1f}KB", file=sys.stderr)
                done_map[v["id"]] = "summary"
                ok_summary += 1
                time.sleep(summary_delay)
            else:
                print("❌ both failed", file=sys.stderr)
                cp.setdefault("failed", []).append(v["id"])
                failed += 1
                time.sleep(2)
        cp["done"] = done_map
        if (ok_transcript + ok_summary) % 5 == 0:
            save_checkpoint(outdir, cp)

    cp["done"] = done_map
    save_checkpoint(outdir, cp)
    print(f"\n{outdir.name}: 📝 {ok_transcript} transcripts  📋 {ok_summary} summaries  ⏭️ {skipped} skipped  ❌ {failed} failed", file=sys.stderr)
    return ok_transcript, ok_summary, skipped, failed

def main():
    parser = argparse.ArgumentParser(description="Unified YouTube transcript/summary fetcher")
    parser.add_argument("url_file", nargs="?", help="Path to URL file")
    parser.add_argument("--all", action="store_true", help="Process all /tmp/*_urls.txt files")
    parser.add_argument("--outdir", "-o", type=Path, default=TRANSCRIPT_DIR)
    parser.add_argument("--delay", "-d", type=float, default=15.0, help="Seconds between transcript fetches")
    parser.add_argument("--summary-delay", type=float, default=5.0, help="Seconds between summary fetches")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--name", help="Override output directory name")
    args = parser.parse_args()

    if args.all:
        url_files = sorted(Path("/tmp").glob("*_urls.txt"))
        total_t = total_s = total_skip = total_fail = 0
        for uf in url_files:
            playlist_name = uf.stem.replace("_urls", "")
            outdir = args.outdir / playlist_name
            t, s, skip, fail = process_playlist(uf, outdir, args.delay,
                                                 summary_delay=args.summary_delay)
            total_t += t; total_s += s; total_skip += skip; total_fail += fail
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"ALL PLAYLISTS: 📝 {total_t} transcripts  📋 {total_s} summaries  ⏭️ {total_skip} skipped  ❌ {total_fail} failed", file=sys.stderr)
    elif args.url_file:
        uf = Path(args.url_file)
        outdir = args.outdir / (args.name or uf.stem.replace("_urls", ""))
        process_playlist(uf, outdir, args.delay, args.start, args.limit, args.summary_delay)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
