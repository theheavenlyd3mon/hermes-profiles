#!/usr/bin/env python3
"""
Per-character palette remapping for Hermes banner_hero art.

Takes the banner_hero from a source skin with per-character color tags,
maps each original hex color to a target gradient via HSL luminance,
re-groups into 4-char blocks to control source line length,
and outputs the recolored banner block ready for patching.

Usage:
    python3 per-character-palette-remap.py <source_skin.yaml> [output_file]

If output_file is omitted, prints to stdout.
"""

import re
import sys

# ─── Target gradient: Dragon's Breath (fire) ──────────────────────────
# (hex, position) pairs. Override in the caller script as needed.
DEFAULT_GRADIENT = [
    ("#5C0000", 0.0),   # deep wine
    ("#8B0000", 0.25),  # blood red
    ("#C0392B", 0.50),  # crimson
    ("#E8630C", 0.75),  # fiery orange
    ("#F4A000", 1.0),   # gold
]

# ─── Colour helpers ───────────────────────────────────────────────────

def hex_to_rgb(h):
    return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)

def rgb_to_hex(r, g, b):
    return f"#{r:02X}{g:02X}{b:02X}"

def rgb_to_hsl(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        return 0, 0, l
    d = mx - mn
    s = d / (1 - abs(2 * l - 1))
    if mx == r:
        h = (g - b) / d + (6 if g < b else 0)
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h / 6, s, l

def lerp_color(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return rgb_to_hex(r, g, b)

def multi_stop(t, stops):
    for i in range(len(stops) - 1):
        c1, p1 = stops[i]
        c2, p2 = stops[i + 1]
        if p1 <= t <= p2:
            denom = p2 - p1
            return lerp_color(c1, c2, (t - p1) / denom if denom else 0)
    return stops[-1][0]

def map_color(c, stops, luminance_scale=1.15):
    """Map a source hex color to the target gradient via its HSL luminance."""
    if c is None:
        return multi_stop(1.0, stops)
    r, g, b = hex_to_rgb(c)
    _, _, l = rgb_to_hsl(r, g, b)
    t = min(1.0, max(0.0, l * luminance_scale))
    return multi_stop(t, stops)

# ─── Tag parsing ──────────────────────────────────────────────────────

def parse_per_char_tags(line):
    """Parse a line into [(hex_color_or_None, character), ...] pairs."""
    result = []
    i = 0
    while i < len(line):
        if line[i] == '[':
            j = line.index(']', i)
            tag = line[i + 1:j]
            if tag.startswith('#'):
                if j + 1 < len(line):
                    result.append((tag, line[j + 1]))
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

def group_chars(pairs, stops, group_size=4):
    """Group consecutive chars into N-char blocks, taking colour from the last."""
    groups = []
    i = 0
    while i < len(pairs):
        chunk = ""
        j = i
        while j < len(pairs) and j - i < group_size:
            _, char = pairs[j]
            chunk += char
            j += 1
        last_hex = pairs[j - 1][0]
        groups.append((map_color(last_hex, stops), chunk))
        i = j
    return groups

def strip_indent(s):
    return s[2:] if s.startswith('  ') else s

# ─── Main ─────────────────────────────────────────────────────────────

def extract_banner_hero(filepath):
    """Extract banner_hero lines from a Hermes skin YAML file."""
    with open(filepath) as f:
        lines = f.read().split('\n')
    start = None
    for i, line in enumerate(lines):
        if 'banner_hero: |-' in line:
            start = i + 1
            break
    if start is None:
        raise ValueError(f"No banner_hero found in {filepath}")
    hero = lines[start:]
    while hero and hero[-1].strip() == '':
        hero.pop()
    return hero

def remap(hero_lines, stops, group_size=4, luminance_scale=1.15):
    """Remap each line's per-character colour tags to the target gradient."""
    out = "banner_hero: |-\n"
    total_open = 0
    total_close = 0
    for line in hero_lines:
        raw = strip_indent(line)
        pairs = parse_per_char_tags(raw)
        if len(pairs) < 2:
            out += f"  {raw}\n"
            continue
        groups = group_chars(pairs, stops, group_size)
        line_out = ""
        for c_hex, c_text in groups:
            if c_text.strip():
                line_out += f"[{c_hex}]{c_text}[/]"
                total_open += 1
                total_close += 1
            else:
                line_out += c_text
        out += f"  {line_out}\n"

    # Verify balance
    if total_open != total_close:
        sys.stderr.write(
            f"WARNING: tag mismatch — {total_open} open, {total_close} close\n"
        )
    else:
        sys.stderr.write(f"Tag balance OK: {total_open} open/close\n")

    # Verify rendered width
    for i, line in enumerate(out.split('\n')):
        clean = re.sub(r'\[/?[^\]]*\]', '', line).strip()
        if clean and len(clean) > 68:
            sys.stderr.write(
                f"WARNING: line {i} rendered width {len(clean)} "
                f"(>68 may wrap)\n"
            )
    return out


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <source_skin.yaml> [output_file]")
        sys.exit(1)

    source = sys.argv[1]
    hero = extract_banner_hero(source)
    result = remap(hero, DEFAULT_GRADIENT)

    if len(sys.argv) >= 3:
        with open(sys.argv[2], 'w') as f:
            f.write(result)
        print(f"Written to {sys.argv[2]}")
    else:
        print(result)
