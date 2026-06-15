---
name: native-mcp
description: "MCP client: connect servers, register tools (stdio/HTTP)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [MCP, Tools, Integrations]
    related_skills: [mcporter]
---

# Native MCP Client

Hermes Agent has a built-in MCP client that connects to MCP servers at startup, discovers their tools, and makes them available as first-class tools the agent can call directly. No bridge CLI needed -- tools from MCP servers appear alongside built-in tools like `terminal`, `read_file`, etc.

## When to Use

Use this whenever you want to:
- Connect to MCP servers and use their tools from within Hermes Agent
- Add external capabilities (filesystem access, GitHub, databases, APIs) via MCP
- Run local stdio-based MCP servers (npx, uvx, or any command)
- Connect to remote HTTP/StreamableHTTP MCP servers
- Have MCP tools auto-discovered and available in every conversation

For ad-hoc, one-off MCP tool calls from the terminal without configuring anything, see the `mcporter` skill instead.

## Prerequisites

- **mcp Python package** -- optional dependency; install with `pip install mcp`. If not installed, MCP support is silently disabled.
- **Node.js** -- required for `npx`-based MCP servers (most community servers)
- **uv** -- required for `uvx`-based MCP servers (Python-based servers)

Install the MCP SDK:

```bash
pip install mcp
# or, if using uv:
uv pip install mcp
```

## Quick Start

Add MCP servers to `~/.hermes/config.yaml` under the `mcp_servers` key:

> **Profile note:** If using a non-default Hermes profile, `load_config()` reads from `~/.hermes/profiles/<profile>/config.yaml`, not the global file. See [Profile Isolation Pitfall](#profile-isolation-pitfall) below before editing — adding to the wrong file silently does nothing.

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
```

Restart Hermes Agent. On startup it will:
1. Connect to the server
2. Discover available tools
3. Register them with the prefix `mcp_time_*`
4. Inject them into all platform toolsets

You can then use the tools naturally -- just ask the agent to get the current time.

## Configuration Reference

Each entry under `mcp_servers` is a server name mapped to its config. There are two transport types: **stdio** (command-based) and **HTTP** (url-based).

### Stdio Transport (command + args)

```yaml
mcp_servers:
  server_name:
    command: "npx"             # (required) executable to run
    args: ["-y", "pkg-name"]   # (optional) command arguments, default: []
    env:                       # (optional) environment variables for the subprocess
      SOME_API_KEY: "value"
    timeout: 120               # (optional) per-tool-call timeout in seconds, default: 120
    connect_timeout: 60        # (optional) initial connection timeout in seconds, default: 60
```

### HTTP Transport (url)

```yaml
mcp_servers:
  server_name:
    url: "https://my-server.example.com/mcp"   # (required) server URL
    headers:                                     # (optional) HTTP headers
      Authorization: "Bearer sk-..."
    timeout: 180               # (optional) per-tool-call timeout in seconds, default: 120
    connect_timeout: 60        # (optional) initial connection timeout in seconds, default: 60
```

### All Config Options

| Option            | Type   | Default | Description                                       |
|-------------------|--------|---------|---------------------------------------------------|
| `command`         | string | --      | Executable to run (stdio transport, required)     |
| `args`            | list   | `[]`    | Arguments passed to the command                   |
| `env`             | dict   | `{}`    | Extra environment variables for the subprocess    |
| `url`             | string | --      | Server URL (HTTP transport, required)             |
| `headers`         | dict   | `{}`    | HTTP headers sent with every request              |
| `timeout`         | int    | `120`   | Per-tool-call timeout in seconds                  |
| `connect_timeout` | int    | `60`    | Timeout for initial connection and discovery      |

Note: A server config must have either `command` (stdio) or `url` (HTTP), not both.

## How It Works

### Startup Discovery

When Hermes Agent starts, `discover_mcp_tools()` is called during tool initialization:

1. Reads `mcp_servers` from `~/.hermes/config.yaml`
2. For each server, spawns a connection in a dedicated background event loop
3. Initializes the MCP session and calls `list_tools()` to discover available tools
4. Registers each tool in the Hermes tool registry

### Tool Naming Convention

MCP tools are registered with the naming pattern:

```
mcp_{server_name}_{tool_name}
```

Hyphens and dots in names are replaced with underscores for LLM API compatibility.

Examples:
- Server `filesystem`, tool `read_file` → `mcp_filesystem_read_file`
- Server `github`, tool `list-issues` → `mcp_github_list_issues`
- Server `my-api`, tool `fetch.data` → `mcp_my_api_fetch_data`

### Auto-Injection

After discovery, MCP tools are automatically injected into all `hermes-*` platform toolsets (CLI, Discord, Telegram, etc.). This means MCP tools are available in every conversation without any additional configuration.

### Connection Lifecycle

- Each server runs as a long-lived asyncio Task in a background daemon thread
- Connections persist for the lifetime of the agent process
- If a connection drops, automatic reconnection with exponential backoff kicks in (up to 5 retries, max 60s backoff)
- On agent shutdown, all connections are gracefully closed

### Idempotency

`discover_mcp_tools()` is idempotent -- calling it multiple times only connects to servers that aren't already connected. Failed servers are retried on subsequent calls.

## Transport Types

### Stdio Transport

The most common transport. Hermes launches the MCP server as a subprocess and communicates over stdin/stdout.

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
```

The subprocess inherits a **filtered** environment (see Security section below) plus any variables you specify in `env`.

### HTTP / StreamableHTTP Transport

For remote or shared MCP servers. Requires the `mcp` package to include HTTP client support (`mcp.client.streamable_http`).

```yaml
mcp_servers:
  remote_api:
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer sk-..."
```

If HTTP support is not available in your installed `mcp` version, the server will fail with an ImportError and other servers will continue normally.

## Security

### Environment Variable Filtering

For stdio servers, Hermes does NOT pass your full shell environment to MCP subprocesses. Only safe baseline variables are inherited:

- `PATH`, `HOME`, `USER`, `LANG`, `LC_ALL`, `TERM`, `SHELL`, `TMPDIR`
- Any `XDG_*` variables

All other environment variables (API keys, tokens, secrets) are excluded unless you explicitly add them via the `env` config key. This prevents accidental credential leakage to untrusted MCP servers.

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      # Only this token is passed to the subprocess
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."
```

### Credential Stripping in Error Messages

If an MCP tool call fails, any credential-like patterns in the error message are automatically redacted before being shown to the LLM. This covers:

- GitHub PATs (`ghp_...`)
- OpenAI-style keys (`sk-...`)
- Bearer tokens
- Generic `token=`, `key=`, `API_KEY=`, `password=`, `secret=` patterns

## Troubleshooting

### "MCP SDK not available -- skipping MCP tool discovery"

The `mcp` Python package is not installed. Install it:

```bash
pip install mcp
```

### "No MCP servers configured"

No `mcp_servers` key in `~/.hermes/config.yaml`, or it's empty. Add at least one server.

### "Failed to connect to MCP server 'X'"

Common causes:
- **Command not found**: The `command` binary isn't on PATH. Ensure `npx`, `uvx`, or the relevant command is installed.
- **Package not found**: For npx servers, the npm package may not exist or may need `-y` in args to auto-install.
- **Timeout**: The server took too long to start. Increase `connect_timeout`.
- **Port conflict**: For HTTP servers, the URL may be unreachable.

### "MCP server 'X' requires HTTP transport but mcp.client.streamable_http is not available"

Your `mcp` package version doesn't include HTTP client support. Upgrade:

```bash
pip install --upgrade mcp
```

### Tools not appearing

- Check that the server is listed under `mcp_servers` (not `mcp` or `servers`)
- Ensure the YAML indentation is correct
- Look at Hermes Agent startup logs for connection messages
- Tool names are prefixed with `mcp_{server}_{tool}` -- look for that pattern

### Connection keeps dropping

The client retries up to 5 times with exponential backoff (1s, 2s, 4s, 8s, 16s, capped at 60s). If the server is fundamentally unreachable, it gives up after 5 attempts. Check the server process and network connectivity.

## Systematic Health Check

When an MCP server is configured but not working as expected, verify each layer from bottom to top. Stop at the first failed layer:

```bash
# Activate venv first
source <venv>/bin/activate

# Layer 1 — Package installed
pip3 show <package-name>
# → If missing, install it

# Layer 2 — Binary on disk  
ls -la $(which <server-binary>)
# → If missing, check install path and PATH

# Layer 3 — Config entry exists
grep -A 3 <server-name> ~/.hermes/config.yaml
# → If empty, check profile isolation — edit the right config file
#   (see Profile Isolation Pitfall section)

# Layer 4 — Hermes recognizes it
hermes mcp list
# → Should show <server-name> with ✓ enabled
# → If empty/absent, agent hasn't loaded config — restart needed

# Layer 5 — Connection works
hermes mcp test <server-name>
# → Should show ✓ Connected (<time>) and ✓ Tools discovered: N
# → If fails, check stderr/logs for why the subprocess failed
```

For profile-isolated setups, the config path may differ. Run the diagnosis from the Profile Isolation Pitfall section above to confirm which file to edit.

### Direct MCP Server Probing (Bypassing Hermes)

When `hermes mcp test` fails and you need to isolate whether the problem is in Hermes' middleware vs the MCP server process itself, probe the binary directly via stdio JSON-RPC:

```bash
# Check if the server binary starts and responds at all
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | /path/to/mcp-binary 2>/dev/null | head -20
```

If this returns a valid JSON-RPC response, the server binary is healthy — the issue is in Hermes' connection layer (config path, env filtering, timeout). If it hangs or errors, the server binary itself is broken.

To list tools without going through Hermes' middleware:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | /path/to/mcp-binary 2>/dev/null
```

This returns the raw tool schema JSON. Useful for verifying tool discovery independently before debugging Hermes' side. Example with iknowkungfu:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | ~/.hermes/hermes-agent/venv/bin/iknowkungfu-mcp 2>/dev/null
```

## Examples

### Blender 3D Modeling (uvx)

Connects Hermes to a running Blender instance for 3D scene manipulation, modeling, materials, and asset generation:

```yaml
mcp_servers:
  blender:
    command: "uvx"
    args: ["blender-mcp"]
```

Requires the Blender addon from [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) installed and the socket server active in Blender. Tools register as `mcp_blender_*`. See the `blender-automation` skill for full setup and usage.

### Time Server (uvx)

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
```

Registers tools like `mcp_time_get_current_time`.

### Filesystem Server (npx)

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/documents"]
    timeout: 30
```

Registers tools like `mcp_filesystem_read_file`, `mcp_filesystem_write_file`, `mcp_filesystem_list_directory`.

### GitHub Server with Authentication

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxxxxxxxxxxxxxxxxxxx"
    timeout: 60
```

Registers tools like `mcp_github_list_issues`, `mcp_github_create_pull_request`, etc.

### Remote HTTP Server

```yaml
mcp_servers:
  company_api:
    url: "https://mcp.mycompany.com/v1/mcp"
    headers:
      Authorization: "Bearer sk-xxxxxxxxxxxxxxxxxxxx"
      X-Team-Id: "engineering"
    timeout: 180
    connect_timeout: 30
```

### Multiple Servers

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]

  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]

  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxxxxxxxxxxxxxxxxxxx"

  company_api:
    url: "https://mcp.internal.company.com/mcp"
    headers:
      Authorization: "Bearer sk-xxxxxxxxxxxxxxxxxxxx"
    timeout: 300
```

All tools from all servers are registered and available simultaneously. Each server's tools are prefixed with its name to avoid collisions.

### CodeGraph (Code Intelligence MCP)

Adds code intelligence tools — symbol search, call graphs, impact analysis, and semantic context — as MCP tools. Each project gets its own `.codegraph/` index.

```bash
npm install -g codegraph
cd /path/to/project && codegraph init && codegraph index
```

```yaml
mcp_servers:
  codegraph:
    command: /absolute/path/to/codegraph   # use `which codegraph` to find
    args: ["serve", "--mcp"]
    timeout: 120
    connect_timeout: 60
    enabled: true
```

Tools register as `mcp_codegraph_*`. See `references/codegraph-setup.md` for CLI quirks, pitfall details, and direct-usage patterns.

### Installing a Skill Registry (iknowkungfu)

For package managers with their own registry (e.g., iknowkungfu for AI agent skills), install the package and add its MCP server:

```bash
pip install iknowkungfu
```

```yaml
mcp_servers:
  iknowkungfu:
    command: iknowkungfu-mcp
    enabled: true
```

The CLI (`kfu`) remains available separately for one-off operations:
```bash
kfu update
kfu search "term" --limit 5
kfu install author/skill-name
```

Tools are registered with `mcp_iknowkungfu_` prefix after Hermes restart.

See `references/iknowkungfu-setup.md` for session-specific installation and verification steps.

## Sampling (Server-Initiated LLM Requests)

Hermes supports MCP's `sampling/createMessage` capability — MCP servers can request LLM completions through the agent during tool execution. This enables agent-in-the-loop workflows (data analysis, content generation, decision-making).

Sampling is **enabled by default**. Configure per server:

```yaml
mcp_servers:
  my_server:
    command: "npx"
    args: ["-y", "my-mcp-server"]
    sampling:
      enabled: true           # default: true
      model: "gemini-3-flash" # model override (optional)
      max_tokens_cap: 4096    # max tokens per request
      timeout: 30             # LLM call timeout (seconds)
      max_rpm: 10             # max requests per minute
      allowed_models: []      # model whitelist (empty = all)
      max_tool_rounds: 5      # tool loop limit (0 = disable)
      log_level: "info"       # audit verbosity
```

Servers can also include `tools` in sampling requests for multi-turn tool-augmented workflows. The `max_tool_rounds` config prevents infinite tool loops. Per-server audit metrics (requests, errors, tokens, tool use count) are tracked via `get_mcp_status()`.

Disable sampling for untrusted servers with `sampling: { enabled: false }`.

## Notes

- MCP tools are called synchronously from the agent's perspective but run asynchronously on a dedicated background event loop
- Tool results are returned as JSON with either `{"result": "..."}` or `{"error": "..."}`
- The native MCP client is independent of `mcporter` -- you can use both simultaneously
- Server connections are persistent and shared across all conversations in the same agent process
- Adding or removing servers requires restarting the agent (no hot-reload currently)

## Profile Isolation Pitfall

When Hermes has a non-default profile active, `load_config()` reads config via `get_hermes_home()`, which checks `HERMES_HOME` env var before falling back to `Path.home() / ".hermes"`. Under profile isolation with `HERMES_HOME` explicitly set, the effective config path is **`~/.hermes/profiles/<profile>/config.yaml`**, NOT the HOME-scoped config at `~/.hermes/profiles/<profile>/home/.hermes/config.yaml`.

**Correct location (when HERMES_HOME is set):**
```yaml
# ~/.hermes/profiles/<profile>/config.yaml
mcp_servers:
  server_name:
    command: /absolute/path/to/mcp-binary
    enabled: true
```

**If HERMES_HOME is NOT set but HOME is overridden** (non-standard setup), `get_hermes_home()` falls back to `Path.home() / ".hermes"`, which resolves relative to the overridden HOME. In that case the path would be `~/.hermes/profiles/<profile>/home/.hermes/config.yaml`. When in doubt, run the diagnosis below.

**Symptoms of wrong location:**
- `load_config()` returns `{}` for `mcp_servers` despite the entry existing in the global-level config
- `hermes mcp list` reports "No MCP servers configured"
- No `mcp_*_` tools appear after gateway restart
- Gateway logs show MCP discovery returning empty

**Diagnosis:**
```bash
source ~/.hermes/hermes-agent/venv/bin/activate
python3 -c "
from hermes_cli.config import load_config, get_config_path
from pathlib import Path
c = load_config()
print('Config path:', get_config_path())
print('HOME:', Path.home())
print('HERMES_HOME:', '$(echo \$HERMES_HOME)')
print('Has mcp_servers:', 'mcp_servers' in c)
if 'mcp_servers' in c:
    print('MCP servers:', list(c['mcp_servers'].keys()))
"
```

The config path in the output tells you exactly which file to edit. If it points to the profile config (`profiles/<name>/config.yaml`), add `mcp_servers` there. If it points to the HOME-scoped config (`profiles/<name>/home/.hermes/config.yaml`), add it there instead.
