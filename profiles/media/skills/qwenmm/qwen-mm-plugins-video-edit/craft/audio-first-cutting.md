# Audio-First Cutting — Cut Points Live in the Sound

> **Bridge notice.** This document owns *where cut candidates come from* in
> speech-led footage. Subtitle styling and narration writing live in the
> `hyperframes` skill family; transcription tooling is `transcribe_audio`
> (see `mcps/core-perception.md`).

## Principle

Audio is primary; visuals follow. For talking heads, interviews, vlogs and
any speech-led footage, cut candidates come from **word boundaries and
silence gaps** — drill into frames only at decision points. Never reason
about audio and video independently: every cut must work on both tracks.

## The numbers (video-use, shipped-video values)

| Rule | Value |
|---|---|
| Cleanest cut targets | silence gaps ≥400ms |
| Usable with a visual check | 150–400ms phrase boundaries |
| Unsafe (mid-phrase) | <150ms gaps |
| Cut-edge padding window | 30–200ms (tight = montage energy, loose = documentary) |
| Speaker handoff air | 400–600ms between utterances |
| Never | cut inside a word |

## Peaks are sacred

Laughs, punchlines, emphasis beats and audible reactions are the energy
anchors of the piece. Preserve them, and **extend past a punchline to include
the reaction** — the laugh IS the beat. Transcript events like `(laughs)`,
`(applause)` mark these moments; treat them as narrative signals, not noise.

## Workflow

1. **Transcribe first** (`transcribe_audio`) — word-level timestamps become
   both the cut map and future subtitle material. Cache per source; never
   re-transcribe unchanged files.
2. **Pre-scan for problems:** verbal slips, false starts, mis-speaks — list
   them so the selection step avoids them.
3. **Pick takes by beat, not by source order:** for multi-take material,
   select the best take of each narrative beat and assemble chronologically
   by beat.
4. **Drill down visually only where it's ambiguous:**
   `scripts/timeline_view.py VIDEO START END` renders filmstrip + waveform +
   shaded silence gaps for exactly this decision. Do not scan every second.
5. **J-cut / L-cut at seams:** offset the audio and video trim points
   independently — speech starts before the picture cuts to the speaker
   (J), or trails after the picture has moved on (L).
6. **30ms audio fades at every cut boundary** — otherwise pops. This is
   correctness, not taste.

## Multi-take 口播 recut — the take map is the edit

Raw 口播 recordings (one camera, speaker re-delivering each beat 2-4× with
flubs, false starts and off-camera note-checking) are cut on paper before
any video work. Field-proven sequence (879s raw → 287s ship):

1. **Take map first**: silencedetect over the full source — ≥400ms gaps
   delineate takes. Cross the gap map with the ASR transcript into a table:
   beat · source region · clean/flubbed · note. Log the AVOID list
   explicitly (stutters, meta comments “可以吗？再来一下”, note-reading
   audio) so selection can't drift back into them.
2. **Radio edit before picture**: pick the best take per beat, read the
   assembled transcript end-to-end for meaning — no dangling clauses, no
   two takes spliced into a claim the speaker never made
   (不拼接误导性结论 is reviewable, not aspirational).
3. **Prep bakes the audio baseline — and PROVES each clip**: each selected
   segment is cut seek-safe AND `loudnorm` to the delivery target (e.g.
   -14 LUFS) at prep — per-segment normalization up front is what makes
   hard-cut seams inaudible later; 30ms fades at every cut stay mandatory.
   Then **ASR every prep clip and diff it against its intended clean text
   BEFORE the scene renders** — approximate segment bounds (`~`, "verify")
   are PLANNING artifacts, never render inputs; an unverified in/out point
   is how a flubbed take ships.
4. **Scene files carry the verbatim text**: each `edit/scenes/S<N>.md` gets
   an `**Audio:**` field with that scene's exact clean-take transcript —
   it is the subtitle source of truth AND the fidelity check target
   (subtitles must match speech; final review spot-checks lines against
   this field).
5. **Disguise the jump cuts on the picture side**: alternate framings via
   crop-reframe (wide/mid/close cycle, never >2 consecutive cuts in the
   same framing), slow keyframed punch-ins across long single takes, and
   B-roll covers over seams — B-roll explains, never buries a punchline,
   and stays ≤6s continuous ([no-occlusion] still applies to the face).
6. **Post-assembly audio verification is part of the cut**: after the
   master exists, verify each scene's audio lands EXACTLY ONCE at its
   ledger offset (per-scene RMS windows + envelope cross-correlation —
   see `engines/hyperframes.md` § Render troubleshooting for the failure
   mode and the video-untouched repair).
7. **Transcript-equality check before the verdict**: ASR the assembled
   deliverable and diff it against the concatenated scene `**Audio:**`
   fields. Any stutter ("AI再聪，AI再聪明"), doubled phrase, orphan clause,
   filler (嗯/呃), meta comment, or missing sentence = FAIL — a flub leaked
   through an unverified in/out point (step 3 was skipped for that clip).
   Field case: ≈20 leaked flubs shipped in a 口播 recut — every
   gate passed (loudness/black/ledger) because none of them read the words;
   subtitles burnt from clean text then mismatched the flubbed audio.

## Self-check

- Any cut landing inside a word or <150ms from one?
- Any punchline cut off before its reaction?
- Did you visually verify the ambiguous seams (not every seam)?
- Do the seams pop when you listen with eyes closed?
- Multi-take recut: was every prep clip ASR-diffed against its clean text
  before its scene rendered — and does ASR of the FINAL match the scene
  `**Audio:**` fields with zero stutters/doubles/fillers/missing lines?
- Multi-source master: does each scene's audio land exactly once, at its
  ledger offset?
