# SessionMetrics Integration Details

## agent.py Patch Points

### Import
```python
from agentunreal.eval.metrics import SessionMetrics
```

### In run() method
1. After `session_path.mkdir()`, add:
   ```python
   metrics = SessionMetrics(session_id=session_id, task=user_prompt)
   ```

2. In the while loop (after `iterations += 1`):
   ```python
   metrics.iterations = iterations
   ```

3. When recording tool calls (after `tool_name = call["function"]["name"]`):
   ```python
   metrics.record_tool(tool_name)
   ```

4. Track errors:
   ```python
   if isinstance(result, dict) and "error" in result:
       metrics.errors.append(f"{tool_name}: {result['error']}")
   ```

5. Build tracking (in build_module branch):
   ```python
   build_attempts += 1
   metrics.build_attempts = build_attempts
   if result.get("result", {}).get("exit_code", 1) == 0:
       metrics.build_success = True
   ```

6. On success (when no tool_calls):
   ```python
   metrics.final_status = "success"
   metrics.save(Path("sessions") / "metrics.jsonl")
   ```

7. On max_iterations:
   ```python
   metrics.final_status = "max_iterations"
   metrics.save(Path("sessions") / "metrics.jsonl")
   ```

## Test Case

```python
def test_metrics_save(tmpdir: Path):
    from agentunreal.eval.metrics import SessionMetrics
    tmpdir = Path(str(tmpdir))
    m = SessionMetrics(session_id="123", task="test")
    m.record_tool("write_file")
    m.build_success = True
    m.save(tmpdir / "metrics.jsonl")
    lines = (tmpdir / "metrics.jsonl").read_text().splitlines()
    data = json.loads(lines[0])
    assert data["tool_calls"]["write_file"] == 1
    assert data["build_success"] is True
```