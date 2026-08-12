# Streaming CLI renderer (kill the black terminal)

The harness's `Agent.run()` blocks through plan → tool-loop → LLM and only
`print()`s the final string. The user sees a dead screen for the whole run.
Fix: one event hook on the Agent + a `rich.live.Live` renderer. No new
dependency (rich is already in requirements). Mirrors the fork's event model
(`tool.start` / `tool.complete`, one line per call, unicode marks).

## The hook (agent.py)

Add `self.on_event: Any = None` in `Agent.__init__`, a helper, and fire at the
single dispatch chokepoint (`_call_tool`) plus plan/result:

```python
def _emit(self, event_type: str, **kw: Any) -> None:
    if self.on_event:
        self.on_event(event_type, **kw)

def _call_tool(self, name: str, args: dict) -> Any:
    ...  # guardrails, lookup
    call_id = uuid.uuid4().hex[:8]
    self._emit("tool.start", id=call_id, name=name, args=args)
    try:
        result = {"result": tool(**args)}
    except Exception as e:
        result = {"error": str(e)}
    self._emit("tool.complete", id=call_id, name=name, result=result)
    return result
# also: self._emit("plan", steps=plan)  after _plan();  self._emit("result", content=...) before return
```

Why a single hook at `_call_tool`: every tool (planner, file/build/editor,
MCP, memory) funnels through it. One emit point covers all of them. Include a
local `id` so `start` and `complete` pair in the renderer.

## The renderer (ui_cli.py)

`rich.live.Live` + a `Group` of `Panel`s — one panel per completed tool, the
in-flight one with a braille spinner. Unicode marks: ▶ start, ✓ ok, ✗ error.

```python
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel

_SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

class LiveRenderer:
    def __init__(self, console=None):
        self.console = console or Console()
        self.live = Live(console=self.console, refresh_per_second=12)
        self._pending, self._done, self._plan = {}, [], []
        self._spin = 0

    def __enter__(self):  self.live.__enter__();  return self
    def __exit__(self, *_):  self.live.__exit__(None, None, None)

    def on_event(self, t, **kw):
        if t == "plan":
            self._plan = kw.get("steps") or []
        elif t == "tool.start":
            self._pending[str(kw["id"])] = {"name": kw["name"], "args": kw.get("args", {})}
        elif t == "tool.complete":
            r = kw.get("result", {})
            mark = "✗" if isinstance(r, dict) and "error" in r else "✓"
            summary = r.get("error", _summarize(r))[:120]
            self._pending.pop(str(kw["id"]), None)
            self._done.append((kw["name"], mark, summary))
        self._render()

    def _render(self):
        self._spin = (self._spin + 1) % len(_SPINNER)
        spin = _SPINNER[self._spin]
        blocks = []
        if self._plan:
            steps = "\n".join(f"  {i+1}. {s.get('tool')} — {s.get('reason')}" for i, s in enumerate(self._plan))
            blocks.append(Panel(steps, title="▸ Plan", border_style="cyan", expand=False))
        for p in self._pending.values():
            blocks.append(Panel(f"[dim]{_summarize(p['args'], 80)}[/dim]", title=f"{spin} {p['name']}", border_style="yellow", expand=False))
        for name, mark, summary in self._done:
            blocks.append(Panel(f"[dim]{summary}[/dim]", title=f"{mark} {name}", border_style="green" if mark=="✓" else "red", expand=False))
        self.live.update(Group(*blocks) if blocks else Text("status: idle"))
```

`_summarize` = `json.dumps(obj, ensure_ascii=False)[:limit]`.

## Wire into the REPL (agent.py `__main__`)

```python
from ui_cli import LiveRenderer
with LiveRenderer() as r:
    agent.on_event = r.on_event
    result = agent.run(task)
    agent.on_event = None
print(result)
```

## Verification (no API key needed)

- Stub the LLM (return one tool call then a final answer) and assert the hook
  emits `['tool.start', 'tool.complete', 'result']` in order.
- Render the panels to a string via a `Console()` (no TTY) and assert the
  `✓`/`✗` glyphs + plan text appear.

## Same hook feeds a Textual dashboard

`tui.py` currently calls `self.agent.run()` synchronously in `action_run_task`
→ freezes, same black screen. After this hook exists, run `agent.run` in a
Textual worker thread and push events from `on_event` into the `#log` widget.
No loop rewrite required. See `references/tui-dashboard.md` for the working
worker-thread + `call_from_thread` marshaling pattern.

## Machine contract: `--json` mode (cli-builder Pattern 3)

The harness entry (`python3 -m agent`) should ALSO emit a pure machine-readable
contract on stdout, separate from the human-facing renderer. This makes the
harness callable/parseable by other agents or scripts. Capture the full event
stream and emit ONE JSON object — never auxiliary text on stdout.

```python
# in agent.py __main__
if args.json:
    events = []
    agent.on_event = lambda t, **kw: events.append({"type": t, **kw})
    prompt = " ".join(args.task) or (sys.stdin.read().strip() if not sys.stdin.isatty() else "")
    if not prompt:
        print(json.dumps({"error": "no prompt provided (arg or stdin)"}, ensure_ascii=False))
        sys.exit(2)
    result = agent.run(prompt)
    agent.on_event = None
    print(json.dumps({"prompt": prompt, "events": events, "result": result}, ensure_ascii=False))
```

Verification: run with a stubbed LLM (no API key) and assert the emitted JSON has
`events` containing `tool.start`/`tool.complete`/`result` in order, and `result`
is the final answer. The cli-builder rule (suppress all non-JSON stdout) holds
because the renderer is NOT used in `--json` mode.

## Pyright pitfall: `on_event = None` typing

Annotate the hook as `self.on_event: Any = None`, not `self.on_event = None`.
The bare `= None` makes Pyright infer `None` as the type, so every call site
`self.on_event(...)` (and assigning a real callback) raises
`reportAttributeAccessIssue` / `reportOptionalCall`. `Any` keeps it call-safe.
