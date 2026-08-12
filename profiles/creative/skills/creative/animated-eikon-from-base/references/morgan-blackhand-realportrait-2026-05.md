# Morgan Blackhand hyper-real monochrome portrait attempt — 2026-05

## Context

After several high-contrast poster/stencil passes (`glyphbase`, then `facecut`), Lucas suggested an opposite hypothesis: the eikon might work better if the source is a hyper-realistic human-like portrait using the same black/white colour scheme.

This is a valid alternate branch when stencil/vector/icon passes make facial features feel too abstract or lost.

## Candidate produced

- Eikon: `morgan-blackhand-realportrait`
- Workspace: `/home/lucas/.hermes/eikon-work/morgan-blackhand-realportrait-20260521-135438`
- Active source: `/home/lucas/.hermes/eikons/morgan-blackhand-realportrait/source`
- Plate sheet: `/home/lucas/.hermes/eikon-work/morgan-blackhand-realportrait-20260521-135438/bw-plates/contact_sheet.png`
- Video sheet: `/home/lucas/.hermes/eikon-work/morgan-blackhand-realportrait-20260521-135438/preview/loop_preview_contact.jpg`
- Probe: `/home/lucas/.hermes/eikon-work/morgan-blackhand-realportrait-20260521-135438/fal-kling/media_probe.json`

Clean source contents after install:

```text
base.png
idle.mp4
listening.mp4
thinking.mp4
speaking.mp4
working.mp4
error.mp4
```

Verifier output confirmed all six clips: `1440x1440`, `24fps`, `~6.08s`, no state PNG shadows.

## GPT-image-2 plate prompt pattern

Use the supplied base image as strict identity reference. Ask for:

- **Hyper-realistic human cinematic portrait**, not cartoon/anime/vector/stencil.
- Same monochrome palette: pure black background, pale/white face highlights, dark hair/beard/collar, silver-gray tonal skin planes.
- Close-up head and shoulders; face large in frame.
- Rugged veteran features: intense brow, deep eye sockets, clear nose bridge, cheekbones, mouth line, heavy beard/stubble, cigar, swept-back hair with bright white streak, massive high black leather collar.
- Strong lighting: key light across face, hard rim light on hair/collar, deep shadow under brow and beard, visible eyes/eye sockets, readable nose/mouth.
- No smoke over face, scenery, text, logos, HUD, city background.
- High contrast but photographic, preserving real skin texture and cinematic detail.

State deltas used:

```text
idle: neutral cold forward glare, cigar steady, calm menace
listening: slight lean-in and head turn, skeptical attentive eyes
thinking: head tilted down, brow tense, jaw clenched, cigar steady
speaking: mouth open mid-word, cigar angled aside enough to reveal mouth line
working: focused downward aggressive scan, narrowed eyes, tense jaw, minimal abstract backlight only
error: controlled angry recoil/grimace, glitch-like rim light behind silhouette only, face unobscured
```

## Kling prompt pattern

Animate the photographic plate directly; do **not** pre-posterize. Keep motion conservative.

Global suffix:

```text
Short seamless loopable hyper-realistic black-and-white close-up portrait animation. Preserve the supplied human face identity, monochrome palette, pure black background, rugged beard, cigar, swept hair streak, high leather collar, strong facial lighting. Locked camera, no cuts, no zoom out, no text/logos/HUD, no extra characters, no smoke over face. Keep motion controlled and return to starting pose by final frame.
```

Negative prompt:

```text
cartoon, anime, vector, stencil, text, logo, subtitle, hud, extra character, camera cut, zoom out, face melting, deformed face, smoke over face, busy background, color wash
```

Then ping-pong with ffmpeg before install.

## QA result

Pros:

- Much more human and less logo/stencil.
- Facial features are naturally distinct at source/video-preview level.
- Good alternate candidate when user dislikes the abstract facecut look.

Risks:

- The source carries a lot of tonal detail. In final 48×24 monochrome raster, this can collapse into gray/glyph noise.
- `facecut` is safer for glyph survival; `realportrait` may look better only if Studio contrast/symbol settings preserve the photographic planes.

## Operational rule

When Lucas proposes a hyper-realistic branch, build it as a separate comparison eikon and state the tradeoff plainly: prettier/more human source vs. weaker guaranteed 48×24 glyph survival.
