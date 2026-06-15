---
name: smart-mirror
description: "Build and maintain a Hermes-driven smart mirror / information display — MagicMirror² on Raspberry Pi, custom module for Hermes push integration, scheduled + on-demand content delivery."
version: 1.0.0
author: senna
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Smart-Home, IoT, Display, Raspberry-Pi, Dashboard, MagicMirror]
    homepage: https://github.com/MagicMirrorOrg/MagicMirror
prerequisites:
  commands: [node, git]
---

IDENTITY: Architect.SmartMirrorBuilder. Fork→AuditDeps→SecureInstall→BuildReceiverModule→WireCron→DeployRPi.
Law: PreInstallDependencyAuditIsNonNegotiable.AlwaysVetBeforeInstall.
WHENUSE: User wants smart mirror/MagicMirror²/Hermes display|IoT dashboard|Raspberry Pi information display. ESPECIALLY:ForkAndCustomize|DependencyRiskAssessment|HermesReceiverModule. NoSkip:SupplyChainHardeningLayer0|SecureInstallProcedure|SameLANRequirement.
REDFLAGS: InstallWithoutVetting->RunDependencyAssessment|SkipPinVersions->StripCaretRanges|ProdInstallWithDevDeps->UseOnlyProd.
RATIONALIZATIONS: GitHubStarsEnough->AuditActualDeps|FastSetup->Phase1SoftwareFirst.
QUICKREF: Phase1(Fork+Clone+SecureInstall+ReceiverModule+CronWire)➔Phase2(DataSources{weather,packages,reminders,briefs})➔Phase3(PhysicalBuild{RPi+Display+Frame}).

# Smart Mirror — Hermes-Driven Information Display

A physical smart mirror / dashboard driven by Hermes: MagicMirror² renders the UI on a Raspberry Pi; Hermes pushes data (weather, briefs, reminders, package tracking) over the local network.

## Architecture (Hybrid Approach — Use This)

```
┌─────────────────────┐     HTTP POST (JSON)      ┌──────────────────────┐
│  Hermes (this Mac)  │ ──────────────────────────→│  Raspberry Pi        │
│                     │       local network        │  MagicMirror²        │
│  - cron jobs        │                            │  Hermes Receiver     │
│  - on-demand push   │←─ ACK / status ────────────│  module              │
│  - daily brief gen  │                            │  renders content     │
└─────────────────────┘                            └──────────────────────┘
```

**Why Hybrid over Full Custom or Poll-only:**
- MagicMirror² provides polished UI (Electron, 23.5k☆, modular)
- Hermes is the brain — generates and pushes content, doesn't render
- Custom "Hermes Receiver" module listens on a port, receives JSON, updates DOM
- Lowest effort to working loop, highest flexibility long-term

## Hardware

| Component | Recommendation | Notes |
|---|---|---|
| SBC | Raspberry Pi 4 (2GB+) or Pi 5 | More RAM = smoother Electron |
| Display | HDMI monitor (size of mirror) | 1080p+ recommended |
| Frame | Custom wood/alu frame | Hides RPi, bezel |
| Optional | Two-way mirror glass | True magic mirror look |
| Optional | PIR motion sensor | Wakes/sleeps display |

## Software Stack

- **MagicMirror²** — v2.36.0+, MIT license (full modification allowed)
- **Node.js** — ≥22.21.1 (on RPi)
- **Hermes Receiver module** — custom MagicMirror² module (to be built)
- **Hermes cron jobs** — push schedules on this Mac

## License Note

MagicMirror² is **MIT licensed** — you can freely modify, redistribute, and use it. The only requirement is keeping the original copyright notice. This means you can:
- Modify `config.js` arbitrarily
- Write custom modules
- Fork and maintain your own distribution
- Use commercially

## Build Phases

### Phase 1 — Foundation (Software-first, no hardware yet)
1. Fork MagicMirror² to GitHub (via web UI if gh token lacks fork permission). You can rename the fork — e.g., this user forked as `HermesMirror` rather than keeping the original name. The fork name has no functional impact.
2. Clone fork to this Mac, set up upstream remote:
   ```bash
   git clone https://github.com/<your-username>/<fork-name>.git
   git remote add upstream https://github.com/MagicMirrorOrg/MagicMirror.git
   ```
3. **Secure install procedure** (always use these steps, in order):
   a. **Vet dependencies** — before installing, assess the dependency tree. See `supply-chain-hardening` skill, Layer 0 (Pre-Install Dependency Risk Assessment). For a worked example, see `supply-chain-hardening` → `references/magicmirror-dependency-analysis.md`
   b. **Pin exact versions** — strip `^` from all production dependencies in `package.json` to prevent range resolution from introducing unexpected code
   c. **Remove unnecessary deps** — if features won't be used (e.g., pm2 process manager), uninstall them before install
   d. **Install production-only** — `npm install --only=prod --omit=dev` (excludes devDependencies entirely)
   e. **Audit and fix** — `npm audit`, then `npm audit fix` for safe fixes
   f. **Prune** — `npm prune` to remove orphaned transitive dependencies
4. Run MagicMirror² on this Mac (runs as Electron on macOS, `npm start` for x11)
5. Build Hermes Receiver module (HTTP listener + DOM renderer)
6. Wire one cron job (e.g., daily brief push)
7. Test end-to-end pipeline: Hermes cron → POST → mirror renders

### Phase 1.5 — Dashboard UI Polish
- Glass + Glow theme for hermes-dashboard (glassmorphism, backdrop-filter, status emoji icons 🚫🔄⚡✅, priority dots with glow)
- Empty state design: checkmark icon + "All clear" + "no active tasks" stacked vertically
- Visual mockup workflow: create HTML preview with side-by-side style options (docs/dashboard-styles.html), let user choose before committing
- Common pitfalls:
  - `board-utils.js` extracted pure functions — don't keep local copies in `node_helper.js` or you get `Identifier has already been declared`
  - `.gitignore` line 58 (`/modules/*`) ignores ALL modules — use `git add -f modules/hermes-*`
  - Server-only mode: bridge's `node_helper.js` must self-start polling in `start()` because `DOM_OBJECTS_CREATED` never fires without a browser

### Phase 2 — hermes-chat (✅ COMPLETE — 2026-06-04)
User chose **passive display** model: mirror shows the current Hermes session in real-time as a scrolling transcript. All interaction stays on phone/CLI/TUI — no mic/keyboard input on the mirror.

**Architecture:** `session-api` plugin (port 8644) reads from `lcm.db` (LCM SQLite) and serves conversation messages via HTTP. hermes-chat module has its own `node_helper.js` that polls session-api independently (does NOT extend hermes-bridge). Full design doc at `docs/HERMES-CHAT-DESIGN.md`.

**Display design choices** (user-selected via visual mockup at `docs/hermes-chat-mockup.html`):
- Layout: `bottom_left`
- Content: markdown rendering (bold, `code`, ```blocks```)
- Tool calls: configurable toggle (`showTools: true/false`)
- Long messages: truncated with fade gradient (max-height 120px)
- States: empty (💬 No active session), offline (📡 Gateway unreachable)

**Module files:** `modules/hermes-chat/` — node_helper.js, hermes-chat.js, hermes-chat.css, README.md
**Plugin files:** `~/.hermes/plugins/session-api/` — plugin.yaml, __init__.py
**Tests:** 38 client + 24 node_helper unit tests
**Config:** added to `config/config.js.sample` with all options

**Data flow:**
```
lcm.db → session-api plugin (8644) → hermes-chat node_helper (polls 5s) → Socket.IO → hermes-chat.js (renders)
```

**Key decisions:**
- Separate plugin (not extending kanban-api) — clean separation of concerns
- hermes-chat has its own node_helper — doesn't couple to hermes-bridge
- Filters `role IN ('user', 'assistant')` — tool calls collapsed or hidden
- Liquid Glass styling matching hermes-dashboard
- User wants visual mockup before committing to style choices — see `docs/hermes-chat-mockup.html`

**Session-api plugin design:** See `references/session-api-plugin.md`

### Phase 3 — Physical Build
- Set up RPi with MagicMirror² + Receiver module
- Display framing
- Two-way mirror installation (optional)
- Presence sensor for wake/sleep
- Touch overlay (optional)

## Hermes Push Mechanics

### HTTP (Recommended for Phase 1)
- Receiver module spins up a tiny HTTP server on the RPi
- Hermes POSTs JSON payloads via cron or on-demand
- Payload format: `{ "type": "brief|weather|reminder", "content": "...", "timestamp": "..." }`
- Fire-and-forget with optional ACK

### Upgrade Paths
- **WebSocket** — persistent connection for sub-second push
- **MQTT** — standard IoT pub/sub for multi-device setups

## GitHub Fork Workflow

When the fine-grained PAT can't fork/create repos:
1. Fork via GitHub web UI: navigate to upstream repo → click Fork
2. Clone locally: `git clone https://github.com/<your>/<fork>.git`
3. Set upstream remote: `git remote add upstream https://github.com/<original>/<repo>.git`
4. Sync later: `git fetch upstream && git merge upstream/main`

## Cron Schedule Patterns

| Data | Frequency | Example |
|---|---|---|
| Daily brief | Once (morning) | 07:00 |
| Weather | Every 30-60min | */30 * * * * |
| Package tracking | Every few hours | 0 */4 * * * |
| Reminders | On change or periodic | Cron + manual trigger |
| On-demand | User says "push to mirror" | Immediate |

## Pitfalls

- **Pre-install dependency audit is non-negotiable.** If the user is security-conscious (especially after a previous npm incident), always run the risk assessment before installing. Load `supply-chain-hardening` skill and use its Layer 0 (Pre-Install Risk Assessment) methodology. Categorize deps by function: static assets, parsers, network-facing — and explain the riskiest ones.
- **RPi performance**: MagicMirror² is an Electron app — Pi 3B+ struggles. Use Pi 4 (2GB+) or Pi 5.
- **Network**: RPi and Hermes must be on the same LAN. VPN or reverse proxy needed for remote access.
- **Public exposure**: MagicMirror² disables CORS proxy by default in v2.36.0 — use reverse proxy if exposing publicly.
- **Module dev**: MagicMirror² modules live in `modules/` directory, register via `config.js`. Use `Module.register()` pattern.
- **Display format**: Decide before Phase 3 — two-way mirror vs naked monitor affects framing and lighting significantly. This user's plan: monitor with a decorative frame first, possibly upgrading to two-way mirror glass later. The Receiver module is identical either way — only the physical build changes.
- **Chrome/Electrum quirks**: MagicMirror² runs in kiosk mode; JavaScript console is the primary debugging tool.
- **Duplicate pure function declarations**: When extracting pure logic to `board-utils.js`, remove the local function definitions from `node_helper.js`. Having both `const { diff } = require("./board-utils")` AND `function diff(...)` in the same file throws `Identifier has already been declared`.
- **Module CSS live reloading**: MagicMirror² caches CSS aggressively. Changes to `*.css` require a server restart to appear. For rapid iteration, preview in a standalone HTML mockup first.

## Dashboard UI Styling

### Liquid Glass theme (user's chosen style — iOS 26.5 inspired)
- **Clear frosted glass cards**: `background: rgba(255,255,255,0.03)`, `backdrop-filter: blur(24px)`, `border-radius: 14px`
- **No color tint** — pure transparency only, no pink/purple/colored gradients
- **Diagonal shine overlay**: `::before` pseudo-element with `linear-gradient(135deg, rgba(255,255,255,0.03), transparent)` for subtle depth
- **Inner highlight**: `box-shadow: inset 0 1px 0 rgba(255,255,255,0.06)` for light-catching edge
- **Status icons** (emoji): 🚫 blocked, 🔄 running, ⚡ ready, ✅ done — rendered as `span` in card header with `opacity: 0.65`
- **Priority dots**: 6px colored circles with `box-shadow` glow — red (p1), amber (p2), green (p3)
- **Status left borders**: subtle white variations — `rgba(255,255,255,0.15)` for ready/done, `rgba(255,255,255,0.25)` for running, red glow for blocked
- **Blocked card glow**: `box-shadow: 0 0 24px rgba(255,107,107,0.08)` — visible from across the room
- **Empty state**: frosted glass widget with stacked layout — ✓ checkmark (32px), "All clear" (15px), "no active tasks" (11px muted)

### Research-first design workflow
When a visual design task requires CSS effects or techniques outside agent expertise (e.g. Liquid Glass implementation), create a kanban research task for the `researcher` profile with explicit scopes and deliverable format rather than iterating on guesses. The user prefers this over trial-and-error CSS iteration.

### Visual mockup workflow
When the user wants to see UI options before committing:
1. Create a self-contained HTML file with 3-4 style variants side-by-side
2. Use the same sample tasks across all variants for fair comparison
3. Include empty state comparison at the bottom
4. Tell the user to open locally with `open docs/file.html` or view on the mirror at `localhost:8080/docs/file.html`
5. Once chosen, apply the CSS + JS changes and restart the server

### Headless server notes
- Always use `node serveronly/index.js` — never `npm start` (launches Electron fullscreen)
- Bridge `node_helper.js` must self-start polling in `start()` with default config — `DOM_OBJECTS_CREATED` never fires in headless mode
- Default gateway URL should match the kanban API plugin port (8643)

## MagicMirror² Integration Modules

The Hermes smart mirror uses centralized integration modules that plug into MagicMirror² without core file changes. Everything lives in `modules/`. The key patterns are summarized here; full reference files live under `references/`.

### Architecture: Event Bridge + Display Modules

A **centralized bridge module** (`hermes-bridge`) polls the Hermes gateway (or the kanban API plugin at port 8643), diffs state, and broadcasts `HERMES_KANBAN_*` notifications. **Display modules** consume those notifications and render DOM.

```
Bridge (node_helper.js):
  - Polls GET {gatewayUrl}/api/kanban/board every 30s
  - Diffs current board against lastState (task_id Map)
  - Emits per-change events: HERMES_KANBAN_TASK_CREATED, _DISPATCHED, _COMPLETED, _BLOCKED, _ARCHIVED
  - Emits HERMES_BOARD_STATE snapshots every 5th poll as heartbeat
  - Retries with exponential backoff (1s→2s→4s→...→cap 30s)
  - Self-starts in start() so headless mode works (DOM_OBJECTS_CREATED never fires without browser)

Client (hermes-bridge.js): pure relay, receives socket notifications from node_helper, re-broadcasts to all modules via sendNotification()
```

### Module Inventory

| Module | Purpose | Has node_helper? |
|--------|---------|-----------------|
| **hermes-bridge** | Centralized poller + event relay | Yes |
| **hermes-dashboard** | Kanban task cards grouped by status | No |
| **hermes-status** | Ambient 4px activity bar | No |
| **hermes-chat** | Real-time session transcript display | Yes (polls session-api on port 8644) |

### Config Format

Add to `config/config.js`:
```js
hermes: {
  gatewayUrl: "http://127.0.0.1:8643",  // kanban API plugin port
  enabled: true,
  refreshInterval: 30
}
```

hermes-chat uses a separate gatewayUrl pointing to session-api:
```js
{
  module: "hermes-chat",
  position: "bottom_left",
  config: {
    gatewayUrl: "http://127.0.0.1:8644",  // session API plugin port
    refreshInterval: 5,
    maxMessages: 30,
    showTimestamps: false,
    showTools: true
  }
}
```

Module order matters — bridge must be FIRST in `config.modules[]` so the broadcast channel exists before consumers start.

### Event Payload Shape

All events use this envelope:
```js
{ task_id, title, assignee, status, created_at, started_at?, completed_at?, summary?, block_reason? }
```

### Local Testing (No Pi / No Browser)

Run `node serveronly/index.js` to validate config, module structure, and bridge polling. The bridge self-initializes in headless mode. For log capture when Node.js buffers stdout in the background, use `scripts/run-server.js` (writes to both terminal and `/tmp/hermesmirror-server.log`).

**Syntax checks (no server needed):**
```bash
node -c modules/hermes-bridge/hermes-bridge.js
node -c modules/hermes-bridge/node_helper.js
npm run config:check
```

**Unit tests (Vitest):**
```bash
npm test                           # full suite
npx vitest run tests/unit         # unit tests only
npx vitest run tests/unit/modules/hermes-bridge/   # specific module
```

For MagicMirror module testing patterns (mocking `Module.register`, jsdom environment, method testing), see `references/vitest-module-testing.md`.

**Pure function testability pattern:** Extract pure logic to a separate file with zero MagicMirror dependencies (e.g., `board-utils.js`). This makes functions independently testable without mocking `Module`, `Log`, or `document`. Export via `module.exports = { diffBoardState, statusToEvent, clamp }`. The consuming `node_helper.js` does `const { diffBoardState } = require("./board-utils")`.

### Kanban API Endpoint

The bridge polls the kanban API via a standalone Hermes plugin at port 8643. The plugin is implemented at `~/.hermes/plugins/kanban-api/` and survives Hermes updates because it lives outside the core repo. Its architecture:

```
Hermes Gateway (8642) — health/chat/jobs     ← Hermes CLI/TUI
Kanban API Plugin (8643) — /api/kanban/board ← hermes-bridge poller
Session API Plugin (8644) — /api/session/messages ← hermes-chat poller
```

The plugin uses `aiohttp.web.AppRunner(handle_signals=False)` in a background thread (standard pattern for thread-safe aiohttp — signal handlers don't work in threads).

**Verification:**
```bash
curl http://127.0.0.1:8643/health     # {"status": "ok", "service": "kanban-api"}
curl http://127.0.0.1:8643/api/kanban/board  # {"tasks": [...], "updated_at": ...}
curl http://127.0.0.1:8644/health     # {"status": "ok", "service": "session-api"}
curl http://127.0.0.1:8644/api/session/messages?limit=5  # {"session_id": "...", "messages": [...]}
```

### Git Tracking Caveat

MagicMirror's `.gitignore` line 58 (`/modules/*`) ignores ALL modules. Force-add Hermes modules:
```bash
git add -f modules/hermes-bridge modules/hermes-dashboard modules/hermes-status
git ls-files modules/  # verify tracked
```

### Pre-Push Checklist

1. `git add -f modules/hermes-*`
2. `git ls-files modules/` — verify tracked
3. `npm run config:check` — clean
4. `npm run lint:js` — no new errors
5. `npm run lint:css` — passes
6. `git push --dry-run`
7. `git push origin <branch>`

### Integration Module Pitfalls

- **Bridge loads BEFORE display modules in config.modules[]** — broadcast channel must exist first
- **Don't poll too fast** — 30s default, under 10s hammers gateway
- **Don't emit full snapshots every poll** — per-change events + heartbeat every 5th poll
- **Shallow-copy archived task payloads** — `{ ...prevTask, status: 'archived' }`, never mutate references from previous-state Map
- **Exponential backoff: separate retryDelay from poll interval** — start 1s, double, cap 30s
- **Keep fork baseline on separate branch** — don't mix upstream translation/lint updates with feature commits
- **`||` vs `??` in sort comparators** — when sorting with a lookup table where `0` is a valid key (e.g., `statusOrder = { blocked: 0, running: 1 }`), `|| fallback` treats `0` as falsy and skips it. Use `?? fallback` instead. Example bug: `blocked` tasks sorted last because `0 || 4 = 4`.
- **Markdown rendering on mirror** — use regex-based approach (escape HTML first, then apply bold/code/block patterns). No external markdown libraries needed for simple chat display. Always escape HTML before applying markdown transforms to prevent XSS.
- **BEM selectors fail stylelint kebab-case rule** — add `selector-class-pattern` override to stylelint config
- **CSS changes need server restart** — MagicMirror caches CSS aggressively
- **ESLint `globalIgnores` blocks custom modules** — the flat config at `eslint.config.mjs` has `globalIgnores(["modules/**/*"])` which excludes ALL modules from linting. Change to `modules/default/**` to lint only the upstream default modules while enabling linting for custom hermes-* modules. The `ignores: []` override approach does NOT work — `globalIgnores` cannot be overridden by later config entries.
- **Unused callback params in `Module.register()`** — MagicMirror callbacks like `notificationReceived(notification, payload, sender)` have required signatures by convention but JS doesn't enforce arity. If you don't use `payload`/`sender`, just remove them from the function definition rather than prefixing with `_`. The `_` prefix requires `argsIgnorePattern: "^_"` in ESLint config which isn't set by default. Example: `notificationReceived (notification) {` works fine.
- **Testing node_helper.js requires mocking NodeHelper and Log** — `node_helper.js` calls `NodeHelper.create()` and `require("logger")` at module load time. Mock both before requiring the module: `vi.mock("node_helper", () => ({ create: vi.fn((obj) => Object.assign({ name: "test" }, obj)) }))` and `vi.mock("logger", () => ({ log: vi.fn(), warn: vi.fn(), error: vi.fn() }))`. Then `require("./node_helper")` returns the testable object. Use `vi.useFakeTimers()` for backoff/timer testing.

### Integration Module Reference Files

- `references/hermes-architecture.md` — gateway route architecture, plugin system gap, kanban data shape, health checks
- `references/kanban-api-plugin.md` — kanban API plugin implementation (aiohttp thread-safe startup, plugin.yaml, CORS)
- `references/session-api-plugin.md` — session API plugin: reads LCM SQLite, serves conversation messages on port 8644
- `references/standalone-api-plugin-pattern.md` — general pattern for building HTTP API plugins (skeleton, port allocation, pitfalls)
- `references/session-api-plugin.md` — session-api plugin for hermes-chat (LCM database schema, session data endpoints)
- `references/integration-test-protocol.md` — step-by-step integration test procedure for the HermesMirror fork
- `references/push-checklist.md` — condensed pre-push checklist

## Related Skills
- `openhue` — Philips Hue control for smart home lighting (complementary)
- `macos-computer-use` — useful if automating macOS-side setup tasks
- `supply-chain-hardening` — pre-install dependency risk assessment (run before any npm install on the mirror project)
- `github-repo-management` — forking, cloning, upstream remote setup
