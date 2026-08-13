#!/usr/bin/env python3
r"""
check_no_hidden_content.py — Pre-render gate: fail if CSS statically hides content.

WHY (reproducibility): the #1 cause of blank/half-empty scenes is a CSS rule like
`opacity: 0` or `visibility: hidden` on a content element, meant to be revealed by
GSAP. When the timeline has any error (or the element is never targeted), the content
stays permanently invisible → a scene whose narration plays over an EMPTY canvas.
This is run-to-run flaky: sometimes the reveal fires, sometimes it doesn't.

RULE (see SKILL.md rule #18): never set the initial hidden state in CSS. Let GSAP
handle it dynamically via `autoAlpha: 0` in a `fromTo()` "from" value (that lives in
JS, not CSS, so this gate does not flag it).

This gate scans ONLY the contents of `<style>` blocks (CSS), so JS `autoAlpha:0` /
`gsap.fromTo(...)` are never flagged. It flags `opacity: 0` and `visibility: hidden`.
`display:none` is intentionally NOT flagged (it is mandated for `.katex-mathml`).

Usage:
    python3 check_no_hidden_content.py [dist_dir]    # default ./dist
Exit 0 = clean, 1 = static-hidden content found (or no HTML found).
"""

import re
import sys
from pathlib import Path

from _shared import iter_compositions, line_of

RE_STYLE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.I | re.S)
RE_OPACITY0 = re.compile(r"opacity\s*:\s*0(?![.\d])\s*(?:!important)?\s*;", re.I)
RE_VIS_HIDDEN = re.compile(r"visibility\s*:\s*hidden", re.I)


def scan_file(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for sm in RE_STYLE.finditer(txt):
        css = sm.group(1)
        base = sm.start(1)
        for m in RE_OPACITY0.finditer(css):
            hits.append((line_of(txt, base + m.start()),
                         "CSS `opacity: 0` on a content element (use GSAP `autoAlpha:0` in JS instead)"))
        for m in RE_VIS_HIDDEN.finditer(css):
            hits.append((line_of(txt, base + m.start()),
                         "CSS `visibility: hidden` on a content element (use GSAP `autoAlpha:0` in JS instead)"))
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
        print(f"\nFAIL: {total} CSS rule(s) statically hide content → if any GSAP tween errors, "
              "the scene plays over an EMPTY canvas (flaky blank scenes).")
        print("FIX: remove `opacity:0` / `visibility:hidden` from CSS. Hide via GSAP only:")
        print('       tl.fromTo(el, {autoAlpha:0, y:30}, {autoAlpha:1, y:0, duration:0.6});')
        print("     and wrap the whole timeline build in try/catch so content stays visible on error.")
        return 1

    print(f"OK: no statically-hidden content across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
