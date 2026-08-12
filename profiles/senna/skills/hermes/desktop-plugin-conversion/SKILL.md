---
name: desktop-plugin-conversion
description: Audit agent plugins for Hermes Desktop conversion.
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [desktop, plugins, conversion, audit, ui]
    category: hermes
    related_skills: [hermes-desktop-plugins]
---

# Desktop Plugin Conversion (agent plugin → desktop surface)

How to turn an existing **agent plugin** (Python + `plugin.yaml` in
`~/.hermes/plugins/`) into a **Hermes Desktop** surface (pane, page,
statusbar chip), or audit a plugin inventory for which ones are worth
converting. Companion to the authoring skill `hermes-desktop-plugins`
(which covers writing a desktop plugin from scratch); this skill covers the
*conversion path*: what's bridgeable, what to check before proposing, and
the rules that prevent reinventing wheels.

## The two-plugin-systems distinction (state it first)

- **Agent plugins** — `~/.hermes/plugins/<name>/plugin.yaml`, Python. Add
  tools/hooks/backends. No UI, loaded by the agent runtime.
- **Desktop plugins** — `~/.hermes/desktop-plugins/<name>/plugin.js`, single
  plain ESM file. Add UI only. Loaded by the desktop app, hot-reloaded on
  save. Folder name MUST equal plugin `id`.

## The bridge (how conversion actually works)

`ctx.rest` / `ctx.socket` on the desktop side reaches a FastAPI backend at
`/api/plugins/<id>/`. That backend lives in a `dashboard/` subfolder of an
AGENT plugin:

```
~/.hermes/plugins/<id>/dashboard/
├── manifest.json      # { "name": "<id>", "api": "plugin_api.py" }
└── plugin_api.py      # exports router = APIRouter()
```

Then the desktop plugin calls `ctx.rest('/board')` → `GET
/api/plugins/<id>/board`. This is the exact pattern the bundled Kanban plugin
uses (`apps/desktop/src/plugins/kanban/` → `plugins/kanban/dashboard/`).

**Security gate:** the Python backend imports only when the plugin is in
`plugins.enabled` in `config.yaml` — a NEW wrapper plugin must be added to
that allow-list, and the desktop-side toggle alone does NOT import Python.

## Audit signals (which plugins are worth converting)

1. Plugin exposes **data worth seeing** — a gallery, history DB, cost ledger,
   DAG, transcript store — or already ships a web console/UI to adapt.
2. `provides_tools` rich in artifacts (images, transcripts, graph nodes).
   Pure-behavior hooks (ponytail-style mode, katana-style scanning) are at
   best statusbar-chip + palette-command material, not full pages.
3. `kind: backend` or `kind: standalone` with a real store beats pure-hook
   plugins.

## Rules learned the hard way

- **Check what the desktop app ALREADY ships before proposing a
  board/gallery.** The app bundles a complete Kanban plugin — `/kanban` page,
  sidebar nav, statusbar running/ready count, ⌘⌥N new-task keybind —
  `defaultEnabled: false` (off by default, flip in Settings → Plugins).
  "Kanban visual" = enable it, never rebuild it.
- **Mirror/LAN HTTP plugins are NOT desktop candidates.** `kanban-api`
  (:8643) and `session-api` (:8644) are HermesMirror bridges for a Pi over
  the LAN. On desktop, read the same data via gateway RPC (`host.request`)
  or a `dashboard/` backend — never duplicate the HTTP hop.
- **Do NOT add `dashboard/` inside a third-party git clone** (e.g. hermes-lcm
  is Voltropy's repo; image-studio is Cliff's repo). Create a NEW tiny
  read-only wrapper plugin that reads the DB directly (the session-api
  pattern: plain sqlite3, no core changes) — it survives upstream updates.
- **The import restriction kills graph/visualization libraries.** Disk
  desktop plugins import ONLY `@hermes/plugin-sdk`, `react`,
  `react/jsx-runtime`. A Skills Hub find like `dagre-react-flow` will NOT
  load. For DAG/graph rendering, exploit the data's own structure — LCM
  `summary_nodes.depth` gives a layered layout with zero physics engine; SVG
  is fine at realistic node counts (dozens, not thousands).
- **Data stores are often created on first use, not at install.** image-studio
  `history.db` doesn't exist until the first generation — the gallery starts
  empty and grows. Design the empty state honestly; say so in the concept
  rather than implying data is already there.
- **Check the source code for schema when the DB doesn't exist yet** — read
  the `CREATE TABLE` statements from `history.py`-style modules instead of
  assuming a live DB to introspect.

## Workflow

1. `ls ~/.hermes/plugins/*/plugin.yaml` — inventory kinds, tools, hooks.
2. `find` for `dashboard/plugin_api.py` — plugins already desktop-ready.
3. Grep `apps/desktop/src/plugins/` — what the app already ships (bundled
   kanban etc.) so you never propose a duplicate.
4. For each candidate, pull the data model (DB schema from source, output
   dirs, env redirects like `HERMES_IMAGE_STUDIO_OUTPUT`).
5. Produce a tiered verdict: Tier 1 = genuinely worth a page/pane, Tier 2 =
   small statusbar/palette, Tier 3 = already covered / LAN-only / not visual.
6. Write concept docs (see `references/agent-plugin-conversion-audit.md` for
   the 2026-08-03 session's full audit table and data models), then get the
   user's green-light before building anything.

## Verification

- Concept is grounded: every claimed data source exists (file, dir, schema
  read from source), every "already covered" claim checks the bundled
  plugins list.
- No duplicate proposals: kanban-style surfaces point at the bundled plugin.
- No third-party repo is modified; any new backend is a wrapper plugin.
