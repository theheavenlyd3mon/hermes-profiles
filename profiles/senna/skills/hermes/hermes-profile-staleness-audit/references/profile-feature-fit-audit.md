# Profile × Feature-Fit Audit (2026-07-28)

Technique for "which profiles should have which Hermes features" audits — MCP servers, plugins, built-in skills, hub catalog. Distinct from staleness (activity/disk) and skill-library (content overlap) audits.

## Headline pattern found

Fleet configs were CLONES: all 23 profiles shared one config.yaml template — same `mcp_servers` (codegraph + iknowkungfu), same 16-entry `plugins.enabled`, same voice/tts/stt/image_gen. Differentiation lived ONLY in `skills/` + `SOUL.md`. So a feature audit reduces to: (a) prune per-profile bloat, (b) make MCP fit intentional, (c) targeted hub adds.

## Procedure

1. **Inventory** per profile: list `skills/`, `plugins/`, `cron/`, `memories/`, and config.yaml/SOUL.md presence+sizes. (`os.listdir` loop; skip dotfiles `.bundled_manifest`, `.usage.json*`, `.curator_*`, `.hub`.)
2. **Parse configs in Python, not grep.** `yaml.safe_load` each config; sections may be dict OR list — normalize with an `enabled_map()` helper (dict: key→enabled flag/bool; list: all-on). Extract `mcp_servers`, `plugins.enabled`, `toolsets`, and flags (`voice/tts/stt/image_gen/x_search/computer_use/lsp` — values may be dicts; use `v.get('enabled', ...)`).
3. **Diff against a baseline profile** to find real per-profile deltas (e.g. only `image-studio` on creative/social and `ponytail` on senna differed from the fleet baseline).
4. **Hub catalog**: `hermes skills search '<q>' --source official --limit 200 --json`. ALWAYS filter `--source official` — the unfiltered catalog is mostly low-quality community noise (hundreds of junk entries). Empty query `''` returns the full official set (~50).
5. **codegraph fit check**: codegraph MCP spawns a process + advertises ~10 tools per session; only useful where a codebase gets indexed. Enabled fleet-wide = dead weight on non-code profiles.
6. **Report shape**: headline structural finding → fleet-wide issues (numbered F1..Fn) → per-profile ADDS (official hub only) → per-profile TRIMS → MCP fit matrix → numbered task list for batched user approval (user's preferred style: "1-8: yes/no/more"). Read-only until approved.

## Pitfalls

- `c.get('plugins')` shape is `{enabled: [...], disabled: [...]}` — a naive key-loop reports the literal strings "enabled"/"disabled" as plugin names.
- `toolsets` was a LIST in these configs, not a dict — `.items()` crashes. Normalize first.
- Config top-level keys are nearly identical across profiles (generated defaults); key-presence tells you nothing. Only parsed VALUES + plugin/skill diffs carry signal.
- Missing SOUL.md + zero skills + missing memories/ but cron locks present = husk profile (found: `secretary`) — flag build-or-archive, don't assume it's active.
- Roster drift: orchestrator TEAM roster said `book-writer` but dir was `novel`; `educate`/`gamehub-mod`/`secretary` absent from roster. Reconcile roster vs disk during the audit.
- Full audit report from this session: `~/profile-feature-audit-2026-07-28.md` (includes per-profile trim lists and the official-hub add matrix).
