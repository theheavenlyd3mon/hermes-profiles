# Morgan Blackhand eikon pipeline notes

Session-specific historical reference for creating a Morgan Blackhand animated eikon from `morgan_blackhand.PNG` received through Tailscale Taildrop.

> Current default supersedes part of this historical run: generate one `canonical_base_plate.png` and use the same uploaded start image for all six state videos. The per-state plate approach below is useful context/scar tissue, not the preferred production pipeline.

## Inputs and paths

- Taildrop receive command: `tailscale file get ~/Taildrop`
- Base image used: `~/Taildrop/morgan_blackhand.PNG`
- Eikon name: `morgan-blackhand`
- Active source folder: `~/.hermes/eikons/morgan-blackhand/source/`
- First workspace shape: `~/.hermes/eikon-work/morgan-blackhand-<timestamp>/`
- Improved face-contrast workspace shape: `~/.hermes/eikon-work/morgan-blackhand-face-contrast-<timestamp>/`

## Credential pattern

Use Agent Vault as the source for fal credentials; never print the key.

```bash
export FAL_KEY="$(agent-vault vault credential get --vault default FAL_AI_API_KEY | tr -d '\n')"
```

Verify only by set/missing/length if needed; do not echo the value.

## Plate generation pattern

Use fal `openai/gpt-image-2/edit` for B/W plate generation when available.

Core arguments:

```json
{
  "image_urls": ["<uploaded base image URL>"],
  "image_size": "square",
  "quality": "high",
  "num_images": 1,
  "output_format": "png"
}
```

The original B/W plates looked good but the face was not readable enough after rasterization. The improved prompt emphasized:

- face readability above coat/detail
- large bright face planes
- deep black eyebrow and eye sockets
- clear nose bridge
- clear cheek shadow
- distinct mouth line
- strong beard outline
- crisp jaw/chin
- readable cigar
- fewer tiny hatch lines
- pure black background
- no smoke over the face

Useful prompt clause:

```text
CRITICAL: make the FACE much easier to read than the reference: large bright face planes, deep black eyebrow/eye sockets, clear nose bridge, clear cheek shadow, distinct mouth line, strong beard outline, crisp jaw/chin, readable cigar. Simplify the face into bold graphic shapes with fewer tiny hatch lines. Face should occupy more visual priority than coat.
```

## State visibility correction

Lucas asked for movements/actions to be more exaggerated for visibility. Future eikon videos should not default to barely perceptible motion. For terminal avatars, state differences need to read in 48x24.

Use stronger motion phrases:

- idle: visible breathing, shoulder rise/fall, hard forward glare
- listening: clear lean-in/head turn, one visible nod
- thinking: clear downward head tilt then return, heavy brow, jaw clench
- speaking: obvious mouth/jaw movement, mouth opens clearly and closes
- working: head dips forward, sharp eye scan, tense jaw, shoulders engaged
- error: sharp recoil, angry grimace, glitch behind head only

## Video generation pattern

Use fal `fal-ai/kling-video/v3/pro/image-to-video` with:

```json
{
  "start_image_url": "<uploaded plate URL>",
  "duration": "3",
  "generate_audio": false,
  "cfg_scale": 0.65,
  "negative_prompt": "blur, distort, low quality, text, logo, subtitle, hud, extra character, camera cut, zoom out, face melting, low contrast, smoky face"
}
```

Prompt suffix for loopability and visibility:

```text
Short seamless loopable close-up head-and-shoulders terminal avatar animation. Preserve the supplied high-contrast black-and-white plate composition and identity exactly. Make the motion more exaggerated than subtle so it reads at 48x24, but return to the starting pose by the final frame for looping. Locked camera, no cuts, no zooming out, no text, no logos, no subtitles, no HUD, no extra characters. Keep face high contrast and easy to read. Pure black background. Natural controlled motion only.
```

## Fully loopable install pattern

Raw Kling clips can still snap at the boundary. For active `.mp4` state sources, make ping-pong loops before install when the user asks for fully loopable output:

```bash
ffmpeg -y -hide_banner -loglevel error -i "$raw" -an -vf "fps=24,scale=1440:1440,format=yuv420p" -c:v libx264 -preset medium -crf 18 "$fwd"
ffmpeg -y -hide_banner -loglevel error -i "$fwd" -vf reverse -an -c:v libx264 -preset medium -crf 18 "$rev"
printf "file '%s'\nfile '%s'\n" "$fwd" "$rev" > "$list"
ffmpeg -y -hide_banner -loglevel error -f concat -safe 0 -i "$list" -c copy "$out"
```

This doubled 3.04s raw clips to ~6.08s installed state clips and made transitions clean.

## QA checklist learned

- Inspect both plate contact sheet and video strip contact sheet before finalizing.
- Face readability matters more than overall cinematic beauty.
- Prefer bold facial planes over tiny detailed hatching.
- No text/logos/HUD.
- Glitch/error effects go behind the head, not over the face.
- Final report should include active source folder, workspace, preview paths, probe summary, and Studio handoff.
