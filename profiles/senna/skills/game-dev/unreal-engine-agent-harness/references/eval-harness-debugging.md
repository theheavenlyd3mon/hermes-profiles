# Eval Harness Debugging — 2026-07-23

Session-specific debugging notes from the 2026-07-23 pass that expanded the
eval task suite from 4 to 26 tasks and fixed 7 bugs in the eval pipeline.

## Bugs found and fixed

### 1. Prompt path resolution (`agent.py`)
`Agent._plan` and `_load_system_prompt` used `Path("prompts/system.txt")` which
resolves relative to CWD. When `python -m agentunreal.eval.run_suite` runs from
a tmp dir, prompts are never found.

**Fix:** Resolve from `__file__`:
```python
def _prompt_path(self, name: str) -> Path:
    repo_root = Path(__file__).resolve().parent.parent.parent
    return repo_root / "prompts" / name
```
`__file__` is `agentunreal/core/agent.py`, so `parent.parent.parent` = repo root.

### 2. ScriptedLLM planner collision (`run_suite.py`)
`_scripted_llm()` returns a fixed sequence of tool calls. But `_plan` calls
`self.llm.invoke(messages)` (no `tools=`) before the main loop. The ScriptedLLM
consumed the first call on the planner step, shifting the entire sequence.

**Fix:** In `ScriptedLLM.invoke`, check `if tools is None` first and return a
canned plan:
```python
def invoke(self, messages, tools=None):
    if tools is None:
        return {"role": "assistant", "content": '[...]', "tool_calls": None}
    # ... consume scripted sequence
```

### 3. Session file selection (`run_suite.py`)
`sorted(Path("sessions").glob("*.jsonl"))[-1]` returned `metrics.jsonl`
(alphabetically last, `m` > `2`) instead of the session log.

**Fix:** Filter out metrics/trajectories:
```python
session_files = sorted(
    f for f in Path("sessions").glob("*.jsonl")
    if f.name not in ("metrics.jsonl", "trajectories.jsonl")
)
```

### 4. Harvest enrichment (`harvest.py`)
The harvester couldn't track `dry_run_before_write` or `files_written` because
the raw log didn't include `tool_name` in tool messages, and the harvest didn't
check for `dry_run` -> `write_file` ordering.

**Fix:**
- In `agent.py`: add `"tool_name": tool_name` to the session log tool entry.
- In `harvest.py`: track `dry_run_paths` and `write_paths` sets; set
  `dry_run_before_write = True` when a `write_file` path matches a prior
  `dry_run` path. Track `files_written` from successful `write_file` results.

### 5. Tool parameter naming (`run_suite.py`)
ScriptedLLM called `build_module` with `{"module": "MyGame"}` but the method
signature is `build_module(self, module_name: str)`. The `_call_tool` method
calls `tool(**args)`, so the mismatch raised `TypeError`.

**Fix:** Use `{"module_name": "MyGame"}` in the ScriptedLLM call sequence.
Always verify ScriptedLLM args match `inspect.signature` of the real tool.

### 6. Task suite expansion
Expanded from 4 to 26 tasks across all four kinds:
- 10 new-class (mana, combat, character, item, game-mode, player-controller,
  weapon, anim-instance, save-game, game-instance)
- 3 build-fix (missing-include, undef-pointer, header-guard)
- 3 refactor (tmap-to-tarray, delegate-to-tarray, fstring-to-fname)
- 6 editor-command (stat-unit, stat-scene, stat-memory, stat-physics,
  compile-blueprints, is-editor-running)

Each task has a clear `expect` block with `must_build`, `max_build_attempts`,
`requires_dry_run`, and `forbidden_error_codes`.

### 7. Schema generator name shadowing (`schema.py`)
`schema_for` used `fn.__name__` as the tool name, which returns the method name
(e.g. `_memory_recall`) instead of the registry key (`memory_recall`). When
memory is enabled, the schema exposed `_memory_recall` to the LLM but the tool
registry only had `memory_recall`, so tool calls would fail. Additionally, the
loop variable `name` in `for name, param in sig.parameters.items()` shadowed the
`name` parameter, causing the schema to use parameter names as tool names.

**Fix:** `schema_for(fn, name=None)` where `name` defaults to `fn.__name__` but
`schemas_from_registry` passes the registry key. Rename loop variable to `pname`.

## Verification
```
pytest test_stub.py -v     -> 16 passed (15 original + 1 new memory schema test)
python -m agentunreal.eval.run_suite --json
  -> 26 tasks, 26 passed, 100% pass rate, 0 constraint violations
```