#!/usr/bin/env python3
r"""
check_root_compositions.py — Pre-render gate: root index.html must reference every scene
sub-composition with the EXACT attribute `data-composition-src`, AND every scene clip +
sub-composition root must declare `data-width`/`data-height`.

WHY (the 全白/all-white bug): HyperFrames loads & compiles an external scene file ONLY when
the clip div carries `data-composition-src="compositions/scene-X.html"`. If the model writes
`data-src="..."` (or `src="..."`, or omits it), NONE of the scenes load — the rendered video
is blank/white except the root-level caption bar. Same if composition files exist but are not
referenced at all (orphaned).

WHY (the 场景缩到左上角/shrunken-scene layout bug): HyperFrames sizes and scales each clip onto
the parent canvas using the clip's `data-width`/`data-height` ATTRIBUTES (NOT CSS width/height).
If a scene clip (or the sub-composition's own root div) omits these attributes — e.g. it only
sets `style="width:1920px;height:1080px"` — the renderer can't tell the scene is 1920×1080, so it
falls back to a content-measured size anchored top-left and does NOT fill the frame. Result: every
scene renders as a small box in the top-left corner with big grey margins on the right/bottom
(the box size even varies per scene by its content). CSS width/height does NOT fix this — the
attributes are required.

FAIL when:
  (A) index.html has a clip pointing at a compositions/*.html via the WRONG attribute
      (`data-src` / plain `src`) instead of `data-composition-src`; OR
  (B) dist/compositions/*.html exist but index.html has ZERO `data-composition-src` refs; OR
  (C) a `data-composition-src` points to a file that does not exist; OR
  (D) a `data-composition-src` clip in index.html is missing `data-width` and/or `data-height`; OR
  (E) a sub-composition root `<div data-composition-id=...>` is missing `data-width`/`data-height`.

Usage:
    python3 check_root_compositions.py [dist_dir]    # default ./dist
Exit 0 = clean, 1 = root won't load its scenes (all-white risk) / scenes won't fill the frame / no index.
"""

import re
import sys
from pathlib import Path

RE_GOOD = re.compile(r'data-composition-src\s*=\s*["\']([^"\']+)["\']', re.I)
# a clip-ish div that uses the WRONG attribute to point at a composition file.
# negative lookbehind [\w-] so `src` inside `data-composition-src` is NOT matched.
RE_WRONG = re.compile(r'<div\b[^>]*?(?<![\w-])(data-src|src)\s*=\s*["\']([^"\']*compositions/[^"\']+\.html)["\']', re.I)
# a clip <div ...> tag that carries data-composition-src (capture the whole opening tag)
RE_CLIP_TAG = re.compile(r'<div\b[^>]*\bdata-composition-src\s*=\s*["\'][^"\']+["\'][^>]*>', re.I)
# a sub-composition root <div ...> tag that carries data-composition-id
RE_ROOT_TAG = re.compile(r'<div\b[^>]*\bdata-composition-id\s*=\s*["\'][^"\']+["\'][^>]*>', re.I)
RE_W = re.compile(r'\bdata-width\s*=', re.I)
RE_H = re.compile(r'\bdata-height\s*=', re.I)


def _attr(tag, name):
    m = re.search(name + r'\s*=\s*["\']([^"\']*)["\']', tag, re.I)
    return m.group(1) if m else "?"


def _missing_size(tag):
    miss = []
    if not RE_W.search(tag):
        miss.append("data-width")
    if not RE_H.search(tag):
        miss.append("data-height")
    return miss


def main() -> int:
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    if not dist.is_dir():
        print(f"ERROR: dist dir not found: {dist}", file=sys.stderr)
        return 1
    idx = dist / "index.html"
    if not idx.is_file():
        print(f"ERROR: {idx} not found", file=sys.stderr)
        return 1

    txt = idx.read_text(encoding="utf-8", errors="replace")
    comps = sorted((dist / "compositions").glob("*.html")) if (dist / "compositions").is_dir() else []
    good = RE_GOOD.findall(txt)
    fails = []

    # (A) wrong attribute name
    for m in RE_WRONG.finditer(txt):
        attr, ref = m.group(1), m.group(2)
        line = txt.count("\n", 0, m.start()) + 1
        fails.append(f"index.html:{line}: 用了 `{attr}=\"{ref}\"` 引用子合成 → HyperFrames 不会加载 → 场景全白。"
                     f"必须改成 `data-composition-src=\"{ref.lstrip('./')}\"`")

    # (B) compositions exist but none referenced
    if comps and not good:
        fails.append(f"dist/compositions/ 有 {len(comps)} 个场景文件，但 index.html 里 0 个 `data-composition-src` 引用 "
                     f"→ 没有任何场景会被加载 → 全片只剩字幕(全白)。")

    # (C) referenced file missing
    for ref in good:
        p = (dist / ref.lstrip("./")).resolve()
        if not p.is_file():
            fails.append(f"index.html: `data-composition-src=\"{ref}\"` 指向的文件不存在 → 该场景空白。")

    # (D) scene clip in index.html missing data-width/data-height
    for m in RE_CLIP_TAG.finditer(txt):
        tag = m.group(0)
        miss = _missing_size(tag)
        if miss:
            line = txt.count("\n", 0, m.start()) + 1
            src = _attr(tag, "data-composition-src")
            fails.append(f"index.html:{line}: 场景 clip (data-composition-src=\"{src}\") 缺 {' 和 '.join(miss)} "
                         f"→ HyperFrames 无法把该场景铺满画布，场景会缩到左上角、四周露出灰底(排版崩塌)。"
                         f"给该 clip 加 `data-width=\"1920\" data-height=\"1080\"`(CSS 里的 width/height 不算数)。")

    # (E) sub-composition root missing data-width/data-height (attributes, not CSS)
    for cf in comps:
        ctxt = cf.read_text(encoding="utf-8", errors="replace")
        rm = RE_ROOT_TAG.search(ctxt)
        if not rm:
            continue
        miss = _missing_size(rm.group(0))
        if miss:
            line = ctxt.count("\n", 0, rm.start()) + 1
            cid = _attr(rm.group(0), "data-composition-id")
            fails.append(f"compositions/{cf.name}:{line}: 子合成根 <div data-composition-id=\"{cid}\"> 缺 "
                         f"{' 和 '.join(miss)} 属性 → 渲染器读不到场景固有尺寸，场景不铺满、缩到左上角。"
                         f"在根 div 上加 `data-width=\"1920\" data-height=\"1080\"`(不能只写在 style/CSS 里)。")

    if fails:
        print("FAIL: root index.html 未正确引用/尺寸化子合成(全白 或 场景缩到左上角):")
        for f in fails:
            print("  - " + f)
        print("\nFIX: (1) 每个场景 clip 必须用精确属性 **`data-composition-src=\"compositions/scene-X.html\"`** "
              "(不是 `data-src`/`src`),且 `data-composition-id` 与该合成内 `window.__timelines[id]` 注册的 id 一致; "
              "(2) 每个场景 clip 和每个子合成根 div 都必须带 **`data-width=\"1920\" data-height=\"1080\"` 属性** "
              "(HyperFrames 只认 data-* 属性来缩放场景, CSS 的 width/height 不生效)。见 step-6 根合成模板。")
        return 1

    print(f"OK: root 正确用 data-composition-src 引用了 {len(good)} 个场景, 且 clip/子合成根均声明了 data-width/height。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
