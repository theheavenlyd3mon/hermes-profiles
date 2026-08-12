---
name: image-studio-batch
description: "Generate multiple AI image variants with Hermes Image Studio. Use when the user wants options to choose from, or needs a variety pack for social media."
---

# Image Studio: Batch Generate

Load this skill when the user wants multiple variations of the same
scene or subject. Uses `image_studio_batch` to run parallel generations
with random seeds.

## When to Use

- "Give me a few options for this"
- "Generate some variations"
- "I want to pick the best one"
- Social media content packs (multiple posts from one idea)
- Finding the perfect seed before committing to a final image

## Workflow

1. **Confirm the brief.** Same as single generation — subject, setting,
   mood, preset, aspect ratio.

2. **Decide count.** Default is 4. Recommend:
   - 4 for quick exploration
   - 6 for important assets (article headers, product shots)
   - 8 for variety packs (social media content)

3. **Call `image_studio_batch`** with prompt, count, preset, aspect ratio.

4. **Present the options.** Show each one with its seed and file path.
   Ask which one they want to use or refine.

5. **Optional refinement.** If they like one but want tweaks, use
   `image_studio_generate` with the specific seed from the batch plus
   their changes to the prompt.

## Tips

- Batch is great for finding the right seed for a prompt you plan to
  use repeatedly (same scene, different aspect ratios later)
- Each variant costs ~1 FAL credit — 4 variants cost ~4 credits
- If none of the variants work, improve the prompt rather than running
  more seeds. The prompt is usually the bottleneck, not the seed.
