#!/usr/bin/env python3
"""
Fetch transcripts for all videos in a YouTube playlist.

Usage:
    python3 fetch_playlist.py PLAYLIST_URL [OUTPUT_PATH] [DELAY_SECONDS]

Defaults: OUTPUT_PATH=~/playlist-transcripts.md, DELAY=5

Features:
    - Retry with exponential backoff on rate limits (429 / IpBlocked)
    - Checkpoint/resume: progress survives process kill
    - yt-dlp fallback when youtube-transcript-api is blocked
    - Incremental markdown output after each video

Requires: pip3 install pytubefix youtube-transcript-api
Optional:  yt-dlp (pip3 install yt-dlp, or brew install yt-dlp)
"""

import json, subprocess, sys, os, re, html, time, glob, tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FETCH_SCRIPT = os.path.join(SCRIPT_DIR, "fetch_transcript.py")
CHECKPOINT_SUFFIX = ".checkpoint.json"

MAX_RETRIES = 5
BASE_DELAY = 5       # seconds between videos on success
BACKOFF_MULT = 2     # multiplier per retry on rate limit
MAX_BACKOFF = 300    # cap at 5 minutes


def get_playlist_videos(playlist_url):
    """Get ordered list of video URLs from a playlist using yt-dlp (more reliable than pytubefix)."""
    try:
        cmd = [sys.executable, "-m", "yt_dlp", "--flat-playlist", "--dump-json",
               "--no-warnings", "--quiet", playlist_url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        videos = []
        title = "YouTube Playlist"
        for i, line in enumerate(r.stdout.strip().split("\n"), 1):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                vid = data.get("id", "")
                vtitle = data.get("title", "Unknown")
                if i == 1:
                    title = data.get("playlist_title", data.get("channel", title))
                videos.append({"index": i, "url": f"https://www.youtube.com/watch?v={vid}",
                               "video_id": vid, "title": vtitle})
            except json.JSONDecodeError:
                continue
        return title, videos
    except Exception:
        # Fallback to pytubefix
        from pytubefix import Playlist
        playlist = Playlist(playlist_url)
        videos = []
        for i, url in enumerate(playlist.video_urls, 1):
            vid = url.split("v=")[-1].split("&")[0]
            videos.append({"index": i, "url": url, "video_id": vid, "title": vid})
        return playlist.title or "YouTube Playlist", videos


def fetch_transcript_primary(video_url):
    """Fetch transcript using youtube-transcript-api via helper script."""
    try:
        r = subprocess.run(
            ["python3", FETCH_SCRIPT, video_url, "--text-only", "--timestamps"],
            capture_output=True, text=True, timeout=60
        )
        output = r.stdout.strip()
        if "IpBlocked" in output or "blocking" in output.lower():
            return ("RATE_LIMITED", "")
        if "Error:" in output or len(output) < 50:
            return ("FAILED", output[:200])
        return ("OK", output)
    except subprocess.TimeoutExpired:
        return ("TIMEOUT", "")
    except Exception as e:
        return ("ERROR", str(e))


def fetch_transcript_ytdlp(video_id):
    """Fallback: fetch transcript via yt-dlp with android client (bypasses PO token)."""
    tmpdir = tempfile.mkdtemp(prefix="yt_subs_")
    out_template = os.path.join(tmpdir, "%(id)s")
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--extractor-args", "youtube:player_client=android",
        "--skip-download", "--write-auto-sub", "--sub-lang", "en",
        "--sub-format", "vtt", "--no-warnings", "--quiet",
        "-o", out_template, f"https://www.youtube.com/watch?v={video_id}"
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if "429" in r.stderr or "429" in r.stdout:
            return ("RATE_LIMITED", "")
        # Find .vtt file
        for vtt_path in glob.glob(os.path.join(tmpdir, "*.vtt")):
            with open(vtt_path) as f:
                text = _parse_vtt(f.read())
            os.remove(vtt_path)
            if len(text) > 50:
                return ("OK", text)
        return ("NO_SUB", r.stderr[:200] if r.stderr else "No subtitle file")
    except subprocess.TimeoutExpired:
        return ("TIMEOUT", "")
    except Exception as e:
        return ("ERROR", str(e))
    finally:
        for f in glob.glob(os.path.join(tmpdir, "*")):
            os.remove(f)
        os.rmdir(tmpdir)


def _parse_vtt(vtt_text):
    """Parse VTT subtitle into clean text."""
    lines, seen = [], set()
    for raw in vtt_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("WEBVTT") or line.startswith("Kind:") \
           or line.startswith("Language:") or line.startswith("NOTE") \
           or "-->" in line or re.match(r"^\d+$", line):
            continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        if line and line not in seen:
            seen.add(line)
            lines.append(line)
    return " ".join(lines)


def load_checkpoint(output_path):
    cp_path = output_path + CHECKPOINT_SUFFIX
    if os.path.exists(cp_path):
        with open(cp_path) as f:
            return json.load(f)
    return {"done": {}, "results": []}


def save_checkpoint(output_path, checkpoint):
    cp_path = output_path + CHECKPOINT_SUFFIX
    with open(cp_path, "w") as f:
        json.dump(checkpoint, f)


def write_markdown(output_path, playlist_title, videos, results, ok_count):
    """Write organized markdown with summary table and full transcripts."""
    with open(output_path, "w") as f:
        f.write(f"# {playlist_title} — Playlist Transcripts\n\n")
        f.write(f"**Total Videos:** {len(videos)}  \n")
        f.write(f"**Transcripts Fetched:** {ok_count}/{len(videos)}\n\n")
        f.write("---\n\n")

        f.write("## Summary\n\n")
        f.write("| # | Title | Status |\n")
        f.write("|---|-------|--------|\n")
        for r in results:
            emoji = "✅" if r["status"] == "OK" else "❌"
            title = r.get("title", r["video_id"])
            f.write(f"| {r['index']} | {title} | {emoji} {r['status']} |\n")
        f.write(f"\n**{ok_count}/{len(results)} transcripts successfully fetched.**\n\n")
        f.write("---\n\n")

        for r in results:
            title = r.get("title", r["video_id"])
            f.write(f"## Video {r['index']}: {title}\n\n")
            f.write(f"**URL:** {r['url']}  \n")
            f.write(f"**Status:** {r['status']}\n\n")
            if r["status"] == "OK":
                f.write(r["transcript"])
                f.write("\n\n")
            else:
                f.write(f"> Transcript not available. ({r['status']})\n\n")
            f.write("---\n\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_playlist.py PLAYLIST_URL [OUTPUT_PATH] [DELAY_SECONDS]")
        sys.exit(1)

    playlist_url = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/playlist-transcripts.md")
    base_delay = float(sys.argv[3]) if len(sys.argv) > 3 else BASE_DELAY

    # Load checkpoint for resume
    checkpoint = load_checkpoint(output_path)
    done_map = checkpoint.get("done", {})
    results = checkpoint.get("results", [])

    print(f"Fetching playlist info...", flush=True)
    title, videos = get_playlist_videos(playlist_url)
    print(f"Playlist: {title} ({len(videos)} videos)", flush=True)

    ok = sum(1 for r in results if r.get("status") == "OK")
    delay = base_delay
    use_ytdlp_fallback = False  # switch to True if primary is rate-limited

    for v in videos:
        idx = v["index"]
        vid = v["video_id"]

        # Skip already-done videos
        if vid in done_map and done_map[vid] in ("OK", "FAILED", "TOO_SHORT"):
            print(f"[{idx}/{len(videos)}] {vid} — already done ({done_map[vid]})", flush=True)
            continue

        print(f"[{idx}/{len(videos)}] {v.get('title', vid)[:50]}...", end=" ", flush=True)

        for attempt in range(MAX_RETRIES):
            if use_ytdlp_fallback:
                status, text = fetch_transcript_ytdlp(vid)
            else:
                status, text = fetch_transcript_primary(v["url"])

            if status == "OK":
                ok += 1
                entry = {"index": idx, "video_id": vid, "url": v["url"],
                         "title": v.get("title", vid), "status": "OK", "transcript": text}
                results.append(entry)
                done_map[vid] = "OK"
                checkpoint["done"] = done_map
                checkpoint["results"] = results
                save_checkpoint(output_path, checkpoint)
                write_markdown(output_path, title, videos, results, ok)
                print(f"✅ ({len(text)} chars)", flush=True)
                delay = max(base_delay, delay // 2)
                break
            elif status == "RATE_LIMITED":
                wait = min(delay * (BACKOFF_MULT ** attempt), MAX_BACKOFF)
                print(f"⏳ rate-limited, waiting {wait}s ({attempt+1}/{MAX_RETRIES})...", flush=True)
                if attempt == 0 and not use_ytdlp_fallback:
                    print("  → switching to yt-dlp fallback for remaining videos", flush=True)
                    use_ytdlp_fallback = True
                time.sleep(wait)
            else:
                entry = {"index": idx, "video_id": vid, "url": v["url"],
                         "title": v.get("title", vid), "status": status, "transcript": ""}
                results.append(entry)
                done_map[vid] = status
                checkpoint["done"] = done_map
                checkpoint["results"] = results
                save_checkpoint(output_path, checkpoint)
                write_markdown(output_path, title, videos, results, ok)
                print(f"❌ {status}", flush=True)
                break
        else:
            # All retries exhausted
            entry = {"index": idx, "video_id": vid, "url": v["url"],
                     "title": v.get("title", vid), "status": "RATE_LIMITED", "transcript": ""}
            results.append(entry)
            done_map[vid] = "RATE_LIMITED"
            checkpoint["done"] = done_map
            checkpoint["results"] = results
            save_checkpoint(output_path, checkpoint)
            print(f"❌ rate-limited after {MAX_RETRIES} retries", flush=True)
            delay = min(delay * 2, 120)

        if idx < len(videos):
            time.sleep(delay)

    write_markdown(output_path, title, videos, results, ok)
    # Clean up checkpoint on completion
    cp_path = output_path + CHECKPOINT_SUFFIX
    if os.path.exists(cp_path):
        os.remove(cp_path)

    print(f"\n{'='*60}", flush=True)
    print(f"Done! {ok}/{len(results)} transcripts → {output_path}", flush=True)


if __name__ == "__main__":
    main()
