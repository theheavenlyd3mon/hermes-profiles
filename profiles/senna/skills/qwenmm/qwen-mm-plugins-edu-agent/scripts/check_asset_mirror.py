#!/usr/bin/env python3
"""
check_asset_mirror.py — verify that GSAP, KaTeX, and fonts are mirrored into dist/compositions/.

Sub-composition HTML files live in dist/compositions/ and use relative paths like
./gsap/gsap.min.js, ./katex/katex.min.js, url(./assets/fonts/...).  These resolve
relative to the composition's own directory, NOT dist/.  Without the mirror, GSAP
fails to load silently → all animations break → elements set to autoAlpha:0 in
fromTo() stay invisible → blank scenes with only the background visible.

Usage:  python3 check_asset_mirror.py dist
Exit 0 = mirror verified.  Exit 1 = missing files (DO NOT render).
"""

import sys
from pathlib import Path

REQUIRED = [
    "compositions/gsap/gsap.min.js",
    "compositions/katex/katex.min.js",
    "compositions/assets/fonts/NotoSansSC-Bold.woff2",
]


def main() -> int:
    dist = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist")
    missing = []
    for rel in REQUIRED:
        p = dist / rel
        if not p.exists():
            missing.append(str(p))

    if missing:
        print(f"FAIL: asset mirror missing in compositions/ — GSAP/KaTeX/fonts will not load in sub-compositions.")
        print(f"  Fix: copy assets into compositions/ directory:")
        print(f"    cp -r {dist}/gsap {dist}/compositions/gsap")
        print(f"    cp -r {dist}/katex {dist}/compositions/katex")
        print(f"    cp -r {dist}/assets {dist}/compositions/assets")
        print(f"  Missing files:")
        for m in missing:
            print(f"    {m}")
        return 1

    print("Asset mirror OK — GSAP, KaTeX, and fonts available in compositions/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
