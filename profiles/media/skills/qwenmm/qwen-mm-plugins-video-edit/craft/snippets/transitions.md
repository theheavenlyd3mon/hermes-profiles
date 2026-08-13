# Snippets — Transitions（转场可抄实现）

Copy-paste implementations for the approved menu in `craft/transitions.md`.
The menu kept shipping as bare hard cuts because its routes pointed at
registry blocks nobody installed — these are self-contained instead: two
overlapping top-level clips on different tracks + timeline tweens. All
seek-safe (`immediateRender: false`, transforms/clip-path only).

Setup shared by every recipe: A = outgoing clip, B = incoming clip. B sits
on the LOWER track and starts at `T_cut - OV` (overlap); A sits on the
HIGHER track and ends at `T_cut`. During the overlap A animates out over B.

```html
<video id="B" class="clip video-clip" data-start="11.4" data-duration="3.6"
       data-track-index="0" src="segments/seg_next.mp4" muted playsinline></video>
<video id="A" class="clip video-clip" data-start="8"  data-duration="4.0"
       data-track-index="2" src="segments/seg_prev.mp4" muted playsinline></video>
<!-- T_cut = 12, OV = 0.6 → A's last 0.6s plays above B's first 0.6s -->
```

Contents: Silky directional slide · Cross-dissolve + micro scale ·
Color-block wipe · Circle-mask reveal (→ footage-devices) · J/L cut note

## Silky directional slide — the workspace signature

One axis per piece. A exits toward −X while B enters from +X (B needs a
brief counter-transform so it lands at identity exactly at T_cut).

```js
const T_cut = 12, OV = 0.6;
tl.fromTo('#A', { xPercent: 0 }, { xPercent: -100, duration: OV,
  ease: 'expo.in',  immediateRender: false }, T_cut - OV);
tl.fromTo('#B', { xPercent: 18 }, { xPercent: 0,  duration: OV,
  ease: 'expo.out', immediateRender: false }, T_cut - OV);
```

B's 18% counter-slide is what makes it "silky" (both layers move); 100/18
asymmetry keeps B readable. Vertical pieces: swap to `yPercent`.

## Cross-dissolve + micro scale — emotional / nostalgic seams

Scenes ≥3s only (kills momentum on fast cuts). The micro scale pair is the
difference between "video editor default" and cinematic.

```js
const T_cut = 24, OV = 0.6;
tl.fromTo('#A', { opacity: 1, scale: 1 }, { opacity: 0, scale: 0.985,
  duration: OV, ease: 'power1.inOut', immediateRender: false }, T_cut - OV);
tl.fromTo('#B', { scale: 1.045 }, { scale: 1,
  duration: OV, ease: 'power1.out', immediateRender: false }, T_cut - OV);
```

## Color-block wipe — playful / cute / comedy

A palette-colored diagonal block sweeps across, covering the cut point at
mid-sweep. One extra div, no overlap needed on the clips themselves.

```html
<div id="wipe" class="clip" data-start="17.7" data-duration="0.7" data-track-index="4"
     style="position:absolute; inset:-10%; background:#ffd76a;
            transform: skewX(-12deg) translateX(-130%);"></div>
```

```js
// block crosses the frame in 0.44s; the clip hard-cut hides under it at 18
tl.fromTo('#wipe', { xPercent: -130 }, { xPercent: 130, duration: 0.44,
  ease: 'power3.inOut', immediateRender: false }, 17.78);
```

Two-color variant: second block, second palette color, 60ms later — reads
as a comic double-wipe. Register: cute/comedy only.

## Circle-mask reveal — object-anchored motivated seam

Code lives in `snippets/footage-devices.md` (it needs a perception pass for
the anchor coordinates). Use when a real object motivates the seam: pan
lid, doorway, ball, palm.

## J/L cut — when sources carry audio

No visuals: offset the audio `data-start` 0.3-1.0s against the picture cut
so sound leads (J) or trails (L). Silent-source pieces skip this one.

---

**Budget & grammar** (`craft/transitions.md` § Selection rules still rule):
hard cut stays the spine; ONE accent family per piece; accents land on
scene changes, not every cut. A transition nobody notices but everybody
feels is the goal — if the seam draws attention to itself twice in a row,
it's over budget.
