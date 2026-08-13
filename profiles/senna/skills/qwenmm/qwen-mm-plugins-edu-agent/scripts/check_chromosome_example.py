#!/usr/bin/env python3
r"""
check_chromosome_example.py — Pre-render gate: chromosome / cell-division scenes MUST follow the
mitosis few-shot (references/examples/mitosis-anaphase.scene.html).

WHY: 染色体/细胞分裂类题目最容易画成"死"动画——纺锤丝是静态线、染色单体乱飞、或染色体在转圈。
那条 mitosis 范例的核心是: (1) 纺锤丝/连接线用动画 <line>，其端点跟着染色单体移动并**缩短牵引**
(GSAP `attr:{x2/y2}` 补间); (2) 绝不给染色体加持续 360° 旋转。本闸门把"必须参考范例"变成可检测产出:
当场景确实是**染色体分裂过程动画**时，强制出现"连接线缩短牵引"的写法，并禁止 360° 转圈。

TRIGGER (self-contained, low false-positive): a composition's VISIBLE text contains 染色体/chromosome
AND at least one cell-division cue (有丝分裂|减数分裂|着丝点|纺锤|姐妹染色单体|移向两极|赤道板|
mitosis|meiosis|spindle|centromere). Pure genetics/karyotype counting问题(无分裂过程线索)不会触发。

FAIL when a triggered project:
  (A) has NO animated connector — no GSAP tween of a <line>'s x2/y2 anywhere
      (`.to(... {attr:{ x2:/y2: ...}}` ) → 纺锤丝没有牵引/缩短动画; OR
  (B) has a continuous 360° spin (`rotation:360` / `rotate(...360)` with repeat) on any element → 廉价转圈.

FIX message points at the few-shot so the author reads & copies it.

Usage: python3 check_chromosome_example.py [dist_dir]   # default ./dist
Exit 0 = clean / not triggered, 1 = triggered but did not follow the example.
"""

import re
import sys
from pathlib import Path

from _shared import line_of

DIV_CUES = re.compile(r"(有丝分裂|减数分裂|着丝点|纺锤|姐妹染色单体|移向两极|赤道板|mitosis|meiosis|spindle|centromere)", re.I)
CHROM = re.compile(r"(染色体|染色单体|chromosome|chromatid)", re.I)
# a GSAP tween animating a line's x2/y2 (the shorten/pull-to-pole signature)
RE_LINE_TWEEN = re.compile(r"attr\s*:\s*\{[^}]*\b(?:x2|y2)\s*:", re.I)
# continuous 360 spin: rotation:360 (any) or rotate(...360...) inside an attr tween, WITH a repeat
RE_SPIN = re.compile(r"rotation\s*:\s*['\"]?\+?=?\s*360|rotate\([^)]*360", re.I)
RE_REPEAT = re.compile(r"repeat\s*:\s*(-1|[1-9])", re.I)


def main() -> int:
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    comp = dist / "compositions"
    files = sorted(list(dist.glob("index.html")) + (list(comp.glob("*.html")) if comp.is_dir() else []))
    if not files:
        print(f"OK: no compositions under {dist}.")
        return 0

    texts = {f: f.read_text(encoding="utf-8", errors="replace") for f in files}
    allt = "\n".join(texts.values())

    if not (CHROM.search(allt) and DIV_CUES.search(allt)):
        print("OK: not a chromosome cell-division scene — check not applicable.")
        return 0

    fails = []
    # (A) require an animated connector (spindle-fiber shorten/pull) somewhere
    if not any(RE_LINE_TWEEN.search(t) for t in texts.values()):
        fails.append("染色体细胞分裂动画缺少「纺锤丝牵引且缩短」的写法：全项目找不到任何 `<line>` 的 "
                     "x2/y2 动画补间(GSAP `attr:{x2:…}` / `attr:{y2:…}`)。纺锤丝必须是带 id 的 <line>，"
                     "其染色单体端随染色单体移动而缩短牵引(与移动同起止/同缓动)。")
    # (B) forbid continuous 360 spin on chromosome-ish elements
    for f, t in texts.items():
        for m in RE_SPIN.finditer(t):
            # only flag if this tween line also has a repeat (continuous)
            seg = t[max(0, m.start() - 120):m.end() + 120]
            if RE_REPEAT.search(seg):
                fails.append(f"{f.name}:{line_of(t, m.start())}: 出现持续 360° 转圈动效(rotation:360 + repeat) "
                             f"→ 染色体/内容物体禁止转圈(显廉价)。改用绘制/位移/脉冲/缓慢漂浮。")
                break

    if fails:
        print("FAIL: 染色体/细胞分裂类场景未遵循 mitosis 范例:")
        for x in fails:
            print("  - " + x)
        print("\nFIX: 必读并套用范例 references/examples/mitosis-anaphase.scene.html "
              "(讲解见 references/example-process-animation.md 的 T2 一分为二并移动 / T3 连接线跟随并缩短牵引 / "
              "T4 数目实时计数 / T6 禁止360°转圈)。纺锤丝=动画<line>，x2/y2 随染色单体移向两极而缩短。")
        return 1

    print("OK: 染色体分裂场景已包含纺锤丝牵引缩短动画，且无360°转圈 — 符合 mitosis 范例。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
