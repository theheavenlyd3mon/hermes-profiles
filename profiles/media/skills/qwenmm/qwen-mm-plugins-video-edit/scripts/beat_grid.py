#!/usr/bin/env python3
"""beat_grid.py — BGM beat-grid fitting, kick locating, and cut-point verification.

Run via uv (no local install needed):
    uv run --with librosa --with scipy --python 3.11 beat_grid.py MEDIA [options]

What it does:
  1. Loads audio (extracts audio via ffmpeg if MEDIA is a video).
  2. librosa beat_track -> least-squares equal-spacing grid fit  t_i = t0 + i*T.
     The fitted BPM is more accurate than beat_track's tempo scalar (which can
     drift 2%+). Residual <= +-15ms means machine-steady drums (grid trustable).
  3. Band-passes the kick range (40-160 Hz) and ranks integer beats by onset
     energy -> the "strongest hit" beats where big slams should be pinned.
  4. Optional --cuts: verifies designed cut points against the grid and reports
     per-cut error in frames (pass <= 3f, ideal <= 1.5f).

Examples:
    uv run --with librosa --with scipy --python 3.11 beat_grid.py bgm.mp3
    uv run --with librosa --with scipy --python 3.11 beat_grid.py final.mp4 \
        --cuts 2.4,5.1,7.8 --fps 30 --json grid.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def extract_audio(media: Path) -> Path:
    """Extract mono 44.1k wav from any media file via ffmpeg."""
    tmp = Path(tempfile.mkstemp(suffix=".wav")[1])
    cmd = [
        "ffmpeg", "-y", "-v", "error", "-i", str(media),
        "-vn", "-ac", "1", "-ar", "44100", "-c:a", "pcm_s16le", str(tmp),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not tmp.exists() or tmp.stat().st_size == 0:
        sys.exit(f"ERROR: cannot extract audio from {media}: {r.stderr.strip()}")
    return tmp


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("media", type=Path)
    ap.add_argument("--top", type=int, default=8, help="top-N strongest kick beats to report")
    ap.add_argument("--cuts", type=str, default="", help="comma-separated designed cut times (s) to verify")
    ap.add_argument("--fps", type=float, default=30.0, help="frame rate for error-in-frames")
    ap.add_argument("--json", type=Path, default=None, help="write machine-readable result JSON")
    args = ap.parse_args()

    try:
        import numpy as np
        import librosa
        from scipy.signal import butter, sosfilt
    except ImportError as e:
        sys.exit(
            f"ERROR: missing dependency ({e.name}). Use a python that has "
            "librosa+scipy (check: python3 -c 'import librosa'), or run via:\n"
            "  uv run --with librosa --with scipy --python 3.11 beat_grid.py ..."
        )

    media = args.media
    if not media.exists():
        sys.exit(f"ERROR: {media} not found")

    wav = media
    cleanup = None
    if media.suffix.lower() not in {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}:
        wav = extract_audio(media)
        cleanup = wav

    y, sr = librosa.load(str(wav), sr=None, mono=True)
    dur = len(y) / sr
    tempo_raw, beats = librosa.beat.beat_track(y=y, sr=sr, tightness=400, units="time")
    if len(beats) < 8:
        sys.exit(f"ERROR: only {len(beats)} beats detected — track too short or beatless")

    # Least-squares equal-spacing grid fit: t_i = t0 + i*T
    i = np.arange(len(beats))
    A = np.vstack([i, np.ones_like(i)]).T
    (T, t0), *_ = np.linalg.lstsq(A, beats, rcond=None)
    bpm = 60.0 / T
    residual = beats - (t0 + i * T)
    res_ms = float(np.abs(residual).max() * 1000)
    grid_ok = res_ms <= 15.0

    # Kick-band onset energy at each integer beat
    sos = butter(4, [40, 160], btype="band", fs=sr, output="sos")
    kick = sosfilt(sos, y)
    env = librosa.onset.onset_strength(y=kick.astype(np.float32), sr=sr)
    times = librosa.times_like(env, sr=sr)
    n_beats = int((dur - t0) / T)
    beat_energy = []
    for n in range(max(n_beats, 0)):
        t = t0 + n * T
        if t < 0 or t > times[-1]:
            continue
        e = float(env[int(np.argmin(np.abs(times - t)))])
        beat_energy.append((n, t, e))
    top = sorted(beat_energy, key=lambda x: -x[2])[: args.top]

    print(f"file      : {media}")
    print(f"duration  : {dur:.2f}s   beats detected: {len(beats)}")
    print(f"raw tempo : {float(np.atleast_1d(tempo_raw)[0]):.2f} BPM (beat_track scalar — do not trust)")
    print(f"fitted    : BPM={bpm:.2f}  t0={t0:.4f}s  T={T:.5f}s")
    print(f"residual  : ±{res_ms:.0f}ms  -> grid {'TRUSTABLE' if grid_ok else 'NOT steady (segment-fit needed)'}")
    print(f"\nstrongest kick beats (pin big slams here):")
    print(f"  {'beat#':>6} {'time(s)':>9} {'frame@'+str(int(args.fps)):>9} {'energy':>8}")
    for n, t, e in top:
        print(f"  {n:>6} {t:>9.3f} {round(t*args.fps):>9} {e:>8.2f}")

    cut_report = []
    if args.cuts:
        print(f"\ncut-point verification (pass ≤3f, ideal ≤1.5f @ {args.fps}fps):")
        for c in [float(x) for x in args.cuts.split(",") if x.strip()]:
            n_near = round((c - t0) / T)
            t_beat = t0 + n_near * T
            err_f = (c - t_beat) * args.fps
            verdict = "PASS" if abs(err_f) <= 3 else "FAIL"
            if abs(err_f) <= 1.5:
                verdict = "IDEAL"
            print(f"  cut {c:>8.3f}s -> beat {n_near} @ {t_beat:.3f}s  err {err_f:+.2f}f  {verdict}")
            cut_report.append({"cut": c, "beat": int(n_near), "beat_time": round(t_beat, 4),
                               "err_frames": round(err_f, 2), "verdict": verdict})

    if args.json:
        args.json.write_text(json.dumps({
            "file": str(media), "duration": round(dur, 3), "bpm": round(bpm, 3),
            "t0": round(float(t0), 5), "T": round(float(T), 6),
            "residual_ms": round(res_ms, 1), "grid_trustable": grid_ok,
            "strongest_beats": [{"n": n, "t": round(t, 4), "energy": round(e, 3)} for n, t, e in top],
            "cuts": cut_report,
        }, indent=2))
        print(f"\njson -> {args.json}")

    if cleanup:
        cleanup.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
