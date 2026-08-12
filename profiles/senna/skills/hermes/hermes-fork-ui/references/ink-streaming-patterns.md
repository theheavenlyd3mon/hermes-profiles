# Reusable Ink/React streaming + tool-trail patterns

Framework-agnostic lessons extracted from the Hermes fork's TS TUI (`ui-tui/`).
Use these when building any streaming agent UI — not just Hermes.

## 1. Event-driven rendering (decouple transport from paint)

The TUI never renders off the raw model stream. The Python gateway emits typed
events (`tool.start`, `tool.progress`, `tool.complete`, `tool.generating`,
`reaction`, `clarify/approval/sudo/secret.request`) and a single handler
(`createGatewayEventHandler.ts`) reduces them into a store. Components are *pure
functions of store state* (`turnStore` via nanostores `useTurnSelector`).

Why it matters: transport (undici → gateway child) can be swapped/retried without
touching paint; the store is trivially unit-testable; a single reducer is the one
place event→state logic lives.

Apply: define a small event union, one reducer, a store, and render from the store.
Never call the renderer from the network callback.

## 2. One line per tool call

Format: `Name("preview") (1.2s) :: detail ✓/✗` (`lib/text.ts`):
- `toolTrailLabel(name)` snake→Title Case (`read_file` → `Read File`).
- `formatToolCall(name, ctx)` → `Read File("path/to/x.py")`.
- `buildToolTrailLine(...)` → appends `(duration_s)`, `:: note`, and `✓`/`✗`.

Keep each tool call to a single compact row. The preview is `compactPreview(...,64)`
— truncate args; the user expands via `/details`, they don't need the full dump inline.

## 3. Braille spinners for in-flight work

Use `unicode-animations` braille frame sets (`helix`, `cascade`, `scan`, …) instead
of redrawing a panel. Pools `THINK` (L40) and `TOOL` (L41) pick a deterministic
frame set per variant. Collapse each frame to its first codepoint (`[...f][0]`, L157)
so multi-codepoint glyphs don't jitter the row width.

Fixed `setInterval` advance (L166-170) with cleanup on unmount. Don't tie frame
advance to the network — the spinner runs independently and just stops when the
`tool.complete` event lands.

## 4. Incremental markdown (the load-bearing trick)

Problem: re-rendering `<Md text={full}/>` on every 20-char delta re-tokenizes the
whole message — O(total) per delta, hundreds of full re-parses over a long reply.

Fix (`streamingMarkdown.tsx`):
- Split `text` at the **last stable top-level block boundary** — a blank line
  outside a fenced code span.
- `stablePrefix`: passed to an inner `<Md>` **memoized on its exact text value**.
  During a turn the prefix only grows monotonically, so the memo key matches the
  previous render and React reuses the cached subtree — **zero re-tokenization**.
- `unstableSuffix`: the in-flight tail. A *separate* `<Md>` re-parses **only this
  tail** each delta → O(unstable length), not O(total).

Always bound worst-case work: `boundedLiveRenderText(...)` caps how much of the
live tail is tokenized per frame so one huge delta can't stall the render loop.

## 5. Stdout routing that doesn't clobber input

CLI side: `prompt_toolkit.patch_stdout` lets a live spinner + streamed text print
above the input box without corrupting it. TUI side: Ink owns the whole frame, so
this is structural — but the equivalent lesson is to keep the *input/compose* area
as a fixed layout region (not part of the streamed region) so text grows upward
into history while compose stays docked.

## 6. Terminal-mode cleanup contract

If you enable DEC mouse/focus/paste tracking (you must, for clickable `<Link>` in
a TUI), reset it on **both** exit paths:
- directly before teardown, AND
- a `process.on('exit')` backstop (runs exactly once, synchronous — `writeSync` ok).

A killed TUI that skips this leaks armed mouse tracking into the parent shell; the
next thing reading stdin (the shell, or a relaunched TUI mid-init) gets
`102;71M5;104;62M`-style garbage in its input box (Hermes bug #28419). Also reset
on graceful-exit cleanups and on `onSignal`.

## 7. Grouping / gutter discipline

Derive blank-line gaps from the **stable predecessor block**, never from the
block's own live content (`hasLeadGap` in `domain/blockLayout.ts`). A block that
renders nothing (e.g. a tool trail hidden by `/details`) must emit no floating gap —
gate visibility on content-bearing sections only, and advance the "previous block"
pointer only past blocks that actually paint (`blockRenders`). This keeps a
streaming block from jumping when it flushes into settled history.

## Pitfalls when adapting these

- **Don't memoize on a changing key.** The stable-prefix trick only works because
  the prefix is a pure function of already-settled text. If you memo on `text` that
  still includes the in-flight tail, you re-parse every delta — defeating the point.
- **Don't put the input box inside the scroll region.** Keep compose docked; stream
  into history above it.
- **Mind multi-codepoint spinner frames.** Wide/combining glyphs shift layout;
  collapse to one code point.
- **Reset terminal modes twice.** One exit path is never enough when a process can
  be SIGKILLed.
