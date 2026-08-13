#!/usr/bin/env python3
r"""
check_svg_transform_anim.py — Pre-render gate for the "物体飞出去 / element jumps off-screen"
bug caused by GSAP-tweening a transform property on an SVG element that is POSITIONED by a
`transform="translate(...) rotate(...)"` attribute.

THE BUG (why an object flies out of frame):
    An SVG element placed with a hard-coded transform, e.g.
        <g transform="translate(390,364) rotate(-30)"> ... </g>   <!-- block on the incline -->
    is then animated with a GSAP transform shorthand:
        gsap.fromTo("g[transform]", {y:10}, {y:0})
    GSAP parses the element's existing transform into its own model (x=390, y=364, rot=-30),
    then the tween OVERRIDES y to 10→0 — so the element's translateY jumps from 364 to 0 and
    the object leaps ~364px off its intended position (flies out of the diagram). The same
    happens for x / rotation / scale / xPercent / yPercent / skew.

RULE 1 — never GSAP-tween a transform property (x, y, rotation[XYZ], scale[XY], xPercent,
yPercent, skew[XY]) on an SVG element that carries a positioning `transform=` attribute.
    Safe alternatives:
      • animate ONLY opacity / autoAlpha on the positioned element, OR
      • NEST: keep the positioning transform on a static outer <g>, put the animated
        fade/slide on an inner <g> (or a wrapper), OR
      • bake the motion into the attribute animation (`attr:{transform:...}`) with the full
        translate+rotate written out — never a bare x/y shorthand.

RULE 2 — never scale/rotate an SVG element with a **px** transformOrigin (use svgOrigin).
    e.g. `gsap.to("#r1", {scale:0.72, transformOrigin:"470px 270px"})` on an SVG <g> whose
    children sit far from the SVG origin → GSAP bakes a large translate and the element FLIES
    off (物体飞出画面). Even when the <g> has NO transform attribute (positioned purely by its
    children's absolute x/y), this still happens — so RULE 1 alone misses it.
    Fix: `svgOrigin:"470 270"` (user-space origin), or wrap it in `<g transform="translate(...)">`
    and scale an inner element. (`transformOrigin` in % — e.g. "50% 50%" — is fine on SVG.)

Usage:
    python3 check_svg_transform_anim.py [dist_dir]     # default ./dist
Exit 0 = clean, 1 = a transform tween on a transform-positioned SVG element.
"""

import re
import sys
from pathlib import Path

from _shared import attr, iter_compositions, line_of

# GSAP transform shorthands that clobber an SVG transform attribute.
TRANSFORM_PROPS = ("x", "y", "rotation", "rotationX", "rotationY", "rotationZ",
                   "scale", "scaleX", "scaleY", "xPercent", "yPercent",
                   "skewX", "skewY")
POS_RE = re.compile(r"(translate|rotate|scale|matrix|skew)\s*\(")

# Rule 2: scale/rotation on an SVG element using a **px** transformOrigin (should be svgOrigin).
# On SVG, `transformOrigin:"470px 270px"` is computed in the element's local/bbox space; combined
# with scale/rotation on a group whose children sit far from the SVG origin, it bakes a large
# translate → the element flies off (物体飞出画面). Correct GSAP API is `svgOrigin:"470 270"`.
SCALE_ROT_PROPS = ("scale", "scaleX", "scaleY", "rotation", "rotationX", "rotationY", "rotationZ")
PX_ORIGIN_RE = re.compile(r"transformOrigin\s*:\s*['\"][^'\"]*px", re.I)


def positioned_elements(txt):
    """Elements inside <svg> that carry a positioning transform attribute.
    Returns (has_any, ids:set, classes:set, tags:set)."""
    ids, classes, tags = set(), set(), set()
    has_any = False
    for sm in re.finditer(r"<svg\b[^>]*>.*?</svg>", txt, re.S):
        svg = sm.group(0)
        for m in re.finditer(r"<([a-zA-Z][\w:-]*)\b([^>]*)>", svg):
            tag, rest = m.group(1), m.group(2)
            tr = attr("<x " + rest + ">", "transform")
            if not tr or not POS_RE.search(tr):
                continue
            has_any = True
            tags.add(tag.lower())
            eid = attr("<x " + rest + ">", "id")
            if eid:
                ids.add(eid)
            cls = attr("<x " + rest + ">", "class")
            if cls:
                classes.update(cls.split())
    return has_any, ids, classes, tags


def svg_elements(txt):
    """ALL elements inside any <svg>…</svg> (not only transform-positioned ones).
    Returns (has_svg, ids, classes, tags) — used to decide if a tween selector targets SVG."""
    ids, classes, tags = set(), set(), set()
    has_svg = False
    for sm in re.finditer(r"<svg\b[^>]*>.*?</svg>", txt, re.S):
        svg = sm.group(0)
        for m in re.finditer(r"<([a-zA-Z][\w:-]*)\b([^>]*)>", svg):
            tag, rest = m.group(1).lower(), m.group(2)
            if tag in ("script", "style"):
                continue
            has_svg = True
            tags.add(tag)
            eid = attr("<x " + rest + ">", "id")
            if eid:
                ids.add(eid)
            cls = attr("<x " + rest + ">", "class")
            if cls:
                classes.update(cls.split())
    return has_svg, ids, classes, tags


def tween_calls(txt):
    """Yield (line_pos, selector, vars_text) for each gsap/tl .to/.from/.fromTo call.
    Selector = first string arg; vars_text = remainder of the same line (covers the vars)."""
    for m in re.finditer(r"\.(?:to|from|fromTo)\s*\(\s*(['\"])(.*?)\1\s*,", txt):
        sel = m.group(2)
        # remainder of the logical line after the selector (one-line calls dominate here)
        eol = txt.find("\n", m.end())
        if eol == -1:
            eol = len(txt)
        yield m.start(), sel, txt[m.end():eol]


def vars_animate_transform(vars_text):
    for p in TRANSFORM_PROPS:
        # `x:` but not `x2:` / `attr:{x:...}` handled naturally (\b before, : after; x2 has digit)
        if re.search(r'(?<![\w$])' + re.escape(p) + r'\s*:', vars_text):
            # exclude transformOrigin / svgOrigin false hits (they contain no bare x:/y:)
            return p
    return None


def selector_hits_positioned(sel, has_any, ids, classes, tags):
    """Does this selector target a transform-positioned SVG element?"""
    for one in sel.split(","):
        one = one.strip()
        if not one:
            continue
        # attribute selector [transform] → matches any positioned element
        if "[transform" in one.replace(" ", "") and has_any:
            return True
        # last simple token in a descendant selector
        token = re.split(r"[ >+~]", one)[-1]
        # #id
        for m in re.finditer(r"#([\w-]+)", token):
            if m.group(1) in ids:
                return True
        # .class
        for m in re.finditer(r"\.([\w-]+)", token):
            if m.group(1) in classes:
                return True
        # bare tag (no # or .) e.g. "g", "rect"
        bare = re.sub(r"[\[#.].*$", "", token).lower()
        if bare and bare in tags:
            return True
    return False


def _vars_has(vtext, props):
    for p in props:
        if re.search(r'(?<![\w$])' + re.escape(p) + r'\s*:', vtext):
            return p
    return None


def scan_file(path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    pos_any, pids, pcls, ptags = positioned_elements(txt)
    svg_any, sids, scls, stags = svg_elements(txt)
    if not svg_any and not pos_any:
        return []
    hits = []
    for pos, sel, vtext in tween_calls(txt):
        # RULE 1: any transform prop on an element positioned by a transform="…" attribute
        if pos_any:
            prop = vars_animate_transform(vtext)
            if prop and selector_hits_positioned(sel, pos_any, pids, pcls, ptags):
                hits.append((line_of(txt, pos),
                             f"GSAP tween animates transform prop '{prop}' on selector "
                             f"\"{sel}\" — an SVG element positioned by a transform=\"translate/"
                             f"rotate/…\" attribute → GSAP overwrites it and the element JUMPS off "
                             f"position (物体飞出画面). 只动 autoAlpha / 嵌套静态外层<g> / 用 "
                             f"attr:{{transform:'…'}} 写全量, 不要用裸 x/y/scale。"))
                continue
        # RULE 2: scale/rotation on an SVG element with a **px** transformOrigin (需用 svgOrigin)
        if svg_any:
            srp = _vars_has(vtext, SCALE_ROT_PROPS)
            if srp and PX_ORIGIN_RE.search(vtext) and "svgOrigin" not in vtext \
                    and selector_hits_positioned(sel, svg_any, sids, scls, stags):
                hits.append((line_of(txt, pos),
                             f"GSAP '{srp}' on SVG selector \"{sel}\" 使用了 **px** 的 "
                             f"transformOrigin → 缩放/旋转会把元素甩飞或错位 (物体飞出画面). "
                             f"SVG 请改用 svgOrigin:\"x y\"(用户坐标系, 如 svgOrigin:\"470 270\"), "
                             f"或把元素套进 <g transform=\"translate(...)\"> 再对内层缩放。"))
    return hits


def main():
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
        print(f"\nFAIL: {total} SVG transform-animation issue(s) (元素会飞出/错位).")
        print("FIX:")
        print("  [规则1] 不要对带 transform=\"translate/rotate/…\" 属性的 SVG 元素补间 "
              "x/y/rotation/scale/… — GSAP 会覆盖属性导致元素飞出。只动 autoAlpha / 嵌套静态外层<g> / "
              "用 attr:{transform:'…'} 写全量。")
        print("  [规则2] 对 SVG 元素做 scale/rotation 时不要用 px 的 transformOrigin — "
              "改用 svgOrigin:\"x y\"(用户坐标系)，或把元素套进 <g transform=\"translate(...)\"> "
              "再对内层缩放。px transformOrigin 会把远离原点的组甩飞。")
        return 1
    print("OK: no risky SVG transform animations (no clobbered transform attr, no px transformOrigin scale/rot).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
