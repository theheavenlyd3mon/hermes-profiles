# Higgsfield Platform Reference
Condensed from higgsfield.ai docs, pricing page, and blog (July 2026).

## Plans & Unlimited

| Plan | Price (annual) | Credits/mo | Unlimited |
|---|---|---|---|
| Starter | $19/mo | 270 | No (selected models only) |
| Plus | $47/mo | 1,200 | All models 7-day Unlimited |
| Ultra | $99/mo | 3,000–9,000 | All models 7-day Unlimited |

- 1-day $0 trial available (renews at $59/mo Plus)
- Unlimited = standard queue, 1 concurrent job, no credits deducted
- Credit mode = priority queue, multiple parallel jobs, faster
- Unlimited NOT available via MCP/CLI/Canvas/Supercomputer — web app only
- Unlimited is for personal human use; automation/scripting prohibited

## Video Model Credit Costs (per 5s unless noted)

| Model | 720p | 1080p | 4K |
|---|---|---|---|
| Seedance 2.0 | 22 cr | 45 cr | 110 cr |
| Seedance 2.0 Fast | 17 cr | — | — |
| Kling 3.0 | 7 cr | 8 cr | 30 cr |
| Kling 3.0 Motion Control | 7 cr | 12 cr | — |
| Kling Omni 3 FLF | 5 cr | 6 cr | — |
| Wan 2.6 | 7 cr (480p) / 13 cr | 20 cr | — |
| Sora 2 | 10 cr/4s | — | — |
| Sora 2 Pro | 30 cr/4s | 50 cr/4s | — |
| Veo 3.1 Fast | 11 cr/4s | 11 cr/4s | — |
| Veo 3.1 | 29 cr/4s | 29 cr/4s | — |
| MiniMax Hailuo 2.3 Fast | 4 cr/6s | 7 cr/6s | — |
| Kling 2.5 Turbo | 4 cr | 6 cr | — |

## Image Model Credit Costs

| Model | Cost |
|---|---|
| Nano Banana Pro | 2 cr (4 cr for 4K) |
| Higgsfield Soul 2.0 | 0.12 cr |
| GPT Image 2 | 1 cr |
| FLUX.2 Pro | 1 cr |
| Seedream 5.0 Pro | 1 cr |

## Model Strengths (tested by Higgsfield Prompt Team)

### Seedance 2.0 (ByteDance)
- Best: multi-shot films, ads, action/VFX with synced audio
- Up to 9 reference inputs (images, video, audio) + text
- Physics-aware: cloth, liquid, weight, collisions
- Clips up to 15s, native audio in one pass
- Weakness: credit-heavy (~90 cr/15s 720p), strict moderation, literal interpretation

### Kling 3.0 (Kuaishou)
- Best: character-driven stories, 4K, cheapest per clip
- Multi-shot storyboarding: up to 6 camera cuts per generation
- Voice Binding: consistent voices across 5 languages
- Omni Native Audio: dialogue, SFX, ambience
- Weakness: rewards setup (define shots/refs/voices), less predictable between gens

### Veo 3.1 (Google DeepMind)
- Best: outdoor, atmospheric, large-scale scenes
- Global illumination, weather, wind, depth of field
- Native audio on all tiers (Lite/Fast/Quality)
- 8s cap per generation
- Weakness: credit-intensive (40–70 cr), softens on close-up faces, needs detailed prompting

### WAN 2.7 (Alibaba)
- Best: restyling/"reshoots", product realism
- Video-reference style transfer: keep motion, change world
- Native audio + lip-sync, multi-shot with auto camera transitions
- Weakness: input-dependent, weak from text-only prompts

### MiniMax Hailuo 2.3
- Best: fast short-form, UGC, anime/stylized
- Fast mode needs minimal prompts, holds color/style
- Sharp on-screen text/logos
- Weakness: speed over cinematic control

### Sora 2 (OpenAI) — SUNSETTING
- App shut down April 26, 2026; API ends September 24, 2026
- Best: physics simulation, object permanence
- Migrate to Seedance 2.0 (commercial) or Veo 3.1 (realism)

## Key Platform Features

### Cinema Studio
- Production layer: explicit camera angles, lighting, character placement, shot sequencing
- Cast: generates character sheet (front/side/back) for consistency
- Optical stack: combine film stocks + lens types (e.g. 16mm + anamorphic)
- Multi-axis motion: stack up to 3 simultaneous camera movements
- Script to Scene: describe vision, auto-selects camera/lighting

### Soul ID
- Train persistent character identity from 20+ reference photos
- Works across ALL models and generations on Higgsfield
- Cast = fictional characters (Cinema Studio only); Soul ID = real people (everywhere)

### MCP Server
- URL: `https://mcp.higgsfield.ai/mcp`
- Auth: OAuth (browser sign-in, no API key)
- Exposes 30+ models, async generation with polling
- Supports: text-to-video, image-to-video, video-to-video, multi-reference, Soul Characters
- Also works with: Claude, Cursor, OpenClaw, Hermes Agent, NemoClaw
- Credits consumed per generation (same as web); Unlimited NOT available via MCP

### CLI
- `npm install -g @higgsfield/cli`
- `higgsfield auth login` (browser OAuth)
- Skills: `npx skills add higgsfield-ai/skills`

## Multi-Shot Prompt Pattern (from Cinema Studio guide)

```
Multi-shot editing, [scene description].

Shot 1:
[Lens type]. [Setting description]. [Character action].

Shot 2:
[Camera movement]. [Action beat]. [Environmental detail].

Shot N:
[Final composition]. [Freeze frame / hold moment].

Throughout: [consistency notes — wardrobe state, physical continuity].
```

Reference existing video for continuation:
```
Multi-shot cinematic scene, continuing @video1
Shot 1 (Wide, interior): ...
```

Tag characters: `@image_1`, `@image_2`, `@image_3`
