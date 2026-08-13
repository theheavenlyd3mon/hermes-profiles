#!/usr/bin/env python3
r"""
check_katex_escaping.py — Pre-render gate: fail if LaTeX inside a JS string literal
uses a single backslash instead of a double backslash.

WHY: In a JavaScript (or Python) string, a backslash starts an escape sequence, so
"4 \times 3" becomes  4 <TAB>imes 3  (\t = tab), "x \neq y" becomes  x <newline>eq y,
"\frac{a}{b}" becomes <form-feed>rac{a}{b}, etc. KaTeX then receives mangled input and
renders "imes" / "eq" / "rac" instead of × / ≠ / a fraction. LaTeX passed to
katex.render(...) or stored in a JS object field (tex:/latex:/formula:/math:) MUST
double-escape every backslash:  "4 \\times 3".

NOTE: this is ONLY a problem inside JS/Python string literals. LaTeX written in HTML —
`data-tex="4\times3"` or `<span class="cm">4\times 3</span>` — is correct with a SINGLE
backslash (HTML does not treat \t as an escape), so those are NOT flagged.

The script scans index.html + compositions/*.html for KaTeX-input JS strings and flags
any lone backslash (`\x` not written as `\\x`) before a letter.

Usage:
    python3 check_katex_escaping.py [dist_dir]      # default ./dist
Exit 0 = clean, 1 = single-backslash LaTeX in a JS string (or no HTML found).
"""

import re
import sys
from pathlib import Path

from _shared import iter_compositions, line_of

# KaTeX-input JS strings:
#   katex.render("...")            -> first string arg
#   tex:"..." / latex:"..." / formula:"..." / math:"..." / expr:"..." / eq:"..."
RE_RENDER = re.compile(r"""katex\.render\s*\(\s*(?P<q>["'])(?P<v>(?:\\.|[^\\])*?)(?P=q)""", re.S)
RE_PROP = re.compile(
    r"""\b(?:tex|latex|formula|math|expr|eq)\s*:\s*(?P<q>["'])(?P<v>(?:\\.|[^\\])*?)(?P=q)""",
    re.S,
)
# A lone backslash before a letter (i.e. NOT written as \\letter) — the bug.
RE_LONE = re.compile(r"(?<!\\)\\[a-zA-Z]")


def scan_file(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for kind, rx in (("katex.render", RE_RENDER), ("tex:/latex: field", RE_PROP)):
        for m in rx.finditer(txt):
            val = m.group("v")
            if RE_LONE.search(val):
                # collect the offending sequences for a clearer message
                bad = sorted(set(re.findall(r"(?<!\\)\\[a-zA-Z]+", val)))
                hits.append((line_of(txt, m.start()), kind, val.strip()[:70], bad))
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
        for line, kind, snippet, bad in scan_file(f):
            total += 1
            print(f"{f}:{line}: single-backslash LaTeX in JS string ({kind}): {bad} in {snippet!r}")

    if total:
        print(f"\nFAIL: {total} KaTeX JS string(s) use a single backslash → JS eats the escape "
              r"and KaTeX renders garbage text instead of math formulas.")
        print(r"")
        print(r"COMMON CASES (all silent — no JS error, just wrong rendering):")
        print(r'  \dfrac{1}{2}  → JS sees \d as literal d   → KaTeX gets "dfrac{1}{2}" → renders italic "dfrac12"')
        print(r'  \frac{a}{b}   → JS sees \f as form-feed   → KaTeX gets "rac{a}{b}"   → renders "rac"')
        print(r'  \times        → JS sees \t as tab          → KaTeX gets "imes"         → renders "imes"')
        print(r'  \neq          → JS sees \n as newline      → KaTeX gets "eq"           → renders "eq"')
        print(r"")
        print(r'FIX: double every backslash in JS/Python strings:')
        print(r'  WRONG: katex.render("\dfrac{1}{4}", el)')
        print(r'  RIGHT: katex.render("\\dfrac{1}{4}", el)')
        print(r'     (LaTeX in HTML data-tex="4\times3" stays single-backslash — that is correct.)')
        return 1

    print(f"OK: no single-backslash LaTeX in JS strings across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
