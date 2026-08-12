# Generating Banner Logos with Pyfiglet + Gradient

## Pipeline Overview

Generate a `banner_logo` for a Hermes skin using pyfiglet ASCII art with grouped-gradient color tags. This produces a wordmark that fills the hero width (~80 chars) instead of a narrow 20-char logo that looks ill-proportioned.

## Prerequisites

Pyfiglet is typically not installed globally. Use a disposable venv:

```bash
python3 -m venv /tmp/figlet_venv
/tmp/figlet_venv/bin/pip install pyfiglet
```

## Step-by-Step Pipeline

### 1. Find Fonts That Match the Hero Width

The banner_hero is ~80 chars wide. Find pyfiglet fonts that render your text between ~40-80 chars with reasonable height (5-9 lines):

```python
from pyfiglet import Figlet, FigletFont

text = "SENNA"  # or your profile name
target_min, target_max = 40, 85
max_height = 12

for f in sorted(FigletFont.getFonts()):
    fig = Figlet(font=f)
    result = fig.renderText(text)
    lines = result.strip().split('\n')
    if lines:
        w = max(len(l) for l in lines)
        h = len(lines)
        if target_min <= w <= target_max and h <= max_height:
            print(f'{w:3d} × {h:2d} lines  {f}')
```

### 2. Preview Candidate Fonts

For a visual check, render each candidate without color tags:

```python
fig = Figlet(font='roman', width=90)
result = fig.renderText('SEN').strip()
lines = result.split('\n')
w, h = max(len(l) for l in lines), len(lines)
print(f"{w}×{h}")
for l in lines:
    print(f"  {l}")
```

### 3. Apply Grouped Gradient Tags

Apply the gold→blood-red (or your palette) gradient using **block-grouped** tags (not per-character). Block size 3 works well for ASCII art text:

```python
def lerp_color(c1, c2, t):
    r1, g1, b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2, g2, b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    r = int(r1 + (r2-r1)*t)
    g = int(g1 + (g2-g1)*t)
    b = int(b1 + (b2-b1)*t)
    return f"#{r:02X}{g:02X}{b:02X}"

def gradient_blocks(text, c1, c2, block_size=3):
    lines = text.strip('\n').split('\n')
    result = []
    for line in lines:
        n = len(line)
        out = ""
        i = 0
        while i < n:
            chunk = line[i:i+block_size]
            t = (i + len(chunk)/2) / n
            col = lerp_color(c1, c2, min(t, 1.0))
            out += f"[{col}]{chunk}[/]"
            i += block_size
        result.append(out)
    return '\n'.join(result)

colored = gradient_blocks(result, "#D4A017", "#8B0000", block_size=3)
for l in colored.split('\n'):
    print(l)
```

### 4. Add the Decorative Separator

Below the logo text, add a separator line matching the skin's theme:

```yaml
  [#D4A017]━━━━━━━━━ ⚔  ☾  ◎ ━━━━━━━━━[/]
```

Keep the separator's hex code fixed to your palette's accent color (not gradient) so it anchors the logo visually.

### 5. Verify Source Line Lengths

Each banner_logo source line should stay under ~250 bytes to avoid TUI wrapping:

```python
for l in colored.split('\n'):
    print(f"  len={len(l)}")
```

If any line exceeds 300 bytes, reduce block_size (try 2) or use a narrower pyfiglet font.

### 6. Validate the YAML

```bash
/tmp/figlet_venv/bin/python3 -c "import yaml; yaml.safe_load(open('path/to/skin.yaml')); print('YAML OK')"
```

## Font Selection Guide

| Font | Width×Height | Vibe | Best for |
|------|-------------|------|----------|
| `roman` | 71×7 | Classic serif | Clean, readable, same height as most current logos |
| `univers` | 68×8 | Sans-serif tech | Cyberpunk, netrunner, modern |
| `mirror` | 89×5 | Blocky, wide | Minimal height, maximum fill |
| `ivrit` | 89×5 | Blocky, wide | Mirror variant, same dimensions |
| `dotmatrix` | 79×8 | LED matrix | Retro/cyberpunk aesthetic |
| `star_strips` | 65×8 | Slashed-tech | Aggressive, tech-noir |
| `eftichess` | 72×9 | Chess-piece shapes | Thematic/experimental |

## Worked Example: "SEN" in roman

From this session's actual output:

```
  .oooooo..o oooooooooooo ooooo      ooo
  d8P'    `Y8 `888'     `8 `888b.     `8'
  Y88bo.       888          8 `88b.    8
   `"Y8888o.   888oooo8     8   `88b.  8
       `"Y88b  888    "     8     `88b.8
  oo     .d8P  888       o  8       `888
  8""88888P'  o888ooooood8 o8o        `8
━━━━━━━━━ ⚔  ☾  ◎ ━━━━━━━━━
```

- Gold `#D4A017` → blood red `#8B0000` gradient
- Block size 3 → source lines ~200 bytes each
- Fills from ~col 3 to ~col 72 of a 80-char hero

## Pitfalls

- **Per-character tags cause wrapping.** Always use block grouping (block_size 2-4). A single `[#HEX]char[/]` per char makes the source line ~700 bytes for a 50-char name → vertical misaligned text.
- **Font line width varies.** The `roman` font for "SEN" is 40×7, but for "SENNA" it would be ~55×7. Always check the rendered width for your exact text.
- **Trailing spaces in pyfiglet output.** Pyfiglet may include trailing spaces that bloat source lines. Trim them before applying color tags.
- **Valid YAML requires correct indentation.** Each banner_logo line must be indented exactly 2 spaces relative to `banner_logo: |-`.
- **The separator line should NOT use gradient.** Use a single fixed-color `[#HEX]...[/]` tag for the decorative line so it reads as a visual anchor.
