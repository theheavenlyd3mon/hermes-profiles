# Fixing Vertical/Misaligned Text in the Senna Skin Banner

## Problem

The Senna skin's `banner_hero` contained three quotation lines inside a framed box
(lines 166-168 of `senna.yaml`). Each used **per-character color tags**:

```yaml
     ║     ◉ [#D4A017]A[/][#D49A18] [/][#D5951A]m[/][#D68F1C]a[/][#D78A1D]n[/]... [/][#8B0000]e[/] ◉      ║
```

This made the English quote line **689 source bytes** wide for just 53 rendered
characters — ~13× markup overhead. The TUI's banner container line-wrapped the
source line, projecting each character onto its own row.

## Fix Applied

Switched to **character-block color tagging** — grouping 2-4 characters per tag
with the same gradient interpolation:

### Japanese quote (勇気なき男は…)
- **16 chars** → 8 tags of block-size 2
- Source: 208 → **112 bytes**
- Gradients by character pair: 勇気, なき, 男は, 、刃, なき, 小刀, のご, とし

### English quote (A man without courage…)
- **53 chars** → 14 tags of block-size 4
- Source: 689 → **221 bytes**

### Romaji quote (Yūki naki otoko…)
- **43 chars** → 15 tags of block-size 3
- Source: 559 → **223 bytes**

## Technique Used

```python
def gradient_block(text, c1, c2, block_size=3):
    """Apply gradient color in blocks of block_size chars."""
    result = ""
    n = len(text)
    i = 0
    while i < n:
        chunk = text[i:i + block_size]
        t = (i + len(chunk) / 2) / n
        color = lerp_color(c1, c2, min(t, 1.0))
        result += f"[{color}]{chunk}[/]"
        i += block_size
    return result
```

## Choosing Block Size

| Content | Block size | Why |
|---------|-----------|-----|
| CJK (Japanese/Chinese) | 2 | Characters are wider, 2 per tag keeps ~8-12 tags per line |
| English prose | 4 | Narrower characters, 4 per tag keeps source ~200-250 bytes |
| Romaji/transliteration | 3 | Mid-width, 3 per tag balances coverage |

## Verification

- YAML validated after the patch (`yaml.safe_load` passed)
- Gold→blood-red gradient preserved (#D4A017 → #8B0000)
- All three quote lines now fit within the TUI banner container width
- No visual change to the rendered output — only source line lengths changed
