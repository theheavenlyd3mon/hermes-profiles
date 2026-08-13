#!/usr/bin/env python3
r"""
check_no_glass.py — Pre-render gate: forbid frosted glass / translucent occluding panels.

WHY (完全避免遮挡): a panel with `backdrop-filter: blur(...)` (frosted glass) or a near-white
see-through background (e.g. `rgba(255,255,255,0.55)`) blurs/washes out everything behind it,
producing a big translucent block that OCCLUDES the problem text, diagram, or formulas. This is
the failure seen in sample 391ada. This design system is OPAQUE-ONLY: depth comes from borders +
layered box-shadow, never from blur or transparency.

Flags (scans index.html + compositions/*.html):
  1. ANY `backdrop-filter` / `-webkit-backdrop-filter` (zero tolerance).                 [FAIL]
  2. A near-white background `rgba(R,G,B,a)` with R,G,B >= 235 and alpha < 0.92          [FAIL]
     (a see-through white panel). Use `#ffffff` (or alpha >= 0.92) instead.

NOTE: decorative non-white tints (colored aurora orbs `rgba(99,102,241,0.5)`), and white used in
box-shadow / border (not `background`) are NOT flagged — only see-through WHITE panel backgrounds.

Usage:
    python3 check_no_glass.py [dist_dir]    # default ./dist
Exit 0 = clean, 1 = frosted glass / translucent panel found (or no HTML found).
"""

import re
import sys
from pathlib import Path

from _shared import iter_compositions, line_of

ALPHA_MIN = 0.92
WHITEISH = 235
RE_BACKDROP = re.compile(r"(?:-webkit-)?backdrop-filter\s*:\s*[^;\"'}]*", re.I)
RE_BG = re.compile(r"background(?:-color)?\s*:\s*([^;\"'}]*)", re.I)
RE_RGBA = re.compile(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9]*\.?[0-9]+)\s*\)", re.I)


def scan_file(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for m in RE_BACKDROP.finditer(txt):
        if "blur" in m.group(0).lower() or "px" in m.group(0).lower():
            hits.append((line_of(txt, m.start()),
                         "backdrop-filter (frosted glass — blurs/occludes content behind the panel)",
                         m.group(0).strip()[:60]))
    for m in RE_BG.finditer(txt):
        for c in RE_RGBA.finditer(m.group(1)):
            r, g, b, a = int(c.group(1)), int(c.group(2)), int(c.group(3)), float(c.group(4))
            if r >= WHITEISH and g >= WHITEISH and b >= WHITEISH and a < ALPHA_MIN:
                hits.append((line_of(txt, m.start()),
                             f"see-through white panel background (alpha {a} < {ALPHA_MIN})",
                             c.group(0)))
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
        for line, msg, snippet in scan_file(f):
            total += 1
            print(f"{f}:{line}: {msg}  ->  {snippet}")

    if total:
        print(f"\nFAIL: {total} frosted-glass / see-through-panel use(s) → a blurred/washed-out block "
              "occludes the content. Content panels MUST be OPAQUE.")
        print("FIX: remove every `backdrop-filter`; set panel `background:#ffffff` (or white alpha >= 0.92). "
              "Get the premium look from border + layered box-shadow, never blur/transparency.")
        return 1

    print(f"OK: no frosted glass / see-through panels across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
