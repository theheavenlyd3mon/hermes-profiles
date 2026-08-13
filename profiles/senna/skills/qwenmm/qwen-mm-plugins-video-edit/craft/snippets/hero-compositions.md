# Snippets — Hero & Section Compositions

Recipes from `craft/motion-recipes.md` § Hero & section compositions.
Helpers from `snippets/README.md` in scope; `tl` / `T0` as defined there.
Budget reminder: these are showpieces — max 1–2 per piece.

Contents: Editorial hero stagger · 3D coverflow spread · Card-stack shuffle

## Editorial hero stagger — chapter cards / openers

Three layers, exact review parameters: line-mask headline (`expo.out`,
stagger `base` 80ms) + floating cards (`lively`, y 24px, then finite
easeInOut float) + oversized background word (~5% white, slow linear drift).

```html
<div class="editorial-hero">
  <div class="bigword">BOHOL</div>
  <div class="headline">
    <div class="mask"><div class="line kicker">EPISODE 02 — TRAVEL DIARY</div></div>
    <div class="mask"><div class="line h1">山谷里，</div></div>
    <div class="mask"><div class="line h1">一餐<em>慢</em>下来。</div></div>
  </div>
  <div class="float-card fc-a"></div>
  <div class="float-card fc-b"></div>
</div>
<style>
  .editorial-hero { position:absolute; inset:0; }
  .bigword { position:absolute; right:-4%; bottom:-6%; font-size:110px;
    font-weight:900; color:rgba(255,255,255,.045); letter-spacing:-4px; white-space:nowrap; }
  .headline { position:absolute; left:8%; top:20%; }
  .mask { overflow:hidden; }
  .line { transform:translateY(110%); }
  .kicker { color:#ffd76a; font-size:12px; letter-spacing:4px; }
  .h1 { color:#fff; font-size:44px; font-weight:900; line-height:1.05; }
  .h1 em { color:#d94f2b; font-style:italic; }
  .float-card { position:absolute; opacity:0; box-shadow:0 16px 40px rgba(0,0,0,.5); }
  .fc-a { right:12%; top:16%; width:120px; height:76px; border-radius:10px;
    background:linear-gradient(135deg,#2a2a33,#3c3c48); border:1px solid rgba(255,215,106,.35); }
  .fc-b { right:26%; top:52%; width:88px; height:88px; border-radius:50%;
    background:radial-gradient(circle at 35% 30%,#d94f2b,#7a2413); }
</style>
```

```js
// layer 1 — background word drift (linear, whole scene)
tl.fromTo('.bigword', { x: 0 }, { x: -30, duration: 6, ease: 'none' }, T0);
// layer 2 — headline line masks
gsap.utils.toArray('.editorial-hero .line').forEach((el, i) => {
  tl.fromTo(el, { yPercent: 110 }, { yPercent: 0, duration: 0.75, ease: 'expo.out' },
    T0 + i * 0.08);
});
// layer 3 — floating cards: lively entrance, then finite float loop
gsap.utils.toArray('.float-card').forEach((el, i) => {
  tl.to(el, {
    keyframes: sKF('lively', p => ({
      y: (1 - p) * 24, scale: 0.9 + 0.1 * p, opacity: Math.min(1, p * 2.2)
    })), duration: 0.85, ease: 'none'
  }, T0 + 0.4 + i * 0.08);
  const loopDur = 2.6 + i * 0.4;
  tl.to(el, { y: i ? 8 : -8, duration: loopDur / 2, ease: 'sine.inOut',
    repeat: Math.ceil(4 / loopDur) * 2, yoyo: true }, T0 + 1.3);
});
```

## 3D coverflow spread — multi-asset preview, album beats

Perspective 900px; per-step translateX 92px / rotateY 21° / z -90px /
scale -0.06; `lively` spring; stagger `base` from center.

```html
<div class="coverflow"><!-- odd count, middle card is o=0 -->
  <div class="cf" data-o="-2"></div><div class="cf" data-o="-1"></div>
  <div class="cf" data-o="0"></div><div class="cf" data-o="1"></div>
  <div class="cf" data-o="2"></div>
</div>
<style>
  .coverflow { position:absolute; inset:0; display:flex; align-items:center;
    justify-content:center; perspective:900px; }
  .cf { position:absolute; width:120px; height:160px; border-radius:12px;
    opacity:0; border:1px solid rgba(255,255,255,.12);
    box-shadow:0 20px 50px rgba(0,0,0,.55); }
</style>
```

```js
gsap.utils.toArray('.cf').forEach(el => {
  const o = +el.dataset.o, ao = Math.abs(o);
  tl.to(el, {
    keyframes: sKF('lively', p => ({
      x: o * 92 * p, z: -ao * 90 * p, rotationY: -o * 21 * p,
      scale: 1 - ao * 0.06 * p, opacity: Math.min(1, p * 2 + 0.1)
    })), duration: 0.9, ease: 'none'
  }, T0 + ao * 0.08);
});
```

## Card-stack shuffle — photo/quote rotation

Top card flicks out (`expo.in` 0.4s, +rotate 14°), lower cards promote via
`ui` spring (y 12px / scale 0.06 per level), ejected card re-enters at the
back. Rounds are laid out on the timeline, not looped at runtime.

```html
<div class="stack">
  <div class="sc" data-lv="0"></div><div class="sc" data-lv="1"></div><div class="sc" data-lv="2"></div>
</div>
<style>
  .stack { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; }
  .sc { position:absolute; width:180px; height:120px; border-radius:14px;
    box-shadow:0 18px 44px rgba(0,0,0,.5); }
</style>
```

```js
const pose = lv => ({ y: lv * 12, scale: 1 - lv * 0.06, zIndex: 3 - lv });
let order = gsap.utils.toArray('.sc');
order.forEach(el => gsap.set(el, { ...pose(+el.dataset.lv), rotation: 0 }));
const ROUND = 1.5;
for (let r = 0; r < 3; r++) {
  const t = T0 + r * ROUND, top = order[0];
  tl.to(top, { x: 180, y: -30, rotation: 14, opacity: 0,
    duration: 0.4, ease: 'expo.in' }, t);
  order.slice(1).forEach((el, i) => {                    // promote lv i+1 → i
    tl.to(el, { keyframes: sKF('ui', p => {
      const lv = (i + 1) + (i - (i + 1)) * p;
      return { y: 12 * lv, scale: 1 - 0.06 * lv };
    }), duration: 0.6, ease: 'none' }, t + 0.1);
    tl.set(el, { zIndex: 3 - i }, t + 0.1);
  });
  tl.set(top, { zIndex: 1, x: -160, y: 24, scale: 0.88, rotation: -10 }, t + 0.45);
  tl.to(top, { keyframes: sKF('ui', p => ({
    x: -160 * (1 - p), y: 24 - 12 * p, scale: 0.88 + 0.06 * p,
    rotation: -10 * (1 - p), opacity: Math.min(1, p * 2)
  })), duration: 0.65, ease: 'none' }, t + 0.5);
  order = [...order.slice(1), top];
}
```
