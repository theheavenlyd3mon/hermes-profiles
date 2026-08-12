# MiniMax H3 — Prompting & Model Reference

Researched 2026-07-31 from the official Notion launch page, platform.minimax.io API docs, runware.ai guide, and morphic.com prompt library.

## Model Specs
- Output: 5–15 seconds, 24 FPS, native synced stereo audio on every generation
- Resolution: 768p (short edge 768px, upscalable to 1440p) or 2K/1440p (short edge 1440px)
- Aspect ratios (fixed set): 21:9, 16:9, 4:3, 1:1, 3:4, 9:16. Text-to-Video requires a ratio; First/Last-Frame follows the input image.
- Prompt length: up to 7,000 characters (API); runware caps at 2,000
- Pricing: 768p $0.09/s, 2K $0.13/s. First 5 reference images free, then $0.04/img. Audio refs free.

## Input Modes
| Mode | Input | Notes |
|---|---|---|
| Text-to-Video | Prompt only | ratio required, cannot be 'adaptive' |
| First/Last Frame | Prompt + 0–2 images | role=first_frame / role=last_frame; ratio follows image |
| Omni Reference | Prompt + up to 9 images + 3 video clips + 3 audio clips (12 files max) | role=reference_image / reference_video / reference_audio. Audio must pair with ≥1 image or video. |

## The Five-Block Prompt Structure

H3 prompts are longer and more structured than tag-based models. Build from five blocks:

### 1. Roles (assign each reference a job)
"Use Image 1 for the environment mood and color palette. Use Image 2 for the character's appearance — preserve [specific features]. Use Image 3 for the vehicle design."
- Name what to preserve from each reference explicitly (hair, implants, body type, material finish)
- Without role assignment, the model guesses what each image is for

### 2. Timed Beats (lay action across the clip)
```
[0–5s] Wide establishing shot...
[5–9s] Character reaches the car...
[9–13s] Engine starts, door opens...
[13–15s] Car departs, street returns to empty...
```
- Timestamps give the model a pacing skeleton
- Each beat should have a distinct visual event, not just a camera change
- For 15s clips, 3–5 beats works well; for 5–8s, 1–2 beats
- Match duration to how much genuinely happens — padding a simple action to 15s causes stalling/looping

### 3. Look (cinematographic language)
- Camera: "low angle, static wide" / "slow push-in to medium" / "three-quarter front angle"
- Lens: "anamorphic with horizontal flare" / "shallow depth of field" / "deep focus"
- Grade: "deep blacks, desaturated midtones, magenta and cyan accents"
- Texture: "fine film grain" / "rain droplets on the lens"
- H3 reads shot-craft terms well — "chiaroscuro", "raking light", "rack focus" all produce visible results

### 4. Sound (a dedicated clause — this is H3's headline feature)
```
Sound: Steady rainfall — soft hiss on asphalt. Distant electrical hum.
At 7s, a sharp electronic chirp as the headlights ignite.
At 9s, deep bass thrum of the engine settling into idle.
Door closing with a heavy seal. Tires hissing on wet asphalt, fading.
```
- Audio is generated IN THE SAME PASS as video — it's not a separate scoring step
- Name specific effects, ambience beds, and one-off hits
- TIME key sounds to on-screen events: "the hammer rings the instant it strikes" syncs; "forge sounds" drifts
- Omit the Sound clause and the model invents fitting audio — but naming it gives control
- "No music" must be stated explicitly if unwanted

### 5. Limits (close with exclusions)
"No on-screen text, no subtitles, no watermarks, no logos. No other characters. No daylight. No music score — pure diegetic sound only."
- H3 follows exclusion instructions well
- Be specific: "no modern clothing" not just "keep it period-accurate"

## Strengths
- Atmospheric, motion-led, single-shot footage with a clear camera idea
- Multi-element scene editing (replace objects, swap costumes, change signage)
- Precise instruction following across complex multi-beat prompts
- Typography and title cards (animated text, credit sequences)
- Native audio synced to on-screen events
- Omni Reference: combine character refs, mood boards, video clips, and audio in one generation
- Voice cloning/transfer from reference audio

## Weaknesses
- Exact on-screen text can drift or garble (especially non-Latin scripts)
- Holding one specific face across a full clip needs reference images — text alone won't lock identity
- Precise object counts are unreliable
- 15s clips with insufficient action tend to stall or loop

## API Shape (platform.minimax.io)
```python
# POST https://api.minimax.io/v2/video_generation
payload = {
    "model": "MiniMax-H3",
    "content": [
        {"type": "text", "text": "...prompt..."},
        {"type": "image_url", "image_url": {"url": "..."}, "role": "reference_image"},
        # role options: first_frame, last_frame, reference_image, reference_video, reference_audio
    ],
    "duration": 15,       # 5-15
    "resolution": "2K",   # or "768P"
    "ratio": "16:9",      # required for text-to-video; omit for image-to-video (adaptive)
}
# Async: poll GET /v2/query/video_generation/{task_id} every ~10s
# On success: task.content.url is the direct download URL
```

## Reference Image Workflow
For a scene with character + vehicle + environment:
1. Generate reference images (image_generate or external) — one per subject
2. Character ref: plain background, three-quarter view, show all distinguishing features
3. Environment ref: wide establishing shot capturing the mood, palette, and atmosphere
4. Vehicle/object ref: three-quarter hero angle, showing material finish and design language
5. Feed all as Omni References with explicit role assignments in the prompt
6. Reuse the same reference set across multiple prompts to hold consistency

## Prompt Length Guidance
- H3 handles long prompts well (up to 7,000 chars) — this is NOT a tag-based model
- A detailed 15s scene with timed beats, sound design, and look direction runs ~2,000–3,000 chars
- Structure > brevity here. The five blocks can be verbose and the model follows them.
- Contrast with the six-part structure for tag-based models (60-120 words) — H3 wants more, not less
