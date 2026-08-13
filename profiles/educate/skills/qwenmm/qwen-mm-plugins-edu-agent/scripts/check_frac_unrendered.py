#!/usr/bin/env python3
r"""
check_frac_unrendered.py — Pre-render gate: detect literal "dfrac", "tfrac", "frac{"
text in HTML body content that should have been rendered by KaTeX but wasn't.

WHY: When KaTeX fails to render a fraction (e.g. due to missing JS, wrong escaping,
or KaTeX load failure), the raw LaTeX command leaks into the visible HTML as plain
italic text like "dfrac12" or "rac{a}{b}". This check catches those leaked fragments
BEFORE rendering to video, so the fraction can be fixed.

WHAT IT SCANS: All text content inside HTML elements (outside of <script>, <style>,
and HTML attributes). It looks for patterns that indicate an unrendered fraction:
  - "dfrac"  (from \dfrac where \d was eaten by JS)
  - "tfrac"  (from \tfrac where \t was eaten by JS → tab + "frac")
  - "frac{"  (raw \frac{} that wasn't rendered — the { is the giveaway)
  - "rac{"   (from \frac where \f was eaten by JS → form-feed + "rac{")

FALSE-POSITIVE EXCLUSIONS:
  - Text inside <script> or <style> tags (that's code, not visible content)
  - Text inside data-tex, data-composition-src, or other HTML attributes
  - The word "fraction" / "refraction" / "diffraction" (English words containing "frac")

Usage:
    python3 check_frac_unrendered.py [dist_dir]      # default ./dist
Exit 0 = clean, 1 = found unrendered fraction text.
"""

import re
import sys
from pathlib import Path

from _shared import iter_compositions, line_of

# Strip <script>...</script> and <style>...</style> blocks
RE_SCRIPT_STYLE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)
# Strip <span class="cm">...</span> — these are KaTeX source spans rendered at runtime
RE_CM_SPANS = re.compile(r'<span\b[^>]*\bclass="[^"]*\bcm\b[^"]*"[^>]*>.*?</span>', re.S | re.I)
# Strip content inside data-tex attributes (KaTeX source in HTML attributes)
RE_DATA_TEX = re.compile(r'\bdata-tex="[^"]*"', re.S)
# Strip all HTML tags (we only want text content)
RE_TAGS = re.compile(r"<[^>]+>")

# Patterns that indicate an unrendered fraction in visible text
# Each is (regex, description)
FRAC_PATTERNS = [
    (re.compile(r"\bdfrac\b|\bdfrac\{", re.I), "dfrac (from \\dfrac with \\d eaten by JS)"),
    (re.compile(r"\btfrac\b|\btfrac\{", re.I), "tfrac (from \\tfrac with \\t eaten by JS)"),
    (re.compile(r"(?<!\w)frac\{"), "frac{ (raw \\frac not rendered by KaTeX)"),
    (re.compile(r"(?<!\w)rac\{"), "rac{ (from \\frac with \\f eaten by JS)"),
    (re.compile(r"\bdfrac\d"), "dfrac+digit (e.g. dfrac12 = unrendered \\dfrac{1}{2})"),
]

# Words that legitimately contain "frac" — exclude them
FALSE_POSITIVES = re.compile(r"\b(?:fraction|fractions|fractional|refraction|diffraction|infractions?)\b", re.I)


def scan_file(path: Path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    # Remove script/style blocks
    clean = RE_SCRIPT_STYLE.sub(" ", raw)
    # Remove <span class="cm">...</span> (KaTeX source rendered at runtime)
    clean = RE_CM_SPANS.sub(" ", clean)
    # Remove data-tex attributes (KaTeX source in HTML)
    clean = RE_DATA_TEX.sub(" ", clean)
    # Remove tags, leaving only text content
    text_only = RE_TAGS.sub(" ", clean)

    hits = []
    for pat, desc in FRAC_PATTERNS:
        for m in pat.finditer(text_only):
            # Check if it's a false positive (English word)
            context_start = max(0, m.start() - 20)
            context_end = min(len(text_only), m.end() + 20)
            context = text_only[context_start:context_end]
            if FALSE_POSITIVES.search(context):
                continue
            # Find approximate line number in original file
            approx_pos = raw.find(m.group(), 0)
            if approx_pos == -1:
                approx_pos = 0
            line = line_of(raw, approx_pos)
            hits.append((line, desc, m.group(), context.strip()))
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
        for line, desc, match, context in scan_file(f):
            total += 1
            print(f"{f}:{line}: UNRENDERED FRACTION in visible text: '{match}' ({desc})")
            print(f"         context: ...{context}...")

    if total:
        print(f"\nFAIL: {total} unrendered fraction(s) found in visible HTML text.")
        print("These will appear as garbled text (e.g. 'dfrac12') in the final video.")
        print("")
        print("COMMON FIXES:")
        scripts = Path(__file__).resolve().parent
        print(f"  1. Run: {sys.executable} {scripts / 'fix_katex_escaping.py'} {dist}")
        print("     (auto-fixes \\dfrac → \\\\dfrac in JS strings)")
        print("  2. Ensure KaTeX JS is loaded from local path: ./katex/katex.min.js")
        print("  3. Ensure katex.render() calls have throwOnError: false")
        print(f"  4. Re-run: {sys.executable} {scripts / 'precheck.py'} {dist}")
        return 1

    print(f"OK: no unrendered fractions in visible text across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
