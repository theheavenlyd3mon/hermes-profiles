---
name: threejs-simulation
description: |
  Build interactive 3D browser simulations with Three.js + Vite. Covers scene setup,
  animation loops with delta-time, interactive UI overlays, camera controls, and
  debugging frozen animation. Trigger when the user asks for a 3D scene, simulation,
  visualization, or interactive Three.js project.
metadata:
  hermes:
    related_skills: [threejs-postprocessing, threejs-shader-patterns, threejs-cinematic-camera, threejs-engine-trail]
---

# Three.js Simulation

Quick-start patterns for building interactive 3D simulations with Three.js and Vite.

## Scaffolding

```bash
mkdir -p <project-dir> && cd <project-dir>
npm init -y
npm install three vite
```

Package.json scripts:
```json
"scripts": {
  "dev": "vite",
  "build": "vite build",
  "preview": "vite preview"
}
```

Run: `npx vite --host 127.0.0.1` (serves on port 5173)

### Post-scaffolding: git init

After initializing the project and creating at least one source file:
```bash
cd <project-dir>
echo "node_modules/\ndist/\n.vite/\n*.local\n.DS_Store" > .gitignore
git init && git add -A && git commit -m "feat: initial commit — <project-name>"
```

Minimal `index.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>body { margin: 0; overflow: hidden; }</style>
</head>
<body>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

## Scene Setup Pattern

Create `src/scene.js` exporting a `createScene()` factory:

```js
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export function createScene() {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000011);

  const camera = new THREE.PerspectiveCamera(
    75, window.innerWidth / window.innerHeight, 0.1, 1000
  );
  camera.position.set(0, 60, 120);
  camera.lookAt(0, 0, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  // Lighting
  scene.add(new THREE.AmbientLight(0xffffff, 0.1));
  const pointLight = new THREE.PointLight(0xffffff, 2);
  pointLight.position.set(0, 0, 0);
  scene.add(pointLight);

  // Resize handler
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  return { scene, camera, renderer, controls };
}
```

## Animation Loop: Timer (r184+)

**This is the most critical pitfall.** Three.js r184 deprecated `THREE.Clock` — the console prints `THREE.Clock: This module has been deprecated. Please use THREE.Timer instead.` AND calling `clock.update()` on Clock throws `TypeError: clock.update is not a function`. Use `Timer` for all r184+ projects.

### Import paths for r184

In Three.js r184, the npm package maps `./addons/*` → `./examples/jsm/*` via package.json exports. The `addons/` prefix is a **virtual alias** — there is no physical `node_modules/three/addons/` directory. Use either path:

```js
// Both resolve to the same file (addons/ is a virtual alias):
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
```

**Timer.js** lives at `three/src/core/Timer.js`, NOT in `three/addons/misc/` and NOT in `three/examples/jsm/misc/`. Import it directly:

```js
import { Timer } from 'three/src/core/Timer.js';
```

**Do not try `import { Timer } from 'three/addons/misc/Timer.js'`** — this path does not resolve in r184.

### Timer (required for r184+)

```js
import { Timer } from 'three/src/core/Timer.js';

const clock = new THREE.Timer();
clock.connect(document);   // Page Visibility API — parameter required in r184+

function animate() {
  requestAnimationFrame(animate);
  clock.update();           // REQUIRED: computes delta for this frame
  const deltaTime = clock.getDelta();  // returns the computed delta
  // ... update objects with deltaTime ...
  controls.update();
  renderer.render(scene, camera);
}
```

### BROKEN patterns

```js
// BROKEN: Clock does not have update()
const clock = new THREE.Clock();
clock.update();  // TypeError: clock.update is not a function

// BROKEN: Timer without connect()
const clock = new THREE.Timer();  // connect() never called
// getDelta() returns 0 on every call → no animation movement

// BROKEN: Timer.connect() without document argument
const clock2 = new THREE.Timer();
clock2.connect();  // TypeError: Cannot read properties of undefined (reading 'hidden')
```

## GLTF Model Loading & Animation

Loading animated 3D characters (dragon, rider, creatures) via `GLTFLoader` and driving them with Three.js's `AnimationMixer`. Required for any scene with imported animated models.

### Setup

```bash
npm install three vite
# GLTFLoader ships with three — no extra deps
```

### Loader + AnimationMixer Pattern

```js
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';  // optional: compressed

const loader = new GLTFLoader();
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.6/');
loader.setDRACOLoader(dracoLoader);

const animMixers = [];

loader.load('/models/dragon.glb', (gltf) => {
  const model = gltf.scene;
  scene.add(model);
  model.scale.set(2, 2, 2);
  model.position.set(0, 20, 0);

  const mixer = new THREE.AnimationMixer(model);
  const action = mixer.clipAction(gltf.animations[0]);
  action.play();
  animMixers.push(mixer);
});

// In animation loop:
function animate() {
  clock.update();
  const dt = clock.getDelta();
  for (const mixer of animMixers) mixer.update(dt);
  controls.update();
  composer.render();
}
```

### Multiple Animations

Models with multiple clips (e.g. "Three Motion Loops" dragon):

```js
loader.load('/models/dragon.glb', (gltf) => {
  const mixer = new THREE.AnimationMixer(gltf.scene);
  const flyAnim = THREE.AnimationClip.findByName(gltf.animations, 'fly');
  const idleAnim = THREE.AnimationClip.findByName(gltf.animations, 'idle');

  let currentAction = mixer.clipAction(flyAnim);
  currentAction.play();

  function switchAnimation(newClip, duration = 0.5) {
    const nextAction = mixer.clipAction(newClip);
    currentAction.crossFadeTo(nextAction, duration, true);
    nextAction.play();
    currentAction = nextAction;
  }
});
```

### Static Model: Procedural Animation

When a glTF model has no animations (`gltf.animations.length === 0`), animate it by parenting it to a `Group` and applying sine-wave transforms to the group each frame. Works for flying creatures, vehicles, and any object where smooth cyclical motion is acceptable.

```js
import * as THREE from 'three';

// In loader callback:
const modelGroup = new THREE.Group();
modelGroup.add(gltf.scene);
scene.add(modelGroup);

// Store references for the animation loop
const dragon = { group: modelGroup, basePos: modelGroup.position.clone() };

// In animation loop:
function updateDragon(dragon, dt, elapsed) {
  const g = dragon.group;

  // Bobbing (up/down) — like riding thermals
  g.position.y = dragon.basePos.y + Math.sin(elapsed * 1.2) * 1.5;

  // Gentle roll (banking side to side)
  g.rotation.z = Math.sin(elapsed * 0.8) * 0.08;

  // Pitch (nodding forward/back)
  g.rotation.x = Math.sin(elapsed * 0.6 + 1.2) * 0.05;

  // Yaw (subtle head turning)
  g.rotation.y += Math.sin(elapsed * 0.3) * 0.002;
}
```

The dragon flies *through* the scene via the camera-path (or by moving the group's position along a curve). The sine-wave transforms add organic liveliness on top.

### Pitfalls

- **CORS:** GLTFLoader fetches .bin + texture files — `file://` fails. Always serve via Vite.
- **Draco decoder path** must point to WASM files. Without it, compressed .glb silently fails.
- **Scale mismatch:** imported glTF units are arbitrary. If the dragon looks like a speck, scale 50×-200×.
- **No animations play / static model:** confirm `gltf.animations.length > 0`. If 0, the model has no rig/animation clips — use the **Static Model: Procedural Animation** pattern above instead of AnimationMixer.
- **Texture loading silently fails:** check Network tab for 404s. Missing textures = grey silhouette.
- **See `references/free-3d-model-sourcing.md`** for finding free animated models (Sketchfab CC, OpenGameArt, selection criteria).
- **See `references/gltf-model-inspection.md`** for inspecting a downloaded glTF before loading (check animations, textures, rig, scale). Always inspect first to avoid loading a model that needs rework.

## Camera Controls: Orbit vs Fly Toggle

Toggle between OrbitControls (damped, target-based) and FlyControls (free-flight, WASD-style) without dispose/re-create to avoid memory leaks.

### Setup

```js
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { FlyControls } from 'three/addons/controls/FlyControls.js';

// Create OrbitControls normally (from createScene)
const orbitControls = new OrbitControls(camera, renderer.domElement);
orbitControls.enableDamping = true;

// Create FlyControls but keep disabled
const flyControls = new FlyControls(camera, renderer.domElement);
flyControls.movementSpeed = 10;
flyControls.rollSpeed = 0.2;
flyControls.dragToLook = true;
flyControls.enabled = false;        // starts disabled
```

### Toggle Logic

```js
function toggleCameraMode() {
  if (cameraMode === 'orbit') {
    orbitControls.enabled = false;
    flyControls.enabled = true;
    cameraMode = 'fly';
  } else {
    flyControls.enabled = false;
    orbitControls.enabled = true;
    cameraMode = 'orbit';
  }
}
```

**Key constraint:** toggle `.enabled`, never create/dispose/re-create. FlyControls registers event listeners (keydown, keyup, mousemove, mousedown, mouseup) in its constructor — creating a new instance every toggle leaks listeners. `.enabled = true/false` cleanly gates input handling without leaks.

### Animation Loop

FlyControls **does** need `update(deltaTime)` called each frame (contrary to some docs about auto-registration):

```js
function animate() {
  requestAnimationFrame(animate);
  clock.update();           // Timer.update() — NOT Clock, which has no update()
  const deltaTime = clock.getDelta();

  // Update active controls
  orbitControls.update();
  flyControls.update(deltaTime);    // safe to call even when disabled

  composer.render();
  labelRenderer.render(scene, camera);
}
```

Calling `flyControls.update(deltaTime)` every frame is harmless when `enabled = false` — it skips all input processing internally.

### Interaction with Raycaster UI

Fly mode disables the orbit-based raycaster. When switching to fly mode:

1. **Hide selection ring** — it only updates correctly under orbit camera control
2. **Deselect any selected object** — info panel becomes stale
3. **Button label update** — show current mode in the UI toggle ("🔄 Orbit" / "🔄 Fly")

```js
// In toggle handler for fly mode:
if (mode === 'fly') {
  const ring = scene.children.find(c => c.isMesh && /* ring identification */);
  if (ring) ring.visible = false;
  selectedObject = null;           // clear selection
  hideInfoPanel();                 // close info overlay
}
```

### Button Pattern

Add to the control bar with consistent styling:

```js
const modeBtn = document.createElement('button');
modeBtn.textContent = '\u{1F504} Orbit';    // 🔄 Orbit
modeBtn.title = 'Toggle OrbitControls / FlyControls';
modeBtn.style.cssText = `
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: white;
  padding: 0 12px;
  height: 36px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
`;

modeBtn.addEventListener('click', () => {
  toggleCameraMode();
  modeBtn.textContent = cameraMode === 'fly' ? '\u{1F504} Fly' : '\u{1F504} Orbit';
});
```

## InstancedMesh for Large Object Counts

Replace `THREE.Points` or `THREE.Mesh` with `THREE.InstancedMesh` for 100k+ objects with per-instance position, scale, rotation, and color — significantly more performant than individual meshes or BufferGeometry points.

### Starfield Pattern

```js
import * as THREE from 'three';

export function createStarfield(scene) {
  const starCount = 100000;
  const radius = 500;

  // Small icosahedron as reference geometry — looks star-like
  const geometry = new THREE.IcosahedronGeometry(0.3, 0);
  const material = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const instanceMesh = new THREE.InstancedMesh(geometry, material, starCount);

  const dummy = new THREE.Object3D();
  const color = new THREE.Color();

  for (let i = 0; i < starCount; i++) {
    // Uniform sphere distribution (same formula as BufferGeometry points)
    const r = radius * Math.cbrt(Math.random());
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);

    dummy.position.set(
      r * Math.sin(phi) * Math.cos(theta),
      r * Math.sin(phi) * Math.sin(theta),
      r * Math.cos(phi)
    );

    // Per-instance scale for variety
    const scale = 0.5 + Math.random() * 2.5;
    dummy.scale.set(scale, scale, scale);

    // Random rotation for visual variety
    dummy.rotation.set(
      Math.random() * Math.PI * 2,
      Math.random() * Math.PI * 2,
      Math.random() * Math.PI * 2
    );

    dummy.updateMatrix();
    instanceMesh.setMatrixAt(i, dummy.matrix);

    // Per-instance color
    const rand = Math.random();
    if (rand < 0.95) {
      color.setHex(0xffffff);          // 95% white
    } else if (rand < 0.975) {
      color.setHex(0xff4444);          // 2.5% red giant
    } else {
      color.setHex(0x4444ff);          // 2.5% blue supergiant
    }
    instanceMesh.setColorAt(i, color);
  }

  instanceMesh.instanceMatrix.needsUpdate = true;
  instanceMesh.instanceColor.needsUpdate = true;
  instanceMesh.computeBoundingSphere();     // enables frustum culling

  scene.add(instanceMesh);
  return instanceMesh;
}
```

### Key constraints

- **InstancedMesh API:** `setMatrixAt(index, matrix)` for transforms, `setColorAt(index, color)` for per-instance colors. Both require `needsUpdate = true` after populating.
- **Material is shared** — you can't have per-instance materials. Use `setColorAt()` for per-instance color variation instead.
- **Frustum culling:** always call `computeBoundingSphere()` after setting all matrices. Without it, the object won't cull and performance degrades at scale.
- **No animation needed** — InstancedMesh handles static objects efficiently. For twinkling, add a simple opacity oscillation in the animation loop.
- **Scales to 500k+** — on modern GPUs, InstancedMesh with a simple geometry (icosahedron, tetrahedron) handles 500k instances at 60fps.
- **Color must be enabled:** `instanceMesh.instanceColor.needsUpdate = true` after the loop — without this, colors silently default to the material color.

### Comparison: Points vs InstancedMesh

| Aspect | THREE.Points | THREE.InstancedMesh |
|--------|-------------|-------------------|
| Object count | ~3k before perf degrades | 100k-500k comfortably |
| Per-instance color | Via BufferAttribute | Via setColorAt() |
| Per-instance scale | Requires separate Points or shader | Via matrix |
| Frustum culling | Not supported by default | With computeBoundingSphere() |
| 3D look | Flat sprites (always face camera) | Real geometry with depth |
| Per-instance animation | Via custom shader (phase attribute) | Not possible — shared material |
| Use case | Distant dust/nebula, twinkling stars | Visible stars, asteroids, particles |

### When to migrate: InstancedMesh → Points + Custom Shader

InstancedMesh shares a single material across all instances — you **cannot** animate individual instances (twinkle, pulse, phase). When you need per-instance animation:

1. Create a `THREE.BufferGeometry` with attributes: `position`, `color`, `size`, `phase`
2. Write a vertex shader that uses `phase` to offset animation timing
3. Use `THREE.Points` with `ShaderMaterial` instead of `InstancedMesh`

```js
// BEFORE (InstancedMesh — static only)
const starfield = new THREE.InstancedMesh(geo, mat, count);
// setColorAt() works, but no per-instance twinkle

// AFTER (Points + shader — per-star animation)
const geo = new THREE.BufferGeometry();
geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
geo.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
geo.setAttribute('phase', new THREE.BufferAttribute(phases, 1)); // unique per star

const mat = new THREE.ShaderMaterial({
  uniforms: { time: { value: 0 }, twinkleSpeed: { value: 1.5 }, twinkleAmount: { value: 0.35 } },
  vertexShader: starVertexShader,  // uses phase for twinkle
  fragmentShader: starFragmentShader,
  transparent: true, blending: THREE.AdditiveBlending, depthWrite: false,
  vertexColors: true,  // enables 'color' attribute
});
const starfield = new THREE.Points(geo, mat);
```

**Key constraint:** When using `vertexColors: true` with ShaderMaterial, the attribute must be named `color` (Three.js convention). For custom names, use `attribute vec3 customColor;` in the shader and set `geometry.setAttribute('customColor', ...)`.

### Orbital/Inward-Spiral Particle Pattern

Particles that follow curved paths inward (accretion stream, whirlpool, funnel). Unlike the linear ring-buffer pattern, each particle tracks its own orbital state:

```js
// Per-particle orbital state (separate arrays for cache locality)
const orbitAngle = new Float32Array(MAX);
const orbitDist = new Float32Array(MAX);
const orbitSpeed = new Float32Array(MAX);
const fallSpeed = new Float32Array(MAX);
const lives = new Float32Array(MAX);  // -1 = dead, 0-1 = alive

// Spawn at inner disk edge
function spawnParticle(i) {
  lives[i] = 0;
  orbitAngle[i] = Math.random() * Math.PI * 2;
  orbitDist[i] = DISK_INNER + Math.random() * 1.5;
  orbitSpeed[i] = 1.5 + Math.random() * 2.0;  // angular velocity
  fallSpeed[i] = 0.8 + Math.random() * 1.2;    // radial velocity
}

// Update — spiral inward
function updateParticles(dt) {
  for (let i = 0; i < MAX; i++) {
    if (lives[i] < 0) continue;

    lives[i] += dt * fallSpeed[i];
    if (lives[i] >= 1.0 || orbitDist[i] <= MIN_DIST) {
      lives[i] = -1;  // kill
      sizes[i] = 0;
      continue;
    }

    orbitDist[i] -= dt * 3.0 * fallSpeed[i];     // spiral inward
    orbitAngle[i] += dt * orbitSpeed[i] * 2.0;   // orbit

    positions[i * 3]     = Math.cos(orbitAngle[i]) * orbitDist[i];
    positions[i * 3 + 1] = 0;  // or tilted
    positions[i * 3 + 2] = Math.sin(orbitAngle[i]) * orbitDist[i];
    sizes[i] = (1.0 - lives[i]) * 2.0;  // shrink as it falls in
  }
}
```

**Spawn throttling:** Don't spawn every frame. Use a timer to spawn 1-3 particles every 50-150ms:
```js
let nextSpawn = 0;
nextSpawn -= dt;
if (nextSpawn <= 0) {
  // find dead particle, call spawnParticle()
  nextSpawn = 0.05 + Math.random() * 0.1;
}
```

### Disk Flare Events (Uniform Modulation)

Random brightness/orbital-speed pulses on an accretion disk. Modulate a shader uniform with exponential decay:

```js
let flareIntensity = 0;
let nextFlareTime = 3 + Math.random() * 5;

function updateFlares(dt) {
  nextFlareTime -= dt;
  if (nextFlareTime <= 0) {
    flareIntensity = 0.3 + Math.random() * 0.7;  // random strength
    nextFlareTime = 4 + Math.random() * 8;        // random interval
  }
  if (flareIntensity > 0) {
    flareIntensity *= Math.pow(0.05, dt);  // exponential decay
    if (flareIntensity < 0.01) flareIntensity = 0;
    diskMat.uniforms.speed.value = baseSpeed * (1.0 + flareIntensity * 0.5);
  }
}
```

**Tuning:** Decay rate `0.05` gives ~2s half-life. Increase for faster decay (0.1 = ~1s). Flare interval 4-12s feels natural for accretion disk variability.

### Vegetation Scattering (Forest / Trees)

Scatter InstancedMesh trees across a terrain surface. The pattern: sample terrain height at each tree position, randomize scale/rotation, and optionally use vertex-shader LOD for distant trees.

```js
import * as THREE from 'three';

export function createForest(terrainHeightFn, treeTrunkGeo, treeCrownGeo, count = 2000) {
  const trunkMat = new THREE.MeshStandardMaterial({ color: 0x5c4033, roughness: 0.9 });
  const crownMat = new THREE.MeshStandardMaterial({ color: 0x2d5a1e, roughness: 0.8 });

  const dummy = new THREE.Object3D();
  const trunkMesh = new THREE.InstancedMesh(treeTrunkGeo, trunkMat, count);
  const crownMesh = new THREE.InstancedMesh(treeCrownGeo, crownMat, count);
  const color = new THREE.Color();

  let idx = 0;
  for (let i = 0; i < count; i++) {
    // Random position within bounds
    const x = (Math.random() - 0.5) * 200;
    const z = (Math.random() - 0.5) * 200;
    const y = terrainHeightFn(x, z);

    // Skip trees below water level or on very steep slopes
    if (y < 0) continue;

    // Randomize scale by species variation
    const s = 0.6 + Math.random() * 0.8;
    dummy.position.set(x, y, z);
    dummy.scale.set(s, s, s);
    dummy.rotation.y = Math.random() * Math.PI * 2;
    dummy.updateMatrix();
    trunkMesh.setMatrixAt(idx, dummy.matrix);
    crownMesh.setMatrixAt(idx, dummy.matrix);

    // Slight color variation per tree
    const greenVar = 0.2 + Math.random() * 0.3;
    color.setHSL(0.28, 0.5 + Math.random() * 0.3, greenVar);
    crownMesh.setColorAt(idx, color);

    idx++;
  }

  trunkMesh.count = idx;
  crownMesh.count = idx;
  trunkMesh.instanceMatrix.needsUpdate = true;
  crownMesh.instanceMatrix.needsUpdate = true;
  crownMesh.instanceColor.needsUpdate = true;

  // Frustum culling for performance
  trunkMesh.computeBoundingSphere();
  crownMesh.computeBoundingSphere();

  const group = new THREE.Group();
  group.add(trunkMesh);
  group.add(crownMesh);
  return group;
}
```

### Vertex-Shader LOD for Distant Trees

For high tree counts, cull distant leaves at the vertex level so the GPU skips fragment shading:

```glsl
// In the leaf/crown material's vertex shader:
uniform float lODistance;

void main() {
  vec4 worldPos = modelMatrix * vec4(position, 1.0);
  float dist = distance(cameraPosition, worldPos.xyz);

  if (dist > lODistance) {
    // Cull this leaf — GPU eliminates it before fragment stage
    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
    return;
  }

  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
```

### Vegetation Scattering Constraints

- **Heightmap sampling:** trees must sit on terrain. Sample terrain Y (from your height function or shader displacement) at each (x, z) before placing.
- **Density control:** 500-2000 trees for a forest from dragon-flight altitude. Above 2000, add vertex LOD or billboard LOD.
- **Skip water/slopes:** trees below water line or on >45° slopes look wrong. Gate with `if (y < waterLevel || slope > threshold) continue;`.
- **Multi-species variety:** use 2-3 trunk/crown geometry pairs for visual diversity. Randomize which pair per tree instance.
- **Shadow culling:** disable shadows on the farthest 30% of trees for a free performance win.
- **See `references/procedural-forest-vegetation.md`** for the full procedural tree generation + vertex LOD pattern from the three.js forum.

## Debugging Frozen Animation

Symptom: objects exist in the scene but don't move despite correct position-update code.

Step-by-step differential diagnosis:

1. **Confirm the animation loop is firing.** Check with a frame counter:
   ```js
   let frameCount = 0;
   setInterval(() => { console.log(`Frames/2s: ${frameCount}`); frameCount = 0; }, 2000);
   // Inside animate(): frameCount++;
   ```
   If frame count is ~120, rAF is running at 60fps.

2. **Log deltaTime.** Inside the animate function:
   ```js
   clock.update();
   console.log('dt:', clock.getDelta().toFixed(5));
   ```
   If it prints `0.00000`, the timer is not being updated. Two possible causes:
   - **`clock.update()` is missing** from the animation loop (the **most common** r184+ bug — Timer separates update from query)
   - `clock.connect()` was never called (relevant only if Page Visibility API is needed)
   A healthy 60fps loop shows `~0.01667`; a headless browser of ~12fps shows `~0.083`.

3. **Log object positions over time.** Inside the update function:
   ```js
   if (frameCount % 60 === 0) {
     console.log('angle:', object.angle.toFixed(4), 'pos:', object.mesh.position.x.toFixed(2));
   }
   ```
   If position changes while deltaTime is 0, the position update uses a wrong time source. If position never changes and deltaTime is 0, the timer is the root cause.

4. **Skip visual debugging in headless browsers.** Browser screenshot tools may not show smooth animation. Prefer console-based state verification.

## Interactive UI Overlays

Keep UI elements as fixed-position DOM overlays, not Three.js objects. Pattern:

```
index.html — contains <div id="ui-container"> styled with position: fixed
src/ui.js  — module that creates sliders, buttons, info panels
```

The UI module accepts `simState` (a shared mutable object) rather than returning values:
```js
const simState = { speedMultiplier: 1, paused: false, selectedPlanet: null };
createUI(scene, camera, renderer, entities, simState);
// Animation loop reads simState.paused and simState.speedMultiplier
```

## Raycaster Selection

Click-to-select pattern for 3D objects:

```js
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener('click', (event) => {
  if (event.target !== renderer.domElement) return; // ignore UI clicks

  const rect = renderer.domElement.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(targetMeshes);

  if (intersects.length > 0) {
    const hit = intersects[0].object;
    // ... show info for selected object ...
  }
});
```

## CSS2D Labels

HTML labels overlaid on 3D objects using the CSS2DRenderer. These render as styled DOM elements on top of the WebGL canvas — text is always sharp, supports full CSS styling, and clicks pass through to the canvas.

### Pattern

```js
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';

// 1. Create the overlay renderer (once, after the WebGL renderer)
const labelRenderer = new CSS2DRenderer();
labelRenderer.setSize(window.innerWidth, window.innerHeight);
labelRenderer.domElement.style.position = 'absolute';
labelRenderer.domElement.style.top = '0';
labelRenderer.domElement.style.left = '0';
labelRenderer.domElement.style.pointerEvents = 'none'; // critical: let clicks through
labelRenderer.domElement.style.zIndex = '1';
document.body.appendChild(labelRenderer.domElement);

// 2. Create a label for a 3D object
function createLabel(name, dataLine, parentMesh, yOffset) {
  const div = document.createElement('div');
  div.style.textAlign = 'center';
  div.style.pointerEvents = 'none';
  div.style.background = 'rgba(0, 0, 20, 0.55)';
  div.style.backdropFilter = 'blur(4px)';
  div.style.border = '1px solid rgba(255, 255, 255, 0.12)';
  div.style.borderRadius = '8px';
  div.style.padding = '4px 10px';

  const nameEl = document.createElement('div');
  nameEl.textContent = name;
  nameEl.style.color = '#fff';
  nameEl.style.fontSize = '13px';
  nameEl.style.fontWeight = '600';

  const dataEl = document.createElement('div');
  dataEl.textContent = dataLine;
  dataEl.style.color = '#aab';
  dataEl.style.fontSize = '10px';

  div.appendChild(nameEl);
  div.appendChild(dataEl);

  const label = new CSS2DObject(div);
  label.position.set(0, yOffset, 0); // above the mesh center
  parentMesh.add(label); // auto-follows parent transforms
  return label;
}

// 3. In animation loop — render AFTER WebGL/composer
function animate() {
  // ... update objects ...
  controls.update();
  renderer.render(scene, camera); // or composer.render()
  labelRenderer.render(scene, camera); // renders on top
}
```

### Key constraints
- **Render order matters:** `labelRenderer.render()` must come AFTER `renderer.render()` / `composer.render()` so labels sit on top
- **`pointer-events: none`** on both div and the labelRenderer domElement — otherwise click events get swallowed by the overlay
- **Children of parent mesh:** adding labels as children of the 3D object means they automatically follow position, rotation, and scale changes
- **No extra npm deps:** CSS2DRenderer ships as `three/addons/renderers/CSS2DRenderer.js`

### Pitfalls
- **UI modules must receive `controls` as parameter if they reference OrbitControls methods.** A common mistake: `ui.js` has a reset button handler that calls `controls.target.set(0, 0, 0)` and `controls.update()`, but `createUI()` never receives `controls` as a parameter — this crashes at runtime. Make sure your `createUI(...)` signature includes `controls` (or `camera`) if any UI callback needs to manipulate the camera or controls:
  ```js
  // CORRECT:
  export function createUI(scene, camera, renderer, controls, planets, simState) {
    // resetBtn handler can now call controls.target.set(...)
  }

  // In main.js:
  const { scene, camera, renderer, controls } = createScene();
  const ui = createUI(scene, camera, renderer, controls, planets, simState);
  ```

- **Both controls update() calls every frame are safe but wasteful.** When toggling between OrbitControls and FlyControls, both `controls.update()` and `flyControls.update(deltaTime)` are called every animation frame even when one is disabled. This is harmless (`flyControls.update()` skips processing when not enabled), but the clean pattern is to only call the active control's update method. However, for simplicity, calling both is acceptable if performance isn't tight.

- CSS2DRenderer does NOT support `transform` matrix manipulation the way WebGL objects do. Labels always face the camera.
- If the scene has transparent objects, labels may render behind them despite z-ordering. Use `sortObjects = false` on the labelRenderer if transparency ordering breaks.
- Window resize must be forwarded: `labelRenderer.setSize(w, h)` in the resize handler.

## Custom Shaders (ShaderMaterial)

For effects beyond what built-in materials support — atmosphere glow, twinkling stars, pulsating neon — use `ShaderMaterial` with vertex/fragment shaders in separate `.glsl.js` files.

### File structure

```
src/
  shaders/
    atmosphere.glsl.js    — exports vertex/fragment strings
    starfield.glsl.js     — exports vertex/fragment strings
  main.js                 — imports and wires ShaderMaterial
```

### Shader module pattern

Each shader file exports vertex and fragment shader source as string constants:

```js
// src/shaders/atmosphere.glsl.js
export const atmosphereVertexShader = `...`;
export const atmosphereFragmentShader = `...`;
```

### Using ShaderMaterial

```js
import { atmosphereVertexShader, atmosphereFragmentShader } from './shaders/atmosphere.glsl.js';

const atmosMat = new THREE.ShaderMaterial({
  vertexShader: atmosphereVertexShader,
  fragmentShader: atmosphereFragmentShader,
  uniforms: {
    glowColor: { value: new THREE.Color(0x44aaff) },
    intensity: { value: 1.5 },
    power: { value: 2.5 },
  },
  transparent: true,
  blending: THREE.AdditiveBlending,
  depthWrite: false,
});
```

### Per-Instance Animation via Uniform Update

For effects where each instance needs independent animation (star twinkle, neon pulse), pass a `time` uniform and use `BufferAttribute` data for per-vertex variation:

```js
uniform float time;
attribute float phase;
attribute float size;

void main() {
  float twinkle = 0.6 + 0.4 * sin(time * 1.5 + phase * 6.283);
  gl_PointSize = size * (300.0 / -mvPosition.z) * twinkle;
}
```

Update the uniform each frame:

```js
function animate() {
  material.uniforms.time.value += dt;
}
```

### Ship Hull + Effect Shader Reference

For Tron panel-seam grid shaders, atmospheric entry glow shells, and other ship effects, see the `threejs-shader-patterns` skill (Patterns 6-7). The pattern is: base MeshStandardMaterial + slightly-larger ShaderMaterial overlay to avoid z-fighting.

### Vertex Colors in Custom Shaders

Use a named attribute (NOT `color` — Three.js reserves `color` for built-in vertex colors):

```js
geometry.setAttribute('customColor', new THREE.BufferAttribute(colors, 3));

// In shader:
attribute vec3 customColor;
varying vec3 vColor;
void main() { vColor = customColor; ... }
```

This avoids conflict with Three.js's `vertexColors: true` path, which only works with the `color` attribute name + MeshBasicMaterial.

### Key constraints

- **`cameraPosition`** is available in fragment shaders without declaration (Three.js injects it)
- **`normalMatrix`** is only available in vertex shaders
- **All shader code is strings** — no syntax highlighting; catch errors via `vite build`
- **`gl_PointCoord`** is only valid in `THREE.Points` — not Mesh shaders
- **Noise function self-reference bug** — `vec3 f = fract(f * f * (3.0 - 2.0 * f))` fails because `f` is used before it's declared. Always write `vec3 f = fract(p); f = f * f * (3.0 - 2.0 * f);`
- **Layered hull overlays z-fight** when the overlay is the same size as the base mesh. Make overlay 1-3% larger (e.g., `new THREE.BoxGeometry(6.05, 1.55, 12.05)` vs `6, 1.5, 12`)

### Ship Creation with Animated Shader Materials

When a ship needs animated shader materials (hull grid, entry glow, engine pulse), return a compound object rather than a bare group so the caller can drive uniform updates:

```js
export function createCruiser() {
  const group = new THREE.Group();
  const hullMat = new THREE.ShaderMaterial({ ... });
  const entryGlowMat = new THREE.ShaderMaterial({ ... });
  const engineGlows = [mat1, mat2];
  // ... build meshes, add to group ...
  return { group, hullMat, entryGlowMat, entryGlow, engineGlows };
}
```

This lets `main.js` set `cruiserObj.hullMat.uniforms.intensity.value = sin(t * PI)` without reaching into the group's children to find materials by index.

## Engine Trail / Circular Buffer Pattern

For trailing effects behind moving objects (engine exhaust, speeder trails, comet tails) use a `THREE.Line` with a circular buffer of positions and vertex colors that fade older points.

### Setup

```js
const MAX = 60;
const trailPositions = new Float32Array(MAX * 3);
const trailColors = new Float32Array(MAX * 3);
const trailGeo = new THREE.BufferGeometry();
trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPositions, 3));
trailGeo.setAttribute('color', new THREE.BufferAttribute(trailColors, 3));
trailGeo.setDrawRange(0, 0);  // start empty

const trailLine = new THREE.Line(trailGeo, new THREE.LineBasicMaterial({
  vertexColors: true, transparent: true,
  blending: THREE.AdditiveBlending, depthWrite: false,
}));
scene.add(trailLine);

let trailIndex = 0, trailCount = 0;
```

### Update (call every frame)

```js
function updateTrail(pos, tangent) {
  const tp = pos.clone().sub(tangent.clone().multiplyScalar(3));
  trailPositions[trailIndex*3] = tp.x;
  trailPositions[trailIndex*3+1] = tp.y;
  trailPositions[trailIndex*3+2] = tp.z;
  trailColors[trailIndex*3] = 0.2;
  trailColors[trailIndex*3+1] = 0.6;
  trailColors[trailIndex*3+2] = 1.0;
  trailIndex = (trailIndex + 1) % MAX;
  trailCount = Math.min(trailCount + 1, MAX);

  // Rebuild ordered + faded
  for (let i = 0; i < trailCount; i++) {
    const src = (trailIndex - 1 - i + MAX) % MAX;
    const dst = trailCount - 1 - i;
    const alpha = 1 - (i / trailCount);
    trailGeo.attributes.position.array[dst*3] = trailPositions[src*3];
    trailGeo.attributes.position.array[dst*3+1] = trailPositions[src*3+1];
    trailGeo.attributes.position.array[dst*3+2] = trailPositions[src*3+2];
    trailGeo.attributes.color.array[dst*3] = 0.2 * alpha;
    trailGeo.attributes.color.array[dst*3+1] = 0.6 * alpha;
    trailGeo.attributes.color.array[dst*3+2] = 1.0 * alpha;
  }
  trailGeo.attributes.position.needsUpdate = true;
  trailGeo.attributes.color.needsUpdate = true;
  trailGeo.setDrawRange(0, trailCount);
}

function hideTrail() { trailLine.visible = false; trailCount = 0; trailIndex = 0; }
```

### Constraints

- Circular buffer avoids re-allocation
- `setDrawRange()` prevents old points from drawing as a zero-length line to origin
- `needsUpdate = true` on every attribute after mutating the typed array
- 40-80 points for smooth trails; 10-20 for jagged/wake effects

## Per-Instance Animation

When many scene elements need independent animation (neon pulsing at different rates, orbiting traffic lights), store material references + per-instance params in arrays.

### Neon pulse pattern

```js
const items = [];
items.push({ mat, baseOpacity: 0.4, phase: Math.random() * 6.28, speed: 0.5 + Math.random() * 1.5 });

function updateAnim(time) {
  for (const entry of items) {
    const pulse = 0.5 + 0.5 * Math.sin(time * entry.speed + entry.phase);
    entry.mat.opacity = entry.baseOpacity + pulse * 0.5;
  }
}
```

### Orbiting objects (traffic lights, drones)

```js
const data = [];
for (let i = 0; i < count; i++) data.push({
  speed: 2 + Math.random() * 5, height: 5 + Math.random() * 25,
  angle: Math.random() * 6.28, dist: 10 + Math.random() * 80, phase: Math.random() * 6.28,
});

function updateOrbits(time) {
  for (let i = 0; i < count; i++) {
    const d = data[i];
    const a = d.angle + time * 0.1 * d.speed;
    positions[i*3] = Math.cos(a) * d.dist;
    positions[i*3+1] = d.height + Math.sin(time * d.speed + d.phase) * 2;
    positions[i*3+2] = centerZ + Math.sin(a) * d.dist;
  }
  geo.attributes.position.needsUpdate = true;
}
```

### Constraints

- `needsUpdate = true` after modifying BufferAttribute arrays
- Randomize phases (`Math.random() * 6.28`) to prevent visible sync
- Prefer `THREE.Points` + BufferGeometry for 200+ objects (fewer draw calls than individual Meshes)

## Post-Processing with EffectComposer

Bloom, glow, outline, and color-grading effects using the EffectComposer pipeline. Replaces `renderer.render()` with a multi-pass composer.

### Pattern

```js
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

function createComposer(scene, camera, renderer) {
  const composer = new EffectComposer(renderer);

  // Pass 1: normal scene render
  const renderPass = new RenderPass(scene, camera);
  composer.addPass(renderPass);

  // Pass 2: bloom (adjust strength/radius/threshold by taste — user feedback matters!)
  // Typical range: strength 0.3-2.0. Start subtle (0.4) and let user tune up.
  const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    0.4,   // strength — 1.5 is intense for sun glow, 0.4 is subtle
    0.6,   // radius — spread of the glow (0.3 tight - 1.2 wide)
    0.15   // threshold — luminance min; 0.05 everything glows, 0.5 only sun
  );
  composer.addPass(bloomPass);

  // Pass 3: color space correction — CRITICAL in r152+
  const outputPass = new OutputPass();
  composer.addPass(outputPass);

  return composer;
}

// In animation loop — composer entirely replaces renderer.render()
controls.update();
composer.render();     // NOT renderer.render()
```

### Managing bloom per-object
- **Threshold controls selectivity:** low threshold (0.05-0.1) blooms all bright objects including stars and emissive surfaces. Higher threshold (0.3-0.5) only blooms the sun.
- **Bloom strength by object:** use THREE.Layers to exclude objects from bloom if needed. Objects on a different layer can be rendered in a separate pass.
- **Sun gets strong bloom easily** because of its emissive material (`emissiveIntensity: 1.5-2.5` creates high luminance). Dial back to ~1.5 if bloom overexposes the scene.
- **Bloom + PointLight intensity interact:** strong PointLight (2+) + high emissiveIntensity (2.5+) + bloom (1.5) will wash out the scene. When tuning bloom, reduce PointLight (to ~1) and emissiveIntensity (to ~1.5) proportionally.
- **Stars bloom naturally** due to bright white against dark background. Lower threshold to ~0.05 if stars aren't glowing enough.

### Pass ordering rules
1. `RenderPass` first (draws the scene)
2. Effect passes in the middle (bloom, outline, SSR, etc.)
3. `OutputPass` LAST — this is **required** for correct sRGB output in Three.js r152+. Without it, colors appear washed out and bloom looks wrong.

### Resize handling
```js
window.addEventListener('resize', () => {
  composer.setSize(window.innerWidth, window.innerHeight);
});
```

### Pitfalls (import paths & pass ordering)

- **`three/addons/*` is a virtual export alias.** Three.js maps `./addons/*` → `./examples/jsm/*` via package.json. Both paths resolve to the same file, but there is no physical `node_modules/three/addons/` directory.
- **Timer.js is NOT under addons/examples.** It lives at `three/src/core/Timer.js`. Import it from there or use `THREE.Clock` (simpler).
- **EffectComposer creates its own render targets** — it takes over `renderer.setSize()`. Always call `composer.setSize()` on resize, not just `renderer.setSize()`.
- **OutputPass is NOT optional** in r152+. Missing it causes incorrect color space — dark scenes look grey, bloom looks blown out.
- **Composer adds ~1-2ms per pass** to frame time. Bloom may require reducing star count from 3000 to 2000 to maintain 60fps on low-end GPUs.
- **No new npm deps needed:** all passes ship as part of the three package.

## Video Recording from Canvas

Export Three.js animations as MP4/WebM/GIF from the browser using `canvas-capture` (wraps CCapture.js + ffmpeg.wasm). No server-side processing needed.

### Installation

```bash
npm install canvas-capture
```

### Basic Pattern (Hotkey-Triggered)

```js
import { CanvasCapture } from 'canvas-capture';

// Initialize with the renderer's canvas
CanvasCapture.init(renderer.domElement, {
  showRecDot: true,     // red recording indicator
});

// Bind keys: V=video, G=gif, P=PNG snapshot
CanvasCapture.bindKeyToVideoRecord('v', {
  format: CanvasCapture.MP4,  // or CanvasCapture.WEBM
  name: 'dragon-flight',
  fps: 30,
  quality: 0.8,
});

// In animation loop:
function animate() {
  requestAnimationFrame(animate);
  // ... update scene, render ...
  CanvasCapture.checkHotkeys();
  if (CanvasCapture.isRecording()) CanvasCapture.recordFrame();
  composer.render();
}
```

### Manual Control (Automated Export)

For recording a timed cinematic without user interaction:

```js
let recordingDuration = 10; // seconds
let elapsed = 0;

// Start recording
CanvasCapture.beginVideoRecord({
  format: CanvasCapture.MP4,
  name: 'dragon-cinematic',
  fps: 30,
});

// In animation loop:
function animate() {
  clock.update();
  const dt = clock.getDelta();
  elapsed += dt;

  // Advance camera path, update scene...
  updateScene(dt);
  composer.render();
  CanvasCapture.recordFrame();

  if (elapsed >= recordingDuration) {
    CanvasCapture.stopRecord();  // triggers download
    return;  // stop the loop
  }
  requestAnimationFrame(animate);
}
```

### Options

```js
{
  format: CanvasCapture.MP4 | CanvasCapture.WEBM,  // default: MP4
  name: 'Video_Capture',
  fps: 60,                                           // default
  quality: 0.6,                                      // 0-1
  onExport: (blob, filename) => {},                  // handle blob manually
  onExportProgress: (p) => console.log(Math.round(p*100) + '%'),
}
```

### Pitfalls

- **MP4 requires SharedArrayBuffer** — the page must be served with these headers:
  ```
  Cross-Origin-Embedder-Policy: require-corp
  Cross-Origin-Opener-Policy: same-origin
  ```
  Vite dev server does NOT set these by default. Add to `vite.config.js` or use WEBM format instead (no headers needed).
- **WEBM is the safe fallback** — works everywhere, no special headers, slightly larger files.
- **Record every frame, not every other** — missing frames creates visible stutter in the export. Always call `CanvasCapture.recordFrame()` on every animation tick during recording.
- **Stop the animation loop after recording** — if the loop continues, the composer keeps rendering but the capture has stopped, wasting GPU.
- **ffmpeg.wasm loads from unpkg by default** — requires internet for first MP4 export. The WASM binary is ~30MB.
- **Check browser support before showing record UI:**
  ```js
  CanvasCapture.browserSupportsWEBM();  // => true/false
  CanvasCapture.browserSupportsMP4();
  ```

## Feature Catalog

See `references/feature-catalog.md` for a browsable catalog of ~40 Three.js features organized by category (post-processing, physics, lighting, camera, UI, performance, educational), each with complexity ratings, API keywords, and integration notes for the hermes-solar-system project.

**Quick reference for common feature requests:**

| If user asks for... | Feature | Reference section | Skill section |
|:--------------------|:--------|:------------------|:--------------|
| Planet labels with data | CSS2DRenderer | 5. UI / Data Visualization | CSS2D Labels (above) |
| Glow/bloom on the sun | UnrealBloomPass | 1. Post-Processing | Post-Processing with EffectComposer (above) |
| Free-flight camera | FlyControls | 4. Camera Features | Camera Controls: Orbit vs Fly Toggle |
| Asteroid belt with collisions | RapierPhysics | 2. Physics / Animation | — |
| Better starfield (100k+ stars) | InstancedMesh | 6. Performance | InstancedMesh for Large Object Counts |
| Guided solar system tour | Cinematic Camera Paths | 4. Camera Features | Camera Tour Pattern — see `references/camera-tour-pattern.md` |
| Cinematic camera fly-through | CatmullRomCurve3 + phased timeline | 4. Camera Features | Cinematic Camera Paths — see `references/cinematic-camera-paths.md` |
| Thick glowing lines (trails, grids) | THREE.MeshLine | 9-repo collection at `~/Threejs/` | `~/Threejs/THREE.MeshLine/USAGE.md` |
| Click-to-highlight planets | OutlinePass | 1. Post-Processing | — |
| Fast raycasting (complex meshes) | three-mesh-bvh | 9-repo collection at `~/Threejs/` | `~/Threejs/three-mesh-bvh/USAGE.md` |
| SDF 3D text labels at any zoom | troika-three-text | 9-repo collection at `~/Threejs/` | `~/Threejs/troika/USAGE.md` |
| Live parameter tuning (no rebuild) | lil-gui / leva | 9-repo collection at `~/Threejs/` | `~/Threejs/leva/USAGE.md` |
| Cinematic camera with visual editing | three-story-controls | 9-repo collection at `~/Threejs/` | `~/Threejs/three-story-controls/USAGE.md` |
| Better bloom + SSAO + SSR pipeline | pmndrs/postprocessing | 9-repo collection at `~/Threejs/` | `~/Threejs/postprocessing/USAGE.md` |

The catalog was compiled from threejs.org docs via the `safe-web-research` skill's subagent-isolation workflow (see `red-teaming/safe-web-research`).

For high-end graphics technique research covering pmndrs/postprocessing, three-story-controls, Shader.lab, real-time path tracing, and SSAO implementations, see `references/research-high-end-graphics.md`.

## Integration Gotchas — CSS2D + Bloom + Controls

When combining CSS2DRenderer labels, EffectComposer bloom, and OrbitControls in the same scene, several interactions must be handled correctly.

### Render order (critical)
```
function animate():
  1. updatePlanets()          // simulation state
  2. controls.update()        // OrbitControls damping
  3. composer.render()        // bloom pass (NOT renderer.render())
  4. labelRenderer.render()   // CSS2D labels ON TOP
```

If CSS2D labels render BEFORE the composer, they appear underneath the 3D scene.
If controls.update() runs after composer.render(), damping won't work smoothly.

### Window resize (must update all three)
```js
window.addEventListener('resize', () => {
  const w = window.innerWidth;
  const h = window.innerHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  composer.setSize(w, h);          // updates internal render targets
  labelRenderer.setSize(w, h);     // updates overlay dimensions
});
```
Missing any of these causes one layer to be the wrong size.

### pointer-events: none on CSS2D overlay
```css
labelRenderer.domElement.style.pointerEvents = 'none';
```
Without this, the transparent overlay div sits on top of the canvas and swallows all mouse events — OrbitControls won't respond to drag, raycaster won't fire on click.

### EffectComposer replaces renderer.render()
Once you create an EffectComposer, call `composer.render()` instead of `renderer.render(scene, camera)` in the animation loop. Calling both double-renders (waste) and the raw render bypasses the bloom pass.

### composer.render() has no arguments
Basic usage: `composer.render()` (no arguments). Some passes accept a deltaTime parameter — only pass it if the pass documentation explicitly asks for it (e.g., time-based GlitchPass). For bloom, zero arguments is correct.

## Blank Screen Debugging

See `references/blank-screen-debugging.md` for a systematic debugging guide covering:
- The `Timer.connect(document)` API change in Three.js r184
- **Import path errors: `three/addons/misc/Timer.js` does not resolve in r184 — use `three/src/core/Timer.js` instead**
- Checking canvas presence and module loading
- Vite HMR artifacts that confuse error diagnosis
- Common root causes mapped to symptoms
- Full rendering pipeline verification checklist

### Pitfall: Invisible content on dark scenes

When the screen appears black but there are **no JS errors** and the canvas exists, the scene IS rendering — you just can't see anything. Common causes:

- **Background too close to object color** — `scene.background = 0x000005` (near-pure black) + planet `color: 0x1a2a4a` (dark navy) is nearly invisible. Use `0x000a1a` or `0x000511` for a perceptible deep blue background.
- **Emissive too weak** — a planet in dark space needs `emissiveIntensity: 0.3+` to be visible, not 0.1.
- **Camera too far** — planet radius 80 at 400+ units distance with 60° FOV is a small dot. Start camera within 200 units.
- **Ambient light too dim** — `AmbientLight(0x222244, 0.3)` barely illuminates anything. Use `(0x334466, 0.6)` or higher.
- **Atmosphere/glow too subtle** — `opacity: 0.08` is invisible. `0.15-0.2` for a rim glow.

**Rule of thumb for first render:** If you can't distinguish the background color from the objects when looking at CSS-styled HUD text on the same page, the lighting/material setup is too dark. Temporarily boost emissive/ambient until shapes are obvious, then dial back.

## Templates

- `templates/cinematic-flythrough/README.md` — Project scaffold for cinematic on-rails fly-through experiences: file architecture, animation loop pattern, phased timeline, import paths, and first-render troubleshooting.

## Reference Files

- `references/fantasy-organic-scenes.md` — Dragon geometry from primitives, vertex-displaced terrain, InstancedMesh forest, misty dawn atmosphere, third-person follow camera, dawn color palette, and scale reference techniques. Trigger when building fantasy/medieval/organic 3D scenes (creatures, landscapes, forests).

## Custom Particle & Sprite Effects

For visual effects beyond engine trails and bloom — atmospheric entry wake, speed lines, lens flares, cloud layers. These patterns use runtime-generated textures, ring-buffer particle systems, and camera-aligned sprite opacity, all within world-space Three.js.

### Ring-Buffer Particle System (Points-based)

Whereas the Circular Buffer pattern uses `THREE.Line` for trails, this pattern uses `THREE.Points` with per-particle physics simulation (velocity, drag, color fade). Better for particle clouds, wake effects, and sparks.

```js
import * as THREE from 'three';

const MAX_PARTICLES = 200;

export function createParticleEffect(opts = {}) {
  const positions = new Float32Array(MAX_PARTICLES * 3);
  const colors = new Float32Array(MAX_PARTICLES * 3);
  const sizes = new Float32Array(MAX_PARTICLES);

  // Per-particle state arrays
  const lifetimes = new Float32Array(MAX_PARTICLES); // -1 = dead
  const maxLifetimes = new Float32Array(MAX_PARTICLES);
  const velocities = [];  // Array of THREE.Vector3

  let writeHead = 0;

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  geo.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

  const mat = new THREE.PointsMaterial({
    size: 2.5,
    vertexColors: true,
    transparent: true,
    opacity: 0.9,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    sizeAttenuation: true,
  });

  const mesh = new THREE.Points(geo, mat);
  mesh.frustumCulled = false;

  // Init dead
  for (let i = 0; i < MAX_PARTICLES; i++) {
    lifetimes[i] = -1;
    velocities.push(new THREE.Vector3());
    sizes[i] = 0;
  }

  function spawn(worldPos, count = 1) {
    for (let i = 0; i < count; i++) {
      const idx = writeHead % MAX_PARTICLES;
      writeHead = (writeHead + 1) % MAX_PARTICLES;

      lifetimes[idx] = 0;
      maxLifetimes[idx] = 0.5 + Math.random() * 1.0;

      positions[idx * 3]     = worldPos.x + (Math.random() - 0.5) * 0.5;
      positions[idx * 3 + 1] = worldPos.y + (Math.random() - 0.5) * 0.5;
      positions[idx * 3 + 2] = worldPos.z + (Math.random() - 0.5) * 0.5;

      velocities[idx].set(
        (Math.random() - 0.5) * 4,
        (Math.random() - 0.5) * 3,
        -2 - Math.random() * 4
      );

      // Orange/white plasma colors
      const heat = Math.random();
      colors[idx * 3]     = 1.0;
      colors[idx * 3 + 1] = 0.4 + heat * 0.5;
      colors[idx * 3 + 2] = heat * 0.2;

      sizes[idx] = 1.5 + Math.random() * 2.5;
    }
  }

  function update(dt) {
    let anyAlive = false;

    for (let i = 0; i < MAX_PARTICLES; i++) {
      if (lifetimes[i] < 0) continue;

      lifetimes[i] += dt;
      const progress = lifetimes[i] / maxLifetimes[i];

      if (progress >= 1) { lifetimes[i] = -1; sizes[i] = 0; continue; }

      anyAlive = true;

      // Physics: move, drag, fade
      positions[i * 3]     += velocities[i].x * dt;
      positions[i * 3 + 1] += velocities[i].y * dt;
      positions[i * 3 + 2] += velocities[i].z * dt;
      velocities[i].multiplyScalar(1 - dt * 1.5);  // drag

      const brightness = 1 - progress;
      sizes[i] = (1.0 + (brightness) * 2.5) * brightness;
      colors[i * 3] = 1.0;
      colors[i * 3 + 1] = 0.6 * brightness;
      colors[i * 3 + 2] = 0.15 * brightness;
    }

    geo.attributes.position.needsUpdate = true;
    geo.attributes.color.needsUpdate = true;
    geo.attributes.size.needsUpdate = true;

    mesh.visible = anyAlive;
  }

  return { update, mesh, spawn };
}
```

### Procedural CanvasTexture for Sprite Effects

Generate streak, glow, and ghost-ring textures at runtime using the Canvas API. No external assets needed. Useful for speed lines, lens flares, and particle glow sprites.

```js
// Streak texture (speed lines)
function makeStreakTexture() {
  const w = 64, h = 16;
  const canvas = document.createElement('canvas');
  canvas.width = w; canvas.height = h;
  const ctx = canvas.getContext('2d');
  const gradient = ctx.createLinearGradient(0, h/2, w, h/2);
  gradient.addColorStop(0, 'rgba(0,0,0,0)');
  gradient.addColorStop(0.15, 'rgba(0,200,255,0.8)');
  gradient.addColorStop(0.3, 'rgba(200,255,255,1)');
  gradient.addColorStop(0.5, 'rgba(255,255,255,0.6)');
  gradient.addColorStop(0.7, 'rgba(200,255,255,0.3)');
  gradient.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, w, h);
  return new THREE.CanvasTexture(canvas);
}

// Soft glow texture (lens flare, engine glow)
function makeGlowTexture() {
  const size = 128;
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d');
  const cx = size/2, cy = size/2;
  const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, size/2);
  gradient.addColorStop(0, 'rgba(255,255,255,1)');
  gradient.addColorStop(0.1, 'rgba(200,230,255,0.6)');
  gradient.addColorStop(0.3, 'rgba(100,180,255,0.2)');
  gradient.addColorStop(0.6, 'rgba(50,100,200,0.05)');
  gradient.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, size, size);
  return new THREE.CanvasTexture(canvas);
}

// Ghost ring texture (lens flare)
function makeGhostTexture() {
  const size = 64;
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d');
  const cx = size/2, cy = size/2;
  const gradient = ctx.createRadialGradient(cx, cy, size*0.15, cx, cy, size*0.45);
  gradient.addColorStop(0, 'rgba(100,200,255,0)');
  gradient.addColorStop(0.3, 'rgba(100,200,255,0.3)');
  gradient.addColorStop(0.5, 'rgba(150,220,255,0.5)');
  gradient.addColorStop(0.7, 'rgba(100,200,255,0.2)');
  gradient.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, size, size);
  return new THREE.CanvasTexture(canvas);
}

// Usage with SpriteMaterial
const mat = new THREE.SpriteMaterial({
  map: glowTex,
  blending: THREE.AdditiveBlending,
  transparent: true,
  opacity: 0,
  depthWrite: false,
  color: new THREE.Color('#44aaff'),
});
const sprite = new THREE.Sprite(mat);
sprite.scale.set(12, 12, 1);
scene.add(sprite);
```

**Pitfall:** CanvasTexture needs to be created AFTER `document.createElement('canvas')` works (not in Node/SSR context). The texture is immutable after creation — recreate or use `needsUpdate = true` if modifying the canvas after initial render.

### Camera-Aligned Sprite Opacity

For effects like lens flare that should appear only when the camera looks toward a specific world-space source (planet, beacon, sun):

```js
function updateFlare(camera, sourceWorldPos, sprites, materials, maxOpacity) {
  const fwd = new THREE.Vector3();
  camera.getWorldDirection(fwd);

  const toSource = new THREE.Vector3()
    .copy(sourceWorldPos)
    .sub(camera.position)
    .normalize();

  // Alignment: 1 = dead center, 0 = 90° off, -1 = behind
  const alignment = Math.max(0, fwd.dot(toSource));

  // Fade in only when alignment > ~0.85 (within ~30° of center)
  const opacityFactor = Math.pow(Math.max(0, (alignment - 0.85) / 0.15), 2);
  const opacity = opacityFactor * maxOpacity;

  for (const mat of materials) {
    mat.opacity = opacity;
  }
}
```

**Key parameters:** `0.85` threshold means the effect appears ~30° from center. `0.15` range controls how quickly it fades in. Square the normalized value for a smooth ramp.

### Phase-Gated Effect Lifecycle

When building a cinematic timeline with multiple phases, create all effects upfront and activate/deactivate them per phase. This avoids creating/disposing objects during playback (which causes GC pauses).

```js
// 1. Create all effects upfront (in setup)
const entryParticles = createEntryParticles();
const speedLines = createSpeedLines();
const lensFlare = createLensFlare(scene);

// 2. Call frame-level updates unconditionally (cheap when inactive)
function animate() {
  entryParticles.update(dt);
  speedLines.update(dt, camera);

  const phase = getPhase(t);
  if (phase === 'cruiser') {
    entryParticles.setActive(true);
    entryParticles.spawn(worldPos, spawnCount);
    lensFlare.update(camera);   // always on, drives its own opacity
  } else if (phase === 'speeder') {
    entryParticles.setActive(false);
    speedLines.setActive(true);
    speedLines.spawnAroundCamera(camera, 5);
  } else {
    entryParticles.setActive(false);
    speedLines.setActive(false);
  }
}

// 3. Each effect's setActive() kills all existing particles, hides mesh
function setActive(val) {
  active = val;
  if (!val) {
    mesh.visible = false;
    // Reset all particle lifetimes
    for (let i = 0; i < MAX; i++) lifetimes[i] = -1;
  } else {
    mesh.visible = true;
  }
}
```

**Key constraint:** The particle system's `update()` must be called every frame regardless of active state — it handles its own visibility. Effect activation should only control spawning and mesh visibility, not the update call itself.

### FBM Cloud Layer (Noise Shader Variant)

A translucent sphere with 4-octave FBM noise, rotating independently from the planet for parallax. The noise samples from 3D position + time drift.

```js
// vertex shader: pass vPosition
// fragment shader:
float fbm(vec3 p) {
  float value = 0.0;
  float amplitude = 0.5;
  float frequency = 1.0;
  for (int i = 0; i < 4; i++) {
    value += amplitude * noise3d(p * frequency);
    frequency *= 2.0;
    amplitude *= 0.5;
  }
  return value;
}

void main() {
  vec3 samplePos = vPosition * 0.15 + vec3(time * 0.008, 0.0, time * 0.005);
  float n = fbm(samplePos);
  float cloud = smoothstep(cloudCoverage, 1.0, n);
  // Edge fade to prevent pop-in at sphere silhouette
  vec3 norm = normalize(vPosition);
  vec3 viewDir = normalize(vPosition - cameraPosition);
  float rim = 1.0 - abs(dot(viewDir, norm));
  float edgeFade = smoothstep(0.0, 0.5, rim);
  float alpha = cloud * cloudDensity * edgeFade;
  if (alpha < 0.01) discard;
  gl_FragColor = vec4(cloudColor, alpha);
}
```

**Key constraint:** Use `smoothstep(coverage, 1.0, n)` to remap the noise so only the brightest bands show — this creates cloud wisp shapes rather than solid noise. `coverage` around 0.4-0.5 produces banded cloud layers.

### Scene Transition Fades (CSS Overlay + Phase Detection)

For cinematic on-rails experiences with multiple phases, smooth fade-to-black transitions between phases eliminate jarring cuts. Pattern: a full-screen black overlay controlled by CSS transitions, triggered on phase changes.

**HTML** — add the overlay div in `index.html`:

```html
<div id="fade-overlay"></div>
```

**CSS** — style the overlay with a transition on opacity:

```css
#fade-overlay {
  position: fixed;
  inset: 0;
  background: #000;
  pointer-events: none;
  opacity: 0;
  z-index: 50;
  transition: opacity 0.3s ease;
}
#fade-overlay.active { opacity: 1; }
```

**JS** — detect phase changes in the animation loop and trigger the fade:

```js
const fadeOverlay = document.getElementById('fade-overlay');
let prevPhase = 'intro';

function triggerFade(callback) {
  fadeOverlay.classList.add('active');
  setTimeout(() => {
    fadeOverlay.classList.remove('active');
    if (callback) callback();
  }, 350); // 300ms fade out + 50ms hold → fade in
}

// In animation loop, after computing phase:
if (phase !== prevPhase) {
  prevPhase = phase;
  triggerFade();
}
```

**Key constraints:**

- **CSS transition handles visual smoothness**, not JS interpolation — the `transition: opacity 0.3s ease` on the overlay is what actually animates. JS only toggles `.active`.
- **Phase detection is a simple inequality check** — `phase !== prevPhase` catches all transitions. Initialize `prevPhase` to the first phase value to avoid a spurious fade at startup.
- **Fade duration (300ms) + hold (50ms) = 350ms total**, which is fast enough to not feel sluggish but long enough to mask the cut. Tune the `transition` CSS and the `setTimeout` delay together.
- **`pointer-events: none`** on the overlay ensures click/keyboard events (spacebar skip) still work through the black screen.
- **Does not interfere with other systems** — the overlay is pure DOM, separate from Three.js. Works alongside bloom, shaders, and particles.

**Pitfalls:**
- If the overlay's `z-index` is higher than the loading screen, it may block the loading screen. Set `z-index` relative to other overlays (e.g., `50` for fades, `100` for loading).
- The `triggerFade` function uses a fixed `setTimeout` delay — if the user's system is under heavy load, 350ms may not be enough for the CSS transition to complete. For safety-critical sync (e.g., UI state changes on callback), increase to 500ms.

## Verification Checklist

- [ ] `npx vite build` succeeds with 0 errors (catches import path issues before runtime)

### Pitfall: `vite build` flagged as long-lived process

The terminal tool may flag `npx vite build` as a long-lived server process and refuse it in foreground mode. Workarounds (try in order):

1. `./node_modules/.bin/vite build` — bypasses npx wrapper entirely
2. `execute_code` with Python subprocess:
   ```python
   import subprocess
   r = subprocess.run(['./node_modules/.bin/vite', 'build'], capture_output=True, text=True, timeout=30)
   print(r.stdout, r.stderr)
   ```
3. Run with `background=true` + `notify_on_complete=true`, then `process(action="log")` to read output

- [ ] `npx vite --host 127.0.0.1` starts without errors
- [ ] Browser console: no JS errors (ignore harmless Vite HMR WebSocket reconnection errors)
- [ ] Three.js Timer imported correctly (from `three/src/core/Timer.js`, not from `addons/misc/`)
- [ ] Objects animate with delta-time-based motion
- [ ] OrbitControls respond to drag/scroll
- [ ] Window resize maintains correct aspect ratio
- [ ] UI controls modify simulation state without errors
