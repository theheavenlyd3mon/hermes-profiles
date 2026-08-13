# Motion Snippets — Copy-Paste Reference Implementations

Reference implementations for recipes in `craft/motion-recipes.md`, converted
into **seek-safe GSAP timeline form** for HyperFrames.

These are starting points, not registry blocks. How to adapt:

- Paste into the composition the `hyperframes` pipeline owns; rename
  selectors. Rejected-list recipes are deliberately absent.
- **Styling is demo dressing** (gold `#ffd76a`, white 42px type, plain
  chips): replace fonts and colors per the taste contract
  (`craft/fonts.md`, `craft/art-direction.md`). **Motion values are starting
  points, not frozen constants**: scale travel/timing to the piece, keep the
  recipe's CHARACTER (preset feel + choreography shape); deviate until it
  reads as a different feel = freestyle → log it in the contract.
- **Snippets are the supporting cast.** The signature device (taste
  contract) is the creativity slot — design it fresh per piece; a piece
  assembled entirely from stock snippets loses the Concept row in review.
  Reusable inventions should be added to the recipe card and snippet together.

| File | Recipes |
|------|---------|
| `text-entrances.md` | Per-char spring rise · Scatter-converge · Line-mask reveal · Scramble settle · Natural typewriter |
| `hero-compositions.md` | Editorial hero stagger · 3D coverflow spread · Card-stack shuffle |
| `data-accents.md` | Count-up · Odometer wheels · Badge spring drop · Skeleton→content · Border beam · Breathing glow frame · Dual ticker |
| `social-overlays.md` | Live comment bubbles · Story progress segments · Hand-drawn arrow poke · Comic speedlines burst · Polaroid toss-in |
| `footage-devices.md` | Freeze-punch still · Speed-ramp bake · Crop-reframe · Circle-mask reveal · Tracking label · Split-screen sync · Ring accent draw-on — **the devices that act on FOOTAGE; a vlog/montage body should draw most of its ≥3 device families from here** |
| `transitions.md` | Silky directional slide · Cross-dissolve + micro scale · Color-block wipe · J/L cut — self-contained two-clip implementations of the `craft/transitions.md` menu |
| `process-ui.md` | Five-act skeleton · Chunk reveal · Mouse arc + click · Focus switch trio · FLIP shared element · Breathing expand · Anticipation entrance (process-UI lineage; camera system → `craft/camera-rig.md`) |

## Shared helpers (paste once per composition)

```js
// Sampled spring → GSAP keyframes (fixed curve: seek-safe, cold-render safe).
// build(p) returns a vars object for progress p (p may overshoot 1).
function springKeyframes(stiffness, damping, build, n = 70) {
  let x = 0, v = 0; const dt = 1 / 60, out = [];
  for (let i = 0; i < n; i++) {
    const a = -stiffness * (x - 1) - damping * v;
    v += a * dt; x += v * dt; out.push(build(x));
  }
  out[n - 1] = build(1);          // land EXACTLY on the resting pose
  return out;
}
// The five approved presets (craft/motion-recipes.md) — use by name:
const SPRING = { snap:[1218,70], ui:[305,33], gentle:[110,20], lively:[622,17], ambient:[43,13] };
const sKF = (preset, build) => springKeyframes(...SPRING[preset], build);
// usage: tl.to('#el', { keyframes: sKF('ui', p => ({ y:(1-p)*24, opacity:Math.min(1,p*2.2) })), duration:0.85, ease:'none' }, T0);

// Deterministic pseudo-random (scatter offsets, typing cadence). NEVER call
// Math.random() in a composition — same seed ⇒ same frames on every render.
function prng(seed) { return () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 2 ** 32; }
```

## Hard conventions (all snippets follow these — keep them when adapting)

1. **One paused master timeline.** Every tween is added to the composition's
   GSAP timeline at an explicit position (`T0 + offset`). No `setTimeout`,
   no `await`, no `requestAnimationFrame`, no WAAPI `el.animate()` — those
   drive their own clock and break deterministic rendering.
2. **`ease:'none'` on sampled-spring keyframes.** The spring curve IS the
   easing; layering another ease distorts it.
3. **Destination vars always end at the resting pose** — including
   `opacity: 1` explicitly in the final state (cold-render safety: frame 0
   of a re-render must not catch a half-registered `from`).
4. **Motion via transforms** (`x`/`y`/`scale`/`rotate`), never `top/left`.
5. **Loops are finite.** `repeat: -1` inside a timeline makes its duration
   infinite; size repeats to the scene: `repeat: Math.ceil(sceneDur/loopDur)`.
6. **Text content never mutates.** Typewriter/scramble reveal pre-built
   spans (autoAlpha / stepped translateY); `textContent` writes only happen
   inside `onUpdate` of a proxy tween (count-up), which re-fires on seek.
7. Registers, budgets and pairing rules stay in `craft/motion-recipes.md` —
   the snippet is HOW, the recipe card is WHEN/WHETHER (plan_gate checks
   the contract names recipes, not snippets).
