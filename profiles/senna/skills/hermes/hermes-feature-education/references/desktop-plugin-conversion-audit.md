# Desktop Plugin Conversion Audit

Method for auditing installed agent plugins for Hermes Desktop conversion, plus
the state of the user's fleet at audit time (2026-08-03).

## The two data doors for a desktop plugin

- **`ctx.rest`** → hits `/api/plugins/<id>` — requires the plugin to ship a
  `dashboard/plugin_api.py` backend (FastAPI `APIRouter`) mounted under
  `~/.hermes/plugins/<id>/dashboard/`. None of the user's plugins had one at
  audit time; adding it IS the conversion step for tool-bearing plugins.
- **`host.request` / `host.onEvent` / `host.state`** → gateway JSON-RPC
  directly, no backend needed. Read-only visualizations (sessions, config,
  cron, kanban data) need only the SDK. Prefer this when the data is already
  reachable from the app.

## Key finding: the desktop app ships a bundled Kanban plugin

`apps/desktop/src/plugins/kanban/plugin.tsx` — a full `/kanban` board page +
sidebar nav row + live statusbar count + ⌘⌥N keybind. `defaultEnabled: false`,
so it inventories in Settings → Plugins until flipped on. It reuses the
in-tree `plugins/kanban/dashboard/plugin_api.py` via `ctx.rest`. Do NOT rebuild
a kanban desktop surface from the `kanban-api` HTTP plugin — the data is
already native on desktop.

## Fleet audit (2026-08-03, ~/.hermes/plugins/)

Tier 1 — worth converting (visual payoff per hour):
- **image-studio** — 8 tools (generate/edit/inpaint/animate/upscale/batch/
  presets/gallery), 11 presets, 9 models, cost tracking. No dashboard backend
  yet. Top visual win: a gallery/studio page showing artifacts + cost.
- **web-search-plus** — multi-provider search, URL extraction, quality reports,
  research mode; ships its own web console at `web/v3/console/` (adaptable into
  a pane).
- **hermes-lcm** — DAG-based context engine; a read-only context-map pane is
  possible, zero risk to the engine.

Tier 2 — small but real:
- **katana** — security audit pane (the SDK's `LogView` component fits an
  audit-trail viewer).
- **icarus** — memory timeline page.
- **eikon** — statusbar avatar + ⌘K commands (its 6 tools map 1:1 to palette
  entries).
- **ponytail** — statusbar mode chip (~10 lines, no backend).

Tier 3 — do NOT convert:
- **kanban-api** (:8643) — LAN bridge for the Pi mirror; bundled desktop kanban
  already covers the data.
- **session-api** (:8644) — LAN bridge for mirror chat; the desktop app shows
  the current session natively and the Sessions pane overlaps the rest.

## Manifest signals

- `kind: backend` → provider-style plugin (image-studio, mnemosyne).
- `kind: standalone` → tools/hooks plugin.
- `provides_tools: []` + `provides_hooks: []` → pure service (kanban-api,
  session-api) — likely a mirror/LAN bridge, check before proposing desktop
  conversion.

## User context

User is visual-first: when proposing desktop plugin concepts, lead with the
surfaces that SHOW things (gallery, board, timeline), not plumbing. User
prefers the audit/tier framing over open-ended concept docs.
