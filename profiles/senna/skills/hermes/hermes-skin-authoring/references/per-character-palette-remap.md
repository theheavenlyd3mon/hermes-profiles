# Per-Character Banner Palette Remapping

## What this technique does

Takes a banner_hero art block that uses **per-character color tags** (hundreds of
`[#HEX]char[/]` pairs per line — see solo-leveling-boss.yaml) and remaps every hex
value to a target gradient while preserving the original **shading and depth** of
the figure. The result is the same Braille/symbol art but in a completely
different color palette.

## Why not just strip tags and wrap per-line?

| Approach | Effect | File size |
|----------|--------|-----------|
| Per-line single tag | Flat gradient — the figure loses 3D depth | ~3KB for 41 lines |
| Per-character remap | Preserves pixel-level shading — dark shadows, bright highlights | ~8.5KB for 41 lines |

If the source skin's art has intricate shading (dark cape folds, glowing aura
edges, eye highlights), the per-character approach preserves that. If the art
is simple block lettering, per-line is sufficient.

## Algorithm

For each character in the banner:

1. **Extract** the original hex color and character from the `[#HEX]char[/]` tag
2. **Convert** the original hex to HSL
3. **Map** the **L** (luminance/lightness, 0.0–1.0) to a position in the target gradient:
   - Dark (L≈0.0) → first gradient stop
   - Mid (L≈0.5) → middle stops
   - Bright (L≈1.0) → last gradient stop
4. **Interpolate** in the target gradient to get the new hex
5. **Group** consecutive characters into blocks of 4 (to keep source lines short)
6. **Wrap** each block in `[#NEW_HEX]block_text[/]`

The luminance scaling can be adjusted — a multiplier of 1.15 compresses darker
shadows slightly and spreads the brighter range, which works well for fire
palettes (more reds/oranges visible, fewer blacks).

## Python pipeline

The reusable script at `scripts/per-character-palette-remap.py` does all of
this in one call:

```bash
python3 per-character-palette-remap.py path/to/source-skin.yaml output.txt
```

The output is a complete `banner_hero: |-` block ready for patching into a
target skin. The script also:
- Validates tag balance (open/close count)
- Warns if any rendered line exceeds 68 chars (TUI wrapping risk)
- Reports the rendered max character width

## Worked example: solo-leveling-boss → senna (fire palette)

Source: `solo-leveling-boss.yaml` — Shadow Monarch figure, 41 lines, ~18KB banner
Target: `senna.yaml` — Dragon's Breath palette

### Step 1: Extract banner_hero from source

```python
with open('solo-leveling-boss.yaml') as f:
    lines = f.read().split('\n')
start = None
for i, line in enumerate(lines):
    if 'banner_hero: |-' in line:
        start = i + 1
        break
hero_lines = lines[start:]
while hero_lines and hero_lines[-1].strip() == '':
    hero_lines.pop()
```

### Step 2: Parse per-character tags

```python
def parse_tags(line):
    result = []
    i = 0
    while i < len(line):
        if line[i] == '[':
            j = line.index(']', i)
            tag = line[i+1:j]
            if tag.startswith('#'):
                if j + 1 < len(line):
                    result.append((tag, line[j+1]))
                    i = j + 2
                else:
                    break
            elif tag == '/':
                i = j + 1
            else:
                i = j + 1
        else:
            result.append((None, line[i]))
            i += 1
    return result
```

### Step 3: Map via HSL luminance

```python
def map_color(orig_hex):
    if orig_hex is None:
        return "#F4A000"  # gold for uncolored chars
    r, g, b = hex_to_rgb(orig_hex)
    h, s, l = rgb_to_hsl(r, g, b)
    t = min(1.0, max(0.0, l * 1.15))
    return fire_gradient(t)
```

### Step 4: Group into 4-char blocks

```python
def group_chars(pairs, group_size=4):
    groups = []
    i = 0
    while i < len(pairs):
        chunk = ""
        j = i
        while j < len(pairs) and j - i < group_size:
            _, char = pairs[j]
            chunk += char
            j += 1
        # Colour from the LAST character in the block
        last_hex = pairs[j-1][0]
        groups.append((map_color(last_hex), chunk))
        i = j
    return groups
```

### Step 5: Patch into target

Use `patch` with:
- `old_string`: the target skin's current `banner_hero: |-` block (exact copy)
- `new_string`: the output from the script (including the `banner_hero: |-` key)

### Verification checklist

- [ ] Tag balance: open count == close count
- [ ] Max rendered line width <= 68 chars
- [ ] YAML validates: `python3 -c "import yaml; yaml.safe_load(open('target.yaml'))"`
- [ ] File size increase is expected (~3× for 4-char grouping vs ~14× for 1-char)

## Pitfalls

- **The colour is taken from the LAST char of each group**, not the first. This
  biases shading slightly toward the right edge of each block. If grouping by 4,
  this is imperceptible. If grouping by 8+, the shift becomes visible.
- **Luminance mapping is a heuristic.** Original purple→cyan gradients can have
  multiple stops at the same luminance (e.g., mid-purple and mid-cyan both at
  L=0.5). The remap will map them both to the same fire stop, which is fine —
  they were at the same brightness level in the original.
- **Uncolored characters** (e.g., the spaces in the figure's negative space) map
  to the brightest stop (gold) by default. This works well for fire palettes
  where bright edges show through. For dark palettes, change the fallback.
- **Verify on-disk content, not session memory.** The target skin may have been
  changed by a different session. Always `read_file` the actual file before
  patching.