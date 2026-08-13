#!/usr/bin/env python3
r"""
check_geometry_verification.py — Pre-render gate: enforce mathematically verified
geometry coordinates in SVG diagrams.

WHY: When building geometry scenes, the LLM may place SVG vertex coordinates by
visual estimation instead of computing them from the problem's mathematical
constraints. This produces diagrams where lines that should be parallel visibly
slant, intersection points are in the wrong place, and midpoints are off.

WHAT IT CHECKS: Every composition that contains an SVG with 3+ geometric point
labels (single uppercase letters like A, B, C, D, E, F in <text> elements) must
have a structured <!-- GEOMETRY VERIFICATION --> block with:
  - A POINTS: line declaring all vertex coordinates
  - One or more ASSERT lines declaring geometric constraints
The script parses the assertions and verifies them mathematically against the
declared coordinates.

ASSERTION TYPES:
  parallel P1 P2 P3 P4      — line P1P2 ∥ P3P4 (cross product ≈ 0)
  perpendicular P1 P2 P3 P4 — line P1P2 ⊥ P3P4 (dot product ≈ 0)
  midpoint M P1 P2           — M = (P1+P2)/2
  on_line P L1 L2            — P on infinite line through L1, L2
  on_segment P L1 L2         — P on segment L1-L2 (on_line + between)
  intersection I L1 L2 L3 L4 — I = intersection of lines L1L2 and L3L4
  ratio |P1P2| |P3P4| R      — dist(P1,P2)/dist(P3,P4) = R
  collinear P1 P2 P3         — three points collinear (triangle area ≈ 0)

TOLERANCES:
  Position: 1.0 SVG unit (sub-pixel at typical viewBox scale)
  Ratio:    2% relative error

Usage:
    python3 check_geometry_verification.py [dist_dir]    # default ./dist
Exit 0 = clean, 1 = verification failure or missing block.
"""

import math
import re
import sys
from pathlib import Path

from _shared import line_of

POS_TOL = 1.0
RATIO_TOL = 0.02

RE_SVG_BLOCK = re.compile(r"<svg\b[^>]*>(.*?)</svg>", re.S | re.I)
RE_GEO_LABEL = re.compile(r"<text\b[^>]*>\s*([A-Z][A-Z0-9'₁₂₃]?)\s*</text>")

RE_GEO_BLOCK = re.compile(
    r"<!--\s*GEOMETRY\s+VERIFICATION\s*\n(.*?)-->", re.S
)
RE_POINTS_LINE = re.compile(r"^\s*POINTS:\s*(.+)$", re.M | re.I)
RE_POINT = re.compile(
    r"([A-Z][A-Z0-9'₁₂₃]*)\s*=\s*\(\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\)"
)
RE_ASSERT_LINE = re.compile(r"^\s*ASSERT\s+(.+)$", re.M | re.I)
RE_SEG = re.compile(r"\|([A-Z][A-Z0-9'₁₂₃]*)([A-Z][A-Z0-9'₁₂₃]*)\|")


def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def vec(p1, p2):
    return (p2[0] - p1[0], p2[1] - p1[1])


def dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]


def cross(v1, v2):
    return v1[0] * v2[1] - v1[1] * v2[0]


def vlength(v):
    return math.sqrt(v[0] ** 2 + v[1] ** 2)


# ── Assertion handlers ──────────────────────────────────────────────────

def check_parallel(pts, args):
    p1, p2, p3, p4 = args
    v1 = vec(pts[p1], pts[p2])
    v2 = vec(pts[p3], pts[p4])
    len1, len2 = vlength(v1), vlength(v2)
    if len1 < 1e-9 or len2 < 1e-9:
        return False, "degenerate zero-length vector"
    sin_angle = abs(cross(v1, v2)) / (len1 * len2)
    deviation = sin_angle * max(len1, len2)
    ok = deviation < POS_TOL
    return ok, f"max endpoint deviation = {deviation:.2f}px (limit {POS_TOL})"


def check_perpendicular(pts, args):
    p1, p2, p3, p4 = args
    v1 = vec(pts[p1], pts[p2])
    v2 = vec(pts[p3], pts[p4])
    len1, len2 = vlength(v1), vlength(v2)
    if len1 < 1e-9 or len2 < 1e-9:
        return False, "degenerate zero-length vector"
    cos_angle = abs(dot(v1, v2)) / (len1 * len2)
    deviation = cos_angle * max(len1, len2)
    ok = deviation < POS_TOL
    return ok, f"max endpoint deviation = {deviation:.2f}px (limit {POS_TOL})"


def check_midpoint(pts, args):
    m, p1, p2 = args
    expected = ((pts[p1][0] + pts[p2][0]) / 2, (pts[p1][1] + pts[p2][1]) / 2)
    d = dist(pts[m], expected)
    ok = d < POS_TOL
    return ok, f"|{m} - midpoint({p1},{p2})| = {d:.2f}px (limit {POS_TOL})"


def check_on_line(pts, args):
    p, l1, l2 = args
    v_line = vec(pts[l1], pts[l2])
    v_point = vec(pts[l1], pts[p])
    line_len = vlength(v_line)
    if line_len < 1e-9:
        return False, f"degenerate line ({l1} == {l2})"
    d = abs(cross(v_line, v_point)) / line_len
    ok = d < POS_TOL
    return ok, f"dist({p} to line {l1}{l2}) = {d:.2f}px (limit {POS_TOL})"


def check_on_segment(pts, args):
    p, l1, l2 = args
    ok_line, detail_line = check_on_line(pts, args)
    if not ok_line:
        return False, detail_line
    v_line = vec(pts[l1], pts[l2])
    v_point = vec(pts[l1], pts[p])
    line_len_sq = dot(v_line, v_line)
    t = dot(v_point, v_line) / line_len_sq
    margin = POS_TOL / math.sqrt(line_len_sq)
    ok = (-margin <= t <= 1 + margin)
    return ok, f"t = {t:.4f} (expected 0..1, margin {margin:.4f})"


def check_intersection(pts, args):
    i, l1, l2, l3, l4 = args
    d1 = vec(pts[l1], pts[l2])
    d2 = vec(pts[l3], pts[l4])
    denom = cross(d1, d2)
    if abs(denom) < 1e-9:
        return False, f"lines {l1}{l2} and {l3}{l4} are parallel (no intersection)"
    diff = vec(pts[l1], pts[l3])
    t = cross(diff, d2) / denom
    expected = (pts[l1][0] + t * d1[0], pts[l1][1] + t * d1[1])
    d = dist(pts[i], expected)
    ok = d < POS_TOL
    return ok, (
        f"|{i} - computed intersection| = {d:.2f}px (limit {POS_TOL}), "
        f"expected ({expected[0]:.1f}, {expected[1]:.1f}), "
        f"got ({pts[i][0]:.1f}, {pts[i][1]:.1f})"
    )


def check_ratio(pts, args):
    seg1, seg2, r_str = args
    m1 = RE_SEG.match(seg1)
    m2 = RE_SEG.match(seg2)
    if not m1 or not m2:
        return False, f"cannot parse segment notation: {seg1}, {seg2}"
    p1, p2 = m1.group(1), m1.group(2)
    p3, p4 = m2.group(1), m2.group(2)
    for name in [p1, p2, p3, p4]:
        if name not in pts:
            return False, f"point '{name}' in segment not defined in POINTS"
    r_expected = float(r_str)
    d1 = dist(pts[p1], pts[p2])
    d2 = dist(pts[p3], pts[p4])
    if d2 < 1e-9:
        return False, "denominator segment has zero length"
    r_actual = d1 / d2
    if r_expected == 0:
        rel_err = abs(r_actual)
    else:
        rel_err = abs(r_actual - r_expected) / abs(r_expected)
    ok = rel_err < RATIO_TOL
    return ok, (
        f"|{p1}{p2}|/|{p3}{p4}| = {d1:.1f}/{d2:.1f} = {r_actual:.4f} "
        f"(expected {r_expected}, err {rel_err:.4f}, limit {RATIO_TOL})"
    )


def check_collinear(pts, args):
    p1, p2, p3 = args
    v1 = vec(pts[p1], pts[p2])
    v2 = vec(pts[p1], pts[p3])
    area2 = abs(cross(v1, v2))
    max_side = max(vlength(v1), vlength(v2), dist(pts[p2], pts[p3]))
    if max_side < 1e-9:
        return True, "all three points coincide"
    h = area2 / max_side
    ok = h < POS_TOL
    return ok, f"height from longest side = {h:.2f}px (limit {POS_TOL})"


HANDLERS = {
    "parallel": (4, check_parallel),
    "perpendicular": (4, check_perpendicular),
    "midpoint": (3, check_midpoint),
    "on_line": (3, check_on_line),
    "on_segment": (3, check_on_segment),
    "intersection": (5, check_intersection),
    "ratio": (3, check_ratio),
    "collinear": (3, check_collinear),
}


# ── Scene detection ─────────────────────────────────────────────────────

def is_geometry_scene(txt: str) -> set:
    """Return the set of geometric point labels if the file is a geometry scene, else empty set."""
    all_labels = set()
    for svg_m in RE_SVG_BLOCK.finditer(txt):
        svg_content = svg_m.group(1)
        labels = set(RE_GEO_LABEL.findall(svg_content))
        if len(labels) >= 3:
            all_labels.update(labels)
    return all_labels


# ── Verification ────────────────────────────────────────────────────────

def verify_geometry(path: Path, txt: str, labels: set):
    """Parse and verify the GEOMETRY VERIFICATION block. Returns list of (line, msg, detail)."""
    fails = []
    block_m = RE_GEO_BLOCK.search(txt)

    if not block_m:
        fails.append((
            0,
            f"MISSING GEOMETRY VERIFICATION — geometry SVG detected "
            f"(labels: {', '.join(sorted(labels))}) but no "
            f"<!-- GEOMETRY VERIFICATION --> block found.",
            "Add a GEOMETRY VERIFICATION block above the SVG with POINTS and ASSERTs. "
            "See step-5-build-components.md 'Geometry Coordinate Accuracy'.",
        ))
        return fails

    block_text = block_m.group(1)
    block_start_line = line_of(txt, block_m.start())

    pts_m = RE_POINTS_LINE.search(block_text)
    if not pts_m:
        fails.append((block_start_line, "PARSE ERROR: no POINTS line in GEOMETRY VERIFICATION block", ""))
        return fails

    points = {}
    for pm in RE_POINT.finditer(pts_m.group(1)):
        points[pm.group(1)] = (float(pm.group(2)), float(pm.group(3)))

    if len(points) < 3:
        fails.append((
            block_start_line,
            f"PARSE ERROR: POINTS line defines only {len(points)} point(s) (need >= 3)",
            "",
        ))
        return fails

    assert_count = 0
    for am in RE_ASSERT_LINE.finditer(block_text):
        assert_count += 1
        line_in_block = block_text[: am.start()].count("\n")
        line_no = block_start_line + line_in_block

        tokens = am.group(1).split()
        if not tokens:
            fails.append((line_no, "PARSE ERROR: empty ASSERT", ""))
            continue

        atype = tokens[0].lower()
        args = tokens[1:]

        if atype not in HANDLERS:
            fails.append((
                line_no,
                f"PARSE ERROR: unknown assertion type '{atype}'",
                f"Valid types: {', '.join(sorted(HANDLERS))}",
            ))
            continue

        expected_argc, handler = HANDLERS[atype]
        if len(args) != expected_argc:
            fails.append((
                line_no,
                f"PARSE ERROR: {atype} expects {expected_argc} args, got {len(args)}: {' '.join(args)}",
                "",
            ))
            continue

        if atype == "ratio":
            parse_ok = True
            for seg_token in args[:2]:
                seg_match = RE_SEG.match(seg_token)
                if not seg_match:
                    fails.append((line_no, f"PARSE ERROR: cannot parse segment '{seg_token}' (expected |XY| format)", ""))
                    parse_ok = False
                    break
                for pname in [seg_match.group(1), seg_match.group(2)]:
                    if pname not in points:
                        fails.append((line_no, f"PARSE ERROR: point '{pname}' in segment '{seg_token}' not in POINTS", ""))
                        parse_ok = False
            if not parse_ok:
                continue
            ok, detail = handler(points, args)
            if not ok:
                fails.append((line_no, f"FAILED: {atype} {' '.join(args)}", detail))
        else:
            missing = [a for a in args if a not in points]
            if missing:
                fails.append((
                    line_no,
                    f"PARSE ERROR: point(s) {', '.join(missing)} in ASSERT {atype} not defined in POINTS",
                    "",
                ))
                continue
            ok, detail = handler(points, args)
            if not ok:
                fails.append((line_no, f"FAILED: {atype} {' '.join(args)}", detail))

    if assert_count == 0:
        fails.append((
            block_start_line,
            "GEOMETRY VERIFICATION block has no ASSERT lines — add at least one constraint",
            "",
        ))

    return fails


# ── Main ────────────────────────────────────────────────────────────────

def main() -> int:
    dist_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    if not dist_dir.is_dir():
        print(f"ERROR: dist dir not found: {dist_dir}", file=sys.stderr)
        return 1

    files = sorted(set(list(dist_dir.glob("index.html")) + list(dist_dir.glob("compositions/*.html"))))
    if not files:
        print(f"ERROR: no index.html / compositions/*.html under {dist_dir}", file=sys.stderr)
        return 1

    total_fails = 0
    geo_files = 0
    for f in files:
        txt = f.read_text(encoding="utf-8", errors="replace")
        labels = is_geometry_scene(txt)
        if not labels:
            continue
        geo_files += 1
        for line_no, msg, detail in verify_geometry(f, txt, labels):
            total_fails += 1
            print(f"{f}:{line_no}: {msg}")
            if detail:
                print(f"    {detail}")

    if total_fails:
        print(f"\nFAIL: {total_fails} geometry verification failure(s) across {geo_files} file(s).")
        print("FIX: recompute coordinates from the problem's mathematical constraints.")
        print("     Update the <!-- GEOMETRY VERIFICATION --> block with correct POINTS and ASSERTs.")
        print("     See step-5-build-components.md 'Geometry Coordinate Accuracy'.")
        return 1

    if geo_files:
        print(f"OK: {geo_files} geometry scene(s) verified — all assertions passed.")
    else:
        print("OK: no geometry scenes detected — nothing to verify.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
