---
name: team-wiki/sync
description: Synchronize Team-Wiki markdown with GBrain database (cron-friendly or daemon mode)
version: 1.0.0
author: Hermes Agent Team
license: MIT
metadata:
  hermes:
    tags: [team-wiki, sync, gbrain, cron, watch]
    related_skills: [team-wiki/setup, team-wiki/maintain, gbrain]
---

# Team-Wiki Sync

Keeps the GBrain knowledge graph synchronized with the Team-Wiki markdown directory. Supports one-shot cron jobs (recommended) or a long-lived watcher daemon.

## Prerequisites

- GBrain installed and initialized
- `WIKI_PATH` environment variable set to Team-Wiki directory
- `GBRAIN_DATABASE_URL` or equivalent env configured (points to `~/.hermes/shared-brain/brain.pglite`)
- Team-Wiki directory exists and is structured per SCHEMA.md

## The Sync Process

GBrain sync is a two-step operation:

1. **`gbrain sync --repo <path>`** — Incremental import of markdown changes. Detects changes via `git diff`, parses frontmatter and wikilinks, extracts entities and relationships, and writes updated pages back to the repo with enriched metadata.

2. **`gbrain embed --stale`** — Generates embeddings for any new or modified chunks that lack vector representations. This step is required to make new content searchable.

**Always chain them:** `gbrain sync --repo $WIKI_PATH && gbrain embed --stale`

If you omit embed, new pages exist in the DB but are invisible to vector search.

## Usage Modes

### Cron Job (Recommended)

Run every 5–30 minutes via Hermes cron:

```bash
# Inside a Hermes cron job or shell script
gbrain sync --repo "$WIKI_PATH" && gbrain embed --stale
```

**Hermes cron syntax:**
```
/cron add "*/15 * * * *" "gbrain sync --repo $WIKI_PATH && gbrain embed --stale" --name "team-wiki-sync"
```

### Watch Daemon (Near-Real-Time)

Poll for changes every 60 seconds. Use under a process manager (systemd, pm2, or Hermes background task) and pair with cron fallback:

```bash
gbrain sync --watch --repo "$WIKI_PATH" && gbrain embed --stale
```

⚠️ `--watch` exits after 5 consecutive failures. Not a long-lived guarantee without supervision.

### Manual One-Shot

```bash
gbrain sync --repo "$WIKI_PATH" && gbrain embed --stale
```

## What Gets Synced

Only "syncable" markdown files are indexed:
- Included: Files under `entities/`, `concepts/`, `comparisons/`, `queries/` with valid frontmatter
- Excluded by design: `.git/`, hidden paths, `ops/`, `README.md`, `index.md`, `SCHEMA.md`, `log.md`

## Verification

After running sync:

```bash
# Check stats: page count should match number of entity/concept files
gbrain stats

# Search for a recent change to confirm it's indexed
gbrain search "your recent edit text"
```

Compare page count to actual files:
```bash
find "$WIKI_PATH" -name '*.md' | grep -v -E '(README|index|SCHEMA|log)' | wc -l
```

A large gap indicates Transaction mode pooler issues (see GBrain docs) or file format errors.

## Troubleshooting

**"`.begin()` is not a function"** — Your DATABASE_URL is using Supabase Transaction mode pooler. Switch to Session mode pooler (port 6543) or direct connection. PGLite (`file:` URL) is unaffected.

**New pages not appearing in search** — Did you run `gbrain embed --stale`? If embeddings count is far below total chunks, re-run embed.

**Sync exits immediately under `--watch`** — Likely 5 consecutive failures. Check `log.md` and GBrain logs. Common causes: database down, path misconfigured, file permission errors.

## Environment Variables

- `WIKI_PATH` — Path to Team-Wiki root (required)
- `GBRAIN_DATABASE_URL` — Database connection (defaults to `file:~/.local/share/gbrain` or `file:~/.hermes/shared-brain/brain.pglite`)
- `OPENAI_API_KEY` — Required for embeddings (unless using a local embedding engine)
- `OPENAI_BASE_URL` — Optional custom endpoint

## Integration

- **MCP Server**: GBrain runs as an MCP server (configured in `~/.hermes/config.yaml`) allowing all Hermes profiles to query the knowledge graph via `gbrain search`, `gbrain get_page`, etc.
- **Obsidian**: Browse and edit the Team-Wiki directly; changes are picked up by the next sync cycle.

## See Also

- `gbrain sync --help` — full CLI flags
- `team-wiki/maintain` — daily lint and health checks
- `team-wiki/ingest` — source ingestion pipeline
- GBrain live-sync guide: `docs/guides/live-sync.md`
