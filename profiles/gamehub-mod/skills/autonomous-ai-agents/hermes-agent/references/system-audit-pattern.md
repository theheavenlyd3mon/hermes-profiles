# Comprehensive System Audit Pattern

A multi-component health check across all major Hermes subsystems. Broader than the
port/service audit (`service-audit-pattern.md`) and plugin location audit
(`plugin-audit-methodology.md`) — this covers config, env paths, plugins, skills,
MCP, cron, Obsidian vault, LLM-Wiki, Team-Wiki, and orphaned components.

## When to Run

- User asks "check if everything is correctly established"
- After a Hermes upgrade (v0.9 → v0.10+)
- After profile reconfiguration
- When something feels off but the error isn't obvious
- Periodic maintenance check

## Audit Sequence

### Phase 1: Shell & Config Health

```bash
# Core config path
hermes config path
cat ~/.hermes/profiles/senna/config.yaml  # or the active profile

# .env paths and line counts
hermes config env-path
wc -l ~/.hermes/.env                      # root (shared defaults)
wc -l ~/.hermes/profiles/senna/.env       # profile (overrides)

# Profiles overview
hermes profile list

# Comprehensive status
hermes status --all
hermes doctor

# Plugins inventory
hermes plugins list
hermes mcp list
hermes cron list --all
hermes skills list
```

### Phase 2: Profile Env Path Verification

**Critical check:** Profile `.env` values override root. Verify path variables point
to the real locations, not template defaults.

```bash
# Check each path variable for root vs profile override
echo "=== OBSIDIAN_VAULT_PATH ==="
grep OBSIDIAN_VAULT_PATH ~/.hermes/.env
grep OBSIDIAN_VAULT_PATH ~/.hermes/profiles/senna/.env

echo "=== FABRIC_DIR ==="
grep FABRIC_DIR ~/.hermes/.env
grep FABRIC_DIR ~/.hermes/profiles/senna/.env

echo "=== WIKI_PATH ==="
grep WIKI_PATH ~/.hermes/.env
grep WIKI_PATH ~/.hermes/profiles/senna/.env

# Verify the actual target directories have content
echo "=== Actual vault content ==="
ls "~/Hermes Vault/Hermes/" 2>/dev/null
echo "=== Profile vault content ==="
ls ~/.hermes/profiles/senna/vault/ 2>/dev/null
```

**Rule:** Path variables belong in root `.env` as single source of truth. Profile
overrides should be INTENTIONAL (different vault per profile), not accidental
template duplication.

### Phase 3: Config Integrity (Post-Upgrade)

Check for sections that Hermes upgrades silently drop:

```bash
# Context engine (should be 'lcm' if using LCM)
grep 'engine:' ~/.hermes/profiles/senna/config.yaml

# Plugins enabled list
grep -A20 '^plugins:' ~/.hermes/profiles/senna/config.yaml | grep "^  - "

# Memory provider
grep -A5 '^memory:' ~/.hermes/profiles/senna/config.yaml | grep provider

# Security toggles
grep 'redact_secrets\|redact_pii\|approvals.mode' ~/.hermes/profiles/senna/config.yaml
```

Watch for **duplicate key** bugs where a key appears twice in config (last wins):

```bash
grep -n 'provider:' ~/.hermes/profiles/senna/config.yaml | grep -v '^.*:auto$' | grep -v deepseek
```

If a key appears twice (e.g., `provider: mnemosyne` followed by `provider: ""`),
the second value silently overrides the first. Remove the spurious duplicate.

### Phase 4: Plugin & MCP Validation

```bash
# List every plugin from config and verify it exists
grep -A20 '^plugins:' ~/.hermes/profiles/senna/config.yaml | grep "^  - " | sed 's/  - //' | while read plugin; do
  found=$(find ~/.hermes/plugins ~/.hermes/profiles/senna/plugins -maxdepth 2 -name "plugin.yaml" 2>/dev/null | grep -i "$plugin")
  entrypoint=$(cat ~/.hermes/hermes-agent/venv/lib/python3.11/site-packages/*.dist-info/entry_points.txt 2>/dev/null | grep "$plugin")
  if [ -n "$found" ]; then
    echo "OK (git-plugin): $plugin → $found"
  elif [ -n "$entrypoint" ]; then
    echo "OK (entry-point pip plugin): $plugin"
  else
    echo "STALE: $plugin in config but no plugin.yaml or entry point found"
  fi
done

# MCP servers
hermes mcp list
# Also check root config.yaml for mcp_servers (hermes mcp list may not show all)
grep -A10 'mcp_servers:' ~/.hermes/config.yaml 2>/dev/null
```

### Phase 5: Vault & Wiki Health

```bash
# Vault structure
ls "~/Hermes Vault/Hermes/"

# Icarus fabric: has entries?
ls "~/Hermes Vault/Hermes/icarus/" | wc -l

# Memory notes present?
ls "~/Hermes Vault/Hermes/Memory/"

# LLM-Wiki: SCHEMA + index + pages
ls "~/Hermes Vault/Hermes/llm-wiki/"
head -5 "~/Hermes Vault/Hermes/llm-wiki/index.md"  # page count
wc -l "~/Hermes Vault/Hermes/llm-wiki/index.md"    # how many entries

# Team-Wiki: SCHEMA + index + pages
ls "~/Hermes Vault/Hermes/Team-Wiki/"
# Check if index has placeholder text (sign of empty wiki)
grep 'placeholder\|Total pages: 0' "~/Hermes Vault/Hermes/Team-Wiki/index.md"
```

### Phase 6: Check for Orphaned Components

Components configured but no longer in use:

- **GBrain:** Check root config.yaml for `mcp_servers.gbrain`; check `~/.hermes/plugins/gbrain/`
- **Deactivated plugins:** Check `hermes plugins list` for `not enabled` entries
- **Stale cron jobs:** Check `hermes cron list --all` for jobs whose purpose is abandoned
- **Stale skills:** Skills that reference removed tools or deprecated architectures

## Presentation

After completing the audit, present findings organized by severity:

```
## ✅ Correctly Configured
[Table of working components with brief status]

## 🚨 Critical (needs fix)
[Items that break functionality — wrong paths, missing config sections]

## ⚠️ Medium
[Functional issues but not blocking — duplicates, formatting artifacts]

## 🔧 Low / Cleanup
[Polish items — unused config, placeholder text, cosmetic issues]
```

## Common Findings

| Finding | Severity | Fix |
|---------|----------|-----|
| Profile .env overrides root vault paths incorrectly | Critical | Remove override lines from profile `.env` |
| Post-upgrade config drops plugins.enabled list | Critical | Re-add plugins to config.yaml |
| Post-upgrade context engine reset to `compressor` | Critical | Set `context.engine: lcm` |
| Duplicate API_SERVER_ENABLED lines | Low | Remove one |
| Team-Wiki with placeholder `$(date)` in index | Low | Update with real content |
| GBrain MCP server in config but GBrain removed | Low | Remove mcp_servers entry + plugin dir |
| Skin mismatch (config says senna, user uses oni) | Low | Update config or note as preference |
