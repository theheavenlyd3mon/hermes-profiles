---
name: threejs-engine-trail
description: "Glowing engine trail for ships in Three.js — circular buffer of N positions rendered as a gradient Line with vertex colors that fade from bright to transparent."
version: 1.0.0
author: Senna
tags: [threejs, effects, particles, trail, engine]
---

# Three.js Engine Trail

Creates a glowing trail behind a moving object using a circular buffer of recent positions, rendered as a `THREE.Line` with per-vertex color gradient.

## How It Works

1. Store the last N positions in a circular buffer
2. Each frame, overwrite the oldest position with the current position
3. Rebuild the line geometry: order points from oldest→newest, fade alpha from 0→1
4. Use additive blending for a glowing look

## Full Implementation

### Setup
```js
const TRAIL_LENGTH = 60;  // number of stored positions
const trailPositions = new Float32Array(TRAIL_LENGTH * 3);
const trailColors = new Float32Array(TRAIL_LENGTH * 3);
const trailGeo = new THREE.BufferGeometry();
trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPositions, 3));
trailGeo.setAttribute('color', new THREE.BufferAttribute(trailColors, 3));
trailGeo.setDrawRange(0, 0);  // start empty

const trailMat = new THREE.LineBasicMaterial({
  vertexColors: true,
  transparent: true,
  blending: THREE.AdditiveBlending,
  depthWrite: false,
});
const trailLine = new THREE.Line(trailGeo, trailMat);
scene.add(trailLine);

// State
let trailIndex = 0;
let trailCount = 0;
```

### Update Every Frame
```js
function updateTrail(shipPosition, shipDirection) {
  // Position is slightly behind the ship (at the engine)
  const trailPos = shipPosition.clone().sub(shipDirection.clone().multiplyScalar(3));

  // Write to circular buffer
  trailPositions[trailIndex * 3] = trailPos.x;
  trailPositions[trailIndex * 3 + 1] = trailPos.y;
  trailPositions[trailIndex * 3 + 2] = trailPos.z;

  // All entries get full color; gradient applied during rebuild
  trailColors[trailIndex * 3] = 0.2;     // R
  trailColors[trailIndex * 3 + 1] = 0.6; // G
  trailColors[trailIndex * 3 + 2] = 1.0; // B  ← cyan

  trailIndex = (trailIndex + 1) % TRAIL_LENGTH;
  trailCount = Math.min(trailCount + 1, TRAIL_LENGTH);

  // Rebuild ordered line: oldest → newest, with alpha gradient
  const posAttr = trailGeo.attributes.position;
  const colAttr = trailGeo.attributes.color;
  for (let i = 0; i < trailCount; i++) {
    const srcIdx = (trailIndex - 1 - i + TRAIL_LENGTH) % TRAIL_LENGTH;
    const dstIdx = trailCount - 1 - i;

    // Position
    posAttr.array[dstIdx * 3] = trailPositions[srcIdx * 3];
    posAttr.array[dstIdx * 3 + 1] = trailPositions[srcIdx * 3 + 1];
    posAttr.array[dstIdx * 3 + 2] = trailPositions[srcIdx * 3 + 2];

    // Color with fade: oldest (i=trailCount-1) → transparent, newest (i=0) → bright
    const alpha = 1 - (i / trailCount);
    colAttr.array[dstIdx * 3] = 0.2 * alpha;
    colAttr.array[dstIdx * 3 + 1] = 0.6 * alpha;
    colAttr.array[dstIdx * 3 + 2] = 1.0 * alpha;
  }
  posAttr.needsUpdate = true;
  colAttr.needsUpdate = true;
  trailGeo.setDrawRange(0, trailCount);
}
```

### Show/Hide Helper
```js
function showTrail() {
  trailLine.visible = true;
}

function hideTrail() {
  trailLine.visible = false;
  trailCount = 0;
  trailIndex = 0;
}
```

## Color Customization

```js
// Engine flame (orange)
trailColors[idx] = { r: 1.0, g: 0.4, b: 0.1 };

// Ion trail (purple)
trailColors[idx] = { r: 0.6, g: 0.2, b: 1.0 };

// Speedster (cyan)
trailColors[idx] = { r: 0.2, g: 0.6, b: 1.0 };

// Afterburner (white → fade)
trailColors[idx] = { r: 1.0, g: 1.0, b: 1.0 };
```

## Advanced: MeshLine Upgrade

When you need **thicker, stylized lines** (engine exhaust, neon edges, Tron grids), the circular buffer + `LineBasicMaterial` approach is limited to 1-2px width. Upgrade to `THREE.MeshLine` for world-unit width, tapering, and texture mapping:

```bash
npm install three.mesh.line
```

```js
import { MeshLine, MeshLineMaterial, MeshLineRaycast } from 'three.mesh.line';

// Replace the BufferGeometry + LineBasicMaterial with MeshLine:
const line = new MeshLine();
line.setPoints(trailPositions); // use same circular buffer positions!

const material = new MeshLineMaterial({
  lineWidth: 0.5,            // world units, not pixels
  color: new THREE.Color(0x0066ff),
  transparent: true,
  opacity: 0.8,
  blending: THREE.AdditiveBlending,
  depthWrite: false,
  // Optional: use alphaMap for gradient glow along the line
});

const mesh = new THREE.Mesh(line, material);
mesh.raycast = MeshLineRaycast; // enables click selection
```

**When to upgrade:** Your current circular buffer approach is perfect for simple, thin trails. Switch to MeshLine when you want: variable width (wider near engine, narrower at tail), texture-mapped glow, or selectable trailing objects.

## Performance Notes

- **Trail length vs FPS:** Keep at 30-60 points. More = smoother but costs more GPU bandwidth.
- **Update cost:** Rebuilding the ordered arrays costs O(N) per frame. For TRAIL_LENGTH=60, it's negligible.
- **Additive blending** means older transparent segments still cost GPU fill rate. Keep trailCount reasonable.
- **LineBasicMaterial** is the cheapest option. For glow effects, consider `LineDashedMaterial` or custom shader.

## Pitfalls

1. **Circular buffer ordering** — the buffer stores newest at `trailIndex`, oldest at `trailIndex + 1`. The rebuild loop reads in reverse order to output oldest→newest.
2. **Trail at rest** — when the ship isn't moving, the trail bunches up in one spot. Either hide the trail or only update when velocity > threshold.
3. **Direction vector** — the trail offset `* 3` behind the ship should match the ship's scale. For larger ships, increase the multiplier.
4. **Initial frame** — on first frame, trailCount=0, so `trailGeo.setDrawRange(0, 0)` renders nothing. The trail appears over ~60 frames as it fills.
5. **BufferGeometry needsUpdate** — forgetting `.needsUpdate = true` on position and color attributes is the most common bug. The trail will silently render nothing.

## Verification

- [ ] Trail appears behind ship when moving
- [ ] Trail fades smoothly from bright to transparent
- [ ] No visual artifacts when trail wraps in circular buffer
- [ ] Hide/show works correctly
- [ ] Performance stays above 50fps on target hardware
