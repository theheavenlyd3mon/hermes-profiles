# iknowkungfu MCP Integration

iknowkungfu is a cross-agent skill registry (inspired by *The Matrix* "I know kung fu"). It connects via MCP as a stdio server, exposing 8 tools for skill discovery, inspection, and installation.

## Quick Reference

| Item | Value |
|------|-------|
| MCP binary | `~/.hermes/hermes-agent/venv/bin/iknowkungfu-mcp` |
| Version | 0.1.8 (as of 2026-05-15) |
| Compatible agents | Claude Code, Hermes, Codex, OpenCode |
| Registry size | 9 skills by samuelgudi |
| License | MIT |

## Querying the Registry Directly (stdin JSON-RPC)

The MCP server accepts JSON-RPC 2.0 requests on stdin. Useful when Hermes's MCP client doesn't surface the tools directly, or for testing:

```bash
# List categories
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_categories","arguments":{}}}' \
  | /path/to/iknowkungfu-mcp

# List tags
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"list_tags","arguments":{}}}' \
  | /path/to/iknowkungfu-mcp

# Search all skills
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search","arguments":{"query":""}}}' \
  | /path/to/iknowkungfu-mcp

# Get full SKILL.md
echo '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"get_skill","arguments":{"id":"samuelgudi/skill-name"}}}' \
  | /path/to/iknowkungfu-mcp

# Install a skill
echo '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"install_skill","arguments":{"id":"samuelgudi/adversarial-test-design"}}}' \
  | /path/to/iknowkungfu-mcp
```

## MCP Tool Schemas (8 tools)

| Tool | Purpose | Key Args |
|------|---------|----------|
| `search` | Search registry by keyword | `query`, `category`, `tags`, `agent` |
| `get_skill` | Fetch full SKILL.md + metadata | `id` (required), `version` |
| `get_skill_file` | Fetch a scripts/ or references/ file | `id`, `version`, `path` |
| `install_skill` | Install to local skills dir | `id` (required), `version`, `agent` |
| `list_categories` | Show categories with counts | none |
| `list_tags` | Show tags with counts | none |
| `list_agents` | Show agents with compatible skills | none |
| `update_registry` | Refresh registry.json + FTS5 index | none |

**Pitfall:** `install_skill` takes `id` (not `skill_id`) as the argument name. The ID format is `owner/skill-name` (e.g. `samuelgudi/adversarial-test-design`).

## Profile Isolation Path Quirk

Under profile isolation (senna profile), `install_skill` writes skills to the old pre-isolation path:
```
~/.hermes/profiles/senna/home/.hermes/skills/{category}/{skill-name}/
```

This path may not be picked up by Hermes's skill discovery. Hermes discovers skills from:
- `~/.hermes/hermes-agent/skills/` (repo-level)
- `~/.hermes/profiles/senna/skills/` (profile-level)

**Workaround:** After installing, copy/move the skill directory to the profile's skills path or symlink it.

## Registry Contents (as of 2026-05-15)

### Categories

| Category | Count |
|----------|-------|
| dev | 3 |
| meta | 2 |
| ops | 2 |
| docs | 1 |
| ai | 1 |

### All 9 Skills

| Skill | Category | Agent Compat | Description |
|-------|----------|-------------|-------------|
| adversarial-test-design | dev | Claude Code, Hermes | Tests that catch regressions, not just turn green |
| semver-bump-decider | dev | Claude Code, Hermes, Codex, OpenCode | Decides major/minor/patch with breaking-change checklist |
| keep-a-changelog | dev | Claude Code, Hermes | CHANGELOG format, six categories, unreleased discipline |
| caddy-local-https | ops | Claude Code, Hermes | Local dev HTTPS via Caddy reverse proxy |
| deployment-runbook | ops | Claude Code, Hermes | Structured deploy: pre-flight, steps, verify, rollback |
| lessons-learned-log | docs | Claude Code, Hermes | One-line-rule format for recording hard-won insights |
| session-handoff | ai | Claude Code, Hermes | Resuming work cleanly across sessions |
| iknowkungfu-discovery | meta | Claude Code, Hermes | Search & install skills from this registry mid-task |
| iknowkungfu-contribution | meta | Claude Code, Hermes | Submit/update/deprecate skills in the registry |

## How to Verify the MCP Server

```bash
# Check it's registered
hermes mcp list

# Test the connection (fastest way to confirm it's alive)
hermes mcp test iknowkungfu
```

Expected output from `test`:
```
Testing 'iknowkungfu'...
  Transport: stdio → /path/to/iknowkungfu-mcp
  Auth: none
  ✓ Connected (Nms)
  ✓ Tools discovered: 8
```

## Evaluating Skills for Registry Contribution

When deciding which local skills are worth contributing to iknowkungfu (or any cross-agent registry), use these criteria ranked by importance:

1. **Agent-agnostic** — Works with Claude Code, Codex, OpenCode, Hermes, not just one platform. Avoid skills that reference platform-specific tools (e.g., Hermes `delegate_task`, `search_files`) in their core workflow.
2. **Universal appeal** — Solves a problem every developer/agent faces (debugging, testing, planning, security).
3. **Documentation quality** — Has a well-structured SKILL.md with triggers, REDFLAGS, RATIONALIZATIONS, and verification steps.
4. **Gap-filling** — Not already covered by existing registry skills. Check `list_categories` + `search` before recommending.
5. **Methodology over toolchain** — The skill's value should be in its methodology/patterns, not in specific tool commands.

**Skills to exclude from contribution:**
- Platform-locked (Apple Skills, Windows-only)
- Agent-specific (Hermes-only plugin setup, TUI config)
- Session-narrative (single PR review, one-off fix)
- Too narrow (niche creative, specific game mod)
