# Suno DSL (Domain-Specific Language) — Math Notation for Song Structure

Suno's style/lyrics fields can understand mathematical DSL notation to describe
precise **energy curves, structural layers, and dynamic arcs** that plain English
struggles to capture concisely.

---

## Core Variables

| Symbol | Meaning | Range / Values |
|---|---|---|
| $S(x)$ | Song structure function (the whole track) | x = time position (normalized 0→1) |
| $E(x)$ | Energy level at position x | 0 (silence) → 10 (max saturation) |
| $dE/dx$ | Rate of energy change (derivative) | >0 = building, <0 = decaying |
| $b(x)$ | Binary state switch | 0 = ambient/sustained, 1 = dropped/saturated |
| $L0, L1, L2...$ | Structural layers / sections | Up to L5 or more |
| $\gamma$ | Peak/critical point (the drop) | Position of $E_{max}$ |
| $\nearrow$ | Gradual increase / crescendo | Use in layer descriptions |
| $\phi'_j \sim \mathcal{N}(0,\sigma^2)$ | Random/textural elements (Gaussian noise) | Chaotic improvisation, glitch, texture |
| $\infty$ | Infinite loop / repeating element | Can prepend to a layer label |

---

## How To Use In Suno

### THE CORRECT METHOD — Standalone DSL Block (entire Style Prompt)

The DSL block **IS the complete Style Prompt**. Paste it directly into Suno's
Style field. No [brackets], no Genre/Mood/Instruments wrappers needed.

```
$S(x)$ lifecycle $dE/dx>0 → b=1 → 0$,
$E(x)$ monotone $dE/dx>0$ L0-L2
then $b(x):0→1$ at $x=\gamma$ $E_{max}$
then $dE/dx<0$ to $\lim E=0$,

L0-L1 EXTENDED slow $\nearrow$ ambient $b=0$ sustained,
L2 euphoric jazz-trap $30eE$ swell,
L3 sudden $b=1$ $E_{max}$ maximum saturation catastrophic sub-bass,
L4 $\phi'_j\sim\mathcal{N}(0, \sigma^2)$ $\infty$ $dE/dx<0$,
L5 instant snap $\lim_{x\to1}E=0$ $\oslash$,

Progressive trap-jazz extended journey
```

**Structure of the block:**

| Part | Content | Example |
|---|---|---|
| 1. Energy function | $S(x)$, $E(x)$, $b(x)$ path across whole song | `$S(x)$ lifecycle $dE/dx>0 → b=1 → 0$` |
| 2. Layer breakdown | L0-L5: each line = DSL notation + 2-5 texture words | `L0-L1 EXTENDED slow ↗ ambient b=0 sustained sparse piano` |
| 3. Genre tag | Final line anchors the genre/hybrid + optional BPM/key | `Trap soul dark noir 75 BPM D minor` |

**⚠️ DO NOT** wrap DSL notation inside `[Dynamics DSL: ...]` brackets.
The whole block stands alone — no brackets on the outside either.

### Method 2 — Hybrid Mode (DSL + bracket tags)

If you want to add specific instrument/vocal/production details that DSL
doesn't cover, put the DSL block FIRST, then append [bracket] tags after:

```
$S(x)$ lifecycle $dE/dx>0 → b=1 → 0$,
...

Progressive trap-jazz extended journey

[Instruments: sparse piano, 808 sub-bass, ambient synth pads]
[Vocal Style: smooth baritone sung-rap, breathy falsetto ad-libs]
```

The DSL block remains the primary prompt — brackets are supplementary.

### Method 3 — Layer references in Suno lyrics with metatags

Use DSL layer labels inside lyrics metatags to keep the energy arc
visible in the Lyrics field:

```text
[Intro — L0, ambient b=0]
(extended slow build, sparse, atmospheric)

[Verse — L1, dE/dx>0 gradual]
(storytelling, low energy, sustained)

[Pre-Chorus — L2, 30eE swell]
(building tension, euphoric climb)

[Chorus — L3, b=1, Emax]
(full drop, catastrophic saturation, sub-bass peak)

[Bridge/Breakdown — L4, φ'j~N(0,σ²), dE/dx<0]
(chaotic textures, noise elements, energy decaying)

[Outro — L5, lim E=0, instant snap ⊘]
(abrupt silence, or fading to zero)
```

---

## Example: Progressive Trap-Jazz DSL Song (RIVEN-adjacent)

Full concept from conversation:

```
$S(x)$ lifecycle $dE/dx>0 → b=1 → 0$,
$E(x)$ monotone $dE/dx>0$ L0-L2
then $b(x):0→1$ at $x=\gamma$ $E_{max}$
then $dE/dx<0$ to $\lim E=0$,

L0-L1 EXTENDED slow ↗ ambient b=0 sustained,
L2 euphoric jazz-trap 30eE swell,
L3 sudden b=1 $E_{max}$ maximum saturation catastrophic sub-bass,
L4 $\phi'_j\sim\mathcal{N}(0, \sigma^2)$ $\infty$ $dE/dx<0$,
L5 instant snap $\lim_{x\to1}E=0$ $⊘$,

Progressive trap-jazz extended journey
```

**Translation:**
1. Very long ambient intro (L0-L1) — sparse, atmospheric, no drop
2. Massive energy swell into euphoric trap-jazz (L2) — exponential growth
3. Sudden full drop (L3) — maximum bass saturation, catastrophic peak
4. Chaotic noise/glitch breakdown (L4) — infinite-feeling loop, energy draining
5. Instant snap to silence (L5) — no fade, just \_cut\_

---

## Why It Works

- **Precision:** "gradually gets louder" is vague; "30eE swell" or
  "dE/dx>0 through L0-L2" is a specific rate and duration
- **Suno interprets math context:** The model picks up on energy curves
  implied by calculus-like notation even when it can't "solve" equations
- **Concision:** A paragraph of dynamics description compresses to one
  line of DSL
- **Layering:** Labeling sections L0-L5 gives Suno a numbered roadmap
  even without traditional [Verse]/[Chorus] metatags

---

## Tips

- Mix DSL with plain English on each layer line:
  `L3 sudden $b=1$ $E_{max}$ catastrophic 808 sub-bass drop`
- The `$...$` LaTeX delimiters are optional — the notation works
  without them in raw text
- `30eE`, `eE`, `e^x` all signal exponential energy growth
- `b=0` / `b=1` is the most reliably interpreted binary — Suno
  understands "ambient vs. full drop"
- `⊘` (silence symbol) and `∞` (infinity loop) are bonus markers
  for extreme dynamics
- The DSL block goes into the **Style field**, not the Lyrics field.
  Use DSL layer labels (L0-L5) in lyrics metatags to keep the arc
  visible there too.

### Related Skill

For the **brief → full output pipeline** (user gives a concept, you
produce DSL block + lyrics), load:

```
skill_view(name='suno-music-creation')
```

It includes RIVEN/SOLA presets, texture word banks, and layer arc
templates. See also:
`Documents/Projects/MyGame/docs/artist-branding/suno-dsl-cheatsheet.md`
