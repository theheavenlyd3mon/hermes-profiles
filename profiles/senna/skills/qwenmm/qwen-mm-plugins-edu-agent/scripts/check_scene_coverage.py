#!/usr/bin/env python3
r"""
check_scene_coverage.py — Pre-render gate: enforce scene decomposition & wiring.

WHY (reproducibility): the biggest run-to-run quality swing comes from the BUILD step
deviating from the storyboard. In a flaky run the model plans N scenes in STORYBOARD.md
(e.g. one per special ray / per solution step) but then CRAMS them into 1–2 oversized
compositions, which under-render (missing axis, blank halves). A good run builds one
composition per planned scene. This gate makes that deterministic.

Checks (all on `dist/`):
  1. Every `data-composition-src` referenced by index.html exists on disk.            [FAIL]
  2. Every composition file registers a timeline on `window.__timelines`.             [FAIL]
  3. index.html wires at least as many scene clips as STORYBOARD.md plans
     (built >= planned). STORYBOARD.md is read from dist/.. (project root);
     planned = number of `### Scene` headings. Skipped if no storyboard / 0 headings.  [FAIL]

Usage:
    python3 check_scene_coverage.py [dist_dir]    # default ./dist
Exit 0 = clean, 1 = a coverage problem (or no index.html found).
"""

import re
import sys
from pathlib import Path

RE_SRC = re.compile(r'data-composition-src\s*=\s*"([^"]+)"', re.I)
# A planned scene heading: "### Scene 1: ..." or "### Scene: mt-...". Requires a colon so
# section headings like "## Scene Timing" / "## Per-Scene Direction" are NOT counted.
RE_SCENE_HEADING = re.compile(r"^#{2,4}\s*Scene\s*\d*\s*[:：]", re.I | re.M)


def main() -> int:
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    if not dist.is_dir():
        print(f"ERROR: dist dir not found: {dist}", file=sys.stderr)
        return 1
    index = dist / "index.html"
    if not index.exists():
        print(f"ERROR: {index} not found (root composition must exist)", file=sys.stderr)
        return 1

    idx_txt = index.read_text(encoding="utf-8", errors="replace")
    srcs = RE_SRC.findall(idx_txt)
    fails = []

    if not srcs:
        fails.append("index.html wires NO scene compositions (no data-composition-src found) — "
                     "build one composition per storyboard scene and reference each in index.html.")

    # 1 + 2: each referenced composition exists and registers a timeline
    seen = []
    for src in srcs:
        f = (dist / src).resolve()
        if f not in seen:
            seen.append(f)
        if not f.exists():
            fails.append(f"index.html references missing composition: {src}")
            continue
        ctxt = f.read_text(encoding="utf-8", errors="replace")
        if "window.__timelines" not in ctxt:
            fails.append(f"{src}: does not register a timeline on `window.__timelines` "
                         "(scene will not animate).")

    built = len(set(srcs))

    # 3: built >= planned (from STORYBOARD.md at project root)
    planned = 0
    sb = None
    for cand in (dist.parent / "STORYBOARD.md", dist / "STORYBOARD.md"):
        if cand.exists():
            sb = cand
            break
    if sb is not None:
        planned = len(RE_SCENE_HEADING.findall(sb.read_text(encoding="utf-8", errors="replace")))
        if planned and built < planned:
            fails.append(f"STORYBOARD.md plans {planned} scenes but index.html only wires {built} "
                         f"composition(s) — do NOT cram multiple planned scenes into one file. "
                         f"Build one composition per planned scene (one special ray / one solution "
                         f"step per scene).")

    if fails:
        for m in fails:
            print(f"{m}")
        print(f"\nFAIL: scene coverage problem(s): {len(fails)}. "
              f"(built={built}, planned={planned or 'n/a'})")
        print("FIX: one composition per storyboard scene; every scene wired in index.html via "
              "data-composition-src; every composition registers window.__timelines[...].")
        return 1

    print(f"OK: scene coverage — built {built} composition(s), "
          f"planned {planned or 'n/a'}, all exist and register timelines.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
