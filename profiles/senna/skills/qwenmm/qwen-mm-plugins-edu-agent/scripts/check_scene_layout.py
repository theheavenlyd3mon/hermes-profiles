#!/usr/bin/env python3
r"""
check_scene_layout.py — Pre-render gate: fail if a scene's content will NOT be
vertically centered and instead piles at the TOP of the frame (bottom half empty).

WHY: A scene's root div is a fixed 1920x1080 box. The inner content lives in a
`<div class="scene-content">` wrapper. For content to sit in the middle of the frame
(the intended look) ONE of these must hold:

  (A) `.scene-content` is itself a CENTERING container:
        .scene-content { position:absolute; inset:0; display:flex;
                         align-items:center; justify-content:center; }
      (this is the canonical rule in design-system.md → *Layout & Space Usage*), OR

  (B) the content wrapper (first child of `.scene-content`) FILLS the height itself,
      e.g. `.principle-layout { display:flex; width:100%; height:100% }` for a split
      diagram, or `.title-container { position:absolute; inset:0; ... }` for a title.

If NEITHER holds — `.scene-content` fills the frame (position:absolute; inset:0) but has
NO flex/grid centering, and its child is a normal-flow block (a glass panel with only
`max-width/width`, no `height:100%`) — then the child collapses to its content height and
sticks to the TOP:
  - vertical centering fails → everything piles at the top, the bottom ~40-50% is empty;
  - height:auto SVG diagrams in a height:100% column collapse → blank side panel.

This is exactly the "排版" bug seen in generated single-panel scenes (problem / step / 结论):
their `.scene-content` was emitted as `position:absolute;inset:0` WITHOUT the
`display:flex;align-items:center;justify-content:center`, so the panel hugged the top.

FIX (preferred): make `.scene-content` a centering flex container:
  .scene-content { position:absolute; inset:0; display:flex;
                   align-items:center; justify-content:center;
                   padding:40px 60px 180px; box-sizing:border-box; }

Usage:
    python3 check_scene_layout.py [dist_dir]    # default ./dist
Exit 0 = clean, 1 = a scene whose content will pile at the top (or no HTML found).
"""

import re
import sys
from pathlib import Path

from _shared import iter_compositions, line_of

# "fills the frame / establishes height" = absolute+inset:0, or an explicit full height
RE_INSET = re.compile(r"inset\s*:\s*0", re.I)
RE_POS_ABS = re.compile(r"position\s*:\s*absolute", re.I)
RE_FULL_H = re.compile(r"height\s*:\s*(100%|100vh|1080px)", re.I)
RE_TOP_BOTTOM = re.compile(r"top\s*:\s*0[^;]*;[^}]*bottom\s*:\s*0", re.I)

# "centers its children" = a flex/grid container that centers on both axes
RE_DISPLAY_FLEXGRID = re.compile(r"display\s*:\s*(flex|inline-flex|grid|inline-grid)", re.I)
RE_ALIGN_CENTER = re.compile(r"align-items\s*:\s*center", re.I)
RE_JUSTIFY_CENTER = re.compile(r"justify-content\s*:\s*center", re.I)
RE_PLACE_CENTER = re.compile(r"place-(items|content)\s*:\s*center", re.I)


def establishes_height(style: str) -> bool:
    if RE_FULL_H.search(style):
        return True
    if RE_POS_ABS.search(style) and (RE_INSET.search(style) or RE_TOP_BOTTOM.search(style)):
        return True
    return False


def establishes_centering(style: str) -> bool:
    """True if this element flex/grid-centers its children on both axes."""
    if not RE_DISPLAY_FLEXGRID.search(style):
        return False
    if RE_PLACE_CENTER.search(style):
        return True
    return bool(RE_ALIGN_CENTER.search(style) and RE_JUSTIFY_CENTER.search(style))


def css_rule_for_class(txt: str, cls: str) -> str:
    """Concatenate every standalone `.cls { ... }` rule body (best-effort).

    Only matches rules whose selector is exactly `.cls` immediately followed by `{`
    (optionally with whitespace) — enough for these self-contained composition files.
    A combined selector like `.a,.b,.cls{...}` is intentionally skipped because those
    shared rules only carry paint (background/border/shadow), never height/centering.
    """
    bodies = []
    for m in re.finditer(r"(?<![\w-])\." + re.escape(cls) + r"\s*\{([^}]*)\}", txt):
        bodies.append(m.group(1))
    return " ; ".join(bodies)


def combined_style_for_div(txt: str, tag: str) -> str:
    """inline style + resolved CSS rules for each class on the given <div ...> tag."""
    sm = re.search(r'style="([^"]*)"', tag)
    style = sm.group(1) if sm else ""
    cm = re.search(r'class="([^"]*)"', tag)
    if cm:
        for cls in cm.group(1).split():
            style += " ; " + css_rule_for_class(txt, cls)
    return style


def first_child_div(txt: str, after_idx: int) -> str:
    """Return the first `<div ...>` opening tag located after after_idx, or ''."""
    m = re.search(r"<div\b[^>]*>", txt[after_idx:])
    return m.group(0) if m else ""


def scan_file(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    hits = []

    # locate .scene-content wrapper(s): inline styles + a CSS rule
    inline = []  # (start_idx, end_idx, opening_tag)
    for m in re.finditer(r'<div[^>]*class="[^"]*\bscene-content\b[^"]*"[^>]*>', txt):
        inline.append((m.start(), m.end(), m.group(0)))
    css_rule = css_rule_for_class(txt, "scene-content")

    if not inline and not css_rule:
        return hits  # no scene-content wrapper in this file → skip

    # combined scene-content style (inline of first wrapper + its CSS rule)
    sc_inline_style = ""
    if inline:
        sm = re.search(r'style="([^"]*)"', inline[0][2])
        sc_inline_style = sm.group(1) if sm else ""
    sc_style = sc_inline_style + " ; " + css_rule

    fills = establishes_height(sc_style)
    centers = establishes_centering(sc_style)
    relies_full_h = bool(re.search(r"height\s*:\s*100%", txt))

    # first content child of .scene-content — does it fill/center itself?
    child_fills = child_centers = False
    if inline:
        child_tag = first_child_div(txt, inline[0][1])
        if child_tag:
            child_style = combined_style_for_div(txt, child_tag)
            child_fills = establishes_height(child_style)
            child_centers = establishes_centering(child_style)

    idx = inline[0][0] if inline else 0
    line = line_of(txt, idx)

    # (1) Legacy failure: no definite height at all, but the scene relies on height:100% inside.
    if not fills and relies_full_h:
        hits.append((line,
                     "`.scene-content` has no definite height but the scene uses height:100% inside"))
        return hits

    # (2) Main failure: wrapper fills the frame but content is NOT centered and does NOT
    #     fill the height itself → the panel collapses to its content and piles at the TOP.
    if fills and not centers and not (child_fills or child_centers):
        hits.append((line,
                     "`.scene-content` fills the frame but is not a centering flex/grid "
                     "container, and its content wrapper has no height:100% → content will "
                     "pile at the TOP (bottom half empty). Add display:flex;align-items:center;"
                     "justify-content:center to .scene-content."))
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
        print(f"\nFAIL: {total} scene(s) will not vertically center → content piles at the top "
              "(bottom empty), or height:auto SVGs collapse.")
        print("FIX: make the wrapper a CENTERING container that fills the frame:")
        print("       .scene-content { position:absolute; inset:0;")
        print("                        display:flex; align-items:center; justify-content:center;")
        print("                        padding:40px 60px 180px; box-sizing:border-box; }")
        print("     (or give the content wrapper height:100% so it fills the frame itself).")
        return 1

    print(f"OK: every scene centers/fills its content across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
