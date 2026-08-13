# Pacing & Rhythm — Energy Skeleton, Cadence, Camera Budget

> **Bridge notice.** This document owns *when to cut and how long to hold*
> for real-footage timelines. Transition implementation, easing, and motion
> choreography live in the `hyperframes` skill family
> (`references/transitions.md`, `references/beat-direction.md`,
> `references/motion-principles.md`) — always read those before implementing
> any designed transition.

## 1. Declare the rhythm before cutting

Never discover pacing mid-timeline. Pick and record the pattern in
`project.md` first:

| Footage situation | Pattern | Shot length |
|---|---|---|
| High volume, many scenes, no single strong clip | Fast cut, on the beat grid | 0.5–2s |
| Low volume, high emotional density | Slow cut, breathing room | 3–8s |
| Mixed (some highlights + ordinary narrative) | Mixed — slow narrative, fast climax/recap | varies |

Common full-piece shape: **fast teaser open → slow narrative middle → fast
montage recap ending.**

## 2. Energy skeleton for multi-shot pieces (≥10s)

Budget the stillness FIRST, then distribute what remains to motion
(shot-scheduling discipline — first drafts are always too fast):

| Segment | Share | Energy | Hard floor |
|---|---|---|---|
| Opening | 8–12% | low | title/wordmark holds ≥1s after landing |
| Single-hero beat | 12–15% | low-mid, slowest of piece | one full action arc ≥3s |
| Climb (main body) | 55–65% | high⇄low alternating | insert a breathing card (2–6 words, huge negative space) every 1–2 feature shots |
| Close | 13–16% | peak of the piece | end on a wide/settled frame, ≥0.8s stillness — never end mid-punch-in |

Never schedule two consecutive high-energy shots; never repeat the same shot
length three times in a row.

## 3. Cadence rules (narrated / A-roll driven pieces)

Practical cadence rule for narration-led edits:

- Cut every **4–6 seconds**; a single shot never exceeds **~7s**.
- One narration beat (~8–10s of speech) = **two shots**: a wide establishing
  shot (carries any headline) + a detail cut-in (no headline). Audio runs
  continuously; the picture cuts mid-sentence.
- **Move on pause:** camera moves and cuts snap to speech gaps — shift
  earlier only, up to 0.8s (`timeline_view.py` shows the gaps).

## 4. Camera/zoom budget (Ken Burns, punch-ins, pans on footage)

Camera moves are a *budget*, not a garnish:

- **Visibility invariant:** what the viewer must see stays in frame with an
  8% safe margin — a move that violates this gets downgraded or cut.
- **Comfort budget:** ≥2.6–3.0s between camera changes; ≤4–5 changes per 15s
  window; ≤6 moves per minute (calm pieces: ≤4).
- **Zoom floor/ceiling:** below 1.25x not worth doing (except a 1.06x
  establishing micro push at open); above 2.3x the pixels won't hold.
- **Seam grammar (anti-nausea):** for adjacent focus targets — near (<0.22
  normalized distance) merge into one shot; mid (0.22–0.45) pan across in one
  shot; far (>0.45) drop the weaker shot. Never chain two far-focus jumps.
- No pump: don't return to 1x between two nearby pushes — transition directly.
- Every push-in ends on a concrete anchor (a face, a number, a dish, a
  button). If you can't name the anchor noun, delete the move.
- Static footage needs intrinsic motion: per-shot Ken Burns should follow the
  subject's own movement direction — but static IS a legal choice;
  text-reading and demo shots default to still.

### Hard-cut entrance grammar (seam aesthetics)

Hard cuts are the right call for fast-cut pieces — but "hard cut + entrance
effect on every shot" is where they turn ugly. When the piece needs actual
seam treatments beyond cuts, pick ONE family from the `craft/transitions.md`
menu. Practical rules:

- **Accent budget.** An entrance move on EVERY cut is a metronome, not
  rhythm — accents only register against plain cuts. Cap entrance accents at
  ~1 per 3–4 cuts, placed on downbeats/section changes; all other cuts land
  clean at full scale.
- **Never animate opacity at a shot entrance.** A 0.6→1 fade-pop over
  0.2–0.3s reads as flicker or a rendering bug, not energy. Shots enter at
  full opacity; motion (scale/position) carries the impact. Scope: hard-cut
  entrances — a DECLARED dissolve-family transition crossfades by
  definition and is governed by `craft/transitions.md`, not this rule.
- **Overshoot is a register.** Elastic/bounce entrances with >1.5x overshoot
  (e.g. 2.6x→1.0 text cards) are cartoon vocabulary — legal for cute/comedy
  registers only. Foodie, lifestyle, travel and premium pieces settle with
  `expo.out` at ≤1.08x overshoot. Scope: FOOTAGE entrances and full-frame
  moves; overlay/graphic elements follow the spring-preset register rule in
  `craft/motion-recipes.md` instead. Avoid punch-zoom + flash entrances as a
  default; they read harsh unless the user explicitly asks for that style.
  Prefer one declared transition family, such as silky directional slides —
  in from one side (`expo.out`), out to the opposite side (`expo.in`).
- **Harshness is structural before it is cosmetic.** If a hard-cut sequence
  feels jittery, the cause is usually too many short shots (the 37×1s strobe
  lesson) or unmotivated seams — fix shot length and seam motivation
  (`workflows/vlog-multi-source.md` Phase 4) before adding any transition
  effect on top.

## 5. Opening and ending

- **Opening hook lands inside 1.5s** for feed platforms: either a trailer
  montage of 0.5–1s snippets promising payoff, or the single strongest clip
  alone. Pick one; never neither. Plan the opening as the boldest beat.
- **Ending:** bookend to the opening's scene/object, or a "group photo"
  finale (a representative element of each section flies in around the
  title) at the piece's energy peak. Then hold.

## 6. Intra-clip trim discipline

- **Golden segment:** from a 10s source clip keep the 3–4s with the highest
  information/emotion density; never use a raw clip whole.
- **J-cut / L-cut:** audio leads or trails the picture cut instead of
  hard-syncing — the cheapest "professional" upgrade available.
- Cut edges land on word boundaries with 30–200ms padding
  (`craft/audio-first-cutting.md`).

## Self-check

- Declared pattern recorded before the first cut was made?
- Stillness budget reserved before motion was scheduled?
- Any shot >7s in a narrated piece? Any two consecutive high-energy shots?
- Every camera move: can you say what question it answers for the viewer?
- Watch the piece once as a stranger: where did your attention drop?
