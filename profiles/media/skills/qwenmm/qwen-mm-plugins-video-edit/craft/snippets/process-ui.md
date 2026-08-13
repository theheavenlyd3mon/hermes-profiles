# Snippets — Process & UI Simulation

Recipes distilled from an internal GSAP recipe study
(user-reviewed, all but one kept). Register: primarily tech / product
demo / promo — "the product is a collaborator, not a magician": show
process, not magic results. Helpers from `snippets/README.md` in scope
(`prng` replaces the source's mulberry32 — same purpose, seeded determinism).

Contents: Five-act skeleton · Chunk reveal · Mouse arc + click · Focus
switch trio · FLIP shared element · Breathing expand · Anticipation entrance

## Five-act skeleton — Slow-Fast-Boom-Stop (15/15/40/20/10%)

Narrative structure for a whole promo scene, not a single element. Even
rhythm reads as a tech demo; staged rhythm reads as a story. S5 holds on
the final frame — NEVER fade to black.

```js
const D = SCENE_DUR, at = p => T0 + D * p;
tl.addLabel('s1_trigger',  at(0));     // slow · one action + whitespace
tl.addLabel('s2_generate', at(0.15));  // one clear wow moment, nothing else
tl.addLabel('s3_process',  at(0.30));  // densest: staggers, streams, focus
tl.addLabel('s4_boom',     at(0.70));  // camera-level: pull-back / 3D pop
tl.addLabel('s5_hold',     at(0.90));  // logo lands, then NO tweens — hard stop
// example beats:
tl.fromTo('#terminal', { y: 48, autoAlpha: 0 },
  { y: 0, autoAlpha: 1, duration: 0.8, ease: 'expo.out' }, 's1_trigger+=0.1');
tl.fromTo('#result',   { scale: 0.92, autoAlpha: 0 },
  { scale: 1, autoAlpha: 1, duration: 0.7, ease: 'expo.out' }, 's2_generate');
tl.fromTo('.row', { y: 10, autoAlpha: 0 },
  { y: 0, autoAlpha: 1, duration: 0.4, ease: 'expo.out', stagger: 0.03 }, 's3_process');
tl.to('#stage', { scale: 0.82, rotationX: 8, duration: 1.2, ease: 'expo.inOut' }, 's4_boom');
```

The 22s variant maps to Invoke 3-4s / Process 5-6s / Insight 4-5s /
Output 3-4s / Hero 4-5s with the same label technique.

## Chunk reveal — streamed AI output (+ the 0.5s hold)

Token-stream feel: split on punctuation, seeded 40-120ms irregular gaps.
`onUpdate` recomputes the FULL visible text from t every frame — pure
function, reverse-seek correct. Never `tl.call()` (irreversible).

```js
const rand = prng(42);
const text = '为你生成了三个候选方案，第一个最激进。';
const chunks = text.split(/(?=[，。、；])|(?<=[，。、；])/);
const times = []; let acc = 0;
chunks.forEach(() => { acc += 0.04 + rand() * 0.08; times.push(acc); });
const el = document.querySelector('#stream'), tw = { t: 0 };
tl.to(tw, { t: acc, duration: acc, ease: 'none',
  onUpdate() { let n = 0;
    while (n < times.length && times[n] <= tw.t) n++;
    el.textContent = chunks.slice(0, n).join(''); } }, T0);
// courtesy hold: 0.5s of NOTHING before the result lands (human reaction time)
tl.fromTo('#result', { scale: 0.94, autoAlpha: 0 },
  { scale: 1, autoAlpha: 1, duration: 0.7, ease: 'expo.out' }, T0 + acc + 0.5);
```

## Mouse arc + hand jitter + click — believable cursor

Linear cursor interpolation reads as a machine. Quadratic bézier (control
point off the midline) + two incommensurate sines for jitter (±2px,
converging near the target) + symmetric easing.

```js
const P0 = [x0, y0], P2 = [tx, ty], P1 = [tx - 200, ty + 80];
const mouse = { p: 0 };
tl.to(mouse, { p: 1, duration: 1.1, ease: 'power1.inOut',
  onUpdate() { const t = mouse.p;
    let x = (1-t)*(1-t)*P0[0] + 2*(1-t)*t*P1[0] + t*t*P2[0];
    let y = (1-t)*(1-t)*P0[1] + 2*(1-t)*t*P1[1] + t*t*P2[1];
    x += Math.sin(t * 47.13) * 2 * (1 - t);
    y += Math.sin(t * 33.7 + 1.3) * 2 * (1 - t);
    gsap.set('#cursor', { x, y }); } }, T0);
// click: anticipation shrink → back.out release; the target must LIGHT UP
tl.to('#cursor', { scale: 0.85, duration: 0.08, ease: 'power1.in' }, '>');
tl.to('#cursor', { scale: 1, duration: 0.25, ease: 'back.out' }, '>');
tl.to('#target', { scale: 1.06, duration: 0.3, ease: 'expo.out' }, '<');
gsap.set('#cursor', { x: P0[0], y: P0[1] });   // first-frame insurance (t=0 onUpdate may not fire)
```

Pairs with the `looks/` rule: the cursor must truly LAND on the button —
a near-miss reads as broken.

## Focus switch trio + flash — background truly recedes

Opacity alone leaves non-focus elements sharp. Three filters via one CSS
variable; release MUST return blur to 0 (a half-blurred hold reads as a
render bug). Blur ≤24px on large surfaces; `will-change: filter` only on
elements whose blur actually animates.

```css
.tile { --f: 0; will-change: filter;
  filter: brightness(calc(1 - 0.5 * var(--f)))
          saturate(calc(1 - 0.3 * var(--f)))
          blur(calc(var(--f) * 4px)); }
```

```js
tl.to('.tile:not(.focus-target)', { '--f': 1, opacity: 0.4,
  duration: 0.5, ease: 'expo.out' }, T0);
tl.fromTo('#focusFlash', { backgroundColor: 'rgba(255,255,255,0.3)' },
  { backgroundColor: 'rgba(255,255,255,0)', duration: 0.15, ease: 'power1.out' }, T0 + 0.5);
tl.to('.tile', { '--f': 0, opacity: 1, duration: 0.5, ease: 'power2.inOut' }, T0 + 2.5);
```

## FLIP shared element — button expands into input

One element transitioning between two states, not two elements
cross-fading. Element sits in its FINAL layout; the start state is pure
transform (never tween width/height — reflow snap jitters on slow tails).

```css
#search-box { width: 560px; height: 56px; }   /* static final state */
```

```js
tl.fromTo('#search-box',
  { x: 200, scaleX: 120/560, scaleY: 44/56, transformOrigin: 'left top' },
  { x: 0, scaleX: 1, scaleY: 1, duration: 0.6, ease: 'expo.out' }, T0);
// inner text enters late so it is never seen stretched by scaleX
tl.fromTo('#search-box .placeholder', { autoAlpha: 0 },
  { autoAlpha: 1, duration: 0.3 }, T0 + 0.4);
```

## Breathing expand — open the shell, then pour the content

Panels never grow width and height together: scaleX first (40% of L),
scaleY joins at 30% of L, content fades in at 75% of L — hides content
distortion during scaling. If border/corner fidelity matters, switch to a
fixed shell + `clip-path` reveal.

```js
const L = 0.9;
tl.fromTo('#panel', { scaleX: 0, scaleY: 0.12, transformOrigin: 'left top' },
  { scaleX: 1, duration: 0.4 * L, ease: 'expo.out' }, T0);
tl.to('#panel', { scaleY: 1, duration: 0.7 * L, ease: 'expo.out' }, T0 + 0.3 * L);
tl.fromTo('#panel .content', { autoAlpha: 0, y: 8 },
  { autoAlpha: 1, y: 0, duration: 0.35 }, T0 + 0.75 * L);
```

## Anticipation entrance — re-approved

Previously rejected as a generic pull-back entrance; the parameterised
version passed re-review. Two forms — transform-only (the curve goes
negative; never on opacity/color):

```js
// single-tween function ease (pointwise-faithful to the source's Easing.anticipation)
const anticipation = t => t < 0.2 ? -0.3*(t/0.2)*(t/0.2)
  : (a => -0.012 + 1.012*a*a*(3-2*a))((t-0.2)/0.8);
tl.fromTo('#card', { y: 40 }, { y: 0, duration: 0.7, ease: anticipation }, T0);

// Disney three-stage: prep → action → follow-through
tl.to('#card', { scale: 0.95, duration: 0.12, ease: 'power1.in' }, T0);
tl.to('#card', { scale: 1.05, duration: 0.30, ease: 'expo.out' }, '>');
tl.to('#card', { scale: 1.00, duration: 0.35, ease: 'elastic.out(1,0.3)' }, '>');
```
