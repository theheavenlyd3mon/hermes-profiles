# Comprehensive Health Audit

A holistic system health audit that goes beyond individual service checks. Captures the full configuration surface: Hermes config, .env hygiene, plugins, MCP, cron, skills inventory, Obsidian vault, knowledge bases, and orphan detection.

## When to Run

- User asks "check if everything is configured correctly"
- After an upgrade (especially cross-major: v0.9 → v0.10+)
- After environment changes (OS update, new profiles, plugin changes)
- Periodic health check (monthly)

## Audit Sequence (in order)

### Phase 1: Config & Credential Surface

```bash
# Profile inventory
hermes profile list

# Full component status
hermes status --all

# Diagnostic health check
hermes doctor

# Root config (shared across profiles)
cat ~/.hermes/config.yaml

# Profile config (profile-specific overrides)
cat ~/.hermes/profiles/<profile>/config.yaml

# Check for post-upgrade config section drops:
grep 'engine:' ~/.hermes/profiles/<profile>/config.yaml   # should be 'lcm' if LCM was set
grep -A5 '^plugins:' ~/.hermes/profiles/<profile>/config.yaml  # should list enabled plugins
grep -A5 '^memory:' ~/.hermes/profiles/<profile>/config.yaml    # should have provider set
grep -A10 '^security:' ~/.hermes/profiles/<profile>/config.yaml  # redact_secrets, tirith etc.
grep -A5 '^context:' ~/.hermes/profiles/<profile>/config.yaml    # engine

# Check for duplicate YAML keys (last occurrence wins — silent override):
grep -n 'provider:' ~/.hermes/profiles/<profile>/config.yaml | sort
grep -n 'engine:' ~/.hermes/profiles/<profile>/config.yaml | sort
# If any key appears more than once, the later one overrides the earlier one silently.
```

### Phase 2: .env Hygiene

Root `.env` (~/.hermes/.env) loads first and holds shared defaults. Profile `.env` (~/.hermes/profiles/<profile>/.env) overrides matching keys. This means a profile `.env` can **silently shadow** correct root values.

```bash
# Check which keys are set in BOTH files — profile overrides root
# Look for these particularly dangerous overrides:
grep -n 'OBSIDIAN_VAULT_PATH\|FABRIC_DIR\|WIKI_PATH' ~/.hermes/.env ~/.hermes/profiles/<profile>/.env

# Check for duplicate lines (harmless but messy):
grep -n 'API_SERVER_ENABLED\|GITHUB_TOKEN\|OPENAI_API_KEY' ~/.hermes/profiles/<profile>/.env | sort
# Duplicates: last occurrence wins

# Check for corrupted line-number-prefix artifacts (lines starting with N|):
head -5 ~/.hermes/profiles/<profile>/.env
# If lines begin with '1|', '2|', etc., the file was written from read_file offset output
```

**Pitfall: Profile .env overrides root .env.** The root `.env` holds canonical paths like `OBSIDIAN_VAULT_PATH`, `FABRIC_DIR`, and `WIKI_PATH`. If the profile `.env` sets these same keys, it isolates the profile from the shared vault, memory fabric, and wiki. Detect by checking for these keys in both files.

### Phase 3: Plugin & MCP Inventory

```bash
hermes plugins list           # Shows enabled/disabled plugins
hermes mcp list               # Shows configured MCP servers
ls ~/.hermes/plugins/         # All plugin directories on disk

# Check for MCP servers in config.yaml:
grep -A3 'mcp_servers:' ~/.hermes/config.yaml ~/.hermes/profiles/<profile>/config.yaml
```

**Orphan detection:** A plugin listed in `plugins.enabled` in config.yaml but with no corresponding directory on disk could be:
- A pip-installed entry-point plugin (no directory — check `~/.hermes/hermes-agent/venv/lib/python3.11/site-packages/` for dist-info)
- A stale config entry left after uninstall (remove from `plugins.enabled` list)

Verify pip-installed plugins:
```bash
~/.hermes/hermes-agent/venv/bin/python -c "import <package>; print('<package> imported OK')"
```

### Phase 4: Cron & Scheduling

```bash
hermes cron list --all         # All jobs, including disabled
hermes gateway status          # Gateway must be running for cron to fire
```

### Phase 5: Obsidian Vault Health

```bash
# Resolve the effective vault path:
# - From profile .env (if set, overrides root)
# - From root .env
# - Fallback: ~/Documents/Obsidian Vault
echo "OBSIDIAN_VAULT_PATH=$OBSIDIAN_VAULT_PATH"

# Verify vault exists and has the expected PARA structure:
ls "REAL_VAULT_PATH"
# Expected: 0-Inbox/, 1-Projects/, 2-Areas/, 3-Resources/, 4-Archive/, 
#            Daily Notes/, Memory/, Sessions/, Team-Wiki/, icarus/

# Check Icarus fabric directory has entries:
ls "REAL_VAULT_PATH/icarus/"  # Should have daily/ subdir and .md entries
```

### Phase 6: Knowledge Base Health

**LLM-Wiki:**
```bash
head -3 "$WIKI_PATH/SCHEMA.md"   # Confirm domain and conventions
head -5 "$WIKI_PATH/index.md"    # Check last-updated date and page count
wc -l "$WIKI_PATH/log.md"        # Count log entries (rotate at 500)
find "$WIKI_PATH" -name "*.md" -not -path "*/raw/*" | wc -l  # Total page count
```

**Team-Wiki:**
```bash
head -5 "$VAULT_PATH/Team-Wiki/index.md"  # Check for placeholder text like $(date) or "Total pages: 0"
find "$VAULT_PATH/Team-Wiki" -name "*.md" ! -name "README.md" | wc -l  # Actual content pages
```

Red flags for Team-Wiki:
- Contains literal `$(date +%Y-%m-%d placeholder)` instead of an actual date
- `Total pages: 0` when the filesystem shows content
- Empty subdirectories (only README.md stubs)

### Phase 7: Skills Inventory

```bash
hermes skills list               # All skills, check for stale/overlapping entries
```

Look for skills referencing components that no longer exist in the stack (e.g., GBrain-related skills after removal).

## Presentation Pattern

Group findings into three tiers:

1. **Critical** — Config errors, wrong paths, missing credentials that break functionality now
2. **Medium** — Duplicates, stale references, overrides that don't break but conflict with the intended setup
3. **Low** — Cosmetic issues, orphaned artifacts, formatting glitches

For each finding, include:
- What was found (with exact path, line number, and current value)
- Why it matters (how it affects behavior)
- The fix (one-liner or specific edit)

## Pitfalls

- **Profile .env silently overrides root .env** on OBSIDIAN_VAULT_PATH, FABRIC_DIR, WIKI_PATH. These are the most common cause of "my vault/icarus/wiki is empty" bugs.
- **Post-upgrade config section drops** — `plugins.enabled`, `context.engine`, `memory.provider` are the three sections Hermes v0.9→v0.10+ is known to drop during config regeneration.
- **Duplicate YAML keys** — Last occurrence wins silently. A `provider: mnemosyne` on one line and `provider: ""` later in the same section means memory falls back to built-in.
- **Pip-installed entry-point plugins** have no directory on disk — they register via Python entry_points.txt. Don't flag them as stale without checking the venv first.
- **.env files with line-number prefixes** (`N|` at start of each line) — these are corrupted from previous read_file write-backs. The env vars still load correctly (shell reads `KEY=VALUE`, ignoring the prefix), but they're a hygiene issue.
