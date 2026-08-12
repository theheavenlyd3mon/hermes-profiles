# Tool Installation in Profile Sandbox — $HOME Redirection

## Problem

When running shell commands from inside a Hermes profile session (e.g. Senna,
Foreman, Coder), the Hermes sandbox redirects `$HOME` to the profile's sandboxed
home directory: `~/.hermes/profiles/<name>/home/` instead of the real home
(`/Users/<you>/`).

Tools that use `$HOME` to determine their install prefix — most notably
`uv tool install`, `pip install --user`, and any tool that installs binaries to
`~/.local/bin/` — will place executables in the **sandboxed** `$HOME/.local/bin/`
instead of the real `~/.local/bin/`. The user's terminal shell does NOT have the
sandboxed path on `PATH`, so the installed command is not found.

## Concrete Example (hermesd)

```bash
# Inside profile session — this installs to the wrong location:
uv tool install hermesd

# Result: binary lands at
#   ~/.hermes/profiles/senna/home/.local/bin/hermesd
# But the user's real PATH has:
#   ~/.local/bin/hermesd     ← NOT found
```

## Diagnosis

```bash
# 1. Check where uv actually put it
uv tool list                     # shows "installed"
which hermesd                    # "not found" or wrong path
find ~ -name hermesd -type f 2>/dev/null   # find the actual binary

# 2. Verify the sandboxed $HOME
echo $HOME                       # inside a profile session
# Shows: ~/.hermes/profiles/senna/home/

# 3. Check your real PATH
echo $PATH | tr ':' '\n' | grep .local/bin
# Should show: ~/.local/bin
```

## Fix

Override `$HOME` explicitly to the real home when installing:

```bash
HOME=~ uv tool install hermesd --force
HOME=~ pip install --user hermesd
```

After the fix, verify:

```bash
~/.local/bin/hermesd --snapshot   # should work
which hermesd                                  # should now resolve
```

## Affected Tools

Any tool that reads `$HOME` to determine its install prefix:

| Tool | Install path pattern | Example fix |
|------|---------------------|-------------|
| `uv tool install` | `$HOME/.local/bin/` | `HOME=~ uv tool install <pkg>` |
| `pip install --user` | `$HOME/.local/bin/` | `HOME=~ pip install --user <pkg>` |
| `npm install -g` | `$HOME/.npm-global/` | `npm config set prefix ~/.npm-global` |
| `cargo install` | `$HOME/.cargo/bin/` | `HOME=~ cargo install <pkg>` |
| `go install` | `$HOME/go/bin/` | `HOME=~ go install <pkg>` |

## Principle

Set `HOME=/Users/<you>` before any command that installs system-wide
executables from within a profile session. For read-only operations and
profile-local data (skills, plugins, config files), the sandboxed `$HOME` is
correct and intentional — it ensures profile isolation. Only override it for
**binary installation** commands.

## Related

- See the `.env` section in the parent skill for how `~` path resolution
  differs inside a profile (a closely related but distinct issue).
- See `mnemosyne-consolidation-cron.md` for the same pitfall affecting
  `Path.home()` in Python scripts run from cron.
