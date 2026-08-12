# Hermes → AgentUnreal: component map and port order

Condensed from the deep architecture review (full doc:
`~/Desktop/ue-agent-harness/HERMES_ARCHITECTURE_REVIEW.md`). Use this
when picking the *next* harness capability — replaces guessing from the loose
"next frontier" list in SKILL.md.

## Big surprises (read these first)

1. **Hermes already ships `optional-mcps/unreal-engine/manifest.yaml`** — Epic's
   official in-editor MCP server (UE 5.8+, HTTP `127.0.0.1:8000/mcp`,
   experimental). The file bridge in `tools/bridge.py` is a workaround for the
   same problem Epic now solves natively. Don't sink more time into the file
   bridge; the MCP swap is the long-term shape.
2. **`agent.py:241` violates role alternation.** The build-retry loop injects a
   synthetic `user` message between tool results. Hermes's AGENTS.md explicitly
   forbids this — breaks strict user/assistant alternation and invalidates
   prompt cache. Fold the retry hint into a tool result or the next assistant
   turn instead.
3. **`AGENTU_COMPARISON.md` compares against the wrong reference** (Hemanth
   HM's `agentu` PyPI package, not Hermes). Its top borrows (subprocess
   sandboxing, declarative workspace, code mode) are not what Hermes itself
   prioritizes. Skills/plugins/cron/profiles — the four biggest Hermes wins —
   aren't on its list.
4. **Hermes's "narrow waist" doctrine**: every core tool ships on every API
   call, so new capability arrives as CLI+skill / gated tool / plugin / MCP —
   NOT as a new core tool. AgentUnreal should keep its 11 tools and grow via
   plugins + skills, not via `_build_tool_registry`.
5. **`on_event` is already 90% of a plugin bus.** Single callable
   `(event_type, **kw)`. Hermes's plugin system = this + fan-out to N
   subscribers + a YAML manifest. One decorator away.

## Top 10 missing components (ranked by impact, with LOC estimate)

| # | Component | Why it matters for UE | ~LOC |
|---|---|---|---|
| 1 | **Skills system** (`skills/<domain>/<name>/SKILL.md` + `skills_list` / `skill_view`) | Self-growing backbone. Captures project-specific conventions (`skills/murim-souls/combat-attributes.md`) so the agent stops re-deriving them. | 80 |
| 2 | **Approval v2** (enforce `dry_run`→`write_file`, real `ask` prompt) | Today `dry_run` is system-prompt convention only — `_call_tool` doesn't check. An agent that hallucinates past it writes unconditionally. Track `(path, content_hash)` of last dry_run; reject mismatched write_file. Replace `ask`-mode error string with `input(f"Approve {name}? [y/N] ")`. | 30 |
| 3 | **Profile isolation** (`~/.agentunreal/profiles/<name>/`) | Natural unit = one uproject. Today memory.db / sessions / progress.md / config all live in the repo dir → one flat state across projects, can't pip-install once. | 40 |
| 4 | **Memory lifecycle hooks** (`prefetch` / `sync_turn` / `on_session_end`) | Memory is currently recall-once-at-start, remember-once-at-end. Misses per-turn prefetch, session-end flush, pre-compress snapshot, per-project scoping. Mnemosyne supports scopes already — one config flag away. | 150 |
| 5 | **Context compressor** (token budget, drop middle) | Build-fix loops blow context: UBT stdout is 5–50KB per attempt, 5+ attempts for a stubborn linker error. `max_iterations=10` won't save you — context window dies first. Estimate `sum(len(m.content))//4`; when >100KB drop messages [2:-6] and replace with a one-line summary. Also cap `parse_build_errors` output. | 60 |
| 6 | **Plugin system** (`plugins/<name>/plugin.yaml` + `__init__.py` with hooks) | The structural answer to "self-growing." Perforce, Rider handoff, asset auditing, nightly summarizer — all become drop-in dirs, not edits to `agent.py`. | 100 |
| 7 | **Cron / scheduled jobs** | Nightly clean rebuild + test + report; hourly Perforce asset scan; pre-commit build-all. Without cron the harness is request-driven only. Single `tick()` + `launchd` every minute. | 80 |
| 8 | **MCP server** (`mcp_serve.py`-style, FastMCP stdio) | Flips the relationship — Cursor / Claude Code / Hermes itself can call `agentunreal_run_task(...)`. Expose 3 tools: `run_task`, `build_module`, `scan_project`. | 40 |
| 9 | **Provider fallback chain + jittered retry** | Long unattended build loops hit 429s. Today `llm.py` raises on unknown provider, no retry. `llm.fallbacks: [...]` in config + walk on RateLimitError. | 30 |
| 10 | **`delegate_task` subagent** | Fan-out patterns (12 Blueprints → C++ base classes; run 5 automation tests in parallel). Restrict child toolset, cap spawn depth, return only final summary to parent. | 60 |

Total: ~670 LOC for the full "Hermes-shaped but UE-focused" skeleton.

## Hermes things NOT to port (over-engineering for a solo UE harness)

- `toolset_distributions.py` — RL training-batch randomization, not needed.
- `gateway/platforms/` (~20 messaging adapters) — Discord webhook plugin suffices.
- `tui_gateway/server.py` (560K) — Electron RPC transport. Textual TUI already covers the local case; AgentUnreal's 30-line `call_from_thread` pattern is correct.
- `acp_adapter/` — Zed's ACP. MCP server (#8) covers the same use case more broadly.
- `agent/learning_graph.py`, `curator.py`, `insights.py` — self-improvement viz. Downstream of having skills at all; revisit after #1 lands.
- `tools/environments/{docker,modal,singularity,daytona,ssh}` — UE builds need a local Windows box; Dockerizing UBT is a separate yak-shave.
- `agent/credential_pool.py`, OAuth flows — enterprise multi-cred rotation.
- `agent/i18n.py`, `locales/` — English-only is fine.
- `tools/computer_use/`, `tools/browser_*` — UE editor already has the file bridge + soon the official MCP.
- `batch_runner.py` — RL trajectory gen. Only if you start fine-tuning.
- All 8 memory backends under `plugins/memory/` — pick one (Mnemosyne is already wired); the ABC matters, not the zoo.

## Sequencing (ponytail order — stop when it stops paying)

1. Skills (#1) → unlocks self-growing
2. Approval v2 (#2) → closes the dry_run-enforcement hole
3. Profile isolation (#3) → moves state out of the repo
4. Memory lifecycle (#4) → better recall per turn
5. Context compressor (#5) → necessary once sessions get long
6. Plugin system (#6) → structural growth vector
7. Cron (#7) → autonomy
8. MCP server (#8) → lets other tools drive AgentUnreal
9. Fallback chain (#9) → reliability for unattended runs
10. Delegate task (#10) → last; depends on #5 and #9 to be safe

## Concrete bug to fix first (independent of the 10)

**`agent.py:241`** — build-retry currently does:

```python
messages.append({"role": "user", "content": f"Build failed (attempt {n}/{m})..."})
break
```

This is a synthetic user message between tool results — violates strict
user/assistant alternation and invalidates prompt cache. Replace with: append
the retry hint as a *tool result* on the `build_module` tool_call_id (the
existing tool message), or fold it into the assistant's next-turn content. Do
not introduce a new `user` role mid-loop.
