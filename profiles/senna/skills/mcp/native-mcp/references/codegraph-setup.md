# CodeGraph MCP Setup & CLI Reference

## Installation

```bash
npm install -g codegraph
codegraph --version  # should show 0.9.x+
```

## MCP Config (Profile-Isolated)

Under profile isolation, always use the absolute path:

```yaml
# ~/.hermes/profiles/<profile>/config.yaml
mcp_servers:
  codegraph:
    command: ~/.nvm/versions/node/v24.15.0/bin/codegraph
    args:
      - serve
      - --mcp
    timeout: 120
    connect_timeout: 60
    enabled: true
```

Find the absolute path: `which codegraph`

**Do NOT use bare `command: codegraph`** — under profile isolation, PATH resolution may fail or resolve to a different Node version.

## Platform Toolset Registration

Add to `platform_toolsets` for CLI access:

```yaml
platform_toolsets:
  cli:
    - mcp-codegraph
    # ... other toolsets
```

## CLI Commands (Direct Usage)

When MCP tools aren't available or you need richer output, use the CLI directly:

### Index Management

```bash
cd /path/to/project
codegraph init          # Initialize .codegraph/ in project root
codegraph index         # Full re-index
codegraph sync          # Incremental sync (fast)
codegraph status        # Show stats: files, nodes, edges, languages
codegraph unlock        # Remove stale lock file blocking indexing
```

### Symbol Queries

```bash
codegraph query "term"              # File-level keyword search (NOT symbol-level)
codegraph callers "symbolName"      # Find what calls this symbol
codegraph callees "symbolName"      # Find what this symbol calls
codegraph impact "symbolName"       # What's affected if this symbol changes
codegraph affected <file1> [file2]  # Find test files affected by source changes
```

### Context Building

```bash
codegraph context "task description"  # Semantic search → markdown context bundle
codegraph files                       # Project tree with symbol counts per file
```

### MCP Server

```bash
codegraph serve --mcp       # Stdio MCP transport (for Hermes integration)
codegraph serve --no-watch  # Disable file watcher (slow filesystems like WSL2)
```

## CLI Quirks & Pitfalls

### `query` is file-level, not symbol-level

`codegraph query "hermes-bridge"` returns files matching the term, ranked by relevance score. It does NOT search inside function/method names. Use `callers`/`callees`/`impact` for symbol-level lookup.

### `context` does semantic search, may return broad results

`codegraph context "hermes-dashboard task card rendering"` may return unrelated code if the semantic similarity is high across the codebase. MagicMirror²'s weather modules share many patterns with custom modules, so weather code often appears. Narrow queries with specific function names work better.

### Modules using `Module.register()` index as 1 symbol

MagicMirror² modules that use `Module.register(moduleName, {...})` pattern only index as a single symbol (the module registration). Internal methods, notification handlers, etc. are NOT individually indexed. This means:
- `callers "socketNotificationReceived"` → "not found"
- `query "_recomputeCounts"` → no results
- Only top-level exports/registrations appear in the symbol table

**Workaround:** Use `codegraph context "description"` for semantic search, or read files directly.

### `affected` may miss test files

`codegraph affected modules/hermes-bridge/board-utils.js` may not find `tests/unit/modules/hermes-bridge/board-utils_spec.js` even when the test file exists and imports from the source. The path-matching heuristic has gaps.

**Workaround:** Use `codegraph query "board-utils"` to find both source and test files.

### `callers` returns ALL matches across the codebase

`codegraph callers "startPeriodicFetch"` returns 13 results including unrelated modules (calendar, newsfeed, all weather providers). Filter results to your module of interest manually.

## Known Working Config (Senna Profile)

As of 2026-05-24, codegraph MCP is configured in senna profile at `~/.hermes/profiles/senna/config.yaml` under `mcp_servers.codegraph`. The CLI binary lives at `~/.nvm/versions/node/v24.15.0/bin/codegraph`.

## Example: HermesMirror

```bash
cd ~/projects/HermesMirror
codegraph status   # 258 files, 1087 nodes, 1352 edges
codegraph sync     # Incremental update
codegraph context "diffBoardState upsertTask"  # Returns hermes-bridge board-utils code
codegraph callers "startPeriodicFetch"          # Shows all fetcher callers
codegraph impact "statusToEvent"                # Shows diffBoardState dependency
```
