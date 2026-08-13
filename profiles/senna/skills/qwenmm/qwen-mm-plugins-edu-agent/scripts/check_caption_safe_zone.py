#!/usr/bin/env python3
r"""
check_caption_safe_zone.py — Pre-render gate: fail if a scene does not reserve the
bottom caption safe zone, so the subtitle would cover scene content (字幕遮挡画面).

WHY: The caption bar sits in the bottom band of the 1920x1080 frame (~bottom 48px + up to
two 38px lines). If a scene lays its content across the full 1080px height (the default
`.scene-content { height:100% }` with only side/top padding), the content extends UNDER the
caption bar and the subtitle covers it. The fix is to reserve the bottom ~180px: content is
flex-centered in the top ~900px and floats above the caption.

This scans each scene composition's `.scene-content` (CSS rule + inline styles) and checks
that it reserves at least MIN_SAFE px at the bottom, via any of:
  - padding-bottom: >=MIN px
  - padding shorthand whose BOTTOM value is >=MIN px   (1/2 vals → 1st; 3/4 vals → 3rd)
  - height: calc(100% - >=MIN px)
  - a var(--caption-safe...) reference (assumed correct)

Scenes with no `.scene-content` are skipped (can't reason about their layout).

Usage:
    python3 check_caption_safe_zone.py [dist_dir] [min_px]   # defaults: ./dist 140
Exit 0 = clean, 1 = a scene does not reserve the caption safe zone (or no HTML found).
"""

import re
import sys
from pathlib import Path

from _shared import line_of

DEFAULT_MIN_PX = 140      # recommend 180; 140 leaves tolerance before failing
RECOMMEND = 180

RE_PAD_BOTTOM = re.compile(r"padding-bottom\s*:\s*(\d+(?:\.\d+)?)px", re.I)
# shorthand `padding:` only — `padding-bottom:` has a '-' before ':' so it won't match here
RE_PAD_SHORT = re.compile(r"(?<![-\w])padding\s*:\s*([^;{}]+)", re.I)
RE_CALC = re.compile(r"height\s*:\s*calc\(\s*100%\s*-\s*(\d+(?:\.\d+)?)px", re.I)
RE_VAR = re.compile(r"--caption-safe|var\(\s*--caption-safe", re.I)
RE_PX = re.compile(r"^(\d+(?:\.\d+)?)px$", re.I)


def _shorthand_bottom_px(value: str):
    toks = value.strip().split()
    if not toks:
        return None
    idx = 0 if len(toks) < 3 else 2      # bottom is 1st (1-2 vals) or 3rd (3-4 vals)
    if idx >= len(toks):
        return None
    m = RE_PX.match(toks[idx])
    return float(m.group(1)) if m else None


def reserved_px(style: str) -> float:
    """Largest bottom reservation the style establishes (0 = none). var() → treated as satisfied."""
    if RE_VAR.search(style):
        return float("inf")
    cands = [0.0]
    m = RE_PAD_BOTTOM.search(style)
    if m:
        cands.append(float(m.group(1)))
    for sm in RE_PAD_SHORT.finditer(style):
        b = _shorthand_bottom_px(sm.group(1))
        if b is not None:
            cands.append(b)
    cm = RE_CALC.search(style)
    if cm:
        cands.append(float(cm.group(1)))
    return max(cands)


def scan_file(path: Path, min_px: float):
    txt = path.read_text(encoding="utf-8", errors="replace")
    hits = []

    # CSS rule body for .scene-content
    css_bodies = [m.group(1) for m in re.finditer(r"\.scene-content\s*\{([^}]*)\}", txt)]
    # inline styles on scene-content elements
    inline = []
    for m in re.finditer(r'<div[^>]*class="[^"]*\bscene-content\b[^"]*"[^>]*>', txt):
        sm = re.search(r'style="([^"]*)"', m.group(0))
        inline.append((m.start(), sm.group(1) if sm else ""))

    if not css_bodies and not inline:
        return hits  # no scene-content wrapper → skip

    best = 0.0
    for b in css_bodies:
        best = max(best, reserved_px(b))
    for _, s in inline:
        best = max(best, reserved_px(s))

    if best < min_px:
        cm = re.search(r"\.scene-content\s*\{", txt)
        idx = cm.start() if cm else (inline[0][0] if inline else 0)
        shown = "no bottom reserve" if best == 0 else f"only {best:g}px reserved"
        hits.append((line_of(txt, idx),
                     f"`.scene-content` does not reserve the caption safe zone ({shown}; need >= {min_px:g}px)"))
    return hits


def main() -> int:
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    min_px = float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_MIN_PX
    if not dist.is_dir():
        print(f"ERROR: dist dir not found: {dist}", file=sys.stderr)
        return 1

    files = sorted(dist.glob("compositions/*.html"))
    if not files:
        print(f"ERROR: no compositions/*.html under {dist}", file=sys.stderr)
        return 1

    total = 0
    for f in files:
        for line, msg in scan_file(f, min_px):
            total += 1
            print(f"{f}:{line}: {msg}")

    if total:
        print(f"\nFAIL: {total} scene(s) do not reserve the bottom caption safe zone → "
              "the subtitle bar will cover scene content (字幕遮挡画面).")
        print(f"FIX: reserve the bottom {RECOMMEND}px so content floats in the top ~900px, e.g.")
        print("       .scene-content { width:100%; height:100%; box-sizing:border-box;")
        print(f"                        padding: 40px 60px {RECOMMEND}px; }}")
        print("     (keep height:100% for vertical centering; border-box makes the padding")
        print("      subtract from the 1080px box so content ends ~y900, clear of the caption.)")
        return 1

    print(f"OK: every scene reserves the caption safe zone (>= {min_px:g}px) across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
