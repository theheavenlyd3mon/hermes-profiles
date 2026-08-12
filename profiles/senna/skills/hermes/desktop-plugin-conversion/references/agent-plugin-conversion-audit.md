# Agent Plugin → Desktop Audit — 2026-08-03 session

The full audit of `~/.hermes/plugins/` for Hermes Desktop conversion
potential, plus the verified data models for the two plugins chosen for
concept work (image-studio Studio page, hermes-lcm Context Map). Reuse the
tiered-verdict shape; the data models below are ground truth for these two
plugins.

## Manifest inventory (verified)

| Plugin | Kind | Desktop verdict | Why |
|---|---|---|---|
| image-studio v1.6.0 | backend, 13 tools | **Tier 1** — Gallery/Studio page | Rich artifacts (images), history DB with cost, presets; NO UI shipped at all |
| web-search-plus v3.4.1 | tools+hooks | **Tier 1/2** — Research console page | Ships its own web console (`web/v3/console/`) but it's OPERATOR telemetry (Overview/Routing Receipts/Benchmark History), not a search UI — adapt, don't copy |
| hermes-lcm v0.20.0 | tools | **Tier 1** — Context Map pane/page | DAG schema is a ready-made graph; read-only viz, zero engine risk |
| katana | standalone, hooks | **Tier 2** — security audit pane | Audit trail is LogView material |
| icarus v0.3.0 | tools+hooks | **Tier 2** — memory timeline page | Self-memory + replacement-model status |
| eikon v1.0.0 | standalone, 6 tools | **Tier 2** — statusbar avatar + ⌘K commands | Tool surface maps 1:1 to palette commands |
| ponytail v0.1.0 | standalone, hooks | **Tier 2 (cheap)** — statusbar chip | ~10-line chip, active this session |
| kanban-api | standalone, HTTP :8643 | **Tier 3 — already covered** | Desktop app BUNDLES a full kanban plugin; port stays for the mirror/LAN |
| session-api | standalone, HTTP :8644 | **Tier 3 — overlaps built-in** | Desktop shows current session natively; LAN bridge for mirror hermes-chat only |

## Bundled desktop plugins (do NOT re-propose)

`apps/desktop/src/plugins/`: `kanban/` (full board — page, nav, statusbar
count, ⌘⌥N; `defaultEnabled: false`), `example/`, `gateway-pill/`,
`hello-runtime/`. Kanban reads via `ctx.rest` → `plugins/kanban/dashboard/
plugin_api.py` (the canonical conversion pattern).

## image-studio data model (for the Studio page)

- Repo: `~/Projects/hermes-image-studio` (senna profile symlinks
  `~/.hermes/plugins/image-studio` → it; creative profile has its own clone
  at `~/.hermes/profiles/creative/plugins/image-studio`).
- Output: `HERMES_IMAGE_STUDIO_OUTPUT=~/Pictures/Image Studio`
  (set in both profiles' `.env`; plugin default `/Volumes/Spare Drive/...`
  does not exist on this Mac).
- History DB: `~/.hermes/data/image-studio/history.db` — **created on first
  generation, did NOT exist 2026-08-03** (empty-gallery v1 is expected).
- `generations` table: `id, created_at, prompt, preset, model, seed, steps,
  aspect_ratio, width, height, image_url, file_path, tags, cost_usd`.
- Also: `upscales` (source_gen_id FK), `saved_prompts` (name UNIQUE),
  `videos`.
- Engine importable directly: `image_studio.engine.generate/upscale/edit/
  animate/inpaint`; `image_studio.presets.PRESETS` (11); models dict has
  prices. `gallery.py` builds a static `gallery.html` (generator only, not
  a UI — don't mistake it for one).
- Backend plan: add `dashboard/` to the image-studio plugin → GET
  /gallery, /stats, /presets, /prompts; POST /generate.

## hermes-lcm data model (for the Context Map)

- hermes-lcm is a THIRD-PARTY git clone (Voltropy) at
  `~/.hermes/plugins/hermes-lcm/` — do not add `dashboard/` inside it; use
  a new `lcm-map` wrapper plugin (must be added to `plugins.enabled`).
- DB: `~/.hermes/profiles/senna/lcm.db` — 167.4 MB, 50,908 messages, 76
  summary nodes (2026-08-03).
- `summary_nodes`: `node_id, session_id, depth, summary, token_count,
  source_token_count, source_ids (JSON array), source_type, created_at,
  earliest_at, latest_at, expand_hint`. Edges = `source_ids`; `depth` =
  rollup level → layered layout, NO force physics needed.
- `messages`: `store_id, session_id, source, role, content, tool_call_id,
  tool_calls, tool_name, timestamp, token_estimate, pinned,
  conversation_id`.
- FTS tables exist (`messages_fts`, `nodes_fts`) for future search.
- Backend plan (`lcm-map` plugin): GET /sessions, /graph?session_id=,
  /node/:id, /messages. Read-only sqlite3, same pattern as session-api.

## Skills Hub result (2026-08-03)

`hermes skills search "desktop plugin"` → nothing. "graph visualization" →
gitnexus, memora (irrelevant). "dag" → `dagre-react-flow` (clawhub) — the
one relevant hit, but desktop disk plugins can only import
`@hermes/plugin-sdk`, `react`, `react/jsx-runtime`, so graph libs cannot
load. Layered-by-depth beats any third-party layout lib anyway.
