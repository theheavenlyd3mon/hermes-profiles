# TUI Gateway ModuleNotFoundError — Root Cause and Fix

## Symptom

Third-party TUI apps (herm, built-in Hermes TUI) fail with:
```
/Library/Developer/CommandLineTools/usr/bin/python3: Error while finding module
specification for 'tui_gateway.entry' (ModuleNotFoundError: No module named 'tui_gateway')
```

## Root Cause

The TUI spawns `python -m tui_gateway.entry` as a subprocess. The Python
interpreter used falls back to the system Python (`/usr/bin/python3` or
`/Library/Developer/CommandLineTools/usr/bin/python3`) instead of the Hermes
Agent venv Python.

The venv lives at:
```
~/.hermes/hermes-agent/venv/bin/python
```

But the TUI's `resolvePython()` function searches in this order:
1. `$HERMES_PYTHON` or `$PYTHON` env var
2. `$VIRTUAL_ENV/bin/python`
3. `<root>/.venv/bin/python`
4. `<root>/venv/bin/python`
5. fallback: `python3` (system)

If the Hermes Agent source tree is at `~/.hermes/hermes-agent/`, the function
needs `root` to point there. But the TUI may be using `~/.hermes/` as root
(where there's no venv/bin/python), causing the fallback to system Python.

## Fix

Two env vars:

```bash
HERMES_PYTHON=~/.hermes/hermes-agent/venv/bin/python
HERMES_CWD=~/.hermes/hermes-agent
```

`HERMES_PYTHON` tells the TUI exactly which Python to use (skips the search).
`HERMES_CWD` tells the TUI which working directory to use (the `PYTHONPATH` is
derived from this).

## Apple Terminal Escape Code Dumping

**This is NOT an Apple Silicon issue — it's Apple Terminal.app specifically.**

Confirmed pattern: herm runs correctly when executed from a PTY session (tool-run commands) but always dumps escape codes in real Apple Terminal windows. The TUI framework (OpenTUI) initializes via `createCliRenderer()` which probes terminal capabilities. Apple Terminal responds to these probes, but the TUI crashes before consuming the responses.

**Full escape sequence dump seen in both attempts:**
```
10;rgb:ffff/ffff/ffff      ← OSC 10 text foreground color response
11;rgb:1e1e/1e1e/1e1e      ← OSC 11 text background color response
;1R;1R;1R;343;570t4;0;rgb:0000/0000/0000  ← CPR + window size + OSC 4
```

These are terminal query responses (OSC color queries, cursor position report,
window size) that the TUI sent during initialization but crashed before
consuming. One or more responses appears per shell prompt line.

**Root cause suspicion:**
- OpenTUI's `createCliRenderer()` does feature probing that Apple Terminal
  handles differently than kernel PTYs
- A prior TUI crash leaves terminal modes in a broken state (compounding)
- The native OpenTUI core binary (`@opentui/core-darwin-arm64`) may have
  compatibility quirks with Apple Terminal's VT100 implementation

**Workarounds (most effective first):**
1. Switch terminal emulator (iTerm2, Warp, Kitty, Alacritty) — works immediately
2. Use Hermes Desktop instead (Electron, not terminal-dependent)
3. `reset` then retry with `--no-splash` (sometimes helps if modes are stuck)

**Does not help:**
- Setting `HERMES_PYTHON` / `HERMES_CWD` (the Python path is correct; the crash is in OpenTUI, not the gateway subprocess)
- Using absolute vs `~` paths
- `--no-splash` flag alone

## macOS 15 "Unsupported by Apple" Gatekeeper

Hermes Desktop (ad-hoc signed Electron app) triggers macOS 15's stricter Gatekeeper even after `xattr -cr`. The message says "unsupported by Apple" or "cannot be verified."

**Bypass flow:**
1. First: `xattr -cr "/Applications/Hermes Agent.app"`
2. Right-click the app → Open → click Open in the dialog
3. If that doesn't work: System Settings → Privacy & Security → scroll down → "App was blocked" → Open Anyway

## Architecture Mismatch — "Incorrect Executable Format"

**Symptom:**
```
$ open "/Applications/Hermes Agent.app"
The application cannot be opened because it has an incorrect executable format.
```

**Root cause:** Downloaded the wrong CPU architecture variant for Hermes Desktop. The release page ships two macOS variants:

| Asset | Architecture | Mac type |
|-------|-------------|----------|
| `Hermes.Agent-*-arm64-mac.zip` | arm64 | Apple Silicon (M1/M2/M3/M4) |
| `Hermes.Agent-*-mac.zip` | x86_64 | Intel Macs |

**How to verify:**
```bash
file "/Applications/Hermes Agent.app/Contents/MacOS/Hermes Agent"
# Correct output for Intel:  Mach-O 64-bit executable x86_64
# Correct output for M-series:  Mach-O 64-bit executable arm64
```

**Fix:** Delete the wrong app, download the correct zip, extract, and re-install.

**Prevention:** Check which architecture your Mac uses before downloading:
```bash
uname -m
# arm64 → Apple Silicon, download *-arm64-mac.zip
# x86_64 → Intel, download *-mac.zip
```
