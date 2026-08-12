# Driving Interactive Hermes CLIs via Background PTY

Some Hermes wizards (`hermes moa configure`, setup flows) are interactive-only
terminal UIs with arrow-key pickers — no flags, no stdin-scriptable prompts.
Drive them as a background PTY process.

## Recipe

1. Start: `terminal(command="hermes --profile <p> moa configure <name>", background=true, pty=true)` → returns a `session_id`.
2. `process(action='poll', session_id=...)` to read the current screen. PTY pickers REPAINT the full screen on every keystroke, so the latest poll tail is the current state — ignore earlier frames in the log.
3. Arrow keys: send raw escape sequences via `process(action='write', ...)` — Up = `\x1b[A`, Down = `\x1b[B`. Multiple moves can be batched in one write (concatenate N sequences; verified 8–10 in one call).
4. Enter: `process(action='submit', data=' ')` — the payload is irrelevant, submit appends the carriage return that registers as select.
5. Repeat poll → navigate → submit until the wizard exits, then `process(action='wait')` to collect the final summary output.

## Gotchas (all hit for real, 2026-07-31)

- `process(action='write')` with EMPTY data writes 0 bytes — nothing happens. Same for a bare `\r` payload. Use `submit` for Enter.
- The cursor position marker (`→`) and selection marker (`(●)`) are different things — navigate by the `→` in the LATEST repaint, not the count of items you think you passed.
- Multi-select flows (e.g. "Add another reference model?") loop back to the provider picker after each pick — don't assume one selection ends the wizard.
- Cursor starts on the item after the previously-used provider in some pickers; always poll before counting arrows.

## One-liner verification after the wizard

`hermes --profile <p> moa list` (or the relevant `list` subcommand) prints the
saved result — treat the wizard's own "Saved ..." line plus the list output as
the confirmation, not the absence of errors.
