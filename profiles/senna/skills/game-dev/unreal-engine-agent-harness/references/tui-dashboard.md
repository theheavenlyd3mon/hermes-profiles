# TUI Dashboard for the UE Agent Harness

When the harness loop works in stub mode, add a Textual/Rich dashboard so the
user can see tool calls, memory, and the journal in one terminal window.

## Why a TUI instead of a plain REPL

A REPL only shows the final answer. A TUI shows:

- Live task log with timestamps.
- Memory state while the task runs (or after it finishes).
- Journal contents without opening another file.
- Sidebar status: bridge mode, memory on/off, current model.
- Session log files written to `sessions/YYYYMMDD_HHMMSS.jsonl`.

## Minimum viable dashboard

Use `textual` + `rich`. Install into the same venv:

```bash
pip install textual rich
```

Key widgets:

| Widget | Purpose |
|--------|---------|
| `Input` | Task prompt entry. |
| `Log` | Timestamped agent/user messages. |
| `TextArea` (read-only) | Memory tab and journal tab. |
| `Static` | Sidebar: config summary, status line. |
| `Button` | Run / Clear actions. |

Keep the layout simple: a narrow sidebar and a main area with tabs.

## Wiring the agent into the TUI (worker thread — NOT blocking)

The TUI must reuse the same `Agent` class as the REPL and one-shot CLI. But
`agent.run()` is blocking and I/O-bound — calling it directly in a Textual
event handler (`action_run_task`, `on_button_pressed`) freezes the UI and shows
nothing until it returns (the same black-screen bug, just framed in Textual).

Fix: run `agent.run` in a Textual **worker thread** and marshal events back to
the main thread. The `on_event` hook from `streaming-cli-renderer.md` already
exists, so you only wire it to `call_from_thread`.

```python
def _run_current_task(self):
    if self._busy:           # guard against overlapping runs (worker not re-entrant here)
        return
    self._busy = True
    self.agent.on_event = self._agent_event          # hook into the run loop
    self.run_worker(self._execute, prompt, thread=True, group="task")  # type: ignore[arg-type]

def _execute(self, prompt: str) -> None:
    result = self.agent.run(prompt)                  # runs OFF the main thread
    self.call_from_thread(self._finalize, result)   # marshal result to main thread

def _finalize(self, result: str) -> None:
    self._say_agent(result)
    self._busy = False
    self.agent.on_event = None

def _agent_event(self, event_type: str, **kw: object) -> None:
    # fired from the worker thread — marshal every event to the main thread
    self.call_from_thread(self._render_event, event_type, kw)

def _render_event(self, event_type: str, kw: dict) -> None:
    # now on the main thread: safe to write RichLog / widgets
    if event_type == "plan":
        self._plan_note(kw.get("steps") or [])
    elif event_type == "tool.start":
        self.tools().write(Text(f"⏳ {kw.get('name')}", style="yellow"))
    elif event_type == "tool.complete":
        ...
```

KEY RULES:
- `run_worker(fn, arg, thread=True)` — `thread=True` runs the synchronous
  `agent.run` off the main loop. The `type: ignore[arg-type]` is needed because
  `run_worker`'s generic signature wants an `Awaitable`; with `thread=True`
  Textual wraps a sync fn, so the lint error is a known false positive.
- NEVER write to RichLog/Textual widgets from inside `_execute` or `_agent_event`
  (they run on the worker thread). Only write from `_render_event` /
  `_finalize`, which run on the main thread via `call_from_thread`.
- Keep a `_busy` guard so the user can't stack two runs (the worker group is not
  re-entrant by default).

## Two-pane layout (chat + tool calls)

A useful default once the loop works: LEFT = chat scrollback (`you ›` / `plan ›`
/ `agent ›` bubbles in a `RichLog`), RIGHT = live tool-call cards (`VerticalScroll`
+ `RichLog`), one line per call numbered and marked `⏳` running / `✓` done /
`✗` error with args/result summaries. A `--json` contract (see
`streaming-cli-renderer.md`) is the machine-facing sibling of this human-facing
view — build one, you get both from the same hook.

Dark-murim palette example (CSS variables in the `App`):
`$background: #0c0c0e; $surface: #141417; $panel: #18181c; $text: #c8c8cf;
$primary: #6b3a3a; $accent: #9a4a4a;` — desaturated/cold with a faint blood
accent, matches a noir martial-arts tone without adding a skinning dependency.

## Session logging (fix the datetime deprecation)

`datetime.utcnow()` is deprecated in Python 3.12+. Use:

```python
from datetime import datetime, timezone
self.session_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
```

## Common pitfalls

- **Adding the TUI before the loop works.** The ReAct loop and stub tests
  should pass before you invest in widgets.
- **Letting the TUI import crash on headless machines.** Keep the TUI in its
  own file (`tui.py`) so CI and tests can import the rest of the harness
  without pulling in `textual`.
- **Blocking the UI during `agent.run`.** Do NOT call `agent.run()` directly in
  an event handler — it freezes the UI. Run it in a worker thread
  (`run_worker(..., thread=True)`) and stream events back via `call_from_thread`,
  as shown above. This is not a "v1 later" optimization; the harness blocks
  through plan→tool-loop→LLM, so any non-trivial task deadlocks the UI.
- **Writing widgets from the worker thread.** Only touch RichLog/widgets from
  `call_from_thread`-marshaled callbacks (`_render_event`, `_finalize`), never
  from `_execute` or `_agent_event`.
- **Forgetting to refresh memory/journal after a run.** If you keep those tabs,
  refresh them in `_finalize` so the user sees the durable state just created.

## Example entry point

```bash
cd /path/to/ue-agent-harness
source .venv/bin/activate
python3 tui.py
```

The TUI should be optional: the harness must still work as `python3 repl.py`
or `python3 agent.py "task here"` without it.
