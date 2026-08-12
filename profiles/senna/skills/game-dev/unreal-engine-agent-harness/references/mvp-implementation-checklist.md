# UE Agent Harness — MVP Implementation Checklist

Context: implementing the minimum viable production set for the standalone
UE agent harness. This checklist was validated in a real session on 2026-07-16.

## Scope

Implement these items before adding planner, MCP, or metrics:

1. Config propagation to LLM.
2. Auto-generated tool schemas.
3. Project-tree path guards.
4. Build retry loop.
5. Persistent memory recall/remember.
8. Security guardrails (`approval_mode`).
10. Config refresh.
11. E2E stub test.

(Items 6, 7, 9 — planner, MCP, metrics — are deferred.)

## File-by-file changes

### `agent.py`

- `Config` dataclass: add `llm_base_url`, `approval_mode`, `allowed_paths`.
- `Config.from_yaml`: read the new fields with `.get(...)` defaults.
- Import `PathGuard`, `schemas_from_registry`.
- In `Agent.__init__`:
  - Build `PathGuard` from `config.uproject_path` parent + `config.allowed_paths`.
  - Pass guard to `FileTools`.
  - Use `schemas_from_registry(self.tools)` for tool schemas.
- Add `DANGEROUS_TOOLS` and `READONLY_TOOLS` sets.
- In `_call_tool`, check `approval_mode` and return `{"error": ...}` for blocked tools.
- In `run()`, prepend memory context, track `build_attempts`, retry on failed build.
- `_remember_outcome` stores task summary to memory.

### `llm.py`

- `LLM.__init__` takes `config` (not zero-arg) and reads provider/model/api_key/base_url from it.
- Update `demo()` or any zero-arg call sites to construct a minimal config first.

### `tools/schema.py` (new)

- `_json_type(t)` maps Python types to JSON Schema types.
- `schema_for(fn)` builds OpenAI-style function schema from `inspect.signature`.
- `schemas_from_registry(registry)` returns the list.
- Add docstrings to tool methods so schemas have descriptions.

### `tools/guard.py` (new)

- `PathGuard` with `project_root`, optional `allowed_paths`.
- `is_safe(target)` checks resolved path is inside project root or allowed paths.
- `assert_safe(target)` raises `ValueError` with a clear message.

### `tools/file.py`

- `__init__` accepts `guard`.
- `_check(path)` catches guard `ValueError` and returns `{"error": str(e)}`.
- `read_file`, `write_file`, `list_source_files`, `dry_run` check guard and return errors as dicts.

### `tools/build.py`

- `build_module` returns synthetic success when UBT is not found (enables off-PC tests).
  - Keep the message honest: `"UBT not found; synthetic pass for testing."`
- `parse_build_errors` regex for `File.cpp(line): error CODE: message`.

### `config.yaml`

```yaml
project:
  uproject_path: "C:/Projects/MyGame/MyGame.uproject"
  default_module: "MyGame"

bridge:
  type: "stub"
  file_path: "./bridge/bridge.json"
  poll_interval: 0.5
  timeout: 30.0

llm:
  provider: "anthropic"
  model: "claude-sonnet-4"
  api_key_env: "ANTHROPIC_API_KEY"
  base_url: ""

agent:
  max_build_retries: 3
  memory_enabled: true
  journal_path: "./progress.md"
  db_path: "./memory.db"
  approval_mode: "auto"      # auto | ask | readonly
  allowed_paths: []           # extra paths outside the project tree

mcp:
  enabled: false
  servers: {}
```

### `prompts/system.txt`

Add explicit safety and workflow rules at the top:

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

### `test_stub.py`

Extend `make_test_config` to include all new fields.

Add tests:

- `test_llm_config_propagation` — assert provider/model/base_url reach the LLM client.
- `test_tool_schema_generation` — assert `write_file`, `build_module` appear in schemas.
- `test_path_guard_blocks_escape` — write to a path outside the project tree and assert `error` in result.
- `test_readonly_mode_blocks_writes` — set `approval_mode="readonly"` and assert writes are blocked.
- `test_build_retry_counter` — assert `config.max_build_retries` is respected.
- `test_e2e_stub_write_and_build` — stub a fake LLM, run a task, and assert a successful response.

## Test tips

- Activate the project's venv before running tests: `source .venv/bin/activate`.
- `pytest` may not be installed in the venv; install it with `pip install pytest`.
- `pytest` passes `tmpdir` as a `py.path.local` object, not a `pathlib.Path`. Wrap it with `Path(str(tmpdir))` before using `.parent` or `write_text(..., encoding="utf-8")`.
- Use `python test_stub.py` as a fallback if `pytest` is unavailable; keep the `if __name__ == "__main__"` block in sync with the pytest functions.

## Verification command

```bash
cd /path/to/ue-agent-harness
source .venv/bin/activate
python -m pytest test_stub.py -v
```

Expected: all tests pass.
