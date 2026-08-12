# Third-Party Hermes Frontends

Landscape of community-built frontends that talk to the Hermes gateway instead of (or alongside) the built-in CLI/TUI. Each replaces or augments the terminal — useful when the user wants to "get out of the terminal."

## Landscape

```
Hermes CLI/Gateway (the core — talks to LLM providers, runs tools, manages sessions)

    ├─ CLI/TUI ───────────→ hermes (built-in terminal interface)
    │                        or herm (3rd-party TUI, OpenTUI/Bun)
    │
    ├─ Web UI ─────────────→ hermes-webui (nesquena, 6.9k ★, browser-based)
    │                        └─ hermes-swift-mac (native Mac window for Web UI)
    │
    ├─ Desktop ───────────→ Hermes Desktop (fathah, 3.5k ★, Electron)
    │
    └─ IDE ───────────────→ ACP adapter (built-in, VSCode/Zed/JetBrains)
```

## herm — Third-Party TUI (liftaris/herm)

**Repo:** https://github.com/liftaris/herm
**Stars:** ~124 | **Version:** v1.5.0 (May 2026) | **License:** MIT
**Stack:** TypeScript/TSX, Bun, OpenTUI (React renderer)

A tabbed, mouse-aware TUI. Think "OpenCode-style interface for Hermes." Tabs for chat, sessions, context, agents, analytics, skills, cron, config, env, memory, kanban. Command palette (Ctrl+K), rebindable keys, theme picker, animated ASCII avatar.

**NOTE:** Always discuss herm features in English. The user communicates in English-only and language mixing in responses has been corrected before.

### Terminal Compatibility

herm uses **OpenTUI**, a React renderer for terminal UIs that requires proper raw-mode and mouse-support from the terminal emulator.

| Terminal | Status | Notes |
|---|---|---|
| **iTerm2** | ✅ Works | Recommended on macOS. Supports all TUI frameworks. |
| **Warp** | ✅ Works | Native TUI support. |
| **Kitty** | ✅ Works | Excellent terminal emulator. |
| **Apple Terminal** | ❌ Fails | OpenTUI crashes during terminal capability probing → raw escape codes printed to screen. Do not attempt to debug — switch to iTerm2, Warp, or Kitty. |

**macOS pitfall:** Apple Terminal is the default on macOS and will produce garbage output (escape codes like `10;rgb:ffff/ffff/ffff`) instead of the TUI. This is a terminal limitation, not a herm bug. Install iTerm2 ([iterm2.com](https://iterm2.com/)) and set it as the default terminal.

### Startup Sequence

herm is **not self-contained** — it needs two things running:

```
1. Hermes gateway  ── started via `hermesd` (background daemon)
2. herm TUI        ── connects to the gateway on :8642
```

**Step by step:**

```bash
# 1. Start the gateway (default profile or specify one)
hermesd                              # uses active_profile
hermesd --profile senna              # explicit profile
# Gateway binds to 127.0.0.1:8642

# 2. In a NEW terminal tab/split, launch the TUI
herm                                 # requires gateway on :8642
```

If the gateway isn't running, herm opens but shows "Connecting..." and hangs. Always start `hermesd` first.

### Profile Configuration

herm connects to whatever profile the gateway is serving. Two ways to control this:

**A) `hermes profile use` (canonical — persistent, survives restarts):**
```bash
hermes profile use senna       # writes "senna" to ~/.hermes/active_profile
hermesd                        # now loads Senna automatically
```

All frontends (herm, Hermes Desktop, hermes-swift-mac, CLI) that connect to the gateway on :8642 will use this profile. Marked with ◆ in `hermes profile list`.

**B) Shell function / alias (fallback — overrides active_profile):**
```zsh
hermesd() { command hermesd --profile senna "$@"; }
```

Use this when you need a different profile than the active default, or as a safety net.

**Check which profile is active:**
```bash
hermes profile list            # ◆ marks the active profile
cat ~/.hermes/active_profile   # raw contents, e.g. "senna"
```

### Install

```bash
# Stable
npm install -g herm-tui
bun add -g herm-tui

# Try without installing
bunx herm-tui

# Bleeding edge (every dev push)
bun add -g herm-tui@next

# Or from source
git clone https://github.com/liftaris/herm.git
cd herm && bun install
bun run src/index.tsx
```

### Required Environment

> **Prerequisite:** The Hermes gateway must already be running on port 8642 before herm can connect. Start it with `hermesd` (or `hermesd --profile <name>`) in a separate terminal or as a background service. See [Startup Sequence](#startup-sequence) above.

herm is NOT self-contained — it spawns `python -m tui_gateway.entry` as a subprocess to connect to the Hermes gateway. The `tui_gateway` Python module lives inside the Hermes agent source tree (`~/.hermes/hermes-agent/tui_gateway/`), and it must be runnable via the Hermes venv Python.

**Default behavior:** herm looks for Python in order:
1. `$HERMES_PYTHON` or `$PYTHON` env vars (direct override)
2. `$VIRTUAL_ENV/bin/python` (active venv)
3. `<hermes_root>/.venv/bin/python`
4. `<hermes_root>/venv/bin/python`
5. Fallback to system `python3`

Where `<hermes_root>` is `~/.hermes` (or `$HERMES_HOME`).

**Common failure mode:** If herm picks up system Python (`/usr/bin/python3` or `/Library/Developer/CommandLineTools/usr/bin/python3`), the `tui_gateway` module won't be importable and you get:

```
ModuleNotFoundError: No module named 'tui_gateway'
/usr/bin/python3: Error while finding module specification for 'tui_gateway.entry'
```

The TUI itself launches and draws the tab bar, but hangs at "Connecting..." and the error appears in stderr.

**Fix — set both env vars:**

```bash
# Point to the Hermes venv Python and agent source root
HERMES_PYTHON=~/.hermes/hermes-agent/venv/bin/python \
  HERMES_CWD=~/.hermes/hermes-agent \
  herm
```

- `HERMES_PYTHON` — direct path to the Hermes venv Python (bypasses the auto-detection chain)
- `HERMES_CWD` — working directory set in the spawned gateway process; also used as the first PYTHONPATH entry so `tui_gateway` is importable

Without `HERMES_CWD`, the PYTHONPATH defaults to `<hermes_root>` (often `~/.hermes/`) which does NOT contain `tui_gateway/`. With `HERMES_CWD=~/.hermes/hermes-agent`, the PYTHONPATH includes `~/.hermes/hermes-agent/` where `tui_gateway/` lives.

**Persistent alias (add to .zshrc or equivalent):**

```zsh
alias herm='HERMES_PYTHON=~/.hermes/hermes-agent/venv/bin/python HERMES_CWD=~/.hermes/hermes-agent herm'
```

### Flags

```
herm                    start a fresh session
herm -c, --continue     resume the last real TUI session
herm --resume [id]      resume last (or the given) session
herm --no-splash        skip the launch splash
herm -v, --version      print version
```

### Customization

herm has a rich theme and avatar customization system. Preferences live at `~/.hermes/herm/tui.json`.

#### Themes

**42 built-in themes** — switchable via the theme picker (Ctrl+K → search "theme") or by setting `"theme": "<name>"` in `tui.json`. The default is `"tokyonight"`.

Full list of built-in themes:
`ares`, `aura`, `ayu`, `carbonfox`, `catppuccin`, `catppuccin-frappe`, `catppuccin-macchiato`, `charizard`, `cobalt2`, `cursor`, `daylight`, `default`, `dracula`, `everforest`, `flexoki`, `github`, `gruvbox`, `kanagawa`, `lucent-orng`, `material`, `matrix`, `mercury`, `mono`, `monokai`, `nightowl`, `nord`, `one-dark`, `opencode`, `orng`, `osaka-jade`, `palenight`, `poseidon`, `rosepine`, `sisyphus`, `slate`, `solarized`, `synthwave84`, `tokyonight`, `vercel`, `vesper`, `warm-lightmode`, `zenburn`

#### Custom Themes

Create a JSON file following the OpenCode theme schema (`$schema: https://opencode.ai/theme.json`). Place it at `~/.hermes/herm/themes/<name>.json` and reference it by name in `tui.json`.

Theme JSON structure:
```json
{
  "$schema": "https://opencode.ai/theme.json",
  "defs": {
    "colorName": "#hex"
  },
  "theme": {
    "primary": { "dark": "#hex", "light": "#hex" },
    "secondary": { "dark": "#hex", "light": "#hex" },
    "accent": { "dark": "#hex", "light": "#hex" },
    "background": { "dark": "#hex", "light": "#hex" },
    "backgroundPanel": { "dark": "#hex", "light": "#hex" },
    "backgroundElement": { "dark": "#hex", "light": "#hex" },
    "text": { "dark": "#hex", "light": "#hex" },
    "border": { "dark": "#hex", "light": "#hex" },
    "error": { "dark": "#hex", "light": "#hex" },
    "warning": { "dark": "#hex", "light": "#hex" },
    "success": { "dark": "#hex", "light": "#hex" },
    "info": { "dark": "#hex", "light": "#hex" },
    "textMuted": { "dark": "#hex", "light": "#hex" },
    "borderActive": { "dark": "#hex", "light": "#hex" },
    "borderSubtle": { "dark": "#hex", "light": "#hex" },
    // ... plus markdown*, diff*, and syntax* tokens (see built-in theme files)
  }
}
```

All tokens support dark/light variants. Colors can reference `defs` entries by name. The `hermAvatar` token defaults to `accent` — it controls the ASCII avatar glyph color and sidebar pillar border.

#### Preferences (tui.json)

`~/.hermes/herm/tui.json` controls herm's behavior:

| Key | Type | Default | Purpose |
|---|---|---|---|
| `theme` | string | `"tokyonight"` | Active theme name |
| `mouse` | bool | `true` | Mouse capture in TUI |
| `targetFps` | int | `30` | Target render FPS |
| `animations` | bool | `true` | Animated avatar (false = static) |
| `eikonPath` | string | — | Path to a custom `.eikon` avatar file |
| `lastSessionId` | string | — | Stub for session resume |
| `timeFormat` | `"12h"|"24h"` | — | Clock format |
| `timeStyle` | `"relative"|"absolute"` | — | Timestamp display style |
| `onGoalDone` | string | `"toast"` | Action on kanban goal completion |
| `keys` | object | — | Keybinding overrides |

#### Avatars / Eikon System

herm uses the `.eikon` format — an NDJSON (newline-delimited JSON) file that defines an ASCII animation with multiple states. The default shipped eikon is named **"nous-girl"** (48×24 chars, 64 frames per state).

**3 bundled eikons** live in the herm package at `assets/eikons/`:
- `default.eikon` — "nous-girl" (1.3 MB, the default)
- `ares.eikon` — war/ares-themed (1.2 MB)
- `mono.eikon` — monochrome/minimalist (1.3 MB)

**To use a custom eikon:**
1. Drop `.eikon` files in `~/.hermes/eikons/` — herm's avatar picker scans this directory automatically
2. Or set `"eikonPath": "/path/to/avatar.eikon"` in `tui.json`

**.eikon file format** (NDJSON, one JSON object per line):

```
Line 1:  {"eikon":1,"name":"name","width":48,"height":24,"author":"...","states":["idle","thinking",...]}
State:   {"state":"idle","fps":16,"frame_count":64,"loop_from":0}
Frame 0: {"f":0,"data":"frame text with \n line breaks"}
```

**Required states:** `idle`, `listening`, `thinking`, `speaking`, `working`, `error`

**Key fields:**
- Header: `eikon` (version), `name`, `width`, `height`, `author`, `states`
- State: `state` (name, must match one of the 6), `fps` (frames per second), `loop_from` (0 = loop whole sequence, =frame_count = play once and hold)
- Frame: `f` (frame index), `data` (the ASCII frame as a string with `\n` for line breaks)

The avatar color is determined by the theme's `accent` color (via the `hermAvatar` token), so the same `.eikon` picks up whatever theme you're on.

### Architecture Detail

herm bundles its own gateway client that spawns a Python subprocess:

```typescript
// In gatewayClient.ts (bundled into index.js):
const python = resolvePython(root)
const cwd = process.env.HERMES_CWD || root
env.PYTHONPATH = pyPath ? `${root}${delimiter}${pyPath}` : root
this.proc = spawn(python, ['-m', 'tui_gateway.entry'], { cwd, env, stdio: ['pipe', 'pipe', 'pipe'] })
```

The spawned Python process connects to the Hermes gateway on `127.0.0.1:8642`. The gateway must already be running (started via `hermes gateway start` or implicitly by the CLI). The Python process speaks JSON-RPC over stdio — the Bun TUI frontend parses lines from stdout and dispatches them as events.

## Hermes Desktop (fathah/hermes-desktop)

**Repo:** https://github.com/fathah/hermes-desktop
**Stars:** ~3.5k | **Version:** v0.3.6 (May 2026) | **License:** MIT
**Stack:** Electron, React, TypeScript

A full native desktop app (not a terminal wrapper) for installing, configuring, and using Hermes. Cross-platform: macOS, Linux, Windows.

### Features

- Guided first-run install (detects existing `~/.hermes`)
- Streaming chat UI with SSE parsing, markdown, syntax highlighting
- Session management with SQLite FTS5 full-text search
- Profile switching, memory viewer/editor, persona (SOUL.md) editor
- 22+ slash commands
- 14 toolsets, 16 messaging gateway platforms
- Cron scheduler with 15 delivery targets
- Token usage tracking (live and historical)
- Backup, import, debug dump
- Auto-updater (electron-updater)
- SSH tunnel connection mode (v0.3.6+)

### Install (macOS)

The DMG can sometimes be corrupt on upload (CRC checksum mismatch). The arm64-mac.zip is a reliable fallback:

```bash
# Preferred — arm64 zip (works when DMG fails):
curl -LO https://github.com/fathah/hermes-desktop/releases/download/v0.3.6/Hermes.Agent-0.3.6-arm64-mac.zip
unzip Hermes.Agent-0.3.6-arm64-mac.zip -d /Applications/
xattr -cr "/Applications/Hermes Agent.app"

# DMG (may fail with "image data corrupted"):
# Download from releases → Open → drag to Applications
xattr -cr "/Applications/Hermes Agent.app"
```

**Not notarized** — on first launch, right-click → Open → click Open, or already handled by `xattr -cr` above.

The app is named "Hermes Agent.app" in /Applications (electron-builder convention).

### How It Works

Hermes Desktop bundles its own gateway client and connects to the Hermes API on `http://127.0.0.1:8642` (local) or a remote URL. It does NOT need the `tui_gateway` module — it talks HTTP/SSE directly to the Hermes API server.

First run: choose local or remote mode → detects existing `~/.hermes` (skips install) → provider setup → chat workspace.

### Profile Default — CLI vs App State Gap

Hermes Desktop has a subtle quirk: the app's internal `activeProfile` state in `Layout.tsx` is hardcoded to start as `"default"` on every launch:

```ts
const [activeProfile, setActiveProfile] = useState("default");
```

This is independent of the CLI-level default set by `hermes profile use <name>` (which writes to the `active_profile` file in `$HERMES_HOME` and marks a profile with ◆ in `hermes profile list`). The Desktop app does **not** read `getActiveProfileName()` from `profiles.ts` on startup to seed this state.

**What this means in practice:**

- Even if Senna (or any non-default profile) is the CLI default with its gateway running on port 8642, the Desktop app's UI will show `"default"` as the selected profile in its header/sidebar.
- Chat messages sent through `127.0.0.1:8642` still go through whatever profile's gateway is listening there — so functionally the chat works with the right profile regardless.
- But the profile indicator and profile-aware features (skill listing, memory viewing, model config) will default to `"default"` until the user explicitly selects a different profile.

**The `desktop.json` config** (stored at `~/.hermes/profiles/<name>/desktop.json`) only tracks connection mode — it does not persist a profile preference:
```json
{
  "connectionMode": "local",
  "remoteUrl": "",
  "remoteApiKey": ""
}
```

**To fix locally** — see `references/hermes-desktop-profile-default-patch.md` under the `hermes-companion-apps` skill for two approaches: patching the bundled `app.asar` directly (quick, no rebuild needed) or wiring a proper IPC channel (survives auto-updates).

**Source trace for debugging:**
- `src/renderer/src/screens/Layout/Layout.tsx` — `activeProfile` initial state (line ~20)
- `src/main/profiles.ts` — `getActiveProfileName()` reads `$HERMES_HOME/active_profile`
- `src/main/index.ts` — `set-active-profile` IPC handler calls `hermes profile use <name>`
- `src/preload/index.ts` — `setActiveProfile` exposed to renderer
- `src/renderer/src/screens/Agents/Agents.tsx` — `listProfiles()` returns `isActive` flag per profile

## hermes-swift-mac (hermes-webui/hermes-swift-mac)

**Repo:** https://github.com/hermes-webui/hermes-swift-mac
**Stars:** ~348 | **Version:** v1.7.0 (May 2026) | **License:** MIT
**Stack:** Swift, WKWebView (no Electron)

A thin native macOS wrapper around [hermes-webui](https://github.com/nesquena/hermes-webui) (6.9k ★). Renders the Web UI in a native Mac window instead of a browser tab.

### Architecture

This is NOT a standalone app — it's a shell. It requires the Hermes Web UI server running at `http://localhost:8787` (or a remote server via SSH tunnel). The app is just a WKWebView pointing at that URL, plus tunnel management, keyboard shortcuts, and macOS-native features.

**Dependency chain:** hermes-swift-mac → hermes-webui (Python/JS backend, must be running) → Hermes gateway on port 8642.

### Notable Features

- Signed & notarized (no Gatekeeper issues starting v1.0.4+)
- Native Dock icon, standard macOS menus, global hotkey (⌘⇧H)
- SSH Tunnel mode with lifecycle management
- Auto-update via Sparkle
- Voice input (microphone permission)
- macOS notifications when AI response completes in background

## Comparison

| | **herm** | **Hermes Desktop** | **hermes-swift-mac** |
|---|---|---|---|
| Escape the terminal? | No | Yes | Yes |
| Platform | Terminal | macOS/Linux/Windows | macOS only |
| Stars | ~124 | ~3.5k | ~348 |
| RAM footprint | Tiny | Medium (Electron) | Low (WKWebView) |
| Setup friction | Low (need alias) | Low (DMG/zip) | Medium (needs Web UI backend) |
| Feature depth | Tabbed TUI | Full GUI | Thin wrapper |
| Mac native? | No | No | Yes (notarized) |
| Needs `tui_gateway`? | Yes (spawns subprocess) | No (HTTP API) | No (talks to Web UI) |

## Quick Decision Guide

- **"I want to stay in the terminal but want tabs and a nicer UI"** → `herm`
- **"I want a real desktop app on any OS"** → Hermes Desktop
- **"I want a lightweight Mac-native window for the Web UI I already run"** → hermes-swift-mac
