---
name: hermes-companion-apps
description: Install, configure, and troubleshoot third-party companion apps for Hermes Agent — TUIs, desktop GUIs, and web wrappers.
trigger: User asks to try, install, set up, or review a non-CLI Hermes interface (herm TUI, Hermes Desktop, Hermes Swift Mac, hermes-webui, etc.)
domain: hermes
version: 1.2.0
---

# Hermes Companion Apps

Class-level guide for installing, configuring, and troubleshooting third-party Hermes companion applications. These are separate projects that interface with the same `~/.hermes` gateway.

## Common Prerequisites

- Hermes Agent must already be installed and working (`hermes status` returns OK)
- `~/.hermes` must exist with a working config and credentials
- The companion app talks to the same HTTP gateway (default: `127.0.0.1:8642`)

## herm TUI (`liftaris/herm`)

A tabbed, mouse-aware TUI built with OpenTUI (React renderer) and Bun.

**Install:**
```bash
npm i -g herm-tui           # stable
bun add -g herm-tui         # alternative
bunx herm-tui               # try without installing
```

**Uninstall:**
```bash
npm uninstall -g herm-tui
```

**Known issue: ModuleNotFoundError — `tui_gateway`**

herm spawns `python -m tui_gateway.entry` as a subprocess but defaults to system Python which can't find the module. The venv lives at `~/.hermes/hermes-agent/venv/bin/python`, not `~/.hermes/venv/bin/python`.

**Fix — alias or wrapper:**
```bash
# Permanent alias (add to ~/.zshrc)
alias herm='HERMES_PYTHON=~/.hermes/hermes-agent/venv/bin/python HERMES_CWD=~/.hermes/hermes-agent herm'

# One-time run
HERMES_PYTHON=~/.hermes/hermes-agent/venv/bin/python HERMES_CWD=~/.hermes/hermes-agent herm
```

**TUI profile resolution — critical gap:**

The `herm` TUI gateway (`tui_gateway.entry`) does NOT use the CLI profile system (`active_profile`, `--profile`, `hermes profile use`). It calls `get_hermes_home()` directly, which defaults to `~/.hermes` — the **default** profile. This means `herm` always loads the default profile's `config.yaml`, skills, memories, and SOUL.md, even when a named profile (e.g. `senna`) is set as active for the CLI.

**Architecture difference:**
| Path | Profile Mechanism | Relevant Code |
|------|-------------------|---------------|
| `hermes chat --profile senna` (CLI) | `_apply_profile_override()` in `hermes_cli/main.py` reads `active_profile` or `-p` flag, sets `HERMES_HOME` | Full profile system |
| `herm` (TUI via `tui_gateway.entry`) | `get_hermes_home()` reads `$HERMES_HOME` env var or falls back to `~/.hermes` | No profile awareness |

**Fix — add `HERMES_HOME` to make `herm` use a named profile:**

```bash
alias herm='HERMES_HOME=~/.hermes/profiles/senna HERMES_PYTHON=~/.hermes/hermes-agent/venv/bin/python HERMES_CWD=~/.hermes/hermes-agent herm'
```

When `HERMES_HOME` is set to a profile directory, the TUI gateway reads that profile's `config.yaml`, `SOUL.md`, skills, memories, and session state. Without it, the TUI runs against the default profile regardless of CLI profile settings.

**Pitfall — sandbox `~/.zshrc` trap:** When adding this alias from within a Hermes profile session (e.g. running as Senna), `$HOME` resolves to the profile's sandbox home (`~/.hermes/profiles/<name>/home/`), NOT the real home. Always edit `/Users/<you>/.zshrc` with absolute paths. See `references/profile-sandbox-dotfile-trap.md`.

**Check the `hermes-agent` skill's `references/hermesd-profile-resolution.md`** for the analogous issue with `hermesd`. The `hermesd` dashboard has the same profile-resolution gap and the same fix (`--hermes-home ~/.hermes --profile senna`).

**⚠️ The `~/.zshrc` sandbox trap:** When running terminal commands inside a profile session (e.g. Senna), `$HOME` resolves to the profile's sandbox home (`~/.hermes/profiles/<name>/home/`), NOT the real home. Any `cat >> ~/.zshrc` or `~/.zshrc` edit writes to the wrong file — iTerm2 never reads it. Always use absolute paths like `~/.zshrc` for user-facing shell config. See `references/profile-sandbox-dotfile-trap.md`.\n```\n\n### Customization: Themes, Avatar, and Preferences\n\nherm has a full theme engine (shared with OpenCode) and an ASCII avatar/animation system. All customization is driven by `~/.hermes/herm/tui.json` (reads from `$HERMES_HOME/herm/`).\n\n**Built-in themes (42 shipped):**\n\n`ares`, `aura`, `ayu`, `carbonfox`, `catppuccin`, `catppuccin-frappe`, `catppuccin-macchiato`, `charizard`, `cobalt2`, `cursor`, `daylight`, `default`, `dracula`, `everforest`, `flexoki`, `github`, `gruvbox`, `kanagawa`, `lucent-orng`, `material`, `matrix`, `mercury`, `mono`, `monokai`, `nightowl`, `nord`, `one-dark`, `opencode`, `orng`, `osaka-jade`, `palenight`, `poseidon`, `rosepine`, `sisyphus`, `slate`, `solarized`, `synthwave84`, `tokyonight`, `vercel`, `vesper`, `warm-lightmode`, `zenburn`\n\nDefault is `tokyonight`. Switch via:\n1. **Theme picker** — accessible from the command palette (Ctrl+K, search \"theme\")\n2. **tui.json** — set `\"theme\": \"catppuccin\"` (or any name from the list)\n\n**Custom themes** follow the OpenCode JSON schema (`$schema: https://opencode.ai/theme.json`). Structure:\n- `defs` — reusable color references (e.g. `\"myBg\": \"#0A0A1A\"`)\n- `theme` — 40+ visual tokens, each with `dark` and `light` variants\n\nKey tokens: `primary`, `secondary`, `accent`, `background`, `backgroundPanel`, `backgroundElement`, `border`, `borderActive`, `borderSubtle`, `text`, `textMuted`, full markdown/syntax/diff color sets, and `hermAvatar` (glyph color, defaults to `accent`).\n\nCustom theme files live at `~/.hermes/herm/themes/<name>.json`.\n\n**Avatar animation:**\n\nState-driven ASCII animation in the sidebar. States: `idle`, `listening`, `thinking`, `speaking`, `working`, `error`. Controllable via tui.json:\n\n| Key | Type | Effect |\n|-----|------|--------|\n| `\"animations\"` | `boolean` | `false` → static frame, saves a bit of CPU |\n| `\"eikonPath\"` | `string` | Path to a custom `.eikon` file (NDJSON ASCII animation format) |\n\nThe `.eikon` format is an NDJSON spec (see `github.com/liftaris/eikon`): header line + state declarations + frame data. herm ships bundled eikons in `assets/eikons/` (one per skin name), and scans `$HERMES_HOME/eikons/` for user-dropped files.\n\n**All tui.json preferences:**\n\n| Key | Type | Default | Purpose |\n|-----|------|---------|---------|\n| `theme` | `string` | `\"tokyonight\"` | Theme name matching a built-in or custom theme |\n| `mouse` | `boolean` | `true` | Mouse capture enabled |\n| `targetFps` | `number` | `30` | Target render FPS |\n| `animations` | `boolean` | `true` | Avatar/spinner frame animations |\n| `eikonPath` | `string` | `null` | Path to custom `.eikon` avatar file |\n| `lastSessionId` | `string` | `null` | Resume previous session on startup |\n| `toolDetails` | `string` | `\"expanded\"` | Thought-cloud tool trail: `\"hidden\"`, `\"collapsed\"`, or `\"expanded\"` |\n| `keys` | `object` | `{}` | Keybinding overrides (ActionId → chord string) |\n| `timeFormat` | `string` | `\"12h\"` | Clock style: `\"12h\"` or `\"24h\"` |\n| `timeStyle` | `string` | `\"relative\"` | List timestamps: `\"relative\"` or `\"absolute\"` |\n| `onGoalDone` | `string` | `\"toast\"` | Session-done action: `\"toast\"`, `\"suspend\"`, or custom shell command |\n\nCustom theme JSON anatomy, tui.json schema, and .eikon spec details: see `references/herm-customization.md`.\n\n**Known issue: Apple Terminal escape code dumping**  

Apple Terminal (the default macOS Terminal.app — not an Apple Silicon issue) cannot run OpenTUI-based TUI apps. Running herm produces raw escape sequences like:
```
10;rgb:ffff/ffff/ffff
11;rgb:1e1e/1e1e/1e1e
;1R;1R;1R;343;570t4;0;rgb:0000/0000/0000
```

These are terminal query responses that the TUI didn't consume before crashing. Apple Terminal is **reliably incompatible** with OpenTUI TUIs — the TUI works fine from PTY sessions (e.g. tool-executed commands) but always dumps escape codes in real Apple Terminal windows.

**Workarounds (first one is most reliable):**
1. Switch to iTerm2, Warp, Kitty, or Alacritty — herm runs fine on those
2. `reset` in the terminal, then retry with `--no-splash` (occasionally helps)
3. Use the built-in Hermes TUI instead (`hermes --tui`)
4. Use Hermes Desktop instead (GUI, no terminal dependency)

## Hermes Desktop (`fathah/hermes-desktop`)

A full Electron desktop GUI for installing, configuring, and chatting with Hermes. Cross-platform (macOS, Linux, Windows).

**Install (macOS):**
```bash
# Download latest from releases
curl -L -o /tmp/hermes-desktop-arm64.zip \
  "https://github.com/fathah/hermes-desktop/releases/download/v0.3.6/Hermes.Agent-0.3.6-arm64-mac.zip"
unzip -qo /tmp/hermes-desktop-arm64.zip -d /tmp/hermes-desktop-extracted
cp -R "/tmp/hermes-desktop-extracted/Hermes Agent.app" /Applications/
xattr -cr "/Applications/Hermes Agent.app"
```

**Pitfalls:**
- **DMG is reliably corrupt** — the `.dmg` download via curl always fails checksum. Always use the `*-arm64-mac.zip` (or `*-mac.zip` for Intel) variant instead.
- **Architecture mismatch → 'incorrect executable format'** — The release page ships both `Hermes.Agent-*-arm64-mac.zip` (Apple Silicon) and `Hermes.Agent-*-mac.zip` (Intel x86_64). Using arm64 on Intel gives `The application cannot be opened because it has an incorrect executable format`. Always verify with `file "/Applications/Hermes Agent.app/Contents/MacOS/Hermes Agent"` — should show `arm64` or `x86_64`.
- **Not notarized** — ad-hoc signed. On macOS 15, even after `xattr -cr`, you'll get "unsupported by Apple" on first launch. Right-click → Open bypasses this. If that doesn't work: System Settings → Privacy & Security → scroll to "App was blocked" → click Open Anyway.
- **It's named 'Hermes Agent.app'** in Applications, not 'Hermes Desktop.app'.
- Since Hermes is already installed, it auto-detects `~/.hermes` and skips the install wizard.

**First launch:**
- Right-click → Open (or `xattr -cr` already done)
- Walks through: local/remote mode → provider selection → chat workspace
- Uses SSE streaming on `127.0.0.1:8642` (same gateway as CLI)

## Hermes Swift Mac (`hermes-webui/hermes-swift-mac`)

A native macOS wrapper (Swift + WKWebView, no Electron) for Hermes Web UI.

**Requires:** Hermes Web UI running as a backend (`localhost:8787`). The wrapper is just a window — the real app is the web server.

**Key points:**
- Signed and notarized (no Gatekeeper issues from v1.0.4+)
- Supports SSH tunnel mode for remote servers
- Global hotkey (⌘⇧H) to bring Hermes forward
- Voice input, macOS notifications, Sparkle auto-update

## Hermes Web UI (`nesquena/hermes-webui`)

The browser-based interface that the Swift Mac wrapper wraps. 6.9k stars, very mature (1,900+ commits).

**Quick start:**
```bash
git clone https://github.com/nesquena/hermes-webui.git ~/hermes-webui
cd ~/hermes-webui && python3 bootstrap.py
# Opens at http://localhost:8787
```

Also available via Docker:
```bash
git clone https://github.com/nesquena/hermes-webui
cd hermes-webui
cp .env.docker.example .env
docker compose up -d
# Open http://localhost:8787
```

## Claw3D (`iamlukethedev/Claw3D`)

A 3D virtual office for AI agents — agents appear as characters at desks in a 3D rendered office (Three.js / React Three Fiber). Supports Hermes through a bundled WebSocket adapter.

**Stars:** 1.6k | **Latest:** v0.1.4 | **License:** MIT | **Setup complexity:** Medium

### Install paths

**Path A — Manual from GitHub:**
```bash
git clone https://github.com/iamlukethedev/Claw3D.git && cd Claw3D
npm install
cp .env.example .env
```

**Path B — Auto-install via Hermes Desktop (recommended for existing Hermes Desktop users):**
Hermes Desktop has a built-in "Hermes Office (Claw3d)" feature. When enabled, it:
- Clones the repo to `~/.hermes/hermes-office/`
- Auto-configures `.env` with the correct `HERMES_API_URL` and `HERMES_ADAPTER_PORT`
- Connects settings stored at `~/.openclaw/claw3d/settings.json`
- Conversation history at `~/.hermes/clawd3d-history.json`

No manual `.env` editing needed — Hermes Desktop handles it.

### Starting Claw3D

**One-command start (after install):**
```bash
bash ~/.hermes/hermes-office/scripts/clawd3d-start.sh
```
This starts both the adapter and dev server with auto port-detection.

**Or two terminals (more control):**
```bash
# Terminal 1 — Hermes WebSocket adapter (translates Claw3D protocol ↔ Hermes HTTP)
npm run hermes-adapter   # starts on ws://localhost:18789

# Terminal 2 — Claw3D studio
npm run dev              # starts on http://localhost:3000
```

Then in the Claw3D UI, choose "Hermes backend" and connect to `ws://localhost:18789`.

### Architecture
```
Browser (3D office) → Claw3D Studio → Hermes WebSocket adapter → Hermes HTTP API
```

Env vars the adapter reads:
| Var | Default | Purpose |
|-----|---------|---------|
| `HERMES_API_URL` | `http://localhost:8642` | Hermes HTTP API base |
| `HERMES_ADAPTER_PORT` | `18789` | WebSocket port for adapter |
| `HERMES_MODEL` | `hermes` | Model display name (cosmetic in UI) |
| `HERMES_AGENT_NAME` | `Hermes` | Display name in Claw3D UI |

### Agents and models — auto-populate

**Agents** — Claw3D discovers agents from Hermes through the adapter. Your Hermes profiles (senna, researcher, etc.) appear as agents in the office. No manual setup needed. You can also spawn additional sub-agents from within Claw3D using the built-in orchestration tools (`spawn_agent`, `delegate_task`, `list_team`, `configure_agent`, `dismiss_agent`, `read_agent_context`).

**Models page** — auto-populates from your Hermes configuration. Whatever provider and model you've configured (e.g. DeepSeek + deepseek-v4-flash) appears automatically. No manual entry required.

### Hermes CLI integration

Hermes has a built-in `claw` CLI command for OpenClaw migration (not needed for standard Hermes use):
```bash
hermes claw migrate              # Preview then migrate from OpenClaw
hermes claw migrate --dry-run    # Preview only
hermes claw cleanup              # Archive leftover OpenClaw directories
```

### Key features
Agent fleet management, 3D office with rooms/navigation, standups, kanban board, multi-floor offices, GitHub review flows, demo mode (no backend required).

### Limitations
Requires two running processes (adapter + studio). Hermes adapter is not yet a native Studio provider — translates Hermes HTTP calls into Claw3D's gateway protocol.

### Profile Default Patching

Hermes Desktop hardcodes `activeProfile` state as `"default"` on launch, even when the CLI default is a different profile. See `references/hermes-desktop-profile-default-patch.md` for two approaches:

- **Approach A (quick, no rebuild):** Patch the bundled `app.asar` directly — change `useState("default")` to `useState("<profile-name>")` in the minified renderer bundle.
- **Approach B (proper, survives updates):** Wire a `get-active-profile` IPC channel from the main process's existing `getActiveProfileName()` through to the renderer.

Approach A loses the patch on auto-update. Approach B is the right long-term fix but requires rebuilding the app.

## hermesd — Terminal Dashboard (`mudrii/hermesd`)

A read-only, live-updating TUI monitoring dashboard for Hermes Agent. Installed via pip/uv — shows 10 panels covering gateway status, sessions, tokens/cost, tools, config, cron, skills, logs, profiles, and memory.

**Repo:** https://github.com/mudrii/hermesd
**Stars:** 45 | **Version:** v2026.5.12 | **License:** MIT
**Stack:** Python, Rich

Unlike the other companion apps in this section, hermesd is not a chat interface — it's an **operator dashboard** for monitoring your Hermes installation. Think `htop` for Hermes.

**Install:**

```bash
# Using uv (preferred)
uv tool install hermesd

# Using pip
pip install hermesd
```

**Usage:**

```bash
hermesd                          # Live TUI (full-screen, auto-refresh)
hermesd --snapshot               # One-shot report (useful for cron/CI)
hermesd --snapshot-panel 3       # Single panel (e.g., tokens/cost)
hermesd --snapshot-file /tmp/report.txt  # Save snapshot to file
hermesd --snapshot-format json   # JSON output for programmatic use
hermesd --refresh-rate 2         # Poll every 2 seconds (default: 5)
hermesd --profile researcher     # Monitor a specific profile
hermesd --log-tail-bytes 10000   # Cap log reads per refresh
```

**10 Dashboard Panels:**

| # | Panel | What It Shows |
|---|-------|---------------|
| 1 | Gateway & Platforms | PID, version, per-platform connection dots |
| 2 | Sessions | Active/total, message/tool call totals, recent list */
| 3 | Tokens / Cost | Today's & all-time tokens, ~USD cost, model/provider breakdown |
| 4 | Tools | Available tools count, per-session call stats, tool name grid |
| 5 | Config | Model, provider, max turns, reasoning, compression, memory |
| 6 | Cron | Job table with schedule, delivery, error count, latest output |
| 7 | Skills / Integrations | Providers, credential pools, hooks, plugins, MCP, skills |
| 8 | Logs | Tailed agent/gateway/errors/cron logs with tab switching + filter |
| 9 | Profiles | Read-only profile discovery: sessions, log freshness, skills count, SOUL excerpts |
| 10 | Memory | Memory provider, file word counts, SOUL.md size |

**Known issues:**\n- **`--profile` flag defaults to "root"** — Without `--profile`, hermesd shows root-level data (labeled "root" in Panel 9). Use `--profile senna` (or the desired profile name) to see that profile's data.\n- **`--profile <name>` can fail in sandbox** — When the terminal's `$HOME` is inside a profile sandbox (`~/.hermes/profiles/<name>/home/`), `hermesd --profile <name>` tries to find `profiles/<name>` under the sandbox path and fails. Fix: `hermesd --hermes-home ~/.hermes --profile <name>`. See the `hermes-agent` skill's `references/hermesd-profile-resolution.md` for full details.\n- Zero config (reads `~/.hermes/` directly), but the session cost panel may skip cron/batch sessions if they have low or zero token counts\n- Refresh rate below 2 seconds is not recommended — collector overhead increases

**Comparison Matrix**

| Tool | Type | Best For |
|------|------|----------|
| Hermes Workspace | Web UI (full) | Power users wanting visual orchestration + multi-agent dashboard |
| Hermes Web UI | Web UI (chat) | Simple browser-based chat |
| Hermes Desktop | Electron GUI | Cross-platform desktop app |
| herm TUI | Terminal TUI | Rich terminal experience |
| hermesd | Terminal dashboard | Read-only monitoring |

## Hermes Workspace (`outsourc-e/hermes-workspace`)

The web UI for Hermes Agent — visual orchestration, multi-agent dashboard, skills management, and chat workspace. 4.8k stars, Node.js + pnpm.

**Repo:** https://github.com/outsourc-e/hermes-workspace

**Quick start (dev):**
```bash
cd ~ && git clone https://github.com/outsourc-e/hermes-workspace.git
cd hermes-workspace && pnpm install
# Create .env with HERMES_API_URL=http://127.0.0.1:8642
pnpm dev   # → http://127.0.0.1:3000
```

**Quick start (production):**
```bash
cd /absolute/path/to/hermes-workspace
pnpm build
NODE_OPTIONS="--max-old-space-size=2048" node server-entry.js
```

**Build output directory:** When the workspace was cloned inside a profile sandbox (`~/.hermes/profiles/<name>/home/`), `pnpm build` outputs there — NOT to `~/hermes-workspace/dist/`. Find the actual output with `find ~ -name "server.js" -path "*/hermes-workspace/dist/server/*"`. Source edits must be made in the copy the build actually reads.

**Dev vs production — key differences:**
- Vite SSR (`pnpm dev`) caches server-side `.ts` in Node.js memory — `touch`/file-watchers do NOT recompile. Kill + restart to reload.
- Production build tree-shakes `gateway-capabilities.ts` — capability overrides must go in `connection-status.ts` route handler instead.
- Cache to clear: `rm -rf .tanstack node_modules/.vite`

**Three services must run:**
1. **Gateway** — `hermes gateway start` on port 864x
2. **Dashboard** — `hermes dashboard --port 9119 --no-open --skip-build`
3. **Workspace** — `pnpm dev` on port 3000

**Key pitfalls:**
- API server must be enabled (`platforms.api_server.enabled: true` in config.yaml) — `/health` returns ok even when disabled
- Each profile needs a unique gateway port if running multiple profiles
- Port 3000 conflicts with Vite dev servers — check `lsof -i :3000`
- Workspace reads `.env` at startup only — restart after changes
- Dashboard is a separate process from the gateway — must start independently

For detailed .env configuration, multi-profile port setup, startup script, and full troubleshooting table, see `references/hermes-workspace-setup.md`. For customizing how your profiles appear in the Operations tab (emoji, color, descriptions), see `references/operations-tab-profile-customization.md`. For probing workspace feature readiness before launch (dashboard API endpoints, swarm verification, auth token, production build tree-shaking pitfall), see `references/workspace-feature-probe.md`. For the dashboard auth middleware, `/api/` route registration patterns, conductor native-swarm mode, the `_PUBLIC_API_PATHS` frozenset trap, Vite SSR module cache behavior, and enabling conductor in production builds via `connection-status.ts`, see `references/workspace-api-routes-and-auth.md`. For per-profile API server port allocation (avoiding port conflicts when multiple profiles run gateway + API server simultaneously), see `references/hermes-workspace-setup.md` (Multi-Profile Port Conflicts section).

## Trifecta (`pkyanam/trifecta`)

Cross-platform coding agent platform: a desktop server that runs AI coding agents, plus native mobile clients (iOS/Android), VS Code/Cursor extension, and web UI. Connects to Hermes via **ACP over stdio**.

**Repo:** https://github.com/pkyanam/trifecta  
**Stars:** 15 | **Version:** v0.0.37-alpha.1 | **License:** Apache-2.0  
**Stack:** Node.js, Effect-TS, Electron 41, React 19, Bun, Turborepo  
**By:** Belweave (based on T3 Code)

### What it gives you

A mobile app to chat with Hermes, review code changes, and manage dev workflow from your phone. Also works as a desktop GUI (Electron) or VS Code extension. Same server backs all clients.

### Architecture

```
Clients (iOS / Android / VS Code / Cursor / Web UI / Electron)
    │ WebSocket + Effect-style RPC
    ▼
Trifecta Server (Node.js, Effect-TS)
    │ ACP over stdio (JSON-RPC)
    ▼
hermes acp  ← uses your existing Hermes install
```

### Prerequisites

- Hermes Agent installed and working
- `hermes acp --check` returns OK
- Node.js ≥ 22.16 (for the Trifecta server)

### Quick start (no install)

```bash
npx @belweave/trifecta
```

Starts the server, prints a pairing URL + QR code. Install the iOS/Android app or use the web UI, scan QR to pair, select Hermes as agent.

### Desktop app install

```bash
# macOS (Homebrew)
brew install --cask belweave-code

# Or from GitHub Releases
# https://github.com/pkyanam/trifecta/releases
```

### Headless server (remote/VPS)

```bash
npx @belweave/trifecta serve --host "0.0.0.0"
# With Tailscale:
npx @belweave/trifecta serve --host "$(tailscale ip -4)"
```

### Self-hosted Docker

```bash
docker build --platform=linux/amd64 -t trifecta-server ./trifecta-desktop
docker run -d --name trifecta --restart unless-stopped -p 3773:3773 \
  -v /opt/trifecta/data:/data \
  -e TRIFECTA_HOST=0.0.0.0 -e TRIFECTA_PORT=3773 -e TRIFECTA_HOME=/data \
  trifecta-server
```

### Connecting mobile app

1. Open Trifecta on iOS/Android
2. Add server: `http://<ip>:3773`
3. Open pairing URL from server logs in mobile browser
4. App pairs and shows connected providers
5. Select Hermes as agent

### Adding projects (CLI required)

```bash
trifecta project add /path/to/repo --title "My Project"
```

GUIs don't support adding projects on remote environments — use CLI.

### Supported agents (for reference)

Codex, Claude Code, OpenCode, Gemini, Antigravity, Cursor, Hermes, Devin, and any ACP-compatible agent.

### Pitfalls

- **Early alpha** — expect rough edges, breaking changes between versions
- **Pairing tokens are one-time** — save the URL, it can't be recovered. Use `trifecta auth` to issue new ones
- **Tailscale recommended for remote access** — exposes port 3773 which has no built-in auth beyond pairing tokens
- **Hermes ACP mode** — Trifecta spawns `hermes acp` as a subprocess. It uses the default profile unless you configure `HERMES_HOME` in the Trifecta server's environment. For named profiles, set `HERMES_HOME=~/.hermes/profiles/<name>` before starting the server

### When to use Trifecta vs other companion apps

- **Want mobile access to Hermes?** → Trifecta (only option with native iOS/Android)
- **Want VS Code integration?** → Trifecta or hermes-lsp
- **Want full orchestration dashboard?** → Hermes Workspace (more mature)
- **Want simple desktop chat?** → Hermes Desktop (simpler, more stable)

For detailed deploy guides, see `references/trifecta-deploy-guide.md`.

## Comparison Matrix (Full)

| Tool | Escape Terminal? | Platform | RAM | Setup Friction | Stars |
|------|-----------------|----------|-----|----------------|-------|
| Hermes Workspace | Yes (web) | Any with browser | Low (Node) | Low (pnpm install) | 4.8k |
| herm TUI | No | Terminal | Tiny | Low (needs env fix) | 124 |
| Hermes Desktop | Yes | macOS/Linux/Windows | Medium (Electron) | Low | 3.5k |
| Swift Mac | Yes | macOS only | Low (WKWebView) | Medium (needs Web UI) | 348 |
| Hermes Web UI | Yes | Any with browser | Low | Low | 6.9k |
| Claw3D | Yes (3D office) | Any with browser | Medium (Three.js) | Medium (needs adapter) | 1.6k |
| Trifecta | Yes (mobile+web) | iOS/Android/Desktop/VS Code | Low (Node.js) | Low (npx) | 15 |

## Requirement Logic

- **Want mobile access to Hermes?** → Trifecta (native iOS/Android via ACP)
- **Want a real GUI?** → Hermes Desktop (most complete, cross-platform)
- **Want full orchestration + multi-agent dashboard?** → Hermes Workspace (web, most feature-rich)
- **Want Mac-native lightweight?** → Swift Mac + Web UI
- **Want to stay in terminal but richer TUI?** → herm (after env fix)
- **Want browser-based access?** → Hermes Web UI (most mature)
- **Want a 3D agent experience?** → Claw3D (novelty + multi-agent visualization)

## Troubleshooting Methodology

When a fix or configuration attempt doesn't work, follow this sequence before proposing another fix:

1. **Verify each assumption** — Confirm each step of the setup independently. E.g., if `hermesd --profile senna` shows "root", check: is the flag being passed? Is `--profile` even what you think it is? Read the tool's `--help`.
2. **Check the data path** — Trace how data flows: where does the tool look for config? What does `$HOME` resolve to in the current context? What does `~` expand to?
3. **Check the file you actually modified** — When editing config files from within a profile sandbox, `~/.zshrc` is the wrong file. Verify with `cat /Users/<you>/.zshrc`, not `cat ~/.zshrc`.
4. **One variable at a time** — Change one thing, test, confirm, then change the next. Avoid stacking changes.
5. **When stuck, present findings first** — List what was tried, what happened (actual output), and a reasoned next step. Don't propose another blind fix.