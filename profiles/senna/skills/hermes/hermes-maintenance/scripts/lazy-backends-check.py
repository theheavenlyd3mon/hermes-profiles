#!/usr/bin/env python3
"""Which LAZY_DEPS backends are currently installed in the Hermes venv?

Run with the Hermes venv interpreter so it sees the same site-packages:
    ~/.hermes/hermes-agent/venv/bin/python3 lazy-backends-check.py

Output: three groups — fully installed / partial (some specs present,
usually just shared deps) / missing (would lazy-install on first use).
Missing is NOT a fault; it means the feature has never been used.
"""
import os, sys
sys.path.insert(0, os.path.expanduser("~/.hermes/hermes-agent"))
from importlib import metadata
from tools.lazy_deps import LAZY_DEPS

def base_pkg(spec: str) -> str:
    return spec.split("[", 1)[0].split("==", 1)[0].split(">=", 1)[0].split("<", 1)[0].strip()

def check(spec: str):
    name = base_pkg(spec)
    try:
        return f"{name}=={metadata.version(name)}"
    except metadata.PackageNotFoundError:
        return None

rows = []
for feat, specs in sorted(LAZY_DEPS.items()):
    present = [v for v in (check(s) for s in specs) if v]
    rows.append((feat, present, specs))

full = [r for r in rows if len(r[1]) == len(r[2])]
partial = [r for r in rows if 0 < len(r[1]) < len(r[2])]
none = [r for r in rows if not r[1]]

print(f"LAZY_DEPS features: {len(rows)} | fully installed: {len(full)} | partial: {len(partial)} | missing: {len(none)}\n")
print("=== FULLY INSTALLED ===")
for feat, present, _ in full:
    print(f"  {feat:28s} {' '.join(present)}")
print("\n=== PARTIAL ===")
for feat, present, specs in partial:
    print(f"  {feat:28s} have: {' '.join(present)}")
    print(f"  {'':28s} want: {', '.join(specs)}")
print("\n=== MISSING (would lazy-install on first use) ===")
for feat, _, specs in none:
    print(f"  {feat:28s} {', '.join(specs)}")
