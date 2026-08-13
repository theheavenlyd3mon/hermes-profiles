#!/usr/bin/env python3
r"""
check_svg_node_graph.py — Pre-render gate for node-and-connector diagrams
(食物链 / 反馈循环 / 流程图 built from SVG boxes + arrows + in-shape labels).

It catches two classes of "排版" bug that the other gates miss (they only look at
the HTML wrapper or at geometry figures, not at node-graph collisions):

  RULE A — light/white `<text>` must be GROUPED with a dark backing shape.
    A label centered inside a colored SVG shape (e.g. white "负反馈" on a purple
    circle) must live in the SAME `<g>` as that shape, so the two move/scale as one
    unit. When the shape and its label are independent siblings, any transform on the
    shape (GSAP scale/pulse, back.out overshoot, svgOrigin residue) shifts the shape
    but NOT the label — the white text slides off the shape onto the light panel and
    becomes invisible (white-on-white). This is exactly the feedback-scene failure.
    Also flags white text with no dark backing shape at all (invisible on the light bg).

  RULE B — an arrow/connector endpoint must keep clearance from the node box.
    A `<line>`/`<path>` that carries a `marker-end` must not end inside (or flush
    against) a node `<rect>`; otherwise the arrowhead is hidden under / pokes into the
    box (箭头和方框重叠). Endpoints must stop >= CLEAR units before the box edge.

  RULE C — a `<text>` label must not overlap a node box it does not belong to
    (标签压在方框上). Edge labels ("取食"/"捕食") crowding the next box read as broken.

Usage:
    python3 check_svg_node_graph.py [dist_dir]     # default ./dist
Exit 0 = clean, 1 = a node-graph collision / invisible label found.
"""

import re
import sys
from pathlib import Path

from _shared import attr, iter_compositions, line_of

CLEAR = 6.0          # min viewBox-units an arrow endpoint must stop before a box edge
OVERLAP_FRAC = 0.30  # min fraction of a text's box that must overlap a node rect to flag

NAMED = {"white": "#ffffff", "black": "#000000", "none": None}


def parse_color(c):
    if not c:
        return None
    c = c.strip().lower()
    if c in NAMED:
        return NAMED[c]
    m = re.fullmatch(r"#([0-9a-f]{3})", c)
    if m:
        h = m.group(1)
        return "#" + "".join(ch * 2 for ch in h)
    m = re.fullmatch(r"#([0-9a-f]{6})", c)
    if m:
        return "#" + m.group(1)
    m = re.fullmatch(r"rgba?\(\s*(\d+)\D+(\d+)\D+(\d+)", c)
    if m:
        return "#%02x%02x%02x" % tuple(int(m.group(i)) for i in (1, 2, 3))
    return None


def luminance(hexc):
    if not hexc:
        return None
    r = int(hexc[1:3], 16) / 255
    g = int(hexc[3:5], 16) / 255
    b = int(hexc[5:7], 16) / 255
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def fill_of(tag, css):
    """Effective fill color of an element: fill attribute, else its class's CSS fill."""
    f = attr(tag, "fill")
    if f is not None:
        return parse_color(f)
    cls = attr(tag, "class")
    if cls:
        for c in cls.split():
            m = re.search(r"(?<![\w-])\." + re.escape(c) + r"\s*\{([^}]*)\}", css)
            if m:
                fm = re.search(r"fill\s*:\s*([^;}\s]+)", m.group(1))
                if fm:
                    return parse_color(fm.group(1))
    return None  # SVG default fill is black (dark)


def font_size_of(tag, css):
    fs = attr(tag, "font-size")
    if fs:
        m = re.match(r"([\d.]+)", fs)
        if m:
            return float(m.group(1))
    cls = attr(tag, "class")
    if cls:
        for c in cls.split():
            m = re.search(r"(?<![\w-])\." + re.escape(c) + r"\s*\{([^}]*)\}", css)
            if m:
                fm = re.search(r"font-size\s*:\s*([\d.]+)px", m.group(1))
                if fm:
                    return float(fm.group(1))
    return 30.0


def text_width(content, fs):
    """Rough rendered width of SVG text content in viewBox units."""
    # decode common entities to a single glyph each
    txt = re.sub(r"&[a-zA-Z]+;", "→", content)  # arrows/etc → 1 wide glyph
    txt = re.sub(r"<[^>]+>", "", txt)
    w = 0.0
    for ch in txt:
        if ch.isspace():
            w += fs * 0.32
        elif ord(ch) > 0x2E80:   # CJK & full-width
            w += fs * 1.0
        else:
            w += fs * 0.55
    return w


def text_bbox(tag, content, css):
    x = float(attr(tag, "x") or 0)
    y = float(attr(tag, "y") or 0)
    fs = font_size_of(tag, css)
    w = text_width(content, fs)
    anchor = (attr(tag, "text-anchor") or "start").strip()
    if anchor == "middle":
        x0, x1 = x - w / 2, x + w / 2
    elif anchor == "end":
        x0, x1 = x - w, x
    else:
        x0, x1 = x, x + w
    return (x0, y - fs * 0.9, x1, y + fs * 0.15)


def path_endpoint(d):
    nums = re.findall(r"-?\d+(?:\.\d+)?", d)
    if len(nums) >= 2:
        return float(nums[-2]), float(nums[-1])
    return None


def find_groups(svg):
    """Return list of (start, end) char spans for each <g>…</g> (depth-aware)."""
    spans = []
    stack = []
    for m in re.finditer(r"<g\b[^>]*>|</g>", svg):
        if m.group(0).startswith("</g"):
            if stack:
                spans.append((stack.pop(), m.end()))
        else:
            stack.append(m.start())
    return spans


def rects_of(svg, css):
    """Node boxes: rects with a stroke and a meaningful size."""
    boxes = []
    for m in re.finditer(r"<rect\b[^>]*/?>", svg):
        t = m.group(0)
        try:
            x = float(attr(t, "x")); y = float(attr(t, "y"))
            w = float(attr(t, "width")); h = float(attr(t, "height"))
        except (TypeError, ValueError):
            continue
        has_stroke = attr(t, "stroke") or (attr(t, "class") or "")
        if w >= 80 and h >= 40 and has_stroke:
            boxes.append((m.start(), x, y, w, h))
    return boxes


def dark_shapes(svg, css):
    """Return True if the substring contains a dark-filled circle/rect/ellipse/path."""
    for m in re.finditer(r"<(circle|ellipse|rect|path)\b[^>]*/?>", svg):
        lum = luminance(fill_of(m.group(0), css))
        if lum is not None and lum < 0.5:
            return True
        # explicit fill omitted on a filled shape defaults to black (dark) — but only
        # count that for circle/ellipse (rects here are white cards). Be conservative.
    return False


def scan_file(path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for sm in re.finditer(r"<svg\b[^>]*>.*?</svg>", txt, re.S):
        svg = sm.group(0)
        base = sm.start()
        groups = find_groups(svg)
        boxes = rects_of(svg, txt)

        def enclosing_groups(pos):
            return [(s, e) for (s, e) in groups if s < pos < e]

        # ---- RULE A: light text must be grouped with a dark shape ----
        for tm in re.finditer(r"<text\b([^>]*)>(.*?)</text>", svg, re.S):
            tag = "<text" + tm.group(1) + ">"
            lum = luminance(fill_of(tag, txt))
            if lum is None or lum < 0.75:
                continue  # only white / very light labels are at risk
            ok = False
            for (s, e) in enclosing_groups(tm.start()):
                if dark_shapes(svg[s:e], txt):
                    ok = True
                    break
            if not ok:
                hits.append((line_of(txt, base + tm.start()),
                             "light/white <text> is not grouped with a dark backing shape "
                             "(put the shape + its label in ONE <g>, or the label slides off "
                             "the shape → invisible white-on-panel)"))

        # ---- RULE B: arrow/connector endpoint clearance from node boxes ----
        connectors = []
        for lm in re.finditer(r"<line\b[^>]*>", svg):
            t = lm.group(0)
            if "marker-end" not in t:
                continue
            try:
                connectors.append((lm.start(), float(attr(t, "x2")), float(attr(t, "y2"))))
            except (TypeError, ValueError):
                pass
        for pm in re.finditer(r"<path\b[^>]*>", svg):
            t = pm.group(0)
            if "marker-end" not in t:
                continue
            ep = path_endpoint(attr(t, "d") or "")
            if ep:
                connectors.append((pm.start(), ep[0], ep[1]))
        for (pos, ex, ey) in connectors:
            for (_, x, y, w, h) in boxes:
                if (x - CLEAR) <= ex <= (x + w + CLEAR) and (y - CLEAR) <= ey <= (y + h + CLEAR):
                    hits.append((line_of(txt, base + pos),
                                 f"arrow/connector endpoint ({ex:.0f},{ey:.0f}) ends inside/"
                                 f"flush against a node box → arrowhead overlaps the 方框; stop "
                                 f"it >= {CLEAR:.0f}u before the box edge"))
                    break

        # ---- RULE C: a text label overlaps a node box it doesn't belong to ----
        for tm in re.finditer(r"<text\b([^>]*)>(.*?)</text>", svg, re.S):
            tag = "<text" + tm.group(1) + ">"
            tb = text_bbox(tag, tm.group(2), txt)
            own = enclosing_groups(tm.start())
            for (bpos, x, y, w, h) in boxes:
                # skip the box that owns this text (same <g>)
                if any(s < bpos < e for (s, e) in own):
                    continue
                ix = max(0.0, min(tb[2], x + w) - max(tb[0], x))
                iy = max(0.0, min(tb[3], y + h) - max(tb[1], y))
                area = ix * iy
                tarea = max(1.0, (tb[2] - tb[0]) * (tb[3] - tb[1]))
                if area / tarea > OVERLAP_FRAC:
                    hits.append((line_of(txt, base + tm.start()),
                                 "text label overlaps a node 方框 it doesn't belong to "
                                 "(move the label into the gap / give it clearance)"))
                    break
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
        for line, msg in scan_file(f):
            total += 1
            print(f"{f}:{line}: {msg}")
    if total:
        print(f"\nFAIL: {total} node-graph collision(s) — invisible in-shape labels or "
              "arrows/labels overlapping node boxes (箭头/文字与方框重叠).")
        print("FIX:")
        print("  - Put every in-shape label in the SAME <g> as its shape: "
              "<g><circle/><text/></g> (never independent siblings).")
        print("  - White SVG text is allowed ONLY inside a dark shape that contains it.")
        print("  - Stop arrow/connector endpoints >= 6u before a node box; keep edge "
              "labels out of the boxes.")
        return 1
    print(f"OK: no node-graph collisions across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
