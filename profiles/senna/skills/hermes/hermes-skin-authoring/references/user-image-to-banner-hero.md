# Worked Example: User Image → Multi-Stop Gradient Banner Hero

## Source

A Stable Diffusion portrait (1152×1920, 2.7MB PNG) of a warrior/kunoichi figure with flowing hair/cape. Dark silhouette against minimal background — ideal for jp2a conversion.

## Step 1: Width Selection

Image was 1152×1920 portrait. jp2a at various widths:

| Width | Lines | Notes |
|-------|-------|-------|
| 68 | 57 | Maximum detail, fills the banner |
| 60 | 50 | Good middle ground |
| 50 | 42 | Solid banner height |
| 40 | 33 | Compact silhouette |

User chose **width=68** (maximum).

## Step 2: Generate ASCII

```
jp2a --width=68 --invert "/path/to/image.png"
```

Output: 57 lines of ASCII composed of `X`, `K`, `0`, `O`, `k`, `x`, `d`, and other density characters. The silhouette resolves a humanoid figure with flowing elements — recognizable as a warrior/kunoichi in dramatic pose.

## Step 3: Multi-Stop Color Gradient

Applied a 4-stop gradient matching the **senna** skin's palette (blood red → gold):

```python
def lerp_color(c1, c2, t):
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02X}{g:02X}{b:02X}"

# Four-stop gradient: dark blood red → mid red → bright red → gold
colors = [("#8B0000", 0.0), ("#C0392B", 0.4), ("#E34234", 0.65), ("#D4A017", 1.0)]

def multi_stop(t):
    for i in range(len(colors)-1):
        c1, p1 = colors[i]
        c2, p2 = colors[i+1]
        if p1 <= t <= p2:
            local_t = (t - p1) / (p2 - p1)
            return lerp_color(c1, c2, local_t)
    return colors[-1][0]

lines = [...]  # 57 jp2a output lines
n = len(lines)
for i, line in enumerate(lines):
    t = i / (n - 1) if n > 1 else 0
    color = multi_stop(t)
    print(f"  [{color}]{line}[/]")
```

### Color Progression

| Line | t | Color | Appearance |
|------|---|-------|------------|
| 1 | 0.00 | `#8B0000` | Dark blood red (head/top of figure) |
| 11 | 0.18 | `#A21913` | Deepening red |
| 21 | 0.36 | `#BA3226` | Mid red (torso) |
| 31 | 0.54 | `#D33D2F` | Transitioning to bright red |
| 41 | 0.71 | `#E0532E` | Bright accent (lower body/base) |
| 57 | 1.00 | `#D4A017` | Gold (bottom edge/ground) |

This creates a visual effect where the figure's upper silhouette is darkest, the center glows brightest, and the base settles into gold.

## Step 4: Patch Into Skin File

The old `banner_hero: |-` block (71 lines of braille katana art with Japanese quotes and decorative borders) was replaced with the new 58-line block (57 ASCII lines + the `banner_hero: |-` key line).

**Key detail:** The patch `old_string` must match the exact content from `banner_hero: |-` through the last `[/]` character — including all whitespace, indentation, and trailing spaces. Copy-paste from `read_file`, don't retype.

**Result:** File went from 175 lines → 162 lines. Skin size dropped from 18,929 bytes → 10,841 bytes (smaller banner without the frame/quotes).

## Lessons

1. **User-provided local images** work well if high-contrast silhouettes (AI art with dark backgrounds is ideal). jp2a handles them better than searching openclipart.
2. **Vision API failure is not a blocker** — jp2a serves as both preview tool and production converter. The ASCII output is readable enough to judge the silhouette.
3. **Multi-stop gradients** add significant depth vs a single accent color. Match the stops to the skin's existing palette (use the `colors:` section values directly).
4. **Per-line color tags** don't cause vertical text issues on ASCII art because each line is only ~68 chars without markup. The `[#HEX]...[/]` pair wraps the whole line, keeping source length reasonable.
5. **Always show options before committing.** The user might want maximum detail (width=68, 57 lines) or compact (width=40, 33 lines) — cannot assume.
