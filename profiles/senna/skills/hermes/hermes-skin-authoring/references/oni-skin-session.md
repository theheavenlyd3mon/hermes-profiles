# ONI Skin — Full Build Log (2026-05-10)

This file documents the complete build of the **oni** skin, including commands used, tools discovered, and pitfalls encountered.

## Goal

Create a custom Hermes skin titled "ONI" — a cyberpunk netrunner who uses a samurai alias. Blend visual elements from three existing skins: solo-leveling-boss, kensei, and netrunner.

## Decision Flow

1. **Colors** → Kensei palette (blood reds #8B0000, gold #D4A017, parchment #E8DCC6 on #0A0A0A background)
2. **Agent name** → "ONI" (Japanese demon mask, fits both hacker alias and visual theme)
3. **Welcome message** → Hybrid of all three source skins:
   - "Connection established. Neural link active." — from netrunner
   - "Blade drawn." — adapted from kensei's "Steel drawn."
   - "State your objective" — from kensei
   - " — or /help for protocols." — from netrunner
   - Cadence from Shadow Monarch's dramatic structure
4. **Verbs** → 14 items mixed: "breaching the gate" (netrunner+SL), "drawing steel" (kensei), "jacking into the NET" (netrunner), "raising shadow soldiers" (SL), "cutting through the firewall" (blend), etc.
5. **Prompt symbols** → All three distributed: ◎ as prompt_symbol, ⚔ as terminal emoji, ☾ as write_file emoji, all three in help_header and banner
6. **Banner art** → Oni mask ASCII (46 lines) from openclipart image + "ONI" in Doom figlet

## Commands Used

### Install jp2a (macOS)
```bash
brew install jp2a
```

### Find usable oni mask image
Navigated to openclipart.org via browser, searched "oni mask", found "oni mask no color" (ID 171060).
```bash
curl -sL -o /tmp/oni-mask-nocolor.png "https://openclipart.org/image/800px/171060"
file /tmp/oni-mask-nocolor.png
# PNG image data, 596 x 800, 8-bit gray+alpha, non-interlaced
```

### Convert to ASCII for banner_hero
```bash
jp2a --width=68 --invert /tmp/oni-mask-nocolor.png
# 46 lines of output — recognizable oni mask with horns, brow, eyes, mouth
```

The `--invert` flag was essential because the image had a transparent background with dark subject matter.

### Generate figlet banner logo for "ONI"
```bash
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=ONI&font=Doom"
# 6-line blocky "ONI" — used Doom font for cyberpunk feel
```

### Generate gradient welcome text
```python
python3 << 'PYEOF'
def lerp_color(c1, c2, t):
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02X}{g:02X}{b:02X}"

text = "Connection established. Neural link active. Blade drawn. State your objective \u2014 or /help for protocols."
c1, c2 = "#D4A017", "#8B0000"  # gold -> blood red
result = ""
for i, ch in enumerate(text):
    t = i / (len(text) - 1) if len(text) > 1 else 0
    color = lerp_color(c1, c2, t)
    result += f"[{color}]{ch}[/]"
print(result)
PYEOF
```

### Generate goodbye gradient (red -> black)
```python
text = "Connection severed. Neural link terminated. The blade returns to shadow."
c1, c2 = "#8B0000", "#000000"
# same lerp_color function, gradient from deep red to pure black
```

## Pitfalls Encountered

1. **YAML `?` quoting**: `clarify: ?` fails with YAML parse error (`mapping keys are not allowed here`). Fix: `clarify: "?"`.
2. **Em dash encoding**: The Python script output `\u2014` as a Python escape, but when written to the YAML file it became the literal string `\u2014` instead of the em dash character `—`. Fixed with `sed -i '' 's/\\u2014/—/g'`.
3. **jp2a claimed "JPEG only"**: Some docs say jp2a only handles JPEG, but it works fine with PNG via libpng.
4. **Openclipart thumbnail vs full image**: The 800px version URL pattern is `https://openclipart.org/image/800px/{id}`. The raw SVG is also available.
5. **Gradient length**: The 86-character welcome generates a very long YAML line. Double-check quotes are properly closed.

## File

The final skin is at `~/.hermes/skins/oni.yaml` (150 lines, ~8KB).
