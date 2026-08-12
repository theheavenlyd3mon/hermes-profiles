---
name: hermes-fork-ui
description: Navigate, dissect, and modify the Hermes fork's CLI/TUI rendering — the two-stack architecture (Python `rich`+`prompt_toolkit` CLI vs TypeScript React-Ink TUI), the TUI↔Python-gateway event protocol, and the reusable streaming/tool-trail rendering patterns. Use when asked to "dissect the fork's UI", "how does the TUI render tool calls / streaming", "where is the tool-call UI", or when building a streaming agent TUI.
---

# Hermes fork — CLI/TUI rendering

## The one correction that matters

`ui-tui/` is **NOT** a Python `textual` app. It is a **React-Ink (TypeScript)** TUI.
The Python CLI (`cli.py` + `agent/`) uses **`rich` + `prompt_toolkit`**. These are
**two independent rendering stacks** that share almost nothing:

- Python CLI: `rich` for panels/tables/markdown/spinners, `prompt_toolkit` for the REPL + `patch_stdout`.
- TS TUI (`ui-tui/`): `ink`/`react`/`nanostores`, plus a local `@hermes/ink` bundle (chalk, cli-boxes, wrap-ansi, strip-ansi). Talks to the Python agent via a **gateway** over events, not in-process.

If a brief says "the TUI uses textual", correct it before doing anything else.

## Two stacks at a glance

| Concern | Python CLI | TS TUI (`ui-tui/`) |
|---|---|---|
| Libs | `rich`, `prompt_toolkit`, `Markdown` | `ink@6`, `react@19`, `nanostores`, `ink-text-input`, `unicode-animations` |
| Entry | `hermes_cli.main:main` / `run_agent:main` | `ui-tui/src/entry.tsx` |
| Build | setuptools (pyproject) | `npm run build:ink` (esbuild) then `node scripts/build.mjs` |
| Spinner | `agent/display.py::KawaiiSpinner` | `unicode-animations` braille frames |
| Tool-call UI | `agent/display.py` + `agent/tool_executor.py` | `components/thinking.tsx` (`ToolTrail`) + `components/messageLine.tsx` |
| Streaming | `patch_stdout` REPL | `components/streamingMarkdown.tsx` |
| Connects to agent | in-process | `GatewayClient` → Python gateway (undici) |

## Launch / build

TUI: `ui-tui/src/entry.tsx` — `new GatewayClient()` (L51) → `gw.start()` (L53) → `ink.render(<App gw={gw}/>)` (L141). No TTY → exit (L17-20). `resetTerminalModes()` on start + `process.on('exit')` (L24, L38) so a killed TUI doesn't leave DEC mouse tracking armed in the parent shell (bug #28419). `@hermes/ink` is bundled via esbuild (`packages/hermes-ink/package.json` build L7).

Python CLI: `cli.py` builds a `prompt_toolkit.Application` + `patch_stdout` (imports L58-71) so a live spinner and streamed text coexist with the input box.

## Event protocol (TUI ↔ gateway)

The TUI never renders directly off the model stream; the Python gateway emits
typed events that a handler reduces into store state. See
`ui-tui/src/app/createGatewayEventHandler.ts`:
- `tool.start` (L728) → `recordToolStart(tool_id, name, context, args_text)`
- `tool.progress` (L706) → `recordToolProgress(name, preview)`
- `tool.complete` (L738) → `recordToolComplete(...)` or `recordInlineDiffToolComplete(...)` when `inline_diff` present
- `tool.generating` (L713), `reaction` (L720), `clarify/approval/sudo/secret.request` (L776+)

**Pattern: the renderer is a pure function of store state**, not of the raw event. Keep that boundary — it's what makes the UI testable and lets the gateway be swapped.

## Tool-call render path (TS)

`streamingAssistant.tsx` flattens live segments → `messageLine.tsx`. A `trail` msg
with tools/thoughts renders `<ToolTrail>` (`thinking.tsx`); a `tool`-role msg renders
a bordered rounded `Box` (`messageLine.tsx` L110-120). Trail line format lives in
`lib/text.ts`:
- `toolTrailLabel(name)` snake→Title Case (L191)
- `formatToolCall(name, ctx)` → `Name("preview")` (L198)
- `buildToolTrailLine(...)` → `Name("preview") (1.2s) :: detail ✓/✗` (L205)

Tree rails `├─ └─` in `thinking.tsx::treeLead` (L54). In-flight tools get a braille
`Spinner` from `unicode-animations` (`thinking.tsx` L3, `Spinner` L153); frame sets
`THINK`/`TOOL` (L40-41).

## Streaming text (no flicker) — the key trick

`streamingMarkdown.tsx` does **not** re-tokenize the whole message per delta. It
splits `text` at the last stable top-level block boundary (blank line outside a
fenced code span): `stablePrefix` is passed to an inner `<Md>` memoized on its exact
text (grows monotonically, memo key matches → React reuses the subtree, zero
re-parse); `unstableSuffix` (the in-flight tail) is the only part re-parsed each
delta — O(unstable) not O(total). `boundedLiveRenderText` caps worst-case cost.

## Reusable patterns (the durable lesson)

1. **Event-driven UI**: agent emits `tool.start|progress|complete`; renderer = pure fn of state. Decouples transport from paint.
2. **One line per call**: `Name("preview") ✓/✗` — name + truncated arg + status glyph. Cheap, scannable.
3. **Braille spinners** (`unicode-animations`) for in-flight tools instead of redrawing.
4. **Incremental markdown**: split at last block boundary, memoize stable prefix, only re-parse the tail.
5. **Bounded live text** + `patch_stdout`-style stdout routing so the render loop doesn't clobber the input box.
6. **Terminal cleanup contract**: reset mouse/focus/paste modes on exit AND on a `process.on('exit')` backstop — killed TUIs otherwise leak DEC mouse tracking into the shell (bug #28419).

## Pitfalls

- Assuming `textual` for `ui-tui/` — wrong; it's React-Ink.
- Editing a `trail` renderer without threading `toolsMode`/`thinkingMode`/`activityMode` section visibility → empty `Box` gutter bug (see `messageLine.tsx` L42-101 and `domain/blockLayout.ts::hasLeadGap`).
- Forgetting `sys_platform` markers on Windows-only deps (`pyproject.toml` L98,140) — they won't install on macOS/Linux.
- `unicode-animations` frames can be multi-codepoint; `streamingAssistant`/`thinking` collapse to `[...f][0]` to keep width stable (thinking.tsx L157).

## References

- `references/fork-ui-map.md` — full file:line dissection of packages, build, tool-call rendering, and streaming (the source of truth for "where is X").
- `references/ink-streaming-patterns.md` — the reusable Ink/React streaming + tool-trail patterns, framework-agnostic, for building your own.
