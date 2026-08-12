# Kanban API Plugin — Implementation Reference

> Plugin at `~/.hermes/plugins/kanban-api/` that serves Hermes kanban data via HTTP to the HermesMirror bridge.

## Why a plugin instead of modifying the gateway

- The Hermes plugin system (`hermes_cli/plugins.py`) has NO `register_api_route()` method as of 2026-05-15
- Adding routes to `api_server.py` directly is overwritten by `hermes update`
- The plugin lives at `~/.hermes/plugins/<name>/` — survives updates completely untouched
- The plugin only needs the venv's aiohttp (already available via the Hermes gateway dep)

## File structure

```
~/.hermes/plugins/kanban-api/
├── plugin.yaml        # manifest
└── __init__.py        # register(ctx) + server logic
```

## plugin.yaml

```yaml
name: kanban-api
version: 1.0.0
description: Serves kanban board data via HTTP API for HermesMirror bridge
author: Senna
kind: standalone
requires_env: []
provides_tools: []
provides_hooks: []
```

## __init__.py — key patterns

### register() entry point

```python
def register(ctx) -> None:
    """Plugin entry point — called by the Hermes plugin loader."""
    try:
        import aiohttp
    except ImportError:
        logger.error("kanban-api: aiohttp not available — skipping")
        return
    start()
```

### Thread-safe aiohttp server startup

**CRITICAL:** `aiohttp.web.run_app()` sets up signal handlers (SIGINT, SIGTERM), which crash with `RuntimeError: set_wakeup_fd only works in main thread of the main interpreter` when called from a background thread.

Use the low-level `AppRunner` + `TCPSite` API with `handle_signals=False`:

```python
def _run_server() -> None:
    import asyncio
    import aiohttp.web

    app = aiohttp.web.Application()
    app.router.add_get("/health", _handle_health)
    app.router.add_get("/api/kanban/board", _handle_board)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    runner = aiohttp.web.AppRunner(app, handle_signals=False)
    loop.run_until_complete(runner.setup())
    site = aiohttp.web.TCPSite(runner, host="127.0.0.1", port=8643)
    loop.run_until_complete(site.start())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(runner.cleanup())
        loop.close()
```

Start the background thread:

```python
_thread_instance = threading.Thread(target=_run_server, daemon=True, name="kanban-api")
_thread_instance.start()
```

### Reading kanban data

Use `hermes_cli.kanban_db` which is importable from within the hermes-agent venv:

```python
from hermes_cli import kanban_db as kb

conn = kb.connect()                          # opens ~/.hermes/kanban.db
tasks = kb.list_tasks(conn, include_archived=False)
```

The `Task` object fields: `id`, `title`, `body`, `assignee`, `status`, `priority`, `created_by`, `created_at`, `started_at`, `completed_at`, `workspace_kind`, `workspace_path`, `tenant`, `result`, `skills`, `max_retries`.

Bridge expects the shape `{ tasks: [...], updated_at }` where each task uses `task_id` (not `id`):

```python
def _serialise_task(task) -> dict:
    return {
        "task_id": task.id,
        "title": task.title,
        "body": task.body,
        "assignee": task.assignee,
        "status": task.status,
        "priority": task.priority,
        "created_by": task.created_by,
        "created_at": task.created_at,
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "workspace_kind": task.workspace_kind,
        "workspace_path": task.workspace_path,
        "tenant": task.tenant,
        "result": task.result,
    }
```

### CORS

The bridge connects from `localhost:8080` (MagicMirror), so the kanban API endpoint should allow cross-origin requests:

```python
headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
}
```

## Enabling the plugin

Add to `~/.hermes/config.yaml`:

```yaml
plugins:
  enabled:
    - kanban-api
```

Then restart the Hermes gateway. The plugin auto-starts when the `register()` function is called during plugin loading.

## Verification

```bash
curl http://127.0.0.1:8643/health
# {"status": "ok", "service": "kanban-api"}

curl http://127.0.0.1:8643/api/kanban/board
# {"tasks": [...], "updated_at": 1747340000}
```

## Independent startup (without full gateway)

```bash
cd ~/.hermes/hermes-agent && source venv/bin/activate
python3 -c "
import sys; sys.path.insert(0, '.')
import importlib.util
spec = importlib.util.spec_from_file_location('kanban_api',
    '~/.hermes/plugins/kanban-api/__init__.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.start()
import time; time.sleep(999999)
"
```

This starts just the kanban API server without the full Hermes gateway.