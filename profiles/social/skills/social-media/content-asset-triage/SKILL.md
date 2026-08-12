---
name: content-asset-triage
description: "Triage a folder of AI assets into tiers before drafting."
version: 1.0.0
triggers:
  - "review this folder"
  - "look at what the profile made"
  - "post about these"
  - "which of these should we post"
  - "triage these assets"
metadata:
  hermes:
    tags: [social-media, content, triage, build-in-public, ai-art, review]
    related_skills: [draft-post, brand-review-content, build-in-public, xurl]
---

# Content Asset Triage

Pre-drafting workflow for when the user hands you a folder of AI-generated creative
assets and wants social content "about it." The job is to decide WHAT is postable and
HOW to frame it — not to draft yet. Drafting lives in `draft-post`; this skill feeds it.

## When to Use

- User points at a folder of generated images/art/UI/comics and wants a post or thread.
- A separate creative/agent profile produced a batch of assets for this profile to ship.
- "Which of these should we use?" / "review what it made."

## When NOT to Use

- Single known asset, just needs a caption → `draft-post` directly.
- Quality-checking a written draft → `brand-review-content`.

## Workflow

1. **Confirm the folder before deep-diving.** Users keep several project folders side by
   side (some shelved). If the user says "the folder the profile made," confirm the exact
   path or search broadly first. Do NOT latch onto the first plausible match and invest a
   deep pass in it — wrong folder = wasted work + a correction.
2. **Read any README/index for orientation only.** Then inspect candidates yourself with
   vision_analyze. A folder's suggested ordering reflects what was easy to generate, not
   what's strongest — do not trust it as a quality ranking.
3. **Sort into three tiers** (see `references/ai-asset-triage.md` for the full rubric):
   - Tier 1 — postable as-is (strong concept, clean render, no embarrassing artifacts)
   - Tier 2 — good but needs a small fix first (almost always broken/garbled TEXT)
   - Tier 3 — not showcase-ready (reads as filter/artifact, not craft)
4. **Pick the strategic frame.** Uneven batch → build-in-public workflow angle ("one
   prompt, the agent ran N skills, produced all this"), where variety is the point and
   rough pieces are evidence not liabilities. Uniformly strong batch → quality showcase.
   Default to the workflow angle for skill-demo batches.
   **Differentiated > commoditized:** When the user wants to spotlight favorites, lean
   into skills that produce outputs the audience HASN'T seen before (e.g., braille
   text-to-image, full UI generation from a prompt). Commoditized outputs (AI
   illustrations, comics, pixel art — things any image generator can do) get a one-line
   mention, not spotlight treatment. The framing: "any tool can do X, but THIS surprised me."
5. **Screenshot HTML/UI assets yourself.** Don't rely on the folder having PNGs of HTML
   files. Use headless Chrome: `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
   --headless --disable-gpu --no-sandbox --window-size=1400,900 --screenshot="OUT.png" "file://SRC.html"`.
   See `references/rendering-techniques.md` for font/rendering pitfalls.
5. **Report, then wait for the green light.** Triage → recommend → (user approves) →
   draft → review gate. Never post straight from a triage pass.

## Output Shape

Lead with the honest quality read (the tiers). Call out what the folder's own README got
wrong. Give the strategic recommendation: which images lead, which frame, which need a fix
first. End with options for next step — not a posted artifact.

## Pitfalls

1. **Don't trust the folder's README ranking.** Inspect with your own eyes.
2. **Don't lead with the weakest category.** Skill-demo folders often open with pixel/ASCII
   art because it's easy to generate; those are usually Tier 3.
3. **Don't frame an uneven batch as a quality showcase.** That invites a quality judgment
   you lose. The workflow story is more honest and more defensible.
4. **Don't skip the text check.** Garbled/misspelled text is the #1 AI-artifact tell and
   the thing that gets a post screenshotted and mocked.
5. **Don't post from triage.** This skill is review-gated by design.
6. **Don't assume PNG previews are correct.** Braille/ASCII art PNGs often render as tofu
   boxes due to missing font glyphs. Always check the source .txt and re-render if needed.
   See `references/rendering-techniques.md`.
7. **Don't over-structure the user's voice.** This user writes short, casual, declarative
   sentences. No "First up:" / "Then:" scaffolding. No product-launch energy. Understated
   enthusiasm > exclamation marks. Match their actual tweet history, not a template.

## Related Skills

- `draft-post` — execution layer; draft the actual post once triage + frame are approved.
- `brand-review-content` — voice/quality check on the draft before it ships.
- `build-in-public` — the strategy layer the workflow-angle reframe comes from.
- `xurl` — actually posting to X (only after approval).
