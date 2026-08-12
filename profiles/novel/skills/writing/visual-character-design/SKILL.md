---
name: visual-character-design
description: "Build art-ready visual character profiles from character sheets. Specific enough to draw from or feed to image models. Includes humanizer pass for visual-specific AI tells."
version: 1.0.0
---

# Visual Character Design

Build visual reference documents that artists and image models can work from. Transforms character sheets (personality, arc, voice) into physical appearance descriptions with hex color palettes.

## When to use

- User asks for "visual profiles", "character art descriptions", "appearance references", "what do they look like"
- Preparing art direction for illustrator or image generation
- Building visual consistency across a project

## Process

1. **Pull character sheets** — read protagonist + companions from vault
2. **Check species/worldbuilding docs** — verify established visual canon before inventing
3. **Write profiles** — one section per character (see structure below)
4. **Humanizer pass** — critical; visual descriptions accumulate AI tells faster than narrative prose
5. **Save to vault** — `02-Characters/visual-profiles.md` or similar

## Structure per character

- **Face** — bone structure, skin tone/color, distinguishing features, scars/marks
- **Eyes** — color with specific shade reference, shape, notable qualities
- **Hair** — color, length, style, texture, organic elements
- **Build** — height, frame, muscle, movement patterns
- **Clothing** — layers, materials, colors, practical details
- **Weapons/Magic** — visible gear, how magic manifests visually
- **Posture and manner** — how they hold themselves, physical tics from dialogue section
- **Palette table** — hex codes for every element

See `references/visual-profiles-workflow.md` for detailed workflow and AI-tell patterns specific to visual descriptions.

## Pitfalls

- Don't skip the humanizer pass — visual descriptions are AI-tell magnets
- Don't invent visual canon if species docs already establish appearance
- Don't use negative definitions ("no X, no Y") — describe what IS there
- Don't skip hex codes — essential for consistency across art/generation
- Don't make every character equally detailed — match to narrative importance
- Don't forget physical tics from character sheet dialogue sections

## User-edit workflow

User frequently edits visual profiles directly and drops their version in chat. When this happens:
1. Read their version carefully — note what they changed vs your draft
2. Apply their changes to the vault file (don't re-present the whole thing)
3. Cascade any fact changes to character sheets and canon (species, parentage, age, etc.)
4. Common user corrections: height/build adjustments, hairstyle preferences, skin tone wording, removing decorative details

## Relationship to other skills

- **character-builder**: builds personality/arc/voice. This skill takes those sheets as INPUT and produces visual appearance.
- **humanizer**: the humanizer pass is mandatory here. See reference file for visual-specific patterns.
- **narrative**: this skill feeds into narrative when describing characters in prose.
