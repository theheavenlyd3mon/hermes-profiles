#!/usr/bin/env python3
r"""
check_caption_position.py — Pre-render gate: force the caption to be pinned to the
BOTTOM of the frame. Fixes the symptom "有的字幕在最上方，有的在中部遮挡内容":
captions drifting to the top or middle instead of a consistent bottom bar.

ROOT CAUSES this catches:
  (A) A caption element (class contains "caption") lives INSIDE a scene composition
      (compositions/*.html) instead of the index.html root track. Inside a scene it
      inherits that scene's positioning/stacking context, so it lands wherever the
      scene flexbox puts it — top or middle — and differs scene to scene.
  (B) The caption CSS is not absolutely/fixed positioned → it flows in normal document
      order and renders at the TOP of the frame.
  (C) The caption CSS anchors with `top:` (or has no `bottom:`) → it sits at the top or
      middle instead of the bottom.

RULE (see design-system.md "Caption Style" and step-6):
  - Captions are a ROOT-LEVEL track in index.html ONLY — never inside a scene composition.
  - The caption rule MUST be `position: absolute` (or `fixed`), anchored with `bottom:`
    (e.g. `bottom: 48px`), and MUST NOT use `top:` (top pulls it up / to the middle).

Usage:
    python3 check_caption_position.py [dist_dir]     # default ./dist
Exit 0 = clean, 1 = a caption is not pinned to the bottom (or no HTML found).
"""

import re
import sys
from pathlib import Path

from _shared import line_of

RE_RULE = re.compile(r"(?P<sel>[^{}]+)\{(?P<body>[^{}]*)\}", re.S)
RE_CAPTION_EL = re.compile(r"""<[^>]*class\s*=\s*(['"])[^'"]*caption[^'"]*\1""", re.I)
RE_POS_ABS = re.compile(r"position\s*:\s*(absolute|fixed)", re.I)
RE_BOTTOM = re.compile(r"(?<![-\w])bottom\s*:\s*(-?\d+(?:\.\d+)?)(px|%|em|rem|vh)", re.I)
# `top:` with a real value (ignore `top:auto`)
RE_TOP = re.compile(r"(?<![-\w])top\s*:\s*(?!auto)(-?\d+(?:\.\d+)?)(px|%|em|rem|vh)", re.I)


def caption_rules(txt: str):
    """yield (start_idx, selector, body) for CSS rules whose selector mentions caption."""
    for m in RE_RULE.finditer(txt):
        sel = m.group("sel")
        if "caption" in sel.lower():
            yield m.start(), sel.strip(), m.group("body")


def main() -> int:
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    if not dist.is_dir():
        print(f"ERROR: dist dir not found: {dist}", file=sys.stderr)
        return 1

    index = dist / "index.html"
    comps = sorted(dist.glob("compositions/*.html"))
    if not index.exists() and not comps:
        print(f"ERROR: no index.html / compositions/*.html under {dist}", file=sys.stderr)
        return 1

    hits = []

    # (A) caption elements must NOT appear inside a scene composition
    for c in comps:
        txt = c.read_text(encoding="utf-8", errors="replace")
        for m in RE_CAPTION_EL.finditer(txt):
            hits.append((c, line_of(txt, m.start()),
                         "caption element inside a scene composition — captions must live only in "
                         "index.html's root track (inside a scene they land top/middle, not bottom)"))
        # a `.caption*` positioning rule inside a composition is equally wrong
        for idx, sel, body in caption_rules(txt):
            if RE_POS_ABS.search(body) or RE_TOP.search(body) or RE_BOTTOM.search(body):
                hits.append((c, line_of(txt, idx),
                             f"caption CSS rule `{sel[:40]}` inside a scene composition — move it to index.html"))

    # (B)/(C) in index.html: caption must be absolute/fixed + bottom-anchored + no top
    if index.exists():
        txt = index.read_text(encoding="utf-8", errors="replace")
        rules = list(caption_rules(txt))
        has_caption_el = bool(RE_CAPTION_EL.search(txt)) or bool(rules)
        if has_caption_el:
            any_abs = any(RE_POS_ABS.search(b) for _, _, b in rules)
            any_bottom = any(RE_BOTTOM.search(b) for _, _, b in rules)
            for idx, sel, body in rules:
                mt = RE_TOP.search(body)
                if mt:
                    hits.append((index, line_of(txt, idx),
                                 f"caption rule `{sel[:40]}` uses `top:{mt.group(1)}{mt.group(2)}` "
                                 "→ caption sits at top/middle; anchor with `bottom:` and remove `top:`"))
            if not any_abs:
                base = rules[0][0] if rules else 0
                hits.append((index, line_of(txt, base),
                             "no caption rule is `position:absolute`/`fixed` → caption flows to the TOP; "
                             "add `position:absolute; bottom:48px; left:50%; transform:translateX(-50%)`"))
            if not any_bottom:
                base = rules[0][0] if rules else 0
                hits.append((index, line_of(txt, base),
                             "no caption rule sets `bottom:` → caption is not pinned to the bottom; "
                             "add `bottom:48px` (and do not use `top:`)"))

    if hits:
        for f, line, msg in hits:
            print(f"{f}:{line}: {msg}")
        print(f"\nFAIL: {len(hits)} caption-position issue(s) → the subtitle is not fixed at the bottom "
              "(有的字幕在最上方/中部遮挡内容).")
        print("FIX: put ALL caption bars in index.html's root track (data-track-index=\"2\"), and style them")
        print("     `position:absolute; bottom:48px; left:50%; transform:translateX(-50%);` — never `top:`,")
        print("     never inside a scene composition.")
        return 1

    print("OK: caption is pinned to the bottom (absolute + bottom, root-level only).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
