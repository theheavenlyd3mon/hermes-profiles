# Hermes Workspace Setup — Detailed Reference

## .env Configuration

```bash
# Required — point to the profile's gateway API server
HERMES_API_URL=http://127.0.0.1:8642

# Optional — dashboard URL (default: 127.0.0.1:9119)
HERMES_DASHBOARD_URL=http://127.0.0.1:9119

# Server binding (local-only by default)
PORT=3000
HOST=127.0.0.1

# HermesWorld game integration (optional)
VITE_HERMESWORLD_ENABLED=true
```

## API Server Must Be Enabled

The gateway's API server on :8642 is **opt-in**. Verify it's running:
```bash
lsof -i :8642 -sTCP:LISTEN
curl -s http://127.0.0.1:8642/health
```

If not running, add to config.yaml:
```yaml
platforms:
  api_server:
    enabled: true
    extra:
      host: 127.0.0.1
      port: 8642
```
Then restart the gateway.

## Multi-Profile Port Conflicts

Each profile defaults to port 8642. When multiple profiles run simultaneously, the default configs compete for the same port.

**Actual behavior (important):** The gateway does NOT fail when 8642 is taken. It silently binds to the next available port (8643, then 8644, etc.). This means the runtime port can drift from what's in config.yaml — and the workspace .env references the runtime port, not the config port.

**Pitfall — silent port drift on restart:**
If gateways restart in a different order, port assignments shift. A gateway that was on 8643 might land on 8642 next time, or vice versa. The workspace .env stays fixed, so the workspace silently loses connection. Always verify the actual port:
```bash
# Check which PID is on which port
lsof -i :8642 -sTCP:LISTEN -o
lsof -i :8643 -sTCP:LISTEN -o
# Confirm the workspace .env matches reality
cat ~/hermes-workspace/.env | grep HERMES_API_URL
```

**Diagnosis workflow** — before setting ports, audit which profiles have api_server and what ports are actually in use:

```bash
# 1. Find all profiles
ls -d ~/.hermes/profiles/*/

# 2. Check which have api_server configured in their own config
for p in ~/.hermes/profiles/*/; do
  name=$(basename "$p")
  if grep -q 'api_server:' "$p/config.yaml" 2>/dev/null; then
    echo "$name: has api_server"
  else
    echo "$name: no api_server in own config"
  fi
done

# 3. Check root config inheritance (bleeds into all profiles)
grep -A5 'api_server:' ~/.hermes/config.yaml

# 4. Find actual runtime ports (gateway PIDs -> listening ports)
lsof -i :8642 -sTCP:LISTEN
lsof -i :8643 -sTCP:LISTEN

# 5. Map PID to profile
ps aux | grep 'gateway run' | grep -v grep

# 6. Test live endpoints
curl -s http://127.0.0.1:8642/health
curl -s http://127.0.0.1:8643/health
```

**Config file location caveat:** `hermes --profile X config set` writes to the flat `~/.hermes/profiles/X/config.yaml`. But some profiles (like senna) read their config from a nested structure at `~/.hermes/profiles/senna/home/.hermes/config.yaml`. If `hermes config set` succeeds but the change doesn't take effect on restart, the profile might be reading from a different config file. Check by looking for a `home/.hermes/` directory inside the profile: `ls ~/.hermes/profiles/<profile>/home/.hermes/config.yaml 2>/dev/null`.

**Adding api_server to a profile that lacks it:** Some profiles won't have `api_server` in their config at all but still run with one — they inherit it from the root `~/.hermes/config.yaml`. To make the config explicit:
```yaml
# Add to profile's config.yaml
platforms:
  api_server:
    enabled: true
    extra:
      host: 127.0.0.1
      port: 8642
```
If the profile uses a `home/.hermes/config.yaml` structure, add it there instead.

**Config inheritance gotcha:** The root `~/.hermes/config.yaml` can bleed into profile configs. A profile with no explicit `api_server` section can still end up with one because profiles inherit from the root config. This causes silent port conflicts when multiple profiles inherit the same default port. Fix: make the port config explicit in each profile that needs one, rather than relying on inheritance.

**Not every profile needs an API server:** Profiles that run as Discord bot gateways (architect, researcher, secretary, foreman, etc.) don't expose an HTTP API server. Only profiles the workspace connects to (senna, coder) need explicit `api_server` config. Adding api_server to all 17 profiles is unnecessary — only add it where the workspace needs direct HTTP access.

**Recommended fix** — set unique ports explicitly per profile so config matches runtime:
```bash
hermes --profile senna config set platforms.api_server.extra.port 8643
hermes --profile coder config set platforms.api_server.extra.port 8642
```
Then restart both gateways. Update workspace `.env` to match the correct port: `HERMES_API_URL=http://127.0.0.1:8643`

## Pitfall: health ≠ API server working

`/health` returns ok even when the API server feature is disabled. To verify:
```bash
curl -s http://127.0.0.1:8642/api/sessions | head -c 100
# Should return JSON array, not "404: Not Found"
```

## Pitfall: Port 3000 conflicts with Vite dev servers

Check with `lsof -i :3000 -sTCP:LISTEN`. If PID's cwd is not `~/hermes-workspace`, it's a conflict.

## Pitfall: Skills/Swarm show "Backend Unavailable"

Root cause is always: API server not enabled or gateway not restarted after enabling it.

## Startup Script

```bash
#!/bin/bash
PROFILE="${1:-senna}"
GATEWAY_PORT="${2:-8642}"

hermes --profile "$PROFILE" dashboard --port 9119 --no-open --skip-build &
DASHBOARD_PID=$!
sleep 3

cd ~/hermes-workspace && HERMES_API_URL="http://127.0.0.1:$GATEWAY_PORT" pnpm dev &
WORKSPACE_PID=$!

echo "Dashboard PID: $DASHBOARD_PID"
echo "Workspace PID: $WORKSPACE_PID"
echo "Workspace: http://127.0.0.1:3000"
echo "Dashboard: http://127.0.0.1:9119"
echo "Gateway:   http://127.0.0.1:$GATEWAY_PORT"
wait
```

## Security Notes

- Workspace binds to 127.0.0.1 by default (local only)
- For remote access, set `HOST=0.0.0.0` and **must** set `HERMES_PASSWORD`
- Without a password, the server refuses to bind to non-loopback

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Workspace loads but no sessions | Gateway API not running | Check `lsof -i :864x`, restart gateway |
| Dashboard features missing | Dashboard not started | Start `hermes dashboard` on :9119 |
| 401 errors | API_SERVER_KEY mismatch | Set HERMES_API_TOKEN in workspace .env |
| Port conflict | Something on :3000 or :9119 | Change PORT in .env or `--port` flag |
| Skills/Swarm show "Backend Unavailable" | API server not enabled | Edit config, restart gateway |
| Wrong app renders on :3000 | Another Vite project hijacked port | Check `lsof -i :3000` PID's cwd |
| Second profile's gateway won't bind | Port 8642 already taken | Set unique port per profile |
| Workspace shows stale connection after .env edit | Workspace reads .env at startup only | Restart workspace process |
| Workspace can't reach gateway despite gateway running | Port drift — gateway landed on different port than config says | Check `lsof -i :8642 :8643`, update `.env` to match runtime port |

## Workspace Capability Probing (Zero-Fork Architecture)

The workspace uses a **zero-fork** architecture. It probes TWO services at startup and reports capabilities:

| Probe Target | URL | What It Provides |
|---|---|---|
| **Gateway** (`CLAUDE_API`) | :8642/:8643 via `HERMES_API_URL` | `/health`, `/v1/chat/completions`, `/v1/models` — core chat |
| **Dashboard** (`CLAUDE_DASHBOARD_URL`) | :9119 via `HERMES_DASHBOARD_URL` | sessions, skills, jobs, config, MCP, Conductor, kanban |

### Reading the capability map

The workspace exposes live capability state through its API. Check from CLI:

```bash
curl -s http://127.0.0.1:3000/api/connection-status | python3 -m json.tool
```

Key fields:
- `conductor` — requires GET `/api/conductor/missions` on dashboard returning JSON or 401
- `mcp` — requires GET `/api/mcp` on dashboard or gateway returning JSON
- `mcpFallback` — enabled when dashboard config has `mcp_servers` key (falls back to config-read mode)
- `dashboard.available` — requires GET `/api/status` on dashboard returning version JSON
- `sessions`, `skills`, `config`, `jobs` — available when dashboard is available

Force a fresh probe (clears 120s cache):
```bash
curl -s -X POST http://127.0.0.1:3000/api/gateway-reprobe
```

### How the probe works for each feature

The workspace probes capabilities by fetching URLs from the dashboard. If the dashboard doesn't have a route for that URL, its SPA catch-all serves `index.html` with content-type `text/html` — the probe recognizes this as "not available."

To check if a route exists on the dashboard:
```bash
# Route exists: returns JSON (even 401 is good — means route is registered)
curl -s http://127.0.0.1:9119/api/conductor/missions
# Returns: {"detail":"Unauthorized"}  ← route exists, needs auth

# Route missing: returns HTML (SPA catch-all)
curl -s http://127.0.0.1:9119/api/conductor/missions
# Returns <!doctype html>...  ← route not registered
```

The probe considers these responses as "available":
- HTTP 401 (route exists, auth-gated) for Conductor
- HTTP 200 with `application/json` content-type
- HTTP 200+valid JSON body for MCP

### Missing capability diagnosis

1. **Conductor unavailable** — Dashboard lacks `/api/conductor/missions` routes. The fix is adding GET/POST/DELETE handlers to `hermes-agent/hermes_cli/web_server.py` (see "Conductor Endpoint Fix" below).

2. **MCP unavailable but mcpFallback works** — Normal. The native `/api/mcp` REST endpoint is not yet implemented in vanilla hermes-agent. MCP management works via the dashboard config's `mcp_servers` key (config CRUD, no test/discover/logs).

3. **Dashboard shows "Not Available"** — Dashboard not running or not reachable. Verify: `curl -s http://127.0.0.1:9119/api/status`. If dashboard is behind auth, the workspace's `dashboardFetch` function scrapes the session token from the dashboard HTML and retries.

4. **All capabilities show as false** — Gateway not running or `HERMES_API_URL` is wrong. Check: `curl -s http://127.0.0.1:8643/health`.

## Conductor Endpoint Fix

The Conductor feature in the workspace requires the dashboard to expose `GET /api/conductor/missions` and `POST /api/conductor/missions`. Add them to the Hermes dashboard backend:

1. Open `~/hermes-agent/hermes_cli/web_server.py`
2. Add after the `_PluginVisibilityBody` class:

```python
# Conductor missions (in-memory, ephemeral — workspace's own conductor-spawn routes manage real state)
_conductors: dict[str, dict] = {}

class _ConductorMissionCreate(BaseModel):
    name: str = ""
    prompt: str = ""

@app.get("/api/conductor/missions")
async def get_conductor_missions(request: Request):
    return {"missions": list(_conductors.values())}

@app.post("/api/conductor/missions")
async def create_conductor_mission(request: Request, body: _ConductorMissionCreate):
    import uuid
    mission_id = str(uuid.uuid4())[:8]
    mission = {
        "id": mission_id,
        "name": body.name or f"mission-{mission_id}",
        "prompt": body.prompt,
        "status": "created",
        "created_at": __import__("time").time(),
    }
    _conductors[mission_id] = mission
    return {"id": mission_id, "name": mission["name"], "session_id": mission_id}

@app.delete("/api/conductor/missions/{mission_id}")
async def delete_conductor_mission(request: Request, mission_id: str):
    _conductors.pop(mission_id, None)
    return {"ok": True}
```

3. **Don't include `_require_token(request)`** in the conductor handlers — the workspace's `dashboardFetch` handles auth via session token, and a `_require_token` call blocks the workspace's probe from detecting the route.

4. Restart the dashboard:
```bash
kill -TERM $(lsof -i :9119 -sTCP:LISTEN -t)
hermes dashboard --port 9119 --no-open &
```

5. The workspace detects the new capability on its next probe cycle (up to 120s). Force immediate reprobe: visit the Conductor tab in the UI, or:
```bash
curl -s -X POST http://127.0.0.1:3000/api/gateway-reprobe
```

**Python .pyc cache trap:** The dashboard's `web_server.py` compiles to `__pycache__/web_server.cpython-311.pyc` on first import. The `.pyc` lives in the **root** hermes-agent checkout at `~/.hermes/hermes-agent/hermes_cli/__pycache__/`, NOT in the profile-specific copy at `~/.hermes/profiles/senna/hermes-agent/hermes_cli/__pycache__/`. When restarting the dashboard after editing web_server.py, always clear BOTH locations:

```bash
find ~/.hermes -path "*/__pycache__/*web_server*" -delete
```

**Vite SSR module cache:** The workspace's `pnpm dev` runs Vite with `@tanstack/react-start`. Server-side `.ts` files (`src/server/*.ts`) are compiled once at process startup and cached in Node.js memory. `touch` or file watchers do NOT trigger recompilation. To force a fresh load:

```bash
lsof -ti :3000 | xargs kill -9
rm -rf .tanstack node_modules/.vite
pnpm dev
```

**Auth middleware `_PUBLIC_API_PATHS`:** The dashboard has a global auth middleware at web_server.py:236-246 that blocks ALL `/api/` paths except those in the `_PUBLIC_API_PATHS` frozenset. Any new `/api/` route must either:
- Be added to the frozenset (if it should be public), OR
- Accept that the middleware blocks unauthenticated requests before the handler runs (`_require_token` inside the handler is redundant — middleware already returns 401)

The `_PUBLIC_API_PATHS` set is at web_server.py:114 and includes `/api/status`, `/api/config/defaults`, `/api/config/schema`, `/api/model/info`, `/api/dashboard/themes`, `/api/dashboard/plugins`, `/api/dashboard/plugins/rescan`. Add new paths here, not in the handler body.
