#!/usr/bin/env python3
r"""Shared helpers for the edu-agent render-check scripts.

These check scripts run standalone (invoked as subprocesses by precheck.py /
postcheck.py), so this module lives beside them in scripts/ and is imported as
`from _shared import ...` — which works because Python puts the script's own
directory on sys.path[0].

Only genuinely duplicated, behaviour-identical helpers belong here; per-check
logic stays in each check file.
"""

from __future__ import annotations

import re
from pathlib import Path


def line_of(text: str, idx: int) -> int:
    """1-based line number of character offset ``idx`` in ``text``."""
    return text.count("\n", 0, idx) + 1


def iter_compositions(dist: Path) -> list[Path]:
    """Every HTML file a check should scan: the root index plus each scene.

    Returns a sorted, de-duplicated list of ``index.html`` and
    ``compositions/*.html`` under ``dist``. Callers keep their own "empty →
    error" handling so their messages stay unchanged.
    """
    return sorted(
        set(list(dist.glob("index.html")) + list(dist.glob("compositions/*.html")))
    )


def attr(tag: str, name: str) -> str | None:
    """Value of attribute ``name`` in an HTML/SVG start-tag string.

    Handles both single- and double-quoted values, is case-insensitive on the
    attribute name, and escapes ``name``. Returns ``None`` when absent.
    """
    m = re.search(rf'\b{re.escape(name)}\s*=\s*"([^"]*)"', tag, re.I)
    if m:
        return m.group(1)
    m = re.search(rf"\b{re.escape(name)}\s*=\s*'([^']*)'", tag, re.I)
    return m.group(1) if m else None
