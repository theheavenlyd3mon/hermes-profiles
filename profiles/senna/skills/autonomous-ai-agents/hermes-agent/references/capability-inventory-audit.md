# Capability Inventory Audit

Systematically catalog every plugin and skill installed across Hermes profiles, cross-reference against config, and assess cron-automation feasibility.

This is distinct from:
- `plugin-audit-methodology.md` (which focuses on detecting misplaced plugins)
- `comprehensive-health-audit.md` (which checks service health, .env hygiene, MCP, vaults)
- `service-audit-pattern.md` (which focuses on gateway/workspace)

This audit answers: *"What do I have installed, what can it do, and what can run on a schedule?"*

## When to Use

- The user asks "review all my plugins and skills"
- The user asks "compile cron jobs from my skills"
- Periodically (quarterly) to detect config/drift: unused skills, stale config entries, missing plugins
- Before installing new plugins — know what you already have

## Methodology

### Phase 1 — Catalog Plugins

Three locations to check:

```bash
# 1. Global plugins directory
ls -la ~/.hermes/plugins/

# 2. Profile plugins directory (overrides global in profile mode)
ls -la ~/.hermes/profiles/<profile>/plugins/

# 3. Check if profile plugins dir is symlinked to global
readlink ~/.hermes/profiles/<profile>/plugins/

# 4. Check config.yaml for enabled plugins
grep -A20 '^plugins:' ~/.hermes/profiles/<profile>/config.yaml
```

For each plugin found:

| Source | What It Means |
|--------|---------------|
| `plugin.yaml` on disk | Directory plugin — installed via `hermes plugins install` or manual copy |
| `pip` entry point (via entry_points.txt) | Pip-installed plugin (no dir on disk). Verify with: `$HERMES_VENV/bin/python -c "import pkg_resources; eps = list(pkg_resources.iter_entry_points('hermes_agent.plugins')); print([e.name for e in eps])"` |
| In config `plugins.enabled` but no dir AND no entry point | **Stale config entry** — was removed or never installed. Flag for cleanup |
| Symlinked dir | Profile shares global plugin set — update-proof but check after Hermes upgrades |

**Cross-reference check:** For each entry in `config.yaml plugins.enabled`, verify it exists as either a directory plugin or a pip entry-point plugin. Missing entries break silently — the config just ignores them.

### Phase 2 — Catalog Skills

Skills live at:
- `~/.hermes/skills/` (global, shared across profiles)
- `~/.hermes/profiles/<profile>/skills/` (profile-specific)
- `~/.hermes/profiles/<profile>/home/.hermes/skills/` (sandboxed home — legacy/stale location)

```bash
# All installed skills by category
find ~/.hermes/profiles/<profile>/skills/ -name 'SKILL.md' -maxdepth 3 | sort

# Count by category
for d in ~/.hermes/profiles/<profile>/skills/*/; do
  echo "$(basename $d): $(ls -1 "$d" 2>/dev/null | wc -l) skills"
done

# Or use the built-in skills listing
hermes skills list
```

For the user's style, organize findings in a **category table**:

| Category | Count | Notable Skills | Automation Potential |
|----------|-------|---------------|---------------------|

### Phase 3 — Catalog Cron Jobs

```bash
hermes cron list --all
hermes gateway status   # critical: cron fires through gateway
```

**Critical constraint:** Hermes cron jobs only fire when the gateway is running. `hermes gateway status` reveals whether automation is possible. If the gateway is stopped, all cron jobs listed below are dormant.

### Phase 4 — Automation Feasibility Assessment

For each skill, evaluate four dimensions:

| Dimension | Questions |
|-----------|-----------|
| **Risk** | Read-only (low) vs writes files (medium) vs deletes/creates state (high) |
| **Value** | Produces new information (high) vs prevents problems (medium) vs cosmetic (low) |
| **Complexity** | Single command (low) vs multi-step with approval (medium) vs LLM-heavy multi-tool (high) |
| **Prerequisites** | Gateway running? API keys set? CLI tools installed? |

**Tier structure for recommendations:**

| Tier | Criteria | Example |
|------|----------|---------|
| **Tier 1 — High Value, Low Risk** | Read-only or non-destructive, produces report, single command | Memory consolidation, session pruning, wiki lint |
| **Tier 2 — Moderate Value, Some Complexity** | Multi-step, needs LLM calls, produces synthesized output | Arxiv digest to wiki, security audit report |
| **Tier 3 — Niche / Conditional** | Requires specific setup or only useful in certain scenarios | Memory curator check, fabric curation |

### Phase 5 — Report Format

Structure the report as:

1. **Plugin inventory** — table of name, type (dir/pip), status (present/stale), notes
2. **Skill inventory by category** — table with categories, counts, highlights
3. **Cron job analysis** — tiered recommendations with schedule, job description, risk notes
4. **Constraints** — gateway status, missing prerequisites, stale config entries

## Pitfalls

- **Gateway dependency:** Always check `hermes gateway status` before recommending cron automation. Jobs registered via `hermes cron create` only fire with a running gateway.
- **Pip entry-point plugins are invisible to `find`:** `rtk-rewrite`, `icarus`, `disk-cleanup` may be installed via `pip` with no `plugin.yaml` on disk. Use the `pkg_resources` check in Phase 1 to find them, or check the venv's `entry_points.txt`.
- **Profile sandboxing:** In a profile context, `~/.hermes/plugins/` resolves to `~/.hermes/profiles/<profile>/plugins/`. A symlink to the global plugins dir is common for primary profiles (like Senna).
- **Git submodules may skew directory counts:** `find` descends into `.git/` — always exclude via `-not -path '*/\.git/*'`.
- **Skills in sandboxed home:** `~/.hermes/profiles/<profile>/home/.hermes/skills/` is a legacy location from when the shell `HOME` was masked. Skills there are functional but in a non-standard location. Flag for potential migration.
- **LLM-heavy cron jobs cost tokens:** Arxiv digest, security audit, wiki ingest — these call LLM APIs. Budget appropriately and prefer `no_agent=true` scripts where possible.

## Commands Reference

```bash
# Quick inventory dump
echo "=== Plugins ==="
hermes plugins list 2>/dev/null
echo ""
echo "=== Config plugins ==="
grep -A20 '^plugins:' ~/.hermes/profiles/senna/config.yaml
echo ""
echo "=== Cron Jobs ==="
hermes cron list 2>/dev/null
echo ""
echo "=== Gateway Status ==="
hermes gateway status 2>/dev/null
echo ""
echo "=== Skills By Category ==="
for d in ~/.hermes/profiles/senna/skills/*/; do
  name=$(basename "$d")
  count=$(find "$d" -name 'SKILL.md' -maxdepth 2 2>/dev/null | wc -l | tr -d ' ')
  echo "  $name: $count"
done
echo ""
echo "=== Skill Total ==="
find ~/.hermes/profiles/senna/skills -name 'SKILL.md' -maxdepth 3 2>/dev/null | wc -l
```
