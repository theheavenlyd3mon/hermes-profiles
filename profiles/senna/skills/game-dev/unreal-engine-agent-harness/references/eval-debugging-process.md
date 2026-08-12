# Debugging Process — Eval Harness Expansion (2026-07-23)

## Investigation flow

The eval suite was expanded from 4 to 26 tasks. During the expansion, the
harvest returned empty results (`build_attempts: 0`, `steps: 0`) even though
the session log had 11 lines. Here's the step-by-step investigation:

### Step 1: Verify the session file has content

```python
session_files = sorted(Path("sessions").glob("*.jsonl"))
sf = session_files[-1]
msgs = [json.loads(l) for l in sf.read_text().splitlines() if l.strip()]
print(f"Total messages: {len(msgs)}")
```

**Result:** `Total messages: 1` — only 1 message with `role=None`.

**Root cause:** `session_files[-1]` was `metrics.jsonl` (alphabetically last),
not the session log. The session log was `20260723_164044.jsonl` which sorts
before `metrics.jsonl`.

**Fix:** Filter out `metrics.jsonl` and `trajectories.jsonl` before selecting
the last file.

### Step 2: Verify the ScriptedLLM produces the right sequence

After fixing the session file selection, the harvest still returned empty
results. The investigation checked if the ScriptedLLM was producing the right
tool calls:

```python
# Check what _plan returns
plan = agent._plan(ex.prompt)
print('plan:', plan)

# Check ScriptedLLM state
resp = agent.llm.invoke([], tools=[{'type':'function','function':{'name':'test'}}])
print('first invoke:', resp)
resp2 = agent.llm.invoke([], tools=[{'type':'function','function':{'name':'test'}}])
print('second invoke:', resp2)
```

**Result:** The ScriptedLLM was consuming its first call on the planner step.
The `_plan` method calls `self.llm.invoke(messages)` (no `tools=`), but the
ScriptedLLM didn't handle `tools is None` separately — it consumed the first
scripted tool call.

**Fix:** In `ScriptedLLM.invoke`, check `if tools is None` first and return a
canned plan.

### Step 3: Verify the harvest can parse tool results

After fixing the ScriptedLLM, the harvest still returned `build_attempts: 0`.
The investigation manually parsed the session file to check if tool results
were being recorded correctly:

```python
for i, m in enumerate(msgs):
    r = m.get("role")
    if r == "tool":
        content = m.get("content")
        print(f"  content type: {type(content).__name__}")
        if isinstance(content, dict):
            res = content.get("result", content)
            print(f"  exit_code: {res.get('exit_code')}")
```

**Result:** The tool messages didn't include `tool_name`, so the harvester
couldn't distinguish `dry_run` from `write_file` calls, and couldn't verify
the `dry_run → write_file` ordering invariant.

**Fix:** Add `"tool_name": tool_name` to the session log tool entry in
`agent.py`'s `run()` method.

### Step 4: Verify the ScriptedLLM args match the tool signature

After fixing the `tool_name` logging, the harvest returned `build_attempts: 0`
still. The investigation checked the `build_module` call:

```python
# ScriptedLLM calls:
("build_module", {"module_name": "MyGame"})
```

But the original ScriptedLLM had `{"module": "MyGame"}` — the parameter
name didn't match `BuildTools.build_module(self, module_name: str)`.

**Fix:** Use `{"module_name": "MyGame"}` in the ScriptedLLM call sequence.

### Key lesson

When debugging an eval pipeline, trace the data flow end-to-end:
1. Does the raw log have the right content? (session file selection)
2. Does the agent produce the right sequence? (ScriptedLLM planner collision)
3. Can the harvester parse the log? (tool_name, result structure)
4. Do the tool args match the signatures? (parameter naming)

Each bug masks the next — fixing one reveals the next in the chain.