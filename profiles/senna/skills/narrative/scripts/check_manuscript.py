#!/usr/bin/env python3
"""Mechanical manuscript checks for narrative v2 project mode.

Usage:
  python check_manuscript.py /path/to/manuscript/{project}

Exits 0 if no blockers; 1 if blockers found.
Does NOT judge moral ambiguity / emotional range — those need a reviewer.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

TIER1 = [
    r"\bdelve\b", r"\butilize\b", r"\bleverage\b", r"\bfacilitate\b",
    r"\belucidate\b", r"\bembark\b", r"\bendeavor\b", r"\bencompass\b",
    r"\bmultifaceted\b", r"\btapestry\b", r"\btestament\b", r"\bparadigm\b",
    r"\bsynerg", r"\bholistic\b", r"\bcataly[sz]", r"\bjuxtapos",
    r"\bnuanced\b", r"\brealm\b", r"\bmyriad\b", r"\bplethora\b",
    r"\btapestry of\b", r"\blandscape\b",
]
TIER1_RE = re.compile("|".join(TIER1), re.I)
NOT_JUST = re.compile(r"not just\b.{0,40}\bbut\b", re.I)
EM_DASH = re.compile(r"—|--")
FICTION_TELLS = [
    r"a sense of \w+",
    r"couldn't help but feel",
    r"the weight of \w+",
    r"the air was thick with",
    r"eyes widened",
    r"a wave of \w+ washed",
    r"a pang of \w+",
    r"heart pounded in (his|her|their) chest",
    r"piercing (blue|green|grey|gray|brown) eyes",
    r"a knowing smile",
]
TELLS_RE = re.compile("|".join(FICTION_TELLS), re.I)


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def chapter_files(root: Path) -> list[Path]:
    ch = root / "chapters"
    if not ch.is_dir():
        return []
    files = sorted(ch.rglob("*.md"))
    return [f for f in files if not f.name.startswith("_")]


def check_tier1(text: str) -> list[str]:
    return sorted({m.group(0).lower() for m in TIER1_RE.finditer(text)})


def check_em_dashes(text: str, words_per_page: int = 300) -> float:
    n = len(EM_DASH.findall(text))
    words = max(1, len(text.split()))
    pages = max(1.0, words / words_per_page)
    return n / pages


def check_foreshadow(root: Path) -> list[str]:
    issues = []
    bank = root / "foreshadow-bank.md"
    if not bank.exists():
        issues.append("missing foreshadow-bank.md")
        return issues
    text = read_text(bank)
    if re.search(r"\|\s*dangling\s*\|", text, re.I) or re.search(r"\bdangling\b", text, re.I):
        # crude: flag if status cell is dangling
        for line in text.splitlines():
            if re.search(r"\bdangling\b", line, re.I) and line.strip().startswith("|"):
                issues.append(f"dangling plant: {line.strip()[:120]}")
    return issues


def check_ledger(root: Path) -> list[str]:
    issues = []
    ledger = root / "plot-ledger.md"
    if not ledger.exists():
        issues.append("missing plot-ledger.md")
        return issues
    text = read_text(ledger)
    for required in ("Catalyst", "Midpoint", "All Is Lost", "Final Image"):
        if required.lower() not in text.lower():
            issues.append(f"ledger missing beat row for '{required}'")
    return issues


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: check_manuscript.py <manuscript_project_dir>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).expanduser().resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2

    blockers: list[str] = []
    warnings: list[str] = []

    for req in ("concept.md", "plot-ledger.md", "character-sheet.md", "worldbuilding.md"):
        if not (root / req).exists() and not (
            req == "character-sheet.md" and (root / "characters").is_dir()
        ):
            warnings.append(f"missing {req}")

    blockers.extend(check_ledger(root))
    blockers.extend(check_foreshadow(root))

    corpus = []
    for f in chapter_files(root):
        corpus.append(read_text(f))
    full = "\n".join(corpus)

    if full.strip():
        t1 = check_tier1(full)
        if t1:
            blockers.append(f"Tier-1 banned words: {', '.join(t1)}")
        nj = NOT_JUST.findall(full)
        if nj:
            blockers.append(f"'not just X but Y' count: {len(nj)}")
        ed = check_em_dashes(full)
        if ed > 2.5:
            blockers.append(f"em-dash density ~{ed:.1f}/page (cap ~2)")
        tells = TELLS_RE.findall(full)
        if tells:
            warnings.append(f"fiction AI-tell phrases: {len(tells)}")
    else:
        warnings.append("no chapter markdown found under chapters/")

    print(f"# check_manuscript: {root.name}")
    if blockers:
        print("## BLOCKERS")
        for b in blockers:
            print(f"- {b}")
    if warnings:
        print("## WARNINGS")
        for w in warnings:
            print(f"- {w}")
    if not blockers and not warnings:
        print("OK — no mechanical issues found")
    elif not blockers:
        print("OK — warnings only (no blockers)")
    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
