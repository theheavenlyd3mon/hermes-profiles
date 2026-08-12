# Standalone File-Based UE Bridge

A minimal bridge that lets a standalone Python agent process send requests to a
running Unreal Editor.

## Why this shape

- No external MCP server or HTTP listener required.
- Both sides only need the ability to read/write a single JSON file and poll it.
- Easy to stub for off-PC development: a stub bridge returns canned responses
  without any editor present.

## Protocol

File: `bridge/bridge.json`

```jsonc
{
  "state": "pending",      // pending | processing | done
  "direction": "agent",    // agent → editor
  "request_id": "uuid",
  "method": "editor_command",
  "params": {"command": "py ..."},
  "result": null,
  "error": null
}
```

## Lifecycle

1. Agent writes `state: pending` and a request.
2. Editor-side `ue_bridge_listener.py` sees pending, sets `state: processing`,
   executes the request.
3. Editor-side writes `state: done` with the result.
4. Agent reads result, then clears the file for the next request.

## Agent-side implementation

```python
class Bridge:
    def request(self, method: str, params: dict) -> dict:
        if self.mode == "stub":
            return self._stub_response(method, params)
        # write request, poll until done, return result
```

## Editor-side implementation

Run this inside the UE editor via `File > Execute Python Script`:

```python
import unreal
# poll bridge.json, dispatch to console commands / Blueprint compile
```

See the harness repo for a complete `ue_bridge_listener.py`.

## Supported requests

- `editor_command` — executes a console command in the editor world.
- `compile_blueprints` — triggers Blueprint compilation.
- `is_editor_running` — health check.
