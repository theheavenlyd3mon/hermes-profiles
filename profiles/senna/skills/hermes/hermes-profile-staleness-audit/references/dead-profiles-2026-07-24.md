# Dead Profile Audit — 2026-07-24

## Profiles with no config.yaml or .env (empty shells)

| Profile | config.yaml | .env | state.db | gateway | Verdict |
|---------|-------------|------|----------|---------|---------|
| `mlops` | ❌ | ❌ | ❌ | ❌ | CANDIDATE-FOR-REMOVAL — completely empty |
| `business` | ❌ | ❌ | ❌ | ❌ | CANDIDATE-FOR-REMOVAL — only .env.bak + SOUL.md |
| `designer` | ✅ | ❌ | ✅ | ❌ | STALE — no gateway, no .env |
| `researcher` | ✅ | ❌ | ✅ | ❌ | STALE — no gateway, no .env |
| `architect` | ✅ | ❌ | ✅ | ❌ | STALE — no gateway, no .env |
| `secretary` | ✅ | ❌ | ✅ | ❌ | STALE — no gateway, no .env |

## Profiles with config.yaml but no gateway

These profiles have config and state.db but no gateway directory — they cannot
receive Discord messages or run as messaging agents.

| Profile | gateway | platforms | state.db size | Verdict |
|---------|---------|-----------|---------------|---------|
| `media` | ❌ | ❌ | 4.0K | STALE — no gateway, tiny state |
| `homelab` | ❌ | ❌ | 0B | STALE — no gateway, empty state |
| `social` | ❌ | ❌ | 4.0K | STALE — no gateway, tiny state |
| `cyber-blue` | ❌ | ❌ | 748K | DORMANT — no gateway but has state |
| `cyber-red` | ❌ | ❌ | 916K | DORMANT — no gateway but has state |

## Profiles with gateways but potential issues

| Profile | gateway_state | api_server | discord | Verdict |
|---------|---------------|------------|---------|---------|
| `senna` | running | fatal (port 8645 in use) | connected | ACTIVE — but api_server broken |
| `code` | running | — | — | ACTIVE |
| `creative` | running | — | — | ACTIVE |
| `finance` | running | — | — | ACTIVE |
| `infra` | running | — | — | ACTIVE |
| `knowledge` | running | — | — | ACTIVE |
| `novel` | running | — | — | ACTIVE |
| `research` | running | — | — | ACTIVE |
| `security` | running | — | — | ACTIVE |

## Recommendation

1. **Remove** `mlops` and `business` — completely empty, no config, no state.
2. **Activate or remove** `designer`, `researcher`, `architect`, `secretary` —
   they have config.yaml but no .env or gateway. If not needed, remove.
3. **Fix api_server port conflict** on senna — port 8645 is in use by another
   process. Change to 8646 in config.yaml.
4. **Check** `media`, `homelab`, `social` — tiny state.db (4K or 0B) suggests
   minimal usage. Consider consolidating their cron jobs onto active profiles.
