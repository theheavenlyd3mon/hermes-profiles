# Looks — Named Visual Style Recipes

Ammunition for the three-direction gate (`craft/art-direction.md` §3), a menu
users can name directly ("use the paper-collage look"), and a **replication
accelerator**: when a reference video's style DNA matches a card
(`workflows/style-replication.md` Phase 2), the card's implementation route
and known pitfalls become the baseline instead of re-deriving from scratch.
**These are options to draw from when the brief has no reference — never a
mandatory menu.** When the user supplies content, a brand, or a reference,
the design grows from there; do not force a card onto it.

Card format (every card): Visual DNA · Preconditions · Not-for ·
Implementation routes · Precedents & known pitfalls.

## Index

| Look | Mood | Best for | Primary route |
|------|------|----------|---------------|
| `paper-collage.md` | editorial, tactile, witty | intros, B-roll, sticker PiP, concept beats | segmentation + HyperFrames (det.) or gen-image + i2v |
| `freeze-punch-intro.md` | high-energy, personal | character/subject introductions | HyperFrames on footage |
| `film-reel-carousel.md` | nostalgic, structured | multi-clip openings, recaps | HyperFrames |
| `brush-calligraphy.md` | artistic, cultural | title moments, cultural content | gen-image assets + HyperFrames |
| `gallery-ripple.md` | scale + gaze | 20+ homogeneous assets (breadth × depth) | HyperFrames |
| `big-number-stage.md` | bold, declarative | stat moments, section titles, hooks | HyperFrames |
| `neon-ui-tech.md` | premium, restrained, futuristic | dark-field tech/product promos (designed frames) | HyperFrames (SVG draw + GSAP) |
| `prompt-to-product-ui.md` | clean, product-feel, light-field | AI/SaaS prompt-to-UI demo pieces (designed frames) | HyperFrames |

## Selection rules

1. The look must fit the **taste contract** (design read + dials) — a look
   that contradicts the contract is out, however pretty.
2. Check the card's **preconditions** against the actual footage before
   proposing it (e.g. gallery-ripple needs 20+ uniform assets).
3. One look per piece. Mixing looks needs an explicit narrative reason
   recorded in `project.md`.
4. Direction C of the three-direction gate draws from here randomly
   (`date +%S` mod the current number of look cards) to break conservative
   habit.
5. The two designed-frames looks (`neon-ui-tech`, `prompt-to-product-ui`)
   describe pieces with little or no real footage — when a task is PURELY
   that, the `hyperframes` entry skill owns execution and these cards
   contribute the taste contract + atom spec through the handoff
   (`engines/hyperframes.md`).
