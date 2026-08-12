# Integrating production agent patterns into a UE harness

Session: 2026-07-16. Reviewed three popular agent repositories and mapped the
useful parts onto the `ue-agent-harness` milestone.

## Repositories reviewed

- `Shubhamsaboo/awesome-llm-apps` — 100+ runnable apps, good for quick
  adaptation and seeing the MCP/multi-agent/always-on patterns in code.
- `NirDiamant/agents-towards-production` — production-grade tutorials on
  memory, guardrails, deployment, security, and observability.
- `microsoft/ai-agents-for-beginners` — 18-lesson course covering design
  patterns (tool use, RAG, planning, multi-agent, metacognition, production,
  protocols, memory, security).

## What applies directly to the UE harness

### 1. Tool schema generation (from `microsoft/ai-agents-for-beginners` / `agentu`)

Hand-coding `_tool_schemas()` in `agent.py` is brittle. Prefer one of these:
- Derive OpenAI-style tool schemas from function signatures and docstrings
  (the `awesome-llm-apps` and `agentu` approach).
- Keep one JSON schema per tool file and load it at startup.

Benefit: adding a new tool is one file change, not a schema edit + registry
edit + test edit.

### 2. MCP support (from `awesome-llm-apps` and `agents-towards-production`)

The harness already has a bridge concept. Wrapping it behind MCP gives it:
- External tools (finance APIs, web search, GitHub) without writing a new
  wrapper per service.
- A standard protocol that other agents can consume.
- Easier integration with coding agents (Claude Code, Codex, Cursor) that can
  install MCP servers.

Implementation path: add a feature flag `mcp.enabled: true` in `config.yaml`,
start a small MCP server that exposes the file/build/editor tools, and let the
agent connect to it as a client when external tools are needed.

### 3. Persistent memory with auto-recall (from `agents-towards-production`)

The current harness uses Mnemosyne but only session-scoped recall. Production
agent patterns call for:
- Pre-task memory retrieval: `memory_recall(user_request)` before the first LLM
  call.
- Post-task memory storage: `memory_remember(task_summary, source="agent")`
  after success.
- Project-level memory: conventions, naming rules, previously rejected
  approaches, common build fixes.

Keep memory optional (feature flag), but when enabled it should be automatic,
not a tool the LLM has to remember to call.

### 4. Security guardrails (from `agents-towards-production` and `microsoft/ai-agents-for-beginners`)

Minimum viable guardrails for a UE harness:
- **Path sandboxing:** `write_file` and `dry_run` must reject paths that resolve
  outside the project root.
- **Dangerous operation approval:** deleting files, force-rebuilding, or running
  editor commands that mutate the project should require explicit user
  approval or a `--dangerous` flag.
- **Output validation:** reject generated code that includes unsafe macros,
  absolute paths, or engine-private headers that are not in the project.

### 5. Multi-agent / specialist split (from `awesome-llm-apps` and `microsoft/ai-agents-for-beginners`)

A single ReAct loop is fine for v1, but as the harness grows, split into:
- **Planner:** reads the task, scans the project, produces a plan.
- **Coder:** writes the actual C++ files.
- **Builder:** runs UBT, parses errors.
- **Verifier:** checks style, tests, and editor state.

This is a future architecture note, not a v1 requirement. The harness should
keep the door open by making the tool registry easy to partition.

### 6. Always-on / scheduled agents (from `awesome-llm-apps`)

Once the build loop works, a background mode can:
- Watch for build failures and retry.
- Poll source control and propose merges.
- Monitor editor crashes and restart the bridge listener.

Use cron or a lightweight scheduler; keep it behind a feature flag.

### 7. Evaluation harness (from `agents-towards-production`)

Before tuning prompts or adding features, measure:
- Build success rate for a fixed set of tasks.
- File change correctness (did it write the right file, in the right module,
  paired with a matching `.cpp` / `.h`).
- Retry count distribution.

A simple JSONL eval runner is enough: run the agent on N tasks, record success /
retry / error, and compare before/after prompt changes.

## Recommended upgrade order

1. Fix the LLM client to respect config (pass `Config` into `LLM`).
2. Generate tool schemas from code instead of hand-coding them.
3. Add path sandboxing and dangerous-operation approval.
4. Make memory auto-recall/auto-remember when enabled.
5. Implement the real `max_build_retries` loop.
6. Add MCP client support as a feature flag.
7. Add a minimal eval harness and run it before prompt changes.
8. Later: split into planner/coder/builder/verifier agents.

## Mapping to the harness files

| Upgrade | Files touched |
|---------|---------------|
| Config-driven LLM | `llm.py`, `agent.py` |
| Tool schema generation | `tools/__init__.py`, `agent.py` |
| Path guards | `tools/file.py`, `tools/build.py` |
| Auto memory | `agent.py`, `tools/memory.py` |
| Build retry loop | `agent.py` |
| MCP client | new `tools/mcp.py`, `config.yaml` |
| Eval harness | new `eval_runner.py` |

## Key insight

The harness is already a reasonable v1. The highest-value next work is not more
UE-specific tools; it is the production patterns that keep the agent from
writing the wrong file, ignoring config, or giving up after the first build
error. The loop is the easy part; the guardrails and retry discipline are what
make it usable daily.
