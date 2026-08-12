# Mnemosyne MCP Server Reference

## Package

- **PyPI:** `mnemosyne-memory` (v3.3.0 as of 2026-06-09)
- **MCP extra:** `pip install "mnemosyne-memory[mcp]"` — pulls `mcp` SDK deps
- **Source:** https://github.com/AxDSan/mnemosyne

## Command

```bash
mnemosyne mcp                          # stdio transport (default)
mnemosyne mcp --transport sse --port 8080   # SSE on loopback
mnemosyne mcp --bank project_a         # specific memory bank
```

## Transport Modes

| Transport | Auth | Use case |
|-----------|------|----------|
| stdio (default) | None needed | Hermes, Claude Desktop, local tools |
| SSE loopback | None needed | Local web clients |
| SSE LAN | Bearer token required | Cross-machine access |

**SSE security:** Binding to non-loopback (0.0.0.0, LAN IP) requires `MNEMOSYNE_MCP_TOKEN` env var. Server refuses to start without it.

## Hermes Config (stdio)

```yaml
mcp_servers:
  mnemosyne:
    command: mnemosyne
    args: ["mcp"]
    enabled: true
    env:
      MNEMOSYNE_DB_PATH: "C:\\Users\\hermes-dev\\.hermes\\mnemosyne.db"
```

## Available MCP Tools

Tools register as `mcp_mnemosyne_*` in Hermes:

| MCP Tool | Description |
|----------|-------------|
| `mcp_mnemosyne_remember` | Store a memory (content, source, importance, metadata) |
| `mcp_mnemosyne_recall` | Search memories (query, max_results, filters) |
| `mcp_mnemosyne_stats` | Memory system statistics |
| `mcp_mnemosyne_forget` | Delete a specific memory |
| `mcp_mnemosyne_export` | Export all memories |

## Native vs MCP Integration

| Aspect | Native (Mac) | MCP Server (Windows) |
|--------|-------------|---------------------|
| Install | `pip install mnemosyne-memory` | `pip install "mnemosyne-memory[mcp]"` |
| Tool prefix | `mnemosyne_*` (bare) | `mcp_mnemosyne_*` (prefixed) |
| Config | Auto-discovered via entry point | `mcp_servers` in profile config.yaml |
| DB location | `~/.hermes/mnemosyne.db` (default) | `MNEMOSYNE_DB_PATH` env var |

## Pitfalls

- **Missing `[mcp]` extra:** `pip install mnemosyne-memory` without `[mcp]` installs the core but not MCP deps. `mnemosyne mcp` fails with "MCP not installed. Run: pip install mnemosyne-memory[mcp]".
- **Profile isolation:** MCP servers must be in the profile's config.yaml, not the global one. See `hermes-mcp-profile-isolation` skill.
- **DB path on Windows:** Use double backslashes or forward slashes in YAML. `C:\Users\hermes-dev\.hermes\mnemosyne.db` works; single backslashes may escape incorrectly.
