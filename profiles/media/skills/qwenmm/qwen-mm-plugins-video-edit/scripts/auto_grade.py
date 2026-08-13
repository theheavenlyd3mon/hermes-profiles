#!/usr/bin/env python3
"""auto_grade.py — analyze a clip and emit a BOUNDED corrective grade.

Mental model: correction, not creative grading. Samples frames via ffmpeg
signalstats, measures luma mean / luma range / saturation, then emits an eq
filter that only fixes under-exposure, flatness and mild desaturation.
Every axis is clamped to roughly +-8%. It never applies creative LUTs,
teal/orange splits or film curves — those are opt-in art direction decisions.

Usage:
    python3 auto_grade.py analyze INPUT [--start S --duration D]
    python3 auto_grade.py apply   INPUT -o OUTPUT [--filter 'eq=...']  # apply
        (without --filter, applies the auto-derived correction)

Requires: ffmpeg/ffprobe on PATH. No third-party python deps.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def probe_duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path)]).decode().strip()
    try:
        return float(out)
    except ValueError:
        return 10.0


def sample_stats(video: Path, start: float, duration: float, n: int = 12) -> dict:
    """Sample n frames via signalstats; return normalized y_mean/y_range/sat_mean."""
    fps = max(0.5, min(n / max(duration, 0.1), 10.0))
    meta = Path(tempfile.mkstemp(suffix=".txt")[1])
    try:
        subprocess.run([
            "ffmpeg", "-y", "-hide_banner", "-nostats",
            "-ss", f"{start:.3f}", "-i", str(video), "-t", f"{duration:.3f}",
            "-vf", f"fps={fps:.2f},signalstats,metadata=print:file={meta}",
            "-f", "null", "-",
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        vals: dict[str, list[float]] = {"YAVG": [], "YMIN": [], "YMAX": [], "SATAVG": []}
        depth = 8
        for line in meta.read_text().splitlines():
            line = line.strip()
            for key in ("YBITDEPTH", *vals.keys()):
                tag = f"lavfi.signalstats.{key}="
                if tag in line:
                    try:
                        v = float(line.rsplit("=", 1)[1])
                    except ValueError:
                        continue
                    if key == "YBITDEPTH":
                        depth = int(v)
                    else:
                        vals[key].append(v)
        if not vals["YAVG"]:
            sys.exit("ERROR: signalstats produced no samples (decode failed?)")
        mx = (2 ** depth) - 1
        y_mean = sum(vals["YAVG"]) / len(vals["YAVG"]) / mx
        y_range = ((sum(vals["YMAX"]) / len(vals["YMAX"])) -
                   (sum(vals["YMIN"]) / len(vals["YMIN"]))) / mx if vals["YMAX"] else 0.7
        sat = (sum(vals["SATAVG"]) / len(vals["SATAVG"]) / mx) if vals["SATAVG"] else 0.25
        return {"y_mean": y_mean, "y_range": y_range, "sat_mean": sat}
    finally:
        meta.unlink(missing_ok=True)


def derive_filter(s: dict) -> str:
    """Bounded corrective decisions. All axes clamped to ~±8%."""
    y_mean, y_range, sat = s["y_mean"], s["y_range"], s["sat_mean"]

    contrast = 1.03  # subtle baseline
    if y_range < 0.65:  # flat → gentle boost, mapped [0.50,0.65] → [1.08,1.03]
        t = max(0.0, min(1.0, (y_range - 0.50) / 0.15))
        contrast = 1.08 - 0.05 * t

    gamma = 1.0
    if y_mean < 0.42:   # dark → lift, mapped [0.30,0.42] → [1.10,1.02]
        t = max(0.0, min(1.0, (y_mean - 0.30) / 0.12))
        gamma = 1.10 - 0.08 * t
    elif y_mean > 0.60:  # hot → tiny pullback
        gamma = 0.97

    saturation = 0.98  # most consumer video is slightly over-saturated
    if sat < 0.18:
        saturation = 1.04
    elif sat > 0.38:
        saturation = 0.96

    contrast = max(0.94, min(1.08, contrast))
    gamma = max(0.94, min(1.10, gamma))
    saturation = max(0.94, min(1.06, saturation))

    parts = []
    if abs(contrast - 1.0) > 0.005:
        parts.append(f"contrast={contrast:.3f}")
    if abs(gamma - 1.0) > 0.005:
        parts.append(f"gamma={gamma:.3f}")
    if abs(saturation - 1.0) > 0.005:
        parts.append(f"saturation={saturation:.3f}")
    return ("eq=" + ":".join(parts)) if parts else ""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["analyze", "apply"])
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--duration", type=float, default=None)
    ap.add_argument("--filter", dest="filter_str", default=None,
                    help="override: apply this raw ffmpeg -vf chain instead of auto")
    args = ap.parse_args()

    if not args.input.exists():
        sys.exit(f"ERROR: {args.input} not found")
    dur = args.duration or probe_duration(args.input)

    stats = sample_stats(args.input, args.start, dur)
    auto = derive_filter(stats)
    print(f"file     : {args.input}")
    print(f"stats    : y_mean={stats['y_mean']:.3f}  y_range={stats['y_range']:.3f}  sat={stats['sat_mean']:.3f}")
    print(f"judgment : "
          f"{'dark' if stats['y_mean'] < 0.42 else 'hot' if stats['y_mean'] > 0.60 else 'exposure ok'}, "
          f"{'flat' if stats['y_range'] < 0.65 else 'contrast ok'}, "
          f"{'desaturated' if stats['sat_mean'] < 0.18 else 'punchy' if stats['sat_mean'] > 0.38 else 'saturation ok'}")
    print(f"filter   : {auto or '(no correction needed)'}")

    if args.mode == "apply":
        if not args.output:
            sys.exit("ERROR: apply mode needs -o OUTPUT")
        chain = args.filter_str or auto
        if not chain:
            cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(args.input),
                   "-c", "copy", str(args.output)]
        else:
            cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(args.input),
                   "-vf", chain, "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                   "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart",
                   str(args.output)]
        subprocess.run(cmd, check=True)
        print(f"applied  : {chain or 'stream copy'} -> {args.output}")


if __name__ == "__main__":
    main()
