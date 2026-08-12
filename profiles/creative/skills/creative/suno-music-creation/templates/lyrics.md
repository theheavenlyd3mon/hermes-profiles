# Suno Lyrics & Lyrical Prompt Template

## Two Modes

| Mode | When to Use | Output |
|---|---|---|
| **Full Lyrics** | User provides a clear theme/concept | Complete lyrics with metatags, ready to paste into Suno Custom mode |
| **Lyrical Prompt** | User wants Suno to write the words | A lyrical direction prompt for the Style field or as instructions alongside a short lyric seed |

---

## Mode 1: Full Lyrics Structure

```
[Intro — {{section_desc}}]
({{delivery_direction}})
{{intro_lines}}

[Verse 1 — {{section_desc}}]
({{delivery_direction}})
{{verse_1_lines}}

[Pre-Chorus — {{section_desc}}]
({{delivery_direction}})
{{prechorus_lines}}

[Chorus]
({{delivery_direction}})
{{chorus_lines}}

[Verse 2 — {{section_desc}}]
({{delivery_direction}})
{{verse_2_lines}}

[Bridge — {{section_desc}}]
({{delivery_direction}})
{{bridge_lines}}

[Chorus]
({{delivery_direction}})
{{chorus_lines}}

[Outro — {{section_desc}}]
({{delivery_direction}})
{{outro_lines}}
```

### Section Fields

| Metatag | DSL Layer | Energy | Purpose |
|---|---|---|---|
| `[Intro]` | L0 | b=0, E=1-2 | Set atmosphere, no beat yet |
| `[Verse 1]` | L1 | b=0, E=3-4 | Storytelling, world-building |
| `[Pre-Chorus]` | L2 | dE/dx>0, E=5-7 | Tension ramp, shorter lines |
| `[Chorus]` | L3 | b=1, E=8-10 | Peak energy, hook, repetition |
| `[Verse 2]` | L1-L2 | b=0→1, E=4-6 | Story deepens, more energy |
| `[Bridge]` | L4 | dE/dx<0, E=2-5 | Shift in perspective, stripped |
| `[Outro]` | L5 | lim E→0, ⊘ | Resolution, fade or cut |

---

## Mode 2: Lyrical Prompt for Suno

Use when the user wants Suno's AI to generate lyrics. Write a lyrical direction into the Style field or as a short instruction:

```
Lyrical Theme: {{theme_sentence}}
Imagery: {{imagery_keywords}}
Tone: {{tone_description}}
Hook Concept: {{hook_concept}}
Structure Hints: {{structure_notes}}
```

### Example

User says: "RIVEN song about being replaced. Angry but not yelling."

**Lyrical Prompt for Style field:**
```
Lyrical Theme: A man realizes he's been replaced and the quiet fury of
being erased without a goodbye.
Imagery: Empty shelves, deleted photos, a key that doesn't fit anymore,
someone else's coat on the hook.
Tone: Controlled anger. Not yelling — precision. The coldest words hit
hardest. Short, cutting sentences.
Hook Concept: "New Name" — repeating hook about how she tells his story
now with someone else's name in his part.
Structure: Verse 1 is confusion (sparse), Chorus is clarity (full),
Verse 2 is anger (tense, rhythmic), Bridge is resignation (stripped),
Outro is silence.
```

---

## Vocal Performance Tags

| Tag | Meaning | Use When… |
|---|---|---|
| `[Whispered]` | Breath/hush delivery | Intimate moments, fragile bridge sections |
| `[Spoken Word]` | Not sung, rhythmic speech | RIVEN verse intros, conversational |
| `[Belted]` | Full voice, powerful | SOLA bridge climax, emotional peak |
| `[Breathy]` | Air in the voice | SOLA intimate verses, near-microphone |
| `[Falsetto]` | High register, lighter | RIVEN ad-libs, hook tags |
| `[Sung-Rap]` | Melodic, rhythmic, not quite sung | RIVEN verses, Bryson/Drake style |
| `[Harmonies]` | Layered vocal stack | Chorus second pass, bridge buildup |
| `[Building Energy]` | Crescendo in delivery | Pre-chorus tension ramp |
| `[Quiet Arrangement]` | Sparse backing | Bridge, early verses |

---

## Phonetic Tricks (Suno Pronounces What It Reads)

| Issue | Fix | Example |
|---|---|---|
| Odd pronunciation | Spell phonetically | "through" → "thru" |
| Syllable control | Hyphenate | "remember" → "re-mem-ber" |
| Sustained notes | Vowel extension | "love" → "lo-o-o-ove" |
| Emphasis | ALL CAPS | "NEVER again" = hit the word hard |
| Numbers | Spell out | "24/7" → "twenty four seven" |
| Acronyms | Space or hyphen | "AI" → "A I" |

---

## Character Limits

- **Suno Style field:** ~1,000 chars (use them)
- **Suno Lyrics field:** ~3,000 chars (~40-60 lines)
- Keep metatag count per section: 5-8 max

---

## Workflow Examples

### Brief → Full Lyrics Output

**User:** "SOLA song about finding your voice after being silenced. Slow build, ethereal, 70 BPM, Fm."

**Output template:**
```
[Intro — atmospheric, voice alone]
(Whispered, fragile)
I forgot the sound of my own voice
Didn't recognize it when it came back

[Verse 1 — sparse piano, b=0]
(Breathy, intimate, low register)
They told me quiet was a virtue
So I learned to disappear
I kept my words inside a bottle
Sank it in a river somewhere

[Pre-Chorus — pad enters, dE/dx>0]
(Building warmth)
But the river's running dry now
And the bottle's coming up

[Chorus — full warm production, b=1, E=8]
(Smoky, sustained, layered)
I'm singing again
Didn't know I still knew how
I'm singing again
Louder than I'm scared now

[Bridge — stripped to keys]
(Whispered, rising to belt)
For every year I didn't speak
For every word I held inside
This one's for the girl who thought
She'd already died

[Chorus — full, final]
(Layered harmonies, sustained)
I'm singing again
I'm singing again

[Outro — float out]
(Whispered, fading)
Singing again...
```
