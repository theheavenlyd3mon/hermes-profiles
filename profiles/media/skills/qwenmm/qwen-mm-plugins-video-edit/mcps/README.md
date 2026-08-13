# MCP Service Cards

MCP tools include **core perception tools** and external capability providers. Perception tools let the agent see and understand media; external providers generate or transform assets. Neither category is a primary edit engine.

Primary engines remain:

- FFmpeg
- HyperFrames

## Runtime Availability Rule

Before mentioning or calling an MCP tool, confirm it is actually registered in the current MCP runtime/tool list.

A local schema file is **not** proof of availability.

If a tool is unavailable:

1. Say which tool/server is missing
2. Do not pretend the call happened
3. Offer an available fallback if one exists
4. Ask before changing the planned output character

## Core Perception Tools (Use First)

The agent's eyes — `read_video`, `read_image`, `visualize`,
`transcribe_audio`, `save_view`, `vision_chat`. Content-driven editing
starts with them, before FFmpeg/HyperFrames execution. Usage patterns,
high-FPS key-window rule and evidence templates: `core-perception.md`.

## Generation Service Roles

| Tool | Role | Handoff |
|------|------|---------|
| `segmentation` / `grounding` | Subject/object mask preparation | see `segmentation-matting.md` |
| `qwen_tts` | Narration generation | HyperFrames audio timeline or FFmpeg mux/mix |
| `qwen_image` | Image generation/editing | HyperFrames visual asset or FFmpeg overlay |
| `happyhorse` | AI video generation/editing | Support clip for FFmpeg/HyperFrames timeline |
| `wan_t2v` | AI video generation fallback | Support clip; verify availability before use |
| `wan_s2v` | Digital human / lip-sync | Foreground clip for FFmpeg/HyperFrames compositing |

**Named play — hand-drawn / sticker asset set (`qwen_image`).** When the
brief asks for 手绘箭头、圈圈、蒸气/香气线、贴纸、涂鸦字等 beyond what plain
SVG strokes give (`snippets/footage-devices.md` § Ring accent), generate a
sticker SET in one style: one prompt → one sheet of 6-10 elements in ≥3
stroke/shape styles (arrows, dashed circles, wavy underlines, sparkles,
steam lines, speech scribbles — variety is the point), flat colors,
bold outlines, **transparent or solid-white background** — then crop/抠图
into individual PNGs (background removal if needed) and freeze them into
the project's `assets/stickers/`. Sample-first applies: check the SHEET at
step 2, split it only after it passes. Animate stickers with the standard
grammar (draw-on, `lively` pop, wiggle) — never static paste; and verify
them on rendered frames (`engines/hyperframes.md` § pitfalls).

## Sample-first generation (`[sample-first]`)

Generation (qwen_image, wan_t2v, happyhorse, wan_s2v, qwen_tts) goes
concept → one sample → batch, each step confirmed before the next:

1. **Concept:** the metaphor / prompt / plan in text. Settle intent here —
   rewriting words is instant.
2. **Single sample:** ONE still / one short clip / one voice line. Verify
   quality and direction on the sample.
3. **Batch:** only after the sample passes. Partial approval is normal —
   advance only the approved items, keep the rest at step 1/2.

In Delegated mode this still applies (it is a quality gate, not a taste
gate): before a batch, state which tool, sample or full run, expected output
path, expected wait, and the fallback if it fails.

## Caching

Cache service outputs under:

```text
<videos_dir>/edit/mcp_cache/<service>/<hash-or-taskid>.<ext>
```

Check cache before re-calling a service with identical inputs and parameters.

## Failure Handling

- Sync service: retry once only if the failure is transient
- Async service: do not blindly resubmit; report task failure and options
- Never spend additional generation attempts just to hide artifacts; disclose limitations and ask if more attempts are desired
- Failed service output must not be treated as a valid asset

## Minimal Service Card Template

```markdown
# <Service Name>

## Role
## Use When
## Do Not Use When
## Inputs / Outputs
## Sync or Async
## Availability Check
## Cache Key
## Failure Handling
## Engine Handoff
```
