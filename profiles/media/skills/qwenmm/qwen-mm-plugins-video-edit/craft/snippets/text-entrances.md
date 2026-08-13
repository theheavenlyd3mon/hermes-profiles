# Snippets — Title & Text Entrances

Recipes from `craft/motion-recipes.md` § Title & text entrances. Helpers
(`sKF`, `SPRING`, `prng`) from `snippets/README.md` must be in scope.
`tl` = the composition's paused master timeline; `T0` = scene-local start (s).

Contents: Per-char spring rise · Scatter-converge · Line-mask reveal ·
Scramble settle · Natural typewriter

## Per-char spring rise — universal hero titles

Spring 190/15 (custom, softer than `lively`), y 44px→0, stagger 60ms,
opacity ramps in the first 40% of travel.

```html
<div class="hero-title"><!-- one span per char, pre-split -->
  <span>山</span><span>谷</span><span>里</span><span>的</span><span>一</span><span>餐</span>
</div>
<style>
  .hero-title { display:flex; justify-content:center; }
  .hero-title span { display:inline-block; font-size:42px; font-weight:800;
    color:#fff; margin:0 2px; opacity:0; }
</style>
```

```js
document.querySelectorAll('.hero-title span').forEach((el, i) => {
  tl.to(el, {
    keyframes: springKeyframes(190, 15, p => ({
      y: (1 - p) * 44, opacity: Math.min(1, p * 2.2)
    })),
    duration: 0.8, ease: 'none'
  }, T0 + i * 0.06);
});
```

## Scatter-converge — heavyweight title moments

Chars fly in from seeded random ±140px offsets with rotation and blur 10→0,
`gentle` spring, stagger `tight` (40ms). Blur is filter-animated — cap this
recipe at one title per scene.

```js
const rand = prng(42);                       // fixed seed = same frames every render
document.querySelectorAll('.hero-title span').forEach((el, i) => {
  const x0 = (rand() - 0.5) * 280, y0 = (rand() - 0.5) * 180, r0 = (rand() - 0.5) * 50;
  tl.to(el, {
    keyframes: sKF('gentle', p => ({
      x: x0 * (1 - p), y: y0 * (1 - p), rotate: r0 * (1 - p),
      filter: `blur(${Math.max(0, 10 * (1 - p))}px)`,
      opacity: Math.min(1, p * 1.8)
    })),
    duration: 1.1, ease: 'none'
  }, T0 + i * 0.04);
});
```

## Line-mask reveal — the default classy choice

Lines slide y 110%→0 inside `overflow:hidden` line boxes, `expo.out` 0.7s,
120ms line stagger; exit y→-110% `expo.in`. Kicker/title/sub each get a box.

```html
<div class="reveal-block">
  <div class="mask"><div class="line kicker">EPISODE 02 · BOHOL</div></div>
  <div class="mask"><div class="line title">山谷里的一餐</div></div>
  <div class="mask"><div class="line sub">巧克力山下的第一顿本地菜</div></div>
</div>
<style>
  .mask { overflow: hidden; }
  .line { transform: translateY(110%); }
  .kicker { color:#ffd76a; font-size:14px; letter-spacing:4px; }
  .title  { color:#fff; font-size:40px; font-weight:800; margin-top:6px; }
  .sub    { color:#9a9aa5; font-size:14px; margin-top:8px; }
</style>
```

```js
const lines = gsap.utils.toArray('.reveal-block .line');
lines.forEach((el, i) => {
  tl.fromTo(el, { yPercent: 110 }, { yPercent: 0, duration: 0.7, ease: 'expo.out' },
    T0 + i * 0.12);
  tl.to(el, { yPercent: -110, duration: 0.45, ease: 'expo.in' },
    T0 + HOLD + i * 0.08);                   // HOLD ≥ 1s after last line lands (T2)
});
```

## Scramble settle — tech / suspense reveals

Random glyphs roll 8×45ms per char, settle from center outward
(90ms × center-distance). Seek-safe form: the glyph sequence is precomputed
per char; a proxy tween's `onUpdate` (re-fires on seek) indexes into it.

```js
const GLYPHS = 'アイウエオ0123456789XYZ#*';
const chars = gsap.utils.toArray('.hero-title span');
const mid = (chars.length - 1) / 2;
const rand = prng(7);
chars.forEach((el, i) => {
  const target = el.textContent;
  const seq = Array.from({ length: 8 }, () => GLYPHS[(rand() * GLYPHS.length) | 0]);
  const proxy = { k: 0 };
  el.textContent = seq[0]; el.style.color = '#ffd76a';
  tl.to(proxy, {
    k: 8, duration: 8 * 0.045, ease: 'none',
    onUpdate() {
      const step = Math.min(8, proxy.k | 0);
      if (step >= 8) { el.textContent = target; el.style.color = '#fff'; }
      else el.textContent = seq[step];
    }
  }, T0 + Math.abs(i - mid) * 0.09);
});
```

## Natural typewriter — narration / vlog monologue

Per-char delay 40–140ms seeded-random, +220ms after punctuation, blinking
caret. Chars are pre-built spans revealed with `display` (hidden chars take
no space, so the inline caret always sits after the last visible char).

```html
<div class="typeline">
  <!-- one span per char, display:none -->
  <span>今</span><span>天</span><span>想</span><span>带</span><span>你</span><span>去</span><span>一</span><span>个</span><span>地</span><span>方</span><span>…</span><span>…</span>
  <span class="caret"></span>
</div>
<style>
  .typeline { font-size:26px; color:#fff; font-weight:600; }
  .typeline span { display:none; }
  .typeline .caret { display:inline-block; width:3px; height:1.1em;
    background:#ffd76a; vertical-align:-0.15em; margin-left:2px; }
</style>
```

```js
const spans = gsap.utils.toArray('.typeline span:not(.caret)');
const rand = prng(11);
let t = T0;
spans.forEach(el => {
  tl.set(el, { display: 'inline-block' }, t);
  t += '，。……'.includes(el.textContent) ? 0.22 : 0.04 + rand() * 0.10;
});
// caret blink: finite stepped loop sized to the typing window + tail
const blinks = Math.ceil((t - T0 + 1.0) / 0.8);
tl.to('.typeline .caret',
  { opacity: 0, duration: 0.4, ease: 'steps(1)', repeat: blinks * 2, yoyo: true }, T0);
```
