# CLI vs MCP: Token Efficiency Tradeoffs

> Source: Jannik Reinhard (Feb 2026) — "Why CLI Tools Are Beating MCP for AI Agents"
> URL: https://jannikreinhard.com/2026/02/22/why-cli-tools-are-beating-mcp-for-ai-agents/

## Core Finding

MCP servers consume massive context by dumping entire tool schemas into the prompt. CLI tools require zero schema tokens because models already know them from training data.

### Token Comparison (same task)

| Phase | MCP Approach | CLI Approach |
|-------|-------------|-------------|
| Tool schema injection | ~28,000 tokens | 0 tokens |
| Agent reasoning/tool selection | ~3,200 tokens | ~800 tokens |
| Execution & parsing | ~13,800 tokens | ~3,350 tokens |
| **Total (50 devices)** | **~145,000 tokens** | **~4,150 tokens** |

**Result: ~35x reduction with CLI.**

### Real-World Example: GitHub MCP Server
- Standard GitHub MCP server: **93 tool definitions**, consuming **~55,000 tokens** before any task begins
- Stacking 3 MCP servers (GitHub + Microsoft Graph + Jira): **150,000+ tokens** of tool definitions alone
- `gh` CLI: **0 schema tokens** — model already knows it

### Benchmark Support
- CLI achieves **28% higher task completion** with similar token counts
- Token Efficiency Score (TES): CLI **202** vs MCP **152** (33% efficiency advantage)

## When to Use Which

### CLI as Default
- Tool exists as a CLI (`gh`, `git`, `az`, `docker`, `kubectl`, `blender` Python scripts)
- Model already knows the tool from training data
- Task is simple enough that structured validation isn't needed
- Context budget is tight

### MCP When You Need Its Guarantees
- Structured production environments requiring strict input validation
- OAuth flows and audit trails
- Multi-tenant SaaS with fine-grained permission scoping
- Non-CLI tools (Figma, custom internal APIs)
- Discovery-heavy scenarios where agents must dynamically find tools

## Practical Guidelines for CLI-First Agents

1. **Provide a focused tool manifest** (~100 tokens instead of full schemas):
   ```
   ## Available Tools
   - `mgc`: Microsoft Graph CLI. Use for Intune, Entra ID, Teams, SharePoint.
   - `gh`: GitHub CLI. Use for repos, issues, PRs.
   - Custom scripts in /tools/: compliance-check.ps1
   ```

2. **Build thin wrapper scripts** — encapsulate multi-step operations into a single script call

3. **Use structured output flags** — `--output json` or `--format json` for clean, parseable data

4. **Leverage `--help` as dynamic documentation** — agents can fetch on-demand docs more efficiently than pre-loading entire schemas

## Guideline

> **Use CLI as your default; fall back to MCP when you need its specific guarantees.**

## Relevance to Hermes

This validates the Hermes approach:
- Heavy use of CLI tools (`gh`, `curl`, `scripts`) for common operations
- MCP used selectively for specialized integrations (Blender, codegraph, iknowkungfu)
- The `tool-call-efficiency` discipline of checking context sufficiency before reaching for tools is the behavioral complement to this architectural insight
