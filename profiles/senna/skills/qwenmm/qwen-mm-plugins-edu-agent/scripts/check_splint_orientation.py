#!/usr/bin/env python3
r"""
check_splint_orientation.py — Pre-render gate (domain semantics): a "燃着/带火星的木条 伸入 集气瓶/试管"
scene must draw the BURNING END (flame) going DOWN INTO the vessel — the flame must sit INSIDE the
vessel mouth, not above/outside it. Flags the classic reversal (火柴/木条画反：火焰在瓶口之上、露在瓶外).

WHY: to test a gas, you lower the BURNING end of the splint into the jar so the flame meets the gas
(木条熄灭 / 复燃 happens INSIDE). Models often reach for the everyday "lit stick = flame on top" schema
and put the flame at the TOP end (held end) with the plain end dipping in — so the flame ends up ABOVE
the jar mouth, outside the gas. Then "木条熄灭"/"复燃" can't physically happen in the picture. This is a
pure orientation/semantics bug that the layout/overlap gates cannot see.

TRIGGER (tight, to avoid flagging legit flame-on-top like 酒精灯/蜡烛加热): a composition whose text has
木条 AND (伸入|插入|伸进) AND (集气瓶|试管|瓶|烧杯). Skips inverted-vessel setups (倒置|瓶口向下|口朝下|
向下排空气) where the geometry differs, and needs to positively identify BOTH a flame element and a
tall vessel rect — otherwise it SKIPs (no false positive).

FAIL when: the flame's anchor is at/above the vessel mouth (flame_y <= mouth_y + MARGIN, i.e. not below
the opening) while horizontally over the vessel → the burning end is NOT inside the jar (画反了).

Usage: python3 check_splint_orientation.py [dist_dir]     # default ./dist
Exit 0 = clean / not applicable, 1 = a reversed burning-splint scene.
"""

import re
import sys
from pathlib import Path

from _shared import attr, line_of

TRIG_STICK = re.compile(r"木条")
TRIG_INSERT = re.compile(r"(伸入|插入|伸进)")
TRIG_VESSEL = re.compile(r"(集气瓶|试管|烧杯|瓶)")
EXEMPT = re.compile(r"(倒置|瓶口向下|口朝下|向下排空气|酒精灯|蜡烛|导管)")
MARGIN = 12.0   # viewBox units: flame must be at least this far BELOW the mouth to count as "inside"

RE_FLAME_ID = re.compile(r'<(?:g|path|use|polygon|ellipse|circle)\b[^>]*\bid\s*=\s*"([^"]*flame[^"]*)"[^>]*>', re.I)
RE_FLAME_FILL = re.compile(r'<(?:path|g|ellipse|polygon)\b[^>]*\bfill\s*=\s*"(?:url\(#[^)]*flame[^)]*\)|#f(?:59e0b|97316|bbf24|b923c|59f00)|orange|gold)"', re.I)
RE_TRANSLATE = re.compile(r'translate\(\s*(-?[\d.]+)\s*[ ,]\s*(-?[\d.]+)\s*\)')
RE_RECT = re.compile(r'<rect\b[^>]*>', re.I)


def fnum(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def find_flame_anchor(txt):
    """Return (x, y, idx) of the flame's anchor, or None. Anchor = the nearest translate() that
    wraps the flame SHAPE (that's where the flame base sits on the stick). We look at the actual
    flame element (a shape filled with a flame gradient/orange, or a <g>/<path> id~flame — NOT a
    <linearGradient id="flameGrad"> def)."""
    cands = [m.start() for m in RE_FLAME_FILL.finditer(txt)]
    cands += [m.start() for m in RE_FLAME_ID.finditer(txt)]
    cands.sort()
    for pos in cands:
        window = txt[max(0, pos - 300):pos]
        trs = list(RE_TRANSLATE.finditer(window))
        if trs:
            t = trs[-1]
            return (fnum(t.group(1)), fnum(t.group(2)), pos)
        t2 = RE_TRANSLATE.search(txt[pos:pos + 200])
        if t2:
            return (fnum(t2.group(1)), fnum(t2.group(2)), pos)
    return None


def find_vessel(txt):
    """Return (mouth_y, x0, x1) for the tallest large 'glass body' rect, or None."""
    best = None
    for m in RE_RECT.finditer(txt):
        tag = m.group(0)
        x, y, w, h = fnum(attr(tag, "x")), fnum(attr(tag, "y")), fnum(attr(tag, "width")), fnum(attr(tag, "height"))
        if None in (x, y, w, h):
            continue
        if h < 120 or h < 1.15 * w:   # a vessel body is TALL
            continue
        area = w * h
        if best is None or area > best[0]:
            best = (area, y, x, x + w)
    if best:
        return (best[1], best[2], best[3])
    return None


def scan_file(path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    # operation trigger: "(燃着)木条 … 伸入/插入 …" — the vessel is detected geometrically (a scene may
    # label it 无色气体 and only DRAW the jar), so we don't require a vessel keyword in the text.
    if not (TRIG_STICK.search(txt) and TRIG_INSERT.search(txt)):
        return None
    if EXEMPT.search(txt):
        return None
    flame = find_flame_anchor(txt)
    vessel = find_vessel(txt)
    if not flame or not vessel:
        return None  # can't confidently judge → skip (no false positive)
    fx, fy, idx = flame
    mouth_y, x0, x1 = vessel
    if fx is None or fy is None:
        return None
    # flame must be horizontally over the vessel to be "the splint in this jar"
    if not (x0 - 40 <= fx <= x1 + 40):
        return None
    # y grows downward: flame INSIDE the jar means flame_y > mouth_y (below the opening).
    if fy <= mouth_y + MARGIN:
        return (line_of(txt, idx), fx, fy, mouth_y)
    return None


def main() -> int:
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    comp = dist / "compositions"
    files = sorted(list(dist.glob("index.html")) + (list(comp.glob("*.html")) if comp.is_dir() else []))
    if not files:
        print(f"OK: no compositions under {dist}.")
        return 0

    fails = []
    for f in files:
        r = scan_file(f)
        if r:
            ln, fx, fy, my = r
            fails.append(f"{f.name}:{ln}: 燃着木条伸入{('集气瓶/试管')}——火焰锚点 y≈{fy:.0f} 在瓶口 y≈{my:.0f} "
                         f"之上/齐平(y 越小越靠上)，即火焰露在瓶口外、燃烧端没有伸进瓶内 → 木条画反了。")

    if fails:
        print("FAIL: 燃着木条方向画反(火焰在瓶外):")
        for x in fails:
            print("  - " + x)
        print("\nFIX: 把【燃烧端(火焰)】朝下伸进瓶内——火焰应位于瓶口以下、瓶身内部(火焰 y > 瓶口 y)，"
              "木条的手握(不燃)端露在瓶口之上。即：翻转木条方向，让火焰在插入端、且几何上在瓶口内侧；"
              "火焰仍向上窜(尖朝上)，但整簇火焰要在瓶内。改完抽帧自查确认火焰在瓶内(见 step-6 视觉自查闭环)。")
        return 1

    print("OK: 未发现燃着木条方向画反(或场景不适用)。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
