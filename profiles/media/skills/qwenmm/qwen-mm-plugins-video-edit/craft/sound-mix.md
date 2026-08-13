# Sound Mix — Two-Track Doctrine, Frequency Separation, SFX Pinning

> **Bridge notice.** This document owns *mixing discipline* for delivered
> edits. BGM/SFX/TTS asset sourcing lives in `hyperframes-media` /
> `media-use`; whether audio may be dropped at all is governed by the
> `[audio-preserved]` hard rule in `SKILL.md`.

## Two-track doctrine (the anti-cheapness core)

A piece with only BGM feels cheap — the viewer subconsciously registers
"things move but nothing responds". Design two independent layers:

| Layer | Role | Sync | Frequency home |
|---|---|---|---|
| SFX (beat layer) | marks visual beats, 0.2–2s hits | frame-accurate | high, 800Hz+ |
| BGM (mood bed) | continuous emotion floor | section-level | low/mid, <4kHz |

## Golden numbers (tested, use as-is)

- BGM volume 0.40–0.50 of full scale; SFX 1.0; BGM peak sits **-6 to -8dB
  under SFX peak** — separation comes from the delta, not absolute loudness.
- **Frequency isolation** (the single biggest clarity win):
  `BGM → lowpass=f=4000`, `SFX → highpass=f=800`.
- Mix with `amix=...:normalize=0` — normalize=1 flattens dynamics.
- BGM fade-in 0.3s at start, fade-out 1.5s tail. SFX carry their own
  envelopes, no extra fades.
- Speech-led mixes: music ducks 18–20dB under narration while speech is
  active; cut 2–4kHz on the music bed to clear the intelligibility band.
- Delivery targets: **-14 LUFS integrated, true peak ≤ -1.5dBTP**
  (`scripts/loudness_check.sh` measures both).

## SFX discipline

- **Bundled first:** reusable cues live in `<skill-root>/assets/sfx/`
  (browse `assets/local-media.html`) — check there before generating or
  downloading. New keepers go back into that folder.
- **The design-floor pair:** even a no-BGM piece gets 1-2 accent cues — one
  on the opening title landing, one on the ending stop (`[design-floor]`).
- **Density follows the piece's personality:** calm/focused 0–3 cues per
  10s; lively/info-dense 6–9 per 10s. When unsure, delete 30–50% of planned
  cues — the survivors gain drama.
- **Priority:** P0 (skip = jarring): user-decision clicks, focus shifts,
  title/logo reveal. P1: entrances/exits, completion moments, big scene
  changes. P2 (rarely): hover ticks, ambient decoration.
- **Foley over decoration:** an identifiable on-screen action gets its real
  sound (typing → keys, item lands → thud), trimmed to the action's exact
  length. Generic whooshes can't cover recognizable actions.
- **Pin by frame in a declarative table** (`project.md` or a cue file):
  `frame | file | volume | on-screen action`. Same-frame alignment for
  clicks/reveals; whooshes lead the visual by 1–2 frames; impacts land 1–2
  frames after. Repeated cues: alternate two samples, step volume down a
  ladder (e.g. 0.40→0.25), accelerate intervals with the animation curve.
- **The re-pin rule:** any change to shot order/length invalidates the whole
  SFX table — re-pin every row before delivery. Mix AFTER the picture locks.
- SFX character matches the visual world: warm/paper look → soft
  taps/paper snaps; tech/dark → clean digital pulses; playful → pops.
  No game-UI sound packs on product/narrative pieces.

## FFmpeg mix template

```bash
ffmpeg -y -i video.mp4 -i sfx-track.mp3 -i bgm.mp3 -filter_complex "\
[2:a]afade=in:st=0:d=0.3,afade=out:st=DUR-1.5:d=1.5,lowpass=f=4000,volume=0.45[bgm];\
[1:a]highpass=f=800,volume=1.0[sfx];\
[bgm][sfx]amix=inputs=2:duration=first:normalize=0[a]" \
-map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k out.mp4
```

(If the video has live audio to keep, add it as a third amix input at
volume 1.0 and duck the BGM under it.)

## Self-check

- Close your eyes and listen: does anything respond when things move?
- Mute the BGM: do the SFX alone carry a countable rhythm?
- Mute the SFX: does the BGM alone have an emotional arc with a clean tail?
- `loudness_check.sh` on the deliverable: PASS, reasonable levels?
- Did the picture change after the SFX table was pinned? Re-pinned?
