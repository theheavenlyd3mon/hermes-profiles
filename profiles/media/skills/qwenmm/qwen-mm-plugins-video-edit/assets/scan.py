#!/usr/bin/env python3
"""Scan the assets tree and write manifest.json for index.html to render.

Human-facing asset browser support (not part of the agent execution path).
Run after adding or removing any asset file:

    python3 assets/scan.py

Creates the standard subdirectories on first run so the layout is obvious.
"""

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Standard buckets. Keys are directory names; each carries the extensions that
# belong in it and the renderer index.html should use.
BUCKETS = {
    "fonts": {"ext": {".ttf", ".otf", ".woff2", ".woff"}, "kind": "font"},
    "sfx": {"ext": {".mp3", ".wav", ".m4a", ".ogg"}, "kind": "audio"},
    "bgm": {"ext": {".mp3", ".wav", ".m4a", ".ogg"}, "kind": "audio"},
    "images": {"ext": {".png", ".jpg", ".jpeg", ".webp", ".svg"}, "kind": "image"},
    "clips": {"ext": {".mp4", ".mov", ".webm"}, "kind": "video"},
}


# ffprobe covers audio and video; a missing binary must not break the scan.
def probe_duration(path: Path) -> float | None:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
            capture_output=True,
            text=True,
            timeout=20,
        )
        return round(float(out.stdout.strip()), 2) if out.returncode == 0 else None
    except (FileNotFoundError, ValueError, subprocess.TimeoutExpired):
        return None


def sidecar_note(path: Path) -> str:
    """A <name>.txt next to an asset carries its license / provenance note."""
    note = path.with_suffix(".txt")
    if note.exists():
        return note.read_text(encoding="utf-8", errors="replace").strip()[:400]
    return ""


def _existing_entries() -> dict:
    """Map file-path → prior manifest entry, so hand-authored fields (register / personality /
    mood / … that craft/fonts.md and index.html rely on) survive a re-scan instead of being
    overwritten with only the auto-scanned columns."""
    path = ROOT / "manifest.json"
    if not path.exists():
        return {}
    try:
        old = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {it["file"]: it for b in old.values() for it in b.get("items", []) if "file" in it}


def main() -> None:
    prior = _existing_entries()
    manifest = {}
    for bucket, spec in BUCKETS.items():
        bucket_dir = ROOT / bucket
        bucket_dir.mkdir(exist_ok=True)  # make the layout self-evident
        items = []
        for path in sorted(bucket_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in spec["ext"]:
                continue
            entry = {
                "name": path.stem,
                "file": path.relative_to(ROOT).as_posix(),
                "ext": path.suffix.lower().lstrip("."),
                "size_kb": round(path.stat().st_size / 1024, 1),
                "note": sidecar_note(path),
            }
            if spec["kind"] in ("audio", "video"):
                entry["duration"] = probe_duration(path)
            # Preserve any hand-authored fields from the prior manifest (setdefault → auto-scanned
            # columns still refresh; curated ones like register/personality/mood are kept).
            for k, v in prior.get(entry["file"], {}).items():
                entry.setdefault(k, v)
            items.append(entry)
        manifest[bucket] = {"kind": spec["kind"], "items": items}

    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    total = sum(len(b["items"]) for b in manifest.values())
    for bucket, data in manifest.items():
        print(f"{bucket:8s} {len(data['items']):3d} items")
    print(f"\n{total} assets → manifest.json")
    if total == 0:
        print("Drop files into the subdirectories above, then re-run this script.")


if __name__ == "__main__":
    main()
