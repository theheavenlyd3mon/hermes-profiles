# Transitions — Named Menu & Selection Rules

This card owns transition *selection* (which seam treatment, for which
register, at what parameters). Implementation is routed: designed transitions
go through the `hyperframes` skill (its `references/transitions.md` mood
tables and `transitions/catalog.md` are the build-level source of truth —
never re-derive GSAP here, per `engines/hyperframes.md`); mechanical
dissolves/wipes may run in FFmpeg (`engines/ffmpeg-direct.md`).

Ground rules (before the menu):

- **Hard cut is the default seam**, and a good one — these entries are
  accents layered on top of a hard-cut spine, not replacements for it.
  Entrance motion on cuts: `craft/pacing-rhythm.md` § Hard-cut entrance
  grammar (accent budget, no opacity pops, overshoot register).
- **One transition family per piece.** Pick ONE signature seam treatment and
  repeat it; a different transition every seam reads as a template reel.
  Declare the family in the taste contract.
- **Motivated beats decorative.** Content-motivated seams (match cut, color
  rhyme, sound-led) outrank any effect. An effect must still answer "why
  here": section change, beat drop, location jump, time skip.
- **Framing integrity (`[no-zoom-drift]`).** Shots REST at exactly scale 1.0
  and native framing. A transition may pass through a micro scale (≤1.05,
  e.g. the dissolve+scale recipe) but must land back at precisely 1.0 — a
  seam that leaves the next shot at 1.02x, or a per-shot cover-crop that
  changes effective zoom cut-to-cut, reads as breathing/instability and
  crops the shot's composed framing. Zoom is never a patch for mismatched
  seams; resolution normalization happens ONCE at footage prep
  (`engines/ffmpeg-direct.md`), never per-seam at runtime. Deliberate zooms
  live under the camera budget (`craft/pacing-rhythm.md` §4), not inside
  transitions.

## The menu (default core)

Propose from this table by default.

| Transition | Feel / register | Key parameters | Not for | Route |
|------------|-----------------|----------------|---------|-------|
| **Hard cut** | the default spine of every piece | 0 frames; entrance grammar per `craft/pacing-rhythm.md` §4 | — | plain cut |
| **J/L-cut (sound-led)** | invisible, professional — audio carries the seam | audio leads/trails picture by 0.3–1.0s | nothing — universal | FFmpeg offset trims / HF `data-start` offsets |
| **Silky directional slide** | premium, calm energy | in from one side `expo.out`, out to opposite side `expo.in`, 0.5–0.7s; one axis per piece | chaotic action montages | `snippets/transitions.md` (copy-paste) |
| **Cross-dissolve + micro scale** | cinematic, emotional, nostalgic | ~0.6s overlap; incoming 1.045→1, outgoing →0.985, ease in/out; scenes ≥3s | fast-cut pieces (kills momentum) | `snippets/transitions.md`, or FFmpeg `xfade=fade` (offset = A_dur − fade_dur) |
| **Color-block / comic wipe** | playful, cute, comedy | diagonal block sweep 0.3–0.5s in a palette color; pairs with sticker/collage looks | premium, documentary | `snippets/transitions.md` |
| **Circle-mask reveal** | motivated seam anchored on a real object (pan lid, doorway, ball) | `clipPath: circle()` collapse, `expo.inOut` 0.55s; anchor coords from a perception pass | pieces with no motivating object | `snippets/footage-devices.md` |
| **Match cut / color rhyme** | invisible craft, highest-prestige seam | plan at selection time: action continuity or dominant-color/composition rhyme between A-out and B-in | n/a — but requires footage that supports it | pure cut — planned in the EDL, no effect |
| **Look-native seams** | piece-defining | film-reel advance, gallery ripple, big-number smash — when a `looks/` card owns the piece, its seam IS the transition family | mixing with another family | the owning `looks/` card |

## Benched (explicit request ONLY)

Do not propose these by default; use only when the user names one.

| Transition | Parameters if requested |
|------------|------------------------|
| Whip pan / directional blur | 0.25–0.4s, one consistent axis, matched blur directions |
| Zoom punch-through | ≤2 per piece, 0.3–0.45s, biggest beats only, never chained |
| Light flash (white/color) | 2–3 frames, ≤2 per piece, palette color not pure white |
| Speed-ramp seam | A-tail 1→3x into the cut, B at 1x, audio continuous; never in dialogue |

## Selection rules

1. **Register first.** Read the taste contract's design read + dials, then
   pick from the rows whose feel matches — the same table logic as
   `craft/art-direction.md` §2 text-treatment matching. Tech/premium → slide,
   dissolve+scale, match cut. Cute/playful → comic wipe. Travel/food energy →
   slide at faster timing (0.4–0.5s) over a hard-cut spine.
2. **Energy budget.** Loud transitions (comic wipe, any benched pick the user
   requests) compete with the signature device — combined count stays inside
   the restraint rules (`review/final-review.md` § Appeal, row 3).
3. **Duration discipline.** A transition longer than 0.7s is a scene of its
   own — only look-native seams have that right.
4. **Reference tasks bypass this menu.** Style replication names the
   reference's actual mechanism instead (`workflows/style-replication.md`
   Phase 2/4 routing).

## Verification

Every seam decision is written in the EDL/storyboard with its motivation.
After render: `scripts/black_check.sh` (gaps at seams), plus a `read_video`
pass at 4–8fps across each seam ±0.5s (`review/final-review.md` §B).
