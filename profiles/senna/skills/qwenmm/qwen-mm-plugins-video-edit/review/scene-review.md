# Scene Review — the fast gate inside the scene loop

Runs once per scene render, BEFORE the ledger row moves to VERIFIED/LOCKED
(`engines/hyperframes.md` § Scene-loop assembly). This is a minutes-scale
check, not an essay — its whole point is catching problems where fixes cost
seconds. The seven-row Appeal rubric does NOT run here; it grades the whole
piece once, at final review.

## The six checks (all on the SCENE RENDER, not snapshots)

1. **Devices** — every contract device this scene owns is visible at its
   timestamp: name → timestamp → what you saw. A device that didn't land
   blocks VERIFIED; "will fix in the master" is not a state that exists.
2. **Type & fonts** — real font files rendering (no PingFang/system
   fallback, no tofu/placeholder glyphs); every size ≥ `craft/fonts.md`
   § Type scale floor; legible at thumbnail zoom.
3. **Composition safety** — nothing covers faces/UI/focal action
   (`[no-occlusion]`); overlay anchor differs from the previous scene's
   (richness floor #4); every overlay has a full life-cycle — entrance,
   idle micro-motion if held >1.5s, choreographed exit with a hard kill
   (no element leaking past the scene's time box).
4. **Motion quality** — entrances match the declared recipes and presets;
   overshoot character fits the register; nothing rests at non-1.0 scale
   at scene end (`[no-zoom-drift]`); first and last frame clean
   (cold-render check — verify frame 0 on the render, not the preview).
5. **Technical** — `black_check.sh` on the scene render (interior AND
   head/tail); duration equals the locked time box exactly; scene-owned
   SFX present and peaking sanely.
6. **Watch it once as a viewer** — does the beat land? Anything you didn't
   have time to read (T2)? This impression IS the NL observation the
   ledger row records; write it while it's fresh, doubts included.

Pass all six → ledger row VERIFIED with evidence (render path + NL note).
Any fix → re-render the scene → recheck what changed (scoped review
invalidation). Then LOCKED.

**Write each pass as an append-only iteration entry** in the scene's detail
section (`review/project-log.md` § Scene detail + iteration log): the six
check results · what you saw · what you changed · the proof frames. One entry
per render — never overwrite the previous one; the ledger row only points at
the newest. A scene taking 2-4 iterations is normal and the log is how that
history stays recoverable.

**Keep 1-3 proof frames per iteration** (`scenes/frames/S<N>_iter<K>_<t>s.jpg`)
— the frames where this scene's devices visibly land. When an iteration
fixes a specific defect, grab the SAME timestamp as the failing round: the
before/after pair at one `t` is what makes "fixed" verifiable instead of
asserted.

## What scene review CANNOT settle — defer, don't fake

These don't exist at scene level; checking them here is wasted work, and
"passing" them here is fiction. They are G rows, verified at global pass /
final review:

- Cross-scene transitions and seam timing (overlaps live in the master)
- Rhythm and energy ACROSS scenes; total piece pacing
- Unified grade consistency between scenes
- BGM, loudness, audio seams (`loudness_check.sh` runs on the final)
- Opening↔ending bookend echo
- Whole-piece restraint counts (T1 signature ≤2, richness floor totals) —
  keep a running tally in the ledger, settle the verdict at final review
- Master-layer bugs: z-order between scene layers, hard-kill collisions —
  re-confirm device timestamps on the FINAL mp4 even though scenes passed

## Relationship to final review

Scene review makes final review cheap, not optional: the Scene Ledger
arrives pre-filled with evidence, and the final pass re-confirms on the
delivered mp4 plus everything in the defer list above
(`review/final-review.md`). A piece whose scenes all passed can still fail
at final — that is the defer list doing its job, not a contradiction.
