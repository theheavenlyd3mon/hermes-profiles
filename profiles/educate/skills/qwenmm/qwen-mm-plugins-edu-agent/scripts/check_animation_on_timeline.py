#!/usr/bin/env python3
r"""
check_animation_on_timeline.py — Pre-render gate: every animation MUST live on the scene's paused,
registered GSAP timeline (`window.__timelines["<id>"]`). Flags bare `gsap.to()/from()/fromTo()` and
CSS `@keyframes` — animation that will NOT render in the seek-based capture (动效渲不出来).

WHY: HyperFrames renders deterministically by SEEKING each scene's registered timeline
(`window.__timelines[id].progress(t)`); it does NOT run the global GSAP auto-play clock and does NOT
reliably flush CSS animations during frame capture. So any tween created with a BARE `gsap.to(...)`
(i.e. not added to the paused `tl` that is registered on `window.__timelines`) autoplays only in a live
browser preview and is FROZEN / erratic in the rendered MP4 — the effect silently disappears. Same for
CSS `@keyframes` animations. Real bug (铁丝燃烧·火星四射): sparks/ripples/wire-glow/orbs were all bare
`gsap.to(...)` not on `tl` → the whole "dynamic effect" was missing from the video, yet lint/validate
passed. Measured contrast: broken scenes had 4–8 bare `gsap.*` each; good-quality scenes had ZERO
(everything on `tl.`). The skill already requires this (step-5 self-review: "All animations on the
seekable timeline (no bare gsap.to())") — this gate enforces it.

FLAGS (per composition + index.html):
  A) bare `gsap.to(` / `gsap.from(` / `gsap.fromTo(`  → tween not on the seekable timeline.
     (Allowed: `gsap.set(` [instant, deterministic], `gsap.timeline(` [creates the tl], `gsap.registerX`.)
  B) CSS `@keyframes`  → CSS keyframe animation won't seek-render (use a GSAP tween on `tl` instead).

FIX: add every tween to the paused registered timeline — `tl.to(...)`, `tl.fromTo(...)` — including
ambient LOOPS (`tl.to(el,{...,repeat:R(dur),yoyo:true}, at)`); register `window.__timelines["<id>"]=tl`
with `tl = gsap.timeline({paused:true})`. Convert `@keyframes`/CSS `animation:` to GSAP on `tl`.

Usage: python3 check_animation_on_timeline.py [dist_dir]     # default ./dist
Exit 0 = clean, 1 = animation found that won't render (off-timeline).
"""

import re
import sys
from pathlib import Path

from _shared import line_of

RE_BARE_GSAP = re.compile(r'\bgsap\s*\.\s*(to|from|fromTo)\s*\(', re.I)
RE_KEYFRAMES = re.compile(r'@keyframes\b', re.I)
# strip HTML comments so commented-out examples don't trigger
RE_COMMENT = re.compile(r'<!--.*?-->', re.S)


def scan_file(path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    txt = RE_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), raw)  # keep line numbers
    hits = []
    for m in RE_BARE_GSAP.finditer(txt):
        hits.append((line_of(txt, m.start()),
                     f"bare `gsap.{m.group(1)}(` — 该动画没挂到可 seek 的时间轴(tl)，渲染时只 seek "
                     f"`window.__timelines[id]`，此 tween 不会被驱动 → 动效在 MP4 里不播/乱播(渲不出来)。"))
    for m in RE_KEYFRAMES.finditer(txt):
        hits.append((line_of(txt, m.start()),
                     "CSS `@keyframes` — CSS 关键帧动画不随 seek 渲染 → 动效渲不出来。改用挂在 tl 上的 GSAP 补间。"))
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
        for ln, msg in scan_file(f):
            total += 1
            print(f"{f.name}:{ln}: {msg}")

    if total:
        print(f"\nFAIL: {total} 处动画不在可 seek 的时间轴上(渲染时不会播)。")
        print("FIX: 把每一个补间都挂到该场景【暂停且已注册】的时间轴上——`tl.to(...)` / `tl.fromTo(...)`；"
              "环境循环动效(orb 漂移、辉光脉动、火星四射)也要用 `tl.to(el,{…,repeat:R(dur),yoyo:true}, at)` 挂在 tl 上，"
              "不要用裸 `gsap.to()`。确保 `tl = gsap.timeline({paused:true})` 且 `window.__timelines[\"<id>\"]=tl`。"
              "CSS `@keyframes`/`animation:` 也要改成 tl 上的 GSAP 补间。渲染后抽帧确认动效真的在动(见 step-6 视觉自查闭环)。")
        return 1

    print(f"OK: {len(files)} 个文件的动画均挂在可 seek 的时间轴上(无裸 gsap.to / 无 @keyframes)。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
