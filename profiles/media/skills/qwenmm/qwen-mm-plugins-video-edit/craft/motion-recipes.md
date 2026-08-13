# Motion Recipes — Approved Animation Vocabulary

User-reviewed palette (live-demo reviews: Motion Lab ×3 + process-UI
Lab) — every recipe was demoed and explicitly kept. The taste contract's
Motion plan names recipes from here (`plan_gate.sh` checks); freestyle
needs a written reason. Copy-paste reference implementations live in
`snippets/` — start from the snippet, don't re-derive from this table's
one-line spec. Provenance: motion.dev / Motion UI / internal motion studies,
re-created deterministically (sampled springs + GSAP); the Motion runtime
is never imported (`engines/hyperframes.md`).

## Contents

- Asset quality bar (`[no-placeholder-assets]`)
- Spring parameter system — five presets
- Title & text entrances → `snippets/text-entrances.md`
- Hero & section compositions → `snippets/hero-compositions.md`
- Data & accent elements → `snippets/data-accents.md`
- Social-platform overlays → `snippets/social-overlays.md`
- Process & camera → `snippets/process-ui.md` + `craft/camera-rig.md`
- Choreography rules · Rejected in review

**Asset quality bar (`[no-placeholder-assets]`).** A recipe defines the
MOTION; the visual asset it animates must be delivery-grade on its own.
Placeholder-grade graphics are forbidden in deliverables even when the
choreography is right — workspace review verdict: motion cannot rescue an
undesigned graphic. Specifically:

- No system emoji as stickers/icons — use `qwen_image`-generated sticker
  assets (consistent illustration style, outlined, matted on white for clean
  cutout) or purpose-designed SVG.
- No bare rounded-rect + flat rgba fill for chips/bubbles/cards — layer
  gradient or texture + stroke + shadow per the card-anatomy rule
  (`craft/art-direction.md` §2).
- Hand-drawn elements (circles, arrows, underlines) need real stroke
  irregularity — generated brush assets or hand-authored SVG paths with
  varying width/wobble; a mathematically perfect ellipse reads as fake.
- One design language per piece: overlay assets share palette, stroke
  weight and corner style, declared in the taste contract.

## Spring parameter system (Motion UI production presets)

Use these five presets by name instead of inventing constants:

| Preset | stiffness/damping | Feel | Use for |
|--------|-------------------|------|---------|
| `snap` | 1218 / 70 | instant, no bounce | micro UI, cursor-like moves |
| `ui` | 305 / 33 | crisp default | cards, reveals, odometer wheels |
| `gentle` | 110 / 20 | unhurried | large elements, hero text masses |
| `lively` | 622 / 17 | playful bounce | badges, floating cards, emphasis |
| `ambient` | 43 / 13 | slow drift | background layers, idle float |

Stagger scale: `tight 0.04s` · `base 0.08s` · `relaxed 0.15s`.
Travel distances: hover 4px · element enter 24px · section enter 48px.

**Deterministic implementation** — sample the spring into fixed keyframes
(seek-safe and cold-render safe by construction), then feed GSAP keyframes /
CSS `@keyframes` / WAAPI:

```js
function springSamples(stiffness, damping, n = 70) {
  let x = 0, v = 0; const dt = 1 / 60, out = [];
  for (let i = 0; i < n; i++) {
    const a = -stiffness * (x - 1) - damping * v;
    v += a * dt; x += v * dt; out.push(x);
  }
  out[n - 1] = 1; return out;
}
```

## Title & text entrances

| Recipe | Parameters | Register |
|--------|-----------|----------|
| **Per-char spring rise** | each char its own spring 190/15, y 44px→0, stagger 60ms, opacity ramps in first 40% | universal hero titles |
| **Scatter-converge** | chars fly in from random ±140px offsets + rotation, `gentle`, blur 10→0, stagger `tight` | heavyweight title moments |
| **Line-mask reveal** | lines slide y 110%→0 inside `overflow:hidden` line boxes, `expo.out` 0.7s, 120ms line stagger; exit y→-110% `expo.in` | premium captions/openers — the default classy choice |
| **Scramble settle** | random glyphs roll 8×45ms per char, settle from center outward (90ms × center-distance) | tech / suspense reveals |
| **Natural typewriter** | 40–140ms random per char, +220ms after punctuation, blinking caret | narration / vlog monologue |

## Hero & section compositions

| Recipe | Parameters | Notes |
|--------|-----------|-------|
| **Editorial hero stagger** | 3 layers: line-mask headline (`expo.out`, stagger `base`) + floating cards (`lively`, y 24px) + oversized background word (5% white, `ambient` drift) | chapter cards / openers; the showpiece composition |
| **3D coverflow spread** | perspective 900px, per-step translateX 92px / rotateY 21° / z -90px / scale -0.06, `lively`, stagger from center | multi-asset preview, album beats |
| **Card-stack shuffle** | top card flicks out (`expo.in` 0.4s, +rotate 14°), lower cards promote via `ui` spring (y 12px / scale 0.06 per level) | photo/quote rotation |

## Data & accent elements

| Recipe | Parameters | Notes |
|--------|-----------|-------|
| **Count-up** | integer ramp with expo deceleration (~0.9s), unit chip pops in `lively` after landing | simple stat moments |
| **Odometer wheels** | each digit a vertical wheel, `ui` spring to position, right→left stagger 80ms, `tabular-nums` | the showpiece stat — prefer over count-up on hero numbers |
| **Badge spring drop** | drop from y -90px, spring 170/16, opacity in first 30% | location pins, tags |
| **Skeleton → content** | shimmer sweep 2×700ms, then content rows replace via `ui` spring, 90ms stagger | info cards, menu/price reveals |
| **Border beam** | conic highlight arc orbits a rounded panel border, 2.2s/loop, 2px band | spotlighting one card/PiP; ≤1 concurrent |
| **Breathing glow frame** | conic rainbow, blur 26px, edge-band mask, 6s rotation + 2.4s opacity breathe | "AI/magic moment" only — strong flavor, needs contract declaration |
| **Dual ticker** | two rows counter-scrolling, linear ~26s/loop, solid glyphs mixed with 1.5px outline glyphs | end credits, keyword walls, brand bands |

## Social-platform overlays (casual registers ONLY)

Platform-native decoration layers (抖音/小红书/Reels vocabulary) that sit ON
footage. **Register guard: these read as clutter in premium/documentary
pieces — legal only in casual/vlog/food/playful registers, and the taste
contract must say so.** These five survived review on choreography, with the
explicit caveat that demo visuals were placeholder-grade — in production the
`[no-placeholder-assets]` bar above applies with full force here.

| Recipe | Parameters | Notes |
|--------|-----------|-------|
| **Live comment bubbles** | bubbles pop in sequentially (`ui` spring, y 26px), older ones slide up to yield; ≤3 alive at once | side commentary, self-banter; obeys `[no-occlusion]` |
| **Story progress segments** | top segmented bar, each chapter fills linearly ~1.1s, author avatar chip springs in | multi-part narrative navigation cue |
| **Hand-drawn arrow poke** | SVG path draw-on 0.4s (`expo.out` dashoffset), then pokes toward target ×3 at 0.7s | strongest gaze-direction tool; pairs with a small label chip |
| **Comic speedlines burst** | radial line flash (conic stripes + center mask) ≤0.9s, center word slams in `lively` with outline stroke | dramatic emphasis, ≤1 per piece |
| **Polaroid toss-in** | `ui` spring, rotate 18°→-3° with slight overshoot, white frame + tape corner + handwritten date | memory/recap moments |

## Process & camera (tech/product-demo vocabulary — process-UI lineage)

Reviewed and kept from a live demo pass. Code: `snippets/process-ui.md`; camera
system: `craft/camera-rig.md`. "Show process, not magic results" — the
product is a collaborator, not a magician.

| Recipe | Parameters | Notes |
|--------|-----------|-------|
| **Five-act skeleton** (Slow-Fast-Boom-Stop) | labels at 15/15/40/20/10% of scene; S5 = hard-stop hold, never fade-out | narrative structure for promo scenes |
| **Chunk reveal** | punctuation-split chunks, seeded 40-120ms gaps, proxy onUpdate; +0.5s courtesy hold before the result | AI/streaming moments |
| **Mouse arc + click** | quadratic bézier + dual-sine jitter ±2px converging, `power1.inOut`; click 0.08s shrink → `back.out` | UI demos; cursor must LAND (`looks/` rule) |
| **Focus switch trio** | brightness+saturate+blur via one CSS var, 0.15s flash guide; release returns blur to 0 | multi-panel focus direction |
| **FLIP shared element** | final-state layout, start pose in transforms only, inner text enters late | button→input, state morphs |
| **Breathing expand** | scaleX 0.4L → scaleY joins at 0.3L → content at 0.75L | panel/card reveals |
| **Anticipation entrance** | function ease (dips −0.3, transform-only) or 3-stage prep/action/follow-through | re-approved — was on the rejected list |
| **Camera rig moves** | settle-in 1.06x · zoomDur log timing · focus-transfer pan · curtain pull-out · diagonal dual-freq drift · 3D golden angle | `craft/camera-rig.md` owns the system + budget |

## Footage devices (act on the material itself — the vlog/montage backbone)

Code in `snippets/footage-devices.md`. These are what "rich but restrained"
means on real footage — a piece whose only devices are text/UI overlays
reads as "给录像加了标题".

| Recipe | Parameters | Use for |
|--------|------------|---------|
| **Freeze-punch still** | pre-extracted peak still, `snap` punch 1→1.12, ring accent draws on +80ms; 2-3 per piece on real peaks only | emotional peak emphasis |
| **Speed-ramp bake** | ffmpeg `setpts` pre-bake (2-2.5x fast / 0.5x slow), hard cut at the tempo change; one ramp pair per piece | energy shifts, rush-in → savor |
| **Crop-reframe** | scale ≤2.8 + `transform-origin` at subject (coords from perception pass); same segment recut at 2 origins = 2 shots | shot variety from monotonous wide/selfie footage |
| **Circle-mask reveal** | `clipPath: circle()` collapse anchored on the motivating object, `expo.inOut` 0.55s, outgoing clip on higher track | motivated transitions at object/action points |
| **Tracking label** | 3-6 position samples from real frames, `sine.inOut` between, `lively` pop-in; ≤1 per piece, never over faces | text that participates in the action |
| **Split-screen sync** | two top-level clips 50/50, panels slide in `expo.out` 0.5s, divider bar snaps | mirrored/parallel actions |
| **Ring accent draw-on** | SVG dashoffset 100→0, `power2.out` 0.45s over live footage, exit ≤1.2s | hand-drawn emphasis without freezing |

## Choreography rules

- **Grid center-out**: for element groups, delay = euclidean distance from
  center × 70ms — reads as a ripple, richer than top-left raster order.
- **visualDuration beat-sync**: on beat-cut pieces the element's BODY arrives
  on the beat line; the spring's bounce tail spills after the beat. Time the
  arrival (~35% of sampled duration covers ~95% travel), not the animation
  end (`craft/music-beat-sync.md`).
- **Spring vs expo**: spring (micro-overshoot) for playful/organic registers;
  `expo.out` (direct settle) for premium/tech. Same register logic as
  `craft/art-direction.md` §2; never mix both feels on peer elements.
- **Budget**: max 1–2 showpiece recipes (editorial hero, coverflow, glow) per
  piece; accents obey the information_density dial and `[no-occlusion]`.
- **Idle micro-motion**: any overlay holding >1.5s keeps living — breathe
  `scale 1.0→1.02` or ±1° tilt, finite yoyo repeats (badge life-cycle code
  in `snippets/data-accents.md`). Enter-then-sit-dead reads as a pasted
  sticker; key parameters may also pulse a highlight color once.
- Loops (ticker, beam, glow, ambient drift) are pure fixed-rate keyframe
  loops — deterministic by construction, safe in HyperFrames.

## Rejected in review (use only on explicit user request)

Path draw-on · typewriter-explode ·
cinematic blur-up mega-title · double-tap like burst · floating hearts
stream · sticker pop & wiggle · scribble circle draw-on · sparkle twinkles ·
bokeh drift · film light leak sweep · logo morph collapse (reviewed).

Re-approvals: anticipation entrance left this list (the parameterised
parameters passed re-review — `snippets/process-ui.md`).
