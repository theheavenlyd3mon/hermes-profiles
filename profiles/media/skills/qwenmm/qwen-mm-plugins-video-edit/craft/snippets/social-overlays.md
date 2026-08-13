# Snippets — Social-Platform Overlays

Recipes from `craft/motion-recipes.md` § Social-platform overlays.
**Register guard applies: casual/vlog/food/playful ONLY, and the taste
contract must say so.** Helpers from `snippets/README.md` in scope.
`[no-placeholder-assets]`: demo emoji/plain chips below are STRUCTURE ONLY —
production uses generated sticker assets / designed chips.

Contents: Live comment bubbles · Story progress segments · Hand-drawn arrow
poke · Comic speedlines burst · Polaroid toss-in

## Live comment bubbles — side commentary, self-banter

Bubbles pop in sequentially (`ui` spring, y 26px), older ones slide up to
yield; ≤3 alive at once. Obeys `[no-occlusion]` — anchor in planned
negative space.

```html
<div class="comments">
  <div class="cb"><span>🍜</span>这碗面我可以!</div>
  <div class="cb"><span>👀</span>蹲一个地址</div>
  <div class="cb"><span>🔥</span>老板加辣谢谢</div>
</div>
<style>
  .comments { position:absolute; left:5%; bottom:8%; display:flex;
    flex-direction:column-reverse; gap:8px; }
  .cb { background:rgba(20,20,26,.82); border:1px solid rgba(255,255,255,.14);
    color:#fff; font-size:13px; border-radius:999px; padding:8px 14px;
    width:max-content; opacity:0; }
  .cb span { margin-right:6px; }
</style>
```

```js
// column-reverse handles the yield-upward layout; entrance only needs the spring
gsap.utils.toArray('.cb').forEach((el, i) => {
  tl.to(el, { keyframes: sKF('ui', p => ({
    y: (1 - p) * 26, scale: 0.86 + 0.14 * p, opacity: Math.min(1, p * 2.2)
  })), duration: 0.6, ease: 'none' }, T0 + i * 0.65);
});
```

## Story progress segments — multi-part narrative navigation cue

Top segmented bar, each chapter fills linearly ~1.1s, author avatar chip
springs in. Active fill color `#ffd76a` on `rgba(255,255,255,.18)` track.

```html
<div class="story-bar">
  <div class="seg"><i></i></div><div class="seg"><i></i></div><div class="seg"><i></i></div>
</div>
<div class="story-who">
  <div class="ava"></div><span>@handle · 第2章</span>
</div>
<style>
  .story-bar { position:absolute; top:7%; left:4%; right:4%; display:flex; gap:6px; }
  .seg { flex:1; height:4px; border-radius:4px; background:rgba(255,255,255,.18); overflow:hidden; }
  .seg i { display:block; height:100%; width:100%; background:#ffd76a;
    transform:scaleX(0); transform-origin:left; }
  .story-who { position:absolute; top:13%; left:4%; display:flex;
    align-items:center; gap:8px; opacity:0; }
  .ava { width:30px; height:30px; border-radius:50%; border:2px solid #ffd76a;
    background:radial-gradient(circle at 35% 30%,#ff9a5f,#d94f2b); }
  .story-who span { color:#fff; font-size:12px; font-weight:600; }
</style>
```

```js
tl.to('.story-who', { keyframes: sKF('ui', p => ({
  opacity: Math.min(1, p * 2), y: (1 - p) * 10 })),
  duration: 0.5, ease: 'none' }, T0);
gsap.utils.toArray('.seg i').forEach((el, i) => {
  tl.to(el, { scaleX: 1, duration: 1.1, ease: 'none' }, T0 + i * 1.1);
});
```

## Hand-drawn arrow poke — strongest gaze-direction tool

SVG path draw-on 0.4s (`expo.out` dashoffset) + head 0.18s, then pokes
toward target ×3 at 0.7s. Pairs with a small label chip (`lively`).
Production arrow paths need hand-drawn irregularity (`[no-placeholder-assets]`).

```html
<svg class="arrow" viewBox="0 0 640 360">
  <g class="arr">
    <path class="shaft" d="M 470 90 C 420 100, 380 140, 360 190"/>
    <path class="head"  d="M 344 162 L 360 194 L 385 172"/>
  </g>
</svg>
<div class="arrow-label">看这里 👇</div>
<style>
  .arrow { position:absolute; inset:0; width:100%; height:100%; }
  .arrow path { fill:none; stroke:#ffd76a; stroke-width:6;
    stroke-linecap:round; stroke-linejoin:round; }
  .arrow-label { position:absolute; left:44%; top:62%; color:#fff; font-size:15px;
    font-weight:700; background:rgba(217,79,43,.9); border-radius:999px;
    padding:7px 16px; opacity:0; }
</style>
```

```js
// measure once at build time, bake the constants (getTotalLength is layout-safe
// here but the values must not change between preview and render)
document.querySelectorAll('.arrow path').forEach(p => {
  const L = p.getTotalLength();
  p.style.strokeDasharray = L; p.style.strokeDashoffset = L;
});
tl.to('.arrow .shaft', { strokeDashoffset: 0, duration: 0.4, ease: 'expo.out' }, T0);
tl.to('.arrow .head',  { strokeDashoffset: 0, duration: 0.18, ease: 'expo.out' }, T0 + 0.4);
tl.to('.arrow-label', { keyframes: sKF('lively', p => ({
  opacity: Math.min(1, p * 2.5), scale: 0.6 + 0.4 * p })),
  duration: 0.5, ease: 'none' }, T0 + 0.5);
tl.to('.arr', { x: -9, y: 12, duration: 0.35, ease: 'sine.inOut',
  repeat: 5, yoyo: true }, T0 + 0.6);            // ×3 pokes = 6 half-cycles
```

## Comic speedlines burst — dramatic emphasis, ≤1 per piece

Radial line flash (repeating-conic stripes + center mask) ≤0.9s with a
2-frame flicker rhythm; center word slams in `lively` with outline stroke.

```html
<div class="speed-lines"></div>
<div class="speed-word">哇!!</div>
<style>
  .speed-lines { position:absolute; inset:-20%; opacity:0;
    background:repeating-conic-gradient(from 0deg at 50% 50%,
      rgba(255,255,255,.9) 0deg 1.6deg, transparent 1.6deg 7deg);
    -webkit-mask-image:radial-gradient(circle at 50% 50%, transparent 26%, #000 48%);
    mask-image:radial-gradient(circle at 50% 50%, transparent 26%, #000 48%); }
  .speed-word { position:absolute; inset:0; display:flex; align-items:center;
    justify-content:center; font-size:46px; font-weight:900; color:#ffd76a;
    -webkit-text-stroke:2px #1f1f26; opacity:0; }
</style>
```

```js
tl.to('.speed-lines', { keyframes: [                 // flicker rhythm from review
  { opacity: 0 }, { opacity: 1 }, { opacity: 0.55 }, { opacity: 1 }, { opacity: 0 }
], duration: 0.9, ease: 'steps(1)' }, T0);
tl.to('.speed-word', { keyframes: sKF('lively', p => ({
  scale: 0.2 + 0.8 * p, rotation: -8 * (1 - p), opacity: Math.min(1, p * 3)
})), duration: 0.6, ease: 'none' }, T0 + 0.08);
```

## Polaroid toss-in — memory/recap moments

`ui` spring, rotate 18°→-3° with slight overshoot, drop from y -190px;
white frame + tape corner + handwritten date. Photo area holds a real
frame/clip in production.

```html
<div class="polaroid">
  <div class="photo"></div>
  <div class="tape"></div>
  <div class="cap">07.26 · 山谷</div>
</div>
<style>
  .polaroid { position:absolute; left:50%; top:50%; width:180px;
    padding:10px 10px 30px; background:#f5f2ea; border-radius:4px;
    box-shadow:0 18px 44px rgba(0,0,0,.5); opacity:0;
    transform:translate(-50%,-50%); }
  .photo { height:110px; border-radius:2px;
    background:linear-gradient(140deg,#3c6e8f,#1d3346); }
  .tape { position:absolute; top:-8px; left:50%; width:56px; height:18px;
    transform:translateX(-50%) rotate(-3deg);
    background:rgba(255,215,106,.75); border-radius:2px; }
  .cap { text-align:center; color:#4a453a; font-size:12px; margin-top:8px; font-weight:600; }
</style>
```

```js
tl.to('.polaroid', { keyframes: sKF('ui', p => ({
  y: (1 - p) * -190, rotation: 18 - 21 * p,           // 18° → -3° through the spring
  scale: 0.8 + 0.2 * p, opacity: Math.min(1, p * 2.5)
})), duration: 0.85, ease: 'none' }, T0);
```
