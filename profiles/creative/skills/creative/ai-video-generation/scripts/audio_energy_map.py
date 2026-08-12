#!/usr/bin/env python3
"""Map an audio track's structure: RMS energy envelope + drop/breakdown detection.

Pure stdlib (no numpy/aubio). Decodes any ffmpeg-readable audio to mono 22050 Hz
s16le PCM, computes an RMS energy envelope, and prints:
  - a per-second ASCII energy bar graph
  - the quietest 2s windows (intros / breakdowns)
  - the loudest 2s windows (drops / peaks)
  - sharp energy onsets (candidate drop hits)

Usage:
    python3 audio_energy_map.py <audio_file> [window_secs]
    (default window_secs = 0.5)

Read the graph for the song's spine: quiet intro -> drop -> sustained ->
breakdown (energy collapse) -> drop #2 (hardest slam) -> outro tail. Cut the
picture to that spine. See references/music-driven-assembly.md.
"""
import struct
import subprocess
import sys
import tempfile
import os

SR = 22050


def rms(chunk: bytes) -> float:
    n = len(chunk) // 2
    if n == 0:
        return 0.0
    total = 0
    for (s,) in struct.iter_unpack("<h", chunk):
        total += s * s
    return (total / n) ** 0.5


def decode_to_pcm(path: str) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".pcm", delete=False) as tmp:
        pcm_path = tmp.name
    subprocess.run(
        ["ffmpeg", "-y", "-i", path, "-ac", "1", "-ar", str(SR),
         "-f", "s16le", "-acodec", "pcm_s16le", pcm_path],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    with open(pcm_path, "rb") as f:
        raw = f.read()
    os.unlink(pcm_path)
    return raw


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    audio = sys.argv[1]
    win = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5

    raw = decode_to_pcm(audio)
    frame_bytes = int(SR * win) * 2  # 16-bit mono

    energies = [rms(raw[s:s + frame_bytes])
                for s in range(0, len(raw) - frame_bytes, frame_bytes)]
    max_e = max(energies) or 1.0
    norm = [e / max_e for e in energies]

    print(f"Track: {audio}  ({len(norm) * win:.1f}s analyzed, {win}s windows)\n")
    print("TIME  ENERGY  BAR")
    print("-" * 60)
    for i in range(0, len(norm) - 1, 2):  # one line per ~1s
        seg = (norm[i] + norm[i + 1]) / 2
        print(f"{i * win:5.1f}s {seg:5.2f}  {'█' * int(seg * 40)}")

    # Smooth over ~1s, then rank 2s windows.
    smooth = []
    for i in range(len(norm)):
        lo, hi = max(0, i - 1), min(len(norm), i + 2)
        smooth.append(sum(norm[lo:hi]) / (hi - lo))
    windowed = [(i * win, sum(smooth[i:i + 4]) / 4)
                for i in range(len(smooth) - 3)]

    print("\n=== Quietest 2s windows (intros / breakdowns) ===")
    for t, e in sorted(windowed, key=lambda x: x[1])[:5]:
        print(f"  {t:5.1f}s  energy={e:.2f}")
    print("=== Loudest 2s windows (drops / peaks) ===")
    for t, e in sorted(windowed, key=lambda x: -x[1])[:5]:
        print(f"  {t:5.1f}s  energy={e:.2f}")

    print("\n=== Sharp energy onsets (candidate drop hits) ===")
    for i in range(4, len(smooth) - 4):
        before = min(smooth[i - 3:i])
        after = max(smooth[i:i + 3])
        if after - before > 0.22 and before < 0.55:
            print(f"  ~{i * win:5.1f}s  rise {before:.2f} -> {after:.2f}")


if __name__ == "__main__":
    main()
