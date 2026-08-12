---
name: hermes-skin-authoring
description: Create, read, combine, and troubleshoot Hermes TUI skins. Covers the full YAML schema (colors, spinner, branding, banner_logo, banner_hero, tool_emojis), where skins live, how to switch at runtime, and how to merge elements from multiple skins into a new one.
triggers:
  - "create a skin"
  - "modify a skin"
  - "combine skins"
  - "change theme"
  - "custom skin"
  - "/skin"
  - "display.skin"
  - "skin yaml"
  - "banner"
  - "banner_hero"
  - "convert my image"
  - "image to banner"
  - "ascii banner"
version: 1.8.0
author: Senna
license: MIT
metadata:
  hermes:
    tags: [hermes, skins, theming, customization, tui]
    related_skills: [hermes-agent, ascii-art]
---

IDENTITY: Designer.Themer. Create, combine, and troubleshoot Hermes TUI skins via YAML — colors, spinners, branding, ASCII banner art, tool emojis, and gradient color tags. Verify skin content from literal bytes on disk, not session memory.
Law: BlockGroupedColorTags — per-character tags inflate source lines 14× causing vertical text wrapping. Group 2-4 chars per tag.
WHENUSE: UserAsks{CreateSkin,ModifySkin,CombineSkins,ChangeTheme,CustomSkin,/skin}. ESPECIALLY:ImageToBannerHero{showMultipleWidthsBeforeCommitting}|SkinDeployment{move,copy,rename,replaceDefault}. NoSkip:PostChangeChecklist{nameMatch,configUpdate,noOrphans,/newOrRestart}.
REDFLAGS: ActiveSkinVsProfileDefault->DontAssumeReadFileOrAsk|UnquotedQuestionMarkInToolEmojis->YAMLParseError|PerCharColorTagsInBanner->VerticalText{fix:blockGrouped}|/skinMidSession->PartialRender{recommend/new}|BannerHeroInflatesFile->ConsiderOmittingForMinimal.
RATIONALIZATIONS: GuessActiveSkinFromConfig->Runtime/skinOverridesConfig|TrustSessionSummaryForSkinContent->ReadLiteralBytesOnDisk|UsePerCharGradientForWelcome->GroupedTagsProduceSameVisualAt65pctShorter.
QUICKREF: Create{Method{FromScratch,CombineSkins,CloneModify}}->Build{Colors{hex palette}->Spinner{faces,verbs,wings}->Branding{welcome,goodbye,labels}->ToolEmojis->BannerLogo{pyfiglet+gradient}->BannerHero{jp2a+multiStopGradient}}->Deploy{MoveToDir,UpdateName,UpdateConfig,Restart}->Verify{YAMLValid{pyLoad},NameMatch{CaseSensitive},UnclosedTags,Indentation,RightDirectory,/skinTest}.

Hermes TUI skins are YAML files that define the entire visual identity of the CLI experience — colors, spinners, boot messages, ASCII art banners, tool emojis, and more. This skill covers the full skin YAML schema, how to create new skins, combine elements from multiple existing skins, switch between them, and troubleshoot common issues.

## Where Skins Live

Skins are stored in YAML files. The canonical locations (in load order):

1. **Global skins:** `~/.hermes/skins/` — available to all profiles
2. **Per-profile skins:** `~/.hermes/profiles/<name>/skins/` — available only to that profile

Both directories function identically. The name of the skin is the `name:` field in the YAML frontmatter, not the filename (though they should match for clarity).

## How the Desktop App Consumes Skins

The desktop app's Themes page merges THREE sources (verified in `apps/desktop/src/themes/`):

1. **Built-in presets** — hardcoded in the app (`presets.ts`: nous, etc.)
2. **User themes** — pasted via the app UI, stored in renderer localStorage (`user-themes.ts`, key `hermes-desktop-user-themes-v1`). Desktop-only; CLI/TUI never see these.
3. **Backend-synced skins** — the shared path. The Hermes backend resolves `$HERMES_HOME/skins/*.yaml` and pushes them to the desktop over JSON-RPC (`gateway.ready`, `skin.changed`; `backend-sync.ts`). `skin.ts` converts the skin palette into a desktop theme: it seeds from the load-bearing keys (background, foreground, accent, error) and derives all glass/shadcn surfaces by mixing toward bg/fg. A skin is single-mode; desktop picks `.dark` from background luminance.

Practical consequences:

- **The desktop does NOT read YAML files itself** — the backend does and pushes them. New skins not appearing → restart the backend/gateway and reload the app.
- **Relaunch mechanics (macOS):** the app is launched with `hermes desktop` from a terminal. Quit with Cmd+Q (closing just the window or terminal can leave the backend alive), then rerun `hermes desktop`. Skins are read at runtime by the backend on connect (`gateway.ready`) — no app rebuild ever needed for skin changes. If new skins still don't show after relaunch, a stale backend is still running: `hermes gateway restart` (or `pkill -f hermes` as the nuclear option) and relaunch.
- **One skin file themes all three surfaces** (CLI, TUI, desktop). There is no separate "desktop theme" file format; community "desktop theme packs" (e.g. CliffWade/hermes-desktop-theme-pack, 24 WCAG-AA-checked YAMLs) are just plain skins installed to `~/.hermes/skins/`.
- **`$HERMES_HOME` is profile-aware**: if the desktop is connected to a profile's backend (e.g. senna), it sees `~/.hermes/profiles/senna/skins/`, not the root `~/.hermes/skins/`. Skins installed globally that don't show in the desktop usually means the desktop backend runs under a profile home — copy/symlink the YAMLs into the profile skins dir.
- Skins carry terminal-only keys (banner/spinner/completion) that the desktop converter ignores — a palette-only skin still works fine on desktop.

## Skin YAML Schema

A skin has these top-level sections. All are optional — missing fields fall through to defaults.

### `name` (string, required)
The skin identifier. Used with `/skin <name>` and `hermes config set display.skin <name>`.

### `description` (string)
A one-liner describing the aesthetic, shown in skin listings.

### `colors` (map of hex color strings)
The largest and most configurable section. Key color groups:

| Group | Keys | Example |
|-------|------|---------|
| **Banner** | `banner_border`, `banner_title`, `banner_accent`, `banner_dim`, `banner_text` | Purple monarchy |
| **UI** | `ui_accent`, `ui_label`, `ui_ok`, `ui_error`, `ui_warn` | Action colors |
| **Prompt** | `prompt`, `input_rule` | Input area — `prompt` controls the color of text the user types at the prompt; `input_rule` colors the underline/hint under the input line |
| **Response** | `response_border`, `response_text` | Message bubbles — `response_text` controls the color of the AI's response output; `response_border` colors the left-side border
| **Reasoning** | `reasoning_border`, `reasoning_text` | Thinking blocks |
| **Session** | `session_label`, `session_border` | Session header |
| **Status bar** | `status_bar_bg`, `status_bar_text`, `status_bar_strong`, `status_bar_dim`, `status_bar_good`, `status_bar_warn`, `status_bar_bad`, `status_bar_critical` | Bottom bar |
| **Voice** | `voice_status_bg` | Voice mode badge |
| **Selection** | `selection_bg`, `completion_menu_bg`, `completion_menu_current_bg`, `completion_menu_meta_bg`, `completion_menu_meta_current_bg` | Autocomplete dropdown |

Color values can be:
- Quoted: `"#A855F7"` or `"#8B0000"`
- Single-quoted: `'#D4A017'`
- Unquoted: `#6B21A8`

Custom color keys can be added (e.g., `blade_glow: "#EF0131"`) and referenced in the `banner_logo` or `banner_hero` sections, but they have no effect on UI chrome — the standard keys drive the actual terminal rendering.

### `spinner` (map of arrays)

```yaml
spinner:
  waiting_faces:         # Spinner frames while waiting for response
    - (☾)
    - (⚔)
  thinking_faces:        # Spinner frames while model is thinking/reasoning
    - (☾)
    - (⚔)
  thinking_verbs:        # Status text shown alongside spinner
    - entering the gate
    - drawing steel
  wings:                 # Paired bracket decorations around spinner
    - - ⟪☾
      - ☾⟫
    - - ⟪⚔
      - ⚔⟫
```

- `waiting_faces` and `thinking_faces`: usually 4-5 unique symbols each.
- `thinking_verbs`: 10-12 phrases that cycle. Should be present-tense actions.
- `wings`: each entry is a 2-element array `[left, right]`. Cycle randomly.

### `branding` (map of strings)

```yaml
branding:
  agent_name: "Shadow Monarch"     # Shown in the UI header
  welcome: "[#A855F7]A[/]RISE."   # Boot message with optional tag-based gradient coloring
  goodbye: "The dungeon has closed."  # Shown on exit
  response_label: " ☾ MONARCH "   # Badge before responses
  prompt_symbol: "☾ "             # Prefix at the input prompt
  help_header: "(☾) Commands"     # Header for /help output
```

**Tag-based gradient coloring in welcome/goodbye:**
The `welcome` and `goodbye` strings support inline color tags for per-character gradients:

```
"[#A855F7]A[/][#A758F4]R[/][#A65CF2]I[/]SE."
```

Each character (or group) is wrapped in `[#HEX]text[/]`. By interpolating hex values between a start and end color, you create a smooth gradient across the message. The gradient technique:
1. Choose start and end hex colors
2. Generate N intermediate hex values (one per character/group)
3. Wrap each character: `[#COLOR]char[/]`

**Quick Python one-liner for generating gradient welcome text:**

```python
python3 << 'PYEOF'
def lerp_color(c1, c2, t):
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02X}{g:02X}{b:02X}"

text = "Connection established. Neural link active."
c1, c2 = "#D4A017", "#8B0000"  # gold -> blood red
result = ""
for i, ch in enumerate(text):
    t = i / (len(text) - 1) if len(text) > 1 else 0
    color = lerp_color(c1, c2, t)
    result += f"[{color}]{ch}[/]"
print(result)
PYEOF
```

**Example gradients from existing skins:**
- Netrunner: `Connection established. Neural link active.` — teal `#00897B` → white `#FFFFFF` over ~40 characters
- Solo Leveling Boss: `ARISE. The system has chosen.` — purple `#A855F7` → cyan `#7FFFD4` over ~30 characters
- Kensei: `Steel drawn. State your objective.` — gold `#D4A017` → blood-red `#8B0000` over ~25 characters
- ONI: `Connection established. Neural link active. Blade drawn. State your objective — or /help for protocols.` — gold `#D4A017` → blood-red `#8B0000` over ~86 characters

### `tool_prefix` (string)
Character/string prepended to tool output lines. Convention: pipe-like characters.
- Netrunner: `▏`
- Solo Leveling Boss: `│`
- Kensei: `│`

### `tool_emojis` (map of tool-name → emoji/string)

```yaml
tool_emojis:
  terminal: ☾
  web_search: ⫷
  read_file: 巻
  write_file: ⚔
  search_files: ⌖
  execute_code: ⚡
  memory: 心
  clarify: '?'
  mixture_of_agents: 衆
  todo_write: ▰
  task: ⟨⟩
```

Each tool type gets an icon shown inline during execution. These are purely cosmetic. You can define icons for any tool, or leave tools unassigned (they get default icons).

**YAML pitfall:** The `?` character has special meaning in YAML (it starts a mapping key). Always quote it: `clarify: "?"` or `clarify: '?'`. Failure to quote will produce a YAML parse error.

### `banner_logo` (block string, `|-` style)
ASCII art shown as the primary banner on startup. Supports inline color tags (`[#HEX]text[/]`). Usually a text-based logo (wordmark or ASCII art name).

Example pattern:
```yaml
banner_logo: |-
  [#A855F7]
       ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗
       ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ██║
       ...[/]
```

For simple text logos, use pyfiglet to generate ASCII art banner text, then apply grouped-gradient color tags. This produces a wordmark that fills the hero width (~80 chars) rather than a narrow 20-char logo.

**Quick pipeline:**

1. Install pyfiglet in a venv: `python3 -m venv /tmp/figlet_v && /tmp/figlet_v/bin/pip install pyfiglet`
2. Find fonts that fill banner width: `FigletFont.getFonts()` filtered to ~40-80 char width, 5-9 line height (see `references/banner-logo-pyfiglet.md` for font selection table)
3. Generate text: `Figlet(font='roman', width=90).renderText('NAME')`
4. Apply grouped gradient color tags (block_size=3, gold→blood-red or your palette colors)
5. Add a decorative separator line (e.g., `━━━ ⚔  ☾  ◎ ━━━`) with a fixed accent color — do NOT gradient the separator
6. Verify source lines stay under ~250 bytes each to avoid TUI wrapping
7. Validate YAML

See `references/banner-logo-pyfiglet.md` for the full step-by-step pipeline, font selection guide, and a worked example ("SEN" in roman font).

### `banner_hero` (block string, `|-` style)
Extended ANSI/unicode art shown below the banner_logo during startup. Supports both inline color tags AND terminal-format colored Braille/symbol art using the standard terminal color tag syntax.

Banner_hero can contain:
- Braille-pattern art (using ⠀ characters with color tags)
- Extended unicode block art
- Decorative borders and frames with custom characters
- Mixed text and visual elements
- Image-to-ASCII converted art from tools like `jp2a`

It is typically the largest section of a skin file (the solo-leveling-boss banner_hero is ~18KB).

**Generating banner_hero art from images:** See the `ascii-art` skill for details. The common pipeline:
1. **Find a reference image.** For generic art (silhouettes, masks, swords), try openclipart.org. For a specific character (anime, game, manga), see `references/finding-character-reference-images.md` — the canonical wiki reference matters more than resolution.
2. **Verify the image** with `vision_analyze` — confirm it actually shows what you need before converting. This catches fan art that doesn't match the canonical design.
3. Download the 800px+ PNG version
4. Convert with `jp2a --width=68 --invert image.png`
5. Wrap the output in `[#ACCENT_COLOR]...[/]` inside the YAML `|-` block

**Pitfall:** Don't trust image filenames or alt text — many wallpaper sites mislabel fan art. Always verify with `vision_analyze` that the image actually shows the intended character with the correct features (body shape, expression, accessories).

**User-submitted image workflow (interactive width preview):**
When the user provides their own image (local file path) for a banner_hero, do NOT commit to a single width up front. The user needs to see options:

1. Check the image file: `file <path>` to confirm format and dimensions. Portrait/manga-style AI art from Stable Diffusion (txt2img) is common — 1152×1920 portrait works well.
2. If the vision API can't analyze the image (model doesn't support vision, file too large, format issue), do NOT stall — convert with jp2a directly. The ASCII output serves as both preview AND silhouette inspection.
3. Convert at multiple banner widths using `jp2a --width=<N> --invert <path>` and count lines with `wc -l`:
   - width=68 → ~55-60 lines (most detail, tall banner)
   - width=60 → ~48-52 lines (middle ground)
   - width=50 → ~40-44 lines (solid banner height)
   - width=40 → ~30-35 lines (compact, clean silhouette)
4. Show the user the line counts and a visual preview at each candidate width.
5. Let them choose before proceeding to color-tagging and injection.
6. Once chosen, wrap the ASCII in color tags and inject into the `banner_hero:` block.

**Multi-stop gradient wrapping (advanced):** Instead of wrapping all 57 lines in a single `[#ACCENT]...[/]`, apply a per-line gradient using a Python multi-stop lerp. This gives the art depth — e.g., dark at the top, bright accent in the middle, gold at the bottom:

```python
def lerp_color(c1, c2, t):
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02X}{g:02X}{b:02X}"

# Multi-stop color gradient: (hex, position) pairs
colors = [("#8B0000", 0.0), ("#C0392B", 0.4), ("#E34234", 0.65), ("#D4A017", 1.0)]

def multi_stop(t):
    for i in range(len(colors)-1):
        c1, p1 = colors[i]; c2, p2 = colors[i+1]
        if p1 <= t <= p2:
            return lerp_color(c1, c2, (t - p1) / (p2 - p1))
    return colors[-1][0]

lines = ["... jp2a output line ..."]  # 57 lines
for i, line in enumerate(lines):
    t = i / (len(lines) - 1)
    color = multi_stop(t)
    print(f"  [{color}]{line}[/]")
```

This produces distinct hex values per line so every row has a unique color in the gradient, creating a smooth transition across the full art.

**Choosing stops for the palette:** Match the skin's existing colors — pull from the skin's `colors:` section. Common patterns:
| Skin palette | Gradient stops | Effect |
|---|---|---|
| Blood red + gold (kensei/senna) | `#8B0000` → `#C0392B` → `#E34234` → `#D4A017` | Dark ominous top → bright center → gold base |
| **Dragon's Breath** (Valyrian/fire) | `#5C0000` → `#8B0000` → `#C0392B` → `#E8630C` → `#F4A000` | Wine-dark top → blood red → crimson → fiery orange → golden. Hotter/warmer than kensei — the gold shifts to orange and deep wine replaces brown |
| Purple + cyan (solo-leveling-boss) | `#581C87` → `#7C3AED` → `#A855F7` → `#7FFFD4` | Deep shadows → glow → magical accent |
| Teal + white (netrunner) | `#004D40` → `#00897B` → `#00BCD4` → `#E0F7FA` | Dark base → neon rise → bright highlight |

**Patching the result into the skin file:** Use the `patch` tool with the full `banner_hero: |-` block (from `banner_hero: |-` through the last `[/]`) as `old_string` and the new gradient-wrapped block as `new_string`. The patch tool's built-in YAML linter will validate automatically.

**Recoloring an existing banner_hero from another skin (per-character palette remapping):**

When you want to use banner_hero art from a different skin in your target skin's color palette, the source likely uses per-character multi-tag coloring (e.g., `[#203050]%[/][#203060]%%%[/]...`). There are two approaches:

### Approach A: Per-character remapping (preserves shading/depth — preferred)

Parses every `[#HEX]char[/]` pair, maps the original color's luminance to the
target gradient, and re-wraps in 4-char block-grouped tags. The figure retains
its 3D depth — dark shadows become dark wine, bright highlights become gold.

Uses `scripts/per-character-palette-remap.py` (included in this skill):

```bash
# Quick one-shot from a script call:
python3 ~/.hermes/profiles/senna/skills/hermes/hermes-skin-authoring/scripts/per-character-palette-remap.py \
  ~/.hermes/skins/solo-leveling-boss.yaml \
  /tmp/new-banner.txt
```

Then patch the output into the target skin using the `patch` tool with the
current banner_hero block as `old_string` and the file contents as `new_string`.

The algorithm:
1. Parse each character's `[#ORIG_HEX]char[/]` tag from the source banner
2. Convert ORIG_HEX to HSL, extract luminance L (0.0 = dark, 1.0 = bright)
3. Map L to a position in the target gradient: dark→first stop, bright→last
4. Interpolate to get the new hex value in the target palette
5. Group consecutive characters into blocks of 4 (controls source line length)
6. Wrap each block: `[#NEW_HEX]block_text[/]`

See `references/per-character-palette-remap.md` for the full worked example
(solo-leveling-boss → senna fire palette, 41 lines, 621 tags, 0 balance errors).

### Approach B: Per-line single tag (simpler, more compact)

When file size is a concern or the art is blocky/abstract (not a detailed figure),
strip tags and wrap each entire line in one color:

1. Extract the banner_hero block from the source skin using `read_file`
2. Write a Python script that reads those lines, strips ALL `[#HEX]` and `[/]`
   tags with regex (`re.sub(r'\\[/?[^\\]]*\\]', '', line)`), giving you the raw
   character content per line
3. Apply a multi-stop gradient by wrapping each line in a single
   `[#COLOR]raw_line[/]` tag (one color per line)
4. Patch into the target skin

~3KB for 41 lines vs ~8.5KB for per-character. Use this when the original
art doesn't have fine shading worth preserving.

**Image format conversion (macOS):** When a user provides a WebP image for jp2a conversion and PIL/Pillow isn't available, use macOS's built-in `sips`:
```bash
sips -s format png input.webp --out output.png
```
This avoids needing to install Pillow globally or in a venv. Works on any macOS system (Intel or Apple Silicon).

Pitfall: Do not guess what width the user wants based on the source image dimensions alone — the banner container's width is fixed (~68 chars), not the image's. Always offer options.
Pitfall: For multi-stop gradients, ensure the Python script generates the full YAML block correctly before patching — count the output lines and verify the last line closes with `[/]`. Patch failures from mismatched old_string are hard to debug.
Pitfall: When producing the full skin block for patching, include the `banner_hero: |-` key line in both old_string and new_string — the patch operates on literal text, not YAML structure. Omitting the key line makes the match ambiguous.
Pitfall: When recoloring an existing multi-tag banner_hero, the recolor script must produce lines with exactly one `[#HEX]...[/]` tag per line (not multiple per line). Verify with a simple grep pattern count before patching — mismatched tag counts cause YAML parse errors or invisible banner output.

See `references/user-image-to-banner-hero.md` for a worked example converting a 1152×1920 Stable Diffusion portrait into a 57-line 4-stop gradient banner hero.

**Banner line-height guidance:**
| Lines | Sits well | Best for |
|-------|-----------|----------|
| ≤25 | Above the fold, leaves room | Minimal skins |
| 30-45 | Solid banner, room for branding | Most skins |
| 50-60 | Dominant — pushes tool output down | Maximalist or art-first skins |
| 60+ | Risk of pushing below fold | Only if the art justifies it |

See `references/banner-hero-examples.md` for technique patterns: how Braille art is built, how gradient borders work, and how to construct a simple hero block.

#### Color tags in banner art and terminal-width wrapping

A critical gotcha: **per-character color tags inflate the source line length dramatically**, which causes the TUI's banner display to wrap long lines — projecting each character onto its own row. This makes text appear vertical and misaligned.

**Math:** Each `[#HEX]char[/]` tag adds ~14 bytes of markup for 1 rendered character. A 53-character English quote becomes ~700 source bytes. If that exceeds the TUI's banner container width, every character wraps independently → vertical text.

**Fix: block-grouped color tags.** Instead of one tag per character, group 2-4 characters under each tag with the same gradient interpolation:

```python
# Per-character (BAD — 689 source bytes for 53 rendered chars):
[#D4A017]A[/][#D49A18] [/][#D5951A]m[/][#D68F1C]a[/][#D78A1D]n[/]...  # 53 tags

# Block-grouped (GOOD — 221 source bytes, same visual):
[#D19916]A ma[/][#CB8D14]n wi[/][#C68112]thou[/][#C07510]t co[/]...   # 14 tags
```

The rendered output is identical — same smooth gradient — but the source line fits within the banner container.

**Choosing block size:**
| Content type | Block size | Source length reduction |
|---|---|---|
| CJK (2-3 char words) | 2 | ~45% shorter |
| English prose | 4 | ~65% shorter |
| Romaji/transliteration | 3 | ~60% shorter |

A reusable script `scripts/gradient-color-tags.py` is included in this skill. Use it instead of hand-writing grouped tags.

See `references/banner-hero-examples.md` for technique patterns: how Braille art is built, how gradient borders work, and how to construct a simple hero block.

## How to Create a New Skin

### Method 1: From Scratch
1. Create a new YAML file in `~/.hermes/skins/` or `~/.hermes/profiles/<profile>/skins/`
2. Set a unique `name:` and `description:`
3. Define the `colors:` section (start with an existing skin's palette and adjust)
4. Define `spinner:`, `branding:`, `tool_emojis:`, `banner_logo:`, `banner_hero:`
5. Switch to it: `/skin <name>` from within a session, or `hermes config set display.skin <name>` then restart

### Method 2: Combine Elements from Multiple Skins (as in this session)
1. Decide which elements to pull from each source skin
2. Copy the `colors:` section from the dominant aesthetic, or create a hybrid palette
3. Copy `spinner:` from one source (or build a hybrid from multiple)
4. Write a new `branding.welcome:` using the tag-gradient technique, optionally inspired by the netrunner-style boot sequence
5. Create `tool_emojis:` by selecting your preferred symbols from each source
6. For `banner_logo:` and `banner_hero:` — either use one from a source, create a new one, or omit for a minimal skin.

   **To copy a banner_hero between skin files using `patch` (common operation):**
   - Read both source and target skin files with `read_file` to see the exact content
   - Identify the boundaries of the `banner_hero: |-` block in both files. The block starts with the `banner_hero: |-` line itself and ends with the closing `[/])` tag on its own line
   - Use `patch` with the target file's current `banner_hero` block as `old_string` and the source file's full block (from `banner_hero: |-` through `[/])` as `new_string` — include the opening key line so the match is unambiguous
   - Verify the patch succeeded by re-reading the target file with `read_file`
   - **Important:** The `old_string` must match the file content exactly — whitespace, indentation, and trailing spaces count. Copy-paste from the file read, don't retype.
7. Test with `/skin <name>` — if it works, it will load immediately (new session). If it fails, check YAML validity.

**Worked example: the ONI skin** — see `references/oni-skin-session.md` for the full merge of solo-leveling-boss, kensei, and netrunner skins into a single oni-themed skin.

### Method 3: Clone and Modify
1. Copy an existing `.yaml` to a new name: `cp kensei.yaml my-custom.yaml`
2. Change `name:` and `description:` at the top
3. Swap colors one at a time
4. Replace spinner symbols and verbs
5. Rewrite branding strings
6. Customize tool_emojis

## Verifying a Skin Loads Correctly

```bash
# Start a session with the new skin
hermes --profile <profile> --skin <name>
# OR in-session:
/skin <name>
# Then /reset to apply changes fully
```

If the skin doesn't load:
1. Check the YAML is valid: `python3 -c "import yaml; yaml.safe_load(open('path/to/skin.yaml'))"`
2. Check the `name:` field matches (case-sensitive)
3. Check the file is in the right directory (`~/.hermes/skins/` or per-profile)
4. Check for unclosed color tags — every `[#HEX]` must have a matching `[/]`
5. Check for YAML indentation errors (especially in `banner_hero` block strings)
6. Check for unquoted `?` in tool_emojis (`clarify: ?` → `clarify: "?"`)

## Skin Deployment & Lifecycle

Beyond creating and editing a skin, you'll need to deploy it to the right location, rename it, and keep config in sync.

### Moving a Skin Between Locations

Skins can live in **global** (`~/.hermes/skins/`) or **per-profile** (`~/.hermes/profiles/<name>/skins/`) directories. To move a skin:

1. **Copy** the YAML file to the target directory
2. **Remove** it from the source directory
3. **Update** `display.skin` in the relevant profile config if the skin name changed
4. **Restart** the session for the change to take effect

Per-profile skin files take priority over global ones with the same `name:` field. Be deliberate about placement.

### Bulk-Importing a Skin Pack (collision hazard)

When installing a public skin pack (`cp skins/*.yaml ~/.hermes/skins/`), same-named
files are silently OVERWRITTEN — no warning, no merge. Real incident 2026-08-03:
importing bchop-studio/hermes-skins-pack clobbered the local `netrunner` (7.2K full
skin with banner_hero/branding/spinner) with the pack's minimal 1.3K palette-only
variant. The original survived only because the senna profile skins dir still
mirrored it — recovery was `cp ~/.hermes/profiles/senna/skins/netrunner.yaml ~/.hermes/skins/`.

Before a bulk import:
1. Diff pack names against `ls ~/.hermes/skins/` (and per-profile dirs) FIRST.
2. For each collision, decide which version wins — pack skins are usually minimal
   complete-palette YAMLs (~1.3K, no banner_hero/spinner/branding), so the richer
   local skin typically wins. Keep the pack's file only if you want the stripped look.
3. Copy with `cp -i` (prompts per overwrite) or exclude colliding files explicitly.
4. Verify after import: every file's `name:` field matches its filename
   (`grep -m1 '^name:' *.yaml`), and spot-check a couple of colors you expected.
5. Profile skins dirs mirror globals by default, so a clobbered global skin is
   usually recoverable from the matching per-profile dir — check there before
   reaching for git or re-downloads.

### Fleet-Wide Sharing via Symlink (multi-profile setups)

Problem: `$HERMES_HOME` is profile-aware, so profiles only see their own `skins/` dir — skins installed to the root `~/.hermes/skins/` are invisible to other profiles' CLIs and to a desktop app connected to a profile backend.

Fix (done fleet-wide 2026-08-04): replace each profile's skins dir with a symlink to the root:

```bash
cd ~/.hermes/profiles
for p in */; do
  p=${p%/}; s="$p/skins"
  [ -L "$s" ] && continue                                    # already linked
  if [ -d "$s" ]; then
    if [ -n "$(ls -A "$s")" ]; then cp "$s"/*.yaml ~/.hermes/skins/; mv "$s" "$s.bak"
    else rmdir "$s"; fi
  fi
  ln -s ~/.hermes/skins "$s"
done
```

Pitfall — same-name/different-content collision: when merging a profile dir into root, a filename may exist in both with DIFFERENT skins inside (real case: `senna.yaml` — profile's dragon palette vs root's netrunner-imperial palette). Don't silently overwrite. Rename the divergent one (`senna-imperial.yaml`, and update its `name:` field to match), keep both. Check with `diff -q` per file before copying; identical files need no action.

After symlinking, one canonical set serves every profile and the desktop app regardless of which profile's backend it connects to. Keep the `.bak` dir until verified, then delete.

### Renaming a Skin

Renaming requires three coordinated changes — skipping any one breaks the skin:

1. **Change the `name:` field** in the YAML file (this is what Hermes actually loads by)
2. **Rename the file** (optional but recommended for clarity — mismatched name/filename works but causes confusion later)
3. **Update `display.skin`** in the profile's `config.yaml` to the new name

```
# Before:
#   ~/.hermes/profiles/senna/skins/oni.yaml  → name: oni
#   config.yaml → skin: oni
# After:
#   ~/.hermes/profiles/senna/skins/senna.yaml → name: senna
#   config.yaml → skin: senna
```

### Replacing a Profile's Default Skin

Each profile usually has a default skin named after the profile (e.g., `senna.yaml` in the `senna` profile's skins directory). To replace it with a different skin:

1. **Delete** the old default skin file (`senna.yaml`) from the profile skins directory
2. **Delete** any other old skin files you're replacing (e.g., `oni.yaml`)
3. **Copy** the new skin into the profile skins directory as the default name (`senna.yaml`)
4. **Update** the `name:` field in the YAML to match the new filename
5. **Verify** `display.skin` in the profile's `config.yaml` is set to the new name
6. **Start a new session** with `/new` to apply

Example from a real session — replacing the `senna` profile's default skin with an updated oni-themed skin:

```
# Clean up old files
rm ~/.hermes/profiles/senna/skins/oni.yaml
rm ~/.hermes/profiles/senna/skins/senna.yaml

# Write the new skin as the profile default
# (write the updated content to senna.yaml with name: senna)

# Update config
# config.yaml: skin: oni → skin: senna
```

### Config Visibility vs Runtime Override

There are two channels for setting the active skin, and they behave differently:

| Channel | How | Persistence | Priority |
|---------|-----|-------------|----------|
| **Config** | `display.skin: senna` in `config.yaml` | Permanent (disk) | Lower — default for new sessions |
| **Runtime** | `/skin senna` inside a session | Current session only | Higher — overrides config |

- `/skin` does not write to `config.yaml`. If a user sets a runtime skin and then restarts, the config default is used.
- `display.skin` in config sets the default for all new sessions. Changing it requires a restart.
- If you rename a skin or change its location, update `display.skin` in config — otherwise the next session will fail to find the old name and fall back to defaults.
- To see the active skin: read `config.yaml` line containing `skin:` and/or observe the banner on startup.

### Checklist: After Any Skin Structure Change

- [ ] Skin file exists in the intended directory
- [ ] `name:` field in YAML matches the intended skin name
- [ ] `display.skin` in profile `config.yaml` matches the name
- [ ] No orphaned skin files left in old locations
- [ ] `/new` or session restart confirms the skin loads without error

## Community Tools

**hermes-mod** (`npx -y hermes-mod`): Web-based visual skin editor by cocktailpeanut (Pinokio creator). Good for quick scaffolding and image-to-banner conversion without touching YAML. Does NOT support per-character gradients or per-profile skins — use our skill for advanced work. See `references/hermes-mod-gui-tool.md` for full review.

## Pitfalls

- **Active skin vs profile default — don't guess.** When a user asks about colors or wants to customize, do not assume the profile's default skin (e.g., `senna.yaml` for the `senna` profile) is what they're seeing. The active skin may have been switched at runtime via `/skin <name>`. A user may have loaded the `oni` skin in a previous session and it persists. Read the active skin file directly or ask "which skin are you using?" before making changes. Setting `display.skin` in config only changes the default — the runtime `/skin` command overrides it session-to-session and does not update config.

- **`banner_hero` can inflate file size dramatically.** The solo-leveling-boss skin is 24KB, of which ~18KB is banner_hero. Consider omitting banner_hero for a minimal skin.
- **Color tag mismatch in banner strings.** Forgetting a closing `[/]` in a long `welcome` gradient causes all subsequent text to be colored, breaking the display. Always pair `[#HEX]` with `[/]`.
- **Skin name vs filename.** The skin is loaded by `name:` field, not the filename. Two files with the same `name:` cause ambiguity. Keep them consistent.
- **Profile vs global.** A skin in `~/.hermes/profiles/senna/skins/` takes priority over the same name in `~/.hermes/skins/`. Be deliberate about placement.
- **Per-skin custom color keys.** You can define extra color keys (e.g., `blade_glow`, `blade_edge`) for use in banner_art, but they don't affect the TUI chrome. Only the standard `colors.*` keys drive actual UI rendering.
- **Wings format is a 2-element list.** Each entry in `spinner.wings` must be `[left_bracket, right_bracket]`. If formatted as a flat list of strings, the spinner code will error silently.
- **Unquoted `?` in YAML.** The `?` character starts a mapping key in YAML. In `tool_emojis`, always quote: `clarify: "?"` or `clarify: '?'`.
- **Raw `[#HEX]...[/]` markup visible in terminal output = the string went through plain `print()` instead of the rich console.** Symptom seen 2026-07-27: user closed Hermes and the goodbye gradient printed as literal color tags. Cause: `_print_exit_summary` in `cli.py` printed the goodbye with `print(goodbye)`, while the welcome banner renders via `self._console_print()` (rich, parses markup). Fix: route through `self._console_print(goodbye)` with a plain-`print` fallback (patched locally at `cli.py` ~L13704; note this is a local fork patch — an upstream `hermes update` may revert it, worth an upstream PR). Diagnose rule: grep the render path for `print(` vs `_console_print(`.
- **Per-character color tags cause vertical text in banners.** When `banner_hero` or `banner_logo` lines use one `[#HEX]char[/]` tag per character, the source line length balloons ~14× the rendered width. If the source exceeds the TUI banner container width, each character wraps to its own row → text appears vertical and misaligned. Fix: use block-grouped color tags (2-4 characters per tag) via `scripts/gradient-color-tags.py`.
- **Gradient welcome text too long.** Very long welcome strings (~100+ characters) generate huge YAML values. Consider truncating the message or using shorter words. 60-90 characters is manageable.
- **Verify skin content directly — don't reconstruct from memory or session summaries.** When checking whether a skin file contains expected changes (banner_hero art, specific hex codes, branding text), always `read_file` the actual YAML. Session summaries can be stale, describe a version at a different path, or reference changes that were later overwritten. Trust the literal bytes on disk, not the assistant's reconstruction of what happened in past sessions.
- **Em dash characters in YAML.** The em dash (`—`) can cause encoding issues when pasted from Python output. Verify it survived into the YAML file. Check that `\\u2014` (Python escape) rendered as the actual `—` character, not a literal backslash-u string.
- **`/skin` mid-session may not fully render all color elements.** The banner, spinners, and branding switch immediately, but `prompt`, `response_text`, and `session_label` colors may stay on the old values until a fresh session. If a user reports "colors didn't change" after `/skin`, the skin file is likely correct — recommend `/new` or a full terminal restart (Ctrl+C + `hermes`).
- **`/new` can produce an asyncio RuntimeWarning.** Under some Hermes TUI versions, `/new` prints: `RuntimeWarning: coroutine 'run_in_terminal.<locals>.run' was never awaited`. This is non-fatal — the session may or may not have restarted cleanly. If the user reports this, recommend exiting with Ctrl+C or `/exit` and restarting from the terminal with `hermes`.

## Existing Skins Reference (this user's setup)

| Skin | Aesthetic | Dominant Colors | Prompt Symbol |
|------|-----------|----------------|---------------|
| **senna** *(profile default)* | Valyrian dragon-rider / fire & blood | Blood red (#8B0000), golden orange (#F4A000), fiery orange (#E8630C) | `◎ ` |
| solo-leveling-boss | Shadow Monarch / dark fantasy | Purple (#A855F7), aquamarine (#7FFFD4) | `☾ ` |
| kensei | Sword saint / samurai | Blood red (#8B0000, #E34234), gold (#D4A017) | `⚔ ` |
| netrunner | Cyberpunk hacker | Teal/cyan (#00E5FF, #00BCD4) | `◎ ❯ ` |
| dos | Retro terminal | Amber/green CRT | — |
| empire | Sci-fi imperial | Red/black | — |
| neonwave | Synthwave | Pink/cyan | — |
| sakura | Japanese floral | Pink/cream | — |
| skynet | Machine/terminator | Red/gray | — |
| mythos | Mythological | Gold/deep blue | — |
| nous | Nous Research brand | Brand colors | — |
| pirate | Pirate | Wood/sea | — |
| bubblegum-80s | Retro bright | Magenta/yellow | — |
| mother | Maternal/soft | Warm/pastel | — |
| lain | Tech/psychological | Cyber/desaturated | — |
| vault-tec | Fallout Vault Boy | Blue/yellow | — |
| telemate | Retro terminal buddy | Green/amber | — |

**IMPORTANT:** This table describes the skin's intended aesthetic. Always verify on-disk availability with `ls ~/.hermes/skins/` and `ls ~/.hermes/profiles/<profile>/skins/` before suggesting or switching — skins may have been renamed, replaced, or removed since this table was last updated.

**2026-08-03 fleet update:** bulk-imported 49 skins from bchop-studio/hermes-skins-pack
(50-skin public pack, MIT) into `~/.hermes/skins/`. Only name collision was `netrunner`
(local richer version kept). The 49 pack skins are minimal complete-palette YAMLs
(~1.3K each — colors + prompt symbol only, no banner_hero/spinner/branding). Notable
for the user's noir/game taste: dragon-blood, shadow-thief, forge-master, arcane-tome,
void-sunset, chrome-rain. Install path for more packs: see Bulk-Importing above.

**2026-08-04 fleet update:** installed 24 more skins from CliffWade/hermes-desktop-theme-pack
(WCAG-AA-checked palettes, 6 categories; "desktop theme pack" is a misnomer — plain skins)
into `~/.hermes/skins/` (no collisions). Same day: all 23 profiles' skins dirs replaced
with symlinks to root — see Fleet-Wide Sharing above. Root's old `senna.yaml` (different
skin, same name) survives as `senna-imperial.yaml`; senna profile originals backed up at
`~/.hermes/profiles/senna/skins.bak`.

See `references/skin-details.hybridization-era.md` for the source-skin analysis that fed into the oni skin, and `references/oni-skin-session.md` for the full build log.
See `references/finding-character-reference-images.md` for how to find and verify canonical images of specific characters (anime, manga, games) for banner_hero conversion — includes a ranked source list and verification workflow.
