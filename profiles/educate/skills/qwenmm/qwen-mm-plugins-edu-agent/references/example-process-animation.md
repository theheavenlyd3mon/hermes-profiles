# Few-shot: Process-Animation Scenes (过程动画 / 生物·物理演示) — a proven, high-scoring example

This is a **worked, copy-me example** distilled from a mitosis (洋葱根尖有丝分裂) tutorial that scored
top marks on the animation/visual dimensions. Use it as a template whenever a scene must **show a
process unfold with real motion** — cell division, force decomposition, wave propagation, a titration
filling, orbits, anything where "things move / change / get pulled" is the point.

The two full reference scenes live next to this file:
- [`examples/mitosis-anaphase.scene.html`](examples/mitosis-anaphase.scene.html) — the star: sister
  chromatids split and are **pulled to the poles by spindle fibers that visibly shorten**, with a live
  "染色体数 16→32" count-up. (The inlined KaTeX CSS blob was replaced by a placeholder for readability —
  restore a real inlined `katex.min.css` per step-6 when you build.)
- [`examples/mitosis-chromosome-chart.scene.html`](examples/mitosis-chromosome-chart.scene.html) — a
  quantity-vs-phase **stepped line chart drawn segment-by-segment** with popping points/labels.

> Why these score well: motion is **purposeful and physically legible** (objects move where the biology
> says, connectors track them), it's **staged** (one idea reveals at a time), and it's **rich but
> controlled** (draw-on, translate, pulse, count-up — never a gimmicky spin). Copy the techniques below.

---

## The reusable techniques (each is model-copyable)

All animation lives in the scene's paused GSAP timeline (`window.__timelines["<id>"]`), times are seconds
**within the scene**. All moving/splitting SVG objects are `<g transform="translate(x,y)">` groups with
a unique `id`; you animate `attr:{transform:...}` on the group (never wrap a transform-animated group in
another transform — see `check_svg_transform_anim`). Connectors are `<line>` with an `id`; you animate
`attr:{x2,y2}`.

### T1 — Staged phase reveal (one idea at a time)
One scene = one phase/step. Reveal the panel, then stagger the feature bullets, so the viewer reads it in
order (this is why it feels "clear", not cluttered):
```js
tl.fromTo("#S .glass-panel", {y:50,autoAlpha:0}, {y:0,autoAlpha:1,duration:0.8,ease:"power3.out"}, 0.15);
tl.fromTo("#S .numchip", {scale:0.7,autoAlpha:0}, {scale:1,autoAlpha:1,duration:0.5,ease:"back.out(1.6)"}, 0.6);
// feature bullets slide in one-by-one:
["#S-f0","#S-f1","#S-f2","#S-f3"].forEach((id,i)=>{
  if(document.querySelector(id)) tl.fromTo(id,{x:30,autoAlpha:0},{x:0,autoAlpha:1,duration:0.5,ease:"power2.out"},1.4+i*0.55);
});
```

### T2 — Split-and-move (one object becomes two that travel to targets)
Pre-place BOTH result halves hidden **at the parent's position**; at the split moment hide the parent,
reveal the halves, then translate each half to its destination. (Mitosis: one chromosome → two chromatids
→ opposite poles.)
```html
<g id="c0" transform="translate(400,280)">…paired object…</g>
<g id="u0" transform="translate(400,280)">…half A…</g>   <!-- starts on top of parent -->
<g id="d0" transform="translate(400,280)">…half B…</g>
```
```js
tl.set("#u0",{autoAlpha:0}); tl.set("#d0",{autoAlpha:0});
tl.to("#c0-in",{scale:1.25,duration:0.28,ease:"sine.inOut",yoyo:true,repeat:1}, 3.0);   // "about to split" pulse
tl.to("#c0",{autoAlpha:0,duration:0.2}, 3.6);
tl.to("#u0",{autoAlpha:1,duration:0.2}, 3.6); tl.to("#d0",{autoAlpha:1,duration:0.2}, 3.6);
tl.to("#u0",{attr:{transform:"translate(400,130)"},duration:1.6,ease:"power2.inOut"}, 3.7);  // → top pole
tl.to("#d0",{attr:{transform:"translate(400,430)"},duration:1.6,ease:"power2.inOut"}, 3.7);  // → bottom pole
```

### T3 — Connector that TRACKS a moving object and SHORTENS (the pull effect) ⭐
The bug this fixes: a spindle fiber / rope / ray / link drawn as a **static** path while the object flies
off looks disconnected and dead. Instead draw the connector as an id'd `<line>` from the anchor (pole /
pivot / source) to the object, and animate its object-end `x2,y2` **with the SAME start/duration/ease as
the object's move**. As the object nears the anchor the line gets shorter → it reads as *actively pulling
/ contracting*. (Also use for: rope over a pulley, a force/velocity vector following a body, a light ray
to a moving image, a leader line to a moving label.)
```html
<line id="sf0u" x1="500" y1="70"  x2="400" y2="280" stroke="rgba(217,119,6,0.55)" stroke-width="3" stroke-linecap="round"/>
<line id="sf0d" x1="500" y1="490" x2="400" y2="280" stroke="rgba(217,119,6,0.55)" stroke-width="3" stroke-linecap="round"/>
```
```js
// object u0 moves to (400,130); its fiber's far end tracks it → fiber shortens in sync:
tl.to("#sf0u", {attr:{x2:400,y2:130},duration:1.6,ease:"power2.inOut"}, 3.7);
tl.to("#sf0d", {attr:{x2:400,y2:430},duration:1.6,ease:"power2.inOut"}, 3.7);
```
Key rule: **connector move = object move (same time window, same ease)**, and the connector's fixed end
stays on the true anchor (pole/pivot), moving end = the object's centre.

### T4 — Live count-up synced to the motion
Animate a plain counter object and write it into the DOM each frame, timed to the event it narrates
(here the "数目暂时加倍" during anaphase):
```js
var cnt={v:16};
tl.to(cnt,{v:32,duration:1.4,ease:"power1.inOut",onUpdate:function(){
  var e=document.getElementById("mt-anaphase-cnt"); if(e) e.textContent=Math.round(cnt.v);
}}, 3.8);
```

### T5 — Stepped "quantity over phases" chart (draw-on)
Model each segment as an id'd `<line>` (horizontal runs + the vertical step where the value jumps), set
`stroke-dasharray=stroke-dashoffset=length`, then reveal them **in phase order** with dashoffset→0; pop a
point + value label at each. Straight segments are correct here (it's a step function — see the
`check_scene_fit`/smooth-curve note: piecewise-linear graphs stay straight). See the chart example file.
```js
// per segment: prime dashoffset, then reveal in order
(function(){var el=document.getElementById("seg3");var L=el.getTotalLength();el.setAttribute("stroke-dasharray",L);el.setAttribute("stroke-dashoffset",L);})();
tl.to("#seg3",{attr:{"stroke-dashoffset":0},duration:0.8,ease:"power1.inOut"}, 5.4);   // the doubling step
tl.fromTo("#vl3",{autoAlpha:0,scale:0.3,svgOrigin:"840 116"},{autoAlpha:1,scale:1,duration:0.4,ease:"back.out(1.8)"}, 5.6);
```

### T6 — Ambient life without gimmicks
Gentle, looped micro-motion keeps the frame alive: aurora orbs drift, a panel breathes, a diagram floats
±16px. **Do NOT** put a continuous 360° spin on a content object (a spinning chromosome/atom/logo reads
as cheap and distracts) — that exact anti-pattern was removed from this example. Prefer draw-on, translate,
scale-pulse, and slow yoyo drifts.
```js
tl.fromTo("#S .a1",{x:0,y:0},{x:-42,y:28,duration:4,ease:"sine.inOut",yoyo:true,repeat:R(4)},0);   // R = repeats to fill scene
```

---

## How to adapt this to a new topic
1. Keep the **one-concept-per-scene** structure: title → overview/flow → one scene per stage → a
   summary/chart. Each stage scene = animated diagram (left) + staged feature bullets (right) + a status
   chip (T1).
2. Map your process to T2/T3: what splits or moves (T2), and what connector should track & pull it (T3).
3. If a quantity changes across stages, add a count-up (T4) and/or the stepped chart (T5).
4. Obey all standard gates (root `id`+`data-width/height`, `<template>` wrapper, `.cm`/getElementById for
   KaTeX, one screen高度, smooth curves for continuous graphs, arrowheads point +x, no 360° spin) — run
   `python3 "$EDU_SKILL_ROOT/scripts/precheck.py" dist` until ALL CHECKS PASSED.
