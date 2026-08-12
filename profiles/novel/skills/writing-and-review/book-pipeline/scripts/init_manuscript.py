#!/usr/bin/env python3
"""Scaffold a manuscript/{project}/ tree for the book-writer pipeline.

Usage:
  python init_manuscript.py <project-slug> [--root /path/to/parent] [--title "Title"]

Creates concept, ledgers, voice stub, chapters/, reviews/, exports/.
"""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

CONCEPT = """# Concept — {title}

## Logline
(one sentence: who, wants, because, but)

## Tone anchor
melancholy | dread | restraint | bright action — pick one:
**melancholy** (default for murim / dark Eastern)

## MICE mix
- Primary:
- Secondary:
- Close order (reverse of open):

## Target length
45000 words (short novel; $3.99–4.99 band)

## Genre / comps
murim martial-arts noir / dark Eastern fantasy

## Created
{today}
"""

CANON = """# Canon — truth ledger

Only facts that are true in-story. Add new facts when introduced; never contradict without an explicit retcon note.

## Names
-

## Places
-

## Rules / magic costs
-

## Timeline
-
"""

LEDGER = """# Plot ledger

Framework: Save the Cat (default) | Harmon | PPP

| Beat | % Mark | Status | Chapter | Scenes | Notes |
|------|--------|--------|---------|--------|-------|
| Opening Image | 0-1% | planned | | | |
| Theme Stated | ~5% | planned | | | (not by protagonist) |
| Setup | 1-10% | planned | | | |
| Catalyst | ~11% | planned | | | EXTERNAL event |
| Debate | 11-23% | planned | | | |
| Break Into Two | ~23% | planned | | | PROTAG CHOICE |
| B Story | ~27% | planned | | | |
| Fun and Games | 26-50% | planned | | | |
| Midpoint | ~50% | planned | | | reverse trajectory |
| Bad Guys Close In | 50-68% | planned | | | |
| All Is Lost | ~68% | planned | | | whiff of death |
| Dark Night | 68-77% | planned | | | |
| Break Into Three | ~77% | planned | | | |
| Finale | 77-97% | planned | | | |
| Final Image | ~99% | planned | | | mirrors opening |

Status: planned | drafted | reviewed | done
"""

FORESHADOW = """# Foreshadow bank

| ID | Plant (ch) | Element | Type | Payoff (ch) | Status |
|----|------------|---------|------|-------------|--------|
| f-001 | | | | | open |

Status: open | planted | payoff | dangling | red-herring

Export fails if any row is `dangling` or payoff lacks plant.
"""

CHARS = """# Character sheet

## Protagonist

```yaml
name: 
sliders: { proactivity: 3, likability: 8, competence: 4 }
arc_type: positive
ghost: ""
wound: ""
lie: ""
want: ""
need: ""
dialogue_profile:
  vocabulary: terse
  formality: contracted
  tics: []
  metaphor_domain: 
  directness: high
  interrupt: submissive
  q_ratio: 0.3
```

## Supporting
(add blocks as needed)
"""

WORLD = """# Worldbuilding

## Pillars (pick 1–2 for depth)
- [ ] Physical
- [ ] Cultural
- [ ] Magical

## Magic / system — Three Laws
1. **Hard rules the reader understands** (First Law):
2. **Limitations ≥ powers; costs drive plot** (Second Law):
3. **Expand before inventing; no new powers last 25%** (Third Law):

## Societal implications (2–3 per speculative element)
1.
2.
3.

## Iceberg hints (unexplained on page, known to author)
-
"""

VOICE = """# Voice profile

```yaml
project: __SLUG__
tone_anchor: melancholy
register:
  level: low-literary
  person: close-third
  tense: past
banned_by_author:
  - delve
  - utilize
  - tapestry
  - realm
  - paradigm
allowed_register_words: []
rhythm_targets:
  avg_sentence_len: 14
  sentence_len_cv_min: 0.35
  em_dash_cap_per_page: 2
  paragraph_len_variance: high
metaphor_domains:
  global: [industrial, weather, martial]
  per_character: {}
forbidden_patterns: []
```

Calibrate from a 500-word sample before chapter drafting (style-revision playbook §3).
"""

MANIFEST = """title: "__TITLE__"
author: "Author"
framework: StC
target_words: 45000
voice_profile: voice-profile.md
genre: dark-fantasy-murim
status: planning
created: __TODAY__
"""

CHAPTER1 = """---
scene_id: ch01-sc01
beat: opening-image
try_fail: 
pov: 
status: planned
---

# Chapter 1

(draft here)
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", help="project folder name (kebab-case)")
    ap.add_argument("--root", default="manuscript", help="parent directory (default: manuscript)")
    ap.add_argument("--title", default=None, help="human title (default: slug title-cased)")
    args = ap.parse_args()

    title = args.title or args.slug.replace("-", " ").title()
    today = date.today().isoformat()
    root = Path(args.root).expanduser().resolve() / args.slug
    root.mkdir(parents=True, exist_ok=True)
    (root / "chapters").mkdir(exist_ok=True)
    (root / "outlines").mkdir(exist_ok=True)
    (root / "reviews").mkdir(exist_ok=True)
    (root / "exports").mkdir(exist_ok=True)

    files = {
        "concept.md": CONCEPT.format(title=title, today=today),
        "canon.md": CANON,
        "plot-ledger.md": LEDGER,
        "foreshadow-bank.md": FORESHADOW,
        "character-sheet.md": CHARS,
        "worldbuilding.md": WORLD,
        "voice-profile.md": VOICE.replace("__SLUG__", args.slug),
        "manuscript.yaml": MANIFEST.replace("__TITLE__", title).replace("__TODAY__", today),
        "outlines/synopsis.md": f"# Synopsis — {title}\n\n",
        "chapters/ch01.md": CHAPTER1,
    }
    for rel, body in files.items():
        path = root / rel
        if not path.exists():
            path.write_text(body, encoding="utf-8")
            print(f"created {path}")
        else:
            print(f"skip (exists) {path}")

    print(f"\nOK — manuscript scaffold at {root}")
    print("Next: fill concept.md + characters + ledger, then draft with narrative skill.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
