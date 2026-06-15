---
name: ascii-art
description: "ASCII art: pyfiglet, cowsay, boxes, image-to-ascii."
version: 4.0.0
author: 0xbyt4, Hermes Agent
license: MIT
dependencies: []
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ASCII, Art, Banners, Creative, Unicode, Text-Art, pyfiglet, figlet, cowsay, boxes, riso, image-to-ascii]
    related_skills: [excalidraw, riso, ascii-video]

---

# ASCII Art Skill

Multiple tools for different ASCII art needs. All tools are local CLI programs or free REST APIs — no API keys required.

## Tool 1: Text Banners (pyfiglet — local)

Render text as large ASCII art banners. 571 built-in fonts.

### Setup

```bash
pip install pyfiglet --break-system-packages -q
```

### Usage

```bash
python3 -m pyfiglet "YOUR TEXT" -f slant
python3 -m pyfiglet "TEXT" -f doom -w 80    # Set width
python3 -m pyfiglet --list_fonts             # List all 571 fonts
```

### Recommended fonts

| Style | Font | Best for |
|-------|------|----------|
| Clean & modern | `slant` | Project names, headers |
| Bold & blocky | `doom` | Titles, logos |
| Big & readable | `big` | Banners |
| Classic banner | `banner3` | Wide displays |
| Compact | `small` | Subtitles |
| Cyberpunk | `cyberlarge` | Tech themes |
| 3D effect | `3-d` | Splash screens |
| Gothic | `gothic` | Dramatic text |

### Tips

- Preview 2-3 fonts and let the user pick their favorite
- Short text (1-8 chars) works best with detailed fonts like `doom` or `block`
- Long text works better with compact fonts like `small` or `mini`

## Tool 2: Text Banners (asciified API — remote, no install)

Free REST API that converts text to ASCII art. 250+ FIGlet fonts. Returns plain text directly — no parsing needed. Use this when pyfiglet is not installed or as a quick alternative.

### Usage (via terminal curl)

```bash
# Basic text banner (default font)
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello+World"

# With a specific font
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Slant"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Doom"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Star+Wars"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=3-D"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Banner3"

# List all available fonts (returns JSON array)
curl -s "https://asciified.thelicato.io/api/v2/fonts"
```

### Tips

- URL-encode spaces as `+` in the text parameter
- The response is plain text ASCII art — no JSON wrapping, ready to display
- Font names are case-sensitive; use the fonts endpoint to get exact names
- Works from any terminal with curl — no Python or pip needed

## Tool 3: Cowsay (Message Art)

Classic tool that wraps text in a speech bubble with an ASCII character.

### Setup

```bash
curl -s https://api.github.com/octocat
```

### Source D: asciiart.eu (recommended for high-quality collections)

```bash
cowsay "Hello World"
cowsay -f tux "Linux rules"       # Tux the penguin
cowsay -f dragon "Rawr!"          # Dragon
cowsay -f stegosaurus "Roar!"     # Stegosaurus
cowthink "Hmm..."                  # Thought bubble
cowsay -l                          # List all characters
```

### Available characters (50+)

`beavis.zen`, `bong`, `bunny`, `cheese`, `daemon`, `default`, `dragon`,
`dragon-and-cow`, `elephant`, `eyes`, `flaming-skull`, `ghostbusters`,
`hellokitty`, `kiss`, `kitty`, `koala`, `luke-koala`, `mech-and-cow`,
`meow`, `moofasa`, `moose`, `ren`, `sheep`, `skeleton`, `small`,
`stegosaurus`, `stimpy`, `supermilker`, `surgery`, `three-eyes`,
`turkey`, `turtle`, `tux`, `udder`, `vader`, `vader-koala`, `www`

### Eye/tongue modifiers

```bash
cowsay -b "Borg"       # =_= eyes
cowsay -d "Dead"       # x_x eyes
cowsay -g "Greedy"     # $_$ eyes
cowsay -p "Paranoid"   # @_@ eyes
cowsay -s "Stoned"     # *_* eyes
cowsay -w "Wired"      # O_O eyes
cowsay -e "OO" "Msg"   # Custom eyes
cowsay -T "U " "Msg"   # Custom tongue
```

## Tool 4: Boxes (Decorative Borders)

Draw decorative ASCII art borders/frames around any text. 70+ built-in designs.

### Setup

```bash
curl -s https://api.github.com/octocat
```

### Source D: asciiart.eu (recommended for high-quality collections)

```bash
echo "Hello World" | boxes                    # Default box
echo "Hello World" | boxes -d stone           # Stone border
echo "Hello World" | boxes -d parchment       # Parchment scroll
echo "Hello World" | boxes -d cat             # Cat border
echo "Hello World" | boxes -d dog             # Dog border
echo "Hello World" | boxes -d unicornsay      # Unicorn
echo "Hello World" | boxes -d diamonds        # Diamond pattern
echo "Hello World" | boxes -d c-cmt           # C-style comment
echo "Hello World" | boxes -d html-cmt        # HTML comment
echo "Hello World" | boxes -a c               # Center text
boxes -l                                       # List all 70+ designs
```

### Combine with pyfiglet or asciified

```bash
python3 -m pyfiglet "HERMES" -f slant | boxes -d stone
# Or without pyfiglet installed:
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=HERMES&font=Slant" | boxes -d stone
```

## Tool 5: TOIlet (Colored Text Art)

Like pyfiglet but with ANSI color effects and visual filters. Great for terminal eye candy.

### Setup

```bash
curl -s https://api.github.com/octocat
```

### Source D: asciiart.eu (recommended for high-quality collections)

```bash
toilet "Hello World"                    # Basic text art
toilet -f bigmono12 "Hello"            # Specific font
toilet --gay "Rainbow!"                 # Rainbow coloring
toilet --metal "Metal!"                 # Metallic effect
toilet -F border "Bordered"             # Add border
toilet -F border --gay "Fancy!"         # Combined effects
toilet -f pagga "Block"                 # Block-style font (unique to toilet)
toilet -F list                          # List available filters
```

### Filters

`crop`, `gay` (rainbow), `metal`, `flip`, `flop`, `180`, `left`, `right`, `border`

**Note**: toilet outputs ANSI escape codes for colors — works in terminals but may not render in all contexts (e.g., plain text files, some chat platforms).

## Tool 6: Image to ASCII Art

Convert images (PNG, JPEG, GIF, WEBP) to ASCII art.

### Option A: riso pipeline (recommended — quality-gated, edge-aware)

The `riso` skill provides a production-grade ASCII rendering pipeline with edge-aware downsampling, four curated presets, and automatic quality gates. Install and use:

```bash
# Installed at ~/riso/
~/.hermes/hermes-agent/venv/bin/python -m ascii_pipeline.cli render-image \
  --input image.png \
  --preset stroke-clarity \
  --out output.txt \
  --preview-out preview.png \
  --diagnostics-out metrics.json \
  [--scale N]
```

**Presets:** `stroke-clarity` (safe default), `d30-dense` (cyber-noir texture), `braille-detail` (max detail via Braille)
**Quality gates:** `high-contrast` → ship; `low-contrast-garble-risk` → reject
**Diagnostics:** unique glyphs, fill/heavy/light ratios, automatic verdict

See the `riso` skill for full documentation including background-removal preprocessing pattern.

For photographs / complex images with dark backgrounds, preprocess to replace black bg with white before running through the pipeline (see `riso/references/preprocessing.md`).

### Option B: ascii-image-converter (modern, easy)

```bash
# Install
sudo snap install ascii-image-converter
# OR: go install github.com/TheZoraiz/ascii-image-converter@latest
```

```bash
ascii-image-converter image.png                  # Basic
ascii-image-converter image.png -C               # Color output
ascii-image-converter image.png -d 60,30         # Set dimensions
ascii-image-converter image.png -b               # Braille characters
ascii-image-converter image.png -n               # Negative/inverted
ascii-image-converter https://url/image.jpg      # Direct URL
ascii-image-converter image.png --save-txt out   # Save as text
```

### Option C: jp2a (lightweight, JPEG + PNG)

Converts images to ASCII art. Works with both JPEG and PNG (via libpng). Good for turning simple silhouettes and grayscale images into terminal banner art.

```bash
# Linux
sudo apt install jp2a -y
# macOS
brew install jp2a

jp2a --width=80 image.jpg                 # JPEG
jp2a --width=68 --invert image.png        # PNG, inverted (white-on-black images)
jp2a --colors image.jpg                   # Colorized output
```

- `--invert` is useful when the source image has a white background with dark subject matter — it flips the character mapping so dark pixels become dense characters.
- Width of 60-72 works well for terminal banner_hero sections. 68 is a good default that balances detail with terminal fit.

## Tool 7: Search Pre-Made ASCII Art

Search curated ASCII art from the web. Use `terminal` with `curl`.

### Source A: ascii.co.uk (recommended for pre-made art)

Large collection of classic ASCII art organized by subject. Art is inside HTML `<pre>` tags. Fetch the page with curl, then extract art with a small Python snippet.

**URL pattern:** `https://ascii.co.uk/art/{subject}`

**Step 1 — Fetch the page:**

```bash
curl -s 'https://ascii.co.uk/art/cat' -o /tmp/ascii_art.html
```

**Step 2 — Extract art from pre tags:**

```python
import re, html
with open('/tmp/ascii_art.html') as f:
    text = f.read()
arts = re.findall(r'<pre[^>]*>(.*?)</pre>', text, re.DOTALL)
for art in arts:
    clean = re.sub(r'<[^>]+>', '', art)
    clean = html.unescape(clean).strip()
    if len(clean) > 30:
        print(clean)
        print('\n---\n')
```

**Available subjects** (use as URL path):
- Animals: `cat`, `dog`, `horse`, `bird`, `fish`, `dragon`, `snake`, `rabbit`, `elephant`, `dolphin`, `butterfly`, `owl`, `wolf`, `bear`, `penguin`, `turtle`
- Objects: `car`, `ship`, `airplane`, `rocket`, `guitar`, `computer`, `coffee`, `beer`, `cake`, `house`, `castle`, `sword`, `crown`, `key`
- Nature: `tree`, `flower`, `sun`, `moon`, `star`, `mountain`, `ocean`, `rainbow`
- Characters: `skull`, `robot`, `angel`, `wizard`, `pirate`, `ninja`, `alien`
- Holidays: `christmas`, `halloween`, `valentine`

**Tips:**
- Preserve artist signatures/initials — important etiquette
- Multiple art pieces per page — pick the best one for the user
- Works reliably via curl, no JavaScript needed

### Source B: Openclipart.org (recommended for custom banner art)

Openclipart provides free, public-domain SVG/PNG clipart with transparent backgrounds — ideal for converting to ASCII banner_hero for terminal skins. The monochrome and silhouette images convert best.

**Search pattern:** `https://openclipart.org/search/?query={subject}`

**Finding usable images:** Openclipart search results show thumbnail images. Use the browser to navigate, then extract image URLs:

```javascript
// In browser console after search:
document.querySelectorAll('a img')
```

Each result links to a detail page with multiple sizes. The `800px` version works well for ASCII conversion.

**Best types for ASCII conversion:**
- Silhouettes (black on white or white on transparent)
- Simple line art with thick strokes
- Grayscale images with high contrast
- Avoid: photos, gradients, fine detail, color-only art

**Available subjects:** Searchable — try `oni mask`, `samurai`, `dragon`, `sword`, `skull`, `cyberpunk`, `ninja`

```bash
# Get the 800px version directly (use the numeric ID from Openclipart)
curl -sL -o subject.png "https://openclipart.org/image/800px/{id}"
jp2a --width=68 --invert subject.png
```

### Source C: GitHub Octocat API (fun easter egg)

Returns a random GitHub Octocat with a wise quote. No auth needed.
```bash
curl -s https://api.github.com/octocat
```

### Source D: asciiart.eu (recommended for high-quality collections)
Larger, more elaborate ASCII art collections than ascii.co.uk. Includes 70+ dragons alone, plus animals, mythology, characters, and more. Artworks are labeled with artist, date, dimensions, and character count.

**URL pattern:** `https://www.asciiart.eu/{category}/{subject}`

**Known catalogs:**
| Catalog | URL | Size |
|---------|-----|------|
| Dragons | `https://www.asciiart.eu/mythology/dragons` | 70 pieces |
| Animals (reptiles) | `https://www.asciiart.eu/animals/reptiles` | Various |
| Mythology | `https://www.asciiart.eu/mythology` | Various |

**Extraction:**
```python
import re, html, requests
text = requests.get('https://www.asciiart.eu/mythology/dragons').text
arts = re.findall(r'<pre[^>]*>(.*?)</pre>', text, re.DOTALL)
for art in arts:
    clean = re.sub(r'<[^>]+>', '', art)
    clean = html.unescape(clean).strip()
    if len(clean) > 30:
        print(clean)
```

**Sorting:** Append `?sort=size&direction=desc` for largest-first.
### Weather as ASCII Art

```bash
curl -s "wttr.in/London"          # Full weather report with ASCII graphics
curl -s "wttr.in/Moon"            # Moon phase in ASCII art
curl -s "v2.wttr.in/London"       # Detailed version
```

## Tool 9: LLM-Generated Custom Art (Fallback)

When tools above don't have what's needed, generate ASCII art directly using these Unicode characters:

### Character Palette

**Box Drawing:** `╔ ╗ ╚ ╝ ║ ═ ╠ ╣ ╦ ╩ ╬ ┌ ┐ └ ┘ │ ─ ├ ┤ ┬ ┴ ┼ ╭ ╮ ╰ ╯`

**Block Elements:** `░ ▒ ▓ █ ▄ ▀ ▌ ▐ ▖ ▗ ▘ ▝ ▚ ▞`

**Geometric & Symbols:** `◆ ◇ ◈ ● ○ ◉ ■ □ ▲ △ ▼ ▽ ★ ☆ ✦ ✧ ◀ ▶ ◁ ▷ ⬡ ⬢ ⌂`

### Rules

- Max width: 60 characters per line (terminal-safe)
- Max height: 15 lines for banners, 25 for scenes
- Monospace only: output must render correctly in fixed-width fonts

## Tool 10: ASCII Video Production Pipeline

For converting video/audio into colored ASCII character video output (MP4, GIF), use the ASCII video production pipeline. This is a full creative pipeline — not a simple converter.

**References** (in `references/` directory):
- `architecture.md` — grid system, resolution presets, font selection, 20+ character palettes, color system
- `composition.md` — pixel blend modes, multi-grid composition, adaptive tonemap, feedback buffer
- `effects.md` — value field generators, noise/fBM, voronoi, particle systems, coordinate transforms
- `shaders.md` — ShaderChain, 38 shader catalog, audio-reactive scaling, transitions
- `scenes.md` — scene protocol, Renderer class, SCENES table, beat-synced cutting, parallel rendering
- `inputs.md` — audio analysis (FFT, bands, beats), video sampling, text/lyrics, TTS integration
- `optimization.md` — hardware detection, quality profiles, parallel rendering, memory management
- `troubleshooting.md` — NumPy broadcasting traps, blend mode pitfalls, ffmpeg issues, font problems

**Pipeline architecture:** `INPUT → ANALYZE → SCENE_FN → TONEMAP → SHADE → ENCODE`

**Modes:** Video-to-ASCII, Audio-reactive, Generative, Hybrid, Lyrics/text, TTS narration

**Stack:** Python 3.10+, NumPy, SciPy, Pillow, ffmpeg, concurrent.futures

**Key rule:** Use adaptive `tonemap()` for brightness — never linear multipliers (`canvas * N`). ASCII on black is inherently dark.

## Decision Flow

1. **Text as a banner** → pyfiglet if installed, otherwise asciified API via curl
2. **Wrap a message in fun character art** → cowsay
3. **Add decorative border/frame** → boxes (can combine with pyfiglet/asciified)
4. **Art of a specific thing** (cat, rocket, dragon) → ascii.co.uk OR asciiart.eu (see Tool 7)
5. **Convert a photo/image to ASCII** → `riso` pipeline (preferred — quality-gated, edge-aware presets). Fallback: ascii-image-converter or jp2a
6. **High-fidelity portrait with clean background** → `riso` with preprocessing (see riso/references/preprocessing.md)
7. **Animated eikon for mirror/avatar** → `riso` pipeline via `build-eikon-from-video`
8. **QR code** → qrenco.de via curl
9. **Weather/moon art** → wttr.in via curl
10. **Something custom/creative** → LLM generation with Unicode palette
11. **Any tool not installed** → install it, or fall back to next option
