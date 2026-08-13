#!/usr/bin/env python3
r"""
check_circuit_inventory.py — Pre-render gate for circuit **component inventory**
correctness (电路元件清单正确性).

The other circuit gates only check layout/wiring/polarity (Section 12 checklist).
None of them checks the *semantic* correctness of the component SET. The most common
semantic failure is a **duplicated instrument**: a rectangular-loop wiring diagram that
draws the SAME single-instance instrument twice — e.g. two "变阻器" (rheostat) boxes in
series — usually because the author padded an empty side of the rectangle with an extra
box to "balance" the loop. A K12 experiment circuit has exactly ONE of each of these
instruments; two is a physics error.

RULE — single-instance instruments must appear at most once per circuit scene.
    Counted instruments (each essentially never duplicated in a K12 circuit):
        变阻器 / 滑动变阻器   (rheostat)
        电流表               (ammeter)
        电压表               (voltmeter)
        开关 / 电键          (switch)
    Resistors (R, R₁, R₂) and bulbs (L₁, L₂) CAN legitimately repeat, so they are
    NOT counted here. Only SVG <text> labels *inside* an <svg> are counted (HTML info
    pills / legends like "电流表 A：串联在干路" are ignored).

Only files that look like a circuit scene are scanned (avoids false positives on
non-circuit scenes).

Usage:
    python3 check_circuit_inventory.py [dist_dir]     # default ./dist
Exit 0 = clean, 1 = a duplicated single-instance instrument found.
"""

import re
import sys
from pathlib import Path

from _shared import iter_compositions, line_of

# Single-instance instruments — canonical keyword -> human name.
# Order matters: more specific first so "滑动变阻器" maps to 变阻器 once (via containment).
INSTRUMENTS = [
    ("变阻器", "变阻器 (rheostat/滑动变阻器)"),
    ("电流表", "电流表 (ammeter)"),
    ("电压表", "电压表 (voltmeter)"),
    ("电键", "开关 (switch)"),
    ("开关", "开关 (switch)"),
]

# A file is treated as a circuit scene if it contains at least TWO of these signals.
CIRCUIT_SIGNALS = ("变阻器", "电流表", "电压表", "开关", "电键", "电源", "电池",
                   "电路", "电流", "电压", "sch-battery", "sch-ammeter",
                   "sch-voltmeter", "sch-switch", "sch-resistor")


def strip_tags(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"&[a-zA-Z#0-9]+;", "", s)
    return s.strip()


def is_circuit_scene(txt):
    return sum(1 for s in CIRCUIT_SIGNALS if s in txt) >= 2


def canonical_instrument(content):
    """Map an SVG text label to a single-instance instrument keyword, or None.
    Uses containment so '滑动变阻器' -> 变阻器. First match wins (specific first)."""
    for kw, _name in INSTRUMENTS:
        if kw in content:
            return kw
    return None


def scan_file(path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    if not is_circuit_scene(txt):
        return []
    hits = []
    # Count PER <svg> block (a single circuit diagram), not across the whole file.
    # This keeps "correct vs wrong wiring" comparison scenes safe: they draw each
    # circuit in a SEPARATE <svg>, so one voltmeter per svg does not trip the rule —
    # while two 变阻器 inside ONE circuit diagram (the real bug) still does.
    for sm in re.finditer(r"<svg\b[^>]*>.*?</svg>", txt, re.S):
        svg = sm.group(0)
        base = sm.start()
        seen = {}  # instrument keyword -> list of (line, label)
        for tm in re.finditer(r"<text\b[^>]*>(.*?)</text>", svg, re.S):
            content = strip_tags(tm.group(1))
            if not content:
                continue
            kw = canonical_instrument(content)
            if kw is None:
                continue
            seen.setdefault(kw, []).append((line_of(txt, base + tm.start()), content))
        for kw, occ in seen.items():
            if len(occ) > 1:
                name = next(n for k, n in INSTRUMENTS if k == kw)
                lines = ", ".join(f"line {ln} ('{lbl}')" for ln, lbl in occ)
                for ln, lbl in occ:
                    hits.append((ln,
                                 f"duplicated single-instance instrument {name}: appears "
                                 f"{len(occ)}× in ONE circuit diagram [{lines}] — a K12 circuit "
                                 f"has exactly ONE {kw}; do NOT add a second to fill/balance "
                                 f"the loop (短边只走导线即可)"))
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
        print(f"\nFAIL: {total} duplicated-instrument occurrence(s) in circuit scene(s).")
        print("FIX:")
        print("  - Each of 变阻器/电流表/电压表/开关 must appear EXACTLY ONCE per circuit "
              "(these are single-instance instruments in K12 experiments).")
        print("  - If you duplicated one to fill a side of the rectangular loop, DELETE the "
              "extra box — an empty side may be just a wire (导线), it does not need a component.")
        print("  - Verify the component set matches the problem's actual circuit before render.")
        return 1
    print(f"OK: no duplicated single-instance instruments across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
