#!/usr/bin/env python3
r"""
check_katex_cjk.py — Pre-render gate: fail if any KaTeX input contains a CJK
(Chinese/Japanese/Korean) character.

WHY: KaTeX renders math with its own math fonts (KaTeX_Main / KaTeX_Math / …),
which contain NO CJK glyphs. Any Chinese character fed into KaTeX — most commonly
a unit inside \text{} such as 50\,\text{秒} — renders as a □ tofu box, even when
the page's Noto Sans SC font is correctly installed. Latin units (\text{s},
\text{m/s}) are fine; Chinese units are not.

This script scans every composition + index.html under a dist/ directory for KaTeX
inputs and reports any that contain CJK, exiting non-zero so the pipeline blocks
the render until it is fixed (move the Chinese unit OUT of KaTeX into plain HTML,
e.g.  需要 <span data-tex="50"></span> 秒).

Usage:
    python3 check_katex_cjk.py [dist_dir]        # default: ./dist
Exit code 0 = clean, 1 = CJK-in-KaTeX found (or no HTML found).
"""

import re
import sys
from pathlib import Path

from _shared import iter_compositions, line_of

# CJK / CJK-punctuation / fullwidth ranges — the glyphs KaTeX math fonts lack.
CJK = re.compile(
    "["
    "　-〿"   # CJK symbols & punctuation （。、「」 …）
    "㐀-䶿"   # CJK Ext A
    "一-鿿"   # CJK Unified (中文常用字)
    "豈-﫿"   # CJK compatibility ideographs
    "＀-￯"   # fullwidth forms （Ａ１，：…）
    "぀-ヿ"   # Hiragana/Katakana
    "가-힯"   # Hangul
    "]"
)

# KaTeX inputs: data-tex="..." / data-tex='...'  AND  katex.render("...", / katex.render('...',
RE_DATA_TEX = re.compile(r"""data-tex\s*=\s*(?P<q>["'])(?P<v>.*?)(?P=q)""", re.S)
RE_KATEX_RENDER = re.compile(r"""katex\.render\s*\(\s*(?P<q>["'`])(?P<v>.*?)(?P=q)""", re.S)


def scan_file(path: Path):
    """Return list of (line, kind, snippet, offending_chars)."""
    txt = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for kind, rx in (("data-tex", RE_DATA_TEX), ("katex.render", RE_KATEX_RENDER)):
        for m in rx.finditer(txt):
            val = m.group("v")
            bad = "".join(sorted(set(CJK.findall(val))))
            if bad:
                hits.append((line_of(txt, m.start()), kind, val.strip()[:80], bad))
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
        hits = scan_file(f)
        for line, kind, snippet, bad in hits:
            total += 1
            print(f"{f}:{line}: CJK {bad!r} inside KaTeX ({kind}): {snippet!r}")

    if total:
        print(f"\nFAIL: {total} KaTeX input(s) contain CJK characters → they render as □ tofu boxes.")
        print("FIX: move the Chinese unit/text OUT of KaTeX into plain HTML.")
        print('  bad : <span data-tex="50\\\\,\\\\text{秒}"></span>')
        print('  good: 需要 <span data-tex="50"></span> 秒')
        print('  (or keep a Latin unit inside KaTeX: data-tex="50\\\\,\\\\text{s}")')
        return 1

    print(f"OK: no CJK inside KaTeX across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
