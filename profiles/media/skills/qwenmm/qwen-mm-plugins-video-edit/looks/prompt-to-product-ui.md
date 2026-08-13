# Look — Prompt-to-Product UI Showcase (light-field AI demo)

Workspace-proven recipe (distilled from the asset pack
`assets/atom-packs/prompt-to-product-ui/` — sourced from a
reference-video study). Core concept: **a user types a prompt, and the
screen grows a complete, tasteful, in-context product UI.** For AI-product
capability demos, SaaS promos, prompt-to-UI/app showcases.

## Visual DNA

- Warm white / beige / light-sand field — deliberately the OPPOSITE
  temperature of `looks/neon-ui-tech.md`'s dark neon.
- One persistent grammar across the piece: white rounded prompt box + black
  send button + a cursor that never disappears.
- Generated UIs are large-radius cards with light shadows, thin borders,
  layered floating collages — they must read as "the AI is generating
  product prototypes", never as a screenshot wall.
- **Causality rule: every style/scene change is TRIGGERED by an input, a
  click, a slider or an option** — nothing changes on its own.

## Atoms

| Atom | Status | Use for |
|------|--------|---------|
| `prompt-composer` | core motif | opener, scene switches, feature triggers — typed prompt + cursor click on the send button |
| `ui-materialization` | core | the first payoff: product UI assembling layer by layer after the click |
| `floating-product-collage` | core | breadth: multiple UI modules in a layered floating collage |
| `data-dashboard-bloom` | depth beat | dashboards/metric cards/charts lighting up in sequence |
| `style-morph-slider` | depth beat | slider drags → skin/typography/palette morphs live |
| `retro-pixel-ui-mode` | memory spike | blue-field pixel UI as the one deliberate style jolt |
| `mobile-app-focus-reveal` | closer | phone mockup centers up for the ending |

## Assembly pattern (~47s piece)

brand word (0–4s) → prompt-composer types the task (4–10s) →
ui-materialization first product (10–18s) → floating collage breadth
(18–28s) → dashboard-bloom OR style-morph depth (28–36s) →
retro-pixel jolt (36–43s) → mobile focus reveal / brand close (43–47s).

## Not for

- Real-footage pieces and casual/vlog registers.
- Dark moody brand films — that register belongs to
  `looks/neon-ui-tech.md`; don't mix the two fields in one piece.

## Precedents & known pitfalls

- Prompt text too long kills the beat — keep prompts short and legible.
- The cursor must truly hit the send button (same "interactions must land"
  rule as the neon look).
- Generated UIs that look like static screenshots break the fantasy — each
  needs its own materialization motion.

## Implementation route

HyperFrames composition (GSAP + spring presets from
`craft/motion-recipes.md`); UI mock assets are designed frames, held to
`[no-placeholder-assets]`. Canonical prototype pack:
`assets/atom-packs/prompt-to-product-ui/` (atoms.json =
machine-readable recipe; preview.html = review page with per-atom feedback).
