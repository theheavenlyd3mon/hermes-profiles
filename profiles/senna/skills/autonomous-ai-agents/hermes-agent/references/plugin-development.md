# Hermes Plugin Development — Reference

## Plugin Anatomy

Every user plugin lives at `~/.hermes/plugins/<name>/` and requires two files:

```
~/.hermes/plugins/<name>/
├── plugin.yaml          # Manifest — name, version, kind, dependencies
└── __init__.py          # Entry point — must expose register(ctx)
```

### plugin.yaml

```yaml
name: my-plugin
version: 1.0.0
description: Does X
author: Your Name
kind: standalone                    # standalone | backend | exclusive | platform | model-provider
requires_env: []                    # API keys the plugin needs
provides_tools: []                  # Tool names (informational)
provides_hooks: []                  # Hook names (informational)
```

Valid kinds:
- `standalone` (default) — tools/hooks of its own; opt-in via `plugins.enabled`
- `backend` — provides *only* a backend component; auto-enabled when any frontend plugin needs it
- `exclusive` — a non-standalone, non-backend plugin that other plugins depend on; auto-enabled
- `platform` — gateway messaging platform adapter (IRC, etc.)
- `model-provider` — inference backend plugin

### __init__.py

Minimal skeleton:

```python
import logging
logger = logging.getLogger(__name__)

def register(ctx):
    """Called by the Hermes plugin loader at startup."""
    logger.info("Registered plugin: %s", ctx.manifest.name)
```

## PluginContext API

The `ctx` object passed to `register()` exposes these registration methods:

| Method | Purpose |
|---|---|
| `ctx.register_tool(name, toolset, schema, handler, ...)` | Register a tool function |
| `ctx.register_hook(hook_name, callback)` | Lifecycle hook (see below) |
| `ctx.register_cli_command(name, help, setup_fn, handler_fn)` | CLI subcommand (`hermes mycmd`) |
| `ctx.register_command(name, handler, description, args_hint)` | Slash command (`/mycmd`) |
| `ctx.register_platform(name, label, adapter_factory, check_fn, ...)` | Gateway platform adapter |
| `ctx.register_skill(name, path, description)` | Read-only skill |

### Available Lifecycle Hooks

```python
VALID_HOOKS = {
    "pre_tool_call", "post_tool_call",
    "transform_terminal_output", "transform_tool_result", "transform_llm_output",
    "pre_llm_call", "post_llm_call",
    "pre_api_request", "post_api_request",
    "on_session_start", "on_session_end", "on_session_finalize", "on_session_reset",
    "subagent_stop",
    "pre_gateway_dispatch",
    "pre_approval_request", "post_approval_response",
}
```

There is currently **no `register_api_route()` hook** — plugins cannot add HTTP routes to the existing gateway API server without modifying core code.

## Standalone HTTP Server Pattern

Since the plugin system has no HTTP route hook, the cleanest approach is a **standalone aiohttp server in a background thread**. The plugin starts its own server on a dedicated port.

### Pattern

```python
import asyncio
import threading
from aiohttp import web

_HOST = "127.0.0.1"
_PORT = 8643
_server_token = None
_thread_token = None


async def _handle_endpoint(request):
    return web.json_response({"status": "ok"})


def _run_server():
    """Run in a background thread. Use AppRunner with handle_signals=False
    to avoid 'set_wakeup_fd only works in main thread' errors."""
    app = web.Application()
    app.router.add_get("/api/v1/data", _handle_endpoint)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    runner = web.AppRunner(app, handle_signals=False)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, host=_HOST, port=_PORT)
    loop.run_until_complete(site.start())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(runner.cleanup())
        loop.close()


def start():
    global _server_token, _thread_token
    if _server_token is not None:
        return
    _thread_token = threading.Thread(target=_run_server, daemon=True)
    _thread_token.start()
    _server_token = True


def register(ctx):
    try:
        import aiohttp
    except ImportError:
        logger.error("aiohttp not available — skipping")
        return
    start()
```

### Key details

- **`handle_signals=False`** — critical. `aiohttp.web.run_app()` sets signal handlers (SIGINT, SIGTERM) which only works in the main thread. Use `AppRunner(handle_signals=False)` + `TCPSite` instead.
- **`daemon=True`** — thread exits when the main process does. No clean shutdown needed.
- **CORS** — add headers in each handler if the server is polled from a browser context (e.g., `Access-Control-Allow-Origin: *`).

## Enabling a Plugin

Plugins are opt-in. Add to `~/.hermes/config.yaml`:

```yaml
plugins:
  enabled:
    - my-plugin
```

Then restart the Hermes gateway for the plugin to load. Verify with:

```bash
hermes plugins list    # Should show my-plugin as enabled
```

## Kanban Data Access

Plugin code can read kanban tasks directly:

```python
from hermes_cli import kanban_db as kb

conn = kb.connect()                                    # Opens the default board
tasks = kb.list_tasks(conn, include_archived=False)     # Returns list of Task objects

# Task objects have: id, title, body, assignee, status, priority,
#   created_by, created_at, started_at, completed_at,
#   workspace_kind, workspace_path, tenant, result, skills, max_retries
```

For JSON serialization, map `task.id` → `"task_id"` (the MagicMirror client modules expect `task_id`, not `id`).

## Pitfalls

1. **No HTTP route hook exists** — you MUST run a separate server or modify `api_server.py` core code. Running a separate server on a different port is the preferred plugin-safe approach.
2. **`handle_signals=False` is required** when running aiohttp from a background thread. Forgetting this gives `RuntimeError: set_wakeup_fd only works in main thread`.
3. **Plugin discovery** — the plugin system scans `~/.hermes/plugins/<name>/`, bundled `<repo>/plugins/<name>/`, project `./.hermes/plugins/<name>/`, and pip entry points. Later sources override earlier ones on name collision.
4. **Enablement check** — `_get_enabled_plugins()` reads `plugins.enabled` list from `config.yaml`. If the key is missing entirely, no user plugins load. If it's malformed, the function returns `None` which callers treat as "nothing enabled yet".
5. **Profile vs root** — user plugins in `~/.hermes/plugins/` (root) are shared across all profiles. Plugins scoped to a specific profile live in `~/.hermes/profiles/<name>/plugins/`.
