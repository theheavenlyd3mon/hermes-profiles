# AI Art Brand Consistency

Use this when the brand is an AI-generated visual identity on X/Instagram.
Covers prompt behavior by backend, composition rules for feed cohesion,
and validation gates before publishing.

## Backend Prompt Mapping

| Backend | Prompt Style | CFG | Steps | Notes |
|---|---|---|---|---|
| Local Illumina | Painterly texture words, loose brushwork phrasing | 6–7 | 25–35 | Fast iterations; color-first thinking |
| Cloud Flux | Screenplay-like structure, explicit subject + environment | 3–5 | 20–30 | Better face/identity hold at full precision |
| Local SDXL | Balanced syntax, quality tags at end | 7 | 25–30 | Baseline fallback |

## Prompt DNA Template

Every publishable prompt should contain:
```
[Archetype DNA] + [Scene DNA] + [Light DNA] + [Texture DNA] + [Quality Stack]
```
Keep archetype and lighting stable across a story arc; reroll environments.

## Consistency Stack

- 1–2 LoRAs at 0.4–0.7
- IP-Adapter FaceID for cross-pose character identity
- ControlNet OpenPose/DWPose or Depth for composition lock
- Fixed seed inside a character arc; new seed per scene
- Hires fix with consistent denoise strength

## Composition Rules for Feed Cohesion

- Limit palette to 2–3 hues per frame
- Use dark canvas on 40–60% of posts
- Every image needs one clear focal highlight
- Keep subject centered; avoid hugging edges
- Preserve neutral/low-angle camera reads for 3D handoff later

## Validation Gate Before Publishing

1. No watermark, no signature text in frame
2. No melting anatomy, duplicate fingers, extra limbs
3. Color palette fits established brand hues
4. Aspect ratio cropped for target platform
5. Filename follows convention: `BRAND_S##E##_slug_variant.ext`

## 3D/Bridge Readiness

If final art may become a 3D model:
- One strong key light + one fill
- Clear silhouette read
- Distinct material groupings (metal / cloth / skin)
- Neutral camera angle; centered subject
