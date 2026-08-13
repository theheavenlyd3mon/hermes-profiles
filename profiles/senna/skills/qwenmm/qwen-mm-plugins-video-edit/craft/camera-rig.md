# Camera Rig — Lens Motion for Designed Compositions

User-reviewed ("特别好，宣传/科技类视频会很有意思") — distilled
from an internal GSAP camera-language study. Scope:
HyperFrames designed compositions (promo, tech demo, chapter cards). For
punch-ins on real footage, framing integrity rules (`[no-zoom-drift]`,
`craft/transitions.md`) still govern.

## The one structural rule

Camera motion and element motion NEVER share a transform. All lens-level
tweens drive one `cam` proxy object; element animations live inside
`#world` and never get touched by camera tweens.

```html
<div id="viewport">                <!-- fixed viewport, overflow:hidden -->
  <div id="camera">                <!-- lens layer: camera transform only -->
    <div id="world">…</div>        <!-- element animations happen in here -->
  </div>
  <div id="hud">…</div>            <!-- captions/badges: sibling = naturally static -->
</div>
```

```css
#viewport { position:relative; width:1920px; height:1080px; overflow:hidden; }
#camera   { position:absolute; inset:0; perspective-origin:960px 540px; }
#world    { position:absolute; transform-origin:0 0; will-change:transform; }
/* pan safety: #world size ≥ viewport + max pan amplitude + 8% margin */
```

## Cam proxy (2D) — everything derives from one object

```js
const cam = { cx: 960, cy: 540, zoom: 1 };
const world = document.querySelector('#world');
function applyCam() {
  world.style.transform =
    `translate(${960 - cam.cx * cam.zoom}px, ${540 - cam.cy * cam.zoom}px) scale(${cam.zoom})`;
}
// after registering the timeline: applyCam();  ← first-frame insurance
// (a paused timeline at t=0 may not fire onUpdate)
```

3D variant (rotX/rotY): use CSS `zoom` on `#world` instead of `scale()` —
layout-level zoom re-rasterizes text at the enlarged size, curing blurry
text in 3D close-ups. CSS `zoom` reflows every frame: acceptable ONLY here
(offline frame-by-frame rendering; realtime preview may drop frames — judge
by the render, not the preview), and it must not spread beyond `#world`.

## Logarithmic zoom duration — fixed durations read amateur

```js
// 1→2x maps to 0.55s; any zoom magnitude gets the same VISUAL speed
function zoomDur(z1, z2) {
  return gsap.utils.clamp(0.30, 0.94,
    0.55 * Math.abs(Math.log(z2 / z1)) / Math.LN2);
}
```

## The four-segment vocabulary

Easing: deliberate push/pull `power3.inOut`; follow moves
`gsap.parseEase("0.33,0,0.15,1")`.

```js
const followEase = gsap.parseEase('0.33,0,0.15,1');
// 1. settle-in micro push: open at 1.06x, ease out to full over ~3s
//    (only for pieces >14s whose first shot >7s)
tl.fromTo(cam, { zoom: 1.06 },
  { zoom: 1, duration: 3.0, ease: 'power2.out', onUpdate: applyCam }, 0);
// 2. push-in to a close-up; duration from zoomDur; then HOLD ≥1.2s (no tween)
tl.to(cam, { cx: 1240, cy: 430, zoom: 1.8,
  duration: zoomDur(1, 1.8), ease: 'power3.inOut', onUpdate: applyCam }, 's2');
// 3. mid-distance focus transfer: do NOT return to 1x — pan across directly
tl.to(cam, { cx: 880, cy: 620,
  duration: 0.7, ease: followEase, onUpdate: applyCam }, 's3+=1.5');
// 4. curtain pull-out + ≥0.8s full-frame hold covered by data-duration
tl.to(cam, { cx: 960, cy: 540, zoom: 1,
  duration: 0.55, ease: 'power3.inOut', onUpdate: applyCam }, 's5');
```

## Camera budget (planning-time rules, not code)

- Adjacent camera tweens start ≥2.6s apart; ≤4-5 moves per 15s window.
- A zoom below 1.25x is not worth scheduling — cut it.
- One 3D pop-out highlight per piece maximum (showpiece budget applies).

## Related space moves (same review batch)

**Diagonal pan drift** — handheld feel on a static stage. Two yoyo tweens
with incommensurate periods (path never closes). Finite repeats.

```js
tl.to('#world', { x: 40, duration: 4.6, ease: 'sine.inOut',
  yoyo: true, repeat: Math.ceil(D / 4.6) }, 0);
tl.to('#world', { y: 30, duration: 2.9, ease: 'sine.inOut',
  yoyo: true, repeat: Math.ceil(D / 2.9) }, 0);
```

**3D golden angle** — the lens sits above-left of a desk: static
`perspective: 2400px` + cards layered by `translateZ` (30/-20/60px on a
3n/5n/7n rhythm), entrance rises from flat to `rotationX: 8, rotationY: -4`
over 1.4s `expo.out`.

## Constant-size annotations & parallax

- Captions/chrome go in `#hud` (free). A label that must track a world
  element while keeping its size: counter-scale it `scale(1/cam.zoom)`
  inside `applyCam`; give its ENTRANCE animation to a child element so the
  two transforms never fight.
- Parallax layers get NO independent tweens — each layer's offset is the
  camera displacement × a coefficient (adjacent coefficients ≥2× apart,
  ≤4 layers), so layers stay in sync and seek-safe by construction.

## Self-check before render

- [ ] Camera tweens only touch `cam`; nothing inside `#world` shares them
- [ ] `applyCam()` called once after timeline registration (first frame)
- [ ] 3D text close-ups use CSS `zoom`, not `scale()` (blur check)
- [ ] All zoom durations from `zoomDur()`, no hand-written constants
- [ ] Post-pull-out full-frame hold ≥0.8s with zero tweens
- [ ] Budget: spacing ≥2.6s, ≤4-5 moves/15s, no sub-1.25x zooms
