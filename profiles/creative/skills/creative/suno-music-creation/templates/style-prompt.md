# DSL Style Prompt Builder

## The Complete Style Prompt is a DSL Block

The DSL block goes **directly into Suno's Style field**. No [brackets] needed.
It has three parts:

```
$S(x)$ lifecycle [overall energy arc in math],
[layer-by-layer: Lx DSL notation + plain English texture],
[Final genre / hybrid tag with BPM and key]
```

---

## Structure Rules

### Part 1: Overall Energy Function (1-3 lines)

Describe the song's energy lifecycle mathematically:

| Pattern | Meaning |
|---|---|
| `$S(x)$ lifecycle $dE/dx>0 \to b=1 \to 0$` | Build up → drop → end |
| `$S(x)$ lifecycle $dE/dx>0$ gradual $b=0$ sustained then $dE/dx<0$` | Slow rise, sustained, gentle fall |
| `$S(x)$ $b=0 \to \phi'_j \infty \to \oslash$` | Ambient → chaos → cut |
| `$E(x)$ monotone $dE/dx>0$ L0-L2 then $b(x):0\to1$ at $x=\gamma$ $E_{max}$` | Steady climb to a peak drop |

### Part 2: Layer Breakdown (L0-L5)

Each layer line has: layer label + DSL notation + 2-5 plain English texture words

```
L0-L1 EXTENDED slow $\nearrow$ ambient $b=0$ sustained sparse piano atmosphere,
L2 $30eE$ swell tension building hi-hats enter,
L3 sudden $b=1$ $E_{max}$ catastrophic 808 sub-bass drop,
L4 $\phi'_j\sim\mathcal{N}(0, \sigma^2)$ $\infty$ $dE/dx<0$ chaotic breakdown noise,
L5 instant snap $\lim_{x\to1}E=0$ $\oslash$ silence,
```

**Layer-to-Section Mapping:**

| Layer | Song Section | Energy |
|---|---|---|
| L0 | Intro / Atmosphere | b=0, E=1-2 |
| L1 | Verse (first half) | b=0, dE/dx>0, E=2-4 |
| L2 | Pre-Chorus / Build | dE/dx>0, E=5-7 |
| L3 | Chorus / Drop | b=1, E_max=8-10 |
| L4 | Bridge / Breakdown | dE/dx<0 or φ'j, E=3-6 |
| L5 | Outro | lim E→0 or ⊘ |

### Part 3: Final Genre Tag

End with a concise genre/hybrid + optional BPM/key:

```
Progressive trap-jazz extended journey
Trap soul dark noir 75 BPM D minor
R&B alt-pop ethereal
```

---

## Artist-Specific Fill Patterns

### RIVEN Template
```
$S(x)$ lifecycle $dE/dx>0 \to b=1 \to 0$,
$E(x)$ monotone $dE/dx>0$ L0-L2
then $b(x):0\to1$ at $x=\gamma$ $E_{max}$
then $dE/dx<0$ to $\lim E=0$,

L0-L1 EXTENDED slow $\nearrow$ ambient $b=0$ sustained {texture},
L2 $30eE$ swell {texture},
L3 sudden $b=1$ $E_{max}$ {texture},
L4 $\phi'_j\sim\mathcal{N}(0, \sigma^2)$ $\infty$ $dE/dx<0$ {texture},
L5 instant snap $\lim_{x\to1}E=0$ $\oslash$ {texture},

Trap soul dark noir {BPM} {key} {theme_tag}
```

### SOLA Template
```
$S(x)$ lifecycle $dE/dx>0$ gradual $b=0$ sustained,
then $dE/dx<0$ to $\lim E=0$,
$E(x)$ slow rise to $E=6$ held then $dE/dx<0$,

L0 voice keys $b=0$ intimate {texture},
L1 $dE/dx>0$ warm {texture},
L2 $E=6$ sustained chorus {texture},
L3 bridge $dE/dx>0$ to $E=8$ {texture},
L4 $\lim E\to0$ float {texture},

R&B alt-pop ethereal {BPM} {key} {theme_tag}
```

### MyGame (Collab) Template
```
$S(x)$ lifecycle alternating $\to$ merged $\to$ alone,

L0 SOLA $b=0$ voice keys intimate,
L1 RIVEN enters $dE/dx>0$ 808 sliding,
L2 both $\nearrow$ trading lines building,
L3 both $b=1$ full harmony $E_{max}$,
L4 SOLA alone $\lim E\to0$,

Trap soul duet dark meets warm {BPM} {key}
```

---

## Texture Word Banks (for the plain English part of each layer line)

**RIVEN textures:** sparse piano, windshield rain, city lights blur, empty passenger seat, broken signal, radio static, cold leather, fog on glass, lone streetlight, midnight highway, concrete echoes, neon bleed

**SOLA textures:** incense haze, golden dust, afternoon light, curtain drift, bare feet, warm linen, honey drip, petal fall, tide pull, breath on skin, silk fold, candle glow

**Collab textures:** half-lit doorway, magnetic gap, almost-touch, shared breath, mirror stance, deferred glance, space between fingers, unresolved chord

---

## Examples

### Brief → DSL Block

**User:** "RIVEN song about revenge, cinematic strings, 75 BPM."

```
$S(x)$ lifecycle $dE/dx>0 \to b=1 \to 0$,
$E(x)$ monotone $dE/dx>0$ L0-L2
then $b(x):0\to1$ at $x=\gamma$ $E_{max}$
then $dE/dx<0$ to $\lim E=0$,

L0-L1 EXTENDED slow $\nearrow$ ambient $b=0$ sustained cold string swells,
L2 $30eE$ swell orchestral tension building low brass,
L3 sudden $b=1$ $E_{max}$ full cinematic drop strings and 808s,
L4 $\phi'_j\sim\mathcal{N}(0, \sigma^2)$ $\infty$ $dE/dx<0$ chaotic string stabs noise,
L5 instant snap $\lim_{x\to1}E=0$ $\oslash$ silence,

Trap soul dark noir cinematic 75 BPM D minor vengeance
```

**User:** "SOLA song about healing, slow burn, 68 BPM."

```
$S(x)$ lifecycle $dE/dx>0$ gradual $b=0$ sustained,
then $dE/dx<0$ to $\lim E=0$,
$E(x)$ slow rise to $E=6$ held then $dE/dx<0$,

L0 voice keys $b=0$ intimate incense haze,
L1 $dE/dx>0$ warm bass pad gold light enters,
L2 $E=6$ sustained chorus letting go bloom,
L3 bridge $dE/dx>0$ to $E=8$ rising from ashes,
L4 $\lim E\to0$ float to silence breath,

R&B alt-pop ethereal 68 BPM C minor healing
```

