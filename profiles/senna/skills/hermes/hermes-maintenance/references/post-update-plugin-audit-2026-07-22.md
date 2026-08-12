# Post-Update Plugin Audit — 2026-07-22

Session: Post-`hermes update` audit of all plugins, git repos, and venv packages.

## Plugin Status Matrix

| Plugin | Type | Git? | Local = Origin | Behind Upstream | Latest | Action |
|--------|------|------|:---:|:---:|:---:|--------|
| hermes-lcm | context engine | ✅ | ✅ | 7 commits | v0.19.0 | `git pull upstream main` |
| icarus | memory | ✅ | ✅ | 0 | — | none |
| ponytail | plugin | ✅ | ✅ | 0 | — | none |
| web-search-plus | web search | ✅ | ❌ | 35 commits | v3.2.0 | `git pull origin main` |
| eikon | standalone | ❌ | — | — | v1.0.0 | none (bundled) |
| hermes-achievements | data | ❌ | — | — | — | none (bundled) |
| kanban-api | standalone | ❌ | — | — | v1.0.0 | none (bundled) |
| katana | security | ❌ | — | — | v1.0.0 | none (bundled) |
| session-api | standalone | ❌ | — | — | v1.0.0 | none (bundled) |
| mnemosyne | memory provider | pip | — | — | 3.14.0 | `uv pip install --upgrade mnemosyne-memory` |
| rtk-rewrite | entry point | pip | — | — | 1.2.3 | config ref only (no dir needed) |

## Key Findings

1. **hermes-lcm** has TWO remotes: `origin` (user fork) and `upstream` (canonical).
   Local is up-to-date with `origin` but 7 commits behind `upstream`.
   Upstream adds 2 new tools: `lcm_recall`, `lcm_recent`.

2. **web-search-plus** is 35 commits behind `origin` and at v3.0.2 (latest is v3.2.0).
   v3.2.0 adds Hound local search provider via MCP.

3. **rtk-rewrite** is in `plugins.enabled` config but has NO plugin directory.
   It's registered via Python entry points (`rtk-hermes` package in venv).
   This is CORRECT — entry-point plugins don't need a directory.
   Detection script: see §6c in SKILL.md.

4. **Non-git plugins** (eikon, katana, kanban-api, session-api) are bundled
   with Hermes and auto-updated. No manual git pull needed.

5. **mnemosyne-memory** is at 3.13.0 (latest 3.14.0). Minor version bump,
   no breaking changes. Upgrade with uv pip install.

## Update Commands (copy-paste)

```bash
# Hermes core (1 commit behind upstream)
cd ~/.hermes/hermes-agent && git pull origin main

# Hermes-LCM (7 commits behind upstream)
cd ~/.hermes/plugins/hermes-lcm && git pull upstream main

# Web Search Plus (35 commits behind origin, v3.0.2 → v3.2.0)
cd ~/.hermes/plugins/web-search-plus && git pull origin main

# Mnemosyne memory provider (3.13.0 → 3.14.0)
~/.local/bin/uv pip install --python ~/.hermes/hermes-agent/venv/bin/python --upgrade mnemosyne-memory

# RTK-Hermes (if wiped during update)
~/.local/bin/uv pip install --python ~/.hermes/hermes-agent/venv/bin/python --upgrade rtk-hermes
```

After all updates: `hermes gateway restart --profile senna`
