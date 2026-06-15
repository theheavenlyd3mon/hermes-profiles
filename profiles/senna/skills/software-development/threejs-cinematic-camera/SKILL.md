---
name: threejs-cinematic-camera
description: "Author cinematic camera moves in Three.js — three-story-controls setup, CatmullRomCurve3 spline paths, and cinematography principles for framing and composition."
version: 1.1.0
author: Senna
tags: [threejs, camera, cinematography, animation]
---

# Three.js Cinematic Camera

## Overview

Two approaches for authored camera paths in Three.js:

1. **CatmullRomCurve3** — built-in, no deps, programmatic splines from waypoints
2. **three-story-controls** (NYTimes) — CameraRig + CameraHelper, designed for narrative camera work

## Approach 1: CatmullRomCurve3 (Built-in)

Best for: procedural paths, quick iteration, no extra dependencies.

```js
import * as THREE from 'three';

// Define waypoints as [x, y, z] arrays
const points = [
  [0, 200, 600],
  [0, 100, 300],
  [0, 20, -20],
  [0, 10, -100],
];

// Create spline
const vecs = points.map(p => new THREE.Vector3(p[0], p[1], p[2]));
const curve = new THREE.CatmullRomCurve3(vecs);

// Sample in animation loop
function animate(t) {
  const pos = curve.getPointAt(t);        // t = 0..1
  const tangent = curve.getTangentAt(t);
  camera.position.copy(pos);

  // Look ahead along the path
  const lookAhead = curve.getPointAt(Math.min(t + 0.05, 1));
  camera.lookAt(lookAhead);
}
```

### Pitfalls
- Waypoints too few → spline can overshoot wildly between points
- Waypoints too far apart → camera speeds up/slows down unevenly
- Use `smoothstep(t)` to ease in/out: `t * t * (3 - 2 * t)`
- For constant speed, re-sample with `curve.getSpacedPoints(n)` or use `getPointAt()` (arc-length parameterized)

## Approach 2: three-story-controls (NYTimes)

Best for: authored, human-crafted camera paths with ease-in/out control.

```bash
npm install three-story-controls
```

### Basic Setup
```js
import { CameraRig } from 'three-story-controls';

const rig = new CameraRig(camera, renderer.domElement, {
  // Path from keyframes
});
```

### Key Concepts
- **CameraRig** — controls camera position + target via authored keyframes
- **CameraHelper** — visual debugging of paths in the scene
- Keyframes can define position, rotation, field of view, and easing per segment

### When to Use Each

| Situation | CatmullRomCurve3 | three-story-controls |
|-----------|-----------------|---------------------|
| Quick prototype | ✅ Best | ❌ Overhead |
| Procedural/generated paths | ✅ Best | ❌ Manual keyframes |
| Human-authored camera moves | ❌ Limited | ✅ Best |
| Multi-segment with different easing | ❌ Manual | ✅ Built-in |
| FOV changes per segment | ❌ Not supported | ✅ Keyframeable |
| Debugging/visualizing paths | ❌ Manual gizmo | ✅ CameraHelper |
| Bundle size impact | 0 (built-in) | ~15KB gzipped |

## Cinematography Principles Applied to 3D

### Rule of Thirds
Divide the frame into a 3×3 grid. Position key subjects at intersection points rather than center. In 3D, adjust camera position/target so the subject lies at a 1/3 or 2/3 position in frame.

```
+---+---+---+
|   |   |   |
+---+---+---+
|   | ● |   |  ← subject at intersection
+---+---+---+
|   |   |   |
+---+---+---+
```

### Golden Ratio (φ ≈ 1.618)
Compose elements using the golden spiral. More dynamic than rule of thirds for fly-throughs.

### 180° Rule
Keep the camera on one side of an imaginary axis between subjects. Prevents disorientation during cuts. For single-shot fly-throughs, keep camera on a consistent side.

### Leading Lines
Use scene geometry (city edges, ship hull lines, road curves) to guide the viewer's eye toward the subject. Position the camera so architectural lines converge on the focal point.

### Depth Layering
Every shot needs three planes of depth:
1. **Foreground** — near objects create depth cues (add ship canopy frame, passing debris, floating particles)
2. **Midground** — primary subject
3. **Background** — environment, sky, atmosphere, distant geometry

Foreground elements are often forgotten in 3D — a subtle ship canopy frame or passing particle instantly adds depth.

### Camera Movement Types for 3D

| Move | 3D Implementation | Emotional Effect |
|------|-------------------|-----------------|
| **Push in** | Move camera forward along forward vector | Intimacy, focus |
| **Pull out** | Move camera backward | Reveal, context |
| **Orbit** | Rotate camera around target (polar coordinates) | Discovery, scale |
| **Tracking/Follow** | Move camera parallel to subject motion | Speed, journey |
| **Crane up/down** | Raise/lower camera on Y-axis | Power, vulnerability |
| **Dutch angle** | Roll camera (rotate around forward axis) | Disorientation, tension |
| **Dolly zoom** | Move camera while zooming opposite direction | Vertigo, dramatic emphasis |
| **Whip pan** | Rapid orbit around a point — animate position in an arc over 0.5s | Urgency, transition |
| **Crash zoom** | Rapid FOV change: animate `camera.fov` from 75 to 10 over 0.3s | Impact, realization |

### Shot Sequence Design

For a cinematic fly-through, design the viewer's journey as a sequence of shots:

1. **Establishing shot** — wide, slow orbit or pull-back showing the full scene (5–10s)
2. **Approach** — tracking shot moving toward the subject (5–8s)
3. **Detail reveal** — slow push-in to highlight a specific element (3–5s)
4. **Action sequence** — fast tracking/chase with camera shake (5–10s)
5. **Climax** — dramatic angle (low shot looking up, or crane shot looking down) (3–5s)
6. **Resolution** — slow pull-out to re-establish context (5–8s)

**Timing:** Animate camera progress with `smoothstep(t)` easing. Total cinematic: 30–90 seconds.

### The 6-Question Cinematic Design Check

Before writing code, answer these six questions:

1. **What mood am I creating?** (Dawn wonder? Neon excitement? Deep-space loneliness? → Controls lighting, fog, color palette)
2. **Where is the viewer looking?** (The subject. → Controls camera framing, rule of thirds, depth layering)
3. **How does the viewer move through the scene?** (Slow reveal? Fast chase? → Controls camera speed, path shape, shake intensity)
4. **What breathes life into this world?** (Particles? Fog? Glowing signs? → Controls effects layer)
5. **What's the visual signature?** (Warm and soft? Cold and sharp? Neon and saturated? → Controls post-processing and color grading)
6. **Can it run at 30+ fps?** (→ Controls half-res, pass count, particle budget)

### Three-Point Lighting
```js
// Key light — primary illumination (strong, directional)
const keyLight = new THREE.DirectionalLight(0xffffff, 1.5);
keyLight.position.set(50, 100, -200);

// Fill light — softens shadows
const fillLight = new THREE.AmbientLight(0x334466, 0.6);

// Back light — rim light, separates subject from background
const backLight = new THREE.DirectionalLight(0x4488ff, 0.5);
backLight.position.set(-50, 50, 200);
```

See [[threejs-cinematic-lighting]] for expanded five-point setup and scene mood guide.

### Parallel Chase Paths (from Approach 3 below)

For third-person shots where subject must fill a specific third of frame, use the parallel chase path offset variant that matches the shot type to offset parameters.

## Camera Shake (for high-speed sequences)

```js
// Add subtle camera shake during fast segments
let shakeIntensity = 0;

function applyShake(camera, intensity) {
  const seed = Math.random() * Math.PI * 2;
  camera.position.x += Math.sin(seed) * intensity;
  camera.position.y += Math.sin(seed * 1.3) * intensity;
}
```

## Approach 3: Parallel Camera Paths (Chase Shots)

For third-person chase shots where the camera follows a moving subject (dragon, speeder, character), derive a second CatmullRomCurve3 from the subject's path by sampling it at N points and computing an offset based on the path tangent at each point.

### Technique

```js
import * as THREE from 'three';

const subjectPoints = [
  new THREE.Vector3(-200, 30, -200),
  new THREE.Vector3(-100, 25, -100),
  new THREE.Vector3(0, 20, 0),
  new THREE.Vector3(100, 25, -50),
  new THREE.Vector3(200, 35, -150),
];

const subjectCurve = new THREE.CatmullRomCurve3(subjectPoints);

// Derive camera path: sample subject path, compute offset per sample
const cameraPoints = [];
const sampleCount = 100;

for (let i = 0; i <= sampleCount; i++) {
  const t = i / sampleCount;
  const pos = subjectCurve.getPointAt(t);
  const tangent = subjectCurve.getTangentAt(t);

  // Right vector (cross tangent with world up)
  const right = new THREE.Vector3()
    .crossVectors(tangent, new THREE.Vector3(0, 1, 0))
    .normalize();

  // Offset: behind (-tangent), right, and up
  const offset = new THREE.Vector3()
    .addScaledVector(tangent, -18)   // behind
    .addScaledVector(right, 8)       // side
    .addScaledVector(new THREE.Vector3(0, 0.4, 0), 6); // above

  // Ease offset spread — tighter at start, wider at end
  const ease = t < 0.1 ? t / 0.1 : (t > 0.9 ? 1.0 - (t - 0.9) / 0.1 : 1.0);
  offset.multiplyScalar(0.6 + ease * 0.4);

  cameraPoints.push(pos.clone().add(offset));
}

const cameraCurve = new THREE.CatmullRomCurve3(cameraPoints);
```

### Synchronized Animation

```js
let progress = 0; // 0..1

function animate() {
  const smoothT = progress * progress * (3 - 2 * progress); // smoothstep

  // Position subject on its path
  const subjPos = subjectCurve.getPointAt(smoothT);
  const subjTangent = subjectCurve.getTangentAt(smoothT);
  subject.group.position.copy(subjPos);
  subject.group.lookAt(subjPos.clone().add(subjTangent)); // face forward

  // Position camera on its offset path
  const camPos = cameraCurve.getPointAt(smoothT);
  camera.position.copy(camPos);
  camera.lookAt(subjPos); // always look at subject

  progress += dt / totalDuration;
}
```

### Variants

| Shot type | Tangent factor | Right factor | Up factor | Use case |
|-----------|---------------|--------------|-----------|----------|
| Tight following | -8 | 3 | 2 | Close chase, rider framing |
| Wide action | -18 | 8 | 6 | Mid shot, environment context |
| Reveal pull-out | dynamic (0→-25) | dynamic (0→12) | 8 | Opening reveal / finale |
| Over-shoulder | -4 | -2 | 1.5 | Subject fills left third |
| Low chase | -10 | 5 | 2 | Ground-level pursuit (speeders) |

### Pitfalls

- **Offset direction flips at path endpoints** if tangent changes sign abruptly. Clamp progress to [0, 1].
- **Camera clips through terrain** when subject banks near geometry. Add a minimum-distance push or cap the offset vector.
- **LookAt snaps** if subject position jumps. Use `camera.position.lerp(target, 0.08)` for smooth follow instead of direct assignment.
- **Offset scaling changes camera speed** — a wider offset creates more lateral movement, making the camera feel faster. Tune offset magnitude, not the path progress rate.
- **Subject rotation via lookAt** works for forward-facing subjects. For subjects that should bank into turns, compute bank angle from the path tangent's rate of change (second derivative).

### When to use parallel paths vs follow-camera lerp

| Approach | When |
|----------|------|
| Parallel paths | Fixed cinematic timeline, camera must hit specific framing at specific times |
| Lerp-follow | Interactive/real-time, subject position is unpredictable |

## Pitfalls

1. **CatmullRomCurve3 waypoint density** — a path with 4 waypoints over 600 units will produce an overly smooth curve that cuts corners. Add intermediate waypoints for complex paths.
2. **Camera lookAt with splines** — `getTangentAt()` gives the direction of travel. For a cinematic feel, look slightly off-axis from the tangent, not directly along it.
3. **Smoothstep is essential** — raw `t` linear interpolation produces jarring starts/stops. Apply `t * t * (3 - 2 * t)` to normalize time.
4. **Frame rate independence** — don't advance `t` by a fixed delta per frame. Advance by `dt / totalDuration`.
5. **Parallel path offset direction** — offset vectors are computed from the tangent, which flips on closed loops or sharp curves. Always verify the camera side stays consistent by visualizing both paths with debug lines.

## Verification

- [ ] Camera path is smooth with no visible jerks
- [ ] Framing follows rule of thirds for key subjects
- [ ] LookAt target stays ahead of camera movement
- [ ] No clipping through scene geometry
- [ ] Camera side remains consistent throughout path (doesn't flip sides at midpoint)
- [ ] Subject's rotation matches path direction (faces forward)
