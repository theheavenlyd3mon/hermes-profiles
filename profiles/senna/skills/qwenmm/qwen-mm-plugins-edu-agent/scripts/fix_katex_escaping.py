#!/usr/bin/env python3
r"""
fix_katex_escaping.py — AUTO-FIX: double-escape every single backslash inside
katex.render("…") JS strings and tex:/latex:/formula:/math: JS property values.

This is the **automatic repair** companion to check_katex_escaping.py (which only
detects). Run this BEFORE precheck.py — it rewrites the offending files in-place
so that check_katex_escaping.py passes cleanly afterward.

WHY: The #1 rendering defect in math-tutorial videos is `\dfrac` / `\frac` written
with a single backslash in a JS string. JS silently eats the backslash:
  "\dfrac{1}{2}"  →  JS sees \d as literal 'd'  →  KaTeX gets "dfrac{1}{2}"
  "\frac{a}{b}"   →  JS sees \f as form-feed     →  KaTeX gets "rac{a}{b}"
  "\times"        →  JS sees \t as tab            →  KaTeX gets "imes"
The fix is trivial: replace every `\X` with `\\X` inside the JS string.

This does NOT touch LaTeX in HTML attributes (data-tex="…") or <span class="cm">
content — those are correct with single backslashes.

Usage:
    python3 fix_katex_escaping.py [dist_dir]      # default ./dist

Exit 0 = success (files fixed or already clean). Exit 1 = dist dir not found.
"""

import re
import sys
from pathlib import Path

from _shared import iter_compositions

# Match katex.render("...") — capture the full call so we can replace in-place
RE_RENDER = re.compile(
    r"""(katex\.render\s*\(\s*)(?P<q>["'])(?P<v>(?:\\.|[^\\])*?)(?P=q)""", re.S
)
# Match tex:"..." / latex:"..." / formula:"..." etc.
RE_PROP = re.compile(
    r"""(\b(?:tex|latex|formula|math|expr|eq)\s*:\s*)(?P<q>["'])(?P<v>(?:\\.|[^\\])*?)(?P=q)""",
    re.S,
)
# A lone backslash before a letter (not already doubled)
RE_LONE = re.compile(r"(?<!\\)\\(?=[a-zA-Z])")


def fix_value(m: re.Match) -> str:
    """Double every lone backslash in the captured LaTeX string value."""
    prefix = m.group(1)      # everything before the opening quote
    q = m.group("q")         # the quote character (' or ")
    val = m.group("v")       # the string content
    fixed = RE_LONE.sub(r"\\\\", val)
    return f"{prefix}{q}{fixed}{q}"


def fix_file(path: Path) -> int:
    """Fix all single-backslash LaTeX in JS strings. Returns number of fixes."""
    original = path.read_text(encoding="utf-8", errors="replace")
    text = original

    count = 0
    for rx in (RE_RENDER, RE_PROP):
        new_text = []
        last_end = 0
        for m in rx.finditer(text):
            val = m.group("v")
            if RE_LONE.search(val):
                new_text.append(text[last_end:m.start()])
                new_text.append(fix_value(m))
                last_end = m.end()
                count += 1
        if new_text:
            new_text.append(text[last_end:])
            text = "".join(new_text)

    if text != original:
        path.write_text(text, encoding="utf-8")

    return count


def main() -> int:
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    if not dist.is_dir():
        print(f"ERROR: dist dir not found: {dist}", file=sys.stderr)
        return 1

    files = iter_compositions(dist)
    if not files:
        print(f"WARNING: no index.html / compositions/*.html under {dist}")
        return 0

    total_fixes = 0
    for f in files:
        n = fix_file(f)
        if n:
            print(f"FIXED {n} LaTeX string(s) in {f}")
            total_fixes += n

    if total_fixes:
        print(f"\nAuto-fixed {total_fixes} single-backslash LaTeX string(s) across {len(files)} file(s).")
        print("All \\dfrac, \\frac, \\times, etc. are now properly double-escaped.")
    else:
        print(f"OK: all {len(files)} file(s) already have correct double-escaped LaTeX.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
