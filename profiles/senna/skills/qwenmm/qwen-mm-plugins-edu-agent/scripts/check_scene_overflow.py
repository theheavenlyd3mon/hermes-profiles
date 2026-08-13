#!/usr/bin/env python3
r"""
check_scene_overflow.py — Pre-render gate: fail on gross OVERSIZE / overflow (排版过大).

WHY: The other layout checks guard against content being too SMALL (fill 70%, min sizes,
caption safe zone). The opposite failure — content sized BIGGER than the 1920x1080 frame —
gets clipped at the edges or pushes neighbours off-screen. This flags the unambiguous
static signals of oversize that legitimate content never hits:

  1. a CSS `width:  N px` with N > 1920  (wider than the frame)
  2. a CSS `height: N px` with N > 1080  (taller than the frame)
  3. a `transform: scale(N)` / scale3d/scaleX/scaleY with N > 3  (blows content off-frame)

These are intentionally loose thresholds (way-out-of-bounds only) to avoid false positives
on legitimate large-but-valid layouts. Font-size is deliberately NOT hard-failed here: big type
is design-dependent (hero titles, faint decorative watermarks at 200px+, large answer numbers are
all legitimate), so a px ceiling would false-positive. The soft proportion advice (hero text
<= ~96px, panels within the 1920x900 safe area, don't crowd the edges) lives in design-system.md
"Layout & Space Usage" and is not machine-enforced.

Note: only CSS px lengths are checked. SVG geometry attributes (`width="2000"` with no unit,
viewBox user units) are NOT flagged — they are internal coordinates scaled by the viewBox.

Usage:
    python3 check_scene_overflow.py [dist_dir]     # default ./dist
Exit 0 = clean, 1 = an oversize/overflow signal found (or no HTML found).
"""

import re
import sys
from pathlib import Path

from _shared import iter_compositions, line_of

FRAME_W = 1920
FRAME_H = 1080
MAX_SCALE = 3.0

# property lookbehind (?<![-\w]) so `max-width`/`line-height`/`min-height` do NOT match
RE_WIDTH = re.compile(r"(?<![-\w])width\s*:\s*(\d+(?:\.\d+)?)px", re.I)
RE_HEIGHT = re.compile(r"(?<![-\w])height\s*:\s*(\d+(?:\.\d+)?)px", re.I)
RE_SCALE = re.compile(r"scale(?:3d|X|Y)?\(\s*(\d+(?:\.\d+)?)", re.I)


def scan_file(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for m in RE_WIDTH.finditer(txt):
        if float(m.group(1)) > FRAME_W:
            hits.append((line_of(txt, m.start()), f"width:{m.group(1)}px > {FRAME_W}px frame width (content clipped at edge)"))
    for m in RE_HEIGHT.finditer(txt):
        if float(m.group(1)) > FRAME_H:
            hits.append((line_of(txt, m.start()), f"height:{m.group(1)}px > {FRAME_H}px frame height (content clipped)"))
    for m in RE_SCALE.finditer(txt):
        if float(m.group(1)) > MAX_SCALE:
            hits.append((line_of(txt, m.start()), f"transform scale({m.group(1)}) > {MAX_SCALE} (blows content off-frame)"))
    return hits


def main() -> int:
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    if not dist.is_dir():
        print(f"ERROR: dist dir not found: {dist}", file=sys.stderr)
        return 1

    files = iter_compositions(dist)
    if not files:
        print(f"ERROR: no index.html / compositions/*.html under {dist}", file=sys.stderr)
        return 1

    total = 0
    for f in files:
        for line, msg in scan_file(f):
            total += 1
            print(f"{f}:{line}: {msg}")

    if total:
        print(f"\nFAIL: {total} oversize/overflow signal(s) → content is bigger than the frame and gets clipped (排版过大).")
        print("FIX: keep every element within the 1920x1080 frame (content within the 1920x900 safe area above the caption):")
        print("     - use %/max-width/max-height and flex/grid instead of fixed px larger than the frame;")
        print("     - hero/title text <= ~96px, body <= ~40px; scale SVGs via viewBox, not huge px;")
        print("     - transform: scale() should stay modest (<= ~1.5).")
        return 1

    print(f"OK: no gross oversize/overflow across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
