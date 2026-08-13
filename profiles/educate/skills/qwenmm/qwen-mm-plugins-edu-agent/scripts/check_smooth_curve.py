#!/usr/bin/env python3
r"""
check_smooth_curve.py — Pre-render gate: a continuous/smooth curve must NOT be drawn as a
handful of straight chords (不要用分段直线逼近曲线).

WHY: function graphs (抛物线/双曲线/正弦/指数衰减 y=x², 1/x, sin, e^{-x}) and trend/oscillation
curves (种群数量波动、阻尼振荡、生态恢复) are often drawn as a `<polyline>` (or an all-`L` `<path>`)
with only ~10-15 vertices → the "curve" is a visible jagged zig-zag of straight segments
(`stroke-linejoin="round"` only rounds the corners, the chords stay straight). The skill's rule
(references/step-5-build-components.md → "Smooth curves (顺滑曲线)") requires either a smooth
`<path>` cubic-Bézier via the `smoothPath()` Catmull-Rom helper, OR a densely-sampled point list
(~1 pt per ≤10 px). This gate enforces that rule.

TRIGGER (per-file, low false-positive): the composition's text contains a continuous-curve cue
(抛物线|双曲线|正弦|指数|衰减|种群|振荡|波动|parabola|sine|exponential|y=x²|1/x …) AND the file
has a curve-shaped element that is TOO SPARSE — a `<polyline>` / all-straight `<path>` that:
  - has 5..29 vertices (a real smooth curve needs many more; the bug is ~10-15), AND
  - is monotonic in x for ≥80% of steps (a function-of-x plot, left→right), AND
  - spans a wide x-range (> 250 units) with no cubic/quadratic/arc command (C/Q/S/T/A),
  - is a stroked open path (fill:none / no fill), not a closed filled polygon.

EXEMPT (whole file) when straight segments are CORRECT — genuinely piecewise-linear graphs:
  分段函数 / 绝对值 / |x| / 折线统计图 / 折线图 / 阶梯图 / 距离-时间(匀速段) / piecewise / step chart.

FAIL prints file:line of the offending element and points at the smoothPath() helper.

Usage: python3 check_smooth_curve.py [dist_dir]     # default ./dist
Exit 0 = clean / not triggered, 1 = a sparse straight-chord curve in a smooth-curve context.
"""

import re
import sys
from pathlib import Path

from _shared import line_of

# "a continuous / smooth curve is being drawn here"
CURVE_CUES = re.compile(
    r"(抛物线|双曲线|正弦|余弦|三角函数|指数|对数|衰减|增长曲线|种群|振荡|波动|阻尼|生态|"
    r"平滑曲线|光滑曲线|连续曲线|正态|钟形|"
    r"parabola|hyperbol|sine|cosine|logarithm|exponential|decay|oscillat|gaussian|"
    r"y\s*=\s*x\s*[\^²2]|y\s*=\s*a?\s*x\s*\^?\s*2|x²|y\s*=\s*1\s*/\s*x|y\s*=\s*\\?sin|y\s*=\s*\\?cos|y\s*=\s*e\s*\^)",
    re.I,
)

# straight segments are CORRECT here → exempt the whole file
PIECEWISE_OK = re.compile(
    r"(分段函数|分段线性|绝对值|\|\s*x\s*\||折线统计图|折线图|折线|阶梯|台阶|"
    r"距离[-—－]?时间|路程[-—－]?时间|s\s*[-—－]\s*t\s*图|v\s*[-—－]\s*t\s*图|"
    r"piecewise|step\s*chart|step\s*function|line\s*chart)",
    re.I,
)

RE_POLYLINE = re.compile(r"<polyline\b([^>]*)\bpoints\s*=\s*\"([^\"]+)\"([^>]*)>", re.I)
RE_PATH = re.compile(r"<path\b([^>]*)\bd\s*=\s*\"([^\"]+)\"([^>]*)>", re.I)
RE_CURVECMD = re.compile(r"[CcQqSsTtAa]")           # any bézier/arc command → already smooth
RE_NUM = re.compile(r"-?\d+(?:\.\d+)?")

MIN_PTS = 5      # below this it's a segment/marker, not a "curve"
MAX_PTS = 29     # at/above 30 it's dense enough to read smooth
MIN_XSPAN = 250  # a real plotted curve spans a wide x-range
MONO_FRAC = 0.8  # fraction of steps that must share x-direction (function-of-x)


def _pts_from_polyline(points_str):
    nums = [float(n) for n in RE_NUM.findall(points_str)]
    return list(zip(nums[0::2], nums[1::2]))


def _pts_from_path(d):
    # only reached when d has NO curve command → all M/L: pull coordinate pairs in order
    nums = [float(n) for n in RE_NUM.findall(d)]
    return list(zip(nums[0::2], nums[1::2]))


def _is_sparse_function_curve(pts):
    n = len(pts)
    if n < MIN_PTS or n > MAX_PTS:
        return False
    xs = [p[0] for p in pts]
    xspan = max(xs) - min(xs)
    if xspan < MIN_XSPAN:
        return False
    steps = [xs[i + 1] - xs[i] for i in range(n - 1)]
    steps = [s for s in steps if s != 0]
    if not steps:
        return False
    pos = sum(1 for s in steps if s > 0)
    neg = len(steps) - pos
    mono = max(pos, neg) / len(steps)
    return mono >= MONO_FRAC


def _attrs_open_stroke(attrs):
    # treat as an open stroked curve unless it's an explicitly filled shape
    m = re.search(r"fill\s*[:=]\s*\"?\s*([^\";\s]+)", attrs, re.I)
    if m and m.group(1).lower() not in ("none", "transparent"):
        return False
    return True


def scan_file(path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    if not CURVE_CUES.search(txt):
        return []
    if PIECEWISE_OK.search(txt):
        return []  # this scene is legitimately piecewise-linear

    hits = []
    for m in RE_POLYLINE.finditer(txt):
        pre, points, post = m.group(1), m.group(2), m.group(3)
        if not _attrs_open_stroke(pre + post):
            continue
        pts = _pts_from_polyline(points)
        if _is_sparse_function_curve(pts):
            hits.append((line_of(txt, m.start()), "polyline", len(pts)))

    for m in RE_PATH.finditer(txt):
        pre, d, post = m.group(1), m.group(2), m.group(3)
        if RE_CURVECMD.search(d):
            continue  # has C/Q/S/T/A → already a smooth curve
        if not _attrs_open_stroke(pre + post):
            continue
        pts = _pts_from_path(d)
        if _is_sparse_function_curve(pts):
            hits.append((line_of(txt, m.start()), "path(all-straight)", len(pts)))

    return hits


def main() -> int:
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    comp = dist / "compositions"
    files = sorted(list(dist.glob("index.html")) + (list(comp.glob("*.html")) if comp.is_dir() else []))
    if not files:
        print(f"OK: no compositions under {dist}.")
        return 0

    total = 0
    for f in files:
        for ln, kind, npts in scan_file(f):
            total += 1
            print(f"{f}:{ln}: continuous curve drawn as a sparse straight-chord {kind} "
                  f"({npts} vertices, monotonic-x, wide span) in a smooth-curve scene "
                  f"→ 用分段直线逼近曲线 (jagged zig-zag).")

    if total:
        print(f"\nFAIL: {total} sparse straight-chord curve(s) in continuous-curve scene(s).")
        print("FIX: render continuous curves SMOOTH — either (1) a `<path fill=\"none\" stroke=…>` whose "
              "`d` is built with the Catmull-Rom `smoothPath()` helper, or (2) a densely-sampled point "
              "list (~1 pt per ≤10 px, ~120+ pts across a wide axis). See references/step-5-build-"
              "components.md → \"Smooth curves (顺滑曲线)\". Genuinely piecewise-linear graphs "
              "(y=|x|, 分段函数, 折线统计图, 匀速距离-时间) are exempt.")
        return 1

    print(f"OK: no sparse straight-chord curves across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
