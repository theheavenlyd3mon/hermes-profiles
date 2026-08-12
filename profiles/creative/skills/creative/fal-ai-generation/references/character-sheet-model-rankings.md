# Character Sheet Model Rankings — 6-Model Shootout (2026-07-29)

Test character: "Eldran" — 19yo male high elf warrior/scout, platinum hair, amber eyes, slate-blue tunic, leather gear, longsword + dagger. Same optimized prompt across all models. Full results at `~/character designs/model-test-eldran/`.

## Final Rankings

| Rank | Model | Score | Text | Layout | Consistency | Time | Cost |
|------|-------|-------|------|--------|-------------|------|------|
| 1 | **Nano Banana Pro** | 8/10 | Clean, readable | Every panel ✅ | Strong | 25s | ~$0.04-0.05 |
| 2 | **GPT-Image 1.5** | 7.5/10 | Best (9.5/10) | Missing eye panel | Strong | 52s | ~$0.04-0.08 |
| 3 | **Seedream 4.5** | 7.5/10 | Typos | Most complete | Hair conflicts | 25s | ~$0.03-0.04 |
| 4 | **Recraft V4 Pro** | 7/10 | Garbled label | Complete, mislabeled | 3 sword designs | 24s | mid |
| 5 | **FLUX.2 Pro** | 6.5/10 | Excellent | Only front/back | Very good | 34s | mid |
| 6 | **Ideogram V3** | 5.5/10 | Gibberish | Missing palette/stats | Moderate | 16s | mid |

## Per-Model QA Notes

### Nano Banana Pro (`fal-ai/nano-banana-pro`) — WINNER
- Only model that delivered ALL panels: front, back, 4 head angles, eye macro, hair breakdown, clothing details (collar/belt/bracer), weapon breakdown (sword + hilt close-up + scabbard + dagger), 9-swatch palette, 7-field info block
- Included orthographic height guide-lines between front/back views (proper production touch)
- Text: crisp black serif caps, all correctly spelled, high contrast
- Minor gaps: no material/prop annotations or hex values on swatches; collar clasp detail not clearly visible on full-body; hero sword render more decorated than held sword; dagger not shown sheathed on body
- Payload: `{"prompt": "...", "image_size": {"width": 1536, "height": 1024}}`

### GPT-Image 1.5 (`fal-ai/gpt-image-1.5`)
- Best text rendering of any model — flawless serif labels, zero garbling
- Clean professional grid with proper rules
- Missing: "EYE CLOSE-UP" header present but contains weapon art instead; "BACK VIEW" is actually 3/4 front
- **CRITICAL PAYLOAD QUIRK:** `image_size` must be a STRING (`"1536x1024"`), NOT a dict. Only accepts `"1024x1024"`, `"1536x1024"`, `"1024x1536"`. Dict format returns HTTP 422.
- Slowest render (52s)

### Seedream 4.5 (`fal-ai/bytedance/seedream/v4.5/text-to-image`)
- Most complete layout — every requested panel physically present
- Beautiful painterly quality, strong material rendering
- Eye close-up actually present (amber iris with slit pupil)
- Text typos: "SLEENGER" (slender), "ATHETIC" (athletic) — not garbled but not clean
- Hair inconsistency: front views show loose hair, back/profile show undercut+braid (two different hairstyles)
- Weapon panel has extra daggers not matching on-body props
- Cheapest option (~$0.03/img)

### Recraft V4 Pro (`fal-ai/recraft/v4/pro/text-to-image`)
- Complete panel set physically present
- Garbled label: "BELTHICLO8ANE" (should be bracer lacing)
- Swapped panels: "BRACER LACING" tile shows an eye macro; eye macro tile shows bracer lacing
- Three conflicting longsword designs (held vs small callout vs large callout)
- Face differs between body render (masculine/sharp) and head studies (softer/freckles)
- Good costume consistency front-to-back

### FLUX.2 Pro (`fal-ai/flux-2-pro`)
- Gorgeous art quality (8.5/10 rendering) but fundamentally wrong assignment
- Only produced front/back turnaround + palette + info text
- Missing: head studies, detail panels, weapons, eye close-up, hair detail
- Character shown SHIRTLESS (base-mesh convention) — ignored the costume description
- Excellent text and cross-panel consistency for what it did render
- Best for: single hero renders, not structured sheets

### Ideogram V3 (`fal-ai/ideogram/v3`)
- Despite typography reputation, multi-panel format overwhelmed it
- Panel captions are garbled pseudo-text (unreadable)
- Subtitle typo: "GIGH" instead of "HIGH"
- Missing: color palette, stat block (only name present)
- Rear view is 3/4, not true orthographic
- Head studies inconsistent (braids appear/disappear between panels)
- Best for: single-image compositions with text (posters, covers), NOT multi-panel sheets

## Recommended Workflow

1. **Draft/explode:** Seedream 4.5 (cheapest, fastest, gets all panels down)
2. **Finalize:** Nano Banana Pro (best all-rounder) or GPT-Image 1.5 (when text labels must be perfect)
3. **Avoid for sheets:** FLUX.2 Pro, Ideogram V3 (both fail at multi-panel structure)

## Prompt Templates

User's templates live at `~/character designs/`:
- `prompt-template-original.md` — ChatGPT original (works well with GPT-Image 1.5)
- `prompt-template-fal-optimized.md` — adjusted for fal.ai (front-loaded layout, positive phrasing, spatial language)
