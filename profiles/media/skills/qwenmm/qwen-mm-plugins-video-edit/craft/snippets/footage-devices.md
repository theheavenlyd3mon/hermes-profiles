# Snippets — Footage Devices（作用在素材上的设备）

The other snippet files dress TEXT and UI. This file is the missing half:
devices that act on the FOOTAGE itself — the weakness reviews keep flagging
("只有标题和角标,像给录像加了标题"). Every recipe here is
deterministic under HyperFrames rules: playback is framework-owned, so
freezes use pre-extracted stills, speed changes are pre-baked media, and
reframes transform the clip element itself (videos must stay top-level
clips — never nest a `<video>` inside another element, known init pitfall).

Helpers (`sKF`, `SPRING`) from `snippets/README.md` in scope; `tl`/`T0` as
defined there.

Contents: Freeze-punch still · Speed-ramp bake · Crop-reframe · Circle-mask
reveal · Tracking label · Split-screen sync · Ring accent draw-on

## Freeze-punch still — emphasis on a peak expression

The device contracts keep declaring and never shipping. Two parts from the
SAME segment: the moving clip ends at the peak frame T; a pre-extracted
still takes over with a snap punch-in + ring accent.

```bash
# extract the freeze frame (peak found via perception pass)
ffmpeg -ss 2.00 -i segments/seg_09.mp4 -frames:v 1 assets/freeze_09.png
```

```html
<video id="mv9" class="clip video-clip" data-start="12" data-duration="2.0"
       src="segments/seg_09.mp4" muted playsinline></video>
<div id="fz9" class="clip freeze-wrap" data-start="14" data-duration="1.1" data-track-index="0">
  <img src="assets/freeze_09.png">
  <svg class="ring" viewBox="0 0 200 200">
    <circle cx="100" cy="100" r="88" pathLength="100" fill="none"
            stroke="#ffd76a" stroke-width="5" stroke-linecap="round"
            stroke-dasharray="100" stroke-dashoffset="100"/>
  </svg>
</div>
<style>
  .freeze-wrap { position:absolute; inset:0; }
  .freeze-wrap img { width:100%; height:100%; object-fit:cover; }
  .freeze-wrap .ring { position:absolute; left:58%; top:20%; width:26%; height:auto; }
</style>
```

```js
// snap punch 1→1.12, ring draws on 80ms later; place the ring OFF faces
tl.fromTo('#fz9', { scale: 1 }, { keyframes: sKF('snap', p => ({ scale: 1 + 0.12 * p })),
  duration: 0.5, ease: 'none' }, 14);
tl.fromTo('#fz9 .ring circle', { strokeDashoffset: 100 },
  { strokeDashoffset: 0, duration: 0.45, ease: 'power2.out', immediateRender: false }, 14.08);
```

Budget: 2-3 per piece, ONLY on real peaks (T1 restraint). Position the ring
with real frame coordinates, not guesses.

**The timed clip is the WRAPPER DIV — never put `class="clip"` on the
`<svg>` itself.** Framework clip visibility manages div clips; an `<svg>`
carrying the timing attributes stays painted after its window and bleeds
into later scenes (field leak: a punch ellipse showed up 3s
later over the next scene and the ending card). Keep the svg as a child of
the div clip, as above.

## Speed-ramp bake — energy change as media, not runtime

playbackRate is not seek-safe; bake the ramp with ffmpeg, then hard-cut
fast→normal (or normal→slow) exactly on the beat.

```bash
# 2.2x rush-in (silent source; add `-af "atempo=2.2"` when audio exists)
ffmpeg -i segments/seg_10.mp4 -vf "setpts=PTS/2.2" -r 25 -an \
  -c:v libx264 -g 25 -movflags +faststart segments/seg_10_fast.mp4
# 0.5x savor on the peak (25fps source keeps enough motion at half speed)
ffmpeg -i segments/seg_11.mp4 -vf "setpts=PTS*2" -r 25 -an \
  -c:v libx264 -g 25 -movflags +faststart segments/seg_11_slow.mp4
```

Composition: `seg_10_fast` (1.1s) hard-cuts into `seg_11_slow` at the lift
moment — the tempo drop IS the emphasis. One ramp pair per piece reads
intentional; three reads like a template.

## Crop-reframe — shot variety from monotonous wide footage

Richness floor #6. Transform the clip element ITSELF (no wrapper): scale
with `transform-origin` at the subject turns one wide selfie into an MCU,
a face CU, or a hands insert. Static per shot, or keyframed as a push.

```html
<!-- same source segment used twice at different framings = two shots -->
<video class="clip video-clip" data-start="20" data-duration="2.2"
       src="segments/seg_07.mp4" muted playsinline
       style="transform: scale(1.9); transform-origin: 38% 30%;"></video> <!-- face MCU -->
<video class="clip video-clip" data-start="22.2" data-duration="1.6"
       src="segments/seg_07.mp4" muted playsinline
       style="transform: scale(2.6); transform-origin: 55% 72%;"></video> <!-- hands/pan CU -->
```

```js
// keyframed push variant (camera-rig grammar, budget applies)
tl.fromTo('#cook-wide', { scale: 1.0 }, { scale: 1.35, duration: 2.4, ease: 'power2.inOut',
  transformOrigin: '52% 40%', immediateRender: false }, 24);
```

Origin coordinates come from a perception pass on the actual frame. Scale
≤2.8 on 1080p (past that it smears). Never let one framing run >2
consecutive shots — recut the same segment at a second origin instead.

## Circle-mask reveal — motivated transition at an object/action point

Richness floor #2. The outgoing shot collapses into a circle anchored on
the motivating object (pan lid, doorway, ball), revealing the next scene.
Outgoing clip must OVERLAP the incoming by the transition length, on a
HIGHER track.

```js
// A (track 2) over B (track 0); circle center = object position in A's last frame
tl.fromTo('#sceneA-out', { clipPath: 'circle(150% at 32% 42%)' },
  { clipPath: 'circle(0% at 32% 42%)', duration: 0.55, ease: 'expo.inOut',
    immediateRender: false }, T_cut);
```

Direction variant: matching action vectors (a turn, a run, a hand-off) use
the silky directional slide (`craft/transitions.md`) with the slide axis =
the subject's motion axis — that alignment is what makes it "motivated".

## Tracking label — text that participates instead of floating

Richness floor #4. Sample the subject's position at 0.4-0.6s intervals from
real frames, then tween the label through the path. 3-6 keyframes is plenty
— smooth easing between samples reads as tracking.

```html
<div id="run-tag" class="clip track-label" data-start="30" data-duration="2.4"
     data-track-index="3">全速前进!</div>
<style>
  .track-label { position:absolute; left:62%; top:58%; padding:10px 22px;
    background:#ffd76a; color:#2b2018; font-size:52px; font-weight:800;
    border-radius:14px; transform:translate(-50%,-100%); }
</style>
```

```js
const PATH = [[62,58],[54,50],[45,47],[38,42]];   // % coords from frame samples
tl.fromTo('#run-tag', { scale: 0 }, { keyframes: sKF('lively', p => ({ scale: p })),
  duration: 0.45, ease: 'none' }, 30);
PATH.slice(1).forEach((pt, i) =>
  tl.to('#run-tag', { left: pt[0] + '%', top: pt[1] + '%',
    duration: 0.55, ease: 'sine.inOut' }, 30 + 0.45 + i * 0.55));
```

One tracked element per piece is the budget; it must point at/follow a real
subject, and never cover a face (`[no-occlusion]`).

## Split-screen sync — parallel actions share the frame

Two top-level clips side by side (no nesting), divider bar snaps in. Made
for mirrored actions: both brushing teeth, parent cooking / kid waiting.

```html
<video id="sp-l" class="clip" data-start="16" data-duration="3" data-track-index="0"
       src="segments/seg_02a.mp4" muted playsinline
       style="position:absolute; left:0; top:0; width:50%; height:100%; object-fit:cover;"></video>
<video id="sp-r" class="clip" data-start="16" data-duration="3" data-track-index="1"
       src="segments/seg_02b.mp4" muted playsinline
       style="position:absolute; left:50%; top:0; width:50%; height:100%; object-fit:cover;"></video>
<div id="sp-bar" class="clip" data-start="16" data-duration="3" data-track-index="2"
     style="position:absolute; left:calc(50% - 4px); top:0; width:8px; height:100%; background:#fff;"></div>
```

```js
// panels slide in from both edges, bar lands with a snap
tl.fromTo('#sp-l', { xPercent: -100 }, { xPercent: 0, duration: 0.5, ease: 'expo.out', immediateRender: false }, 16);
tl.fromTo('#sp-r', { xPercent: 100 }, { xPercent: 0, duration: 0.5, ease: 'expo.out', immediateRender: false }, 16);
tl.fromTo('#sp-bar', { scaleY: 0 }, { scaleY: 1, duration: 0.35, ease: 'power3.out', immediateRender: false }, 16.3);
```

## Ring accent draw-on — hand-drawn emphasis without freezing

The lightweight sibling of freeze-punch: SVG circle/underline draws on over
LIVE footage at a peak micro-moment. Same draw mechanics as the freeze ring
(pathLength=100, dashoffset 100→0, `power2.out`, 0.4-0.5s); add
`stroke-dasharray="100"` wobble via a slightly rotated ellipse for the
hand-drawn read. Position from real frames; auto-exit after ≤1.2s with a
0.2s fade. Pairs with the arrow poke (`social-overlays.md`). When the brief
wants richer hand-drawn texture than SVG strokes (蒸气/香气线, 涂鸦贴纸,
scribble 字), generate a sticker set via `qwen_image` — named play in
`mcps/README.md`.

---

**Perception first, then coordinates.** Every device above needs real frame
coordinates (faces, hands, objects, motion vectors). Grab frames, look,
measure — a ring around empty air or a track path through a face is worse
than no device at all.
