#!/usr/bin/env python3
r"""
check_svg_arrow.py — Pre-render gate: catch broken SVG arrows (force/vector/velocity arrows).

Three failure modes seen in rendered videos (受力/矢量箭头):

  1. GIANT arrowheads (箭头太大). A `<marker>` with no `markerUnits` defaults to
     `markerUnits="strokeWidth"`, so the arrowhead size is MULTIPLIED by the line's
     stroke-width. Force arrows use a thick stroke (6–8) for video, so a
     `markerWidth="12"` head becomes ~72–96px — a huge triangle swamping the figure.
     FIX: put `markerUnits="userSpaceOnUse"` on the marker and size it in absolute px.

  2. Zero-length animated line WITH a marker (线没画出来 + 箭头方向不对). Authors draw a
     `<line>` collapsed to a point (`x1==x2 && y1==y2`) and grow it via GSAP `attr:{y2}`.
     A zero-length line has NO shaft, and `orient="auto"` on it is undefined → the
     arrowhead renders at 0° (sideways) instead of along the force. If the attr tween
     doesn't seek correctly at render, the shaft never appears at all.
     FIX: draw the line at FULL length (correct geometry so orient is right) and reveal it
     with `stroke-dashoffset` (draw-on). Or use the prebuilt CSS `force-arrow` component
     (assets/components/mechanics/force-arrow.html), whose head is a fixed size.

  3. Arrowhead geometry points the WRONG WAY under orient="auto" (箭头方向画错了 —
     该向下的箭头，头部却画成了水平/侧向). `orient="auto"` rotates the marker so its LOCAL
     +x axis follows the line's travel direction, so the arrowhead triangle MUST be drawn
     pointing to the RIGHT (+x). Authors instead draw it pointing along +y (down) —
     e.g. `<polygon points="0,0 16,0 8,14">` (apex at the bottom) — thinking of the final
     on-screen direction. orient="auto" then adds the line's rotation ON TOP, so on a
     vertical (downward) line the apex ends up pointing sideways (horizontal). Real bug:
     `<marker orient="auto"><polygon points="0,0 16,0 8,14"/></marker>` on a straight-down
     line rendered a horizontal arrowhead.
     FIX: draw the head pointing +x, e.g. `points="0,0 0,16 14,8"` (apex at right,
     refX≈14 refY≈8) and keep orient="auto" — it then points correctly along ANY line.
     If you really want a fixed non-rotating arrow, keep the +y geometry but use a numeric
     `orient` (e.g. orient="0"/"90") instead of "auto".

Usage:
    python3 check_svg_arrow.py [dist_dir]     # default ./dist
Exit 0 = clean, 1 = a broken arrow found.
"""

import math
import re
import sys
from pathlib import Path

from _shared import attr, iter_compositions, line_of

RE_MARKER = re.compile(r"<marker\b[^>]*>", re.I)
RE_MARKER_BLOCK = re.compile(r"<marker\b[^>]*>.*?</marker\s*>", re.I | re.S)
RE_HAS_USOU = re.compile(r'markerUnits\s*=\s*"userSpaceOnUse"', re.I)
RE_LINE = re.compile(r"<line\b[^>]*>", re.I)
RE_HAS_MARKEREND = re.compile(r'marker-(?:end|start)\s*=', re.I)
RE_POLYGON = re.compile(r"<polygon\b[^>]*\bpoints\s*=\s*\"([^\"]*)\"[^>]*>", re.I)
RE_PATH = re.compile(r"<path\b[^>]*\bd\s*=\s*\"([^\"]*)\"[^>]*>", re.I)
RE_NUM = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _points_from(numbers):
    """Turn a flat list of numbers into (x, y) pairs, de-duplicating consecutive/closing repeats."""
    pts = []
    for i in range(0, len(numbers) - 1, 2):
        p = (round(numbers[i], 3), round(numbers[i + 1], 3))
        if not pts or pts[-1] != p:
            pts.append(p)
    # drop a closing point equal to the first (polygon auto-closes / path "Z")
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts.pop()
    return pts


def arrowhead_direction(pts):
    """
    Given the vertices of a triangular arrowhead, return a unit (dx, dy) for the
    direction it visually points, or None if it's not a recognizable triangle.

    The apex is the vertex whose two edges to the other two are most nearly equal
    (arrowheads are isosceles; the two base corners mirror across the pointing axis).
    Direction = apex - midpoint(base).
    """
    if len(pts) != 3:
        return None
    best_apex = None
    best_asym = None
    for i in range(3):
        apex = pts[i]
        a, b = pts[(i + 1) % 3], pts[(i + 2) % 3]
        la = math.dist(apex, a)
        lb = math.dist(apex, b)
        asym = abs(la - lb)
        if best_asym is None or asym < best_asym:
            best_asym, best_apex, base = asym, apex, (a, b)
    mx = (base[0][0] + base[1][0]) / 2.0
    my = (base[0][1] + base[1][1]) / 2.0
    dx, dy = best_apex[0] - mx, best_apex[1] - my
    n = math.hypot(dx, dy)
    if n == 0:
        return None
    return (dx / n, dy / n)


def scan_file(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    hits = []

    # 1) arrowhead markers must be userSpaceOnUse (else scaled by strokeWidth → giant)
    for m in RE_MARKER.finditer(txt):
        tag = m.group(0)
        if not RE_HAS_USOU.search(tag):
            mid = attr(tag, "id") or "?"
            hits.append((line_of(txt, m.start()),
                         f'<marker id="{mid}"> has no `markerUnits="userSpaceOnUse"` → the arrowhead is '
                         f'scaled by the line stroke-width (thick force strokes → giant head). '
                         f'Add markerUnits="userSpaceOnUse" and size the head in absolute px.'))

    # 1b) arrowhead geometry must point +x when orient="auto" (else wrong direction after rotation)
    for m in RE_MARKER_BLOCK.finditer(txt):
        block = m.group(0)
        open_tag = block[:block.find(">") + 1]
        orient = (attr(open_tag, "orient") or "0").strip().lower()
        if orient not in ("auto", "auto-start-reverse"):
            continue  # numeric/absent orient → author controls rotation, geometry is intentional
        mid = attr(open_tag, "id") or "?"
        # find the arrowhead shape inside the marker (polygon preferred, else a simple path)
        pm = RE_POLYGON.search(block)
        nums = None
        if pm:
            nums = [float(x) for x in RE_NUM.findall(pm.group(1))]
        else:
            pa = RE_PATH.search(block)
            if pa:
                nums = [float(x) for x in RE_NUM.findall(pa.group(1))]
        if not nums or len(nums) < 6:
            continue
        pts = _points_from(nums)
        d = arrowhead_direction(pts)
        if d is None:
            continue  # not a plain triangle → don't guess
        dx, dy = d
        # a correct orient="auto" head points to the RIGHT: dx>0 and dominant over dy
        if dx > 0 and dx >= abs(dy):
            continue
        if abs(dy) > abs(dx):
            wrong = "vertically (up/down, +y/-y)"
        else:
            wrong = "to the left (-x)"
        hits.append((line_of(txt, m.start()),
                     f'<marker id="{mid}" orient="auto"> arrowhead points {wrong}, but orient="auto" '
                     f'rotates the marker so its LOCAL +x axis follows the line — so the head MUST be drawn '
                     f'pointing RIGHT (+x). As drawn, orient="auto" adds the line angle on top, so e.g. a '
                     f'straight-down line renders a sideways/horizontal head (方向画错了). '
                     f'FIX: draw the triangle pointing +x, e.g. points="0,0 0,16 14,8" (apex at right, '
                     f'refX≈14 refY≈8); or keep this geometry but set a numeric orient (e.g. orient="90").'))

    # 2) a <line> that carries a marker but is ZERO-LENGTH in the static SVG
    for m in RE_LINE.finditer(txt):
        tag = m.group(0)
        if not RE_HAS_MARKEREND.search(tag):
            continue
        x1, y1 = num(attr(tag, "x1")), num(attr(tag, "y1"))
        x2, y2 = num(attr(tag, "x2")), num(attr(tag, "y2"))
        if None in (x1, y1, x2, y2):
            continue
        if x1 == x2 and y1 == y2:
            lid = attr(tag, "id") or "?"
            hits.append((line_of(txt, m.start()),
                         f'<line id="{lid}"> has a marker but is ZERO-LENGTH (x1==x2 && y1==y2) → no shaft '
                         f'renders and `orient="auto"` points the arrowhead sideways (方向不对). Draw the line '
                         f'at FULL length and reveal with stroke-dashoffset (do NOT animate length from a point).'))
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
        print(f"\nFAIL: {total} broken SVG arrow(s) → giant/sideways/wrong-direction/invisible force arrows.")
        print("FIX: (a) every arrowhead `<marker>` uses `markerUnits=\"userSpaceOnUse\"` + absolute px size; "
              "(b) an orient=\"auto\" arrowhead must be drawn pointing RIGHT (+x), e.g. points=\"0,0 0,16 14,8\" "
              "(NOT +y like \"0,0 16,0 8,14\", which renders sideways on vertical lines); "
              "(c) draw force lines at FULL length with correct direction and reveal via `stroke-dashoffset` "
              "(never animate a marker line from zero length). Best: reuse the prebuilt CSS `force-arrow` component.")
        return 1

    print(f"OK: SVG arrows are well-formed across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
