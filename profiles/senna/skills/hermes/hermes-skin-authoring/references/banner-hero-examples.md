# Banner Hero Techniques

The `banner_hero` section of a Hermes skin supports complex ANSI/unicode artwork. This reference documents the techniques used in existing skins so you can create or modify banner_hero art.

## Technique 1: Braille Pattern Art

Both solo-leveling-boss and kensei use Unicode Braille characters (U+2800–U+28FF, e.g., ⠀ ⠁ ⠃ ⡇ ⣿) to create pixel-art-style images in the terminal.

**How Braille pixel art works:**
- Each Braille character is a 2×4 dot grid (2 columns × 4 rows = 8 dots)
- By selecting specific Braille glyphs, you control which dots are filled
- This gives effective 2×4 pixel blocks per character
- Combined into a grid, they form shapes, figures, scanlines, etc.

**The solo-leveling-boss approach:**
```yaml
banner_hero: |-
  [#203050]%[/][#203060]%%%%%%%[/][#204060]%%%[/][#203050]%[/]...
```
Uses `%` characters (which render as block fills in some terminals) alongside Braille, with per-character color tags creating a gradient effect across the figure. The SL boss banner hero uses a grid approximately 70×25 characters creating a shadowy figure with glowing eyes/power lines.

**The kensei approach:**
```yaml
banner_hero: |-
  [bold #f70240]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀...[/]
```
Uses Braille characters (`⠀` and variants) with a single color tag wrapping larger sections rather than per-character tags. This creates a katana/samurai silhouette figure. The kensei hero is approximately 80×30 characters.

**Trade-offs:**
- Per-character color tags (SL boss style): Supports gradients and multiple colors in one figure, but inflates file size dramatically (18KB for the SL hero). Each of ~1,750 characters has a `[#HEX]` tag.
- Section-level color tags (kensei style): Smaller file size (8-12KB), but only one flat color per section. Less visual depth.
- Netrunner approach: Small Braille skull (1.5KB) with simple teal/white color sections. Minimal and effective.

## Technique 2: Decorative Borders and Frames

Kensei uses extended unicode and special characters to frame the hero:

```
._._._._._._._._._._.|________________________________________________________.
|_#_#_#_#_#_#_#_#_#_|________________________________________________________/
                     l
     ╔𒌐𒉭𒌐══════════════════════════════════════════════════════════════𒌐𒉭𒌐╗
     ║                ◉ ...quoted text... ◉                ║
     ╠𒌐𒉭𒌐══════════════════════════════════════════════════════════════𒌐𒉭𒌐╣
     ║         ㊙ 不名誉より死 ㊙ 不名誉より死 ㊙ 不名誉より死 ㊙         ║
     ╚𒌐𒉭𒌐══════════════════════════════════════════════════════════════𒌐𒉭𒌐╝
  ._________________________________________________________|_._._._._._._._._._.
   \________________________________________________________|_#_#_#_#_#_#_#_#_#_|
                                                           l
```

**Characters used:**
- `╔══╗║╠╣╚═╝` — Box drawing (U+2550–U+256C)
- `𒌐𒉭` — Cuneiform signs (U+12310, U+1226D) — exotic decorative accents
- `㊙` — Japanese "secret" symbol (U+3299)
- `._._.` and `|_#_#_` — ASCII decorative borders

This creates a visual "scroll" or "document" framing effect around the Braille art.

## Technique 3: Text-Based Gradient Banner Logos

The `banner_logo` section typically uses large ASCII-rendered text (from tools like figlet or TOIlet) with gradient color tags:

**Solo leveling boss:**
```
       ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗
       ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ██║
       ███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║
       ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║
       ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝
       ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝
```

Wrapped in a single `[#A855F7]...[/]` to color the entire wordmark purple.

**Netrunner:**
```
             ███╗   ██╗███████╗████████╗
             ████╗  ██║██╔════╝╚══██╔══╝
              ██╔██╗ ██║█████╗     ██║
              ██║╚██╗██║██╔══╝     ██║
              ██║ ╚████║███████╗   ██║
              ╚═╝  ╚═══╝╚══════╝   ╚═╝
██████╗ ██╗   ██╗███╗   ██╗███╗   ██╗███████╗██████╗
██╔══██╗██║   ██║████╗  ██║████╗  ██║██╔════╝██╔══██╗
██████╔╝██║   ██║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
██╔══██╗██║   ██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
██║  ██║╚██████╔╝██║ ╚████║██║ ╚████║███████╗██║  ██║
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
```

Each row has a different color tag creating a gradient from dark teal (`#003333`) to bright cyan (`#00FFFF`). Plus a subtitle line in dark teal: `◎ JINTEKI SYSTEMS AGENT ◎`.

## Building Your Own Banner Hero

For a custom skin, consider these approaches depending on how much effort you want to invest:

| Approach | Complexity | File Size | Visual Impact |
|----------|-----------|-----------|---------------|
| Text-only logo (like netrunner) | Low | 1-2KB | Clean, professional |
| Small Braille art (like netrunner skull) | Medium | 2-5KB | Nice accent |
| Large Braille art with section coloring (like kensei) | Medium-High | 8-12KB | Strong silhouette |
| Full per-character gradient Braille (like SL boss) | High | 15-25KB | Highest detail |

**Tools for generating ASCII art:**
- `figlet` / `toilet` — text banners (netrunner-style)
- `jp2a` / `img2txt` — image → ASCII/Braille conversion
- `chafa` — image → ANSI colored output
- Manual Braille grid editors or pixel-to-Braille converters
