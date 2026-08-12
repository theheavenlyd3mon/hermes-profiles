# Workspace Feature Probe — Verifying Before Launch

Before telling the user the workspace is ready, probe the actual API endpoints
to confirm each feature will work. The workspace uses a zero-fork architecture:
it probes the gateway and dashboard at startup and shows "Not Available" for
missing features.

## What to Probe

The workspace at `http://localhost:3000` has its own backend server. It reads
`HERMES_API_URL` and `HERMES_DASHBOARD_URL` from `.env` and probes these:

### Gateway (usually :8642 or :8643)

| Endpoint | What it checks | Expected |
|----------|---------------|----------|
| `/health` | Gateway is alive | `{"status":"ok"}` |
| `/v1/models` | Chat completions available | JSON model list |
| `/v1/chat/completions` | Streaming capable | 405 (exists but GET rejected) |

### Dashboard (:9119)

| Endpoint | What it checks | Expected |
|----------|---------------|----------|
| `/api/status` | Dashboard is alive | `{"version":"0.13.0",...}` |
| `/api/sessions` | Sessions API | `{"sessions":[...]}` |
| `/api/skills` | Skills management | `[{"name":"...","enabled":true},...]` |
| `/api/config` | Config access (auth required) | Full config YAML as JSON |
| `/api/plugins/kanban/board` | Kanban board | `{"columns":[...]}` — empty board is fine |
| `/api/conductor/missions` | Conductor (optional) | 404 or HTML = not available |

### One-shot probe script

```bash
API=http://127.0.0.1:8643
DASH=http://127.0.0.1:9119

# Get dashboard auth token
TOKEN=*** -s $DASH/ | grep -o 'window.__HERMES_SESSION_TOKEN__=*** | cut -d'"' -f2)
AUTH="Authorization: Bearer $TOKEN"

echo "=== Gateway ==="
echo "health:       $(curl -s --connect-timeout 2 $API/health | head -c 50)"
echo "models:       $(curl -s --connect-timeout 2 $API/v1/models | head -c 50)"

echo "=== Dashboard ==="
echo "status:       $(curl -s --connect-timeout 2 $DASH/api/status | head -c 50)"
echo "sessions:     $(curl -s --connect-timeout 2 -H "$AUTH" $DASH/api/sessions | head -c 50)"
echo "skills:       $(curl -s --connect-timeout 2 -H "$AUTH" $DASH/api/skills | head -c 50)"
echo "kanban:       $(curl -s --connect-timeout 2 -H "$AUTH" $DASH/api/plugins/kanban/board | head -c 50)"
```

### Reading the live capability map

The workspace exposes its probe results at:
```bash
curl -s http://127.0.0.1:3000/api/connection-status | python3 -m json.tool
```

Key fields: `conductor`, `mcp`, `mcpFallback`, `dashboard.available`, `kanban`.

Force a fresh probe (clears the 120s cache):
```bash
curl -s -X POST http://127.0.0.1:3000/api/gateway-reprobe
```

### Production build tree-shaking pitfall

The production build (`pnpm build` → `node server-entry.js`) tree-shakes `gateway-capabilities.ts` entirely — the compiled `dist/server/server.js` bundle has zero references to the probe functions or capability map. This means:

1. Changing `probeConductor()` to `return true` does NOT affect the production server
2. The only way to override a capability in production is to modify `src/routes/api/connection-status.ts` (the route handler that builds the response body)
3. Source edits must be made in the SAME directory that `pnpm build` outputs to — check with `find ~ -name "server.js" -path "*/hermes-workspace/dist/server/*"` to find the right one

## Dashboard Auth Token

The dashboard injects an ephemeral session token into its root HTML page:

```html
<script>window.__HERMES_SESSION_TOKEN__="abc123...";</script>
```

The workspace's `fetchDashboardToken()` scrapes this on startup and uses it
for authenticated requests. The token changes on each dashboard restart.
Probe without the token returns `{"detail":"Unauthorized"}` for protected
endpoints — that means the workspace will also need to scrape the token.

## Feature Autodetection

The workspace's `probeGateway()` function runs at startup and logs results:

```
[gateway] gateway=http://127.0.0.1:8643 dashboard=http://127.0.0.1:9119 mode=zero-fork
         core=[health, chatCompletions, models, streaming, dashboard]
         enhanced=[sessions, skills, memory, config, jobs, mcp, mcpFallback, conductor]
         missing=[]
```

- `mode=zero-fork` = full features (gateway + dashboard both healthy)
- `mode=portable` = gateway reachable but dashboard missing → partial features
- `mode=disconnected` = nothing reachable

Missing features show graceful placeholders in the UI, not errors.

## Swarm Verification

The workspace loads swarm configuration from `swarm.yaml` in the workspace root.
Each worker's `profile:` field must match a real Hermes profile:

```bash
# Check all swarm profiles exist
for p in $(grep 'profile:' ~/hermes-workspace/swarm.yaml | awk '{print $2}'); do
  if [ -d "~/.hermes/profiles/$p" ]; then
    echo "$p: exists"
  else
    echo "$p: MISSING"
  fi
done
```

Missing profiles show up as disconnected workers in the Swarm tab.

## Operations Tab Presets

Workspace ops presets live in `src/screens/agents/agent-presets.ts`.
They seed browser localStorage on first visit — profiles appear regardless,
but custom emoji/color/description only show if seeded.

## Skills Count

The workspace serves its own `/api/skills` endpoint (not the dashboard's):

```bash
curl -s http://localhost:3000/api/skills | python3 -c \
  "import json,sys; d=json.load(sys.stdin);\
   print(f'{len(d.get(\"skills\",[]))} skills from workspace')"
```

This endpoint combines skills from the dashboard with registry data.