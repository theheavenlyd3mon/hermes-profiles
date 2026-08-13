#!/usr/bin/env python3
r"""
precheck.py — ONE pre-render gate that runs all math-tutorial render checks at once.

Run this from the project root (the parent of dist/) BEFORE `npx hyperframes render`:

    python3 "$EDU_SKILL_ROOT/scripts/precheck.py" dist

It runs every check in this scripts/ directory and prints a single consolidated report.
Exit 0 = all passed (safe to render). Exit 1 = at least one failed (DO NOT render yet).

Self-correction loop (this is the intended workflow):
    1. run  python3 "$EDU_SKILL_ROOT/scripts/precheck.py" dist
    2. if it exits non-zero, READ each "FAIL" block — every line gives file:line and a fix
    3. apply the fixes to the offending composition(s) / index.html
    4. re-run precheck.py and repeat until it prints "ALL CHECKS PASSED"
    5. only then run the renderer

AUTO-FIX (runs before checks):
    fix_katex_escaping.py     — auto-doubles single backslashes in katex.render() JS strings
                                (fixes \dfrac→\\dfrac, \frac→\\frac, \times→\\times, etc.)

Checks run (each is also runnable on its own):
    check_composition_format.py — sub-compositions are HTML fragments, not full docs (else blank panels)
    check_asset_mirror.py     — GSAP/KaTeX/fonts mirrored into compositions/ (else blank scenes)
    check_katex_cjk.py        — no Chinese inside KaTeX (\text{秒} → □ tofu)
    check_katex_escaping.py   — LaTeX in JS strings double-escaped (\times not \\times → "imes")
    check_frac_unrendered.py  — no literal dfrac/frac{/rac{ in visible HTML text (unrendered fractions)
    check_composition_root_id.py — scene root has id matching data-composition-id when #<id> is used (else blank formulas)
    check_caption_size.py     — caption font-size 36–40px (not 64px giant subtitles)
    check_caption_safe_zone.py— scenes reserve bottom ~180px so the subtitle never covers content
    check_scene_layout.py     — .scene-content centers & fills the frame (else content piles at top)
    check_svg_label_overlap.py— no overlapping SVG <text> labels (标签文字重叠)
    check_svg_height_bound.py — SVG width:100% must bound its height (height:auto + tall viewBox → 场景突然变大)
    check_svg_node_graph.py   — node-graph: in-shape labels grouped/visible, arrows & labels clear of boxes
    check_no_hidden_content.py— no CSS opacity:0 / visibility:hidden (flaky blank scenes)
    check_svg_filter_bbox.py  — no glow/blur filter on axis-aligned <line> (invisible force arrows)
    check_no_glass.py         — no frosted glass / see-through panels (no 遮挡/occlusion)
    check_scene_coverage.py   — one composition per storyboard scene; all wired & timelined
    check_geometry_verification.py — geometry SVG coordinates verified against mathematical constraints
    check_circuit_inventory.py — no duplicated single-instance instrument (变阻器/电流表/电压表/开关) in a circuit scene
    check_circuit_closed.py — circuit loop closed: power source both terminals wired, no dangling wire endpoints
    check_svg_transform_anim.py — no GSAP transform-tween (x/y/rotation/scale) on a transform-positioned SVG element (else it flies off-screen)
"""

import subprocess
import sys
from pathlib import Path

CHECKS = [
    ("check_composition_format.py", "Sub-composition format (HTML fragment, not full document — else blank panels)"),
    ("check_asset_mirror.py", "Asset mirror (GSAP/KaTeX/fonts in compositions/)"),
    ("check_katex_cjk.py", "No Chinese inside KaTeX"),
    ("check_cjk_font.py", "Chinese text uses a CJK font (no NO GLYPH/豆腐块 from Inter/latin-only)"),
    ("check_katex_escaping.py", "LaTeX in JS strings double-escaped"),
    ("check_frac_unrendered.py", "No unrendered fractions (dfrac/frac/rac) in visible text"),
    ("check_composition_root_id.py", "Scene root has id matching data-composition-id when #<id> is used (else blank formulas / unstyled scene)"),
    ("check_caption_size.py", "Caption font-size not oversized"),
    ("check_caption_safe_zone.py", "Scenes reserve the bottom caption safe zone (no 字幕遮挡)"),
    ("check_caption_position.py", "Caption pinned to the bottom (not top/middle), root-level only"),
    ("check_caption_overflow.py", "Captions width-bounded & short (no off-frame overflow)"),
    ("check_scene_layout.py", "Scene content wrapper centers & fills the frame"),
    ("check_scene_overflow.py", "No gross oversize/overflow (排版过大, content clipped at edges)"),
    ("check_svg_height_bound.py", "SVG width:100% must bound its height (no height:auto blow-up → 场景突然变大)"),
    ("check_scene_fit.py", "Scene content fits inside 1920×1080 (headless-measured; content not clipped off top/bottom — 内容超出一屏被裁切)"),
    ("check_svg_label_overlap.py", "No overlapping SVG <text> labels (标签文字重叠)"),
    ("check_svg_label_on_figure.py", "SVG labels don't overlap the drawing (字母不压线/不压点)"),
    ("check_svg_node_graph.py", "Node-graph diagrams: in-shape labels grouped & visible, arrows/labels not overlapping boxes (箭头/文字与方框重叠)"),
    ("check_no_hidden_content.py", "No CSS-hidden content (no flaky blank scenes)"),
    ("check_svg_filter_bbox.py", "No glow/blur filter on axis-aligned <line> (invisible force arrows)"),
    ("check_svg_arrow.py", "SVG arrows well-formed (fixed-size heads, orient=auto heads point +x/正确方向, full-length lines — no giant/wrong-direction/invisible)"),
    ("check_no_glass.py", "No frosted glass / see-through panels (no occlusion)"),
    ("check_scene_coverage.py", "Scene coverage (one composition per storyboard scene)"),
    ("check_root_compositions.py", "Root references scenes via data-composition-src AND clips/roots declare data-width/height (no all-white / no shrunk-to-top-left scenes)"),
    ("check_geometry_verification.py", "Geometry coordinate verification (SVG math accuracy)"),
    ("check_circuit_inventory.py", "Circuit component inventory (no duplicated 变阻器/电流表/电压表/开关 — single-instance instruments)"),
    ("check_circuit_closed.py", "Circuit connectivity (电源两端接线 / 回路闭合 / 无悬空导线)"),
    ("check_svg_transform_anim.py", "No GSAP transform-tween on a transform-positioned SVG element (物体飞出画面)"),
    ("check_chromosome_example.py", "Chromosome/cell-division scenes follow the mitosis few-shot (纺锤丝牵引缩短动画 + 无360°转圈)"),
    ("check_smooth_curve.py", "Continuous curves are smooth, not sparse straight-chord polylines (不用分段直线逼近曲线 — 抛物线/双曲线/sin/衰减等)"),
    ("check_render_overlap.py", "Headless render-truth: no <text> painted under/over a box it doesn't belong to (文字被方框覆盖/压框 — 取食→取)"),
    ("check_splint_orientation.py", "Burning-splint test scene: flame (burning end) inserted INTO the vessel, not above the mouth (燃着木条方向不画反)"),
    ("check_animation_on_timeline.py", "All animation on the seekable paused timeline — no bare gsap.to()/@keyframes (否则动效渲不出来)"),
]

# Auto-fix scripts run BEFORE checks — they repair common issues automatically.
AUTO_FIXES = [
    ("fix_katex_escaping.py", "Auto-fix LaTeX backslash escaping in JS strings"),
]


def main() -> int:
    here = Path(__file__).resolve().parent
    dist = sys.argv[1] if len(sys.argv) > 1 else "dist"

    # Phase 1: Auto-fixes (repair common issues before checking)
    print("=" * 70)
    print(f"PRECHECK — math-tutorial render gates on: {dist}")
    print("=" * 70)

    print("\n--- Phase 1: Auto-fixes ---")
    for script, desc in AUTO_FIXES:
        path = here / script
        if not path.exists():
            print(f"[SKIP] {desc} — script not found: {path}")
            continue
        proc = subprocess.run(
            [sys.executable, str(path), dist],
            capture_output=True, text=True,
        )
        output = (proc.stdout + proc.stderr).strip()
        if output:
            for line in output.splitlines():
                print(f"  {line}")
        status = "DONE" if proc.returncode == 0 else "WARN"
        print(f"[{status}] {desc}")

    # Phase 2: Validation checks
    print("\n--- Phase 2: Validation checks ---")
    results = []  # (name, desc, rc, output)
    for script, desc in CHECKS:
        path = here / script
        if not path.exists():
            results.append((script, desc, 2, f"MISSING check script: {path}"))
            continue
        proc = subprocess.run(
            [sys.executable, str(path), dist],
            capture_output=True, text=True,
        )
        results.append((script, desc, proc.returncode, (proc.stdout + proc.stderr).strip()))

    failed = []
    for script, desc, rc, out in results:
        status = "PASS" if rc == 0 else "FAIL"
        if rc != 0:
            failed.append((script, desc, out))
        print(f"[{status}] {desc}  ({script})")
        if rc != 0:
            for line in out.splitlines():
                print(f"        {line}")

    print("-" * 70)
    if not failed:
        print("ALL CHECKS PASSED — safe to render.")
        return 0

    print(f"PRECHECK FAILED — {len(failed)} check(s) need fixing. DO NOT render yet.")
    print(f"Fix every file:line listed above, then re-run:  {sys.executable} {Path(__file__).resolve()} {dist}")
    print("Repeat until this prints 'ALL CHECKS PASSED'.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
