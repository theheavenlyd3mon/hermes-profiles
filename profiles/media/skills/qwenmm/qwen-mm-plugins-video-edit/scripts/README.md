# Scripts — Verified Measurement & Processing Tools

Deterministic tools that back the craft/review documents. Docs teach *why and
when*; these scripts execute the *how* reproducibly. The tools are validated
against representative fixtures covering clean renders, silent audio,
black-gap failures, incomplete project logs, and FFmpeg-only handoff mistakes.

Regression coverage includes:

- `loudness_check.sh`: fails missing audio streams, digital silence, malformed
  loudness output, and defensive parse edge cases such as `-inf`.
- `black_check.sh`: fails interior black gaps while allowing clean clips and
  reporting head/tail fades as advisories.
- `plan_gate.sh`: fails incomplete taste contracts, missing named motion
  recipes, missing design-floor slots, missing Direction/Engine decisions, and
  FFmpeg-only designed deliverables without a user-granted mechanical
  exemption.
- `scene_gate.sh`: fails unlocked ledger rows and scene logs without concrete
  render/check iteration entries.
- `review_gate.sh`: re-runs the technical gates plus plan/scene gates so a
  deliverable cannot pass review by skipping an earlier gate.

## Index

| Script | Purpose | Owning doc | Mutates media? | Deps |
|--------|---------|-----------|----------------|------|
| `check_env.sh` | Environment self-check: OK/MISSING/WARN per dependency with install hints (exit = #missing) | `SKILL.md` § Environment | no | bash |
| `plan_gate.sh` | Pre-assembly gate: taste-contract fields + Motion plan cites approved palette + the three `[design-floor]` slots (Opening/Transitions/Ending) + Direction & Engine Decision logged (exit 2 = plan incomplete, no assembly) | `craft/art-direction.md` §2, `SKILL.md` flow step 5 | no | bash |
| `scene_gate.sh` | Pre-master gate: every Scene Ledger row LOCKED + every `edit/scenes/*.md` carries a real `## iter N` entry — an empty `## Iteration log` placeholder does not count (exit 2 = scene loop incomplete, no master render) | `engines/hyperframes.md` § Scene-loop assembly, `SKILL.md` flow step 7 | no | bash |
| `timeline_view.py` | Filmstrip + RMS waveform + shaded silence gaps for a time window — cut-point decisions, seam checks | `craft/audio-first-cutting.md` | no | python3, PIL, numpy, ffmpeg |
| `beat_grid.py` | BGM beat-grid fit (true BPM + phase), kick locating, cut-point error report (pass ≤3f) | `craft/music-beat-sync.md` | no | python3, librosa, scipy, ffmpeg |
| `auto_grade.py` | Bounded (±8%) corrective grade: analyze → judge → optional apply | `craft/footage-grading.md` | `apply` writes a new file | python3, ffmpeg |
| `loudness_check.sh` | Audio stream presence + LUFS / true peak / LRA + silence heuristic (exit 2 = fail) | `review/final-review.md` | no | bash, ffmpeg |
| `black_check.sh` | Black-gap scan: interior black = broken transition / timeline gap (exit 2 = fail); head/tail black = fade advisory | `review/final-review.md` | no | bash, ffmpeg, python3 |
| `review_gate.sh` | Single mandatory review entry: ffprobe + loudness + black + **plan-gate re-run** + **scene-gate re-run** in one command, byte-identity hash, paste-into-verdict block (exit 2 = any hard fail) | `review/final-review.md` | no | bash, ffmpeg, python3 |
| `contact_sheet.sh` | Per-second frame tiles in one JPG — full-duration visual evidence | `review/final-review.md` | no | bash, ffmpeg |

## Conventions

- Prefer a local python that already has the deps (check first: `python3 -c
  "import librosa"`); fall back to `uv run --with librosa --with scipy
  --python 3.11 beat_grid.py ...` — note the uv path re-downloads deps per
  ephemeral env and can be slow on throttled networks.
- Scripts only measure and report; the single exception is `auto_grade.py
  apply`, which writes a NEW file (never overwrites its input).
- All outputs go under `<videos_dir>/edit/` per the working-directory
  convention — never inside this skill directory.
- Adding a script here requires: single purpose, no creative decisions,
  validation evidence on real media recorded in this README.
