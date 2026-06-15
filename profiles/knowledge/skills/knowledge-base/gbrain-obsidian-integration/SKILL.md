---
name: gbrain-obsidian-integration
description: Integrate GBrain knowledge graph engine with an Obsidian vault — architecture patterns, sync strategy, MCP setup, and Team-Wiki mirroring. Use when setting up GBrain alongside an existing Obsidian vault with PARA structure.
triggers:
  - "use gbrain with obsidian"
  - "gbrain obsidian integration"
  - "gbrain vault setup"
  - "knowledge base with gbrain"
  - "team-wiki gbrain"
version: 0.2.0
author: Senna (Hermes)
deprecated: true
---

# GBrain + Obsidian Integration

> **DEPRECATED** — GBrain was removed from this stack on 2026-05-10. The MCP server config was deleted from root config.yaml and the plugin directory at `~/.hermes/plugins/gbrain/` is orphaned (not referenced by any config). This skill is preserved for reference only — it documents the integration pattern if GBrain is reinstated.

**Purpose:** Connect GBrain (knowledge graph engine) with an existing Obsidian vault that uses PARA structure, enabling the agent to maintain a separate compiled knowledge base while you write in your normal vault.

**Trigger:** User asks how to use GBrain with Obsidian, or wants to set up a team knowledge base with GBrain backing an Obsidian vault.

---

## Architecture Decision

First, choose your integration pattern:

### Approach A: Separate Brain + Mirror (Recommended for existing PARA vaults)

**Layout:**
```
~/Hermes Vault/Hermes/          ← your writing surface (PARA)
  1-Projects/
  2-Areas/
  3-Resources/
  4-Archive/
  Memory/
  Sessions/
  icarus/
  Team-Wiki/                    ← READ-ONLY mirror of ~/.hermes/brain/markdown/
     people/
     companies/
     concepts/
     comparisons/
     queries/
     SCHEMA.md
     index.md
     log.md

~/.hermes/brain/                ← GBrain's authoritative markdown mirror
   people/
   companies/
   ...
   brain.db                      ← PGLite database

~/.local/share/gbrain/          ← GBrain's structured database only
   gbrain.db
```

**Flow:**
1. You write markdown in your vault using PARA folders (unchanged workflow).
2. Cron job runs `gbrain sync` → imports vault markdown → extracts entities, links, timeline → updates `brain.db` and regenerates markdown into `~/.hermes/brain/`.
3. One-way mirror (symlink or rsync) copies `~/.hermes/brain/markdown/*` → `vault/Team-Wiki/` so you can browse the compiled knowledge in Obsidian's Graph View.
4. Hermes queries GBrain via MCP tools (`gbrain query`, `gbrain search`) for intelligent answers.
5. Agent-written material goes into `~/.hermes/brain/` (not your PARA folders), keeping human and agent layers separate.

**When to choose:**
- You already have an established PARA vault
- You want to keep your manual notes untouched by agent automation
- You want clean separation: human writing surface vs. agent-compiled knowledge
- Team-Wiki structure is for **browsing what the agent knows**, not for your daily capture

### Approach B: Direct Vault Usage (GBrain owns the wiki)

**Layout:**
```
~/Hermes Vault/Hermes/
  people/
  companies/
  concepts/
  raw/
  SCHEMA.md
  index.md
  log.md
```

**Flow:**
- GBrain's `WIKI_PATH` points directly at your vault
- Agent reads/writes wiki pages in-place
- Obsidian shows the same files the agent maintains

**When to choose:**
- Starting fresh with no existing vault content
- Want a single source of truth
- Comfortable with agent-written pages mixing with human notes (use clear naming conventions)

**Drawbacks for PARA users:**
- Requires restructuring your vault from PARA to GBrain's schema
- Migration step needed (`gbrain migrate` from Obsidian → GBrain format)
- Your existing PARA folders would need to be moved or archived

---

## Platform Compatibility & Path Selection

macOS 15.6 (Darwin 26.3) has a known WASM regression that breaks PGLite. If you're on this or a later macOS version, **skip to Path B (Postgres fallback)**. On earlier macOS versions, PGLite should work fine.

**Quick check:**
```bash
sw_vers | grep ProductVersion
# 15.6+ → use Postgres; <15.6 → PGLite safe
```

Or attempt a dry-run: `gbrain init` — if you see *"PGLite failed to initialize its WASM runtime. This is most commonly the macOS 26.3 WASM bug"*, switch to Postgres.

### Path A: Standard PGLite Setup (macOS < 15.6)

[Existing PGLite steps go here — unchanged]

### Path B: Postgres Fallback (macOS 15.6+ or PGLite failure)

Uses a real PostgreSQL server instead of PGLite. More setup steps but fully reliable on affected macOS versions. Production-grade anyway (faster, multi-device ready, concurrent-safe).

#### B1. Install PostgreSQL 17

```bash
brew install postgresql@17
```

#### B2. Initialise a dedicated data directory

Avoid clobbering any existing Postgres cluster:

```bash
mkdir -p ~/.hermes/shared-brain/pgdata
initdb -D ~/.hermes/shared-brain/pgdata -U $(whoami) -E UTF8
chmod 0700 ~/.hermes/shared-brain/pgdata
```

#### B3. Start the PostgreSQL server

Choose one launch method:

**Option A — via brew services (auto-starts on login):**
```bash
brew services start postgresql@17
```

**Option B — manual background (easier to port-pin for this setup):**
```bash
# Start on port 5433 and bind to /tmp socket
postgres -D ~/.hermes/shared-brain/pgdata -p 5433 -k /tmp &
```

Verify it's running:
```bash
ps aux | grep postgres | grep 5433
pg_isready -p 5433 -h /tmp
```

#### B4. Create the GBrain database

```bash
# Using createdb (respects the data directory config)
createdb -D ~/.hermes/shared-brain/pgdata brain_hermes

# Or via SQL:
psql -d postgres -p 5433 -h /tmp -c "CREATE DATABASE brain_hermes OWNER $(whoami);"
```

#### B5. Install required PostgreSQL extensions

```bash
# Vector for embeddings
brew install pgvector

# Load extensions into the brain_hermes database
psql -d brain_hermes -p 5433 -h /tmp -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -d brain_hermes -p 5433 -h /tmp -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

#### B6. Configure GBrain to use Postgres

Create or edit `~/.gbrain/config.json`:

```json
{
  "engine": "postgres",
  "database_url": "postgres://$(whoami)@localhost:5433/brain_hermes?host=/tmp"
}
```

Key details:
- `engine` must be `"postgres"` (PGLite uses different connection semantics)
- `?host=/tmp` tells libpq to use the Unix socket at `/tmp/.s.PGSQL.5433`
- Alternatively omit `?host=/tmp` and use `-h /tmp` on `psql`; the URL alone often suffices

Alternatively set via environment (Hermes prefers this):

```bash
export GBRAIN_DATABASE_URL="postgres://$(whoami)@localhost:5433/brain_hermes"
```

Hermes MCP server will pick this up if defined in `~/.hermes/config.yaml` under `env`.

#### B7. Initialise GBrain's schema

```bash
cd ~/.hermes/plugins/gbrain
./bin/gbrain init
```

Expected output:
```
✓ Database connected
✓ Schema version latest
✓ GBrain ready at postgres://… brain_hermes
```

If you see *"PGLite failed to initialize its WASM runtime. This is most commonly the macOS 26.3 WASM bug"*, your config is still pointing to PGLite. Double‑check `~/.gbrain/config.json` and any `GBRAIN_DATABASE_URL` env var overriding it.

#### B8. Keep PostgreSQL running across reboots

```bash
# brew services (you already started it above)
brew services enable postgresql@17

# or: create a launchd plist similar to the Windows version, targeting:
#   /usr/local/bin/postgres -D ~/.hermes/shared-brain/pgdata -p 5433 -k /tmp
```

#### B9. Resume Path A

Rejoin the shared workflow at Step 4 (Import vault) and continue through 5–10. Differences:
- DB engine: `postgres`
- Connection via URL (no local file path)
- PostgreSQL process must stay alive (brew services handles this)
- Performance is faster and concurrent-safe

**Migration note:** If you already tried PGLite and have a `brain.pglite` directory, keep it as a backup or delete it. To migrate existing data you'd need both engines available: `gbrain migrate --to postgres`. In our case we started fresh.

---

## Platform diagnostic

When the user reports *"PGLite failed to initialize its WASM runtime"*, confirm:
1. `sw_vers | grep ProductVersion` → 15.6+ (Darwin 26.3) is the trigger
2. No workaround exists for WASM; the only fix is switching to Postgres engine
3. Path B above is the recommended permanent solution (not a temporary workaround)

---

## Recommended Setup (Approach A)

### Prerequisites

- Bun runtime: `curl -fsSL https://bun.sh/install | bash`
- GBrain plugin already cloned: `~/.hermes/plugins/gbrain/` (if not, `git clone https://github.com/garrytan/gbrain.git ~/.hermes/plugins/gbrain`)
- OpenAI-compatible API key for embeddings (your existing `OPENAI_API_KEY` in `~/.config/nim/env.sh` works)
- Obsidian vault path confirmed: `~/Hermes Vault/Hermes`

### Step-by-Step

#### 1. Install Bun & GBrain dependencies

```bash
# Install Bun (if not already)
curl -fsSL https://bun.sh/install | bash
export PATH="$HOME/.bun/bin:$PATH"

# Install GBrain
cd ~/.hermes/plugins/gbrain
bun install
bun link  # makes `gbrain` CLI available in ~/.bun/bin
```

Verify: `gbrain --version` should print a version.

#### 2. Create brain repository

```bash
mkdir -p ~/.hermes/brain
cd ~/.hermes/brain
git init
```

This repo will contain GBrain's markdown mirror (not your vault). Keep it separate.

#### 3. Initialize GBrain database

```bash
gbrain init  # creates PGLite DB at ~/.local/share/gbrain/gbrain.db
```

PGLite is zero-config (no Postgres server needed). For large vaults (1000+ files), consider Supabase + pgvector instead — see `gbrain docs/ENGINES.md`.

#### 4. Import your Obsidian vault

```bash
gbrain import ~/Hermes\ Vault/Hermes --no-embed
```

This scans your vault's markdown, extracts frontmatter and wikilinks, and writes pages into `~/.hermes/brain/markdown/` following GBrain's schema (people, companies, concepts, etc.). The `--no-embed` flag skips vector embedding for now (fast import).

**Expected:** New markdown files appear under `~/.hermes/brain/` in category directories, plus `timeline.md` and link index.

#### 5. Generate embeddings

```bash
gbrain embed --stale
```

This processes all pages missing embeddings, calls your OpenAI-compatible endpoint (`text-embedding-3-large` by default), and stores vectors in the DB. Time depends on vault size (~1 sec per 100 pages on average).

#### 6. Backfill knowledge graph

```bash
gbrain extract links --source db
gbrain extract timeline --source db
```

Populates the typed relationship graph (`attended`, `works_at`, `founded`, etc.) and structured timeline from existing content. These tables auto-update on future writes; this is a one-time backfill.

#### 7. Set up live sync (cron)

Configure a recurring job to keep brain current:

```bash
# Add to crontab (edit with `crontab -e`)
*/15 * * * * cd ~/.hermes/brain && gbrain sync --follow >> ~/.hermes/logs/gbrain-sync.log 2>&1
# Daily embed refresh (catches new pages)
0 3 * * * cd ~/.hermes/brain && gbrain embed --stale >> ~/.hermes/logs/gbrain-embed.log 2>&1
# Weekly health check
0 6 * * 1 cd ~/.hermes/brain && gbrain doctor --json >> ~/.hermes/logs/gbrain-doctor.log 2>&1
```

**Important:** Use `--follow` mode for the sync job — it runs continuously, watches for filesystem changes via `fswatch`, and updates immediately. The cron entry above starts it every 15 min; if it's already running, the new instance exits immediately (idempotent).

Alternatively, use GBrain's built-in `cron-scheduler` skill if you prefer agent-managed scheduling.

#### 8. Mirror brain to Team-Wiki (one-way)

The agent writes to `~/.hermes/brain/markdown/`. To browse these pages in Obsidian, mirror them into your vault:

**Option A: Symbolic link (simple, live)**
```bash
mkdir -p ~/Hermes\ Vault/Hermes/Team-Wiki
ln -s ~/.hermes/brain/markdown/* ~/Hermes\ Vault/Hermes/Team-Wiki/
# Note: ln -s doesn't merge directories; better to symlink the parent:
rmdir ~/Hermes\ Vault/Hermes/Team-Wiki  # if empty
ln -s ~/.hermes/brain/markdown ~/Hermes\ Vault/Hermes/Team-Wiki
```

**Option B: Rsync (copy, safe)**
```bash
mkdir -p ~/Hermes\ Vault/Hermes/Team-Wiki
rsync -av --delete ~/.hermes/brain/markdown/ ~/Hermes\ Vault/Hermes/Team-Wiki/
```

Automate with a cron (runs after sync):
```bash
*/16 * * * * rsync -av --delete ~/.hermes/brain/markdown/ ~/Hermes\ Vault/Hermes/Team-Wiki/ >> ~/.hermes/logs/gbrain-mirror.log 2>&1
```

**Recommendation:** Use symlink if you're the only user and want live updates. Use rsync if multiple people write to the vault or you want to avoid symlink clutter in Obsidian.

#### 9. Configure Hermes MCP access

Edit `~/.hermes/config.yaml` (create if missing):

```yaml
mcp_servers:
  gbrain:
    command: ~/.hermes/plugins/gbrain/bin/gbrain
    args: ["serve"]
    enabled: true
    # Optional: filter tools if you want subset
    # tools:
    #   allow: ["query", "search", "put_page", "sync"]
```

Restart Hermes. Verify with `/plugins` — should list `gbrain` MCP server.

Now Hermes can call GBrain tools directly:
- `/gbrain query "who works at Acme?"`
- `/gbrain search "quantum crypto"` (hybrid)
- `/gbrain graph-query "marcus-reid" --depth 2`

#### 10. Populate vault with GBrain skill reference

Copy the 26 GBrain skill docs into your vault for manual reading:

```bash
mkdir -p ~/Hermes\ Vault/Hermes/3-Resources/Skills/Agents/GBrain/
cp -r ~/.hermes/plugins/gbrain/skills/* ~/Hermes\ Vault/Hermes/3-Resources/Skills/Agents/GBrain/
```

Update your `3-Resources/Skills/Agents/gbrain.md` index note to point to these local copies.

### Optional: Auto-enrichment

If you want GBrain to pull external data (web search, social profiles) when entities are mentioned:

```bash
gbrain integrations install web-search  # or: twitter, email, etc.
```

Each integration has its own credential requirements. Run `gbrain integrations list` to browse.

---

## Key Conventions

### GBrain's schema (what gets created under `~/.hermes/brain/`)

```
markdown/
├── people/                # Person pages (slugified name)
│   └── marcus-reid.md
├── companies/             # Company pages
│   └── acme-ai.md
├── concepts/              # Topics, techniques, frameworks
├── comparisons/           # Side-by-side analyses
├── queries/               # Past query results worth saving
├── timeline.md            # All dated events across entities
├── SCHEMA.md              # Conventions (read by agent before writing)
└── index.md               # Catalog of pages
```

**Page format (each `.md` file):**
```markdown
---
title: Marcus Reid
type: person
created: 2026-04-20
updated: 2026-04-23
tags: [person, investor, ai]
sources: [raw/meetings/2026-04-20-acme-meeting.md]
---

## Summary
CTO at Acme AI, previously at Meta. Focused on quantum-resistant cryptography.

## Current
- **Role:** CTO
- **Company:** [[acme-ai]]
- **Joined:** 2024-01

## See Also
- [[priya-patel]] — co-founder
- [[threshold-ventures]] — investor

---

## Timeline
- 2026-04-20 — attended meeting with Acme AI team [source: meetings/2026-04-20]
- 2026-04-18 — mentioned in tweet about quantum crypto [source: raw/tweets/...]
```

### Vault PARA vs Team-Wiki

- **PARA folders** (`1-Projects/`, `2-Areas/`, etc.): Your manual notes. Free-form. No schema enforcement.
- **Team-Wiki/**: Agent-generated, GBrain-sourced. Read-only for you. Reflects what the brain knows.

Do NOT edit files under `Team-Wiki/` manually — they'll be overwritten on next sync. To correct something, edit the source note in your PARA vault or use `gbrain put_page` to update the brain's data layer; the next sync regenerates the markdown.

---

## Querying the Brain

Once MCP is live, ask Hermes:

```
/gbrain query "what have I discussed with Marcus about quantum?"
/gbrain search "Series B funding"           # hybrid: vector + keyword
/gbrain graph-query "acme-ai" --depth 2     # show connections
/gbrain get "people/marcus-reid"            # raw page
/gbrain stats                               # page count, link density
```

All results cite sources (links to vault files or raw sources).

---

## Maintenance

- **Weekly:** `gbrain doctor --json` — health check (broken links, orphans, stale pages)
- **Monthly:** `gbrain extract links --source db` (redundant but safe) and `gbrain lint` (if available)
- **Log rotation:** GBrain auto-rotates its internal logs; your vault `Team-Wiki/log.md` rotates at 500 entries via Secretary

### Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| MCP tools not appearing | `gbrain serve` not running or Hermes not restarted | Run `gbrain serve` manually to test; restart Hermes |
| No results from query | Brain DB empty or not synced | Run `gbrain sync --follow` and wait for initial import |
| Mirror shows stale pages | Rsync/cron lag or symlink broken | Check `~/.hermes/logs/gbrain-sync.log`; run mirror manually |
| Embedding failures | OpenAI key missing or wrong model | Verify `echo $OPENAI_API_KEY`; check `gbrain config` |
| Duplicate entity pages | Import ambiguity; resolver needs tuning | Adjust `~/.hermes/brain/SCHEMA.md` resolver rules; re-run `gbrain import` with `--rebuild` |

---

## Related Skills

- `obsidian` — read/write vault files directly
- `obsidian-memory-bridge` — syncs Hermes memory to `Memory/Hermes Memory.md`
- `llm-wiki` — Karpathy's wiki pattern (GBrain implements this with graph + embeddings)
- `team-wiki/setup` (create if needed) — bootstraps Team-Wiki directory structure, SCHEMA.md, index.md
- `team-wiki/sync-gbrain` (create if needed) — automates the GBrain sync + mirror cron as an agent skill

---

## Next Steps After Setup

1. **Test the pipeline:** Write a test note in `0-Inbox/` containing "Meeting with [[Marcus Reid]] from [[Acme AI]]". Wait 15 min (or run `gbrain sync --once` manually). Check `~/.hermes/brain/people/` for new pages.
2. **Browse Team-Wiki:** Open Obsidian, look at `Team-Wiki/` graph. Verify links appear.
3. **Query via Hermes:** `/gbrain query "who is Marcus Reid?"`
4. **Set up Secretary:** Ensure Secretary profile runs the `obsidian-memory-bridge` skill to keep `Memory/` current.
5. **Configure cron:** Double-check cron jobs are active with `crontab -l`.

---

## References

- GBrain docs: `~/.hermes/plugins/gbrain/README.md`, `docs/GBRAIN_RECOMMENDED_SCHEMA.md`
- Hermes MCP: `website/docs/user-guide/features/mcp.md`
- Obsidian vault: `~/Hermes Vault/Hermes/`
- Icarus memory fabric: `vault/icarus/`
