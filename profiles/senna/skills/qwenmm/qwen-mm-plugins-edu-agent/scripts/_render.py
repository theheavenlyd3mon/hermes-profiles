"""Shared headless-render helpers for the edu-agent post-render check scripts.

The scripts that drive a headless Chrome (check_scene_fit, check_render_overlap,
check_smooth_curve_render, check_circuit_closed, check_curves_rendered) each used to carry
byte-identical copies of these. They live here so there is one Chrome/Node resolution path.

Env is read via `env_config.get_env` (environment > ~/.qwen-mm-plugins/config > default), so the
Chrome binary and NODE_PATH can be set in the shared config file, not just exported in the shell.
"""

from __future__ import annotations

import glob
import os
import subprocess
import sys
from pathlib import Path

from env_config import get_env


def find_chrome() -> str | None:
    """Locate a Chrome/Chromium binary: explicit config > puppeteer cache > system install."""
    p = get_env("PUPPETEER_EXECUTABLE_PATH")
    if p and Path(p).is_file():
        return p
    for pat in (
        "/root/.cache/puppeteer/chrome/*/chrome-linux64/chrome",
        str(Path.home()) + "/.cache/puppeteer/chrome/*/chrome-linux64/chrome",
    ):
        g = sorted(glob.glob(pat))
        if g:
            return g[-1]
    system = ["/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"]
    if sys.platform == "darwin":
        system = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    for cand in system:
        if Path(cand).is_file():
            return str(cand)
    return None


def npm_global_root() -> str | None:
    try:
        out = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, timeout=20)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return None


def node_path_dirs() -> list[str]:
    """Directories to expose on NODE_PATH so `require('puppeteer-core')` resolves.
    puppeteer-core ships nested under the global `hyperframes/node_modules`, not the global root."""
    dirs: list[str] = []
    cands: list[str] = []
    groot = npm_global_root()
    if groot:
        cands += [groot, str(Path(groot) / "hyperframes" / "node_modules")]
    # fallback: derive from the hyperframes binary location
    try:
        hf = subprocess.run(["which", "hyperframes"], capture_output=True, text=True, timeout=10).stdout.strip()
        if hf:
            for parent in Path(hf).resolve().parents:
                if parent.name == "hyperframes":
                    cands.append(str(parent / "node_modules"))
                    break
    except Exception:
        pass
    for c in cands:
        if c and Path(c).is_dir() and c not in dirs:
            dirs.append(c)
    return dirs


def build_node_env() -> dict[str, str]:
    """Parent env for the node driver, with puppeteer-core dirs prepended onto NODE_PATH."""
    env = dict(os.environ)
    parts = node_path_dirs()
    existing = get_env("NODE_PATH")
    if existing:
        parts.append(existing)
    if parts:
        env["NODE_PATH"] = os.pathsep.join(parts)
    return env
