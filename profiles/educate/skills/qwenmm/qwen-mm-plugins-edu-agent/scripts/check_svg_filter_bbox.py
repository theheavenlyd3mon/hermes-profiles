#!/usr/bin/env python3
r"""
check_svg_filter_bbox.py — Pre-render gate: fail if a glow/blur filter is applied to
an axis-aligned <line> (a force arrow, axis, ray, wire, tick, …).

WHY (reproducibility): a perfectly horizontal or vertical <line> has a DEGENERATE
bounding box — zero height (horizontal) or zero width (vertical). SVG filters default
to `filterUnits="objectBoundingBox"` with a filter region of x=-10% y=-10% w=120%
h=120% RELATIVE TO THAT BBOX. Multiply a percentage by a zero dimension and the filter
region collapses to zero area → the filtered result is EMPTY. The line AND its
`marker-end` arrowhead render nothing at all, while the separate <text> label (which
carries no filter) still shows. Symptom in the video: "只有力的字，没有力的线条" —
the force LETTER appears but the force ARROW/LINE is invisible.

This is insidious because it only bites AXIS-ALIGNED strokes: a diagonal ray has a
nonzero-area bbox and survives, so the same `filter="url(#glow)"` pattern looks fine on
slanted light rays but silently deletes vertical gravity/normal arrows and horizontal
velocity arrows. Blank-frame detection does NOT catch it (the scene still has the belt,
block and labels, so it is not "blank").

RULE (see SKILL.md): never put a bbox-relative filter directly on an axis-aligned line.
Fix any of these ways:
  1. BEST — drop the filter from the arrow; use a slightly thicker stroke + marker. A
     force arrow does not need a glow to read well.
  2. Give the referenced <filter> an ABSOLUTE region so it no longer depends on the
     bbox:  <filter id="fGlow" filterUnits="userSpaceOnUse"
                    x="0" y="0" width="<viewBoxW>" height="<viewBoxH>"> … </filter>
  3. Apply the glow to a wrapping <g> that also contains a non-degenerate element, or
     nudge the line 0.01px off-axis (hacky — prefer 1 or 2).

This gate scans <line> elements with an inline `filter="url(#ID)"` attribute. A line is
flagged when it is axis-aligned (x1==x2 OR y1==y2, which also covers the zero-length
`x2=x1,y2=y1` start state used for draw-on animation) AND the referenced filter is NOT
declared `filterUnits="userSpaceOnUse"`. Diagonal filtered lines are never flagged.

Usage:
    python3 check_svg_filter_bbox.py [dist_dir]    # default ./dist
Exit 0 = clean, 1 = at least one degenerate filtered line (or no HTML found).
"""

import re
import sys
from pathlib import Path

from _shared import attr, iter_compositions, line_of

RE_LINE = re.compile(r"<line\b[^>]*>", re.I)
RE_FILTER_ATTR = re.compile(r"""\bfilter\s*=\s*["']\s*url\(\s*#([\w:-]+)\s*\)""", re.I)
RE_FILTER_DEF = re.compile(r"<filter\b[^>]*\bid\s*=\s*[\"']([\w:-]+)[\"'][^>]*>", re.I)
RE_USERSPACE = re.compile(r"""filterUnits\s*=\s*["']\s*userSpaceOnUse""", re.I)


def userspace_filter_ids(txt: str):
    """IDs of <filter> defs declared filterUnits='userSpaceOnUse' (safe — absolute region)."""
    safe = set()
    for m in RE_FILTER_DEF.finditer(txt):
        if RE_USERSPACE.search(m.group(0)):
            safe.add(m.group(1))
    return safe


def scan_file(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    safe = userspace_filter_ids(txt)
    hits = []
    for m in RE_LINE.finditer(txt):
        tag = m.group(0)
        fm = RE_FILTER_ATTR.search(tag)
        if not fm:
            continue
        fid = fm.group(1)
        if fid in safe:
            continue  # filter uses an absolute region → bbox is irrelevant
        x1 = attr(tag, "x1") or 0.0
        y1 = attr(tag, "y1") or 0.0
        x2 = attr(tag, "x2") or 0.0
        y2 = attr(tag, "y2") or 0.0
        vertical = (x1 == x2)
        horizontal = (y1 == y2)
        if vertical or horizontal:
            if x1 == x2 and y1 == y2:
                kind = "zero-length (draw-on start) → axis-aligned"
            elif vertical:
                kind = "vertical (bbox width = 0)"
            else:
                kind = "horizontal (bbox height = 0)"
            hits.append((line_of(txt, m.start()), fid, kind))
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
        for ln, fid, kind in scan_file(f):
            total += 1
            print(f"{f}:{ln}: <line> is {kind} but has filter=\"url(#{fid})\" "
                  f"→ zero-area filter region makes the line + arrowhead INVISIBLE.")

    if total:
        print(f"\nFAIL: {total} axis-aligned <line>(s) carry a bbox-relative glow/blur filter. "
              "They render NOTHING in the video (only their <text> labels show).")
        print("FIX (pick one):")
        print("  1. BEST — remove filter=\"url(#…)\" from the arrow/line; use a thicker stroke.")
        print("  2. Make the filter absolute so it ignores the degenerate bbox:")
        print('       <filter id="fGlow" filterUnits="userSpaceOnUse" x="0" y="0" '
              'width="<viewBoxW>" height="<viewBoxH>">…</filter>')
        print("  3. Apply the glow to a wrapping <g> with a non-degenerate child.")
        return 1

    print(f"OK: no axis-aligned filtered <line>s across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
