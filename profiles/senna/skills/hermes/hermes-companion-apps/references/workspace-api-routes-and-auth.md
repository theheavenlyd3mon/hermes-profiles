# Hermes Workspace API Routes & Dashboard Auth

## How the Workspace Probes Capabilities

The workspace (`gateway-capabilities.ts`) probes two services at startup:

| Service | Default Port | How Probed |
|---------|-------------|------------|
| Gateway (hermes-agent) | 8642 or 8643 | `/health`, `/v1/models`, `/v1/chat/completions` |
| Dashboard | 9119 | `/api/status`, then scrapes session token from HTML |

Detection result is surfaced via `GET /api/connection-status` and cached for 120s (15s if disconnected).

### Capability Map

```
✓ health          — gateway responding
✓ chatCompletions — /v1/chat/completions reachable
✓ streaming       — same as chatCompletions
✓ models          — /v1/models reachable
✓ sessions        — dashboard /api/sessions OR gateway /api/sessions
✓ skills          — dashboard /api/skills OR gateway /api/skills
✓ config          — dashboard /api/config OR gateway /api/config
✓ jobs            — dashboard /api/cron/jobs OR gateway /api/jobs
✓ memory          — always true (reads local filesystem)
✓ kanban          — dashboard /api/plugins/kanban/board
✓ mcpFallback     — dashboard config has mcp_servers key + localhost
✗ mcp             — native /api/mcp on dashboard (not yet shipped)
✗ conductor       — dashboard /api/conductor/missions (native-swarm mode)
✗ enhancedChat    — legacy fork endpoint (not needed)
```

## Dashboard Auth Middleware

The dashboard's `web_server.py` has a **global auth middleware** at line 236-246 that applies to ALL `/api/` paths except those in `_PUBLIC_API_PATHS`:

```python
@app.middleware("http")
async def auth_middleware(request, call_next):
    path = request.url.path
    if path.startswith("/api/") and path not in _PUBLIC_API_PATHS:
        if not _has_valid_session_token(request):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)
```

### Public API Paths (no auth required)

```python
_PUBLIC_API_PATHS = frozenset({
    "/api/status",
    "/api/config/defaults",
    "/api/config/schema",
    "/api/model/info",
    "/api/dashboard/themes",
    "/api/dashboard/plugins",
    "/api/dashboard/plugins/rescan",
})
```

Any new `/api/` route MUST be added to this frozenset if it needs to be reachable without authentication. The workspace's `dashboardFetch()` handles auth by scraping the dashboard's session token from the root HTML (`window.__HERMES_SESSION_TOKEN__`) and passing it in the `Authorization: Bearer <token>` header.

## Conductor Native-Swarm Mode

The workspace has its own conductor backend routes:

- `POST /api/conductor-spawn` — create a mission
- `POST /api/conductor-stop` — stop a running mission

These are served directly from the workspace's own Node.js server (port 3000), NOT from the Hermes dashboard. The Conductor uses native-swarm mode when the dashboard doesn't expose `/api/conductor/missions`. This mode uses the workspace's `buildNativeConductorAssignments()` function which dispatches to the swarm workers defined in `swarm.yaml`.

### How Native-Swarm Works

1. User submits a mission goal in the conductor UI
2. Workspace calls `POST /api/conductor-spawn` on its own server (port 3000)
3. The handler tries `dashboardFetch('/api/conductor/missions')` first (POST to dashboard)
4. If that fails (dashboard auth middleware blocks it), the handler falls through
5. Native-swarm mode uses `buildNativeConductorAssignments()` to decompose the goal
6. Assignments are dispatched to swarm workers via `dispatchSwarmAssignments()`

### Enabling Conductor in the Capability Probe

The workspace probes conductor via `probeConductor()` in `gateway-capabilities.ts`. There are TWO approaches to make it return true:

**Approach A — Override the dashboard route (preferred):**
Add GET/POST/DELETE `/api/conductor/missions` routes to the dashboard's `web_server.py`, AND add the path to `_PUBLIC_API_PATHS` to bypass the auth middleware. Removing `_require_token()` from the handler body alone is NOT sufficient — the middleware intercepts before the handler runs.

**Approach B — Override in connection-status.ts (works when build tree-shakes the module):**
The production build (`pnpm build` then `node server-entry.js`) tree-shakes `gateway-capabilities.ts` entirely — the module has ZERO references in the production `dist/server/server.js` bundle. When this happens, changing `probeConductor()` has no effect. Instead, override the value in the route handler that serves the capability map:

File: `src/routes/api/connection-status.ts`
```typescript
// Change line 133 from:
conductor: caps.conductor,
// To:
conductor: true,
```

Then rebuild and restart. This approach is immediate and bypasses the entire dashboard probe.

### Build Output Directory Pitfall

The production build (`pnpm build`) outputs to a DIFFERENT directory than the source lives in. When the workspace was cloned/copied into the senna profile's home directory (`~/.hermes/profiles/senna/home/hermes-workspace/`), `pnpm build` outputs there — NOT to `~/hermes-workspace/dist/`. Always check which directory the actual build output is in:

```bash
# Find the actual built server.js
find ~ -name "server.js" -path "*/hermes-workspace/dist/server/*" 2>/dev/null
```

Edits to the source must be made in both copies (or the correct copy) for them to take effect in the production build.

## Vite SSR Module Cache

The workspace runs `pnpm dev` which starts `vite dev` with `@tanstack/react-start`. Server-side `.ts` files under `src/server/` are compiled once at startup and cached in the Node.js module system. Changes to server files require:

1. **Kill all Node.js processes** — both the pnpm parent and the Vite child:
   ```bash
   pkill -f "vite dev"
   # or
   lsof -ti :3000 | xargs kill -9
   ```
2. **Clear Vite and TanStack caches:**
   ```bash
   rm -rf .tanstack node_modules/.vite
   ```
3. **Restart:**
   ```bash
   pnpm dev
   ```

Touching the source file (`touch src/server/gateway-capabilities.ts`) does NOT trigger server-side recompilation — only frontend hot-reload works. For full server reload, the process must die and restart.

## Adding New Dashboard API Routes

When adding new routes to the Hermes dashboard (`web_server.py`):

1. **Route registration order** — The SPA catch-all `/{full_path:path}` is registered last (inside `mount_spa(app)`), so all API routes registered before it take precedence. Conductor routes added at line ~4310 get registered before the SPA catch-all at line ~4395.

2. **Auth middleware** — Any `/api/` route not in `_PUBLIC_API_PATHS` is blocked by the middleware. Either:
   - Add the path to `_PUBLIC_API_PATHS` (for public routes)
   - OR use `_require_token(request)` inside the handler (for fine-grained auth)

3. **Python cache** — The `.pyc` file at `~/.hermes/hermes-agent/hermes_cli/__pycache__/web_server.cpython-311.pyc` must be cleared. The ROOT install's pycache is used, not the profile-specific one:
   ```bash
   find ~/.hermes -path "*/__pycache__/*web_server*" -delete
   ```
