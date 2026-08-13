#!/usr/bin/env python3
r"""
check_composition_root_id.py — Pre-render gate: a scene scopes CSS/JS to `#<composition-id>`
but the root <div> has no matching DOM `id` (so the selector matches NOTHING).

THE BUG (silent, severe — 公式/样式全都没渲染出来):
    A sub-composition's root is written as
        <div data-composition-id="mt-formula" data-width="1920" data-height="1080">
    and the scene then scopes its styles / KaTeX rendering to the id selector `#mt-formula`:
        #mt-formula { width:1920px; ... }                       (CSS)
        document.querySelectorAll("#mt-formula [data-tex]")     (KaTeX render loop)
    But `data-composition-id` is a DATA ATTRIBUTE, not a DOM `id`. There is no element with
    `id="mt-formula"`, so `#mt-formula` matches nothing:
      • the KaTeX loop finds 0 elements → `katex.render` never runs → EVERY `[data-tex]` / `.cm`
        formula span stays empty → all formulas are blank in the video;
      • the `#mt-formula { … }` container CSS never applies → layout/background can break too.
    It's silent because `querySelectorAll` returning empty throws no error.

    NOTE: the skill's own templates DON'T hit this — index.html renders `.cm` spans by CLASS,
    and scene templates use `getElementById("mt-f-eq-1")` on real inner ids. This gate exists to
    catch a model that invents a `#<composition-id>`-scoped selector without also giving the root
    a matching `id`.

THE FIX (either is fine; do the first):
    1. Give the root BOTH attributes:
         <div data-composition-id="mt-formula" id="mt-formula" data-width="1920" data-height="1080">
    2. Or don't scope by the root id at all — use a class / attribute selector
       (`[data-composition-id="mt-formula"] [data-tex]`) or `getElementById` on inner element ids.

Usage:
    python3 check_composition_root_id.py [dist_dir]     # default ./dist
Exit 0 = clean, 1 = at least one composition scopes to a missing root id.
"""

import re
import sys
from pathlib import Path

from _shared import iter_compositions, line_of

RE_ROOT = re.compile(r'<div\b[^>]*\bdata-composition-id\s*=\s*"([^"]+)"[^>]*>', re.I)


def scan_file(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    m = RE_ROOT.search(txt)
    if not m:
        return hits
    cid = m.group(1)

    # Does the file reference `#<cid>` as a selector (CSS or JS)?  `#mt-formula` but not `#mt-formulaX`.
    ref = re.search(r'#' + re.escape(cid) + r'(?![\w-])', txt)
    if not ref:
        return hits  # scene doesn't use the id selector → no requirement for an id

    # Is there a STANDALONE id="<cid>"?  Must NOT match the `id="..."` substring inside
    # `data-composition-id="..."`, so forbid a preceding word-char or hyphen.
    has_id = re.search(r'(?<![\w-])id\s*=\s*"' + re.escape(cid) + r'"', txt)
    if has_id:
        return hits

    # Point at the KaTeX case explicitly if that's what's scoped (most damaging), else generic.
    katex_scoped = re.search(r'querySelectorAll\(\s*["\']#' + re.escape(cid) + r'\b', txt)
    detail = ("its KaTeX render loop is scoped there (querySelectorAll(\"#" + cid + " [data-tex]\")) "
              "→ 0 matches → NO formula is rendered (公式全空)"
              if katex_scoped else
              "CSS/JS scoped to it will not apply")
    hits.append((line_of(txt, ref.start()),
                 f'scene root is <div data-composition-id="{cid}"> but there is NO element with '
                 f'`id="{cid}"`, yet the selector `#{cid}` is used here — {detail}. '
                 f'`data-composition-id` is a data-attribute, NOT a DOM id. '
                 f'FIX: add `id="{cid}"` to the root div (keep data-composition-id too), or use a '
                 f'class/attribute selector `[data-composition-id="{cid}"] …` / getElementById on inner ids.'))
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
        print(f"\nFAIL: {total} composition(s) scope CSS/JS to `#<composition-id>` with no matching root `id` "
              f"→ silent no-op (blank formulas / unstyled scene).")
        print('FIX: give the root `<div data-composition-id="X" id="X" …>` (both attributes), '
              'or scope via class/attribute selector / getElementById instead of `#X`.')
        return 1

    print(f"OK: no missing-root-id selector scoping across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
