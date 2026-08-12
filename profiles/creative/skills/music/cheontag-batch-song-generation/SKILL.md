---
name: "cheontag-batch-song-generation"
description: "Generate multiple Suno-ready songs in one response: artist tracks using RIVEN/SOLA profiles and template tracks using hybrid songwriting methodologies. Supports batch outputs for creative music pipelines."
---

# Batch Song Generation for Suno

## Purpose
Use when the user requests multiple songs at once—typically 5 artist tracks + 5 template/variant tracks. This skill encodes the batch workflow, variation philosophy, and deliverable format.

## Workflow

### Step 1: Parse the Batch Brief
- Count = N total songs
- Split: N1 using **RIVEN** or **SOLA** / **MyGame** profiles (load `suno-music-creation` + `songwriting-and-ai-music`)
- Split: N2 using **template/methodology variants** (new hybrid techniques, structural experiments, or vibe-first prompts)

### Step 2: Generate RIVEN/SOLA Tracks
Use the 8-step pipeline from `suno-music-creation`:
1. Parse brief → artist, mood, concept, BPM, key
2. Load artist DNA
3. Apply prosody framework
4. Select DSL arc
5. Apply section textures
6. Build DSL style prompt
7. Write lyrics or lyrical prompt
8. Present

**Vary these per song to avoid repetition:**
- DSL energy arc (pick different patterns from the 12-arc library)
- BPM within artist range (RIVEN: 72–88, SOLA: 68–80)
- Key from artist palette (RIVEN: Dm, Ebm, Fm, Gm; SOLA: Cm, Fm, Abm, Bbm)
- Rhyme scheme (rotate AABB, ABAB, ABCB, AABBA partially)
- Section count (some 5-section, some 6-section)
- Lyrics mode: mix full lyrics with lyrical prompts

### Step 3: Generate Template/Methodology Tracks
Use alternate approaches to create distinct musical DNA:
- **Methodology A** — Vocal persona + genre mash notes (no artist persona): treat singer as a new character, build from instrument-first
- **Methodology B** — Rhythmic-first / groove-focused: describe the rhythmic feel and production texture, minimal lyrical constraint
- **Methodology C** — Cinematic narrative arc: structure around a short story or scene
- **Methodology D** — Instrumental-focused Dub/Ambient House: describe the DJ/producer side
- **Methodology E** — Show-don't-tell object writing: extract sensory phrases, then build lyrics solely from objects/textures

### Step 4: Assemble Deliverable
For every song produce:
- Title
- DSL Style Prompt (exactly as it goes in Suno's Style field)
- Lyrics field content OR lyrical prompt

### Step 5: Quality Check Formula
```
AestheticQuality? → distinct energy arcs, different themes
Accessible? → no trademarked names, phonetic respelling for tricky words
BrandConsistent? → if RIVEN/SOLA, profile matches known vocal/production DNA
FileSaved? → output to a clearly labeled batch file if requested
```

## Output Format
Use the standard Suno output structure for each song:

```
## TITLE — ARTIST / MIX
**BPM** | **Key** | **Arc**

### DSL Style Prompt
[exact block]

### Lyrics / Lyrical Prompt
[content]
```