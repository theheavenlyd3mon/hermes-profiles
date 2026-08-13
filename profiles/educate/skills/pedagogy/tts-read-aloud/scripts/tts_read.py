#!/usr/bin/env python3
"""Read a narration script aloud via edge-tts + local player.

Usage: python3 tts_read.py /tmp/narration.txt [--voice en-US-AriaNeural]

Splits the script into paragraph-sized chunks (~3500 chars each),
synthesizes each to MP3 with edge-tts, plays them in order,
and prints progress so the agent/user can track position.

The player command is the only OS-specific line: afplay (macOS),
falling back to mpv if present.
"""
import shutil
import subprocess
import sys
import os
import re

VOICE = "en-US-AriaNeural"
CHUNK_SIZE = 3500
OUT_DIR = "/tmp/tts_chunks"

def player_cmd():
    for exe in ("afplay", "mpv"):
        if shutil.which(exe):
            return [exe] if exe == "afplay" else [exe, "--really-quiet"]
    raise SystemExit("No audio player found (need afplay or mpv).")

def chunk_text(text: str) -> list:
    paras = re.split(r"\n\s*\n", text.strip())
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 2 > CHUNK_SIZE and cur:
            chunks.append(cur.strip())
            cur = p
        else:
            cur = (cur + "\n\n" + p).strip()
    if cur.strip():
        chunks.append(cur.strip())
    return chunks

def main():
    path = sys.argv[1]
    voice = VOICE
    if "--voice" in sys.argv:
        voice = sys.argv[sys.argv.index("--voice") + 1]
    text = open(path, encoding="utf-8").read()
    chunks = chunk_text(text)
    os.makedirs(OUT_DIR, exist_ok=True)
    play = player_cmd()
    total = len(chunks)
    est_min = sum(len(c.split()) for c in chunks) / 160  # ~160 wpm speaking rate
    print(f"Voice: {voice} | {total} chunks | ~{est_min:.0f} min listen", flush=True)
    for i, chunk in enumerate(chunks, 1):
        mp3 = f"{OUT_DIR}/part-{i:02d}.mp3"
        r = subprocess.run(
            ["edge-tts", "--voice", voice, "--text", chunk, "--write-media", mp3],
            capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            print(f"  [chunk {i}] TTS FAILED: {r.stderr[:200]}", flush=True)
            continue
        print(f"  > part {i}/{total} playing ({len(chunk)} chars)...", flush=True)
        subprocess.run(play + [mp3], check=True)
    print("DONE — finished reading.", flush=True)

if __name__ == "__main__":
    main()
