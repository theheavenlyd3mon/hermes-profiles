# Approval V2: Interactive `ask` Mode

## What changed

Approval mode `ask` went from a stub that returned `{"error": "Approval required"}` to a real interactive stdin prompt. The approval prompt and the dry_run→write_file hash gate are **two independent layers**:

1. **Approval prompt** (asks mode): "should this dangerous tool run at all?" — prompts on stdin, defaults to deny, auto-approves if the dry_run hash matches.
2. **Hash gate** (always on): "has this exact content been reviewed via dry_run?" — hash-matches `path+content` against the last `dry_run` call.

Both must pass for `write_file` to execute.

## The `_call_tool` flow

```python
def _call_tool(self, name: str, args: dict) -> Any:
    # Layer 1: readonly mode
    if self.config.approval_mode == "readonly" and name not in READONLY_TOOLS:
        return {"error": f"Readonly mode: {name} is not allowed."}

    # Layer 2: ask mode — prompt for dangerous tools
    if self.config.approval_mode == "ask" and name in DANGEROUS_TOOLS:
        h = hashlib.sha256((args.get("path", "") + args.get("content", "")).encode()).hexdigest()
        if h == self._last_dry_run_hash:
            pass  # dry_run already reviewed, proceed
        else:
            approved = self._prompt_approval(name, args)
            if not approved:
                return {"error": f"Approval denied for {name}."}

    # Layer 3: hash gate (always enforced)
    tool = self.tools.get(name)
    if not tool:
        return {"error": f"Unknown tool: {name}"}
    if name == "write_file":
        h = hashlib.sha256((args.get("path", "") + args.get("content", "")).encode()).hexdigest()
        if h != self._last_dry_run_hash:
            return {"error": "write_file blocked: call dry_run with the same path+content first."}
    if name == "dry_run":
        self._last_dry_run_hash = hashlib.sha256((args.get("path", "") + args.get("content", "")).encode()).hexdigest()

    # Execute
    call_id = uuid.uuid4().hex[:8]
    self._emit("tool.start", id=call_id, name=name, args=args)
    try:
        result = {"result": tool(**args)}
    except Exception as e:
        result = {"error": str(e)}
    self._emit("tool.complete", id=call_id, name=name, result=result)
    return result
```

## Test patterns (tests/test_approval.py)

| Test | What it verifies |
|---|---|
| `test_readonly_blocks_dangerous` | readonly mode rejects all DANGEROUS_TOOLS |
| `test_readonly_allows_safe_tools` | readonly mode allows READONLY_TOOLS |
| `test_ask_mode_prompts_and_denies` | ask mode prompts, "n" denies |
| `test_ask_mode_prompts_and_approves` | ask mode prompts, "y" approves but hash gate still blocks (need dry_run first) |
| `test_ask_mode_auto_approves_after_dry_run` | ask mode auto-approves when dry_run hash matches (no prompt) |
| `test_ask_mode_prompts_on_different_content` | ask mode prompts when content differs from dry_run, but hash gate blocks after approval |
| `test_ask_mode_eof_denies` | ask mode denies on EOF (non-interactive context) |
| `test_dangerous_tools_set` | DANGEROUS_TOOLS contains write_file, build_module, editor_command |

## Key insight

The approval prompt fires **before** the hash gate. If the user approves a write_file whose content differs from the last dry_run, the prompt passes but the hash gate still blocks. This is correct: the prompt is about "is this tool safe to run?" while the hash gate is about "has this exact content been reviewed?".
