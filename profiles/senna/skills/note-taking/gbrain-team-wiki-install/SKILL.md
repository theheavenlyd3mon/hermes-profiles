---
name: gbrain-team-wiki-install
description: Install and configure GBrain with a shared Team-Wiki in the Obsidian vault for multi-agent collaboration
version: "0.2.0"
author: Hermes Agent
license: MIT
deprecated: true
metadata:
  hermes:
    category: "note-taking"
    tags: ["gbrain", "team-wiki", "install", "setup", "mcp"]
---

# GBrain + Team-Wiki Installation — SKILL

> **DEPRECATED** — GBrain was removed from this stack on 2026-05-10. The MCP server config was deleted from root config.yaml and the plugin directory at `~/.hermes/plugins/gbrain/` is orphaned. This skill is preserved for reference if GBrain is reinstated.

**Owner:** Secretary, Architect (review)

## Purpose
End-to-end setup of GBrain as a shared knowledge graph backend with a Team-Wiki in the Obsidian vault, accessible to all Hermes agent profiles via Icarus fabric. Covers Bun installation, GBrain dependency setup, shared database configuration, MCP server definition, Team-Wiki scaffolding, skill creation, and cron scheduling.

## Trigger
- "setup gbrain team wiki"
- "install gbrain plugin"
- "create shared knowledge base"
- "team wiki bootstrap"

## Context & Constraints

### Must-haves
- **Shared database**: All agent profiles must read/write the same GBrain PGLite DB (not per-profile copies)
- **Shared wiki**: Single `Team-Wiki/` directory inside the user's Obsidian vault, separate from personal PARA notes
- **MCP integration**: GBrain runs as an MCP server defined in `~/.hermes/config.yaml` with auto-start
- **Skill reuse**: Four reusable skills (`team-wiki/setup`, `sync`, `maintain`, `ingest`) under `~/.hermes/skills/team-wiki/`
- **Cron scheduling**: Sync runs every 15 min via Hermes cron; maintenance runs daily
- **Env security**: No API keys in files; use existing `~/.config/nim/env.sh` or process environment

### Known Pitfalls (discovered during implementation)
1. **Profile sandboxing redirects paths** — When running under a Hermes profile, `~` expands to `~/.hermes/profiles/<profile>/home`. This causes:
   - GBrain to create its DB in a profile-local `~/.gbrain/brain.pglite` instead of shared location
   - Skills written to profile-space `~/.hermes/skills/` instead of canonical `~/.hermes/skills/`
   - **Fix**: Use absolute `/Users/<username>` paths for all shared resources; verify with `os.path.realpath(os.path.expanduser('~'))`

2. **Bun binary location** — `bun link` places `gbrain` in `~/.bun/bin/gbrain`, but in sandboxed sessions that directory may not exist in PATH. The binary also may be a symlink to a sandboxed node_modules.
   - **Fix**: Install Bun from the user's real shell; verify with `which gbrain && gbrain --version` outside Hermes

3. **GBrain config precedence** — `~/.gbrain/config.json` is written during `gbrain init` and overrides env vars. If you want shared DB:
   - **Step A**: Set `GBRAIN_DATABASE_URL` env and run `gbrain init` verbosely to confirm path
   - **Step B**: Move the created `brain.pglite` to canonical shared location (e.g., `~/.hermes/shared-brain/brain.pglite`)
   - **Step C**: Rewrite `~/.gbrain/config.json` with the shared `database_path`
   - **Step D**: Test with `gbrain doctor --json` (if available) or `gbrain status`

4. **Vault path with spaces** — `~/Hermes Vault/Hermes/` contains a space. Must be quoted or escaped in all shell commands and YAML strings. GBrain accepts it as a plain path string; no URI encoding needed.

5. **Hermes cron directory** — Not all installations use `~/.hermes/cron/` by default. Confirm in `config.yaml` under `cron.jobs_dir`. Create the directory if missing; Hermes auto-polls for executable scripts.

6. **Schema design for AI agents** — Standard wiki schemas (personal, corporate) don't fit. Needed domain-specific tags with prefixes: `agent:`, `skill:`, `infrastructure:`, `concept:`, `company:`, `person:`, `project:`. Page thresholds: create only if entity appears in 2+ sources or is central to one.

## Prerequisites
- User has an Obsidian vault at known path (commonly `~/Hermes Vault/Hermes/`)
- Hermes agent runtime installed; Icarus memory bridge configured; profiles can share vault
- OpenAI API key available in environment (for embeddings). User uses `~/.config/nim/env.sh` — ensure Hermes sources it
- Linux/macOS with Bash

## Step-by-Step Procedure

### Phase 1 — Install Bun
```bash
# Run from user's regular shell (not inside Hermes)
curl -fsSL https://bun.sh/install | bash
# Follow printed instructions (usually: source ~/.bun/profile)
source ~/.bun/profile
which gbrain
gbrain --version
```
**Expected:** `gbrain 0.16.x` or newer.

### Phase 2 — Install GBrain Plugin Dependencies
```bash
cd ~/.hermes/plugins/gbrain
export PATH="$HOME/.bun/bin:$PATH"
bun install
bun link
```
**Verification:** `ls ~/.bun/bin/gbrain` exists and is executable.

### Phase 3 — Create Shared Brain Database

**Important — Read this first: Database engine selection**

GBrain supports two engines:
- **PGLite**: Embedded Postgres via WASM. Simpler (zero external services), but **broken on macOS 15.6+ (Darwin 26.3)** due to a known `@electric-sql/pglite` WASM regression. Use only on older macOS or if you need portability.
- **PostgreSQL 17**: Recommended for all modern setups. Slightly more operational overhead, but reliable, performant, and supports full Postgres extensions (vector, pg_trgm).

**Rule of thumb:**
- macOS 15.6 or newer → **Postgres 17** (Path B)
- macOS 15.5 or older → PGLite is fine (Path A)
- Any uncertainty → choose Postgres (future-proof)

#### Path A: PGLite (macOS < 15.6, or zero-config preference)

```bash
# PGLite stores everything in a file
mkdir -p ~/.hermes/shared-brain
# GBrain will initialise the file automatically on first run
gbrain init   # creates ~/.local/share/gbrain/gbrain.db (PGLite)
```

#### Path B: PostgreSQL 17 (macOS 15.6+ or when PGLite fails)

**Install & configure:**

```bash
brew install postgresql@17

# Initialise a dedicated cluster for GBrain
mkdir -p ~/.hermes/shared-brain/pgdata
initdb -D ~/.hermes/shared-brain/pgdata -U $(whoami) -E UTF8
chmod 0700 ~/.hermes/shared-brain/pgdata

# Start it (choose one)
brew services start postgresql@17   # persists across reboots
# or: postgres -D ~/.hermes/shared-brain/pgdata -p 5433 -k /tmp &
```

**Create the database and extensions:**

```bash
createdb -D ~/.hermes/shared-brain/pgdata brain_hermes
psql -d brain_hermes -p 5433 -h /tmp -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -d brain_hermes -p 5433 -h /tmp -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

**Configure GBrain:**

```bash
# Write global config (shared across all profiles)
cat > ~/.gbrain/config.json <<'EOF'
{
  "engine": "postgres",
  "database_url": "postgres://$(whoami)@localhost:5433/brain_hermes?host=/tmp"
}
EOF
```

Keep PostgreSQL running (via `brew services` or a launchd plist). If you prefer PGLite instead, delete `~/.gbrain/config.json` and let GBrain create its default file-based DB at `~/.local/share/gbrain/gbrain.db`; then set `GBRAIN_DATABASE_URL` only if you need a non-default location.

---

Once the DB is ready, continue.

### Phase 4 — Initialize GBrain Database

Set env and run init **from real user environment** (so HOME resolves correctly):

```bash
export HOME="~"  # your actual home
export PATH="$HOME/.bun/bin:$PATH"
export WIKI_PATH="$HOME/Hermes Vault/Hermes/Team-Wiki"
export GBRAIN_DATABASE_URL="file:$HOME/.hermes/shared-brain/brain.pglite"

gbrain init
```

Expected output: `Brain ready at ... 0 pages.`

If DB already exists, `gbrain init` is a no-op.

### Phase 5 — Hermes MCP Configuration
### Phase 5 — Hermes MCP Configuration

GBrain runs as an MCP server. Create `~/.hermes/config.yaml`:

```yaml
version: "1.0"
mcp_servers:
  gbrain:
    command: ~/.hermes/plugins/gbrain/bin/gbrain
    args: ["serve"]
    cwd: ~/.hermes/plugins/gbrain   # adjust for your user
    env:
      OPENAI_API_KEY: "${env.OPENAI_API_KEY}"
      OPENAI_BASE_URL: "${env.OPENAI_BASE_URL:-https://api.openai.com/v1}"
      # Database selection — set ONE of the following:
      # GBRAIN_DATABASE_URL for Postgres:
      # GBRAIN_DATABASE_URL: "postgres://$(whoami)@localhost:5433/brain_hermes?host=/tmp"
      # OR: use PGLite file (default if neither is set; reads from ~/.gbrain/config.json)
    auto_start: true
    restart: on-failure
    description: "GBrain knowledge graph MCP server for Team-Wiki"
cron:
  enabled: true
  jobs_dir: ~/.hermes/cron
```

**Important:**
- Uncomment `GBRAIN_DATABASE_URL` if using Postgres; leave it commented if using PGLite.
- `~/.gbrain/config.json` takes precedence over env vars when present. For Postgres, either set the env var or write the correct JSON (`{"engine":"postgres","database_url":"…"}`).
- Use absolute paths; `$HOME` within Hermes may be sandboxed per profile.

### Phase 6 — Team-Wiki Scaffolding

Create directory structure and core files:

```python
import os

wiki = os.path.join("~", "Hermes Vault", "Hermes", "Team-Wiki")
subdirs = [
    "entities", "concepts", "comparisons", "queries",
    "raw/articles", "raw/papers", "raw/transcripts", "raw/assets"
]
for d in subdirs:
    os.makedirs(os.path.join(wiki, d), exist_ok=True)

# SCHEMA.md (domain-specific for Hermes agents)
with open(os.path.join(wiki, "SCHEMA.md"), 'w') as f:
    f.write("""# Team-Wiki Schema

## Domain
Hermes agent ecosystem — AI agents, skills, infrastructure, companies, people, concepts.

## Conventions
- Filenames: lowercase, hyphenated, no spaces
- Every page: YAML frontmatter (title, created, updated, type, tags, sources)
- Use `[[wikilinks]]`; ≥2 outbound links per page
- Timeline: `## YYYY-MM-DD — action` sections appended to bottom; bump `updated`
- Provenance citations: `^[raw/articles/source.md]`
- index.md lists all entity pages alphabetically by section
- Threshold: create page if entity appears in 2+ sources OR is central to one

## Tag Taxonomy
agent:|skill:|infrastructure:|company:|person:|project:|concept:|comparison:|meta:

## Page Types
| Type | Folder | Tag prefix |
|------|--------|------------|
| Agent | entities | agent: |
| Skill | entities | skill: |
| Company | entities | company: |
| Person | entities | person: |
| Project | entities | project: |
| Concept | concepts | concept: |
| Comparison | comparisons | comparison: |
| Query | queries | query: |
""")

# index.md
with open(os.path.join(wiki, "index.md"), 'w') as f:
    f.write("""# Team-Wiki Index

> Last updated: — | Total pages: 0

## Agents
## People
## Companies
## Skills
## Projects
## Infrastructure
## Concepts
## Comparisons
## Queries
""")

# log.md
with open(os.path.join(wiki, "log.md"), 'w') as f:
    f.write("""# Team-Wiki Log

> Append-only. Rotate after 500 entries.

## [2026-04-25] create | Wiki initialized
- Domain: Hermes agent ecosystem
- Structure: SCHEMA.md, index.md, log.md, folders
- Responsible: @senna setup
""")

# Folder READMEs
for folder in ["entities", "concepts", "comparisons", "queries"]:
    with open(os.path.join(wiki, folder, "README.md"), 'w') as f:
        f.write(f"# {folder.title()}\n\nPrimary home for `type={folder.rstrip('s')}` pages.\n")
```

### Phase 7 — Create Team-Wiki Skills

Create `~/.hermes/skills/team-wiki/` with four skills:

1. **team-wiki/setup** — idempotent bootstrap (this entire procedure, minus Bun install). Validates existing structure before writing.
2. **team-wiki/sync** — runs `gbrain sync --repo "$WIKI_PATH"`; designed for cron (lockfile, quiet mode, duration logging).
3. **team-wiki/maintain** — daily checks: orphans, broken links, index completeness, frontmatter validation, tag audit, log rotation, stale content. Generates markdown report appended to `log.md`.
4. **team-wiki/ingest** — source capture (URL/file/clipboard) → raw/ → entity extraction (GBrain MCP or LLM) → dedup → page creation/update → cross-linking → index + log updates.

**Key patterns for all skills:**
- Always respect `WIKI_PATH` env var; default to `~/Hermes Vault/Hermes/Team-Wiki`
- Read `SCHEMA.md` first (pre-answer ritual)
- All actions append to `log.md` with date and `@agent` attribution
- Use `[[wikilinks]]` in reports and page bodies
- Fail clearly with actionable messages (e.g., "missing OPENAI_API_KEY — embeddings disabled, continuing")

### Phase 8 — Cron Jobs

Create executable scripts in `~/.hermes/cron/`:

**`team-wiki-sync.sh`** (every 15 min):
```bash
#!/usr/bin/env bash
export PATH="$HOME/.bun/bin:$PATH"
export WIKI_PATH="$HOME/Hermes Vault/Hermes/Team-Wiki"
export GBRAIN_DATABASE_URL="file:$HOME/.hermes/shared-brain/brain.pglite"

LOCKFILE="/tmp/team-wiki-sync.lock"
if [ -e "$LOCKFILE" ] && kill -0 "$(cat "$LOCKFILE")" 2>/dev/null; then
  echo "$(date) — sync already running" >&2
  exit 1
fi
echo $$ > "$LOCKFILE"

gbrain sync --repo "$WIKI_PATH" --quiet
exit_code=$?
rm -f "$LOCKFILE"
exit $exit_code
```

**`team-wiki-maintain.sh`** (daily 04:00 UTC):
```bash
#!/usr/bin/env bash
export PATH="$HOME/.bun/bin:$PATH"
export WIKI_PATH="$HOME/Hermes Vault/Hermes/Team-Wiki"
# Execute maintenance checks via skill or inline Python
```

Make both executable: `chmod +x ~/.hermes/cron/*.sh`

Hermes cron daemon auto-detects new scripts.

### Phase 9 — Post-Install Verification

```bash
# 1. Confirm Bun and GBrain
which gbrain && gbrain --version

# 2. Check shared DB
ls -lh ~/.hermes/shared-brain/brain.pglite

# 3. Check global config
cat ~/.gbrain/config.json

# 4. Check MCP config
cat ~/.hermes/config.yaml | grep -A10 gbrain

# 5. Check Team-Wiki structure
find ~/Hermes\ Vault/Hermes/Team-Wiki -type f | head -20

# 6. Check skills
ls -R ~/.hermes/skills/team-wiki/

# 7. Check cron scripts
ls -l ~/.hermes/cron/

# 8. Restart Hermes to load MCP server
hermes restart

# 9. Verify MCP server list
hermes mcp list   # should show 'gbrain'

# 10. Run initial sync
hermes run team-wiki/sync
# or: gbrain sync --repo ~/Hermes\ Vault/Hermes/Team-Wiki

# 11. Run initial setup (idempotent, adds first log entry if missing)
hermes run team-wiki/setup
```

## Success Criteria
- [ ] `gbrain` CLI works outside Hermes (`gbrain status` succeeds)
- [ ] Shared DB file exists at `~/.hermes/shared-brain/brain.pglite` and is not zero bytes
- [ ] `~/.gbrain/config.json` points to shared DB
- [ ] `~/.hermes/config.yaml` has MCP server `gbrain` with correct absolute paths
- [ ] `Team-Wiki/` directory exists with SCHEMA.md, index.md, log.md, subfolders, READMEs
- [ ] Four skills present in `~/.hermes/skills/team-wiki/` with complete SKILL.md content
- [ ] Cron scripts in `~/.hermes/cron/` are executable
- [ ] Hermes restart shows MCP server startup without errors
- [ ] First `gbrain sync` completes with exit 0 and processes 0+ pages
- [ ] `team-wiki/setup` runs idempotently (no clobbering)

## Rollback
If something fails:
1. Stop Hermes: `hermes stop`
2. Remove MCP entry from `~/.hermes/config.yaml`
3. Move or delete `~/.hermes/shared-brain/` (DB) and `~/Hermes Vault/Hermes/Team-Wiki/`
4. Remove `~/.hermes/skills/team-wiki/`
5. Remove cron scripts from `~/.hermes/cron/`
6. Restart Hermes; state returns to pre-install

## Future Work
- Make `team-wiki/sync` an autonomous skill (daemon mode with built-in lock/heartbeat) instead of shell+cron wrapper
- Add `gbrain extract` wrapper skill to hide MCP vs direct CLI differences
- Implement `team-wiki/query` skill for natural-language searches over the knowledge graph
- Integrate `obsidian-memory-bridge` to mirror Team-Wiki back to agent session memory automatically
- Auto-tag suggestion based on SCHEMA.md taxonomy during ingest

---

## Appendix — Embedding Endpoint Troubleshooting

If embeddings fail with 404/401 errors or `gbrain embed --stale` produces no results, the issue is usually a mismatched embedding endpoint configuration. GBrain uses the OpenAI-compatible API interface; you must point it at an endpoint that serves the embedding model you specify.

### Common root causes

| Symptom | Likely cause | Fix |
|--------|-------------|-----|
| `404 Not Found` on `/embeddings` | Wrong base URL (NIM chat endpoint instead of embedding) | Set `OPENAI_BASE_URL` to an endpoint that supports embeddings, and specify `OPENAI_EMBEDDING_MODEL` |
| `401 Unauthorized` | API key missing or invalid | Ensure `OPENAI_API_KEY` points to a key valid for the target endpoint |
| No vectors generated | Embedding model name not recognized by endpoint | Use a model ID that the provider actually serves |
| Slow/rate-limited | Using a chat model as embedding model | Switch to a proper embedding model (dimensionality mismatch) |

### Provider configurations

**OpenAI (recommended)**
```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_EMBEDDING_MODEL="text-embedding-3-large"   # 3072 dims
# or: text-embedding-3-small (1536 dims) or text-embedding-ada-002 (1536 dims)
```

**OpenRouter**
```bash
export OPENAI_API_KEY="sk-or-..."   # your OpenRouter key
export OPENAI_BASE_URL="https://openrouter.ai/api/v1"
export OPENAI_EMBEDDING_MODEL="text-embedding-3-large"
```
OpenRouter forwards to whichever provider you've configured in your dashboard (typically OpenAI for embeddings). Works identically to direct OpenAI usage.

**NVIDIA NIM**
NIM hosts inference microservices. The default chat endpoint (`https://integrate.api.nvidia.com/v1`) **does not** expose embeddings. You must either:
- Deploy a dedicated NIM embedding microservice (e.g., `nvidia/nv-embedqa-e5-v5`) and point `OPENAI_BASE_URL` to its URL
- Or switch to OpenRouter/OpenAI for embeddings (simpler)

**Generic OpenAI-compatible server**
```bash
export OPENAI_API_KEY="any"           # or real key if provider requires it
export OPENAI_BASE_URL="http://localhost:11434/v1"   # Ollama example
export OPENAI_EMBEDDING_MODEL="nomic-embed-text"    # whatever your server serves
```

### Configuration workflow

1. **Verify key location**: GBrain MCP server inherits environment from Hermes. Ensure your key is in one of:
   - `~/.config/nim/.env` (if Hermes sources it)
   - `~/.env` (home-directory env file)
   - Exported in the shell that launches Hermes
   - Check with: `env | grep -i open` from the same session you start Hermes

2. **Test the endpoint manually** (before running GBrain):
   ```bash
   curl -s -H "Authorization: Bearer $OPENAI_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"input":"test","model":"'"$OPENAI_EMBEDDING_MODEL"'","encoding_format":"float"}' \
        "$OPENAI_BASE_URL/embeddings" | python3 -m json.tool | head -5
   ```
   Should return JSON with a `data` array containing an embedding vector. If not, fix endpoint config first.

3. **Configure GBrain** — set the three env vars **before** Hermes starts:
   - In `~/.hermes/config.yaml` under `mcp_servers.gbrain.env` (Hermes injects these into the MCP process)
   - Or system-wide in the shell environment (e.g., `~/.profile`, `~/.zshrc`)
   - GBrain reads them from its process environment; `~/.gbrain/config.json` **does not** control embedding endpoints

4. **Run embedding pass**:
   ```bash
   # After Hermes restarts and MCP is connected
   gbrain embed --stale   # embeds all pages without vectors
   gbrain stats          # verify: Embedded count should increase
   ```

5. **Search verification**:
   ```bash
   # Vector search (requires embeddings)
   gbrain search-vector "your query here --limit 5
   # Keyword fallback (always works)
   gbrain search "exact keyword"
   ```

### Systematic API key discovery (when user says "I already added it")

If a user claims they've entered their API key but it's not found in expected files, search systematically:
1. Check `~/.config/nim/.env` (primary location for NIM/OpenRouter keys)
2. Check `~/.env` (home-directory dotfile)
3. Check `~/.secrets/*` (common convention)
4. Check skill-local `.api_key` files: `~/.hermes/profiles/<profile>/skills/*/.api_key`
5. Grep user's home for partial key patterns or provider names: `rg -i "openrouter|nous|sk-or-" ~ 2>/dev/null | head`
6. Ask the user for the exact path they saved to — interactive prompts are often GUI-based and save to unexpected locations

### Success indicator

After successful configuration:
- `gbrain embed --stale` reports `embedded X pages` without errors
- `gbrain stats` shows non-zero `Embedded` count
- Vector search `gbrain search-vector "test"` returns ranked results
- No 404/401 errors in `gbrain` stderr