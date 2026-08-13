#!/usr/bin/env python3
r"""
check_composition_format.py — Pre-render gate: sub-composition files must be HTML fragments,
NOT full HTML documents.

WHY (the 空白面板/blank-panels bug): HyperFrames loads sub-compositions by injecting their
content into the parent document. When a sub-composition is wrapped in `<!doctype html>`,
`<html>`, `<head>`, `<body>` tags (a full HTML document), the renderer cannot properly execute
the GSAP scripts inside it. All content elements remain at their initial hidden state
(autoAlpha:0) — the video shows blank white panels with only the background texture visible.
Audio and captions (in index.html) play normally, making this bug deceptive.

CORRECT format for dist/compositions/*.html:
    <div data-composition-id="mt-problem" data-width="1920" data-height="1080">
      ... scene content, <style>, <script> ...
    </div>

WRONG format (causes blank panels):
    <!doctype html>
    <html lang="zh">
    <head><meta charset="UTF-8" /></head>
    <body>
    <div data-composition-id="mt-problem" ...>
      ...
    </div>
    </body>
    </html>

Only the root index.html should be a full HTML document. Sub-compositions are fragments.

FAIL when:
  (A) A composition file contains <!DOCTYPE, <html, <head>, or <body> tags; OR
  (B) A composition file does NOT have a root <div data-composition-id="..."> element.

Usage:
    python3 check_composition_format.py [dist_dir]    # default ./dist
Exit 0 = clean, 1 = format violation found (blank panels risk) / no compositions.
"""

import re
import sys
from pathlib import Path

from _shared import line_of

RE_DOCTYPE = re.compile(r"<!doctype\b", re.I)
RE_HTML_TAG = re.compile(r"<html[\s>]", re.I)
RE_HEAD_TAG = re.compile(r"<head[\s>]", re.I)
RE_BODY_TAG = re.compile(r"<body[\s>]", re.I)

RE_COMP_ID = re.compile(r'data-composition-id\s*=\s*["\']([^"\']+)["\']', re.I)

FORBIDDEN = [
    (RE_DOCTYPE, "<!DOCTYPE>"),
    (RE_HTML_TAG, "<html>"),
    (RE_HEAD_TAG, "<head>"),
    (RE_BODY_TAG, "<body>"),
]


def scan_file(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    hits = []

    for regex, tag_name in FORBIDDEN:
        for m in regex.finditer(txt):
            hits.append((line_of(txt, m.start()),
                         f"子合成文件包含 `{tag_name}` — 这是完整HTML文档格式,会导致GSAP脚本无法执行,场景内容全部空白。"
                         f" Sub-composition contains `{tag_name}` — full HTML document format breaks GSAP execution → blank panels."))

    if not RE_COMP_ID.search(txt):
        hits.append((1,
                      "子合成文件缺少 `data-composition-id` 属性 — 根元素必须是 `<div data-composition-id=\"...\">`. "
                      "Missing `data-composition-id` — root element must be `<div data-composition-id=\"...\">`"))

    return hits


def main() -> int:
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    if not dist.is_dir():
        print(f"ERROR: dist dir not found: {dist}", file=sys.stderr)
        return 1

    comp_dir = dist / "compositions"
    if not comp_dir.is_dir():
        print(f"OK: no compositions/ directory under {dist} — nothing to check.")
        return 0

    files = sorted(comp_dir.glob("*.html"))
    if not files:
        print(f"OK: no .html files in {comp_dir} — nothing to check.")
        return 0

    total = 0
    for f in files:
        for line, msg in scan_file(f):
            total += 1
            print(f"{f}:{line}: {msg}")

    if total:
        print(f"\nFAIL: {total} format violation(s) in sub-composition files → GSAP脚本无法正确执行 → 场景面板全部空白(blank panels).")
        print("FIX: 子合成文件必须是HTML片段,不能是完整HTML文档。")
        print("     删除 <!DOCTYPE>, <html>, <head>, <body> 等标签,保留以 <div data-composition-id=\"...\"> 为根的片段即可。")
        print("     只有根 index.html 才是完整HTML文档。")
        print()
        print("     CORRECT format:")
        print('       <div data-composition-id="mt-scene" data-width="1920" data-height="1080">')
        print("         ... <style> ... <script> ...")
        print("       </div>")
        print()
        print("     WRONG format (causes blank panels):")
        print("       <!doctype html>")
        print("       <html><head>...</head><body>")
        print('         <div data-composition-id="mt-scene" ...>...</div>')
        print("       </body></html>")
        return 1

    print(f"OK: {len(files)} sub-composition(s) are HTML fragments (correct format).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
