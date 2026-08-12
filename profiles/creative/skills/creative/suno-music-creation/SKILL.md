---
name: suno-music-creation
description: "Generate Suno-ready style prompts, lyrics, and DSL energy arcs from a user brief. Supports RIVEN (trap soul/dark R&B male — J. Cole × Drake × Kid Laroi × Bryson Tiller) and SOLA (alt-R&B/neo-soul female — Kehlani × SZA × Ella Mai × Summer Walker × Billie Eilish) artist identities."
related_skills: [songwriting-and-ai-music]
platforms: [macos, linux]
triggers:
  - suno style prompt
  - suno lyrics
  - suno prompt
  - make a track
  - create a suno song
  - riven song
  - sola song
  - dsl energy arc
  - half the distance
  - rivsol
---

# Suno Music Creation — Brief → Full Output Pipeline

## When to Use

A user gives you a brief (genre, mood, theme, artist choice, BPM, key)
and you produce:

1. **DSL Style Prompt** — A complete DSL + plain-text block that goes
   directly into Suno's Style field. This IS the style prompt.
2. **Lyrics OR Lyrical Prompt** — Full lyrics with metatags, or a lyrical
   direction for Suno to write from.

The DSL block replaces the traditional [Genre:][Mood:][Instruments:]
[bracket] format entirely — it's more precise and Suno understands it.

---

## Complete Workflow

### Step 1 — Parse the Brief

Extract these from the user's message:

- **Artist** — RIVEN, SOLA, or MyGame (collab), or a new artist
- **Theme/Concept** — What's the song about? (one sentence)
- **Mood** — 2-4 adjectives
- **Genre** — Base genre + hybrid (becomes the final tag)
- **BPM + Key** — If not given, default to artist preset (RIVEN: 72 Dm/Fm, SOLA: 74 Fm/C)
- **Mode** — Full lyrics or prompt-only for Suno to write?

### Step 2 — Load Artist DNA

Before writing anything, consult the artist profile to ground the
song in the correct vocal, production, and thematic territory:

| What to Load | Source | RIVEN | SOLA |
|-------------|--------|-------|------|
| Artist profile | \`riven-sola-profiles.md\` | J. Cole × Drake × Kid Laroi × Bryson Tiller | Kehlani × SZA × Ella Mai × Summer Walker × Billie Eilish |
| Vocal signature | Profiles doc | Sung-rap, conversational, gritty belt, close-mic | Silky breathy, runs, harmonies in 3rds, whisper-to-power |
| Production DNA | Profiles doc | 808 glide, ambient pads, Rhodes, sparse percussion | Rhodes/Wurlitzer, warm sub, brushed trap, lush space |
| Thematic territory | Profiles doc | Late-night introspection, regret, emotional whiplash | Self-discovery, arrival, clarity, safe warmth |
| Chord zones | Profiles doc, references/chord-progressions.md | Minor: i–bVI–bVII–i, i–iv–v–iv | Maj7: Imaj7–vi7–IVmaj7–V7, vi–IV–I–V |

### Step 3 — Apply Prosody Framework

Determine if the song's emotional intent is **stable** or **unstable** (or a
shift between them). This governs rhyme choice, harmonic feel, and arrangement
density. Reference \`../../songwriting-and-ai-music/references/prosody-framework.md\`.

**For RIVEN:** Default to UNSTABLE — slant/assonance rhymes, extended minor chords,
breathy-to-belted dynamics, syncopated delivery. Moments of stability hit harder
because they're earned.

**For SOLA:** Default to STABLE — perfect/family rhymes, maj7 warmth, on-pocket
delivery, full warm arrangement. Moments of instability add emotional depth.

### Step 4 — Select DSL Energy Arc

Choose from 12 arcs in \`templates/dsl-arc.md\`:

| For RIVEN | For SOLA | For Both |
|-----------|----------|----------|
| Classic Build-Drop (#1) | Slow Float (#2) | One-Way Crescendo (#3) |
| Stutter Dynamics (#4) | Float with Spike (#7) | Anti-Chorus (#8) |
| Ambient Explosion (#5) | Slow Burn (#10) | |
| Crescendo Collapse (#6) | Whisper Cascade (#12) | |
| Jagged Push-Pull (#9) | | |
| Stutter-Step Drop (#11) | | |

Match the arc to the emotional intent: a regret song gets a different arc
than a confident one.

### Step 5 — Apply Section Texture Template

Use the section texture tables (below) to map each section's production
language. Every section has a specific instrumentation, vocal delivery,
and texture target. This becomes the texture words in DSL Lx lines.

### Step 6 — Build the DSL Style Prompt

Combine arc + section textures into the DSL block:

```
$S(x)$ lifecycle [overall energy arc from chosen pattern],
$E(x)$ [specific energy curve matching the arc],

[L0-L5 lines — each = DSL notation + texture words from section textures],

[Final genre tag] [BPM] [Key] [theme descriptor]
```

**Rules:** Lines 1-3 = energy function. L0-L5 = layer lines with notation +
texture words. Final line = genre tag. DO NOT wrap DSL in [brackets].

### Step 6b — Check Persona & Build Style Tags

> **Persona = artist identity.** **Style prompt = producer brief.**
> With Persona active: 4–7 tags. Without Persona: 8–15 tags.

Compose the non-DSL tags using the **5-Part Style Prompt Formula** (see below)
and the vocal stack templates at \`references/vocal-stacks.md\`.

**Without Persona — full combined block:**
```
$S(x)$ lifecycle ..., [DSL block],
[5-part tags with full production], [BPM], [Key]
```

**With Persona — shorter:**
```
[Persona fills identity] $S(x)$ ... [DSL],
[4–7 genre/production tags] [BPM] [Key]
```

### Step 7 — Write Lyrics or Lyrical Prompt

**Pull sensory imagery** from \`references/sensory-word-banks.md\` to avoid
generic language. Use per-artist word banks organized by sense.

**Apply the artist's rhyme strategy:**
- **RIVEN:** Slant/assonance primary, internal rhymes for density,
  perfect rhymes for impact moments
- **SOLA:** Perfect/family rhymes primary, assonance for emotional depth

**If Full Lyrics:** Use \`templates/lyrics.md\`. 4-8 lines per section.
Match DSL layer arc. Add vocal direction from vocal stacks as [metatags].
Use phonetic respelling for tricky words.

**If Lyrical Prompt:**
```
Lyrical Theme: {one sentence}
Imagery: {3-5 keywords from sensory word banks}
Tone: {delivery style from vocal stacks}
Hook Concept: {the repeated line / title}
Structure Hints: {section notes}
```

### Step 8 — Present the Output

```
## DSL Style Prompt (paste into Suno's Style field)

[DSL block + style tags]

## Lyrics (paste into Suno's Lyrics field)

[Section tags + lyrics + inline cues]
```

If Persona exists, remind user to select it in Custom Mode before pasting.

---

## Artist DSL Presets

### RIVEN — Default DSL Arc
```
$S(x)$ lifecycle $dE/dx>0 \to b=1 \to 0$,
$E(x)$ monotone $dE/dx>0$ L0-L2
then $b(x):0\to1$ at $x=\gamma$ $E_{max}$
then $dE/dx<0$ to $\lim E=0$,

L0-L1 EXTENDED slow $\nearrow$ ambient $b=0$ sustained sparse piano atmosphere,
L2 $30eE$ swell tension building hi-hats enter,
L3 sudden $b=1$ $E_{max}$ catastrophic 808 sub-bass drop,
L4 $\phi'_j\sim\mathcal{N}(0, \sigma^2)$ $\infty$ $dE/dx<0$ chaotic breakdown noise,
L5 instant snap $\lim_{x\to1}E=0$ $\oslash$ silence,

Trap soul dark noir {custom_tag}
```

### SOLA — Default DSL Arc
```
$S(x)$ lifecycle $dE/dx>0$ gradual $b=0$ sustained,
then $dE/dx<0$ to $\lim E=0$,
$E(x)$ slow rise to $E=6$ held then $dE/dx<0$,

L0 voice keys $b=0$ intimate breathy solo,
L1 $dE/dx>0$ warm bass pad enters,
L2 $E=6$ sustained chorus bloom full warmth,
L3 bridge $dE/dx>0$ to $E=8$ emotional belt peak,
L4 $\lim E\to0$ float to silence breath fade,

Alt-R&B neo-soul ethereal {custom_tag}
```

---

## The 5-Part Style Prompt Formula

For every Suno generation, structure the non-DSL tags in the Style
field around these five pillars. Optimal: 8–15 total tags.

| Part | What | RIVEN Example | SOLA Example |
|------|------|---------------|--------------|
|| 1. Genre + Subgenre | trap soul, neo-soul | `trap soul, dark R&B, melodic rap` | `neo-soul, alt-R&B, ethereal R&B` |
|| 2. Mood + Energy | 2–4 adjectives | `dark, intimate, brooding, nocturnal` | `warm, ethereal, dreamy, celestial` |
|| 3. Vocal Direction | Character + delivery | `raspy male sung-rap, close-mic intimate, gritty belt on hook, conversational verses` | `silky female with runs and melisma, breathy warm delivery, harmonies in 3rds, close-mic intimacy` |
|| 4. Instrumentation | Specific textures | `heavy 808 with glide and long decay, atmospheric pads, Rhodes electric piano, hi-hat micro-rolls, restrained sparse percussion` | `Rhodes/Wurlitzer electric piano, warm sub-bass (round attack), brushed trap drums, lush reverb, sparse arrangement` |
|| 5. Production + Tempo | Mix quality + BPM | `tape saturation, behind-the-beat swing, sidechain low end, 72 BPM` | `analog warmth, spacious cinematic reverb, room to breathe, 74 BPM` |

**Gold standard RIVEN example:**
```
trap soul, dark and intimate, raspy male vocals with sung-rap delivery, heavy 808 sub-bass with long decay, atmospheric pads, electric piano, hi-hat rolls with trap pocket, close-mic intimate verses, full saturation on chorus, 72 BPM, F minor
```

**Gold standard SOLA example:**
```
neo-soul, warm and ethereal, silky female vocals with runs and melisma, Rhodes electric piano, warm sub bass, brushed trap drums, layered R&B harmonies on chorus, breathy lead with doubled center, 74 BPM, F minor
```

---

## Section Texture Templates

Translate each song section into production language that Suno
understands. These map onto the L0-L5 layer structure in the DSL.

### RIVEN Section Textures

| Section | L# | Texture Words | Vocal | Instrumentation |
|---------|----|--------------|-------|-----------------|
| **Intro** | L0 | sparse, minimal, atmospheric, foreshadowing | none or breathy murmur | electric piano, ambient pad, sub-bass heartbeat |
| **Verse 1** | L1 | intimate, close-mic, conversational, unfolding | breathy sung-rap, low register | keys + 808 (heartbeat) + light hi-hats |
| **Pre-Chorus** | L2 | tension rising, swelling, reaching | higher register, urgency enters | hi-hat rolls, snare build, pad swell |
| **Chorus** | L3 | full saturation, catastrophic, the drop | gritty belt, doubled vocal, slight rasp | full 808 with long decay, all layers |
| **Breakdown** | L4 | chaotic, glitch, noise | distorted fragments | static, cut-up elements |
| **Bridge** | L4 | stripped, vulnerable, the lowest point | whispered, raw, cracked | keys + voice only (maybe 808 heartbeat) |
| **Outro** | L5 | decay, silence, cut | breath fade, vocal fry | 808 trails out, elements drop one by one |

### SOLA Section Textures

| Section | L# | Texture Words | Vocal | Instrumentation |
|---------|----|--------------|-------|-----------------|
| **Intro** | L0 | intimate, breath, space, waking | breathy solo, soft hum | voice + Rhodes/e-piano alone |
| **Verse 1** | L1 | warm, entering, blooming, safe | low register, smooth, conversational | add warm sub-bass, gentle brushed percussion |
| **Pre-Chorus** | L2 | lift, reaching, swelling, almost there | rising register, fuller tone | trap snare rolls, pad build, gentle lift |
| **Chorus** | L3 | full float, warm saturation, the arrival | sustained notes, layered harmonies in 3rds | full production, subby warm 808, all pads |
| **Bridge** | L4 | stripped, bare, the vulnerable truth | whisper to belt, emotional peak | voice + keys first, then slow build |
| **Outro** | L5 | safe landing, breath fade | breath fade, sustained note dissolving | elements drop one by one, Rhodes holds last chord |

---

## Expanded DSL Arc Patterns

Beyond the defaults, here are new energy arcs discovered from
contemporary songwriting research:

### "Crescendo Collapse" (RIVEN — aggressive)
```
L0-L1 slow ↗ ambient b=0 sustained sparse minimal,
L2 dE/dx>0 808 enters heartbeat,
L3 30eE swell trap rolls tension peaks,
L4 b=1 E_max full saturation EVERYTHING,
L5 instant ⊘ cut to silence,
(optional L6) b=0 whisper reprise
```

### "Float with Spike" (SOLA — dynamic warmth)
```
L0 voice keys b=0 intimate breath,
L1 dE/dx>0 warm pad slow bloom,
L2 E=6 sustained chorus full float,
L3 b=1 sudden to E=8 emotional spike belt,
L4 lim E→0 rapid decay to breath,
L5 b=0 held fade sustained warmth
```

### "Anti-Chorus" (both artists — subvert expectation)
```
L0-L1 build b=0 to b=1 classic tension,
L2 L3 E_max saturation full power pre-drop,
L3 L4 b=0 sudden drop to voice-keys only,
(the emptiness IS the impact)
L5 lim E→0 breath fade
```

### "Stutter Dynamics" (RIVEN — glitchy)
```
L0 b=0 ambient,
L1 ⊘ cut,
L2 b=1 E_max sudden,
L3 ⊘ cut,
L4 b=0 whisper,
L5 ⊘ silence
```

### "Slow Burn" (SOLA — extended float)
```
L0-L2 EXTENDED b=0 sustained ambient,
L3 dE/dx>0 very gradual warmth enters,
L4 E=6 held at peak no drop,
L5 lim E→0 gentle decay
```

---

## Templates and References in This Skill

### Templates

| Template | Location | Use |
|---|---|---|
| DSL Style Prompt Builder | `templates/style-prompt.md` | Building a complete DSL block from a brief. RIVEN/SOLA presets. |
| Lyrics & Prompt Guide | `templates/lyrics.md` | Full lyrics structure, lyrical prompt mode, vocal tags, phonetic tricks |
| DSL Arc Builder | `templates/dsl-arc.md` | DSL energy arc patterns, layer line components |

### References

| Reference | Location | Covers |
||---|---|---|
|| Suno Persona Workflow | `references/suno-persona-workflow.md` | Creating/using Personas, Persona + DSL hybrid, testing workflow, troubleshooting |
|| MyGame Project Context | `references/mygame-project-context.md` | RIVEN/SOLA/MyGame project details |
|| Artist Profiles (full) | `../../../../Documents/Projects/MyGame/docs/artist-branding/riven-sola-profiles.md` | Full artist DNA — reference blends, vocal signatures, production DNA, chord zones |
|| Sensory Word Banks | `../../../../Documents/Projects/MyGame/docs/artist-branding/references/sensory-word-banks.md` | Per-artist thesaurus by sense (sight/sound/touch/smell/taste/organic/motion) |
|| Section Texture Templates | `../../../../Documents/Projects/MyGame/docs/artist-branding/references/section-textures.md` | Per-section production guide for RIVEN, SOLA, and MyGame collab |
|| Chord Progression Cards | `../../../../Documents/Projects/MyGame/docs/artist-branding/references/chord-progressions.md` | 7 progressions per artist with emotional effect, bass strategy, arc pairing |
|| Vocal Stack Templates | `../../../../Documents/Projects/MyGame/docs/artist-branding/references/vocal-stacks.md` | Per-section vocal production descriptions, full Persona blurbs |
|| Rhyme Scheme Matrix | `../../../../Documents/Projects/MyGame/docs/artist-branding/references/rhyme-schemes.md` | 15 schemes with prosody effects, section recommendations |

---

## DSL Notation Reference

Used inside the DSL Style Prompt block:

| Symbol | Meaning |
|---|---|
| **$S(x)$** | Song structure function |
| **$E(x)$** | Energy level at position x |
| **$dE/dx > 0$** | Energy rising |
| **$dE/dx < 0$** | Energy falling |
| **$b=0$** | Ambient / calm / sustained |
| **$b=1$** | Full energy / dropped / saturated |
| **$L0, L1…** | Structural layers |
| **$\gamma$** | Peak / drop point |
| **$E_{max}$** | Maximum energy |
| **$\nearrow$** | Gradual crescendo |
| **$30eE$** | Exponential energy swell |
| **$\phi'_j \sim \mathcal{N}(0,\sigma^2)$** | Chaos / noise / glitch |
| **$\infty$** | Loop / repeat |
| **$\lim E \to 0$** | Energy decays to zero |
| **$\oslash$** | Silence / cut |

See full cheatsheet at:
`Documents/Projects/MyGame/docs/artist-branding/suno-dsl-cheatsheet.md`

---

## Example

**User:** "RIVEN song about driving through the city at 3AM regretting a breakup. 75 BPM."

→ Load this skill, then produce:

```
### DSL Style Prompt

$S(x)$ lifecycle $dE/dx>0 \to b=1 \to 0$,
$E(x)$ monotone $dE/dx>0$ L0-L2
then $b(x):0\to1$ at $x=\gamma$ $E_{max}$
then $dE/dx<0$ to $\lim E=0$,

L0-L1 EXTENDED slow $\nearrow$ ambient $b=0$ sustained windshield rain sparse keys,
L2 $30eE$ swell 808 enters city lights blur,
L3 sudden $b=1$ $E_{max}$ full drop empty passenger seat,
L4 $\phi'_j\sim\mathcal{N}(0, \sigma^2)$ $\infty$ $dE/dx<0$ broken signal radio static,
L5 instant snap $\lim_{x\to1}E=0$ $\oslash$ cut to silence,

Trap soul dark noir 75 BPM D minor late night drive

### Lyrics

...
```


---

*This skill works alongside `songwriting-and-ai-music` for foundational songwriting craft.*
