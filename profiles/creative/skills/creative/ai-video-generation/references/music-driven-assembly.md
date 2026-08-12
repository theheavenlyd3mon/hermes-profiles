# Music-Driven Assembly — cutting a multi-clip sequence to a generated track

The principle: once music is added, the relationship flips. The music becomes the
timeline and the picture bends to it. Cuts land on beats, the slow-mo hero sits in
a musical breakdown, the biggest action hits on the drop. "Video with a song under
it" vs "a cut that feels choreographed" is decided here.

## Step 1 — Map the track's structure before touching a cut

Run `scripts/audio_energy_map.py <audio.mp3>`. It:
- decodes to mono 22050 Hz s16le PCM via ffmpeg
- computes an RMS energy envelope over ~0.5s windows (pure stdlib; `audioop` was
  removed in Python 3.13, so RMS is computed with `struct.iter_unpack("<h", ...)`)
- prints a per-second ASCII bar graph
- reports the quietest 2s windows (intros/breakdowns), loudest 2s windows
  (drops/peaks), and sharp onsets (energy rise > 0.22 within ~1.5s after a low —
  candidate drop hits)

Read the graph for the song's spine. A typical Suno action-sports track (145 BPM,
build-and-drop) yields: quiet intro → drop #1 → sustained energy → a clean
breakdown (energy collapses to ~0.2, drums vanish) → drop #2 (hardest slam) →
outro tail. Suno often returns a FULL song (~90-100s), not a 30s clip — a gift:
multiple builds/drops to choose from. Pick the section whose breakdown→drop is
cleanest and cut to it.

## Step 2 — Build the picture on the song's spine

Map video sections to music sections, e.g. for ~45s:
| Video time | Music | On screen |
|---|---|---|
| 0–6s | Quiet intro | Cold open / establishing |
| 6–12s | Tension rising | B-roll + first action |
| ~13s | DROP #1 | First hard action lands on the hit |
| 13–39s | Full energy | Fast cuts on beats (POV, tricks, powder) |
| 40–42s | BREAKDOWN | Slow-mo apex, drums gone, suspended |
| ~43s | DROP #2 | Hardest trick + hero stop on the slam |
| ~48s | Sustained/tail | Ride-away, fade |

The aerial/slow-mo lives in the breakdown; the biggest tricks land on the drop.
That's choreography, not luck. A clean breakdown→drop already in the track is worth
more than fighting the edit to fit a chosen section.

## Step 3 — Assemble with FFmpeg

- Trim each clip so its CUT POINT lands on a downbeat (`trim=0:N,setpts=PTS-STARTPTS`).
- Apply ONE unified grade to every clip so the world never resets:
  `eq=contrast=1.08:saturation=1.12:brightness=0.01,colorbalance=bs=0.05:rm=0.06,unsharp=3:3:0.4`
  (cool shadows + warm mids + light sharpen; tune to taste).
- Fade in on the first clip, fade out on the last (`fade=t=in/out`).
- Duck the wind/SFX under the music; sidechain-style dip on hits if you want punch.
- Join with the `concat` filter (interleave v/a per clip), encode
  `libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart`.

## Honest caveats
- Beat-perfect sync to GENERATED audio is never sample-accurate — a few ms of feel
  remains. Get it tight by eye on the waveform; don't promise sample accuracy.
- If the track's drop isn't clean where you need it, iterate the TRACK (regenerate),
  not the cut.
- FLUX 3 clips top out at 720p — fine for social, not 4K. Fast cuts + mood over
  continuity is the sweet spot; a recurring face across 20 shots is the hard case
  (lean on the character-sheet anchor + B-roll ratio).
