#!/usr/bin/env python3
"""Verify an animated Herm eikon source folder is clean and state MP4s probe.

Usage:
  python verify_eikon_source.py ~/.hermes/eikons/<name>/source

Checks:
- active source has base.png or base.mp4
- six state MP4s exist: idle/listening/thinking/speaking/working/error
- same-name state PNGs are absent, because they can shadow videos in Studio
- ffprobe can read each MP4 and reports duration/fps/size
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

STATES = ["idle", "listening", "thinking", "speaking", "working", "error"]


def probe(path: Path) -> dict:
    p = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=index,codec_type,codec_name,width,height,r_frame_rate,nb_frames,duration",
            "-show_entries",
            "format=duration,size,format_name",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if p.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}: {p.stderr.strip()}")
    return json.loads(p.stdout)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: verify_eikon_source.py ~/.hermes/eikons/<name>/source", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).expanduser().resolve()
    errors: list[str] = []
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 1

    if not ((root / "base.png").exists() or (root / "base.mp4").exists()):
        errors.append("missing base.png or base.mp4")

    for state in STATES:
        mp4 = root / f"{state}.mp4"
        png = root / f"{state}.png"
        if png.exists():
            errors.append(f"state PNG may shadow video in Studio: {png.name}")
        if not mp4.exists():
            errors.append(f"missing state MP4: {mp4.name}")
            continue
        try:
            data = probe(mp4)
            stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
            fmt = data.get("format", {})
            print(
                f"{state}: {stream.get('width')}x{stream.get('height')} "
                f"fps={stream.get('r_frame_rate')} duration={fmt.get('duration')} size={fmt.get('size')}"
            )
        except Exception as exc:  # noqa: BLE001 - CLI verifier should report every failure cleanly
            errors.append(str(exc))

    if errors:
        print("\nFAIL:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    print("\nOK: clean animated eikon source folder")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
