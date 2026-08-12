---
name: unreal-engine-agent-harness
description: >
  Design and bootstrap a minimal, generic AI agent harness for Unreal Engine
  game development. Covers architecture, bridge selection, tool inventory,
  build loop, optional memory integration, and a lazy cross-platform dev split.
tags: unreal-engine, game-dev, agent, ai, python, mcp
---

# Unreal Engine Agent Harness

Build a minimal AI agent harness that can read a UE project, write C++ source,
trigger builds, and report results. Keep it generic enough that anyone can
fork it for their own project and engine.

## When to use

- You are building an agent harness for UE C++ / gameplay work.
- You need to choose between a native UE bridge, an MCP server, or an external
  protocol.
- You want to scope a first milestone that can be tested on macOS/Linux without
  launching the UE editor.
- You want a standalone agent process that talks to a running editor through a
  file-based bridge.

## Core principles

1. **The loop is trivial; the tools are the work.** Spend effort on the
   UE-specific tool wrappers, not the ReAct loop.
2. **Start standalone.** If the agent must run as its own process, design a
   file-based bridge from the start; use a stub mode for off-PC development.
3. **Ship a stub bridge.** Let the harness run and be tested on a machine that
   does not have the editor open.
4. **One real end-to-end task in v1.** Pick a single C++ class addition, not a
   feature family.
5. **Make memory optional.** Persistent memory is useful only after the harness
   already works.

## Architecture

```
┌──────────────────────────┐
│   CLI / REPL / TUI       │
├──────────────────────────┤
│   Agent Loop             │  ReAct: LLM → tool → LLM
├──────────────────────────┤
│   Tool Registry          │  project, file, build, editor
├──────────────────────────┤
│   UE Bridge              │  native Python Editor Scripting API or stub
├──────────────────────────┤
│   LLM Provider           │  pluggable (Anthropic, OpenAI, local)
├──────────────────────────┤
│   Memory (optional)      │  Mnemosyne / journal / session JSONL
└──────────────────────────┘
```

The loop is a single Python file. Tools are thin classes. The UE bridge is a
standalone file-based JSON protocol, with a swappable stub for off-PC development.
The UI layer is separate: start with a REPL, add a one-shot CLI, and only then
add a Textual dashboard.

## Key design decisions

### Bridge: standalone file-based protocol first

- The agent runs as a standalone Python process.
- It communicates with a running Unreal Editor through a simple file-based
  JSON bridge (one file, polled by both sides).
- A `ue_bridge_listener.py` script runs inside the editor and executes
  requests.
- A `stub` bridge mode returns canned responses so the harness can be built
  and tested on macOS/Linux without the editor open.

### Cross-platform dev split

- Build and test the harness on your main dev machine (macOS/Linux) using a
  **stub bridge** that returns canned responses.
- Move the same code to the Windows PC, set bridge to **file**, and run with
  the editor open.
- This avoids the "I cannot test until I am at the PC" trap.

### Tool inventory

- **Project:** `scan_project`, `read_build_cs`.
- **File:** `read_file`, `write_file`, `dry_run`.
- **Build:** `build_module`, `parse_build_errors`.
- **Editor:** `editor_command`, `is_editor_running`, `compile_blueprints`.
- **Memory (optional):** `memory_remember`, `memory_recall`.

### Memory integration

- Persistent memory (e.g. Mnemosyne) is a feature flag, not a dependency.
- If enabled, recall before each task and remember after each success.
- If disabled, rely on a `progress.md` journal and the current project state.
- See `references/mnemosyne-integration-recipe.md` for a standalone Python integration that does not require running inside Hermes.

### Naming the harness

- Check PyPI, GitHub, and generic web search before a name hardens into files.
- If a collision exists, rename early. See `references/agentu-naming-collision.md`.

## Minimal v1 milestone

1. User says: "Add a simple C++ class."
2. Agent scans the project and reads existing source.
3. Agent recalls prior project memory when memory is enabled.
4. Agent proposes changes with `dry_run`.
5. Agent writes `.h` and `.cpp` files.
6. Agent runs `build_module`.
7. If the build fails, parse errors, feed them back to the LLM, edit files, and
   retry up to a configured limit (e.g. 3).
8. If the build succeeds, remember the outcome, write `progress.md`, and return a summary.

## Implementation notes for v1

### Config dataclass

Use a single `Config` dataclass loaded from `config.yaml` and pass it to every
service that needs configuration (LLM, build tools, bridge, etc.). Do not let
sub-components re-read the YAML file. This keeps the agent's behavior fully
determined by the loaded config.

Required fields:

```python
@dataclass
class Config:
    uproject_path: str
    default_module: str
    bridge_type: str                 # stub | file
    bridge_file_path: str
    bridge_poll_interval: float
    bridge_timeout: float
    llm_provider: str
    llm_model: str
    llm_api_key_env: str
    llm_base_url: str                # empty string means provider default
    max_build_retries: int
    memory_enabled: bool
    journal_path: str
    db_path: str
    approval_mode: str = "auto"      # auto | ask | readonly
    allowed_paths: list[str] = field(default_factory=list)
    _profile_root: str | None = None  # set by from_profile
```

### Profile isolation

State (memory.db, sessions/, progress.md, skills/) should live outside the repo. Use a profile directory layout:

```
~/.agentunreal/profiles/<name>/
├── config.yaml
├── memory.db
├── sessions/
├── progress.md
├── skills/
├── plugins/
└── .env
```

Add `from_profile` to `Config` and a `profile_path` helper:

```python
@classmethod
def from_profile(cls, name: str, profile_root: str | None = None) -> "Config":
    if profile_root is None:
        profile_root = str(Path.home() / ".agentunreal" / "profiles" / name)
    profile = Path(profile_root)
    config_path = profile / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"No config.yaml in profile: {profile}")
    cfg = cls.from_yaml(str(config_path))
    cfg.journal_path = str(profile / "progress.md")
    cfg.db_path = str(profile / "memory.db")
    cfg._profile_root = str(profile)
    return cfg

def profile_path(self, *parts: str) -> Path:
    root = getattr(self, "_profile_root", None)
    if root is None:
        return Path(*parts)
    return Path(root) / Path(*parts)
```

Wire `_profile_root` into session paths, metrics paths, and `SkillTools(skills_dir=...)`. CLI: `--profile <name>` loads from the profile dir; falls back to `--config` / default `config.yaml` when no profile is specified.

### Auto-generated tool schemas

Create a small `tools/schema.py` that walks the tool registry with `inspect`:

```python
import inspect

def schema_for(fn):
    sig = inspect.signature(fn)
    properties = {}
    required = []
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
        param_type = "string"
        if param.annotation is not inspect.Parameter.empty:
            origin = getattr(param.annotation, "__origin__", None)
            if origin in (list, dict):
                param_type = "array" if origin is list else "object"
            elif isinstance(param.annotation, type):
                param_type = {str:"string", int:"integer", float:"number", bool:"boolean"}.get(param.annotation, "string")
        properties[name] = {"type": param_type, "description": f"Parameter `{name}`."}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {
        "type": "function",
        "function": {
            "name": fn.__name__,
            "description": (fn.__doc__ or "").strip(),
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }

def schemas_from_registry(registry: dict) -> list[dict]:
    return [schema_for(fn) for fn in registry.values()]
```

Then `agent.py` exposes the registry to the LLM with `schemas_from_registry(self.tools)`.
Add a one-line docstring to each tool method so the schema has meaningful descriptions.

### Path guard

```python
from pathlib import Path

class PathGuard:
    def __init__(self, project_root: Path, allowed_paths: list[Path] | None = None):
        self.project_root = project_root.resolve()
        self.allowed = [p.resolve() for p in (allowed_paths or [])]

    def is_safe(self, target: Path) -> bool:
        resolved = target.resolve()
        if resolved == self.project_root or self.project_root in resolved.parents:
            return True
        for allowed in self.allowed:
            if resolved == allowed or allowed in resolved.parents:
                return True
        return False

    def assert_safe(self, target: Path) -> None:
        if not self.is_safe(target):
            raise ValueError(f"Path {target} is outside the allowed project tree.")
```

Pass the guard into `FileTools` and call `assert_safe` before reading/writing.
Catch the exception at the tool boundary and return `{"error": str(e)}`.

### Security guardrails

Define:

```python
DANGEROUS_TOOLS = {"write_file", "build_module", "editor_command"}
READONLY_TOOLS = {"scan_project", "read_file", "read_build_cs", "list_source_files", "dry_run", "is_editor_running", "memory_recall"}
```

In `_call_tool`:
- If `approval_mode == "readonly"` and `name not in READONLY_TOOLS`, return `{"error": "Readonly mode: ..."}`.
- If `approval_mode == "ask"` and `name in DANGEROUS_TOOLS`, prompt on stdin with the tool name, path, and a truncated content preview. `[y/N]` — defaults to deny. Auto-approve if the `dry_run` hash matches (already reviewed). On `EOFError`/`KeyboardInterrupt` (non-interactive context), deny.
- If `approval_mode == "auto"`, no prompts.

The approval prompt and the dry_run→write_file hash gate are **independent layers**. The prompt asks "should this dangerous tool run at all?"; the hash gate asks "has this exact content been reviewed via dry_run?". Both must pass for `write_file` to execute.

```python
def _prompt_approval(self, name: str, args: dict) -> bool:
    """Interactive stdin prompt for dangerous tools in 'ask' mode."""
    path = args.get("path", "")
    content_preview = args.get("content", "")
    if content_preview:
        content_preview = content_preview[:200] + ("..." if len(args.get("content", "")) > 200 else "")
    prompt = f"\n[APPROVAL] {name}"
    if path:
        prompt += f" path={path}"
    if content_preview:
        prompt += f"\n  content: {content_preview}"
    prompt += "\nApprove? [y/N] "
    try:
        resp = input(prompt)
    except (EOFError, KeyboardInterrupt):
        return False
    return resp.strip().lower() in ("y", "yes")
```

Set `approval_mode: "auto"` in tests so the harness can run without user prompts.

### Build retry loop

Inside `Agent.run`, track `build_attempts`. When `build_module` returns
`exit_code != 0` and `build_attempts < config.max_build_retries`, parse the
errors and **fold the retry nudge into the tool result** — do NOT append a
synthetic `user` message (see pitfalls: that breaks role alternation + prompt
cache). Cap the error dump so a 30KB UBT log doesn't blow context.

```python
if tool_name == "build_module":
    build_attempts += 1
    if result.get("result", {}).get("exit_code", 1) != 0 and build_attempts < self.config.max_build_retries:
        errors = self.tools["parse_build_errors"](output=...)
        result["retry_nudge"] = f"Build failed (attempt {build_attempts}/{self.config.max_build_retries}). Fix these errors and call build_module again: {json.dumps(errors)[:2000]}"
```

### Enforce dry_run → write_file (hash gate)

The system-prompt rule "always dry_run before write_file" is not enforced by
default — a hallucinating agent writes unconditionally. Make it code in
`_call_tool` by hash-matching the last `dry_run(path+content)`:

```python
import hashlib  # + self._last_dry_run_hash = None in __init__
if name == "write_file":
    h = hashlib.sha256((args.get("path","") + args.get("content","")).encode()).hexdigest()
    if h != self._last_dry_run_hash:
        return {"error": "write_file blocked: call dry_run with the same path+content first."}
if name == "dry_run":
    self._last_dry_run_hash = hashlib.sha256((args.get("path","") + args.get("content","")).encode()).hexdigest()
```

### Auto memory recall and remember

Before the first LLM call, build a memory context from several queries and
prepend it to the user prompt. After a final answer, remember the outcome. Tools
are only added to the registry when memory is enabled.

```python
def _recall_memory_context(self, user_prompt: str) -> str:
    if not self.memory:
        return ""
    project = Path(self.config.uproject_path).stem
    queries = [user_prompt, f"{project} project conventions", f"{project} build failures"]
    seen = set()
    memories = []
    for q in queries:
        for m in self.memory.recall(q, top_k=3):
            mid = m.get("memory_id")
            if mid and mid not in seen:
                seen.add(mid)
                memories.append(m)
    if not memories:
        return ""
    return "\n".join(["Relevant memory context:"] + [f"- {m.get('content', '')}" for m in memories])

def _remember_outcome(self, user_prompt: str, summary: str, success: bool = True) -> None:
    if not self.memory:
        return
    status = "succeeded" if success else "failed"
    self.memory.remember(
        f"Project: {Path(self.config.uproject_path).stem}\nTask: {user_prompt}\nOutcome: {status}\nSummary: {summary}",
        source="agent", importance=0.7, scope="session"
    )
```

### System prompt safety rules

Add explicit safety and workflow rules to `prompts/system.txt` so the model
knows the constraints:

```
SAFETY RULES:
- Never write files outside the project Source directory or allowed_paths.
- Always call dry_run before write_file.
- Always pair new .h files with .cpp files under the same module.
- Never delete existing source files unless the user explicitly asks.
- If a build fails, read the error output, fix the root cause, and retry.

WORKFLOW RULES:
- Before writing code, plan: scan the project, read relevant source, then dry_run.
- After writing code, call build_module.
- After a successful build, update progress.md and remember the outcome.
```

## Current state

Verified 2026-07-17 (`git log` + `pytest`, 22 green): **all 11 evolution-plan tasks are merged** — config propagation, auto schemas, path guards, build retry, memory recall/remember, planner, MCP flag, guardrails/approval, eval harness, config sync, e2e test. Beyond the plan: streaming `on_event` hook, two-pane Textual TUI, `--json` machine contract, `ue5.py` CLI, `.env` loading.

**Milestone M3 (2026-07-17, commit `669dd7d`) — Phase 0+1 of the three-way diagnostic (`docs/DIAGNOSTIC_AND_PLAN_2026-07.md`) landed:**
- **Phase 0 (correctness):** role-alternation bug fixed (build-retry nudge folded into tool result via `result["retry_nudge"]`, no synthetic `user` msg mid-loop); dry_run→write_file hash gate in `_call_tool`; stale docs synced, `AGENTU_COMPARISON.md` deleted.
- **Phase 1 (backbone):** skills system (`tools/skills.py` → `skills_list`/`skill_view`, `skills/` dir, seeded `new-cpp-class.md`, system prompt says load-before-task + offer-to-save-after); trajectory harvest (`eval/harvest.py` → `sessions/trajectories.jsonl`).

**Milestone M4 (2026-07-17) — Phase 2 (Evaluate) + package reorg + web dashboard:**
- **Phase 2 (Evaluate):** deterministic eval in `agentunreal/eval/` — `suite.py` (EvalExample loader + fixture materializer, tasks in `eval/tasks/*.json`, kinds new-class/build-fix/refactor/editor-command), `score.py` (deterministic scoring: build_success, dry_run-before-write, MSVC/LNK codes, constraint violations — NO LLM judge; the engine gives binary ground truth), `run_suite.py` (stub-mode runner + aggregate rollup), `ab.py` (A/B two system prompts → pass-rate/build/attempt/violation deltas). "Measure before optimize" gate = `python -m agentunreal.eval.run_suite` + pytest green; a variant that breaks the suite is rejected regardless of A/B numbers.
- **Package reorg (pi-style, stays Python):** installable `agentunreal/` package — `core/` (agent, llm, Config), `tools/`, `eval/`, `ui/` (tui, ui_cli, repl, ue5_cli), `bridge/` (stub_bridge, ue_bridge_listener) — with thin root shims (`agent.py`, `ue5.py`, `tui.py`, `repl.py`) so old commands still run. `pyproject.toml` adds console scripts `ue5`/`agentunreal`/`agentunreal-tui`.
- **Web dashboard:** `web/` = Vite+React+TS (Murim Noir, from `docs/ui-design-spec.md`) + `serve.py` stdlib backend (port 7822). Contract + pitfalls in `references/web-dashboard-contract.md`.

**Next (needs user go):** expand `eval/tasks/` to 15–30 tasks — **DONE (26 tasks, 100% pass, 0 violations, 16 tests green, see `references/eval-harness-debugging.md` for the 7 bugs found and fixed during expansion**); Phase 3 (plugins + context compression + GEPA on `system.txt` once 50+ real sessions exist); MCP server mode (user chose MCP over bespoke bridge). UI: murim-noir spec in `docs/ui-design-spec.md`, parallel polish track.

`agent.py` (~370 lines) is the single-file core: Config dataclass, ReAct loop (max_iter=10) with plan step, memory recall before / remember after, build-retry via `retry_nudge`, dry-run gate, `SessionMetrics` → `sessions/metrics.jsonl`, per-run `sessions/*.jsonl`.

## Common pitfalls

- **Trust the code, not the roadmap markdown.** The repo's README roadmap and `AGENTU_COMPARISON.md` both lagged the actual code by a full milestone (11 merged tasks) — they claimed hand-wired schemas, no guardrails, no retry loop when all existed. Before planning work against this repo, run `git log --oneline -15` and `pytest -q` to establish the real baseline; treat markdown roadmaps as hints, not ground truth.
- **Black terminal between submit and answer.** If `run()` blocks through plan+tool-loop+LLM and only `print()`s the final string, the user sees a dead screen. Add ONE event hook on the Agent and a `rich.live.Live` renderer (see `references/streaming-cli-renderer.md`). The hook fires at the single dispatch chokepoint (`_call_tool`): `tool.start` (id+name+args), `tool.complete` (id+✓/✗ result), plus `plan` and `result`. The same hook later feeds a Textual dashboard — no loop rewrite.
- **Synchronous `agent.run()` inside a Textual event handler.** The existing `tui.py` calls `self.agent.run()` directly in `action_run_task` → it freezes and shows nothing until done (same black-screen root cause, just framed). Fix: run `agent.run` in a Textual worker thread and push events from `on_event` into the `#log` widget. The hook already exists from the streaming-CLI work.
- **Building the TUI/IDE before the loop works.** Use a REPL until the loop is proven.
- **Choosing editor-only when you need standalone.** If the agent must run as its own process, design a bridge interface from the start, even if v1 uses a stub.
- **Requiring the editor for every test.** Use a stub bridge for off-PC development.
- **Making memory a hard dependency.** It adds failure modes and can be added later behind a flag. When you do add it, keep the tools out of the registry unless memory is actually enabled.
- **Editing files without source control.** The first safety tool should be a `snapshot` / `revert` wrapper around git or P4.
- **Over-fitting to one project.** Keep project names, module names, and class names in config, not in code.
- **Naming the harness before checking for collisions.** A name that is already a PyPI package, GitHub org, or framework (e.g. `AgentU` vs. the published `agentu` package) creates search ambiguity, import conflicts, and brand confusion. Before committing to a public name, search PyPI and GitHub, and document the distinction or rename early.
- **Forgetting to update test constructors when the config dataclass changes.** Adding `db_path` to `Config` also requires updating every `Config(...)` call in `test_stub.py` and any other test fixtures.
- **Instantiating the LLM client without passing config.** A generic `LLM()` that reads `config.yaml` itself may ignore the model/provider the agent was configured with. Pass the config object to the LLM client so one source of truth controls provider, model, and base URL.
- **Hand-coding OpenAI-style tool schemas.** Derive tool schemas from function signatures and docstrings, or maintain one schema file per tool. This avoids drift when a tool gains a parameter and is the pattern used by production agent frameworks.
- **Config-path args that crash the LLM when omitted.** A tool signature like `scan_project(self, uproject_path: str) -> dict` forces the LLM to always pass `uproject_path`, which is wrong for a harness where the project is already known from `config.uproject_path`. Make such config-derived params optional and fall back: `def scan_project(self, uproject_path: str | None = None) -> dict:` then `if uproject_path is None: uproject_path = self.config.uproject_path`. This matches sibling tools like `read_build_cs` (which already reads `self.config.uproject_path`) and prevents the tool-call crash where the model invokes `scan_project()` with no args.
- **Re-editing the schema to make an arg optional.** Unnecessary. `tools/schema.py: schema_for` only appends a param to `required` when `param.default is inspect.Parameter.empty`. Giving the param a default (`=None`) automatically drops it from `required` — the single signature change is sufficient. Verify with `agent._tool_schemas()` and assert the tool's `required == []`.
- **Forgetting a regression test for a tool-crash fix.** A one-line signature change that fixes a crash is invisible to the suite until a test calls the new path. Add a test that invokes the tool with no args (e.g. `agent.project_tools.scan_project()`) and asserts the expected happy-path result (`error is None`, `name` matches `Path(config.uproject_path).stem`). This both locks the fix and documents the contract.
- **Writing files outside the project tree.** A destructive file tool should reject paths that resolve outside the configured project root.
- **Hard-coding platform paths in build tools.** Windows UBT paths belong in config or environment variables, not in source code. Fallback to a synthetic pass on non-Windows so the harness can be tested off-PC.
- **Letting `max_build_retries` sit unused.** A config value for retries is only useful if the agent loop actually consumes it: parse errors, append them to the LLM context, and loop until success or retries are exhausted.
- **Path guard exception handling.** Letting `PathGuard` raise an exception inside a file tool is fine for internal callers, but a tool that returns JSON to the LLM must surface guard failures as a result dict with an `error` key. The LLM cannot parse a stack trace, but it can read `"error": "Path ... is outside ..."` and choose another path. Catch guard exceptions at the tool boundary and return `{"error": str(e)}`.
- **Approval-mode serialization for tool returns.** Security guardrails such as `approval_mode: "ask"` / `"readonly"` should return the same dict-shaped error to the LLM, not raise. A consistent `{"error": ...}` shape across guardrails, path checks, and missing-tool errors lets the agent retry rather than crash.
- **Synthetic pass when UBT is unavailable.** On macOS/Linux the Windows `Build.bat` will not exist. Make `build_module` return a synthetic success (`exit_code: 0`) in that case so the harness can be tested off-PC, but log that it is synthetic. This is a stub-test enabler, not a production build path.
- **Tests must use `Path(str(tmpdir))` with pytest.** `pytest` passes a `py.path.local` (or `LocalPath`) that lacks `pathlib` methods like `.parent` and the `encoding=` keyword on `write_text`. Wrap it with `Path(str(tmpdir))` before using pathlib operations, or write tests that explicitly pass `encoding="utf-8"`.
- **Shipping a zero-arg `LLM()` demo path.** If the LLM wrapper has a `demo()` or `__main__` that constructs the client without config, it will break after the constructor changes. Update the demo path to build a minimal `Config` object or remove it.
- **Not tracking dependencies.** A Python harness that uses `pyyaml`, `anthropic`, `openai`, and optional extras needs a `requirements.txt` or `pyproject.toml` so a fresh venv can reproduce it. Without this, `pytest` and other tools may not be installed on the next machine.
- **Execution-order assumption.** When running the evolution plan with subagents, land Task 10 (config + prompt sync) before Tasks 6/7/9. The later tasks read config keys (`mcp_enabled`, `approval_mode`) that only exist after Task 10. Running them in parallel against an old `config.yaml` causes false test failures.
- **Same-file parallel edits.** `agent.py` and `test_stub.py` are touched by multiple evolution tasks. Do not dispatch Tasks 6, 7, and 9 as parallel leaf subagents that all edit `agent.py` and `test_stub.py` — they will race and clobber each other. Serialize them or give each task a disjoint region (e.g. one adds `_plan`, another adds MCP wiring in `__init__`, another adds metrics in `run`). CONFIRMED in Task 7: a sibling subagent clobbered `agent.py` (deleted `_load_system_prompt` body) and mangled `test_stub.py` (joined two lines into one) mid-edit. Re-read before writing and verify after with `python -m pytest`.
- **`datetime.utcnow()` is deprecated (Python 3.12+).** Any session-log or timestamp code in the agent/TUI must use `datetime.now(timezone.utc)` (import `timezone` from `datetime`). A bare `utcnow()` still works but emits a `DeprecationWarning` and will break on future Python.
- **The entry point should expose a `--json` machine contract.** `python3 -m agent` is both a human REPL and a callable tool. Add a `--json` flag (cli-builder Pattern 3): collect the `on_event` stream and emit ONE JSON object on stdout with `{prompt, events, result}`, no auxiliary text. This lets other agents/scripts drive the harness. See the `--json` mode section in `references/streaming-cli-renderer.md`.
- **Synthetic `user` messages mid-loop break prompt cache and alternation.** `agent.py`'s build-retry loop injects `{"role": "user", "content": "Build failed..."}` between tool results. Hermes's AGENTS.md explicitly forbids this pattern: strict user/assistant alternation is required, and any mid-loop role mutation invalidates the per-conversation prompt cache (real $ cost on every subsequent turn). Deliver retry hints as a tool result on the original `build_module` tool_call_id, or fold into the next assistant content. See `references/hermes-port-map.md` §"Concrete bug to fix first".
- **When borrowing from a larger reference codebase, diff against its TOP-LEVEL module layout, not its feature docs.** The Hermes review surfaced components (`cron/`, `plugins/`, `providers/base.py`, `optional-mcps/unreal-engine/`) that don't appear in any of Hermes's own feature READMEs — you only find them by `ls`-ing the repo root and reading `__init__.py` docstrings. Feature docs lag; module layout is ground truth.
- **A trajectory harvest is only as good as the raw log it folds.** `eval/harvest.py` produced 41 sessions but mostly `steps: 0` because the per-session `sessions/*.jsonl` records tool *names*, not args/results/exit_codes. If you want to score or optimize later, enrich the log at write time (per-step args, ok, exit_code, error codes) — a harvester can't recover detail that was never written. Enrich first, harvest second. **CONFIRMED 2026-07-23:** the harvest must also track `dry_run_before_write` (did `dry_run` fire before `write_file` for the same path?) and `files_written` (paths from successful `write_file` results). The raw log must include `tool_name` in each tool message so the harvester can distinguish `dry_run` from `write_file` calls — without it, `dry_run_before_write` is always `False` and every `requires_dry_run` task fails. See `references/eval-harvest-enrichment.md`.
- **Prompt path resolution breaks when run as a module.** `Agent._plan` and `_load_system_prompt` that use `Path("prompts/system.txt")` resolve relative to the *current working directory*, not the package root. When `python -m agentunreal.eval.run_suite` runs from a tmp dir (as the eval runner does), the prompts are never found and the planner silently returns `[]`. Fix: resolve from `__file__`: `Path(__file__).resolve().parent.parent.parent / "prompts" / name`. The `_plan` method must also gracefully return `[]` when the planner file is missing, not crash.
- **ScriptedLLM consumes its first call on the planner step.** The eval runner's `_scripted_llm()` returns a fixed sequence of tool calls, but `_plan` calls `self.llm.invoke(messages)` (no `tools=`) before the main loop. If the ScriptedLLM doesn't handle `tools is None` separately, the planner call consumes the first scripted tool call (`scan_project`), shifting the entire sequence and producing a broken trajectory. Fix: in the ScriptedLLM's `invoke`, check `if tools is None: return a canned plan` before consuming the scripted sequence.
- **Session file selection picks the wrong file.** `sorted(Path("sessions").glob("*.jsonl"))[-1]` returns `metrics.jsonl` (alphabetically last) instead of the actual session log, because `m` > `2`. The harvest then reads the metrics file (which has `role=None` for its single JSON line) and produces `steps: 0`, `build_success: False`. Fix: filter out `metrics.jsonl` and `trajectories.jsonl` before selecting the last file.
- **Tool parameter names must match between ScriptedLLM and the real tool.** The ScriptedLLM called `build_module` with `{"module": "MyGame"}` but `BuildTools.build_module` expects `module_name`. The `_call_tool` method calls `tool(**args)`, so the mismatch raises `TypeError` and the build result is `{"error": ...}` with no `exit_code`. Always verify the ScriptedLLM's call args match the actual tool signature — `inspect.signature` is the source of truth.
- **Tool messages in the session log must include `tool_name`.** The `Agent.run` method writes `{"role": "tool", "tool_call_id": ..., "content": ...}` to the session log. Without `tool_name`, the harvester cannot distinguish `dry_run` from `write_file` calls and cannot verify the `dry_run → write_file` ordering invariant. Add `"tool_name": tool_name` to the log entry.
- **Schema generator must use the registry key, not `fn.__name__`.** When tools are registered under names that differ from the method name (e.g. `registry["memory_recall"] = self._memory_recall`), the schema generator must use the registry key as the tool name, not `fn.__name__` which returns `_memory_recall`. Fix: `schema_for(fn, name=None)` where `name` defaults to `fn.__name__` but `schemas_from_registry` passes the registry key. Also rename the loop variable in `schema_for` to avoid shadowing the `name` parameter.
- **Eval task count must match the suite's coverage.** The original 4 tasks covered all four kinds (new-class, build-fix, refactor, editor-command) but were too narrow. Expanding to 26 tasks (10 new-class, 3 build-fix, 3 refactor, 6 editor-command, 4 original) across the MyGame domain gives the suite enough breadth to catch regressions in each tool category. Each task must have a clear `expect` block: `must_build`, `max_build_attempts`, `requires_dry_run`, `forbidden_error_codes`.
- **Parallel subagents on one repo → reconciliation debt + contract drift.** Dispatching a reorg agent and a feature agent against the same working tree concurrently makes the reorg *move* the feature's just-written files, splitting them across the old/new layout — and a separately-built frontend/backend pair silently diverges on the JSON contract. CONFIRMED M4: the reorg moved `eval/score.py`+`suite.py` into the package but left `run_suite.py`/`ab.py`/`tasks/` in the stale `eval/` dir; and `serve.py` (written before reading the frontend) got the port AND field names wrong. Mitigate: serialize repo-wide reorgs before/after feature work (not during), and define the shared contract FIRST (see next pitfall).
- **Define the frontend↔backend contract BEFORE building both sides.** When a Python backend and a TS/Vite frontend are built in parallel (or the backend is written before reading the frontend), they drift on the JSON shape — port, field names, event schema. Have the frontend author publish `types.ts` (the single source of truth) FIRST, then conform the backend to it; it's cheaper to change the backend. See `references/web-dashboard-contract.md`.

  ## Verification

- **Off-PC test:** stub bridge returns canned responses, loop completes.
- **PC test:** run the same command with the editor open and the real bridge.

## References

- `references/ue-agent-harness-decisions.md` — bridge choice and lazy split
  from a real scoping session.
- `references/standalone-file-bridge.md` — recipe for the file-based bridge
  between a standalone agent and the UE editor.
- `references/agentu-naming-collision.md` — why to check for package/name
  collisions before settling on a harness name.
- `references/tui-dashboard.md` — adding a Textual/Rich dashboard after the
  loop and stub tests are working.
- `references/streaming-cli-renderer.md` — minimal rich.live.Live renderer that
  streams plan + tool calls live, killing the "black terminal" between task
  submit and final answer. Reuse when the CLI shows nothing until `run()` returns.
- `references/mnemosyne-integration-recipe.md` — adding durable memory to a
  standalone Python harness without running inside Hermes.
- `references/integrating-production-agent-patterns.md` — how to borrow
  memory, MCP, guardrails, multi-agent, and eval patterns from popular agent
  repositories and apply them to the harness.
- `references/mcp-client-pattern.md` — optional MCP client feature-flag wiring (Task 7).
- `references/hermes-port-map.md` — ranked top-10 components to port from the Hermes fork (with LOC estimates + sequencing), a "do not port" list, and the role-alternation bug to fix first. Replaces the loose "next frontier" guesses.
- `references/self-improvement-roadmap.md` — Collect→Evaluate→Optimize self-growth plan mined from hermes-agent-self-evolution + Icarus fabric: stage-by-stage loop, portability map, UE-specific eval signals (UBT exit codes, MSVC error taxonomy), trajectory JSONL schema, and the honest "GEPA later, A/B now" call.
- `references/engine-verified-self-growth-roadmap.md` — condensed 2026-07-17 three-way diagnostic: the engine-verified thesis, the free-binary-ground-truth eval signals, the phased Collect→Evaluate→Optimize build order, and the GEPA-later/fabric-capstone call.
- `references/web-dashboard-contract.md` — the serve.py↔web/ JSON contract (RunState/event schema, port, Vite proxy), how the backend enriches the raw on_event stream, and the frontend-first-contract pitfall hit when both sides were built without sharing types.ts first.
- `references/approval-v2-interactive-ask.md` — interactive `ask` mode with stdin
  prompt, two-layer gate (approval prompt + dry_run hash gate), and test patterns.
- `references/eval-harness-debugging.md` — session-specific debugging notes from the 2026-07-23 pass that expanded the eval task suite from 4 to 26 tasks and fixed 7 bugs in the eval pipeline (prompt path resolution, ScriptedLLM planner collision, session file selection, harvest enrichment, tool parameter naming, task suite expansion, schema generator name shadowing).
- `templates/config.yaml` — starter config for a new harness.
- `references/mvp-implementation-checklist.md` — exact files, fields, and test
  cases to implement the v1 milestone end-to-end.

## Session format

Use JSONL for session logs: one line per message, append-only, easy to inspect.
Keep the journal (`progress.md`) short: what changed, what failed, what is next.
