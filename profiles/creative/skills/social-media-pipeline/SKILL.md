---
name: social-media-pipeline
description: "Build a creative brand identity and content pipeline for social media — from name brainstorming through visual identity, content strategy, and generation workflow."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative, social-media, brand, content-pipeline, x-twitter, instagram, design]
    category: creative
    related_skills: [ideation, comfyui, claude-design, sketch]
---

# Social Media Content Pipeline

Build a creative brand identity and content generation pipeline for social media accounts — from naming through visual identity, content pillars, and automated production workflows.

## When to Use

- User wants to start a new social media account (any platform)
- User asks to brainstorm brand names, visual identity, or content strategy
- User wants to set up a content generation pipeline (text + images + video)
- User mentions "social media strategy", "brand identity", "content calendar", "posting schedule"
- User wants to combine AI generation tools (ComfyUI, image_gen) with a publishing workflow

## When NOT to Use

- Single image generation request — use `comfyui` or `image_gen` directly
- Pure design work (landing page, UI) — use `claude-design` or `sketch`
- Technical ComfyUI setup — use `comfyui` skill
- One-off content idea brainstorming — use `ideation`

## Pipeline Phases

### Phase 1: Brand Foundation

Establish identity before generating anything.

**1a. Name Discovery**
- Use `ideation` skill's constraint method for name brainstorming
- Consider: pronounceability, cross-platform handle availability, visual brandability
- Test names against: Does it work as a hashtag? As a handle? On a business card?
- Present 6-10 options across 2-3 vibe categories (evocative, bold, technical, etc.)
- Narrow to top 3 with rationale

**1b. Visual Identity**
- Color palette: 2-3 primary colors + neutrals, with hex codes
- Typography: 1-2 font families (display + body)
- Style direction: the aesthetic "feel" (e.g., "cinematic anime", "clean minimal", "dark moody")
- Mood references: 3-5 existing accounts or artworks that capture the vibe
- Use `claude-design` skill to prototype visual concepts if needed

**1c. Voice & Tone**
- How the account talks to its audience
- Content tone: educational, inspirational, technical, playful, etc.
- Engagement style: responsive, curated, mysterious, community-driven

**1d. Content Pillars**
- 3-5 recurring content types (e.g., "scene of the day", "process breakdown", "before/after")
- Format mix: static images, carousels, threads, video, reels
- Platform-specific adaptations (X vs Instagram vs TikTok)

### Phase 2: Content Strategy

**2a. Posting Cadence**
- Start conservative: 3-5 posts/week minimum viable
- Batch generation beats daily grinding
- Best times to post (platform-specific, but general: evenings, weekends)
- Content calendar: theme days, series, events

**2b. Content Types by Platform**
| Platform | Strengths | Ideal Formats |
|----------|-----------|---------------|
| X (Twitter) | Threads, community, quick takes | Images, threads, polls, short video |
| Instagram | Visual portfolio, discovery | Carousels, reels, stories |
| TikTok | Viral reach, trends | Short video, transitions |
| LinkedIn | Professional, long-form | Articles, carousels, text posts |

**2c. Engagement Strategy**
- Reply strategy: how fast, how deep
- Community building: retweets, collaborations, features
- Hashtag strategy: niche + broad mix

### Phase 3: Technical Pipeline

**3a. Generation Setup**
- Confirm backend choice: local vs cloud vs mixed
- Mixed/local-cloud examples:
  - Local Illum for speed/iteration on 6–12 GB cards
  - Cloud Flux for consistency, hi-res, and heavier stacks on 48 GB
- Hardware constraints → model selection (see `comfyui` skill)
- Workflow templates for each content type, one per backend/model

**3b. Prompt & Model Routing**
- Same brand should not sound identical across different backends; map prompt language to model behavior:
  - Local Illumina: painterly texture words, looser brushwork phrasing, lower CFG
  - Cloud Flux: screenplay-style structure, explicit composition, lower CFG
- Maintain a prompt DNA template so every prompt includes archetype + scene + light + texture + quality anchors
- Save model-specific positive/negative token banks in brand files

**3c. Consistency Stack**
To keep a gallery feeling like one film:
- 1–2 LoRAs at 0.4–0.7 weight
- IP-Adapter FaceID/Plus when character identity must hold across poses
- ControlNet OpenPose/DWPose for pose lock; ControlNet Depth for environment fidelity
- Hires fix with stable denoise strength
- Fixed seed within a character arc; reroll per new scene

**3d. Output Organization**
```
outputs/
  raw/          # untouched generations, highest res
  curated/      # selected finals, hero/supporting/environment
  x_ready/      # cropped, branded, compressed, platform crops
prompt_archive/
```

**3e. Blender / 3D Handoff** (if brand work will later become 3D)
- Generate with 3D in mind: centered subject, one key light + one fill, neutral camera angle, clear silhouette read, distinct material groupings
- For concept packages: front/side/3-quarter views, palette PNG, materials.txt, pose reference folder
- Use ControlNet depth/lineart on base renders to keep composition fidelity across 2D→3D handoff

### Phase 4: Publish & Iterate

**4a. Launch**
- Profile setup: bio, header, profile pic (use brand identity)
- First 9-12 posts: establish visual consistency
- Pin best work

**4b. Feedback Loop**
- Track engagement (likes, retweets, replies, follows)
- Identify top-performing content types
- Iterate on style, timing, format

**4c. Growth**
- Collaborations with other AI artists
- Participate in challenges/trends
- Cross-platform posting
- Build email list or Discord community

## Brand Identity Template

```markdown
## Brand: [Name]

### Visual Identity
- Primary colors: [#hex1, #hex2]
- Accent: #hex3
- Neutral: #hex4
- Font (display): [Font Name]
- Font (body): [Font Name]
- Style keywords: [3-5 adjectives]

### Voice
- Tone: [educational/inspirational/technical/playful]
- Engagement: [responsive/curated/mysterious/community]
- Sample post: [example of typical content]

### Content Pillars
1. [Pillar 1] — [description, frequency]
2. [Pillar 2] — [description, frequency]
3. [Pillar 3] — [description, frequency]

### Platform Handles
- X: @handle
- Instagram: @handle
- TikTok: @handle
```

## Pitfalls

1. **Don't generate before branding** — inconsistent output wastes content and confuses audience
2. **Don't over-post at launch** — 3 quality posts/week beats 7 mediocre ones
3. **Don't ignore platform differences** — X and Instagram need different content
4. **Don't skip the feedback loop** — post → measure → iterate, not post → post → post
5. **Don't lock brand too early** — first 2 weeks are exploration, not commitment
6. **GPU VRAM matters** — verify hardware specs before making claims (I got this wrong once)

## Reference Files

- `references/brand-brainstorming.md` — name discovery workflow, constraint method, example output
- `references/content-calendar.md` — weekly theme structure, pillar definitions, posting schedule, metrics
- `references/loratlas-cheonma.md` — Loratlas discovery notes, curated Cheonma-adjacent style tiers, prompt protocol, brand file pointer
- `references/brand-markdown-patch-pitfall.md` — when patching prompt template markdown, always re-read after patching; small edits can bisect fenced code blocks or duplicate headings

## Integration Points

- `ideation` — name and concept brainstorming
- `comfyui` — local image/video generation
- `image_gen` — quick generation without local setup
- `claude-design` — visual identity prototyping
- `sketch` — rapid concept exploration
- `nous-branding` — if the brand is Nous-adjacent
- `cronjob` — scheduled content generation

## Example: AI Art Account Setup

**User request:** "I want to start an AI art page on X with anime/semi-realistic style"

**Execution:**
1. Brainstorm 10 names across 3 vibe categories → narrow to 3
2. Define visual identity: colors, fonts, style direction
3. Set content pillars: "Scene of the Day", "Process Breakdown", "Before/After"
4. Set up ComfyUI workflows for each pillar type
5. Create cron job for weekly batch generation
6. Launch with 9-post grid establishing visual consistency
7. Iterate based on engagement data
