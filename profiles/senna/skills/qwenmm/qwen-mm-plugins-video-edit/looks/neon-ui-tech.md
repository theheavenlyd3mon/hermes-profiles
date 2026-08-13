# Look — Neon UI Tech (dark-field product promo)

Workspace-proven recipe (distilled from the reviewed asset pack
`assets/atom-packs/tech-promo-neon-ui/` — README + atoms.json +
preview, each atom user-reviewed individually). For premium, restrained,
futuristic product films: AI, SaaS, data platforms, dev tools, smart
hardware.

## Visual DNA

- Near-black field carrying a FEW glowing elements — never a wall of cyber
  grids, particle storms or long subtitles.
- Neon gradient strokes (blue / purple / pink / cyan, sparing fluorescent
  green); every color serves an "edge of light" or a focus point.
- Copy is 1–3 abstract value words (`Focused`, `Smart Focus`,
  `Giving Space`) — never sentences.
- Cursor, selection box, rounded pill, data path, node network and logo
  lockup all imply "the product is being operated".
- Motion vocabulary: light draw-on, morph expansion, cursor guidance, scan
  lock-on, zoom in/out, brief flashes.

## Atoms (user-reviewed status)

| Atom | Status | Use for | Key implementation |
|------|--------|---------|--------------------|
| `neon-line` light draw-on | recommended | 0.5–1.5s "interface is born" opener; product outline, data path, logo frame, section divider | SVG path draw (dasharray/dashoffset), gradient stroke, soft bloom |
| `cursor-pill` activation | usable — cursor MUST truly land on the button | 1s beats between feature points; abstract value words | pill expands, cursor travels to the end button, spark + slight press |
| `focus-scan` lock-on | reworked — NO eye glyph, abstract scan only | AI retrieval / smart focus / scan-recognize | scan ring rotates, target morphs circle→rounded square, sweep line, short word lands |
| `orbit-dots` network | needs enhancement — a plain dot ring is banned | ecosystem / data hub / collaboration | perspective-tilted ring, pulsing core, dashed spokes, one signal dot orbiting |
| `selection-space` expand | strongly recommended | hero product-UI beat; editor/design tools; the zoom in/out camera feel is the point | thin selection line grows to a region, corner handles appear, cursor nudges, push-in/pull-back |
| `brand-lockup` close | recommended | ending logo + tagline + product name | a faint light line converges into the symbol, then the name; design 2–3 closing intensities |

## Assembly pattern (20–40s piece)

neon-line opener (0–3s) → cursor-pill first value word (3–8s) →
focus-scan AI beat (8–14s) → orbit-dots ecosystem (14–20s) →
selection-space hero UI with zoom feel (20–30s) → brand-lockup (30–36s).

## Not for

- Casual/vlog/food registers (this is a product-film vocabulary).
- Pieces built on real footage — this look is a designed-frames look.

## Precedents & known pitfalls (from review)

- Eye graphics as the AI-focus metaphor: rejected — reads like a logo, not
  premium. Use abstract scan ring + target frame + beam.
- Interactive effects must LAND: a cursor that only gets near its target
  reads as broken; the arrow tip ends ON the button.
- Orbit ring with dots only = generic; must add connections, data flow or
  depth.
- Don't fill the dark field with dense subtitles — short words + few UI
  elements read more premium.

## Implementation route

HyperFrames composition (SVG stroke draw + GSAP, spring presets from
`craft/motion-recipes.md`); asset quality per `[no-placeholder-assets]`.
Canonical prototype pack with per-atom parameters:
`assets/atom-packs/tech-promo-neon-ui/` (atoms.json is the
machine-readable recipe; preview.html is the human review page).
