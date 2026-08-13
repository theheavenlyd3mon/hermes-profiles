#!/usr/bin/env python3
"""timeline_view.py — filmstrip + audio waveform composite for a time range.

The cut-decision drill-down tool: extracts N evenly spaced frames across
[start, end], renders them as a filmstrip, and draws an RMS waveform ribbon
underneath with silence gaps (>= threshold) shaded. Use it at decision points
(ambiguous cuts, seam checks, silence hunting) — not as a scan-everything tool.

Usage:
    python3 timeline_view.py VIDEO START END [-o OUT.png] [--frames N]
                             [--silence-th 0.02] [--silence-min 0.4]

Requires: ffmpeg/ffprobe on PATH; python PIL + numpy.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

BG = (18, 18, 22)
FG = (235, 235, 235)
DIM = (110, 110, 120)
WAVE = (140, 180, 255)
SILENCE = (60, 90, 140, 110)


def extract_frames(video: Path, start: float, end: float, n: int, dest: Path) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    times = [start + i * (end - start) / max(n - 1, 1) for i in range(n)]
    paths = []
    for i, t in enumerate(times):
        out = dest / f"f_{i:03d}.jpg"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video),
            "-frames:v", "1", "-q:v", "4", "-vf", "scale=320:-2", str(out),
        ], check=True)
        paths.append(out)
    return paths


def rms_envelope(video: Path, start: float, end: float, samples: int) -> np.ndarray:
    wav = Path(tempfile.mkstemp(suffix=".wav")[1])
    try:
        r = subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-i", str(video),
            "-t", f"{end - start:.3f}", "-vn", "-ac", "1", "-ar", "16000",
            "-c:a", "pcm_s16le", str(wav)], capture_output=True)
        if r.returncode != 0 or not wav.exists() or wav.stat().st_size < 128:
            return np.zeros(samples)
        import wave as wavemod
        with wavemod.open(str(wav), "rb") as w:
            pcm = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        if pcm.size == 0:
            return np.zeros(samples)
        win = max(1, pcm.size // samples)
        usable = (pcm.size // win) * win
        env = np.sqrt(np.mean(pcm[:usable].reshape(-1, win) ** 2, axis=1))
        env = np.pad(env, (0, max(0, samples - env.size)))[:samples]
        return env / env.max() if env.max() > 0 else env
    finally:
        wav.unlink(missing_ok=True)


def find_silences(env: np.ndarray, start: float, end: float,
                  th: float, min_len: float) -> list[tuple[float, float]]:
    dur = end - start
    dt = dur / len(env)
    gaps, gap_start = [], None
    for i, v in enumerate(env):
        t = start + i * dt
        if v < th:
            gap_start = t if gap_start is None else gap_start
        else:
            if gap_start is not None and t - gap_start >= min_len:
                gaps.append((gap_start, t))
            gap_start = None
    if gap_start is not None and end - gap_start >= min_len:
        gaps.append((gap_start, end))
    return gaps


def load_font(size: int):
    for p in ("/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Helvetica.ttc"):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("video", type=Path)
    ap.add_argument("start", type=float)
    ap.add_argument("end", type=float)
    ap.add_argument("-o", "--out", type=Path, default=None)
    ap.add_argument("--frames", type=int, default=10)
    ap.add_argument("--silence-th", type=float, default=0.02)
    ap.add_argument("--silence-min", type=float, default=0.4)
    args = ap.parse_args()

    if not args.video.exists():
        sys.exit(f"ERROR: {args.video} not found")
    if args.end <= args.start:
        sys.exit("ERROR: end must be > start")
    out_path = args.out or Path(f"timeline_{args.start:.1f}_{args.end:.1f}.png")

    with tempfile.TemporaryDirectory() as tmp:
        frames = extract_frames(args.video, args.start, args.end, args.frames, Path(tmp))
        imgs = []
        frame_h = 180
        for fp in frames:
            im = Image.open(fp).convert("RGB")
            imgs.append(im.resize((int(frame_h * im.width / im.height), frame_h), Image.LANCZOS))

        strip_w = sum(im.width for im in imgs) + 4 * (len(imgs) - 1)
        W = max(1200, strip_w + 100)
        wave_h, strip_y = 160, 46
        wave_y = strip_y + frame_h + 16
        H = wave_y + wave_h + 56

        canvas = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(canvas, "RGBA")
        draw.text((50, 12), f"{args.video.name}   {args.start:.2f}s → {args.end:.2f}s "
                            f"({args.end - args.start:.2f}s, {len(imgs)} frames)",
                  fill=FG, font=load_font(20))

        x = 50
        for im in imgs:
            canvas.paste(im, (x, strip_y))
            x += im.width + 4
        x0, x1 = 50, x - 4

        def t2x(t: float) -> int:
            return int(x0 + (t - args.start) / (args.end - args.start) * (x1 - x0))

        draw.rectangle((x0, wave_y, x1, wave_y + wave_h), fill=(28, 28, 34))
        env = rms_envelope(args.video, args.start, args.end, max(x1 - x0, 200))
        has_audio = bool(env.max() > 0)
        silences = find_silences(env, args.start, args.end,
                                 args.silence_th, args.silence_min) if has_audio else []
        for a, b in silences:
            draw.rectangle((t2x(a), wave_y, t2x(b), wave_y + wave_h), fill=SILENCE)

        mid, amp = wave_y + wave_h // 2, wave_h // 2 - 6
        pts_top, pts_bot = [], []
        for i, v in enumerate(env):
            xi = x0 + int(i * (x1 - x0) / max(len(env) - 1, 1))
            pts_top.append((xi, mid - int(v * amp)))
            pts_bot.append((xi, mid + int(v * amp)))
        if has_audio:
            draw.line(pts_top, fill=WAVE, width=1)
            draw.line(pts_bot, fill=WAVE, width=1)
            draw.polygon(pts_top + pts_bot[::-1], fill=(*WAVE, 60))
        else:
            draw.text((x0 + 10, mid - 10), "NO AUDIO STREAM", fill=DIM, font=load_font(16))

        fnt = load_font(13)
        for i in range(7):
            t = args.start + i * (args.end - args.start) / 6
            xi = t2x(t)
            draw.line((xi, wave_y + wave_h + 2, xi, wave_y + wave_h + 8), fill=DIM)
            draw.text((xi - 18, wave_y + wave_h + 11), f"{t:.2f}s", fill=DIM, font=fnt)
        if silences:
            draw.text((x0, H - 22), f"shaded = silence ≥{args.silence_min}s ({len(silences)} gap(s)): "
                                    + ", ".join(f"{a:.2f}-{b:.2f}" for a, b in silences[:6]),
                      fill=DIM, font=fnt)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out_path, "PNG", optimize=True)
        print(f"saved: {out_path} ({out_path.stat().st_size // 1024} KB)"
              f"  audio={'yes' if has_audio else 'no'}  silences={len(silences)}")


if __name__ == "__main__":
    main()
