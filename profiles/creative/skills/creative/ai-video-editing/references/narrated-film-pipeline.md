# Narrated short-film pipeline (multi-minute, dialogue-driven)

For a 2-4 minute essay/documentary film where a voiceover carries the narrative
(as opposed to a music-driven contest trailer). Proven end-to-end on a 3:38
two-host tech-history film ("The Evolution", 2026-08). The assembly/cut-to-
dialogue half of this is the editing skill's domain; the generation half is
documented here so the whole flow lives in one place.

## The order (do not skip ahead)
1. **Write + time the dialogue FIRST.** Render the VO (ElevenLabs two-voice is the
   quality bar: cast distinct voices with contrasting accents so the hosts have
   identities — e.g. a warm British storyteller + a bright American). Measure every
   line's REAL duration with ffprobe, then build the timeline on those numbers plus
   explicit inter-line gaps and longer act-transition gaps. The dialogue track is
   the SPINE; the video bends to it, never the reverse.
2. **Storyboard to the timeline.** Map each dialogue beat to a shot. Compute each
   shot's target duration from the line boundaries it covers. Vary clip lengths
   (5-20s) — don't default everything to one length.
3. **Generate reference STILLS first (FAL Seedream 4.5), one per shot.** These are
   the exact frame-0 anchors. QA the whole board as a contact sheet BEFORE animating
   (a director looks at the wall, not one frame). Re-roll flagged frames with
   tightened prompts (forbid stray borders/text, force the intended grade).
4. **Animate each still with image_to_video** (not text_to_video). Pinning the
   curated still as frame 0 is the single highest-leverage move for visual
   consistency across 15+ clips — the look is locked, only the motion is generated.
   Keep a repeated style prefix + a deliberate GRADE ARC across all prompts (e.g.
   warm amber Kodak → cool CRT blue → clinical data-center blue → electric
   gold/blue; "the grade is the clock"). Serial generation: one job at a time,
   ~5min cooldown, poll each to Ready.
5. **Assemble by cutting clips to the dialogue timeline.** For each beat: if the
   clip is longer than the beat, hard-trim; if shorter, slow-mo (setpts + trim).
   Insert black/title segments for act gaps and title cards. Concat, then mux the
   dialogue track with in/out fades. See ffmpeg-recipes.md for the exact commands.
6. **QA.** Bright-pixel check on every title card (recipe 9). Audio volumedetect
   (mean ~-25dB = healthy). Keyframe contact sheet for the progression + grade arc
   (video-analyze-qa.md failure mode 3).

## Lessons that paid off
- image_to_video off a curated still beats text_to_video for cross-clip consistency
  by a wide margin. Spend the effort on the stills.
- A repeated verbatim style prefix + a designed grade arc is what makes 18 separate
  generations read as ONE film.
- Bookend motifs (e.g. the same push-in on a glowing screen at open and close, forty
  years apart) carry the thesis visually without narration.
- Build the timeline on MEASURED VO durations. Estimated timecodes drift; real ones
  let every cut land on a spoken beat within ~0.03s.
- Total footage will be shorter than the dialogue track — the gap is title cards,
  act-gap blacks, and a few held beats. Plan for it; don't over-generate.
