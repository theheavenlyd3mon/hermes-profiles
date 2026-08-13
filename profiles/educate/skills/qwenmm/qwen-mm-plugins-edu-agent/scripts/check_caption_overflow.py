#!/usr/bin/env python3
r"""
check_caption_overflow.py — Pre-render gate: fail if captions can run off the frame edge.

WHY: The bottom subtitle sometimes overflows the left/right video boundary and gets
clipped (字幕超出画面边界). Root cause: a caption bar styled `white-space:nowrap` with no
`max-width`, centered via translateX(-50%) — a long single line grows past both edges.
Fix = cap the width and wrap (balanced) as a safety net, AND keep each cue short
(split long sentences into sequential one-line cues; see step-6 caption rules).

Checks (scan index.html + compositions/*.html):
  1. Any CSS rule / inline style on a caption element with `white-space:nowrap`.        [FAIL]
  2. A caption bar rule with NO `max-width` (<= 1728px) — nothing bounds its width.      [FAIL]
  3. A caption cue whose visible text is very long (> MAX_CHARS) → split it into
     shorter sequential cues (formulas in <span class="cm"> are excluded from the count). [FAIL]

Usage:
    python3 check_caption_overflow.py [dist_dir] [max_chars]   # defaults: ./dist 60
Exit 0 = clean, 1 = an overflow risk found.
"""

import re
import sys
from pathlib import Path

from _shared import iter_compositions, line_of

DEFAULT_MAX_CHARS = 60          # hard ceiling; step-6 recommends <= ~22 (one line) for aesthetics
MAX_MAXWIDTH = 1728             # 90% of 1920 — a caption max-width must be <= this to stay on-frame

RE_NOWRAP = re.compile(r"white-space\s*:\s*nowrap", re.I)
RE_MAXW = re.compile(r"max-width\s*:\s*(\d+(?:\.\d+)?)px", re.I)
RE_ZINDEX = re.compile(r"z-index\s*:\s*(\d+)", re.I)
MIN_Z = 1000            # caption must sit above every scene layer
RE_LEFT50 = re.compile(r"left\s*:\s*50%", re.I)
RE_TRANSLATE = re.compile(r"transform\s*:[^;]*translate[xX]?\s*\(\s*-?50%", re.I)
RE_WIDTH_INTRINSIC = re.compile(r"width\s*:\s*(?:max-content|fit-content)", re.I)
RE_CM = re.compile(r'<span[^>]*class="[^"]*\bcm\b[^"]*"[^>]*>.*?</span>', re.I | re.S)
RE_TAG = re.compile(r"<[^>]+>")


def scan_file(path: Path, max_chars: int):
    txt = path.read_text(encoding="utf-8", errors="replace")
    hits = []

    # --- CSS rules whose selector mentions "caption" (allows `.caption {` with spaces) ---
    for m in re.finditer(r"([^{}]*caption[^{}]*)\{([^}]*)\}", txt, re.I):
        body = m.group(2)
        ln = line_of(txt, m.start())
        if RE_NOWRAP.search(body):
            hits.append((ln, "caption CSS uses `white-space:nowrap` → long lines run off-frame; "
                             "use `white-space:normal` + `max-width` (wrap as safety net)"))
        # only the main caption bar rule needs a max-width (skip tiny helper rules like `.caption .katex`)
        if "position" in body and "absolute" in body and not RE_MAXW.search(body):
            hits.append((ln, "caption bar CSS has no `max-width` → nothing bounds its width; "
                             "add `max-width:1600px` so it never bleeds past the frame edge"))
        mw = RE_MAXW.search(body)
        if mw and float(mw.group(1)) > MAX_MAXWIDTH:
            hits.append((ln, f"caption `max-width:{mw.group(1)}px` is wider than the safe area "
                             f"(<= {MAX_MAXWIDTH}px on a 1920 frame)"))
        # centered via left:50%+translateX but no intrinsic width → shrink-to-fits to the ~960px
        # half-frame and wraps even SHORT captions (the max-width is never reached)
        if RE_LEFT50.search(body) and RE_TRANSLATE.search(body) and not RE_WIDTH_INTRINSIC.search(body):
            hits.append((ln, "caption centered with `left:50%`+`translateX(-50%)` but no `width:max-content` "
                             "→ it shrink-to-fits to the ~960px half-frame and wraps even short captions; "
                             "add `width:max-content` (keeps it one line up to max-width)"))
        # caption MUST be topmost — an abs-pos caption bar with no / low z-index gets covered by scenes
        if "position" in body and "absolute" in body:
            zm = RE_ZINDEX.search(body)
            if not zm or int(zm.group(1)) < MIN_Z:
                shown = "no z-index" if not zm else f"z-index:{zm.group(1)}"
                hits.append((ln, f"caption bar has {shown} → a scene panel can paint OVER it (字幕被遮挡). "
                                 f"Set a very high z-index (e.g. `z-index:2147483647`) so the caption is "
                                 f"ALWAYS on top of every scene layer."))

    # --- inline nowrap on caption elements ---
    for m in re.finditer(r'<[^>]*class="[^"]*caption[^"]*"[^>]*style="([^"]*)"[^>]*>', txt, re.I):
        if RE_NOWRAP.search(m.group(1)):
            hits.append((line_of(txt, m.start()),
                         "inline `white-space:nowrap` on a caption element → remove it"))

    # --- over-long caption cues ---
    for m in re.finditer(r'<div[^>]*class="[^"]*caption[^"]*"[^>]*>(.*?)</div>', txt, re.I | re.S):
        inner = RE_CM.sub("公式", m.group(1))     # formula spans render compact → count as ~2 chars
        visible = RE_TAG.sub("", inner)
        visible = re.sub(r"\s+", "", visible)
        if len(visible) > max_chars:
            hits.append((line_of(txt, m.start()),
                         f"caption cue is {len(visible)} chars (> {max_chars}) → split it into shorter "
                         f"sequential one-line cues (recommend <= 22 chars/cue). Text: {visible[:30]}…"))
    return hits


def main() -> int:
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    max_chars = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_MAX_CHARS
    if not dist.is_dir():
        print(f"ERROR: dist dir not found: {dist}", file=sys.stderr)
        return 1
    files = iter_compositions(dist)
    if not files:
        print(f"ERROR: no index.html / compositions/*.html under {dist}", file=sys.stderr)
        return 1

    total = 0
    for f in files:
        for line, msg in scan_file(f, max_chars):
            total += 1
            print(f"{f}:{line}: {msg}")

    if total:
        print(f"\nFAIL: {total} caption overflow risk(s) → the subtitle can run off the frame edge.")
        print("FIX: caption bar = `max-width:1600px; white-space:normal; text-wrap:balance;` (never nowrap), "
              "and split long sentences into short sequential one-line cues (see step-6).")
        return 1

    print(f"OK: captions are width-bounded and short enough across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
