#!/usr/bin/env python3
r"""
check_svg_height_bound.py — Pre-render gate: fail when an inline <svg> is sized
`width:100%` with an UNBOUNDED height (`height:auto` or no height at all) and its
viewBox aspect ratio would blow the SVG past the usable frame height (场景突然变大).

WHY: This is the exact cause of the "后面的渲染场景突然变大" bug. A content SVG styled

    #mt-g-svg { width:100%; height:auto; }      /* viewBox="0 0 1000 760" */

inside a full-width panel (`.geometry-canvas{width:100%;max-width:1480px}`) becomes
~1380px wide, and because `height:auto` ties the height to the viewBox ratio
(760/1000), it renders ~1050px TALL — far past the ~860px usable height (1080 − top
padding − 180px caption safe zone). The diagram overflows the frame and looks like the
scene "suddenly got big" versus the earlier text scenes.

The static overflow gate (check_scene_overflow.py) CANNOT see this: there is no literal
`px > frame` — the blow-up is produced at render time by `width:100%` × viewBox ratio.
The runtime gate (check_scene_fit.py) DOES catch it, but it GRACEFULLY SKIPS when Chrome
is unavailable. This gate is the deterministic, browserless backstop for that class.

HOW: for each dist/compositions/*.html and dist/index.html it
  - collects every CSS `max-width:Npx` in the file (to estimate the SVG's container width),
  - for each inline `<svg>`, resolves its effective width & height from (a) inline
    `style=`, (b) the `width`/`height` attributes, (c) CSS rules matching its `#id` or
    `.class`,
  - flags the SVG when width ∈ {100%, 100vw} AND height is unbounded (`auto`, or absent,
    with no `max-height`), AND the projected height
        projectedH = innerContainerWidth × ratio
    exceeds SAFE_SVG_H. `ratio` is the CSS `aspect-ratio` when set (that variant —
    `width:100%; aspect-ratio:1` — is the same blow-up), else the intrinsic viewBox ratio
    (viewBoxH / viewBoxW). Wide/landscape SVGs (small ratio) stay well within bounds and are
    NOT flagged; only tall/near-square SVGs at full width trip it — matching the real bug.

Background/decoration SVGs (position:absolute + inset:0, e.g. particle layers) do NOT set
`width:100%;height:auto`, so they are not affected.

Usage:
    python3 check_svg_height_bound.py [dist_dir]     # default ./dist
Exit 0 = clean, 1 = an unbounded-height SVG would overflow the frame.
"""

import re
import sys
from pathlib import Path

from _shared import iter_compositions, line_of

FRAME_W = 1920
FRAME_H = 1080
# Usable content height ≈ 1080 − ~40 top padding − 180 caption safe zone ≈ 860.
# An SVG usually shares its panel with a title/padding, so a content SVG taller than this
# threshold is an overflow risk. Set with margin so only clear cases (like the ~1050px
# graph scene) trip — a borderline 16:9 diagram stays under it.
SAFE_SVG_H = 820
# Fallback container width when the SVG is width:100% and no panel max-width is declared:
# the scene-content inner width (frame − 2×~60px scene padding).
DEFAULT_CONTAINER_W = FRAME_W - 120  # 1800
# Horizontal chrome (panel padding + borders) subtracted from the container ceiling.
PANEL_H_PADDING = 120

RE_SVG = re.compile(r"<svg\b[^>]*>", re.I)
RE_VIEWBOX = re.compile(r'viewBox\s*=\s*"([^"]+)"', re.I)
RE_ID_ATTR = re.compile(r'\bid\s*=\s*"([^"]+)"', re.I)
RE_CLASS_ATTR = re.compile(r'\bclass\s*=\s*"([^"]+)"', re.I)
RE_STYLE_ATTR = re.compile(r'\bstyle\s*=\s*"([^"]+)"', re.I)
RE_W_ATTR = re.compile(r'(?<![-\w])width\s*=\s*"([^"]+)"', re.I)
RE_H_ATTR = re.compile(r'(?<![-\w])height\s*=\s*"([^"]+)"', re.I)
RE_MAXWIDTH_PX = re.compile(r"max-width\s*:\s*(\d+(?:\.\d+)?)px", re.I)

# CSS rule blocks: "selectorlist { decls }"
RE_CSS_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)


def decl_value(decls: str, prop: str):
    """Return the value of a CSS property from a declaration string, or None.
    Uses a lookbehind so `max-width` / `min-height` don't match `width` / `height`."""
    m = re.search(r"(?<![-\w])" + re.escape(prop) + r"\s*:\s*([^;]+)", decls, re.I)
    return m.group(1).strip().lower() if m else None


def parse_aspect_ratio(value):
    """Parse a CSS aspect-ratio into rendered-height/width, or None.
    Accepts `W / H`, `W/H`, or a single number N (= N/1). Ignores the `auto` keyword."""
    if not value:
        return None
    v = value.replace("auto", "").strip()
    if not v:
        return None
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(?:/\s*(\d+(?:\.\d+)?))?$", v)
    if not m:
        return None
    w = float(m.group(1))
    h = float(m.group(2)) if m.group(2) else 1.0
    if w <= 0 or h <= 0:
        return None
    return h / w  # rendered height / width


def build_css_index(txt: str):
    """Map a simple selector token (#id or .class) -> merged declaration string."""
    index = {}
    for m in RE_CSS_RULE.finditer(txt):
        selectors, decls = m.group(1), m.group(2)
        # skip @font-face / @keyframes / at-rules and property-looking noise
        for sel in selectors.split(","):
            sel = sel.strip()
            # keep only a leading simple #id or .class token
            tok = re.match(r"([#.][\w-]+)", sel)
            if not tok:
                continue
            key = tok.group(1)
            index.setdefault(key, "")
            index[key] += ";" + decls
    return index


def resolve_prop(prop, inline_style, attrs, css_index, svg_id, svg_classes):
    """Resolve an effective CSS-ish property for the svg following inline > attr > CSS."""
    # 1. inline style
    if inline_style:
        v = decl_value(inline_style, prop)
        if v is not None:
            return v
    # 2. presentation attribute (width/height only)
    if prop in ("width", "height") and prop in attrs and attrs[prop] is not None:
        return attrs[prop].strip().lower()
    # 3. CSS by id then class
    if svg_id and ("#" + svg_id) in css_index:
        v = decl_value(css_index["#" + svg_id], prop)
        if v is not None:
            return v
    for c in svg_classes:
        if ("." + c) in css_index:
            v = decl_value(css_index["." + c], prop)
            if v is not None:
                return v
    return None


def container_ceiling(txt: str) -> float:
    """Estimate the widest panel the SVG could sit in from declared max-width px values."""
    widths = [float(m.group(1)) for m in RE_MAXWIDTH_PX.finditer(txt)]
    widths = [w for w in widths if 400 <= w <= FRAME_W]
    ceiling = max(widths) if widths else DEFAULT_CONTAINER_W
    return min(ceiling, DEFAULT_CONTAINER_W)


def scan_file(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    css_index = build_css_index(txt)
    ceiling = container_ceiling(txt)
    inner_w = max(200.0, ceiling - PANEL_H_PADDING)
    hits = []

    for m in RE_SVG.finditer(txt):
        tag = m.group(0)
        vb = RE_VIEWBOX.search(tag)
        if not vb:
            continue
        nums = re.split(r"[\s,]+", vb.group(1).strip())
        if len(nums) != 4:
            continue
        try:
            vb_w, vb_h = float(nums[2]), float(nums[3])
        except ValueError:
            continue
        if vb_w <= 0 or vb_h <= 0:
            continue

        id_m = RE_ID_ATTR.search(tag)
        cls_m = RE_CLASS_ATTR.search(tag)
        style_m = RE_STYLE_ATTR.search(tag)
        svg_id = id_m.group(1) if id_m else None
        svg_classes = cls_m.group(1).split() if cls_m else []
        inline_style = style_m.group(1) if style_m else None
        attrs = {
            "width": (RE_W_ATTR.search(tag).group(1) if RE_W_ATTR.search(tag) else None),
            "height": (RE_H_ATTR.search(tag).group(1) if RE_H_ATTR.search(tag) else None),
        }

        width = resolve_prop("width", inline_style, attrs, css_index, svg_id, svg_classes)
        height = resolve_prop("height", inline_style, attrs, css_index, svg_id, svg_classes)
        max_height = resolve_prop("max-height", inline_style, attrs, css_index, svg_id, svg_classes)
        aspect = resolve_prop("aspect-ratio", inline_style, attrs, css_index, svg_id, svg_classes)

        # Only the full-width case blows up vertically.
        if width not in ("100%", "100vw"):
            continue
        # A declared max-height means the author bounded it — trust that.
        if max_height:
            continue
        # Height must be unbounded: explicit `auto`, or simply not set.
        # `aspect-ratio` with an auto/unset height ALSO drives the height from the width,
        # so it is the same blow-up (width:100%; aspect-ratio:1 → square, overflows).
        height_unbounded = (height is None) or (height == "auto")
        if not height_unbounded:
            continue

        # Ratio (rendered height / width). Prefer an explicit CSS aspect-ratio; else the
        # intrinsic viewBox ratio drives `height:auto`.
        ratio = vb_h / vb_w
        ratio_src = f"viewBox {int(vb_w)}×{int(vb_h)}"
        ar = parse_aspect_ratio(aspect)
        if ar is not None:
            ratio = ar
            ratio_src = f"aspect-ratio {aspect.strip()}"

        projected_h = inner_w * ratio
        if projected_h > SAFE_SVG_H:
            label = ("#" + svg_id) if svg_id else (
                ("." + svg_classes[0]) if svg_classes else "<svg>")
            unbounded_by = "height:auto" if ar is None else "aspect-ratio + auto height"
            hits.append((
                line_of(txt, m.start()),
                f"{label}: width:100% + {unbounded_by} with {ratio_src} "
                f"(ratio {ratio:.2f}) → renders ~{int(projected_h)}px tall at "
                f"~{int(inner_w)}px wide, past the ~{SAFE_SVG_H}px safe height "
                f"(内容溢出，场景突然变大)",
            ))
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
        print(f"\nFAIL: {total} unbounded-height SVG(s) will overflow the frame (场景突然变大).")
        print("FIX: never size a content <svg> as `width:100%; height:auto` with a tall/near-square")
        print("     viewBox — its height then follows the aspect ratio and can exceed the frame.")
        print("     Bound the height instead so it letterboxes within the scene:")
        print("       - give the SVG `max-height:<usable>px` (e.g. max-height:760px) OR")
        print("         size it by height (`height:100%` inside a bounded flex/grid box) and let")
        print("         `preserveAspectRatio=\"xMidYMid meet\"` fit the width, OR")
        print("       - pick a viewBox whose aspect ratio matches the available box so width:100%")
        print("         keeps the height within ~820px (usable = 1080 − top pad − 180px captions).")
        return 1

    print(f"OK: no unbounded-height SVG overflow across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
