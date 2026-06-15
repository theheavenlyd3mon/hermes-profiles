---
name: animated-eikon-from-base
description: "Turn one supplied base image into a full animated herm eikon: generate one high-contrast black/white canonical base plate, animate six state clips from that same starting frame with fal.ai/Kling, install sources under ~/.hermes/eikons/<name>/source/, and hand off to Eikon Studio for baking."
tags: [eikon, avatar, animation, fal-ai, kling, image-to-video, herm]
related_skills: [eikon, eikon-create, riso]
---

# Animated eikon from one base image

Use this when Lucas provides **one base image of any subject** and wants a complete animated herm eikon with states: `idle`, `listening`, `thinking`, `speaking`, `working`, `error`.

The input can be a human portrait, animal, mascot, robot, object, logo/mark, product photo, vehicle, landscape, abstract symbol, or style board. The skill must first distill the image into a terminal-readable avatar subject, then animate state-specific variants.

The mission is not “make pretty videos.” The mission is a terminal-readable animated avatar. At 48×24, cinematic detail dies. Poster shapes survive.

## Output contract

Given:

```text
/base/image.png
```

Produce:

```text
~/.hermes/eikon-work/<name>-<YYYYMMDD-HHMMSS>/
  source-input/<original image>
  bw-plates/
    canonical_base_plate.png
    contact_sheet.png
    optional_rejected_state_plates/
      <state>_bw_plate.png
  fal-kling/
    payloads/*.json
    queue_submits/*.json
    statuses/*.json
    results/*.json
    videos/
      idle.mp4
      listening.mp4
      thinking.mp4
      speaking.mp4
      working.mp4
      error.mp4
    media_probe.json
  preview/
    state_contact_sheet.jpg
    loop_preview_contact.jpg
  manifest.json

~/.hermes/eikons/<name>/source/
  base.png or base.mp4
  idle.mp4
  listening.mp4
  thinking.mp4
  speaking.mp4
  working.mp4
  error.mp4
```

Then tell Lucas:

```text
Open Herm → Eikon tab → eikon row → <name> → tune contrast/invert/zoom/rasterizer → Ctrl+S to bake.
```

Do **not** hand-write `.eikon` or `studio.json` unless Lucas explicitly asks for a low-level converter. Studio owns bake output.

## Hard visual rule

Design the source like an icon, not a film frame:

- black/white or near-monochrome
- pure black or pure white background, depending on which reads best
- one dominant subject, centered and large
- strong silhouette and clean negative space
- huge identifying landmarks: face/eyes/jaw for people, ears/muzzle/tail for animals, outline/emblem/corners for objects, letterform/shape for logos, skyline/ridge/sun/moon for landscapes
- no smoky midtone soup
- no tiny texture
- no busy scenery unless the scenery itself is the subject, and even then reduce it to 2–4 big shapes
- no text/logos/HUD unless the supplied image is itself a logo/mark; even then preserve only the iconic shape, not small readable text

Scar: the old Johnny cinematic red/magenta videos looked good as video, then became a terrifying ghost in `.eikon`. The fix was high-contrast black/white poster plates before animation.

## Universal input adaptation rule

Before plate generation, classify the supplied image and choose the “surviving landmarks.” Do not blindly use human-face prompts for every input.

| input type | extract as eikon subject | landmark priority | avoid |
|---|---|---|---|
| human portrait | head/shoulders avatar | face planes, hair mass, eyes/brow/glasses, nose/mouth, jaw/collar | pores, wrinkles, tiny hair, cinematic smoke |
| animal | bust or full-body mascot | ears/horns, eyes, muzzle/beak, paws/claws/tail, posture | fur microtexture, background habitat clutter |
| robot/mech | bust/iconic chassis | head/visor, antennae, shoulder/chest silhouette, panel seams | tiny greebles, unreadable wires |
| object/product | emblematic object icon | outer contour, handle/screen/lens/edges, one face/front plane | specular clutter, small labels, packaging text |
| vehicle | 3/4 silhouette or front icon | wheel/wing/cockpit/grill, strong body outline | busy environment, tiny reflections |
| logo/mark | simplified mark | primary shape, negative-space cuts, brand silhouette | slogans, tiny letters, gradients |
| landscape/place | iconic scene symbol | horizon/ridge/building silhouette, sun/moon/window blocks | foliage/detail/noisy perspective |
| abstract/art | distilled sigil | 2–4 dominant shapes, rhythm, contrast | preserving every brushstroke |
| style board/UI sheet | art direction only | mood, palette, silhouette vocabulary | importing frames, labels, arrows, panels |

If the image has no obvious avatar subject, make one explicit in the plate prompt: “distill the supplied image into a single centered eikon sigil/avatar that preserves its most recognizable shapes.”

If the user did not name the eikon, derive a neutral slug from the file name or subject. Do not invent copyrighted character names beyond what the user provided.

## Mandatory skill chain

Load first:

- `eikon`
- `eikon-create`

Follow their rules too. This skill is the one-base-image end-to-end pipeline layered on top.

## Credential strategy

This pipeline has two distinct fal.ai stages with different credential requirements:

**Step 1 (image gen — base plate):** Uses `fal-ai/gpt-image-2/edit` or similar image-to-image model. With a Nous Portal subscription (`image_gen.use_gateway: true` in config.yaml), this works through the Nous gateway proxy — no direct FAL_KEY needed. The gateway covers the official image generation models (Flux, GPT-Image, etc.) via the subscription.

**Step 2 (video gen — Kling animations):** Uses `fal-ai/kling-video/v3/pro/image-to-video`. The Nous gateway does NOT proxy video generation. You need a direct FAL_KEY from fal.ai for this step. Hermes docs explicitly say FAL video models (Kling, Veo 3.1, Pixverse) need FAL_KEY.

**Recommended setup:** Get the canonical base plate through the Nous gateway (free, no key needed). Then set FAL_KEY in your profile .env or vault for the Kling video generation. This minimizes direct fal credit spend since you only pay for the 6 state videos, not the test plates.

## Related skills

- **`riso` skill** — Complementary ASCII/Braille eikon pipeline. Once you have the 6 state MP4s from this skill, feed them through `riso`'s `build-eikon-from-video` to produce ASCII-rendered `.eikon` files for terminal-only display. riso handles text-based eikons; this skill handles real video eikons for Herm Studio.

## Step 0 — create workspace

Slug the name:
```bash
name="<slug>"
ts=$(date +%Y%m%d-%H%M%S)
work="$HOME/.hermes/eikon-work/${name}-${ts}"
out="$HOME/.hermes/eikons/${name}/source"
mkdir -p "$work/source-input" "$work/bw-plates" "$work/fal-kling" "$work/preview" "$out"
cp "<base-image>" "$work/source-input/base.${ext}"
```

Verify image dimensions:

```bash
python3 - <<'PY'
from PIL import Image
from pathlib import Path
p=Path('<base-image>')
im=Image.open(p)
print({'path': str(p), 'size': im.size, 'mode': im.mode})
PY
```

## Step 1 — make one canonical black/white base plate first

Do **not** generate six independent starting plates for the six states. Six different plates create six different starting poses/crops/identities, which makes Herm state transitions snap and feel jarring. The preferred pipeline is:

1. Generate **one** terminal-readable canonical base plate from the supplied image.
2. QA that one plate hard.
3. Use that **same canonical plate as `start_image_url` for all six Kling animations**.
4. Put state differences in the **motion prompt**, not in six different first frames.

Do **not** animate the raw cinematic base directly unless the base is already a clean icon/poster image.

### When the user provides a style board / avatar breakdown

If Lucas provides a polished dashboard-style avatar breakdown, treat it as **art direction**, not as the source image. Full layout boards usually contain text, panels, arrows, grids, barcodes, UI cards, warning icons, and tiny labels that become terminal noise at 48×24. Extract the useful doctrine — silhouette, facial planes, lighting, state vocabulary, mood — then generate clean avatar-only plates with no UI frame or readable text.

For the Morgan `operatorfile` branch, the winning hybrid was: photoreal human portrait, but lit like a glyph-survival signal map. Keep the face/collar/cigar large; put state overlays behind the silhouette only; preserve premium operator mood without importing dashboard clutter.

Preferred when fal.ai is available: use `openai/gpt-image-2/edit` through fal for image-to-image transformation of the supplied base into **one** B/W canonical plate. Upload the base with `fal_client.upload_file`, pass `image_urls: [ref_url]`, `image_size: "square"`, `quality: "medium"`, `num_images: 1`, and save the result JSON. This preserves identity much better than local posterization while still producing a clean terminal-readable starting frame.

Generate or edit one clean plate image using the available image generation/editing tool. Save it as:

```text
<work>/bw-plates/canonical_base_plate.png
```

If OpenAI image editing is used and `OPENAI_BASE_URL` is blank, strip it before SDK init:

```python
if not os.environ.get('OPENAI_BASE_URL', '').strip():
    os.environ.pop('OPENAI_BASE_URL', None)
```

### Canonical base plate prompt

Use the supplied base image as strict identity reference.
```text
Use the supplied base image as strict identity/shape reference. Adapt the subject class first: if it is a person, preserve face/hair/jaw/clothing silhouette; if an animal, preserve ears/eyes/muzzle/body posture; if a robot/object/vehicle, preserve the chassis/outer contour/key parts; if a logo/abstract image, preserve the mark's dominant shape and negative space; if a landscape, distill it into one iconic scene silhouette. Then create a high-contrast black-and-white poster/icon plate for a terminal ASCII/Braille avatar. Pure flat background, no scenery unless the scene is the subject, no smoke, no gradients, no tiny detail, no small readable text, no logos except a supplied logo's primary mark. Strong readable silhouette. Big bold landmarks that survive at 48x24 terminal size. Single subject centered, large in frame.
```

### State-specific motion design

State differences should come from Kling motion prompts while keeping the first frame identical. Do not generate six different first-frame plates just to express states.

| state | motion prompt intent from the same canonical plate |
|---|---|
| idle | neutral/resting loop; stable pose, subtle breath/sway/energy |
| listening | attentive/listening motion: slight lean-in/head turn/sensor orientation/pulse, then return to the canonical pose |
| thinking | pensive/processing motion: slow head tilt/downward glance/sensor scan/tiny orbit, then return to the canonical pose |
| speaking | communication motion: mouth/jaw/beak movement or simple pulse/radiating non-text signal, then return to the canonical pose |
| working | focused/action motion: scanning, operating pulse, contained directional energy behind the silhouette, then return to the canonical pose |
| error | controlled failure motion: short recoil/stutter/glitch/fractured outline behind/around subject, then return to the canonical pose |

Only create state-specific still plates as rejected experiments or emergency fallbacks, and put them under `bw-plates/optional_rejected_state_plates/`. They are not the default production substrate.

### Legibility and glyph-survival correction

If the user says the subject is hard to make out, do not just raise generic contrast. Regenerate the plates with a subject-first prompt:

- people: large bright face planes, deep black brow/eye sockets, clear nose bridge, cheek shadow, mouth line, beard/jaw/hair outline, fewer hatch lines, no smoke over face
- animals: large eye/muzzle/ear or beak shapes, clear body outline, simplified fur/feather masses, no habitat clutter
- robots/objects/vehicles: thick outer contour, one dominant front plane, oversized visor/screen/wheel/wing/handle/key part, no tiny greebles or labels
- logos/abstract marks: reduce to the mark's core silhouette and negative-space cuts, no slogans or microtext
- landscapes: reduce to skyline/ridge/building/sun/moon/window-block silhouette, no leaves/texture/noise

Subject readability beats cinematic mood for a 48×24 terminal avatar.

If an exact 48×24 source experiment looks bad, do **not** keep pushing lower-resolution sources. Lucas's correction from the Morgan Blackhand run was that the problem was feature distinctiveness / value separation, not literal source resolution. Return to high-resolution plates and make the icon landmarks more obvious. For people this means bright face mask planes, black brow/eye/nose/mouth slashes, hair streaks, cigar/prop if present, hard jaw/collar block. For non-human subjects this means fewer, bigger shape blocks and clear negative-space cuts. Prompt for clean graphic shapes rather than more accessories.

For Unicode/Braille raster output, design the source as a **glyph-survival signal map**, not an illustration: pure black background, light subject, three-value black/gray/white poster shapes, subject filling the frame, and features large enough to survive harsh thresholding. Before spending Kling credits, inspect the plate at thumbnail size and, if possible, with a 48×24 Braille/threshold preview. If it only works as a full-size drawing, it will probably fail as an eikon.

If the subject's landmarks are still getting lost, escalate beyond “more contrast” into an **extreme stencil pass**. Make the source less illustrative and more combat-patch/signage-like: tighter crop, 2–5 large shape masses, one or two huge black/white feature cuts, no subtle eyes, wrinkles, hatching, fur, smoke, texture, reflections, or tiny background details. The goal is recognizable landmarks at 48×24, not a beautiful full-resolution image.

If Lucas specifically asks to try the opposite direction — **hyper-realistic human portrait with the same monochrome palette** — create it as a separate comparison eikon rather than replacing the stencil candidate. Prompt GPT-image-2 for a photographic black/white close-up: pure black background, pale face highlights, deep eye sockets, clear nose bridge, visible mouth line, rugged beard/stubble if present, strong key/rim lighting, no smoke over the face. Do not posterize the plates before Kling; keep the photographic tonal planes and let Studio contrast/rasterizer decide. Warn in the final QA that this may look better as a human portrait but may collapse more than stencil at 48×24 because tonal detail can turn into glyph noise.

### Plate QA gate

Before any video spend, make a contact sheet/proof image for the **single canonical plate** and inspect it:

```bash
python3 - <<'PY'
from PIL import Image, ImageDraw
from pathlib import Path
folder=Path('<work>/bw-plates')
p=folder/'canonical_base_plate.png'
im=Image.open(p).convert('RGB')
thumb=im.resize((240,240))
sheet=Image.new('RGB',(720,320),'white')
d=ImageDraw.Draw(sheet)
sheet.paste(thumb,(20,50)); d.text((20,25),'canonical_base_plate',fill='black')
# small repeated strip makes it obvious whether state transitions will share a stable first frame
for i,state in enumerate(['idle','listening','thinking','speaking','working','error']):
    x=280+(i%3)*140; y=35+(i//3)*140
    sheet.paste(im.resize((120,120)),(x,y+20)); d.text((x,y),state,fill='black')
sheet.save(folder/'contact_sheet.png')
print(folder/'contact_sheet.png')
PY
```

Use terminal preview too:
```bash
chafa --size=48x24 --symbols=braille --colors=none --format=symbols --stretch "<work>/bw-plates/canonical_base_plate.png" 2>/dev/null || true
```

Pass only if:

- one dominant subject reads at thumbnail size
- the subject's top 2–4 landmarks read (face/ears/muzzle/visor/object contour/logo cut/skyline, depending on input)
- silhouette and negative space read
- the neutral pose can plausibly support all six state motions without needing a different crop/identity
- background is clean or deliberately reduced to iconic scene shapes

If it fails, regenerate the canonical plate. Do not spend fal credits animating garbage.


## Step 2 — animate plates with fal.ai / Kling

Preferred model when available:
```text
fal-ai/kling-video/v3/pro/image-to-video
```

Use direct fal queue/API if wrappers expose stale schemas. Correct field. Upload **one** `canonical_base_plate.png` and reuse its uploaded URL for every state:

```json
{
  "start_image_url": "<uploaded canonical_base_plate URL>",
  "prompt": "<state motion prompt>"
}
```

Do not upload six different state plate URLs for production unless Lucas explicitly wants the older experimental pipeline. Stable first frame beats extra still-state variety.

Load `FAL_KEY` without printing it. Prefer Agent Vault when available; Lucas has used `FAL_AI_API_KEY` in the default vault:

```bash
export FAL_KEY="$(agent-vault vault credential get --vault default FAL_AI_API_KEY | tr -d '\n')"
```

Fallback configured env files:

```text
~/.hermes/.env
/home/lucas/projects/OpenMontage/.env
```

Never expose the key in stdout/final answers.

### Global video prompt suffix

Append this to every state motion prompt:

```text
Short loopable close-up terminal avatar animation. Preserve the supplied black-and-white canonical plate composition and subject identity/shape exactly. The first frame should match the supplied start image; animate only the requested state motion and return to the same canonical pose by the final frame. Locked camera, no cuts, no zooming out, no text, no logos, no subtitles, no HUD, no extra characters. Keep background flat and clean unless the supplied subject is a landscape/scene, in which case preserve only the simple iconic scene silhouette. Strong silhouette, high contrast, terminal-readable at 48x24. Natural controlled motion only.
```

### State video prompts

For terminal eikons, state motion should be visibly readable at 48×24. If the user asks for more visible states, use exaggerated-but-controlled movements rather than subtle micro-motion, and explicitly ask the provider to return to the starting pose by the final frame for loopability.

`idle`:

```text
Animate as idle/resting: subtle breathing or quiet energy if biological; tiny idle sway, sensor hum, light pulse, or environmental shimmer if non-biological. Keep the subject mostly stable.
```

`listening`:

```text
Animate as listening/receiving: slight lean-in/head turn for faces; ear/antenna/sensor movement for animals/robots; gentle orientation shift or pulse for objects/logos/scenes. No speaking or text.
```

`thinking`:

```text
Animate as thinking/processing: slow head tilt or downward glance for faces; sensor scan, tiny orbit, or contained internal glow for non-faces. Controlled pensive motion, then return forward.
```

`speaking`:

```text
Animate as speaking/transmitting: natural mouth/jaw/beak movement for faces; simple pulse, speaker-grille vibration, light emission, or radiating non-text signal for objects/logos/scenes. No subtitles or speech bubbles.
```

`working`:

```text
Animate as working/active mode: focused scanning, tense posture, machine/object operating pulse, or directional energy behind silhouette only. No readable code or HUD.
```

`error`:

```text
Animate as error/failure: short controlled recoil, grimace, stutter, glitch, warning shake, or fractured outline, then return to the stable pose. Effects stay behind/around the subject and must not obscure the key landmarks. No readable error text.
```

### Receipts or it didn't happen

For every state save:

- payload JSON
- queue submit JSON / request id
- latest status JSON
- final result JSON
- downloaded MP4

Never tell Lucas generation completed until final MP4s exist and probe clean.

## Step 3 — verify videos

Probe each video:
```bash
ffprobe -v error \
  -show_entries stream=index,codec_type,codec_name,width,height,r_frame_rate,nb_frames,duration \
  -show_entries format=duration,size,format_name \
  -of json "<video>"
```

Write a combined `media_probe.json`.

Make a contact sheet:
```bash
ffmpeg -y -hide_banner -loglevel error -i "<video>" -vf "fps=1,scale=240:240,tile=5x1" "<state>_strip.jpg"
```

QA for:

- subject identity/shape stable
- no landmark melting or over-interpretation
- no text/logos unless the primary supplied logo mark is the subject
- no background clutter
- high contrast preserved
- state motion readable and appropriate to the subject class
- no wild camera crop changes

## Step 4 — loopable clips

Raw provider clips often snap at loop boundary. If Lucas asks for fully loopable output, or if the clip will be installed as an active state source, prefer making a ping-pong forward+reverse loop before install. When Lucas asks for more visible state motion, exaggerate the movement enough to read at 48×24, but still prompt the model to return to the starting pose by the final frame before ping-ponging.

Use this pattern:
```bash
ffmpeg -y -hide_banner -loglevel error -i "$in" -an -vf "fps=24,scale=1440:1440,format=yuv420p" -c:v libx264 -preset medium -crf 18 "$fwd"
ffmpeg -y -hide_banner -loglevel error -i "$fwd" -vf reverse -an -c:v libx264 -preset medium -crf 18 "$rev"
printf "file '%s'\nfile '%s'\n" "$fwd" "$rev" > "$list"
ffmpeg -y -hide_banner -loglevel error -f concat -safe 0 -i "$list" -c copy "$loop"
```

Verify duration roughly doubled and use the looped file as `<state>.mp4`.

## Step 5 — install into Eikon Studio source folder

Back up any existing active source files first:
```bash
target="$HOME/.hermes/eikons/<name>/source"
ts=$(date +%Y%m%d-%H%M%S)
mkdir -p "$target/backups-$ts"
cp "$target"/* "$target/backups-$ts"/ 2>/dev/null || true
```

Copy exact state names. Keep the active source folder clean: `base.png` plus six `.mp4` state files. Do **not** leave `idle.png`, `listening.png`, etc. beside the videos unless Lucas explicitly wants static state overrides; Studio/source resolution may prefer those PNGs and make states appear non-animated.
```bash
# Back up/remove static state PNGs that could shadow animated state videos.
ts=$(date +%Y%m%d-%H%M%S)
mkdir -p "$target/static-state-backup-$ts"
for st in idle listening thinking speaking working error; do
  [ -f "$target/$st.png" ] && mv "$target/$st.png" "$target/static-state-backup-$ts/$st.png"
done

cp "$work/fal-kling/videos/idle.mp4" "$target/idle.mp4"
cp "$work/fal-kling/videos/listening.mp4" "$target/listening.mp4"
cp "$work/fal-kling/videos/thinking.mp4" "$target/thinking.mp4"
cp "$work/fal-kling/videos/speaking.mp4" "$target/speaking.mp4"
cp "$work/fal-kling/videos/working.mp4" "$target/working.mp4"
cp "$work/fal-kling/videos/error.mp4" "$target/error.mp4"
cp "$work/bw-plates/canonical_base_plate.png" "$target/base.png"
```

Verify active files:
```bash
stat "$target"/*.mp4 "$target/base.png"
# Use HERMES_HOME (set by Hermes to active profile root, e.g. ~/.hermes/profiles/senna/)
# Falls back to ~/.hermes/skills/ for non-profile setups.
skill_dir="${HERMES_HOME:-$HOME/.hermes}/skills/creative/animated-eikon-from-base"
python "$skill_dir/scripts/verify_eikon_source.py" "$target"
```

## Step 6 — hand off to Studio

Tell Lucas exactly:

```text
Open Herm → Eikon tab → eikon row → <name>.
Use source row to pick the installed state clips if needed.
Tune zoom / pan / contrast / invert / symbols in Studio.
Ctrl+S bakes <name>.eikon and studio.json.
```

Do not pretend Studio bake happened unless you actually see `<name>.eikon` written after Lucas/Studio saves.

## Step 7 — final report format

Keep it short. Include:

- eikon name
- workspace path
- active source folder path
- generated plate contact sheet
- generated video contact sheet
- active state file list
- ffprobe summary: dimensions, fps, duration, bytes
- estimated fal cost if known
- any rejected states and why
- exact Studio handoff steps

## 48×24 exact-source experiments

If Lucas asks to test exact 48×24 source images, create a separate comparison eikon rather than overwriting the production candidate. Start from the best high-res face-contrast plates, crop tightly around face/collar, resize to exactly 48×24, quantize to a few tones, and save those PNGs as the experimental source files. For video generation, nearest-upscale the 48×24 plates to a provider-friendly 2:1 frame (for example 960×480) but keep the exact 48×24 PNGs in the source folder. Treat this as an experiment: it can produce a pre-baked pixel look, but it often hurts facial fidelity and can make video models over-interpret the face.

## Reference examples

- `references/single-canonical-plate-pipeline.md` — current default: generate one `canonical_base_plate.png`, reuse the same uploaded start image for all six Kling state videos, and keep state differences in motion prompts to avoid jarring transitions.
- `references/universal-input-adaptation.md` — universal subject-class adaptation: people, animals, robots, objects, vehicles, logos, landscapes, abstract art, and style boards; includes prompt skeletons and QA gates for any supplied image.
- `references/morgan-blackhand-fal-pipeline.md` — receipt-backed example using Taildrop input, Agent Vault `FAL_AI_API_KEY`, fal GPT Image 2 plate generation, Kling v3 Pro video generation, ffprobe/contact-sheet verification, and final Eikon source install.
- `references/48x24-source-eikon-test.md` — exact 48×24 source-image experiment pattern, QA findings, and recommendation to prefer high-res face-contrast plates for production unless explicitly testing a pre-baked pixel look.
- `references/morgan-blackhand-distinctive-contrast-2026-05.md` — Lucas correction after the 48×24 test: fix feature distinctiveness/value separation with high-res plates, not lower source resolution.
- `references/unicode-raster-base-guidelines.md` — research-backed glyph-survival rules for Unicode/Braille eikon sources: high-res three-value poster plates, big landmarks, harsh 48×24 QA before video spend.
- `references/morgan-blackhand-facecut-2026-05.md` — session-specific correction when Lucas said facial features were still getting lost: use extreme facecut/stencil combat-patch plates, keep active source folders free of state PNG shadows, label partial/static placeholder animation honestly, then rerun only missing Kling states after fal credits recover.
- `references/morgan-blackhand-realportrait-2026-05.md` — alternate hyper-realistic monochrome human portrait branch: photographic plates, conservative Kling motion, and the QA tradeoff between human likeness and 48×24 glyph survival.
- `references/morgan-blackhand-operatorfile-2026-05.md` — Higgsfield-style avatar breakdown → operatorfile branch: use UI-sheet references as art direction only, generate clean photoreal glyph-lit portrait plates, keep state overlays behind the silhouette, and handle partial Kling completion honestly with static placeholders only when balance dies mid-run.
- `scripts/verify_eikon_source.py` — reusable verifier for active source folders; checks `base.png/base.mp4`, six state MP4s, absence of state PNG shadows, and ffprobe readability.

## Failure modes / scars

- **Six independent state plates cause jarring transitions.** Default to one `canonical_base_plate.png`, reuse it as the `start_image_url` for all six state animations, and encode state differences in motion prompts. Only use separate state plates as labeled experiments/fallbacks.
- **Human-only prompt on non-human input.** Do the classification pass first; use universal subject landmarks instead of face/jaw/collar language for every image.
- **Cinematic color source → ghost eikon.** Do not convert red smoky videos directly. Build a B/W canonical plate first.
- **Midlane gradients disappear.** Use hard silhouette and clean negative space.
- **Tiny details die.** Preserve the subject's big landmarks, not microtexture: face/ears/muzzle/visor/object contour/logo cut/skyline.
- **Provider ignores negative prompt.** Reset substrate with a clean plate, then animate. Do not keep rerolling from contaminated old video.
- **Blank OpenAI base URL breaks SDK.** Strip blank `OPENAI_BASE_URL`.
- **fal wrapper may be stale.** Direct queue/API route is valid when wrapper lacks `v3/pro`.
- **Receipts beat narration.** Queue id or final file, not vibes.
- **Studio owns bake.** Source install is the agent job unless asked to inspect/patch Herm internals.
