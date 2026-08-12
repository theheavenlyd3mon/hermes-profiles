# Prompt Library — Verbatim Examples, Annotated

Proven FLUX 3 (and transferable) prompts. Each keeps its source attribution and
carries a one-line note on WHY it works. Steal structure and phrasing; swap the
subject. All follow the anatomy in SKILL.md: shot → subject action w/ timing →
environment motion → Audio: → Style: → Constraints:.

---

## Flick.art FLUX 3 guide
Source: https://flick.art/blog/flux-3-guide

> Slow aerial push over a rain-soaked futuristic city at night. Neon signs reflect in puddles below, steam rises from street vents, distant traffic hums, and a low synth drone builds under the shot. Cinematic realism, wet asphalt, volumetric light, no readable text, no logos.

WHY: one shot, one move; ambience + SFX + score all named; explicit text/logo ban.

> Locked-off medium shot of a tired astronaut sitting alone inside a dim spacecraft cockpit. At the start, only the soft instrument panel glow lights their face. After three seconds, a red warning light begins pulsing. The astronaut slowly turns toward the window as distant debris taps against the hull. Audio: low spacecraft hum, faint alarm pulse, subtle breathing inside the helmet, no music. Cinematic realism, shallow depth of field, no text, no extra characters.

WHY: timing beat ("after three seconds"); SFX bound to visible events; "no music" stated.

> Slow handheld tracking shot behind a detective walking down a narrow motel hallway at midnight. The detective moves cautiously, one hand near the wall, then stops when a door creaks open at the end of the hall. Fluorescent lights flicker overhead, dust floats in the air, rain runs down the window at the far end. Audio: soft footsteps on carpet, low motel electricity hum, distant rain, one sharp door creak, no music. 1970s neo-noir, 35mm film grain, warm green fluorescent cast, realistic motion. No readable text, no logos, no extra people.

WHY: period + film-stock style block; layered audio; movement + a change over time.

> Close-up of an exhausted pilot in a dim cockpit, helmet visor half raised. The pilot looks down, breathes once, then says quietly: "We are not going back." Warning lights pulse across their face as the camera slowly pushes in. Audio: cockpit hum, soft alarm beeps, intimate dry dialogue, no music. Cinematic sci-fi realism, shallow depth of field, preserve face, no text.

WHY: dialogue with a VISIBLE speaker (so it renders as speech, not burned-in text); "preserve face".

> Locked-off wide shot of an empty farmhouse hallway at night. At first nothing moves. After four seconds, a floorboard creaks off-screen, then the hanging light swings slightly. Audio: deep room tone, distant wind, single floorboard creak, faint chain movement, no music. Natural darkness, practical bulb light, realistic horror atmosphere, no visible monster.

WHY: pure withhold — sound precedes image; "no visible monster" is the suspense constraint.

> Slow studio orbit around a matte black cinema camera on a reflective table. Light sweeps across the lens glass as the camera rotates, revealing subtle dust particles in the air. Audio: quiet mechanical rotation, soft room tone, no music. Premium commercial lighting, crisp reflections, minimal background. No logos, no text, keep object shape consistent.

WHY: product-shot template; "keep object shape consistent" guards against morph.

> Wide cinematic shot of ancient ships cutting through dark water at dawn. Oars move in rhythm, sails snap in the wind, mist wraps around rocky cliffs. Audio: waves against wood, distant sailcloth snapping, low wind, subtle drum pulse. Historical epic realism, warm sunrise, 70mm texture, grounded scale. No modern objects, no fantasy creatures, no readable text.

WHY: era-locked with negative constraints ("no modern objects") to keep the world coherent.

---

## X / @umesh_ai — split-screen nursery monitor
Source: https://x.com/umesh_ai/status/2082052078730633307

> 15-second split-screen video, two equal vertical halves, one continuous take, no cuts. Both cameras show the same event at the same time, perfectly frame-synchronized. Scene: A house at night. A nursery upstairs; a kitchen downstairs. Left: Camera in the kitchen. A tired mother stands at the counter warming a bottle, a baby monitor screen beside her showing grainy black-and-white video of the nursery: crib, mobile, sleeping baby. Show only the kitchen and the monitor screen. The real nursery is never directly visible on the left. Right: Camera mounted high in the actual nursery — the exact same view the monitor shows, but in full color and clarity. Everything on the monitor screen in the left half must match this right half frame by frame: same crib, same baby, same movements, converted to grainy monochrome on the little screen.
> 0–5s: Right: the crib mobile begins turning slowly on its own; no one is in the room. Left: on the monitor screen, the same mobile turns; the mother doesn't notice, she's testing the bottle on her wrist. 5–10s: Right: the nursery door behind the crib drifts open a few centimeters. Left: same drift on the monitor; the mother glances at the screen, pauses, unsure, steps closer. 10–15s: Right: a cat walks in through the open door, jumps onto the crib rail, and the mobile stops. Left: the mother sees the shape on the grainy screen, tenses — then recognizes the cat, exhales, and smiles, bottle in hand. Final frame: both halves showing the cat curling up, monitor and reality identical. Every motion in the nursery must appear on the kitchen monitor at the same frame. No cuts, no lag between right half and monitor, no extra figures.

WHY: the split-screen masterclass — per-half visibility rules + frame-sync matching rules
+ timed beats + explicit desync prohibitions ("no lag", "no extra figures").

## X / @umesh_ai — split-screen fisherman (opening)
Source: https://x.com/umesh_ai/status/2082010903097311553

> 15-second split-screen video, two equal vertical halves, one continuous take, no cuts. Both cameras show the same event at the same time, perfectly frame-synchronized. Scene: Calm lake at dusk. An old fisherman in a small wooden rowboat pulls a rope from the water. Left: Water-level camera from another boat. Show only the fisherman, boat, rope above water, ripples, and splashes. Nothing below the waterline is visible. Right: Underwater camera looking up. The rope leads to a sunken bicycle tangled in glowing green weeds, surrounded by small silver fish.

(+ rules: parts "must appear above water on the left only when that exact part crosses
the waterline on the right… same height, angle, motion, rope tension, splashes, and
timing frame by frame… No duplicate bicycle, broken rope, teleporting, timing offset,
or camera change.")

WHY: a physical seam (the waterline) drives the matching rule; prohibitions name the
exact artifacts to avoid ("no timing offset").

---

## X / @JulienAIArt — surreal western with full audio direction (abridged)
Source: https://x.com/i/status/2081134611443413453

> Cinematic dark surrealist western, photorealistic, anamorphic 35mm, heavy film grain, high contrast, blown orange sky, deep blacks, shallow depth of field. Setting: an endless orange sand desert under a burning yellow sky... 0sec to 5sec: WIDE and low from the sand, the two of them far apart on opposing dunes... Then both draw at once. Camera locked. 5sec to 10sec: HARD CUT to over the Nun's shoulder... Audio: heavy percussive gunshots with long desert reverb, wind across sand, coat and fabric snap, shell casings ringing on hard ground, a low driving score building through the exchange and cutting out dead at the final standoff. No dialogue, no voiceover, no narration. Style: photorealistic, practical film look, real weight to bodies and fabric, no CG gloss…

WHY: multi-shot INSIDE one generation via "HARD CUT"; a dense style prefix; audio
score "cutting out dead" as a deliberate silence beat.

---

## X / @heavypulp — dialogue control pattern
Source: https://x.com/heavypulp/status/2079629061836472762

> ...both characters speak in this clip, one at a time, never overlapping: she speaks on camera; his single reply arrives as a voice off-frame… Speaks spaced, low warm alto, soft Greek accent: Keep this house. Beat. Be ageless. Beat. Softer: Forever.

WHY: "one at a time, never overlapping" + voice qualities (register, accent) + "Beat."
pauses + delivery direction ("Softer:") = precise spoken-line control.

## X / @junwatu — let-the-model-improvise dialogue
Source: https://x.com/junwatu/status/2081345133224640916

> A cinematic conversation between a large stone golem and a rugged forest troll… The golem speaks in a deep rumbling voice, the troll replies in a rough gravelly tone… (Automatically generate their full dialogue and burn subtitles on screen for everything they say).

WHY: the opposite pattern — describe the situation + voices and let the model write the
lines; note subtitles are EXPLICITLY requested here (so they're wanted, not accidental).

---

## X / @Maddox_Digital — single-take action skeleton
Source: https://x.com/Maddox_Digital/status/2081441388747796875

> Hyper realistic blockbuster cinematic 15-second action sequence in one true unbroken continuous shot, with no cuts, no morphing, and no scene transitions. [Detailed subject/action]. Camera begins [start framing] then [precise choreography with timing]. [Physics, lighting, environment details]. Seamless throughout, consistent characters and world.

WHY: the reusable action template — the anti-artifact constraint line ("one true
unbroken continuous shot, no cuts, no morphing") is the morph fix.

---

## fluxproai.net parameterized templates
Source: https://www.fluxproai.net/

Product video:
> Create a [duration] second cinematic product video of [product] on [surface/environment]. The camera begins with a close macro detail of [specific product feature], then slowly pulls back to reveal the full product. Lighting is [lighting style], color palette is [brand colors], and the mood is [premium/minimal/energetic/technical]. Add subtle audio: [sound effects], [music mood], and a clean final accent when the product name appears. Keep the product shape accurate, preserve logo placement, avoid warped text, avoid extra reflections, and keep the background uncluttered.

Image-to-video:
> Animate the reference image into a natural [duration] second scene. Keep the character identity, face shape, hairstyle, outfit, and color palette consistent. The character [action], while the camera [camera movement]. The environment is [setting], with [lighting] and [atmosphere]. Add natural audio: [room tone], [physical sound], and optional dialogue in [language] with [tone]. Avoid face flicker, changing clothing, extra limbs, unstable eyes, and sudden background shifts.

Keyframe transition:
> Generate a smooth transition from Keyframe A: [describe first image] to Keyframe B: [describe second image]. The transition should feel [natural/cinematic/surreal/technical]. Keep [stable elements] consistent while [changing elements] transform over time. Camera movement is [movement]. Audio begins with [start sound], builds with [middle sound], and resolves with [end sound]. Avoid abrupt morphing, melted objects, unstable faces, and inconsistent lighting.

WHY: fill-in-the-blank skeletons for the three common jobs; each ends with an
artifact-specific prohibition list and an audio arc (begins/builds/resolves).

---

## Cross-model fragments worth stealing
(From Runway / Sora 2 / Kling / Veo guides — vocabulary FLUX 3 also understands.)

Runway Gen-4 (https://help.runwayml.com/hc/en-us/articles/39789879462419-Gen-4-Video-Prompting-Guide):
- "the handheld camera tracks the mouse as it scurries away."
- Rule: focus the prompt on MOTION; phrase positively — "Camera holds completely static" not "no camera movement". (Note: FLUX 3 video tolerates explicit negatives — see SKILL.md tension note.)

Sora 2 cookbook (https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide):
- Structure block: "Camera shot: wide shot, low angle / Depth of field: shallow (sharp on subject, blurred background) / Lighting + palette: warm backlight with soft rim"
- Shot-list style: "0.00–2.40 — 'Arrival Drift' (32mm, shoulder-mounted slow dolly left). Camera slides past platform signage edge; shallow focus reveals traveler mid-frame… train headlights flare softly through mist."
- Format tokens: "180° shutter; digital capture emulating 65mm photochemical contrast; fine grain; subtle halation on speculars" / "Black Pro-Mist 1/4"

Kling AI (https://kling.ai/blog/kling-ai-prompt-guide):
- Structure: Subject → Action → Scene → Camera → Lighting/Mood.
- Camera lines: "The camera slowly pushes toward the subject" · "The camera pans across the room or tilts up to the sign" · "The camera follows beside the runner" · "Close-up on the speaker's face."
- Atmosphere: name visible details — "haze, rim light, long shadows, soft golden sunlight, cold blue night tones, reflections on wet pavement."

Veo 3 (https://deepmind.google/models/veo/prompt-guide/):
- "A medium shot frames an old sailor, his knitted blue sailor hat casting a shadow over his eyes, a thick grey beard obscuring his chin. He holds his pipe in one hand, gesturing with it towards the churning, grey sea beyond the ship's railing."
- "A snow-covered plain of iridescent moon-dust under twilight skies. Thirty-foot crystalline flowers bloom, refracting light into slow-moving rainbows. A fur-cloaked figure walks between these colossal blossoms, leaving the only footprints in untouched dust."
- Audio inline: "Audio: crunchy, sugary typing sounds, delighted giggles."
- Found-footage cue: "The camera is often shaky… catching unintentional lens flares from the natural, often harsh, sunlight."

Runway Gen-4.5 community (https://imagine.art/blogs/runway-gen-4-5-prompt-guide):
- "A handheld low angle tracking shot, with low contrast and fast-paced motion, follows a skilled astronaut skateboarder on a moon landscape… Film grain, low contrast, black and white."

Sora generic formula (https://academy.techpresso.co/prompts/sora-prompts):
- "A [subject] [action] in [environment]. Shot on 35mm film with shallow depth of field, golden hour lighting. Camera slowly tracks left to right."

WHY (all of the above): concrete camera + lens + lighting nouns beat vague "cinematic";
audio named inline; motion is the subject of the sentence.
