#!/usr/bin/env python3
r"""
check_svg_label_overlap.py — Pre-render gate: fail if two SVG <text> labels inside the
same <svg> visibly OVERLAP each other (标签文字重叠).

WHY: SVG <text> is positioned by hand (absolute x/y in viewBox units). When several labels
are packed around a shared point or along a short line — a classic case is a pulley/lever
diagram with the fulcrum label 支点O plus 动力臂r / 阻力臂r crammed onto the same diameter —
their glyph boxes collide and the text mashes together ("动力臂 支点O 阻力臂 r"). This is a
real, if subtle, defect the other layout gates miss on purpose:
  - check_scene_overflow.py explicitly IGNORES SVG coordinates (they are viewBox user units).
  - check_scene_layout.py only checks the DOM wrapper height.
So intra-SVG label collisions have no gate — this script fills that gap.

RULE (SKILL.md Rule #28): never stack multiple labels on a shared point / short segment. Give
each label its own side with a clear gap of ≥ ~1 label-height; put a center/fulcrum label
ABOVE the line and the arm/segment labels BELOW it (or offset perpendicular to the line);
anchor arm labels `end`/`start` and push them outward so their boxes never meet.

HOW IT WORKS: for each <svg>, every <text> gets an ESTIMATED bounding box in viewBox units
(font-size resolved from an inline attr/style or a CSS class; width from a CJK/ASCII per-char
em heuristic; x-extent from text-anchor). Two labels in the same <svg> are flagged only when
their boxes overlap SUBSTANTIALLY in BOTH axes (> 35% of the smaller box on each axis) — a
tangent touch or a tiny nick is never flagged. Anything the estimate can't handle safely is
SKIPPED (unresolved font-size, multiline tspan/dy, rotated text/group) so the gate stays
conservative: a render-blocking false positive is worse than a rare miss.

Usage:
    python3 check_svg_label_overlap.py [dist_dir]    # default ./dist
Exit 0 = clean, 1 = at least one overlapping label pair (or no HTML found).
"""

import html
import re
import sys
from pathlib import Path

from _shared import attr, iter_compositions, line_of

RE_SVG = re.compile(r"<svg\b[^>]*>.*?</svg>", re.I | re.S)
RE_STYLE_BLOCK = re.compile(r"<style\b[^>]*>(.*?)</style>", re.I | re.S)
RE_TSPAN_DY = re.compile(r"<tspan\b[^>]*\bdy\s*=", re.I)
RE_TAGS = re.compile(r"<[^>]+>")
RE_WS = re.compile(r"\s+")
# tokens walked in document order inside one <svg>: open-<g>, close-</g>, whole <text>…</text>
RE_TOKEN = re.compile(r"<g\b[^>]*>|</g\s*>|<text\b[^>]*>.*?</text>", re.I | re.S)
RE_TRANSLATE = re.compile(r"translate\(\s*(-?[\d.]+)(?:[ ,]+(-?[\d.]+))?\s*\)", re.I)
RE_NONTRANSLATE_TF = re.compile(r"\b(rotate|scale|matrix|skew[XY]?)\s*\(", re.I)
RE_SCRIPT = re.compile(r"<script\b[^>]*>(.*?)</script>", re.I | re.S)
RE_TWEEN = re.compile(r"\.(?:to|from|fromTo)\s*\(\s*(['\"])(.*?)\1", re.S)
# a tween moves (repositions) its target when its arg objects change x/y/translate/left/top
RE_POS_PROP = re.compile(r"translate\(|[\{,]\s*x\s*:|[\{,]\s*y\s*:|left\s*:|top\s*:", re.I)

# overlap must exceed this fraction of the SMALLER box on BOTH axes to count as a real collision
OVERLAP_FRAC = 0.35


def _num(val):
    if val is None:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", str(val))
    return float(m.group(0)) if m else None


def parse_class_font_sizes(page_text: str) -> dict:
    """Map CSS class name -> font-size(px) from all <style> blocks (last decl wins)."""
    sizes = {}
    for sm in RE_STYLE_BLOCK.finditer(page_text):
        css = sm.group(1)
        # very small CSS parser: `.name , .other { ... font-size: 24px ... }`
        for rule in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
            selectors, body = rule.group(1), rule.group(2)
            fm = re.search(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", body, re.I)
            if not fm:
                continue
            fs = float(fm.group(1))
            for cls in re.findall(r"\.([-\w]+)", selectors):
                sizes[cls] = fs
    return sizes


def resolve_font_size(tag: str, class_sizes: dict):
    """inline font-size attr > inline style font-size > class font-size. None if unknown."""
    fs = _num(attr(tag, "font-size"))
    if fs:
        return fs
    style = attr(tag, "style") or ""
    sm = re.search(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", style, re.I)
    if sm:
        return float(sm.group(1))
    cls = attr(tag, "class") or ""
    for c in cls.split():
        if c in class_sizes:
            return class_sizes[c]
    return None


def inner_text(text_el: str) -> str:
    body = re.sub(r"^<text\b[^>]*>", "", text_el, flags=re.I)
    body = re.sub(r"</text>$", "", body, flags=re.I)
    body = RE_TAGS.sub("", body)  # strip any <tspan>/etc.
    body = html.unescape(body)    # &#8322; → ₂, &minus; → −  (1 glyph, not N chars)
    return RE_WS.sub(" ", body).strip()


def char_em(ch: str) -> float:
    """Approx advance width in em units (no font metrics available)."""
    o = ord(ch)
    if o >= 0x2E80 or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF:
        return 1.0            # CJK ideographs & full-width punctuation
    if ch in "0123456789.,'’\"|iIl!:;":
        return 0.5            # narrow glyphs
    if ch == " ":
        return 0.35
    return 0.6                # generic latin


def text_width(s: str, fs: float) -> float:
    return sum(char_em(c) for c in s) * fs


def text_bbox(tag: str, s: str, fs: float, ox: float = 0.0, oy: float = 0.0):
    """Estimated (x0, y0, x1, y1) in viewBox units, or None if position missing.
    ox/oy = cumulative translate from ancestor <g>s (and the text's own translate)."""
    x = _num(attr(tag, "x"))
    y = _num(attr(tag, "y"))
    if x is None or y is None:
        return None
    x += ox
    y += oy
    w = text_width(s, fs)
    anchor = (attr(tag, "text-anchor") or "").strip().lower()
    if anchor == "middle":
        x0, x1 = x - w / 2, x + w / 2
    elif anchor == "end":
        x0, x1 = x - w, x
    else:
        x0, x1 = x, x + w
    # baseline model: most of the glyph sits above the baseline y
    y0, y1 = y - 0.8 * fs, y + 0.2 * fs
    return (x0, y0, x1, y1)


def overlaps(a, b) -> bool:
    ox = min(a[2], b[2]) - max(a[0], b[0])
    oy = min(a[3], b[3]) - max(a[1], b[1])
    if ox <= 0 or oy <= 0:
        return False
    min_w = min(a[2] - a[0], b[2] - b[0])
    min_h = min(a[3] - a[1], b[3] - b[1])
    if min_w <= 0 or min_h <= 0:
        return False
    return ox > OVERLAP_FRAC * min_w and oy > OVERLAP_FRAC * min_h


def has_rotation(tag: str) -> bool:
    tr = attr(tag, "transform") or ""
    return bool(RE_NONTRANSLATE_TF.search(tr)) or bool(attr(tag, "rotate"))


def parse_transform(tag: str):
    """Return (dx, dy, unsupported) for a tag's transform: summed translate() offset,
    and whether it also carries a rotate/scale/matrix/skew (which makes the estimate
    unreliable → children are skipped)."""
    tr = attr(tag, "transform") or ""
    dx = dy = 0.0
    for m in RE_TRANSLATE.finditer(tr):
        dx += float(m.group(1))
        dy += float(m.group(2)) if m.group(2) is not None else 0.0
    return dx, dy, bool(RE_NONTRANSLATE_TF.search(tr))


def selectors_of(tag: str) -> set:
    """CSS selectors that could match this element: #id and .class tokens."""
    out = set()
    _id = attr(tag, "id")
    if _id:
        out.add("#" + _id)
    for c in (attr(tag, "class") or "").split():
        out.add("." + c)
    return out


def moved_selectors(page_text: str) -> set:
    """Selectors GSAP-tweened with a POSITION change (translate / x / y / left / top).
    These elements are repositioned at runtime, so their static x/y is not where they
    render — skip them to avoid false overlaps (e.g. a movable slider clip). Rotation-
    /scale-/opacity-only tweens are intentionally NOT included (they don't separate two
    labels from each other), so labels inside a rocking <g> are still checked."""
    js = "\n".join(RE_SCRIPT.findall(page_text))
    moved = set()
    for m in RE_TWEEN.finditer(js):
        sel = m.group(2)
        window = js[m.end():m.end() + 500]
        # bound the window to THIS tween call only, so a neighbouring tween's x/y
        # (e.g. an aurora-orb drift right after) can't bleed in and falsely mark this one
        cut = len(window)
        for pat in (");", ".to(", ".from(", ".fromTo("):
            i = window.find(pat)
            if i != -1:
                cut = min(cut, i)
        window = window[:cut]
        if RE_POS_PROP.search(window):
            for s in sel.split(","):
                s = s.strip()
                if s.startswith(("#", ".")):
                    moved.add(s)
    return moved


def scan_file(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    class_sizes = parse_class_font_sizes(txt)
    moved = moved_selectors(txt)
    hits = []
    for sm in RE_SVG.finditer(txt):
        svg = sm.group(0)
        svg_start = sm.start()
        labels = []           # (abs_line, text_str, bbox)
        gstack = []           # per-open-<g>: (dx, dy, unsupported, selectors)
        active_sel = []       # ancestor-group selectors currently in scope
        ox = oy = 0.0         # cumulative translate from ancestor <g>s
        bad_depth = 0         # inside how many rotate/scale/matrix groups (skip texts)
        for tm in RE_TOKEN.finditer(svg):
            tok = tm.group(0)
            tl = tok.lower()
            if tl.startswith("</g"):
                if gstack:
                    dx, dy, unsup, sels = gstack.pop()
                    ox -= dx
                    oy -= dy
                    if unsup:
                        bad_depth -= 1
                    for s in sels:
                        active_sel.remove(s)
                continue
            if re.match(r"<g[\s>]", tl):
                dx, dy, unsup = parse_transform(tok)
                sels = list(selectors_of(tok))
                gstack.append((dx, dy, unsup, sels))
                ox += dx
                oy += dy
                if unsup:
                    bad_depth += 1
                active_sel.extend(sels)
                continue
            # <text>…</text>
            if bad_depth > 0:
                continue
            open_tag = re.match(r"<text\b[^>]*>", tok, re.I).group(0)
            if has_rotation(open_tag) or RE_TSPAN_DY.search(tok):
                continue      # rotated or multiline — estimate unreliable, skip
            self_sel = selectors_of(open_tag)
            if moved and (self_sel | set(active_sel)) & moved:
                continue      # element (or an ancestor group) is repositioned by GSAP
            s = inner_text(tok)
            if not s:
                continue
            fs = resolve_font_size(open_tag, class_sizes)
            if not fs:
                continue      # unknown size → cannot estimate → skip (conservative)
            tdx, tdy, tunsup = parse_transform(open_tag)
            if tunsup:
                continue
            bbox = text_bbox(open_tag, s, fs, ox + tdx, oy + tdy)
            if bbox is None:
                continue
            abs_line = line_of(txt, svg_start + tm.start())
            labels.append((abs_line, s, bbox))
        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                if overlaps(labels[i][2], labels[j][2]):
                    a, b = labels[i], labels[j]
                    hits.append((a[0], a[1], b[0], b[1]))
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
        for la, sa, lb, sb in scan_file(f):
            total += 1
            print(f"{f}:{la}: SVG <text> \"{sa}\" overlaps <text> \"{sb}\" (line {lb}) "
                  f"— labels collide in the same <svg>.")

    if total:
        print(f"\nFAIL: {total} overlapping SVG <text> label pair(s). The text mashes together "
              "in the rendered diagram (文字重叠).")
        print("FIX (see SKILL.md Rule #28):")
        print("  - Never stack multiple labels on a shared point / short diameter.")
        print("  - Put a center/fulcrum label ABOVE the line and arm/segment labels BELOW it,")
        print("    or offset each perpendicular to the line, with a gap of ≥ ~1 label-height.")
        print("  - Anchor arm labels end/start and push them outward past the shape edge.")
        return 1

    print(f"OK: no overlapping SVG <text> labels across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
