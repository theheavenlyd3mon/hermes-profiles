# Notion MCP Setup

Notion provides a **hosted MCP server** (HTTP/StreamableHTTP transport) that gives AI assistants full workspace access — read/write pages, databases, comments, search — via OAuth.

This is an alternative to the raw REST API approach. Best when:
- You want multiple MCP-compatible agents (Claude Code, Cursor, ChatGPT, Hermes) to access Notion
- You don't want to manage API keys per agent
- Your agent already uses Hermes native-mcp

## Prerequisites

- `pip install mcp` — MCP SDK with HTTP transport support
- A Notion workspace with admin access
- The `native-mcp` skill is already available in Hermes

## Setup (Notion Side)

1. Go to **notion.so/my-integrations**
2. Create or select an integration
3. Under **MCP Server**, enable the connection
4. Complete the OAuth flow to authorize your workspace
5. Notion provides you with an MCP server URL and authentication token

## Configuration in Hermes

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  notion:
    url: "https://mcp.notion.com/v1"  # URL from Notion's MCP setup
    headers:
      Authorization: "Bearer <oauth-token-from-notion>"
    timeout: 180
```

After restarting Hermes, tools appear as `mcp_notion_*` in the tool registry and are available in every conversation.

## Supported Tools (from Notion MCP)

Notion's MCP server provides tools for:

- **Create/read/update pages** — Full page CRUD including properties
- **Search workspace content** — Across all shared pages and databases
- **Manage databases** — Query, filter, sort, update schemas
- **Read/write comments** — Page comments and inline comments
- **File operations** — Upload and attach files
- **Markdown content** — Import/export page content as enhanced markdown

## Compatible Clients

Notion MCP works with these AI assistants out of the box:
- **Claude Code** (Anthropic)
- **Cursor** (via custom agent integration)
- **VS Code** (via MCP extensions)
- **ChatGPT** (via MCP)
- **Hermes Agent** (via native-mcp)

## REST vs MCP: When to Use Which

| Factor | REST via curl | Notion MCP |
|--------|---------------|------------|
| Setup complexity | API key only | OAuth flow required |
| Tool prefix | none (direct curl) | `mcp_notion_*` |
| Access scope | Databases shared with integration | Full workspace (OAuth-scoped) |
| Agent independence | Each agent needs the key | Shared via MCP server |
| Performance | Direct, no middleware | Via MCP protocol |
| Multiple agent types | Must set up per agent | Works with any MCP client |

**Recommendation:** For Hermes-specific tooling, use REST via curl (simpler, no OAuth). For multi-agent setups where Claude Code, Cursor, or ChatGPT also need Notion access, set up the MCP server once and share it.

## How It Works

Notion's MCP server is fully hosted — you don't run anything locally. The flow:

1. Your MCP client (Hermes, Claude Code, etc.) connects to Notion's MCP server URL
2. Notion handles authentication via OAuth
3. The server exposes tools (create_page, search, query_database, etc.)
4. Your agent calls these tools as if they were built-in

Notion hosts both the MCP server and the underlying API — your tool only contains an MCP client.

## Security

- OAuth tokens are scoped to the workspace and permissions the user authorized
- Tokens can be revoked from the Notion integrations page
- Hermes' native-mcp filters environment variables for stdio servers (not relevant for HTTP transport, but the token in config.yaml should be kept secure)

## Notes

- The MCP server URL and exact tool names come from Notion's developer portal after OAuth setup
- If `mcp.client.streamable_http` is not available in your `mcp` package version, upgrade: `pip install --upgrade mcp`
- The External Agents API (alpha) is a different feature — that embeds your agent *inside* Notion, while MCP gives agents *access to* Notion
