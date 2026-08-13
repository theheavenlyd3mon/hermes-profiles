# Final Review — Evidence, Independence, Appeal

Run before presenting any rendered deliverable. Objective, evidence-based,
adversarial. Plan it as TWO separate steps in the todo list — never fold
into a "render and verify" bullet:

1. **Self-review pass** — the maker runs the checks below on its own output.
2. **Independent tool-verified pass** — for production-level, style-
   sensitive, reference-driven or ambiguous outputs, dispatch a
   clean-context review subagent. The maker has confirmation bias about its
   own output; **the first real check must not be the user's viewing.**
   Harness has no subagent capability ⇒ pass 2 = the `vision_chat`
   adversarial review (§C) + the review gate, and the verdict states this
   substitution — never silently skip pass 2.

## Contents

Review invalidation rule · A. Technical evidence (`review_gate.sh`) ·
B. Visual evidence · C. Second opinion · D. Appeal rubric (concept veto) ·
E. Delivery promise · Subagent brief · Verdict format

## Review invalidation rule

A review is valid only for the exact file reviewed. ANY mutation (re-render,
remux, subtitle burn, crop, concat, audio mix, patch) resets review status —
rerun this protocol on the new file before presenting it. The last log entry
before delivery must reference the same path/version being delivered.

## A. Technical evidence (objective, scripted)

**Mandatory single entry point:**

```bash
bash <skill-root>/scripts/review_gate.sh FINAL.mp4
```

One command runs all hard gates (ffprobe → loudness_check → black_check) and
prints a `REVIEW GATE` block with a byte-identity hash. **Paste that block
verbatim into the verdict and `project.md` — a review without it is void;
"pass" written by hand without gate output counts as a skipped review, not a
passed one.** Exit 2 = at least one hard failure; fix and re-run on the new
file.

Additional evidence per piece:

- `scripts/contact_sheet.sh FINAL.mp4 sheet.jpg` — full-duration frame
  evidence; inspect for black frames, repeats, glitches, chrome.
- Beat-synced pieces: `scripts/beat_grid.py FINAL.mp4 --cuts ...` — error
  table, all ≤3f (`craft/music-beat-sync.md`).
- `<videos_dir>/edit/project.md` exists and reflects this task's taste
  contract, decisions and outputs (`review/project-log.md`).

Gate details: `scripts/loudness_check.sh` exit 2 = `[audio-preserved]`
failure unless dropped audio was explicitly approved. `scripts/black_check.sh`
exit 2 = interior black segment (unfilled timeline gap / bad xfade offset /
missing asset rendering black); head/tail black is advisory but must match a
declared fade in the taste contract.

## B. Visual evidence (timestamped, full duration)

Inspect with `read_video`, not just the opening: first frame / cold open;
every seam ±0.5s; text/overlay/PiP moments; middle; last frame. Re-read
timing-sensitive windows at 4–8fps. For each criterion cite evidence — a
criterion without a timestamp cannot be marked pass:

```markdown
- 0:04.5 title readable over dark background — pass
- 0:23.4 transition flashes white unexpectedly — fail
```

Watch for: mojibake/tofu text, black frames, flash/hard transition
accidents, frozen crossfades, dropped/popping audio at seams, black bars,
duration drift, subject-matte edge crawl (cutout pieces:
`mcps/segmentation-matting.md` checks).

## C. Second opinion (`vision_chat`)

After direct inspection, ask `vision_chat` with concrete adversarial
prompts (black/blank frames? garbled text? occlusion? jarring transitions?
slideshow feel? reference mismatches?). A plausible finding must be fixed or
explicitly justified — never ignored because self-review already passed.

## D. Appeal rubric (concept can veto)

Score 0–10 per dimension against the taste contract
(`craft/art-direction.md`). **Concept ≤5 caps the total verdict at
"revise" — execution polish cannot rescue an empty concept.**

**Use these seven rows verbatim (`[rubric-verbatim]`).** Renaming them or
substituting your own dimensions voids the review — the rows below are
chosen precisely because they catch self-flattering empty edits.

**Row 0 also enforces `[design-floor]`:** if the piece has no opening
treatment, no designed body beats (a bare clip chain), or no deliberate
ending, concept is ≤5 by definition — "the footage speaks for itself" is not
a concept. Count the body beats on the render: at least one designed moment
per scene change, cadence per the density dial.

| # | Dimension | Anchor questions |
|---|-----------|------------------|
| 0 | **Concept** (veto) | Can you state the piece's idea in one sentence? Cover all text — is the subject still recognizable? Swap the subject — does the piece still "work"? (If yes → template, ≤5.) |
| 1 | Contract adherence | Do pacing/density/motion match the three dials? Design read realized? **Device ledger: every declared device (signature + each Body item) gets a render timestamp — declared-but-absent = fail this row**. Count ≥3 distinct BODY device families on the render (title/badges/closing card don't count — art-direction.md § Richness floor). |
| 2 | Rhythm | Hook inside 1.5s? Energy alternates? Holds respected (T2)? No shot >7s in narrated pieces? |
| 3 | Restraint | Signature device 1–2 uses (T1)? No mass glints (T3)? No repetition (T4)? |
| 4 | Craft quality | Seams motivated, text sharp, mattes clean, grade consistent |
| 5 | Sound | Two-track doctrine present? SFX pinned to real actions? Clean tail? |
| 6 | Typography & motion | Hero titles match the declared text treatment? Bare default font on a hero title without written justification = fail this row; **Chinese text in a system fallback (PingFang/Heiti) = fail even if declared** — bundled `zh/` faces exist (`craft/fonts.md`). Text below the Type scale floor = fail. Overlay/title/data motion matches the contract's Motion plan (named recipes) — undeclared freestyle motion = fail this row. |

Common failures to name explicitly: slow/unclear opening; flat shot rhythm;
decorative motion serving nothing; same layout every scene; text cards
dominating; hero titles in undeclared default type; overlay motion outside
the approved palette with no logged reason; uniform punch-in
entrance on every cut; opacity pops at shot entrances; elastic overshoot in
a non-cute register; shots resting at non-1.0 scale after a seam (zoom
drift/breathing); effective zoom or sharpness jumping cut-to-cut from
runtime rescaling; no reason to keep watching.

## E. Delivery promise

Multi-scene pieces deliver a **review board** beside the mp4:
`<videos_dir>/edit/board.html`, generated FROM the Scene Ledger (a view,
never hand-edited — regenerate after changes). One card per S/G row:
embedded scene-render preview + proof-frame thumbnails + ledger fields + the
NL observation + status badge; every card carries a ✓/✗ toggle and a
free-text suggestion box, with one-click export of all feedback (scene
numbers included) at the top. User feedback then arrives pre-addressed for
local repair.

Did the output preserve the approved direction/engine/treatment? Any
downgrade (motion→still, designed→plain, service swap, dropped audio) must
have been disclosed and approved — otherwise FAIL regardless of quality.
Engine check: the verdict's **Engine** line must match the `## Decision —
Engine` entry in `project.md`; a watchable deliverable assembled FFmpeg-only
without a logged mechanical exemption is an automatic FAIL here
(`[hyperframes-handoff]`).

## Independent subagent brief (pass 2)

Give the reviewer: final MP4 + contact sheet, taste contract, footage
log/storyboard, chosen look card, this protocol. Do NOT give: the maker's
reasoning, excuses, or iteration history. Require numbered findings with
frame/timestamp evidence, severity-ranked (fix-before-deliver / should-fix /
polish), plus "cannot verify" for missing inputs. No evidence-free "looks
good overall".

## Verdict format

```markdown
## Final Review
**Output:** /abs/path/final_v2.mp4  (reviewed after last mutation: yes)
**Best passing render:** same file as Output — confirm no better render exists (`[no-silent-downgrade]`)
**Engine:** hyperframes handoff | ffmpeg-mechanical (USER-granted exemption: quote it) — must match project.md's Engine Decision; missing line = void verdict
**Design floor:** opening · transition family · body beats (count them) · deliberate ending — all four present? (`[design-floor]`) **Verify on frames, not on the contract**: grab one frame from the opening card, one body beat, and the final 1s; check each against its contract slot line — declared-but-unrealized fails the slot. Verify the richness-floor counts on the render (≥3 body families, ≥2 motivated transitions, climax emphasis, varied placement, one grade).
**Device ledger:** each declared device → render timestamp(s), confirmed on
the FINAL mp4 (the Scene Ledger gives you the draft — aggregate its rows;
re-verify on the final render, master-layer bugs don't exist at scene
level). **A device with no timestamp makes the whole verdict FAIL — "PASS
with notes" is an unshipped edit**. Two legal exits only: implement it, or
amend the contract with a logged `## Decision` BEFORE assembly ends.
**Technical:** pass — REVIEW GATE block pasted below (mandatory, includes the plan-gate result)
**Visual:** pass — timestamped list
**Audio:** pass — loudness gate PASS, seams clean
**Beat sync:** pass — max err 2.1f  (or n/a)
**Appeal:** concept 8 · contract 7 · rhythm 8 · restraint 9 · craft 7 · sound 8
**Second opinion:** run — findings addressed
**Delivery promise:** pass
**Verdict:** deliver | revise (smallest targeted fix: ...) | blocked

<verbatim REVIEW GATE output for this exact file>
```

After any fix, rerun the full protocol on the new assembled output.
