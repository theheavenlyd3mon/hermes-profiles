# Vlog Multi-Source Workflow

Use this when the task is: "cut a vlog/edit from a pile of raw, multi-clip footage" — there is no style reference to replicate (for that, use `style-replication.md`). The footage itself, not a reference video, drives every downstream decision: what survives, how fast it cuts, how it connects, and how each clip is trimmed internally.

This workflow builds on `review/source-review.md` (source review, incl. the footage log), `review/project-log.md` (persistence), and `review/final-review.md` (verification). It adds the footage-driven editing steps a professional editor would run before ever opening a timeline. Pacing depth: `craft/pacing-rhythm.md`; speech-led cut points: `craft/audio-first-cutting.md`.

## Phase 1 — Footage Cataloging (Digitize Before You Edit)

Relying on memory fails once footage volume grows — clips get missed or forgotten. Build a footage log before making any selection or ordering decision; the act of logging is also how the narrative thread reveals itself.

For every clip, record:

| Field | Notes |
|---|---|
| Clip ID | Fast lookup key |
| In/Out timecode | Precise to the second |
| Caption | One sentence: what actually happens (e.g. "she picks up a shell on the beach, turns and smiles") |
| Emotion tag | healing / funny / awkward / highlight / flat |
| Quality score | 1-5 (composition, sharpness, light) |
| Intended slot | opening / main narrative / transition / B-roll / ending |
| Duplicate group | Mark clips that are redundant takes of the same moment |

Practical technique:

- **Transcribe first.** If a clip has speech, run it through `transcribe_audio` even roughly — this speeds up writing captions and doubles as future subtitle material.
- **Build a keyword index.** Group clips by recurring keyword (all "laughing" clips, all "scenic B-roll" clips) so later phases can reverse-lookup by keyword instead of re-scanning raw footage.
- **Sampling depth.** Use `read_video` at ~1fps per clip to fill in Caption/Emotion/Quality — this extends `review/source-review.md`'s content-review requirement with a structured log, it does not replace the technical probe.

Checkpoint the log as `<videos_dir>/edit/footage_log.md` (or `.csv`) before moving to Phase 2. Selection and ordering decisions made without a written log are not valid — the agent should not be reasoning from memory of "what footage exists."

## Phase 2 — Selection (Not All Footage Should Survive)

Run this decision tree in order, using the log's quality/emotion scores:

1. **Dedupe** — for clips in the same duplicate group (same content/setup shot repeatedly), keep only the one with the highest combined quality + emotion score.
2. **Cut the ugly** — quality score below a stated threshold (e.g. <3/5) is discarded regardless of sentimental value.
3. **Cut the off-topic** — content unrelated to the confirmed narrative thread is discarded even if technically high quality.
4. **Prioritize** — clips tagged `highlight` move into the main narrative; ordinary clips demote to B-roll candidates.

State the quality threshold used, and record what was cut and why in the checkpoint. A 20-40% footage utilization rate for a multi-minute vlog is normal — do not force usage out of attachment to raw footage.

## Phase 3 — Pacing Design (Cut Speed Is Footage-Driven, Not a Style Preference)

Declare the rhythm pattern before cutting — do not discover it by accident mid-timeline.

| Footage situation | Pacing |
|---|---|
| High volume, many scenes, no single strong clip | **Fast cut** (~0.5-2s/shot). Cut to the BGM's BPM/beat. Density compensates for depth. |
| Low volume, high emotional density (scenery, emotional story) | **Slow cut** (~3-8s/shot). Leave breathing room; only justified if the content itself rewards lingering. |
| Mixed (some highlights, some ordinary narrative) | **Mixed pacing** — slow through narrative passages, fast through climax/recap. This is the most common and best-received vlog structure. |

Common overall shape: **fast-cut teaser open → slow-cut narrative middle → fast-cut montage recap ending.**

For the fast-cut, BPM-synced portions: measure the beat grid and write cut times in beat numbers per `craft/music-beat-sync.md` (grid fit → beat-number timeline → post-render ≤3f verify) — never eyeball the tempo. Rhythm *design* (which beats carry energy) pairs with the `hyperframes` skill's `references/beat-direction.md`.

## Phase 4 — Aesthetic Stitching (Opening / Transition / Ending / Text Cards / PIP / B-roll)

**Opening (hook).** Either (a) a trailer-style montage: pull 0.5-1s snippets from later highlight clips into a ~3s open that promises payoff, or (b) isolate the single strongest emotional/visual clip and open on it alone for contrast and curiosity. Pick one, not neither.

**Transitions.** Prefer content-motivated transitions over decorative ones:

- **Match cut** — action continuity (clip A closes a door → clip B opens a door)
- **Color/composition match** — A's ending dominant color or composition rhymes with B's opening
- **Sound-led transition** — ambient sound or a BGM hit carries the cut so it feels smooth even though the picture is a hard cut

Decorative transitions (spin, wipe) suit a lighthearted/funny tone; avoid them for a serious or premium tone. When an effect-based seam IS warranted, pick one family from the `craft/transitions.md` menu (register-matched, parameters included). This is the same judgment the taste contract and the `hyperframes` skill's `references/transitions.md` mood tables govern — apply it here too, not just in style-replication.

**Ending.** A bookend — returning to the opening's scene or object to close the loop — is the highest-leverage move for a premium feel. Prefer leaving a hook or an emotional pause over a flat verbal summary.

**Text cards & titled B-roll.** When the piece calls for chapter cards,
location/time labels or text-led breathing points, don't default to plain
type on a color block — consult the register → text-treatment table in
`craft/art-direction.md` §2 first. A cozy family/travel vlog earns a brush
banner or collage cardstock label (generated art assets, one style per
piece); a tech/product vlog stays with clean designed type — art text there
reads as costume, not craft. Build every card to the card-anatomy rule
(same section): backplate + type hierarchy + edge-anchored accents with
staggered entrances — a single line floating on flat color is a placeholder,
not a deliverable. The chosen treatment goes into the taste contract's Text
treatment line before any card is built.

**Picture-in-picture.** Use for map/location pins, phone-screen inserts (texting, searching), or side-by-side comparisons (before/after, multi-angle). Respect the skill's `[no-occlusion]` rule: shadow + rounded corner + restrained proportion — the PIP must not outweigh the main frame's visual weight.

**B-roll.** Placing B-roll is this skill's job, not the user's — do a
dedicated B-roll pass over the assembled timeline and propose insertions
proactively instead of waiting to be asked. Scan for the classic trigger
points, then reverse-lookup candidates in the Phase 1 keyword index:

- Any talking-face stretch longer than ~8-10s — cover part of it, keeping
  the speech audio running underneath (J/L-cut per Phase 5)
- Something mentioned but not shown — a place, dish, object or person named
  in speech is a standing invitation to cut to it
- Insert during speech pauses/breaths so the edit doesn't dead-stare at a talking face
- Use over emotional transitions to give the viewer time to process
- Use to cover narrative gaps when a single clip can't carry the story alone

Each insert still earns its place — breathing point, evidence, or gap cover;
never wallpaper. If the footage log has no matching clip, say so rather than
forcing an off-topic shot (a designed text card per the paragraph above can
fill the hole instead).

## Phase 5 — Intra-Clip Re-Trim (Never Use a Raw Clip Whole)

- **Golden-segment rule.** For a 10s source clip, isolate the 3-4s with the highest information or emotional density; the rest is setup or dead motion — cut it, don't keep it "just in case."
- **Speed treatment.** Light slow-motion on emotional peaks (a turn-and-smile) for emphasis; speed-ramp through purely procedural motion (walking, opening a door) rather than leaving it at real-time.
- **J-cut / L-cut (audio-picture split edit).** Let audio lead into or trail out of a cut instead of hard-syncing both tracks — speech starts before the picture cuts to the speaker, or continues briefly after the picture has moved on. In FFmpeg, offset the audio and video trim points independently; in HyperFrames, offset the `<audio>` and `<video>` elements' `data-start` values. This single technique reads as noticeably more "professional" in vlogs.
- **Reframe for vertical.** When repurposing horizontal footage for a vertical platform, don't naively center-crop. Use a subject-centered zoom or a blurred-background pad to fill the frame (an `object-fit: cover` wrapper in HyperFrames compositions), or an auto-reframe helper if one is available in the current MCP runtime.

## Checklist Before Delivery

- [ ] `[design-floor]` three slots shipped and verified on the render:
      designed **Opening** (1-3s), ONE named **Transition** family,
      deliberate **Ending** (bookend/lockup + held frame, no fade-out) —
      defaults in `craft/art-direction.md` § Default kit when the brief is silent
- [ ] Footage log (`footage_log.md`) complete — Caption/Emotion/Quality/Slot recorded per clip before selection began
- [ ] Selection followed the dedupe → cut-ugly → cut-off-topic → prioritize order, with the quality threshold stated
- [ ] Pacing pattern (fast/slow/mixed) declared before cutting, and matches the footage's actual character
- [ ] Every transition is content-, color-, or sound-motivated — not decorative by default
- [ ] Text cards / titled B-roll use a register-matched treatment (declared in the taste contract) — no art text in a mismatched register, no undeclared plain-default — and every card meets the card-anatomy rule (backplate + hierarchy + accents)
- [ ] A proactive B-roll pass was run: long talking stretches covered, mentioned-but-unshown subjects cut to where footage exists, gaps disclosed where it doesn't
- [ ] Opening and ending are intentionally connected (bookend or deliberate contrast), not arbitrary
- [ ] No clip is used in full without isolating its golden segment first
- [ ] `<videos_dir>/edit/project.md` updated with the taste contract and decisions (`[log-or-it-didn't-happen]`)
- [ ] Final review planned and executed as its own step(s) — self-review pass + independent tool-verified pass, per `review/final-review.md` (`[review-independence]`)
- [ ] Output audio stream explicitly checked; any muted/dropped source audio disclosed and approved (`[audio-preserved]`)
- [ ] Final review completed per `review/final-review.md`, including the Appeal rubric
