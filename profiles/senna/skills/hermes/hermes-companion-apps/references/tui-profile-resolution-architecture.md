# TUI Profile Resolution Architecture

## The Problem

When `herm` TUI starts, it does NOT use the CLI profile system. A user can have `hermes profile use senna` active and run `hermes chat` on Senna, but `herm` will load the **default** profile's config, SOUL.md, and memories.

## Why: Two Code Paths

### CLI path (`hermes chat --profile senna`)

```
hermes_cli/main.py  →  _apply_profile_override()
                          ├── reads argv for -p/--profile
                          ├── checks $HERMES_HOME env (trusts if points to profiles/<name>)
                          ├── reads ~/.hermes/active_profile from disk
                          └── sets HERMES_HOME to the profile directory
                       →  AIAgent loads from that HERMES_HOME
```

Key function in `hermes_cli/main.py`:
```python
def _apply_profile_override():
    # 1. Check argv for -p/--profile flag
    # 2. If HERMES_HOME already points to a profile dir (parent.name == "profiles"), return early
    # 3. Read ~/.hermes/active_profile file
    # 4. If found, set HERMES_HOME = ~/.hermes/profiles/<name>
```

### TUI path (`herm`)

```
herm (Bun binary)  →  spawns: python -m tui_gateway.entry
                        ├── cwd = $HERMES_CWD or <root>
                        ├── PYTHONPATH = <root>
                        └── env = inherited from parent process

tui_gateway/entry.py  →  tui_gateway/server.py
                            └── _hermes_home = get_hermes_home()
                                    └── reads $HERMES_HOME env var
                                        └── fallback: ~/.hermes (default profile!)
```

`get_hermes_home()` in `hermes_constants.py`:
```python
def get_hermes_home() -> Path:
    val = os.environ.get("HERMES_HOME", "").strip()
    if val:
        return Path(val)
    # Falls back to ~/.hermes — the DEFAULT profile
    ...
```

The TUI gateway then reads config from `_hermes_home / "config.yaml"`, tools/state from `_hermes_home`, etc. It never reads `active_profile` or checks for `-p`.

## The Fix

Set `HERMES_HOME` in the `herm` alias environment so the TUI gateway uses the right profile directory:

```bash
alias herm='HERMES_HOME=~/.hermes/profiles/senna \
  HERMES_PYTHON=~/.hermes/hermes-agent/venv/bin/python \
  HERMES_CWD=~/.hermes/hermes-agent herm'
```

Three env vars needed:
| Env Var | Purpose | Value |
|---------|---------|-------|
| `HERMES_HOME` | Tells the gateway which profile to use | `~/.hermes/profiles/<name>` |
| `HERMES_PYTHON` | Tells the TUI which Python to use for the gateway | `~/.hermes/hermes-agent/venv/bin/python` |
| `HERMES_CWD` | Tells the TUI where to find `tui_gateway.entry` module | `~/.hermes/hermes-agent` |

## Verification

After updating the alias:
1. `source ~/.zshrc`
2. Run `herm`
3. The gateway loads `~/.hermes/profiles/senna/config.yaml` — check the model, skin, and SOUL.md are correct

Or check directly:
```bash
HERMES_HOME=~/.hermes/profiles/senna HERMES_PYTHON=~/.hermes/hermes-agent/venv/bin/python HERMES_CWD=~/.hermes/hermes-agent python -c "
from hermes_constants import get_hermes_home
print(get_hermes_home())
"  # Should print: ~/.hermes/profiles/senna
```

## Related

- `references/tui-gateway-path-issue.md` — Covers the ModuleNotFoundError (`tui_gateway` not found) and Apple Terminal escape code dumping
- The `hermes-agent` skill's `references/hermesd-profile-resolution.md` — Same class of problem for `hermesd` dashboard (profile resolution when `$HERMES_HOME` is set to the profile dir)
- https://github.com/NousResearch/hermes-agent/wiki/Profiles — Upstream profile documentation
