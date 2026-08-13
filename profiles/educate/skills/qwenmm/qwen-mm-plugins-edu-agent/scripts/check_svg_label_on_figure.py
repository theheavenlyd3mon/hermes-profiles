#!/usr/bin/env python3
r"""
check_svg_label_on_figure.py — Pre-render gate: fail if an SVG `<text>` label overlaps the
DRAWING itself (a line/segment/axis passing through the letters, or a vertex dot sitting on
top of the label). Symptom: 图里的字母(A/B/O/F…)压在图形/线条上,看不清 (文字和画图重叠).

This complements `check_svg_label_overlap.py` (which only checks label-vs-label). Here we
check label-vs-geometry:
  1. a `<line>` segment that passes THROUGH a label's box (the stroke crosses the letters);
  2. a small vertex-marker `<circle>` (a point dot, r<=12) whose center sits INSIDE a label.

FIX: offset every point/vertex/curve label OUTWARD, away from the figure, by ~18–24 units
(never place a label exactly on the point coordinate or on a stroke). Anchor it on the side
pointing away from the shape center; put axis-point labels just below/above the axis, not on it.

DESIGN FOR LOW FALSE POSITIVES: coordinates must be literal numbers; text/line/circle inside a
transformed `<g>` (rotate/scale/matrix or translate) are SKIPPED (coords can't be trusted);
font-size must resolve; the label box is shrunk to its inner 60% before testing, so a label
merely sitting NEXT TO a line (the normal, correct case) is never flagged — only a stroke
cutting through the middle of the glyphs, or a dot squarely inside them, trips it.

Usage:
    python3 check_svg_label_on_figure.py [dist_dir]     # default ./dist
Exit 0 = clean, 1 = a label overlaps the drawing (or no HTML found).
"""

import html
import re
import sys
from pathlib import Path

from _shared import attr, iter_compositions

RE_SVG = re.compile(r"<svg\b[^>]*>.*?</svg>", re.I | re.S)
RE_STYLE_BLOCK = re.compile(r"<style\b[^>]*>(.*?)</style>", re.I | re.S)
RE_TEXT = re.compile(r"<text\b[^>]*>.*?</text>", re.I | re.S)
RE_LINE = re.compile(r"<line\b[^>]*>", re.I)
RE_CIRCLE = re.compile(r"<circle\b[^>]*>", re.I)
RE_TAGS = re.compile(r"<[^>]+>")
RE_WS = re.compile(r"\s+")
RE_ANYTRANSFORM = re.compile(r"transform\s*=", re.I)
VERTEX_DOT_MAX_R = 12.0      # a circle this small is a point marker, not a shape
INSET = 0.20                 # shrink label box to inner 60% before testing


def num(v):
    if v is None:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", str(v))
    return float(m.group(0)) if m else None


def class_font_sizes(page):
    sizes = {}
    for sm in RE_STYLE_BLOCK.finditer(page):
        for rule in re.finditer(r"([^{}]+)\{([^{}]*)\}", sm.group(1)):
            fm = re.search(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", rule.group(2), re.I)
            if fm:
                for cls in re.findall(r"\.([-\w]+)", rule.group(1)):
                    sizes[cls] = float(fm.group(1))
    return sizes


def font_size(tag, class_sizes):
    fs = num(attr(tag, "font-size"))
    if fs:
        return fs
    style = attr(tag, "style") or ""
    m = re.search(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", style, re.I)
    if m:
        return float(m.group(1))
    for c in (attr(tag, "class") or "").split():
        if c in class_sizes:
            return class_sizes[c]
    return None


def inner_text(el):
    b = re.sub(r"^<text\b[^>]*>", "", el, flags=re.I)
    b = re.sub(r"</text>$", "", b, flags=re.I)
    b = html.unescape(RE_TAGS.sub("", b))
    return RE_WS.sub(" ", b).strip()


def char_em(ch):
    o = ord(ch)
    if o >= 0x2E80 or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF:
        return 1.0
    if ch in "0123456789.,'\"|iIl!:;":
        return 0.5
    if ch == " ":
        return 0.35
    return 0.6


def text_bbox(tag, s, fs):
    x, y = num(attr(tag, "x")), num(attr(tag, "y"))
    if x is None or y is None:
        return None
    w = sum(char_em(c) for c in s) * fs
    anchor = (attr(tag, "text-anchor") or "").strip().lower()
    if anchor == "middle":
        x0 = x - w / 2
    elif anchor == "end":
        x0 = x - w
    else:
        x0 = x
    x1 = x0 + w
    y0, y1 = y - 0.75 * fs, y + 0.20 * fs   # baseline → glyph box
    return (x0, y0, x1, y1)


def inset_box(b):
    x0, y0, x1, y1 = b
    dx, dy = (x1 - x0) * INSET, (y1 - y0) * INSET
    return (x0 + dx, y0 + dy, x1 - dx, y1 - dy)


def seg_hits_box(x1, y1, x2, y2, box):
    """Liang–Barsky: does segment (x1,y1)-(x2,y2) intersect axis-aligned box?"""
    bx0, by0, bx1, by1 = box
    dx, dy = x2 - x1, y2 - y1
    p = [-dx, dx, -dy, dy]
    q = [x1 - bx0, bx1 - x1, y1 - by0, by1 - y1]
    u1, u2 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return False
        else:
            t = qi / pi
            if pi < 0:
                u1 = max(u1, t)
            else:
                u2 = min(u2, t)
    return u1 <= u2


def scan_svg(svg, page_start_line, full_txt):
    hits = []
    class_sizes = class_font_sizes(full_txt)

    # collect literal, non-transformed lines & small vertex dots
    lines = []
    for m in RE_LINE.finditer(svg):
        tag = m.group(0)
        if RE_ANYTRANSFORM.search(tag):
            continue
        c = [num(attr(tag, a)) for a in ("x1", "y1", "x2", "y2")]
        if None not in c:
            lines.append(tuple(c))
    dots = []
    for m in RE_CIRCLE.finditer(svg):
        tag = m.group(0)
        if RE_ANYTRANSFORM.search(tag):
            continue
        cx, cy, r = num(attr(tag, "cx")), num(attr(tag, "cy")), num(attr(tag, "r"))
        if None not in (cx, cy, r) and r <= VERTEX_DOT_MAX_R:
            dots.append((cx, cy))

    if not lines and not dots:
        return hits

    for m in RE_TEXT.finditer(svg):
        tag = m.group(0)
        if RE_ANYTRANSFORM.search(tag.split(">", 1)[0]):
            continue
        s = inner_text(tag)
        if not s:
            continue
        fs = font_size(tag, class_sizes)
        if not fs:
            continue
        b = text_bbox(tag, s, fs)
        if not b:
            continue
        ib = inset_box(b)
        ln = page_start_line + svg[:m.start()].count("\n")
        crossed = next((L for L in lines if seg_hits_box(*L, ib)), None)
        if crossed:
            hits.append((ln, f'label "{s[:14]}" has a <line> passing THROUGH it (stroke crosses the '
                             f'letters) → offset the label off the stroke (~18–24u away from the figure).'))
            continue
        dot = next((d for d in dots if ib[0] <= d[0] <= ib[2] and ib[1] <= d[1] <= ib[3]), None)
        if dot:
            hits.append((ln, f'label "{s[:14]}" sits on top of a vertex dot → offset the label outward '
                             f'(~18–24u) instead of placing it on the point.'))
    return hits


def main():
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
        txt = f.read_text(encoding="utf-8", errors="replace")
        for m in RE_SVG.finditer(txt):
            base = txt[:m.start()].count("\n") + 1
            for line, msg in scan_svg(m.group(0), base, txt):
                total += 1
                print(f"{f}:{line}: {msg}")

    if total:
        print(f"\nFAIL: {total} label(s) overlap the drawing (文字和画图重叠).")
        print("FIX: offset each point/vertex/curve label OUTWARD ~18–24 units, away from the shape "
              "center; never place a label on a stroke or exactly on a point/dot.")
        return 1

    print(f"OK: no label overlaps the drawing across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
