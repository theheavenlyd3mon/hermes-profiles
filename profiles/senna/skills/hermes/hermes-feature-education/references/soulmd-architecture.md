# SOUL.md Architecture — Root vs Per-Profile Resolution

Corrected 2026-06-26 via live code audit of `agent/prompt_builder.py` and `hermes_cli/main.py`.

## How SOUL.md Is Loaded

```python
# agent/prompt_builder.py:load_soul_md()
soul_path = get_hermes_home() / "SOUL.md"
```

`get_hermes_home()` returns `$HERMES_HOME`. The question is: **what is `HERMES_HOME`?**

## Resolution Chain

| Scenario | Impact on `HERMES_HOME` | SOUL.md loaded from |
|----------|------------------------|---------------------|
| Default (no profile) | `~/.hermes/` (or `%LOCALAPPDATA%/hermes/` on Windows) | `~/.hermes/SOUL.md` |
| `hermes -p senna` | `~/.hermes/profiles/senna/` | `~/.hermes/profiles/senna/SOUL.md` |
| `hermes profile use senna` (sticky) | `~/.hermes/profiles/senna/` (on next `hermes`) | `~/.hermes/profiles/senna/SOUL.md` |

The mechanism: `_apply_profile_override()` in `hermes_cli/main.py` runs BEFORE any agent modules import. It reads `--profile`/`-p` from argv, calls `resolve_profile_env(name)` → `get_profile_dir(name)` → returns `~/.hermes/profiles/<name>/`, and sets `os.environ["HERMES_HOME"]` to that path. By the time `load_soul_md()` runs, `get_hermes_home()` returns the profile's directory.

**Key takeaway: Per-profile SOUL.md IS auto-loaded when that profile is active.** The root and profile SOUL.md files are separate files in separate directories — they just happen to both be named `SOUL.md` in different `HERMES_HOME` contexts.

## Why "Root vs Profile" Confusion Happens

1. The Hermes docs say "SOUL.md is loaded from $HERMES_HOME" — which is correct, but users think `$HERMES_HOME` is always `~/.hermes/`
2. In early Hermes versions (pre-profiles), there was only one `HERMES_HOME` and one `SOUL.md`
3. Profile isolation introduced per-profile `HERMES_HOME` but the doc's wording stayed the same
4. Multi-agent orchestration users create per-profile SOUL.md files and assume they're "blueprints," not realizing they ARE the live identity when the profile is active

## Practical Consequences

- `~/.hermes/SOUL.md` and `~/.hermes/profiles/senna/SOUL.md` are both live identities — they just answer to different profile contexts
- Copying a profile's SOUL.md to root only matters if you want the **default** (no-profile) session to use that persona
- A profile WITHOUT a SOUL.md falls back to the built-in default identity ("You are Hermes Agent...")
- `hermes profile create` auto-seeds a template SOUL.md precisely to prevent this silent fallback

## Verification

To check which SOUL.md is actually being loaded in a given session:
```bash
# Check what HERMES_HOME resolves to for the active profile
hermes status  # look for "Project:" path

# Or check directly
echo $HERMES_HOME             # only if set as env var
cat ~/.hermes/active_profile  # sticky profile, if set

# Read the SOUL.md that's actually in play
cat "$(hermes status 2>&1 | grep 'Project:' | awk '{print $2}')/SOUL.md"
```
