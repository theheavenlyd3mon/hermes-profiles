# Web dashboard contract — serve.py ↔ web/ (Vite+React+TS)

Session detail from the M4 dashboard build (2026-07). The reusable lesson is in
SKILL.md pitfalls; this file is the concrete contract so the two sides don't
drift again.

## Architecture (pi-borrow applied Python-side)

pi (earendil-works/pi) is a TS npm-workspaces monorepo built with **esbuild,
not Vite**. What AgentUnreal borrowed: the modular packages/* layout +
JSON-RPC-style UI contract. The core stays Python; Vite+React+TS lives ONLY in
`web/` (Murim Noir dashboard). `serve.py` (stdlib http.server, port **7822**)
is the backend.

## The contract (web/src/types.ts is the source of truth)

```
POST /api/run  {"prompt": "..."}  -> RunState
GET  /api/run/<id>                -> RunState
GET  /api/config                  -> RunState minus events (status bar)
GET  /api/health                  -> {"ok": true}

RunState = {
  id, prompt,
  status: 'idle'|'plan'|'run'|'build'|'done'|'error',
  bridge, memory: bool, provider, model,
  buildAttempt, buildMax,
  events: HarnessEvent[]
}
HarnessEvent =
  | {type:'plan', t, steps:[{tool, note}]}
  | {type:'tool.start', t, id, name, args}
  | {type:'tool.complete', t, id, name, duration, ok, result?, error?}
  | {type:'result', t, content, ok}
```

Vite dev proxy: `'/api' -> http://localhost:7822`. Frontend falls back to
`mockData.ts` MOCK_RUN when the backend is absent (fetch throws or !ok).

## Enrichment is the backend's job

The raw `on_event` hook emits `plan(steps)` / `tool.start(id,name,args)` /
`tool.complete(id,name,result)` / `result(content)` — **no** `t`, `duration`,
`ok`, or `status`. serve.py's `_RunBuilder` derives them: monotonic-clock `t`
per event, `duration` = complete−start matched by call id, `ok` = result dict
has no `"error"` key, `status` from last event type (`build_module` bumps
`buildAttempt` and sets `build`).

## Mismatches actually hit (why frontend-first matters)

Backend was written before reading types.ts and got BOTH wrong:
1. Port 8000 vs Vite proxy 7822.
2. Field names: backend `{task}` in / `{run_id}` out vs frontend `{prompt}` /
`{id}`. Backend now accepts `prompt` (and `task` as fallback) and returns `id`.
