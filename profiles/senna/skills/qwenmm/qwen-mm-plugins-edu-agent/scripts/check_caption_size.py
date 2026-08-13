#!/usr/bin/env python3
r"""
check_caption_size.py — Pre-render gate: fail if any caption font-size is too large.

WHY: On a 1920x1080 canvas the caption belongs at ~36-40px. Models sometimes set a
much larger value (e.g. font-size:64px on a custom `.caption-text` class), which makes
the subtitle huge, wrap to two lines, and dominate the frame. The skill template uses
`.caption-bar { font-size:36px }`, but a model that invents its own caption class can
bypass that example — this check enforces the limit regardless of class name.

It scans index.html (and compositions/*.html) for:
  - CSS rules whose selector mentions "caption", reading their `font-size:NNpx`
  - inline `style="...font-size:NNpx..."` on elements whose class mentions "caption"
and fails if any caption font-size exceeds MAX_PX.

Usage:
    python3 check_caption_size.py [dist_dir] [max_px]   # defaults: ./dist 44
Exit 0 = clean, 1 = oversized caption found (or no HTML found).
"""

import re
import sys
from pathlib import Path

from _shared import iter_compositions, line_of

DEFAULT_MAX_PX = 44          # 1080p caption should be ~36-40px; 44 leaves headroom
RECOMMEND = "36-40px"

# CSS rule:  <selector> { <body> }  — capture selector + body
RE_RULE = re.compile(r"(?P<sel>[^{}]+)\{(?P<body>[^{}]*)\}", re.S)
RE_FONT_PX = re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", re.I)
# inline style on a caption element:  class="...caption..." ... style="...font-size:NNpx..."
RE_CAPTION_TAG = re.compile(
    r"""<[^>]*class\s*=\s*(['"])[^'"]*caption[^'"]*\1[^>]*style\s*=\s*(['"])(?P<style>[^'"]*)\2[^>]*>""",
    re.I | re.S,
)


def scan_file(path: Path, max_px: float):
    txt = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    # 1) CSS rules whose selector mentions "caption"
    for m in RE_RULE.finditer(txt):
        sel = m.group("sel")
        if "caption" not in sel.lower():
            continue
        for fm in RE_FONT_PX.finditer(m.group("body")):
            px = float(fm.group(1))
            if px > max_px:
                hits.append((line_of(txt, m.start()), f"{sel.strip()[:50]} {{ font-size:{fm.group(1)}px }}", px))
    # 2) inline style on caption elements
    for m in RE_CAPTION_TAG.finditer(txt):
        for fm in RE_FONT_PX.finditer(m.group("style")):
            px = float(fm.group(1))
            if px > max_px:
                hits.append((line_of(txt, m.start()), f"inline style font-size:{fm.group(1)}px", px))
    return hits


def main() -> int:
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    max_px = float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_MAX_PX
    if not dist.is_dir():
        print(f"ERROR: dist dir not found: {dist}", file=sys.stderr)
        return 1

    files = iter_compositions(dist)
    if not files:
        print(f"ERROR: no index.html / compositions/*.html under {dist}", file=sys.stderr)
        return 1

    total = 0
    for f in files:
        for line, what, px in scan_file(f, max_px):
            total += 1
            print(f"{f}:{line}: caption font-size {px:g}px exceeds {max_px:g}px — {what}")

    if total:
        print(f"\nFAIL: {total} caption font-size(s) over {max_px:g}px → subtitle too large / wraps and dominates the frame.")
        print(f"FIX: set caption font-size to {RECOMMEND} (the skill template uses 36px). Captions sit at the bottom on a 1920x1080 canvas.")
        return 1

    print(f"OK: all caption font-sizes <= {max_px:g}px across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
