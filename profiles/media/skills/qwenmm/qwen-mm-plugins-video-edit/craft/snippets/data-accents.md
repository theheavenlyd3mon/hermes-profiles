# Snippets — Data & Accent Elements

Recipes from `craft/motion-recipes.md` § Data & accent elements. Helpers
from `snippets/README.md` in scope; `tl` / `T0` as defined there.

Contents: Count-up · Odometer wheels · Badge spring drop · Skeleton→content ·
Border beam · Breathing glow frame · Dual ticker

## Count-up — simple stat moments

Integer ramp with expo deceleration (~0.9s), unit chip pops in `lively`
after landing. `textContent` written only in `onUpdate` — re-fires on seek.

```html
<div class="stat"><span class="num">0</span><span class="unit">家店</span></div>
<style>
  .stat { display:flex; align-items:baseline; }
  .num { color:#fff; font-size:64px; font-weight:800; font-variant-numeric:tabular-nums; }
  .unit { color:#ffd76a; font-size:22px; font-weight:700; margin-left:6px; opacity:0; }
</style>
```

```js
const TARGET = 127, numEl = document.querySelector('.stat .num');
const proxy = { v: 0 };
tl.to(proxy, { v: TARGET, duration: 0.9, ease: 'expo.out',
  onUpdate: () => numEl.textContent = Math.round(proxy.v) }, T0);
tl.to('.stat .unit', { keyframes: sKF('lively', p => ({
  scale: 0.4 + 0.6 * p, opacity: Math.min(1, p * 2.5) })),
  duration: 0.6, ease: 'none' }, T0 + 0.9);
```

## Odometer wheels — the showpiece stat

Each digit a vertical wheel of 0-9, `ui` spring to position, right→left
stagger 80ms, `tabular-nums`. Prefer over count-up on hero numbers.

```html
<div class="odometer"><!-- one .digit per char of the target number -->
  <div class="digit" data-d="2"></div><div class="digit" data-d="3"></div>
  <div class="digit" data-d="8"></div><div class="digit" data-d="0"></div>
  <span class="unit">km 骑行</span>
</div>
<style>
  .odometer { display:flex; align-items:baseline; }
  .digit { height:64px; overflow:hidden; }
  .digit .wheel { display:flex; flex-direction:column; }
  .digit .wheel span { color:#fff; font-size:56px; font-weight:800; height:64px;
    line-height:64px; font-variant-numeric:tabular-nums; text-align:center; min-width:.62em; }
  .unit { color:#ffd76a; font-size:20px; font-weight:700; margin-left:8px; opacity:0; }
</style>
```

```js
const H = 64, digits = gsap.utils.toArray('.odometer .digit');
digits.forEach(d => d.innerHTML = `<div class="wheel">${
  Array.from({ length: 10 }, (_, k) => `<span>${k}</span>`).join('')}</div>`);
digits.forEach((d, i) => {
  const target = +d.dataset.d;
  tl.to(d.querySelector('.wheel'), {
    keyframes: sKF('ui', p => ({ y: -target * H * p })),
    duration: 1.1, ease: 'none'
  }, T0 + (digits.length - 1 - i) * 0.08);       // right → left
});
tl.to('.odometer .unit', { keyframes: sKF('lively', p => ({
  scale: 0.5 + 0.5 * p, opacity: Math.min(1, p * 2.5) })),
  duration: 0.6, ease: 'none' }, T0 + 1.2);
```

## Badge spring drop — location pins, tags

Drop from y -90px, spring 170/16 (between `gentle` and `ui` — reviewed as
its own constant), opacity in the first 30%.

```html
<div class="badge">📍 巧克力山 · 打卡</div>
<style>
  .badge { position:absolute; left:50%; top:40%; transform:translateX(-50%);
    background:#d94f2b; color:#fff; border-radius:999px; padding:10px 26px;
    font-size:16px; font-weight:800; box-shadow:0 10px 30px rgba(217,79,43,.35); opacity:0; }
</style>
```

```js
tl.to('.badge', {
  keyframes: springKeyframes(170, 16, p => ({
    y: (1 - p) * -90, opacity: Math.min(1, p * 3)
  })), duration: 0.9, ease: 'none'
}, T0);
```

**A badge is alive for its whole stay — entrance is only a third of the
job.** Static labels that spring in and sit dead until they vanish read as
template stickers. The full life-cycle:

```js
// 2. idle — gentle breathe + micro tilt for the badge's whole hold (finite
//    repeats, still seek-safe; scale D/1.6 cycles to fill the hold time D)
tl.to('.badge', { scale: 1.03, rotation: 1.2, duration: 0.8,
  ease: 'sine.inOut', yoyo: true, repeat: Math.ceil(D / 0.8 / 2) * 2 - 1 }, T0 + 0.9);
// 3. exit — choreographed, never a bare opacity cut
tl.to('.badge', { y: -26, opacity: 0, duration: 0.3, ease: 'back.in(1.6)' }, T0 + D - 0.3);
// icon chip gets its own late bounce so the badge reads two-layered
tl.fromTo('.badge .ico', { scale: 0 }, { keyframes: sKF('lively', p => ({ scale: p })),
  duration: 0.5, ease: 'none', immediateRender: false }, T0 + 0.35);
```

Vary the anchor per scene (left-bottom → top-right → beside the subject);
one badge per piece may track the action instead
(`footage-devices.md` § Tracking label).

## Skeleton → content — info cards, menu/price reveals

Shimmer sweep 2×700ms, then content rows replace via `ui` spring, 90ms
stagger. Skeleton and content are sibling layers toggled with autoAlpha —
no innerHTML swap (seek-safe).

```html
<div class="info-card">
  <div class="skel">
    <div class="sk" style="width:40%"><i></i></div>
    <div class="sk" style="width:80%;height:22px"><i></i></div>
    <div class="sk" style="width:60%"><i></i></div>
  </div>
  <div class="content">
    <div class="row kicker">TODAY'S PICK</div>
    <div class="row title">辣油拌面 · ¥18</div>
    <div class="row sub">本地人从小吃到大的味道</div>
  </div>
</div>
<style>
  .info-card { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%);
    width:56%; background:#1d1d25; border-radius:14px; padding:16px; overflow:hidden; }
  .sk { height:14px; border-radius:6px; background:#26262e; margin-top:10px;
    position:relative; overflow:hidden; }
  .sk:first-child { margin-top:0; }
  .sk i { position:absolute; inset:0; transform:translateX(-100%);
    background:linear-gradient(100deg,transparent 30%,rgba(255,255,255,.14) 50%,transparent 70%); }
  .content { position:absolute; inset:16px; opacity:0; }
  .content .kicker { color:#ffd76a; font-size:12px; letter-spacing:2px; }
  .content .title { color:#fff; font-size:22px; font-weight:800; margin-top:6px; }
  .content .sub { color:#9a9aa5; font-size:13px; margin-top:6px; }
  .content .row { opacity:0; }
</style>
```

```js
for (let r = 0; r < 2; r++)
  tl.fromTo('.sk i', { xPercent: -100 }, { xPercent: 100, duration: 0.7,
    ease: 'sine.inOut' }, T0 + r * 0.7);
tl.set('.skel', { autoAlpha: 0 }, T0 + 1.4);
tl.set('.content', { opacity: 1 }, T0 + 1.4);
gsap.utils.toArray('.content .row').forEach((el, i) => {
  tl.to(el, { keyframes: sKF('ui', p => ({
    y: (1 - p) * 18, opacity: Math.min(1, p * 2.5) })),
    duration: 0.65, ease: 'none' }, T0 + 1.4 + i * 0.09);
});
```

## Border beam — spotlighting one card/PiP (≤1 concurrent)

Conic highlight arc orbits a rounded panel border, 2.2s/loop, 2px band.
The beam is an oversized conic layer clipped by the 2px padding frame.

```html
<div class="beam-card">
  <div class="beam"></div>
  <div class="beam-inner"><!-- panel content --></div>
</div>
<style>
  .beam-card { position:absolute; width:270px; height:150px; border-radius:16px;
    padding:2px; overflow:hidden; opacity:0; }
  .beam { position:absolute; left:50%; top:50%; width:600px; height:600px;
    margin:-300px 0 0 -300px;
    background:conic-gradient(transparent 0deg,transparent 300deg,#ffd76a 340deg,#fff 350deg,transparent 360deg); }
  .beam-inner { position:absolute; inset:2px; border-radius:14px; background:#15151b; }
</style>
```

```js
tl.to('.beam-card', { keyframes: sKF('ui', p => ({
  opacity: Math.min(1, p * 2), scale: 0.94 + 0.06 * p })),
  duration: 0.6, ease: 'none' }, T0);
const SPIN = 2.2;                                  // finite: sized to the scene
tl.to('.beam', { rotation: 360, duration: SPIN, ease: 'none',
  repeat: Math.ceil(SCENE_DUR / SPIN) }, T0);
```

## Breathing glow frame — "AI/magic moment" only (contract declaration required)

Conic rainbow, blur 26px, edge-band mask, 6s rotation + 2.4s opacity
breathe. Strong flavor — one per piece, declared in the taste contract.

```html
<div class="ai-glow"></div>
<style>
  .ai-glow { position:absolute; inset:-12%; opacity:0;
    background:conic-gradient(from 0deg,#ff5f6d,#ffc371,#4facfe,#a18cd1,#ff5f6d);
    filter:blur(26px) saturate(1.4);
    -webkit-mask-image:radial-gradient(ellipse 68% 62% at 50% 50%,transparent 58%,#000 78%);
    mask-image:radial-gradient(ellipse 68% 62% at 50% 50%,transparent 58%,#000 78%); }
</style>
```

```js
tl.to('.ai-glow', { opacity: 0.45, duration: 0.5, ease: 'none' }, T0);
tl.to('.ai-glow', { rotation: 360, duration: 6, ease: 'none',
  repeat: Math.ceil(SCENE_DUR / 6) }, T0);
tl.to('.ai-glow', { opacity: 0.9, duration: 1.2, ease: 'sine.inOut',
  repeat: Math.ceil(SCENE_DUR / 2.4) * 2, yoyo: true }, T0 + 0.5);
```

## Dual ticker — end credits, keyword walls, brand bands

Two rows counter-scrolling, linear ~26s/loop, solid glyphs mixed with 1.5px
outline glyphs. Duplicate the word list once so `-50%` loops seamlessly.

```html
<div class="ticker">
  <div class="t-row t-a"><!-- words ×2, alternating .solid / .outline --></div>
  <div class="t-row t-b"><!-- same, phase-shifted --></div>
</div>
<style>
  .ticker { position:absolute; inset:0; display:flex; flex-direction:column;
    justify-content:center; gap:18px; }
  .t-row { display:flex; width:max-content; }
  .t-row span { font-size:30px; font-weight:900; margin:0 18px; white-space:nowrap; }
  .t-row .solid { color:#fff; }
  .t-row .outline { color:transparent; -webkit-text-stroke:1.5px rgba(255,255,255,.55); }
</style>
```

```js
const LOOP = 26;
tl.fromTo('.t-a', { xPercent: 0 },   { xPercent: -50, duration: LOOP, ease: 'none',
  repeat: Math.ceil(SCENE_DUR / LOOP) }, T0);
tl.fromTo('.t-b', { xPercent: -50 }, { xPercent: 0,   duration: LOOP, ease: 'none',
  repeat: Math.ceil(SCENE_DUR / LOOP) }, T0);
```
