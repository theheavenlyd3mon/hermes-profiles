---
name: threejs-postprocessing
description: "Configure and tune post-processing pipelines for Three.js r184+ — pmndrs/postprocessing library setup, effect chains (Bloom, SSAO, DOF, SSR), performance optimization, and integration with EffectComposer."
version: 1.1.0
author: Senna
tags: [threejs, post-processing, webgl, effects, bloom, ssao]
---

# Three.js Post-Processing

## Overview

Post-processing applies screen-space effects after the scene is rendered. Two paths:

1. **Three.js built-in** (`EffectComposer` + `UnrealBloomPass` + `OutputPass`) — no extra deps, fewer effects
2. **pmndrs/postprocessing** (2.8k⭐) — more effects, single-triangle GPU rendering, better performance

## High-Quality Rendering Ecosystem

The local `~/Threejs/` directory contains curated repos for high-quality rendering. See `references/threejs-ecosystem.md` for:

- **glTF-Transform** — Model optimization (60-90% smaller files, fastest load times)
- **three-particles** — GPU particles (50K-350K at 60fps, WebGPU compute, collision)
- **three-volumetric-pass** — Screen-space volumetric fog/clouds
- **fake-glow-material** — Per-object glow WITHOUT post-processing
- **three-effects** — Photoshop-style layer effects (stroke, shadow, glow, blur)

### Rendering Stack Order

For the Star Wars x Tron aesthetic, combine in this order:

1. **Asset optimization** → glTF-Transform
2. **Particles** → three-particles (engine exhaust, debris)
3. **Atmosphere** → three-volumetric-pass (planetary depth)
4. **Neon glow** → FakeGlowMaterial or three-effects.stroke (per-object)
5. **Post-processing** → pmndrs/postprocessing (bloom, SSR, SSAO)
6. **Camera** → three-story-controls + GSAP (cinematics)

## When to Use Which

| Situation | Use |
|-----------|-----|
| Simple bloom + tone mapping | Three.js built-in (no extra dep) |
| Bloom + SSAO + DOF + god rays | pmndrs/postprocessing |
| Target: Radeon Pro 555X / low-mid GPU | pmndrs (single-triangle = faster) |
| Quick prototype | Three.js built-in |
| Production cinematic | pmndrs |

## Installation

```bash
npm install postprocessing
```

### Import Paths (Three.js r184+)

Three.js r184 uses `./addons/*` as an export alias for `./examples/jsm/*`:

```js
// Three.js built-in
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';

// pmndrs/postprocessing
import { BloomPass, SSAOPass, DepthOfFieldPass, EffectPass } from 'postprocessing';
```

**Pitfall:** `three/addons/...` resolves via package.json exports but does NOT exist as a physical directory. Always use `three/examples/jsm/...` for explicit imports, or rely on Vite/Rollup export resolution.

## React Three Fiber (R3F) Integration

If you're using React Three Fiber (`@react-three/fiber`), use `@react-three/postprocessing`
(the R3F wrapper) instead of the raw pmndrs lib. Install BOTH:

```bash
pnpm add @react-three/postprocessing postprocessing
```

The R3F wrapper uses JSX components — no manual EffectComposer creation:

```tsx
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'

// Inside your R3F scene component, AFTER all scene objects:
<EffectComposer>
  <Bloom
    intensity={0.6}
    luminanceThreshold={0.15}
    luminanceSmoothing={0.08}
    mipmapBlur        // smoother glow — important prop, not obvious from docs
  />
  <Vignette offset={0.3} darkness={0.6} />
</EffectComposer>
```

**Key differences from raw pmndrs:**
- No `RenderPass` — the wrapper handles it
- No `EffectPass` — each effect is a separate JSX component
- No `OutputPass` — the wrapper handles color space correction
- Props use camelCase (`luminanceThreshold`) not constructor options
- `mipmapBlur` on Bloom gives smoother glow spread (equivalent to higher kernelSize)

**Canvas setup for post-processing in R3F:**
```tsx
<Canvas gl={{ antialias: true, toneMapping: 3, toneMappingExposure: 1.0 }}>
```

For the full R3F game setup including post-processing, see
`game-dev-with-hermes` skill → "Post-Processing Setup" section and
`references/magitech-rendering-recipe.md`.

## Pattern: Three.js Built-in (Bloom + Output)

```js
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));

const bloom = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  0.6,  // strength — 0.1 subtle, 1.5 intense
  0.4,  // radius — spread of glow (0.3 tight, 1.2 wide)
  0.1   // threshold — luminance; 0.05 everything glows, 0.5 only bright
);
composer.addPass(bloom);

// CRITICAL in r152+: OutputPass must be LAST
composer.addPass(new OutputPass());

// In animation loop — replaces renderer.render()
composer.render();
```

## Pattern: pmndrs/postprocessing

```js
import { BloomPass, SSAOPass, DepthOfFieldPass, EffectPass, RenderPass } from 'postprocessing';
import { SMAAImageLoader } from 'postprocessing';

const renderPass = new RenderPass(scene, camera);
const bloomPass = new BloomPass({
  intensity: 0.6,
  width: 500,      // internal resolution
  height: 500,
  kernelSize: 5,   // larger = wider glow
  luminanceThreshold: 0.2,
  luminanceSmoothing: 0.08,
});

const effectPass = new EffectPass(camera, bloomPass);
// Chain multiple effects in one EffectPass for performance
```

## Bloom Tuning Guide

| Effect | Parameter | Range | Cinematic Use |
|--------|-----------|-------|---------------|
| Subtle glow | strength | 0.2–0.4 | Space scenes, atmosphere |
| Neon pop | strength | 0.6–0.8 | City lights, Tron aesthetic |
| Intense bloom | strength | 1.0–1.5 | Engine glows, explosions |
| Wide spread | radius | 0.6–1.0 | Soft atmospheric glow |
| Tight glow | radius | 0.2–0.4 | Neon signs, precise highlights |
| Selective | threshold | 0.3–0.5 | Only bloom very bright objects |

## Performance Optimization

### Half-Resolution Bloom
```js
// Built-in: create composer at half resolution
const composer = new EffectComposer(renderer);
composer.setSize(Math.floor(window.innerWidth / 2), Math.floor(window.innerHeight / 2));

// pmndrs: pass resolution to BloomPass
const bloomPass = new BloomPass({ width: 960, height: 540 });
```

### Pixel Ratio Capping
```js
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
// On Retina displays (pixel ratio ~2), this halves render resolution vs 3x
```

### Resize Handler (must update ALL)
```js
window.addEventListener('resize', () => {
  const w = window.innerWidth;
  const h = window.innerHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  composer.setSize(w, h);
});
```

## Performance Budget (Radeon Pro 555X target)

| Effect | Cost | Limit |
|--------|------|-------|
| Bloom (half-res) | ~0.5ms | Always use — biggest quality-per-millisecond gain |
| SSAO | ~0.8ms | Use intensity 0.3 max; skip on space-only scenes |
| DOF | ~1.0ms | Skip unless specific close-up needs focus blur |
| SSR | ~1.5ms | Only on reflective surfaces; usually skip on this GPU |
| Volumetric fog (half-res) | ~2-3ms | Use halfRes=true, numSteps=12 max |

**When combo to use:**
- **Fast (dark scenes, particles only):** Bloom only (~0.5ms)
- **Balanced (city/neon scenes):** Bloom + SSAO (~1.5ms)
- **Cinematic (close-ups):** Bloom + SSAO + DOF (~2.5ms, expect 30fps)

Max 3 passes total including OutputPass. Beyond that, half-resolution trade-offs become visible.

## Pitfalls

1. **OutputPass is NOT optional** in Three.js r152+. Missing it causes washed-out colors and broken bloom.
2. **EffectComposer takes over renderer.setSize()** — always call `composer.setSize()` on resize, not just `renderer.setSize()`.
3. **pmndrs/postprocessing and built-in EffectComposer are incompatible** — don't mix them in the same pipeline. Pick one.
4. **Bloom + dark scenes** — bloom on near-black backgrounds creates a grey haze. Set threshold appropriately.
5. **Adding ~1-2ms per pass** — on Radeon Pro 555X, keep it to 2-3 passes max.
6. **HalfFloatType required** for pmndrs — `new EffectComposer(renderer, { frameBufferType: THREE.HalfFloatType })`. Without it, precision drops and banding appears.
7. **Glow decision guide** — see wiki pages for per-object glow (FakeGlowMaterial) vs scene-wide bloom (this skill) vs Photoshop-style layer effects (three-effects) at [[threejs-glow-and-effects]].
8. **Bloom kills subtle transparent effects** — when bloom threshold is ≥0.1, additive-blended overlay effects (ripples, lens flares, gravitational wave rings, subtle glows) can become completely invisible. The bloom pass either suppresses them as below-threshold or washes them into the glow of brighter objects. Fix: lower threshold to 0.05 for scenes with many subtle glow layers, AND set `depthTest: false` + `renderOrder: 999` on overlay materials so they render on top of bloom-processed geometry. Without `depthTest: false`, the depth buffer from nearer transparent objects (accretion disk, atmosphere) occludes the overlay even with additive blending.

## Verification

- [ ] Build succeeds (`npx vite build`)
- [ ] No console errors about post-processing imports
- [ ] Bloom glows on emissive/neon objects, not on dark background
- [ ] Frame rate stays above 40fps on target hardware
