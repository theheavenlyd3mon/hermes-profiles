# Cinematography Vocabulary — Lookup Tables

Load this when choosing shots, moves, lighting, or lenses for a FLUX 3 prompt.
Every term earns its place twice: (a) it carries a known emotional effect in film,
and (b) it is already recognized vocabulary in Runway / Sora / Kling / Veo
prompting guides — so the FLUX 3 reasoning harness understands it. Pick the term
whose emotional effect matches the beat, then drop it into the prompt anatomy's
shot / style slots.

---

## 1. Shot types (framing / size)

| Term | What it is | Emotional effect / when to use |
|---|---|---|
| Establishing shot | Opening wide of the location, often with a boom/crane move | Orients the audience; sets scale and tone before anything happens |
| Extreme wide (EWS) | Subject tiny in a vast landscape | Isolation, insignificance, dread of scale — perfect for "something is out there" |
| Wide / long shot (WS/LS) | Full subject with headroom; 16–35mm, f/8–f/11, deep focus | Narrative distance; character dwarfed by environment (Kubrick's favorite); scale + grandeur |
| Medium long / "cowboy" (MLS) | Knees up | Spatial awareness + detail; lone figure vs. landscape (Westerns) |
| Medium shot (MS) | Waist up; 35–50mm natural perspective | Neutral, conversational, balanced coverage |
| Medium close-up (MCU) | Chest up | Emotional connection while keeping situational context; pair with dutch angle for unease |
| Close-up (CU) | Face fills frame; 85–135mm, f/1.8–2.8 shallow DOF | Reveals emotion/reaction; intensifies drama; the "realization" beat before a reveal |
| Extreme close-up (ECU) | One feature (eye, claw, scale) | Maximum intimacy or menace; withholds context — ideal for monster glimpses |
| POV shot | Camera = character's eyes, often handheld | Immersion; audience *is* the prey/witness |
| Over-the-shoulder (OTS) | 50–85mm, behind one subject | Biased perspective, power dynamics, "what is he looking at?" |
| Low angle | Camera below subject looking up | Dominance, menace, monumentality |
| High angle / bird's-eye | Camera above looking down | Vulnerability, insignificance, omniscient surveillance |
| Dutch angle / canted | Tilted horizon | Instability, wrongness, psychological tension |
| Aerial / drone | Free overhead movement | Epic survey of terrain; god's-eye dread; classic trailer opener over mountains |

Sources: studiobinder.com/blog/types-of-camera-shots-sizes-in-film/ ; adobe.com/creativecloud/video/production/cinematography/camera-shots-and-angles.html ; eac.libguides.com/c.php?g=723550&p=5311207

---

## 2. Camera movements

| Term | Motion | Emotional effect (documented) |
|---|---|---|
| Static / locked | No movement | Focus, restraint; a still frame makes any later tiny move feel huge (Godfather push-in example) |
| Pan | Rotates horizontally | Reveals new information, follows action, adds energy |
| Whip pan | Fast blur pan | Sudden energy, shock cut without cutting |
| Tilt | Rotates vertically | Scale, dominance, awe — Spielberg tilts UP to reveal the dinosaurs in Jurassic Park |
| Push-in (slow dolly in) | Moves toward subject | Tension, intimacy, drawing into a character's realization; *the* pre-reveal move |
| Pull-out (dolly out) | Moves away | Isolation, detachment, revealing the terrible context (Kubrick, The Shining) |
| Tracking / dolly | Moves with/through scene | Immersion, momentum, pursuit |
| Truck | Lateral left/right | Parallel observation, journey |
| Arc / orbit | Circles the subject | Unease, menace (Nolan's Joker); majesty at slow speed |
| Boom / crane / jib | Vertical rise or drop | Grandeur, epic scale; crane-down-to-subject = classic trailer open; crane-up-away = ending beat |
| Handheld | Operator shake | Immediacy, documentary realism, chaos; in horror the shake *is* fear |
| Dolly zoom (Vertigo) | Dolly + counter-zoom | Disorientation, reality breaking, dawning horror |
| Zoom | Focal-length change | Artificial, unnerving; horror/thriller staple (Kubrick) |
| Roll | Rotates on long axis | Dizziness, discomfort, world gone wrong (Black Panther throne) |
| Rack focus | Focus shifts between planes | Redirects attention; "look at what was behind you the whole time" |
| Aerial follow | Drone tracking | Scale + pursuit; the flying-thing's POV |

Pace + reveal phrasing that works (model-agnostic, matches FLUX usage):
- "Pan right, smooth speed, following the motorcycle's path, dust swirling."
- "Slow push in, intimate pace, intensity increasing on the bottle, light glinting off glass."
- "Truck left, consistent pace, keeping pace with runner, revealing the products on the shelf."
- "Orbit clockwise, smooth cinematic pace, circling the car, neon reflections shifting on metal."
- "Rack focus, gentle transition, shifting sharpness to the house in back, flowers swaying."
Golden rule: active kinetic verbs (glides, drifts, swirls, rushes) + clear camera directions.

Sources: studiobinder.com/blog/different-types-of-camera-movements-in-film/ ; eac.libguides.com/c.php?g=723550&p=5311207 ; letsenhance.io/blog/all/ai-video-camera-movements

---

## 3. Lighting vocabulary

| Term | Meaning | Emotional effect |
|---|---|---|
| Golden hour | Sun near horizon, warm soft directional light | Beauty, nostalgia — contrast it against what's coming |
| Blue hour / twilight | Post-sunset cool ambient | Melancholy, ominous calm |
| Low-key | Key ≫ fill, deep shadows | Drama, horror, mystery |
| High-key | Near 1:1 ratio, few shadows | Safety, comedy — use to fake safety before the turn |
| Chiaroscuro | Hard light/dark contrast, Caravaggio-style | Dread, moral darkness, sculptural menace |
| Rembrandt lighting | Key from ~45° with cheek triangle | Classical drama, gravity |
| Rim / edge light | Backlight tracing the silhouette | Separates subject from darkness; a rim-lit silhouette IS the monster tease |
| Silhouette / backlit | Subject as dark shape against light | Withholds identity; pure suspense |
| Volumetric light / god rays | Beams made visible by haze/fog | Scale, awe, cathedral dread |
| Practicals | Visible in-scene lights (fire, lamps, windows) | Grounded realism, warm anchor in a dark frame |
| Negative fill | Removing bounce to deepen shadow | Heaviness, gloom |
| Atmosphere / haze / fog | Particulate in air | Depth layering, mystery, softens and hides — fog is a reveal-delay device |
| Halation | Glow bleed on highlights | Filmic warmth, dreamlike |
| Moonlight / cool night | 5600K+ blue cast | Cold, isolation |
| Flicker / lightning flash | Intermittent illumination | Reveals the creature in strobing fragments |

Verbatim lighting fragments worth stealing:
- "Golden hour sunlight streaming through tall windows"
- "Warm tungsten spotlighting from camera left, creating Rembrandt lighting"
- "Chiaroscuro lighting with deep blacks and bright highlights"
- "Warm 3200K lighting for intimate scenes" · "Cool 5600K daylight"

Sources: spectrum.rosco.com/the-basics-of-film-lighting ; powtoon.com/blog/veo-3-video-prompt-examples/ ; developers.openai.com/cookbook Sora 2 guide

---

## 4. Lens / depth-of-field language

| Term | Effect |
|---|---|
| 16–24mm wide | Exaggerated depth, vast environment, distortion near edges |
| 35mm | Natural documentary eye; the default "cinematic realism" tag ("shot on 35mm film") |
| 50mm prime | Human-eye perspective, intimacy |
| 85–135mm telephoto | Compression, flattened layers, isolated subject, creamy bokeh |
| Anamorphic 2.0x | Oval bokeh, horizontal flares, epic scope — strongest single "cinematic" cue |
| Shallow DOF (f/1.8–2.8) | Subject sharp, world blurred; attention control |
| Deep focus (f/8–11) | Everything sharp; dread via clarity, Kubrick wides |
| Rack focus | Pulls focus foreground↔background mid-shot; the "it's behind you" device |
| Black Pro-Mist 1/4 | Bloomed highlights, softened contrast (Sora 2 cookbook uses this verbatim) |
| Film grain, 180° shutter, halation | Photochemical texture cues that read as "real film" |

Weak → strong: "Cinematic look" → "Anamorphic 2.0x lens, shallow DOF, volumetric light."
Camera/lens simulation reads as realism: "shot on 35mm film, shallow depth of field"
beats "professional video."

Sources: adobe.com camera-shots guide ; developers.openai.com/cookbook/examples/sora/sora2_prompting_guide ; sider.ai/blog/ai-tools/how-to-prompt-sora-2-for-cinematic-videos-a-director-s-playbook
