# Fork UI map — file:line dissection

Derived from a `hermes-agent` reference fork checkout at `hermes-agent-fork-reference/`.

## Packages / manifests

### Python CLI — root `pyproject.toml`
- `rich==14.3.3` (L50) — panels, tables, markdown, syntax, trees, `Live`.
- `prompt_toolkit==3.0.52` (L62) — REPL, `patch_stdout`, layout, key bindings.
- `Markdown==3.10.2` (L84) — md→html for gateway delivery (now on default path).
- Exact-pin policy: every direct dep pinned to `==X.Y.Z` (L24-44) — supply-chain hardening after the Mini Shai-Hulud worm hit `mistralai` 2.4.6 (L30-33). Provider/backend deps live in `[project.optional-dependencies]` and lazy-install via `tools/lazy_deps.py` (L42-43, L143+).
- Scripts (L307-310): `hermes=hermes_cli.main:main`, `hermes-agent=run_agent:main`, `hermes-acp=acp_adapter.entry:main`.
- Packages found (L356-357): `agent`, `tools`, `hermes_cli`, `gateway`, `tui_gateway`, `cron`, `acp_adapter`, `plugins`, `providers`. Note: `tui_gateway` exists in the Python tree but the *actual* TUI is the separate `ui-tui/` Node app — do not conflate.

### TS TUI — `ui-tui/package.json`
- deps: `ink ^6.8.0`, `react ^19.2.4`, `@nanostores/react` + `nanostores`, `ink-text-input ^6`, `unicode-animations ^1.0.3`, `undici ^6` (GatewayClient transport).
- `@hermes/ink` is a local file: dep (`"@hermes/ink": "file:./packages/hermes-ink"`) — a hand-rolled Ink re-export bundle.
- scripts: `dev` = `build:ink && tsx --watch src/entry.tsx`; `build` = `node scripts/build.mjs`; `build:ink` = `npm run build --prefix packages/hermes-ink`; `check` = build:ink + typecheck + test.

### TS TUI — `ui-tui/packages/hermes-ink/package.json`
- Custom Ink bundle (esbuild, ESM, `--packages=external`): holds `Box`, `Text`, `Ansi`, `NoSelect`, `CLI` primitives re-exported + `FrameEvent` type for perf.
- deps: `chalk`, `cli-boxes`, `wrap-ansi`, `strip-ansi`, `bidi-js`, `get-east-asian-width`, `emoji-regex`, `react-reconciler`, `semver`, `signal-exit`.

## Build / launch

### TUI
- `ui-tui/src/entry.tsx`:
  - L1-4 `forceTruecolor.js` import first (nudges chalk/supports-color before init).
  - L17-20 no-TTY → `console.log('hermes-tui: no TTY'); exit(0)`.
  - L24 `resetTerminalModes()` on start; L38-40 `process.on('exit')` backstop re-runs it (bug #28419: killed TUI left DEC mouse tracking armed in parent shell).
  - L45-49 Termux keeps prior output; desktop clears with `\x1b[2J\x1b[H\x1b[3J`.
  - L51-53 `const gw = new GatewayClient(); gw.start()`.
  - L124-129 lazy-loads `@hermes/ink`, `./app`, `./lib/perfPane`, `./lib/fpsStore`.
  - L133-139 `onFrame` attached only when perf/fps flags on (ink skips timing otherwise).
  - L141-151 `ink.render(<App gw={gw}/>, { exitOnCtrlC:false, onFrame, onHyperlinkClick })`.
  - Graceful exit (L58-85): cleanups reset modes + `gw.kill('graceful-exit-cleanup')`; SIGINT ignored in DASHBOARD_TUI_MODE so the embedded PTY child can't be killed.
  - Memory monitor (L87-116): onCritical → `process.exit(137)` + heap dump breadcrumb (otherwise a render-tree blowup OOMs silently as a bare gateway `stdin EOF`, bug #34095).

### Python CLI
- `cli.py` L58-71 imports `prompt_toolkit` (Application, Layout, HSplit, Window, FormattedTextControl, ConditionalContainer, KeyBindings, patch_stdout, FileHistory, Style). `patch_stdout` is what lets a spinner + streamed text coexist with the input box.

## Tool-call rendering

### Python CLI
- `agent/display.py::KawaiiSpinner` (L969-1464): braille frames (`SPINNERS`, L972), kawaii faces `KAWAII_WAITING`/`KAWAII_THINKING` (L984-993), `THINKING_VERBS` (L995). `__init__` captures `sys.stdout` NOW before any child-agent `redirect_stdout(devnull)` (L1052-1054). `print_fn` override routes all output (silence background agents).
- `agent/tool_executor.py` drives it: L659, L1382, L1445, L1477 start quiet spinner when `_should_emit_quiet_tool_messages()` + `_should_start_quiet_spinner()`; L1521 builds cute completion message via `_get_cute_tool_message_impl(...)`.
- `agent/moa_loop.py::_render_tool_calls` (L453) for the MoA aggregator path.
- Pure display fns in `display.py` (no AIAgent dep): `redact_tool_args_for_display` (L390), `summarize_shell_command` (L315), `get_tool_emoji` (L147), `set_tool_preview_max_len` (L115, configurable via `display.tool_preview_length`).

### TS TUI
- `ui-tui/src/components/streamingAssistant.tsx`:
  - L14-15 `groupedSegments` folds a `Msg[]` via `appendToolShelfMessage`.
  - L34-37 pulls `streamSegments`, `streamPendingTools`, `streaming`, `tools` from `turnStore` (nanostores selector `useTurnSelector`).
  - L49 maps stream segments to `LiveBlock[]`; L51-53 appends active tools block; L55-63 appends streaming block (with pending tools) or a pending-tools trail.
  - L70-97 renders each block via `<MessageLine>`, advancing the grouping `prev` only past blocks that actually paint (`blockRenders`, L92) — keeps streaming block from jumping when it flushes.
- `ui-tui/src/components/messageLine.tsx`:
  - L42-51 resolves `thinkingMode`/`toolsMode`/`activityMode` via `sectionMode(...)` (per-section overrides win).
  - L60 `hasLeadGap(prev, msg)` from `domain/blockLayout.ts` — one blank line above a block iff it opens a new visual group vs the block above; stream-safe (derived from stable predecessor).
  - L66-75 `trail` with todos → `<TodoPanel>`.
  - L77-93 `trail` with tools/thoughts → `<ToolTrail>`.
  - L99-101 empty trail → render nothing (no floating gutter gap).
  - L103-122 `tool`-role msg → bordered rounded `Box`, `marginLeft=3`, `wrap="truncate-end"`; ANSI preserved via `<Ansi>`, else muted preview; `(empty tool result)` fallback.
  - L124-189 role glyph/prefix from `domain/roles.ts`, gutter width from `lib/inputMetrics.ts`; L158-160 renders non-user ANSI as `<Ansi>`; L162-173 assistant → `<StreamingMd>` (isStreaming) or `<Md>`; L140-155 collapsible long system message.
- `ui-tui/src/components/thinking.tsx` (`ToolTrail` + tree):
  - L40-41 `THINK`/`TOOL` braille spinner name pools.
  - L54-55 `treeLead(rails, branch)` → `├─ `/`└─ ` with rail `│ `/`  `.
  - L153-173 `Spinner` component: picks a variant frame set via `pick()`, collapses multi-codepoint frames to `[...f][0]` (L157) for stable width, `setInterval` advance (L166-170).
  - Tool-call lines assembled as `● <line>` tree rows (L451-465 in `SubagentAccordion`; the live trail uses the same `buildToolTrailLine` format from `lib/text.ts`).

## Streaming text

- `ui-tui/src/components/streamingMarkdown.tsx`:
  - L1-15 doc: naive `render <Md text={full}/>` re-tokenizes the entire message every delta (150 full re-parses for a 3 KB reply at 20-char batches).
  - Fix: split at last stable top-level block boundary (blank line outside fenced code span) into `stablePrefix` (memoized on exact text, grows monotonically → React reuses subtree, zero re-parse) and `unstableSuffix` (the in-flight tail, re-parsed each delta — O(unstable) not O(total)).
  - `boundedLiveRenderText` (from `lib/text.ts`) caps worst-case cost so a single huge delta can't stall the frame.

## Store / event wiring

- `ui-tui/src/app/turnStore.ts` — nanostores store of the current turn: `streamSegments`, `streaming`, `streamPendingTools`, `tools`, `todos`, `todoCollapsed`. `useTurnSelector` is the memoized selector.
- `ui-tui/src/app/createGatewayEventHandler.ts` — reduces gateway events into the store:
  - `tool.start` L728 → `recordToolStart(tool_id, name, context, args_text)`.
  - `tool.progress` L706 → `recordToolProgress(name, preview)`.
  - `tool.complete` L738 → `recordToolComplete(tool_id, name, error, summary, duration_s, todos, resultText)`; if `inline_diff` present uses `recordInlineDiffToolComplete(...)` (L753).
  - `tool.generating` L713, `reaction` L720, `clarify/approval/sudo/secret.request` L776+.
- `ui-tui/src/gatewayClient.ts` — `undici` transport to the Python gateway; spawns/kills the gateway child (`gw.kill`, `gw.start`).
