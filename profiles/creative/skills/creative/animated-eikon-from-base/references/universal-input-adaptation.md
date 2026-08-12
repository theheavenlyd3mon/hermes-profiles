# Universal input adaptation for animated eikons

Use this reference to adapt `animated-eikon-from-base` to any source image, not just human portraits.

## Core rule

Every eikon needs one dominant terminal-readable subject. The source image may be complex, but the plate should not be. Distill the source into a single glyph-survival avatar.

At 48×24, the question is not “does the image look good?” It is:

1. Can I recognize the subject from silhouette?
2. Can I read 2–4 landmarks?
3. Can I tell the six states apart?
4. Is there enough clean negative space for the rasterizer?

## Classification pass

Before prompting GPT Image 2, classify the input:

- person / face / character
- animal / creature
- robot / mech / device
- object / product / tool
- vehicle / ship / aircraft
- logo / symbol / mark
- landscape / place / building
- abstract art / texture
- style board / UI sheet / mood board

Then choose a subject strategy.

## Subject strategies

### Person / face / character

Crop to bust or head/shoulders. Preserve identity through face planes, eyes/brow/glasses, nose/mouth, jaw/beard/hair, collar/shoulders.

Prompt keywords:

```text
large bright face planes, deep black brow/eye sockets, clear nose bridge, mouth slash, jaw block, hair mass, clean shoulder/collar silhouette, no pores, no tiny wrinkles, no smoke over face
```

### Animal / creature

Use bust or full-body mascot depending on recognizability. Preserve ears/horns, eyes, muzzle/beak, paws/claws/tail, posture.

Prompt keywords:

```text
large readable eyes, oversized ear/horn/muzzle/beak silhouette, simplified fur/feather masses, clear body outline, no habitat clutter, no tiny fur texture
```

### Robot / mech / device

Use a front/3-4 bust or emblematic chassis view. Preserve head/visor/sensor, antennae, shoulders, chest shape, one or two panel seams.

Prompt keywords:

```text
bold chassis silhouette, large visor/sensor, simplified armor plates, one dominant front plane, thick black/white panel cuts, no tiny wires, no small greebles
```

### Object / product / tool

Turn it into an emblematic object icon. Preserve the outer contour and one or two key parts: handle, lens, screen, button, blade, rim, edge.

Prompt keywords:

```text
single centered object icon, thick outer contour, clear front plane, oversized key feature, no packaging, no labels, no tiny reflections
```

### Vehicle / ship / aircraft

Use a 3/4 silhouette or front icon. Preserve wheels/wings/cockpit/grill/hull outline.

Prompt keywords:

```text
strong vehicle silhouette, large wheel/wing/cockpit/grill landmarks, clean high contrast body shape, no road/city/background clutter, no tiny reflections
```

### Logo / symbol / mark

Preserve the primary mark and negative-space cuts. Remove slogans, microtype, gradients, and brand collateral unless the user explicitly asks otherwise.

Prompt keywords:

```text
simplified monochrome mark, preserve dominant logo silhouette and negative space, no slogan, no microtext, no gradients, no brand sheet frame
```

### Landscape / place / building

A landscape cannot animate like a face. Distill it into an iconic scene sigil: skyline, ridge, building, sun/moon, window blocks, one horizon.

Prompt keywords:

```text
single iconic scene silhouette, bold horizon/ridge/building shape, 2-4 large value masses, high contrast negative space, no leaves/noise/texture, no tiny people
```

### Abstract art / texture

Pick the dominant rhythm and reduce to 2–4 bold shapes. Avoid preserving every brushstroke.

Prompt keywords:

```text
distilled abstract sigil, 2-4 dominant shapes, clear rhythm, strong black/white value separation, clean negative space, no fine brush texture
```

### Style board / UI sheet / mood board

Treat as art direction only. Do not import frames, labels, arrows, panels, tiny icons, or dashboard cards. Generate a clean avatar/sigil using the mood and silhouette doctrine.

Prompt keywords:

```text
use supplied board only as art direction: preserve mood, silhouette vocabulary, contrast, and state language; generate one clean centered avatar/sigil; no UI panels, no labels, no arrows, no text
```

## Universal state mapping

| state | person/animal | object/robot/logo/scene |
|---|---|---|
| idle | breathing/resting pose | quiet pulse / stillness |
| listening | lean-in, ear/head turn | sensor/antenna/orientation pulse |
| thinking | head tilt, downward glance | contained scan/orbit/internal glow |
| speaking | mouth/beak movement | signal pulse/light/speaker vibration |
| working | focused scanning/action posture | active-mode pulse/directional energy |
| error | grimace/recoil/glitch behind subject | shake/fracture/glitch behind subject |

Never add readable words to explain the state. The motion/shape must carry it.

## Universal GPT Image 2 prompt skeleton

```text
Use the supplied image as strict identity/shape/style reference. First classify the subject and distill it into one centered terminal eikon avatar/sigil. Preserve the most recognizable 2-4 landmarks: <landmarks>. Create a high-resolution black/white/very-light-gray poster plate, pure clean background, strong silhouette, large value-separated shapes that survive at 48x24 Braille/ASCII. State: <state>. Show <state-specific analogue>. No tiny texture, no busy background, no small readable text, no HUD, no extra characters. If the source is a logo, preserve only the primary mark and negative-space cuts.
```

## Universal Kling prompt skeleton

```text
Animate as <state/action analogue>. Preserve the supplied monochrome plate composition and subject identity exactly. Motion should be controlled but visible at 48x24. Locked camera, no cuts, no zooming out, no extra subjects, no readable text/HUD. Keep background clean. Effects must stay behind/around the subject and not obscure the key landmarks. Return near the starting pose by the final frame for looping.
```

## QA gates

Before Kling spend:

- contact sheet at 240×240 per state
- at least one chafa 48×24 preview
- list the subject class and chosen landmarks in the manifest
- reject plates where the subject only reads full-size

After Kling:

- ffprobe every MP4
- make strips/contact sheet
- inspect for subject drift, text, extra characters, background clutter, and landmark melting
- install only verified state MP4s

## Common universal failures

- Human prompts applied to logos/objects, producing fake faces.
- Logo prompts preserving tiny slogans that turn into terminal noise.
- Landscape prompts preserving detailed scenery instead of a bold skyline/ridge.
- Product shots preserving labels and reflections rather than object contour.
- Animal prompts preserving fur texture but losing ears/muzzle.
- Abstract art prompts preserving every stroke instead of a sigil.

When any of these happens, regenerate plates with fewer shapes and stronger landmarks before animating.
