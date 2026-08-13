#!/usr/bin/env python3
r"""
check_cjk_font.py — Pre-render gate: fail if any element renders Chinese (CJK) text with a
font-family that has NO CJK glyphs. Symptom: 中文变成 "NO GLYPH"/豆腐块/.notdef boxes.

ROOT CAUSE: The air-gapped render sandbox ships exactly ONE CJK font — "Noto Sans SC".
Latin-only faces (Inter, JetBrains Mono, serif, and the bare `sans-serif` fallback which has
no CJK in the sandbox) contain no Chinese glyphs. So an SVG label like
    <text font-family="Inter, sans-serif">v = 常量</text>
draws "v = " fine but 常量 has no glyph → the renderer shows ".notdef" placeholders that read
"NO GLYPH". This bites SVG <text>/<tspan> most (they take an explicit font-family and do NOT
inherit the CJK-first body stack), and any HTML element that inline-overrides font-family.

RULE (see design-system.md typography + step-5 fonts): ANY element containing CJK text MUST
use a font stack that includes "Noto Sans SC" (the shipped CJK face). Put it first, e.g.
    font-family="Noto Sans SC, Inter, sans-serif"
Latin-only labels (v, F, N, numbers, units) may use Inter — this check only fires when the
element's own text actually contains a CJK character.

Usage:
    python3 check_cjk_font.py [dist_dir]     # default ./dist
Exit 0 = clean, 1 = CJK text on a non-CJK font (or no HTML found).
"""

import re
import sys
from pathlib import Path

from _shared import iter_compositions, line_of

CJK = r"一-鿿㐀-䶿豈-﫿぀-ヿ"  # Han + kana (kana also absent from Inter)
RE_CJK = re.compile(f"[{CJK}]")
# an SVG text/tspan element with its inner content
RE_SVG_TEXT = re.compile(r"<(text|tspan)\b([^>]*)>(.*?)</\1>", re.I | re.S)
# an HTML element that inline-sets font-family, plus the text immediately following the tag
RE_INLINE_FF = re.compile(
    r"<[^>]*\bstyle\s*=\s*(['\"])[^'\"]*font-family\s*:\s*(?P<ff>[^;'\"]+)[^'\"]*\1[^>]*>(?P<txt>[^<]*)",
    re.I | re.S,
)
RE_FF_ATTR = re.compile(r"""font-family\s*=\s*(['"])(?P<ff>[^'"]*)\1""", re.I)
RE_FF_IN_STYLE = re.compile(r"font-family\s*:\s*(?P<ff>[^;'\"}]+)", re.I)

CJK_FONT_OK = re.compile(r"noto\s*sans\s*(sc|cjk)|source\s*han|微软雅黑|黑体|宋体", re.I)


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)


def font_ok(ff: str) -> bool:
    return bool(CJK_FONT_OK.search(ff or ""))


def scan_file(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    hits = []

    # 1) SVG <text>/<tspan> — explicit font-family attr (or inline style) that lacks a CJK face
    for m in RE_SVG_TEXT.finditer(txt):
        attrs, inner = m.group(2), m.group(3)
        content = strip_tags(inner)
        if not RE_CJK.search(content):
            continue
        ff_attr = RE_FF_ATTR.search(attrs)
        ff_style = RE_FF_IN_STYLE.search(attrs)
        ff = (ff_attr.group("ff") if ff_attr else None) or (ff_style.group("ff") if ff_style else None)
        if ff is None:
            continue  # inherits (usually the CJK-first body/CSS stack) — not flaggable here
        if not font_ok(ff):
            snippet = content.strip()[:16]
            hits.append((line_of(txt, m.start()),
                         f"<{m.group(1)}> font-family=\"{ff.strip()[:40]}\" has no CJK glyphs but text is Chinese "
                         f"(\"{snippet}\") → renders as NO GLYPH/豆腐块"))

    # 2) HTML elements inline-overriding font-family to a non-CJK face, with CJK text right after
    for m in RE_INLINE_FF.finditer(txt):
        ff, following = m.group("ff"), m.group("txt")
        if RE_CJK.search(following) and not font_ok(ff):
            hits.append((line_of(txt, m.start()),
                         f"inline font-family:{ff.strip()[:40]} has no CJK glyphs but text is Chinese "
                         f"(\"{following.strip()[:16]}\") → renders as NO GLYPH/豆腐块"))

    # 3) CSS CLASS rules whose font-family lacks a CJK face, applied to an element with CJK text.
    #    (The common miss: `.block-number{font-family:Inter,sans-serif}` on `<div ...>对称性</div>`.)
    # NOTE: font-family values legitimately contain quotes ("Noto Sans SC"), so read the whole
    # declaration up to ; or } — do NOT stop at a quote (that would truncate `Inter,"Noto Sans SC"`).
    ff_decl = re.compile(r"font-family\s*:\s*([^;}]+)", re.I)
    risky = {}   # class name -> latin-only font-family
    for sm in re.finditer(r"<style\b[^>]*>(.*?)</style>", txt, re.I | re.S):
        for rm in re.finditer(r"\.([A-Za-z][\w-]*)\s*\{([^}]*)\}", sm.group(1)):
            name, body = rm.group(1), rm.group(2)
            if "katex" in name.lower():
                continue
            ffm = ff_decl.search(body)
            if not ffm:
                continue
            if font_ok(ffm.group(1)):
                risky.pop(name, None)          # a CJK-ok rule for this class clears it
            else:
                risky[name] = ffm.group(1).strip()[:40]
    if risky:
        # scan elements: <tag ... class="..."> immediate text
        for em in re.finditer(r'<([a-zA-Z][\w-]*)\b([^>]*)\bclass\s*=\s*(["\'])([^"\']*)\3([^>]*)>([^<]*)', txt):
            attrs_all = em.group(2) + em.group(5)
            classes = em.group(4).split()
            following = em.group(6)
            if not RE_CJK.search(following):
                continue
            inline_ff = ff_decl.search(attrs_all)      # element inline font-family overrides
            if inline_ff and font_ok(inline_ff.group(1)):
                continue
            bad = [c for c in classes if c in risky]
            if bad:
                hits.append((line_of(txt, em.start()),
                             f".{bad[0]} sets font-family:{risky[bad[0]]} (no CJK glyphs) but its text is Chinese "
                             f"(\"{following.strip()[:16]}\") → renders as NO GLYPH/豆腐块. Add \"Noto Sans SC\" to that class."))
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
        print(f"\nFAIL: {total} CJK-on-non-CJK-font issue(s) → Chinese renders as NO GLYPH / 豆腐块.")
        print("FIX: any element whose text contains Chinese MUST use a stack that includes \"Noto Sans SC\",")
        print("     e.g. font-family=\"Noto Sans SC, Inter, sans-serif\". Keep Inter only for pure Latin")
        print("     labels (v, F, N, digits, units). The sandbox ships no other CJK font.")
        return 1

    print(f"OK: all CJK text uses a CJK-capable font across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
