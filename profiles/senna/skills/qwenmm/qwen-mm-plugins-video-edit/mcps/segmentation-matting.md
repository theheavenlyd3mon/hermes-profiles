# Segmentation / Subject Matting

Use this when an edit needs to isolate people, objects, UI regions, or foreground subjects for compositing, masking, background replacement, text-behind-subject effects, PiP emphasis, or reveal transitions.

## Role

Segmentation/matting is an **asset preparation step**, not a primary edit engine.

Typical chain:

```text
source image/video
→ segmentation / matting tool
→ mask or alpha foreground asset
→ FFmpeg or HyperFrames compositing
→ high-FPS/visual review
```

## Related Tools

| Tool | Role |
|------|------|
| `segmentation` | Text-prompted object/subject mask generation, backed by SAM3 server |
| `grounding` | Locate objects/people with bounding boxes before segmentation |
| `read_image` | Inspect static masks, overlays, and cutout quality |
| `read_video` | Inspect matting stability across time for video foregrounds |
| `vision_chat` | Second-opinion review for mask quality, edge artifacts, and compositing naturalness |

## Use When

- Isolating a person or object from an image/video
- Creating text-behind-subject effects
- Placing a person in front of a designed background
- Creating keyframed spotlight/mask effects
- Creating PiP or cutout layers
- Removing or replacing a background
- Building a transition based on a subject or shape mask

## Do Not Use When

- A simple crop/rectangle overlay is enough
- The source subject is too small, heavily blurred, or heavily occluded
- The edit cannot tolerate edge errors and no proper matting model is available
- The segmentation server/tool is unavailable and only a rough polygon fallback exists

## Availability Requirements

`segmentation` requires a SAM3 server. Pass the server explicitly or configure:

```text
SAM3_SERVER_URL=http://host:port
```

If the tool returns a server-missing or timeout error, do not claim segmentation succeeded. Report the blocker and choose one of:

- retry on a smaller image
- simplify the prompt (`all people`, `the person`, `the object`)
- segment subjects separately and merge masks
- **local rembg fallback** (verified working in this workspace): no text
  prompting, but solid for person/foreground cutouts —
  `python -c "from rembg import remove, new_session; ..."` with the
  `u2net_human_seg` session for people (`u2netp` for speed); same
  quality gates below apply before use
- use a rough polygon mask only as a workflow test, clearly labeled as non-production

`grounding` may require `DASHSCOPE_API_KEY` depending on runtime configuration.

## Output Types

Useful segmentation/matting outputs include:

- Mask metadata (bbox, area, score, mask id)
- Mask preview overlay image
- Binary or grayscale mask image
- Transparent foreground PNG/WebP
- Alpha video / matte video for video foregrounds
- Foreground video with alpha (e.g., WebM VP9 alpha or ProRes 4444, if supported)

## Image Cutout Workflow

1. Read the image with `read_image`.
2. Run `segmentation` with a precise prompt.
3. Inspect the mask overlay.
4. If the mask is too broad/narrow, retry with a simpler or more specific prompt.
5. Create transparent foreground only after the mask is visually acceptable.
6. Verify the transparent output with `read_image` against a contrasting background.

## Video Matting Workflow

For video, do not assume one good frame means the sequence is usable.

1. Identify key motion windows with `read_video`.
2. Test segmentation/matting on representative frames first.
3. If producing a video matte, inspect at higher FPS around motion, hair, hands, fast gestures, and occlusions.
4. Check for temporal flicker, edge crawl, missing limbs/fingers, and background leakage.
5. Only then apply to a longer segment.

## Quality Checks

A matte/cutout passes only if:

- Subject boundaries are reasonably accurate
- Hair/hands/edges are not obviously chopped off
- The mask does not include large unintended background regions
- Edges are not harsh unless stylistically intended
- No visible background halo, green/white/black fringe, or sticker-like edge remains
- For video: mask is temporally stable and does not flicker
- Composited foreground matches the new background's scale, color, light direction, and softness

## Common Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Background included in cutout | prompt too broad, SAM mask too large | retry with more specific prompt or use grounding first |
| Missing hands/hair | subject detail too fine or motion blur | higher-res source, softer edge, better matting model |
| Flickering video edges | frame-by-frame mask inconsistency | temporal smoothing or video matting model |
| Person looks like a sticker | no shadow/light/color integration | add shadow, color match, light wrap, grain, or softer edge |
| Tool timeout | server busy, cold model, large image | downscale image, simplify prompt, retry later |

## Evidence Template

```markdown
**Matting evidence:**
- `segmentation` prompt: "all people"
- Overlay preview: /abs/path/mask_overlay.png
- Cutout output: /abs/path/foreground.png
- `read_image` check: 0 visible tofu/text issues, foreground includes both people, background leakage near right curtain remains — revise before production
```
