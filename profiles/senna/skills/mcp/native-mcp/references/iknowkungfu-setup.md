# iknowkungfu Setup (Session-Specific Details)

## Installation

Install inside the Hermes venv so both `iknowkungfu-mcp` and the `kfu` CLI are on the venv's PATH:

```bash
cd ~/.hermes/hermes-agent
source venv/bin/activate
pip install iknowkungfu
```

The binaries land at:
- `venv/bin/iknowkungfu-mcp` — MCP server binary
- `venv/bin/kfu` — CLI for registry operations

## MCP Config

### Without Profile Isolation

Add to `~/.hermes/config.yaml` using an **absolute path** to the venv binary:

```yaml
mcp_servers:
  iknowkungfu:
    command: ~/.hermes/hermes-agent/venv/bin/iknowkungfu-mcp
    enabled: true
```

### With Profile Isolation (Senna's setup)

Under the `senna` profile, `HERMES_HOME` is set to `~/.hermes/profiles/senna/`, so `load_config()` reads from **`~/.hermes/profiles/senna/config.yaml`** — NOT the global config, and NOT the HOME-scoped config in `senna/home/`.

**File:** `~/.hermes/profiles/senna/config.yaml`

```yaml
mcp_servers:
  iknowkungfu:
    command: ~/.hermes/hermes-agent/venv/bin/iknowkungfu-mcp
    enabled: true
```

**Verify the correct location for your setup:**

```bash
source ~/.hermes/hermes-agent/venv/bin/activate
python3 -c "
from hermes_cli.config import load_config, get_config_path
print('Config path:', get_config_path())
"
```

The printed path is the one file that needs the `mcp_servers` entry.

### After Config Change

**Critical:** Restart the gateway after adding/modifying the entry — MCP tools only load at startup. Until then, `mcp_iknowkungfu_*` tools won't appear or be callable.

**Preferred (launchd-managed):**
```bash
source ~/.hermes/hermes-agent/venv/bin/activate
hermes gateway start
```
This registers or reloads the service under launchd and returns immediately.

**Alternative (foreground, blocks):**
```bash
source ~/.hermes/hermes-agent/venv/bin/activate
hermes gateway run --replace
```
This kills any running instance and starts a new one in the foreground. Use in a dedicated terminal session or with `background=true` / tmux — it never exits on its own.

## Verification (Preferred — CLI Tools)

### 1. Check registry status

```bash
source ~/.hermes/hermes-agent/venv/bin/activate
hermes mcp list
```

Expected output: `iknowkungfu` listed with `✓ enabled` status.

### 2. Test connection & tool discovery

```bash
source ~/.hermes/hermes-agent/venv/bin/activate
hermes mcp test iknowkungfu
```

Expected output: `✓ Connected (< 500ms)`, `✓ Tools discovered: 8`.

### 3. Systematic health check (all layers)

Run these in order when troubleshooting:

| Layer | Command | Expected |
|-------|---------|----------|
| Package | `pip3 show iknowkungfu` | Version shown |
| Binary | `ls -la $(which iknowkungfu-mcp)` | File exists |
| Config | `grep -A 3 iknowkungfu ~/.hermes/profiles/senna/config.yaml` | `enabled: true` |
| Status | `hermes mcp list` | `✓ enabled` |
| Connection | `hermes mcp test iknowkungfu` | `✓ Connected`, tools count |

### kfu CLI Commands

All `kfu` commands require the venv activated:

```bash
source ~/.hermes/hermes-agent/venv/bin/activate

# Update registry (sync latest skills)
kfu update

# Search by keyword
kfu search "python web"

# Search by category (ai, dev, docs, meta, ops)
kfu search "category:dev"

# List installed skills
kfu list
```

## Tools Available After Restart

8 tools discovered (as of 2026-05-15):

- `mcp_iknowkungfu_search` — search the skill registry
- `mcp_iknowkungfu_get_skill` — inspect a skill by name
- `mcp_iknowkungfu_get_skill_file` — retrieve a specific file from a skill
- `mcp_iknowkungfu_install_skill` — install a skill
- `mcp_iknowkungfu_list_categories` — list all categories
- `mcp_iknowkungfu_list_tags` — list all tags
- `mcp_iknowkungfu_list_agents` — list supported agent hosts
- `mcp_iknowkungfu_update_registry` — refresh the registry from upstream

## Post-Update Binary Recovery

`hermes update` runs `uv` cache cleanup that **can clear pip-installed binaries** from the venv, including `iknowkungfu-mcp` and `kfu`. After every update:

```bash
ls -la ~/.hermes/hermes-agent/venv/bin/iknowkungfu-mcp 2>/dev/null || echo "MISSING — reinstall needed"
```

If missing:
```bash
cd ~/.hermes/hermes-agent && source venv/bin/activate && pip install iknowkungfu
```

Then restart the gateway to pick up the restored MCP server:
```bash
hermes gateway restart --profile senna
```

## Troubleshooting

### "MCP server not showing up" / tools not discovered

1. **Check binary exists at configured path:**
   ```bash
   ls -la ~/.hermes/hermes-agent/venv/bin/iknowkungfu-mcp
   ```
   If missing: `pip install iknowkungfu` in the venv.

2. **Config points to wrong venv path** — common after profile migration. The config should point to the MAIN venv, not a profile-scoped path:
   ```yaml
   # WRONG — profile-scoped path doesn't exist
   command: ~/.hermes/profiles/senna/hermes-agent/venv/bin/iknowkungfu-mcp
   
   # RIGHT — main venv
   command: ~/.hermes/hermes-agent/venv/bin/iknowkungfu-mcp
   ```

3. **Restart gateway after config changes** — MCP tools only load at startup.

4. **Profile isolation tilde expansion** — see `hermes-mcp-profile-isolation` skill. Under profile isolation, `~` expands to the profile HOME, not real HOME. Always use absolute paths.

## Registry Status

- **9 skills** registered (as of 2026-05-15)
- Categories: `ai` (1), `dev` (3), `docs` (1), `meta` (2), `ops` (2)
- All by **samuelgudi**, all MIT-licensed
- All support `hermes` and `claude-code`; `semver-bump-decider` also supports `codex`/`opencode`
- **No skills installed** by default — install via `kfu install <author>/<skill>`

### Available by Category

#### dev (3)
| Skill | Version | Description |
|-------|---------|-------------|
| `samuelgudi/semver-bump-decider` | v0.1.1 | Decide major/minor/patch bump from change classes; covers 0.x and pre-1.0 conventions |
| `samuelgudi/adversarial-test-design` | v0.1.0 | Write tests that catch regressions — real inputs, mock discipline, false-green detection |
| `samuelgudi/keep-a-changelog` | v0.1.0 | Maintain CHANGELOG per Keep a Changelog format; six change categories |

#### ops (2)
| Skill | Version | Description |
|-------|---------|-------------|
| `samuelgudi/caddy-local-https` | v0.1.0 | Caddy reverse proxy for local HTTPS; .localhost domains, path-based routing |
| `samuelgudi/deployment-runbook` | v0.1.0 | Structured deploy procedures; pre-flight, verify, rollback |

#### docs (1)
| Skill | Version | Description |
|-------|---------|-------------|
| `samuelgudi/lessons-learned-log` | v0.1.0 | One-line-rule format for recording hard-won insights so they aren't rediscovered |

#### ai (1)
| Skill | Version | Description |
|-------|---------|-------------|
| `samuelgudi/session-handoff` | v0.1.0 | Resume work cleanly across context limits; handoff doc structure, what state to capture |

#### meta (2)
| Skill | Version | Description |
|-------|---------|-------------|
| `samuelgudi/iknowkungfu-discovery` | v0.2.0 | Search/install skills from this registry mid-task |
| `samuelgudi/iknowkungfu-contribution` | v0.2.0 | Submit, deprecate, or yank a skill in the registry |

### Tags Available

`release`, `changelog`, `iknowkungfu`, `registry`, `semver`, `versioning`, `agent-workflow`, `caddy`, `context-window`, `continuity`, `contribution`, `deployment`, `discovery`, `documentation`, `handoff`, `https`, `knowledge-management`, `lessons-learned`, `local-dev`, `localhost`, `mocks`, `ops`, `postmortem`, `procedure`, `quality`, `regression`, `release-notes`, `resume`, `retrospective`, `reverse-proxy`, `rollback`, `runbook`, `search`, `session`, `submit`, `tdd`, `test-design`, `testing`, `tls`
