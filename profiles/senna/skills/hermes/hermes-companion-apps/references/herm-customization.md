# herm TUI — Customization Reference

Theme engine, avatar animation, and preferences for the `herm` TUI client (liftaris/herm).

## Theme System

Theme JSON files follow the OpenCode schema: `$schema: https://opencode.ai/theme.json`

### File Layout

```
~/.hermes/herm/
├── tui.json                    # Preferences (theme name, animations, keys, etc.)
└── themes/
    └── <name>.json             # Custom theme files (auto-discovered)
```

### Theme JSON Structure

Two top-level sections:

```json
{
  "$schema": "https://opencode.ai/theme.json",
  "defs": {
    "myBg": "#0A0A1A",
    "myAccent": "#FF6B6B",
    "myText": "#E0E0E0"
  },
  "theme": {
    "primary": { "dark": "#FF6B6B", "light": "#CC3333" },
    "background": { "dark": "myBg", "light": "#F8F8F8" },
    "text": { "dark": "myText", "light": "#1A1A1A" },
    "accent": { "dark": "myAccent", "light": "#CC3333" },
    "border": { "dark": "#3A3A5C", "light": "#D0D0D0" },
    "hermAvatar": { "dark": "myAccent", "light": "#990000" }
  }
}
```

- **`defs`** — Named color references. Values can be hex strings or cross-references to other defs.
- **`theme`** — 40+ visual tokens. Each token has `dark` and `light` variants. Values can be hex, defs references, or ANSI 256 color codes.

### Complete Token Reference

Tokens not specified inherit from the default theme (tokyonight).

**Core (6):** `primary`, `secondary`, `accent`, `error`, `warning`, `success`, `info`

**Text (3):** `text`, `textMuted`, `selectedListItemText`

**Background (4):** `background`, `backgroundPanel`, `backgroundElement`, `backgroundMenu`

**Border (3):** `border`, `borderActive`, `borderSubtle`

**Diff (12):** `diffAdded`, `diffRemoved`, `diffContext`, `diffHunkHeader`, `diffHighlightAdded`, `diffHighlightRemoved`, `diffAddedBg`, `diffRemovedBg`, `diffContextBg`, `diffLineNumber`, `diffAddedLineNumberBg`, `diffRemovedLineNumberBg`

**Markdown (14):** `markdownText`, `markdownHeading`, `markdownLink`, `markdownLinkText`, `markdownCode`, `markdownBlockQuote`, `markdownEmph`, `markdownStrong`, `markdownHorizontalRule`, `markdownListItem`, `markdownListEnumeration`, `markdownImage`, `markdownImageText`, `markdownCodeBlock`

**Syntax (9):** `syntaxComment`, `syntaxKeyword`, `syntaxFunction`, `syntaxVariable`, `syntaxString`, `syntaxNumber`, `syntaxType`, `syntaxOperator`, `syntaxPunctuation`

**Herm (1):** `hermAvatar` — color of the sidebar ASCII avatar glyphs (defaults to `accent`)

**Numeric (1):** `thinkingOpacity` (default: 0.6)

### Theme Resolution

The resolver in `src/theme/resolve.ts`:
1. Reads `theme` object + `defs` from the JSON
2. For each token, resolves the dark/light variant based on terminal mode
3. Follows reference chains through `defs` (circular-detected, throws on loop)
4. Converts hex strings → OpenTUI RGBA objects via `RGBA.fromHex()`
5. Supports ANSI 256-color codes (0-15 standard, 16-231 cube, 232-255 grayscale)
6. Supports `"transparent"` / `"none"` → zero-alpha RGBA

### Source Code Reference

- `src/theme/types.ts` — TypeScript types (ThemeCurrent, ThemeJson, etc.)
- `src/theme/resolve.ts` — Resolver function with reference chain, ANSI, RGBA conversion
- `src/theme/builtin.ts` — Static imports of all 42 JSON themes, DEFAULT_THEME = "tokyonight"
- `src/theme/themes/*.json` — Individual theme files (same set as OpenCode)
- `src/theme/index.ts` — Public exports
- `src/theme/context.tsx` — ThemeProvider + useTheme hook for React components

## Avatar System

### Architecture

- `src/components/avatar/AnimatedAvatar.tsx` — React component that renders stateful frames
- `src/components/avatar/states/index.ts` — AvatarState type (6 states) + DEFAULT_EIKON + STATE_FRAMES fallback map
- `src/components/avatar/eikon.ts` — `.eikon` NDJSON parser (header + state declarations + frame data)
- `src/components/avatar/bundled.ts` — Ships bundled `.eikon` files from `assets/eikons/`, also scans `$HERMES_HOME/eikons/` for user-dropped files
- `src/components/avatar/default.eikon` — Bundled default avatar

### State Machine

6 states the avatar can be in:
- `idle` — Default, looping animation
- `listening` — User is speaking/typing
- `thinking` — Agent processing
- `speaking` — Agent responding
- `working` — Agent running tools
- `error` — Error state

### Animation Driver

Forward-only state driver:
- `intro` — frames `[0 .. loopFrom-1]` played once on state entry
- `loop` — frames `[loopFrom .. N-1]` repeated
- `loopFrom = 0` — no intro, loop whole sequence
- `loopFrom = N` — play once, hold last frame (timer stops, fires `onHold` callback)

### Eikon Format

NDJSON (newline-delimited JSON). Line 1 is the header object; subsequent lines are state declarations or frame data.

```jsonl
{"version":1,"name":"my-avatar","width":8,"height":12,"states":["idle","thinking"]}
{"state":"idle","fps":4,"frame_count":6,"loop_from":0}
{"f":0,"data":["  ____  "," /    \\ ","| o  o |","|  __  |","|_/  \\_|"]}
{"f":1,"data":["  ____  "," /    \\ ","| o  o |","|  __  |","|_/  \\_|"]}
...
{"state":"thinking","fps":6,"frame_count":4,"loop_from":2}
{"f":0,"data":["  ____  "," / ?? \\ ","| ?  ? |","|  __  |","|_/  \\_|"]}
...
```

Each state gets: `fps`, `frame_count`, `loop_from`. Each frame: `f` (index), `data` (array of strings, one per row).

## preferences.json (tui.json) Reference

Persisted to `$HERMES_CONFIG_DIR/tui.json` (defaults to `~/.hermes/herm/tui.json`).

Logic in `src/context/preferences.ts`:
- `load()` — Reads JSON, deep-merges with defaults, caches. Never throws — returns defaults on missing/corrupt file.
- `set(key, value)` — Writes merged prefs to disk with sorted keys. Silently fails on write error.
- `usePref(key)` — React hook subscribes to changes; re-renders on set().
- `get(key)` — Sync read of cached prefs.

### Quick Config Examples

```bash
# Current file location
cat ~/.hermes/herm/tui.json

# Switch theme to catppuccin
# Edit tui.json to set: "theme": "catppuccin"

# Disable animations
# Edit tui.json to set: "animations": false

# Custom avatar
# Drop a .eikon file anywhere, then in tui.json: "eikonPath": "/path/to/custom.eikon"
```
