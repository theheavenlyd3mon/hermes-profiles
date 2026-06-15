---
name: threejs-shader-patterns
description: "Reusable GLSL shader patterns for Three.js — fresnel atmosphere, per-instance animation, noise, grid/line shaders, and hex grid. Each pattern includes the full ShaderMaterial setup code."
version: 1.0.0
author: Senna
tags: [threejs, shaders, webgl, glsl, shadermaterial]
---

# Three.js Shader Patterns

Reusable GLSL shader patterns for Three.js `ShaderMaterial`. Each pattern includes vertex + fragment shader code and the JS setup.

## Common Setup

```js
import * as THREE from 'three';

const material = new THREE.ShaderMaterial({
  uniforms: {
    time: { value: 0 },
    color1: { value: new THREE.Color(0x00ccff) },
    // ...pattern-specific uniforms
  },
  vertexShader: `...`,
  fragmentShader: `...`,
  transparent: true,
  blending: THREE.AdditiveBlending,  // for glow effects
  depthWrite: false,
  side: THREE.FrontSide,
});

// Update time in animation loop
material.uniforms.time.value += dt;
```

## Pattern 1: Fresnel Rim Glow

Creates a bright glow at grazing angles (edges of a sphere/object). Used for planet atmospheres.

### Vertex Shader
```glsl
varying vec3 vNormal;
varying vec3 vPositionW;

void main() {
  vNormal = normalize(normalMatrix * normal);
  vec4 worldPos = modelMatrix * vec4(position, 1.0);
  vPositionW = worldPos.xyz;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
```

### Fragment Shader
```glsl
uniform vec3 glowColor;
uniform float intensity;
uniform float power;

varying vec3 vNormal;
varying vec3 vPositionW;

void main() {
  vec3 viewDir = normalize(cameraPosition - vPositionW);
  float rim = 1.0 - max(0.0, dot(viewDir, vNormal));
  float fresnel = pow(rim, power);

  vec3 color = glowColor * fresnel * intensity;
  float alpha = fresnel * 0.8;

  gl_FragColor = vec4(color, alpha);
}
```

### JS Setup
```js
const atmosMat = new THREE.ShaderMaterial({
  uniforms: {
    glowColor: { value: new THREE.Color(0x44aaff) },
    intensity: { value: 1.5 },
    power: { value: 2.5 },
  },
  vertexShader: fresnelVertexShader,
  fragmentShader: fresnelFragmentShader,
  transparent: true,
  side: THREE.FrontSide,
  blending: THREE.AdditiveBlending,
  depthWrite: false,
});
```

**Tuning:** `power` controls fade sharpness (1.5 = soft, 4.0 = sharp rim). `intensity` controls brightness.

## Pattern 2: Per-Instance Twinkle

Animate each point/particle independently using a phase attribute. Used for starfields.

### Vertex Shader
```glsl
attribute float size;
attribute float phase;
attribute vec3 customColor;

uniform float time;
uniform float twinkleSpeed;
uniform float twinkleAmount;

varying vec3 vColor;

void main() {
  vColor = customColor;
  vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);

  float twinkle = 1.0 - twinkleAmount * (0.5 + 0.5 * sin(time * twinkleSpeed + phase * 6.283));
  gl_PointSize = size * (300.0 / -mvPosition.z) * twinkle;
  gl_Position = projectionMatrix * mvPosition;
}
```

### Fragment Shader
```glsl
varying vec3 vColor;

void main() {
  float d = distance(gl_PointCoord, vec2(0.5));
  if (d > 0.5) discard;
  float alpha = 1.0 - smoothstep(0.0, 0.5, d);
  vec3 color = vColor * (1.0 + 0.5 * (1.0 - d * 2.0));
  gl_FragColor = vec4(color, alpha);
}
```

### JS Setup
```js
const geometry = new THREE.BufferGeometry();
// positions, colors, sizes, phases — set as BufferAttributes
geometry.setAttribute('customColor', new THREE.BufferAttribute(colors, 3));
geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
geometry.setAttribute('phase', new THREE.BufferAttribute(phases, 1));

const material = new THREE.ShaderMaterial({
  uniforms: {
    time: { value: 0 },
    twinkleSpeed: { value: 1.5 },
    twinkleAmount: { value: 0.4 },
  },
  vertexShader: twinkleVertexShader,
  fragmentShader: twinkleFragmentShader,
  transparent: true,
  blending: THREE.AdditiveBlending,
  depthWrite: false,
});

// Update in animation loop
material.uniforms.time.value += dt;
```

## Pattern 3: Grid/Line Shader

Creates glowing grid lines on a surface. Used for Tron-style city grids, ship hull panels.

### Fragment Shader
```glsl
uniform vec3 gridColor;
uniform float gridSize;
uniform float lineWidth;
uniform float glowIntensity;

varying vec2 vUv;

void main() {
  // Grid lines at UV boundaries
  vec2 grid = abs(fract(vUv * gridSize - 0.5) - 0.5);
  float line = min(grid.x, grid.y);
  float glow = 1.0 - smoothstep(0.0, lineWidth, line);

  vec3 color = gridColor * glow * glowIntensity;
  float alpha = glow * 0.6;

  gl_FragColor = vec4(color, alpha);
}
```

## Pattern 4: Noise/Cloud Shader

Simplex noise approximation for organic effects (clouds, terrain, atmospheric turbulence).

### Fragment Shader (simplified value noise)
```glsl
uniform vec3 cloudColor;
uniform float time;
uniform float density;

varying vec3 vPosition;

// Simple pseudo-random noise
float hash(vec3 p) {
  p = fract(p * 0.3183099 + 0.1);
  p *= 17.0;
  return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

float noise(vec3 p) {
  vec3 i = floor(p);
  vec3 f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(mix(hash(i), hash(i + vec3(1,0,0)), f.x),
                 mix(hash(i + vec3(0,1,0)), hash(i + vec3(1,1,0)), f.x), f.y),
             mix(mix(hash(i + vec3(0,0,1)), hash(i + vec3(1,0,1)), f.x),
                 mix(hash(i + vec3(0,1,1)), hash(i + vec3(1,1,1)), f.x), f.y), f.z);
}

void main() {
  float n = noise(vPosition * density + time * 0.05);
  float alpha = smoothstep(0.3, 0.7, n) * 0.4;
  gl_FragColor = vec4(cloudColor, alpha);
}
```

## Pattern 6: Ship Hull Panel-Seam Grid

Tron-style glowing grid lines on a ship hull. Layered on top of a `MeshStandardMaterial` so the base stays metallic/PBR while the grid glows.

### Vertex Shader
Same as Pattern 1 — passes `vNormal`, `vPositionW`, and `vUv`.

### Fragment Shader
```glsl
uniform vec3 gridColor;
uniform float gridIntensity;
uniform float gridLines;   // number of lines across UV space
uniform float gridWidth;   // line thickness
uniform float pulseSpeed;
uniform float pulseAmount;

varying vec2 vUv;
varying vec3 vNormal;

float gridLine(vec2 uv, float lineCount, float width) {
  vec2 grid = fract(uv * lineCount);
  float line = min(
    smoothstep(0.0, width, grid.x) * step(width, grid.y),
    smoothstep(0.0, width, grid.y) * step(width, grid.x)
  );
  return 1.0 - line;
}

void main() {
  vec3 baseColor = vec3(0.18, 0.18, 0.25);  // dark metallic
  float line = gridLine(vUv, gridLines, gridWidth);
  float pulse = 1.0 + pulseAmount * sin(time * pulseSpeed);
  vec3 color = baseColor + gridColor * line * gridIntensity * pulse;
  float alpha = 0.15 + line * 0.8 * pulse;
  gl_FragColor = vec4(color, alpha);
}
```

### JS Setup (Layered Pattern)
```js
// Layer 1: solid base for metallic PBR
const baseMat = new THREE.MeshStandardMaterial({
  color: 0x333355, roughness: 0.7, metalness: 0.8,
});
const body = new THREE.Mesh(geometry, baseMat);
group.add(body);

// Layer 2: translucent grid overlay (slightly larger)
const gridMat = new THREE.ShaderMaterial({ ... });
const gridOverlay = new THREE.Mesh(geometry.clone().scale(1.01), gridMat);
group.add(gridOverlay);
```

**Tuning:** `gridLines` controls panel density (3-10). `gridWidth` should be 0.05-0.1. Layer the overlay 1-5% larger than the base mesh so it sits on top without z-fighting.

## Pattern 7: Atmospheric Entry Heat Shield Glow

Fresnel rim + noise-based flicker for a plasma/heat effect around a ship. Used for atmospheric descent sequences.

### Fragment Shader
```glsl
uniform vec3 glowColor;     // orange/red for heat
uniform float intensity;    // 0-1, controlled from JS based on phase
uniform float noiseScale;   // spatial frequency
uniform float noiseSpeed;   // temporal speed of flicker

varying vec3 vNormal;
varying vec3 vPosition;

// hash() and noise() from Pattern 4 (noise/cloud shader)

void main() {
  vec3 viewDir = normalize(vPosition - cameraPosition);
  float rim = 1.0 - max(0.0, dot(viewDir, vNormal));
  float fresnel = pow(rim, 2.5);
  float flicker = 0.5 + 0.5 * noise(vPosition * noiseScale + time * noiseSpeed);
  vec3 color = glowColor * fresnel * intensity * flicker;
  gl_FragColor = vec4(color, fresnel * intensity * 0.6);
}
```

### JS Setup
```js
const entryGlow = new THREE.Mesh(
  new THREE.SphereGeometry(4, 16, 12),
  entryGlowMat
);
entryGlow.scale.set(1.3, 0.6, 2.5);  // flattened sphere around ship
entryGlowMat.uniforms.intensity.value = Math.sin(phaseProgress * Math.PI); // ramp up/down
entryGlow.visible = intensity > 0.05;
```

**Key constraint:** Use a noise function that calls `fract(p)` before smoothing — a common GLSL bug is `fract(f * f * (3.0 - 2.0 * f))` instead of `fract(p); f = f * f * (3.0 - 2.0 * f)`. The former uses `f` before it's defined.

## Pattern 8: Cubemap Gravitational Lensing

Distort a real environment through a gravitational lens using CubeCamera + samplerCube. The lens shell samples a dynamically-rendered cubemap with bent view directions, creating Einstein ring and chromatic aberration effects.

### Key technique: `uniform bool hasEnvMap`

GLSL does **not** allow comparing or constructing sampler types. You cannot write `if (envMap != samplerCube(0))` — this produces `ERROR: 'samplerCube' : cannot construct this type`. Instead, pass a boolean uniform from JS:

```js
const lensMat = new THREE.ShaderMaterial({
  uniforms: {
    bhCenter: { value: new THREE.Vector3(0, 0, 0) },
    bhRadius: { value: 2.0 },
    lensStrength: { value: 1.0 },
    envMap: { value: cubeRenderTarget.texture },
    hasEnvMap: { value: true },   // ← controls shader path
    time: { value: 0 },
  },
  // ...
});
```

```glsl
uniform samplerCube envMap;
uniform bool hasEnvMap;

void main() {
  if (hasEnvMap) {
    vec3 lensedColor = textureCube(envMap, bentDir).rgb;
    // ... cubemap lensing
  } else {
    // ... procedural fallback
  }
}
```

### CubeCamera setup

```js
const cubeRenderTarget = new THREE.WebGLCubeRenderTarget(256, {
  format: THREE.RGBAFormat,
  generateMipmaps: true,
  minFilter: THREE.LinearMipmapLinearFilter,
});
const cubeCamera = new THREE.CubeCamera(1, 500, cubeRenderTarget);
cubeCamera.position.set(0, 0, 0);
scene.add(cubeCamera);
```

### Animation loop: render cubemap every N frames

```js
let frameCount = 0;
function animate() {
  frameCount++;
  if (frameCount % 3 === 0) {  // every 3rd frame for performance
    lensShell.visible = false;  // avoid self-intersection
    cubeCamera.update(renderer, scene);
    lensShell.visible = true;
  }
  // ... rest of loop
}
```

### Chromatic aberration near Einstein ring

```glsl
float chromStrength = deflection * 0.08;
float r = textureCube(envMap, bentDir + vec3(chromStrength, 0.0, 0.0)).r;
float g = textureCube(envMap, bentDir).g;
float b = textureCube(envMap, bentDir - vec3(0.0, 0.0, chromStrength)).b;
vec3 chromatic = vec3(r, g, b);
vec3 envColor = mix(lensedColor, chromatic, ringFactor * 0.6);
```

## Pitfalls

1. **`gl_PointSize` is limited by GPU** — max 64-256px depending on hardware. For larger particles, use sprites or quads.
2. **Additive blending on transparent objects** — renders even invisible fragments, costing GPU time. Use `discard` early in fragment shader.
3. **Fresnel on flat surfaces** — fresnel requires curved normals. On flat planes, normals don't vary, so every pixel calculates the same rim value.
4. **Shader compilation errors** — GLSL doesn't give great error messages. Test in small increments. Use `npx vite build` to catch import/syntax issues.
5. **Mobile/Intel GPU compatibility** — avoid `textureCube`, use `#version 300 es` for modern WebGL2 features.
6. **Noise function self-reference bug** — `vec3 f = fract(f * f * (3.0 - 2.0 * f))` fails because `f` is used before assignment. Fix: `vec3 f = fract(p); f = f * f * (3.0 - 2.0 * f);`
7. **Layered overlay z-fighting** — when overlaying a shader mesh on a solid base mesh, make the overlay 1-5% larger to avoid z-fighting artifacts.
8. **GLSL sampler comparison is illegal** — `if (envMap != samplerCube(0))` fails with `cannot construct this type`. Samplers are opaque types in GLSL — no comparison, construction, or assignment. Use `uniform bool hasEnvMap` to control code paths instead.
9. **CubeCamera self-intersection** — when rendering a cubemap for lensing/reflections, hide the receiving object before calling `cubeCamera.update()`, then restore visibility. Otherwise the shell reflects/distorts itself.
10. **`Math.sin` vs `sin` in JS** — inside nested scopes or callbacks, always use `Math.sin()`. Bare `sin()` is undefined in strict mode. Also avoid reusing variable names like `tiltRad` in nested blocks — use distinct names (`tiltRad2`) to prevent scope shadowing bugs.
11. **Geometry must cover the shader's visible area** — when using a shader to create an expanding ring/wave effect (e.g., gravitational wave ripple), the geometry must cover the ENTIRE area where the effect needs to be visible, not just where the ring eventually appears. If you use `RingGeometry(BH_RADIUS * 1.5, MAX_RADIUS)` for an effect that starts at the center and expands outward, the shader has no fragments to draw at radii < BH_RADIUS*1.5, so the early stages of the animation are invisible. Fix: use `RingGeometry(0.5, MAX_RADIUS)` — a near-full disk — so the shader can render the expanding ring at any radius. The shader itself handles which pixels are bright (via Gaussian falloff around the current ring radius) — the geometry just needs to provide fragments everywhere the shader might draw.
12. **depthTest: false for overlay effects** — when rendering effects that must appear on top of other transparent objects (ripples over accretion disk, lens flare over atmosphere), set `depthTest: false` on the overlay material. Without it, the depth buffer from nearer transparent objects (like the accretion disk) can occlude the overlay even with additive blending. Combine with `renderOrder: 999` to ensure the overlay draws last.

## Verification

- [ ] Shader compiles (check browser console for errors)
- [ ] Uniforms animate correctly over time
- [ ] Transparency + blending produce expected visual
- [ ] No performance drop on target hardware
- [ ] Layered overlays do not z-fight with base mesh
