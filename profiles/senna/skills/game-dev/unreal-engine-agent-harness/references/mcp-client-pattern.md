# MCP Client Pattern for UE Agent Harness

Implementation from Task 7 of the evolution plan (2026-07-16). Adds optional MCP support behind a feature flag.

## Files

- `tools/mcp_client.py` — MCPClient class with optional import, discover(), and call()
- `agent.py` — wiring in Agent.__init__ (reads mcp_enabled, mcp_servers from config)
- `test_stub.py` — test_mcp_disabled_by_default

## Design

1. **Optional import** — `mcp` package is imported inside a try/except; if unavailable, `_MCP_AVAILABLE = False`.
2. **Feature flag** — `mcp_enabled` and `mcp_servers` read from config via `getattr(config, ..., default)` so they work before the Config dataclass is updated.
3. **MCPClient.discover()** — connects to each configured stdio server, lists tools, returns flat map `tool_name -> {server, schema}`.
4. **MCPClient.call(tool_name, args)** — re-establishes session, calls tool, returns `{"result": [...]}` or `{"error": ...}`.
5. **Agent wiring** — in `__init__`, if `mcp_enabled`:
   - Instantiate MCPClient
   - Discover tools
   - Add each tool to `self.tools` as lambda: `self.mcp_client.call(name, args)`
   - Store schemas in `self.mcp_tool_schemas` list
6. **Schema merging** — `_tool_schemas()` returns `schemas_from_registry(self.tools) + self.mcp_tool_schemas`.

## Test

```python
def test_mcp_disabled_by_default(tmpdir: Path):
    config = make_test_config(tmpdir)
    agent = Agent(config)
    assert agent.mcp_client is None
```

## Config example (config.yaml)

```yaml
mcp:
  enabled: false
  servers:
    filesystem:
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
```

## Pitfalls

- **Same-file parallel edits**: `agent.py` and `test_stub.py` are touched by multiple evolution tasks (6, 7, 9, 11). Serialize these tasks or give each a disjoint region.
- **Sibling agents**: when running with subagents, they may race on the same files. Coordinate or run sequentially.
- **Missing mcp package**: `_MCP_AVAILABLE = False` causes discover to return {} and call to return `{"error": "MCP package not installed."}` — correct fallback behavior.
- **Schema drift**: since schemas come from `discover()` at runtime, they cannot be generated at import time. The `mcp_tool_schemas` list bridges this.