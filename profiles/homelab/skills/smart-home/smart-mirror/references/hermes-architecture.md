## Gateway API Contract

Bridge expects Hermes gateway to expose:
```
GET /api/kanban/board
Response: { tasks: [{ task_id, title, assignee, status, ... }], updated_at }
```

**⚠️ NOT YET IMPLEMENTED.** The bridge correctly handles the 404 with exponential backoff (as of 2026-05-15), but display modules receive no task data until the endpoint is added.

### How the Hermes Gateway Routes Work

The gateway uses **aiohttp** (Python async HTTP). The `api_server` platform adapter creates a `web.Application` with middlewares and registers routes in `api_server.py` (lines ~3363-3386):

```python
self._app = web.Application(middlewares=mws, client_max_size=MAX_REQUEST_BYTES)
self._app.router.add_get("/health", self._handle_health)
self._app.router.add_get("/health/detailed", self._handle_health_detailed)
self._app.router.add_get("/v1/models", self._handle_models)
self._app.router.add_get("/v1/capabilities", self._handle_capabilities)
self._app.router.add_post("/v1/chat/completions", self._handle_chat_completions)
self._app.router.add_post("/v1/responses", self._handle_responses)
self._app.router.add_get("/v1/responses/{response_id}", self._handle_get_response)
self._app.router.add_delete("/v1/responses/{response_id}", self._handle_delete_response)
# Cron jobs management API
self._app.router.add_get("/api/jobs", self._handle_list_jobs)
self._app.router.add_post("/api/jobs", self._handle_create_job)
self._app.router.add_get("/api/jobs/{job_id}", self._handle_get_job)
self._app.router.add_patch("/api/jobs/{job_id}", self._handle_update_job)
self._app.router.add_delete("/api/jobs/{job_id}", self._handle_delete_job)
self._app.router.add_post("/api/jobs/{job_id}/pause", self._handle_pause_job)
self._app.router.add_post("/api/jobs/{job_id}/resume", self._handle_resume_job)
self._app.router.add_post("/api/jobs/{job_id}/run", self._handle_run_job)
# Structured event streaming
self._app.router.add_post("/v1/runs", self._handle_runs)
self._app.router.add_get("/v1/runs/{run_id}", self._handle_get_run)
self._app.router.add_get("/v1/runs/{run_id}/events", self._handle_run_events)
self._app.router.add_post("/v1/runs/{run_id}/approval", self._handle_run_approval)
self._app.router.add_post("/v1/runs/{run_id}/stop", self._handle_stop_run)
```

Key takeaway: routes are registered directly via `self._app.router` with method + path + handler. The `api_server.py` file lives at `gateway/platforms/api_server.py` in the hermes-agent repo.

### The Plugin System Gap for HTTP Routes

The Hermes plugin system (`hermes_cli/plugins.py`) supports registering:
- **Tools** (`ctx.register_tool()`)
- **CLI commands** (`ctx.register_cli_command()`)
- **Slash commands** (`ctx.register_command()`)
- **Platform adapters** (`ctx.register_platform()`)
- **Lifecycle hooks** (`ctx.register_hook()`)
- **Skills** (`ctx.register_skill()`)

**There is NO `register_api_route()` method.** As of 2026-05-15, the only way to add custom HTTP routes to the gateway is to modify `api_server.py` directly. The lifecycle hooks (`VALID_HOOKS`) include `pre_gateway_dispatch`, `on_session_start`, etc., but none provide access to the aiohttp route table.

**Three paths to close this gap:**
1. Add `register_api_route()` to `PluginContext` in `plugins.py` (+ core change), then create a plugin
2. Add the route directly to `api_server.py` (minimal, direct)
3. Create a standalone platform adapter plugin that runs its own HTTP server on a different port

### Kanban Data from the CLI

The kanban data can be read from the CLI as JSON:
```bash
hermes kanban list --json
```

Task shape:
```json
{
  "id": "t_abc12345",
  "title": "task title",
  "body": null,
  "assignee": "architect",
  "status": "done",
  "priority": 0,
  "tenant": null,
  "workspace_kind": "scratch",
  "workspace_path": "~/.hermes/kanban/workspaces/t_abc12345",
  "created_by": "user",
  "created_at": 1778523771,
  "started_at": 1778523809,
  "completed_at": 1778526432,
  "result": null,
  "skills": [],
  "max_retries": null
}
```

The bridge expects `{ tasks: [...], updated_at }`. The kanban data maps cleanly — `id` → `task_id`, `title` → `title`, `assignee` → `assignee`, `status` → `status`.

### Gateway Health Check

```bash
curl http://127.0.0.1:8642/health
# {"status": "ok", "platform": "hermes-agent"}
```

Confirmed running: Python process from the hermes-agent venv, listening on `127.0.0.1:8642`.
