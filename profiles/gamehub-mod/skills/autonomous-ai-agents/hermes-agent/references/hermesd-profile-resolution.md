# fallback-model-config: see `references/fallback-model-config.md`
# hermesd Profile Resolution Issue

## The Problem

When `$HERMES_HOME` is set to a profile directory (e.g., `~/.hermes/profiles/senna`), running `hermesd --profile senna` fails with:

```
Error: Profile 'senna' does not exist
```

**Root cause**: `hermesd/paths.py` resolves the profile path as `$HERMES_HOME/profiles/<name>`. When `$HERMES_HOME` IS the profile directory, it looks for `profiles/senna` inside itself — which doesn't exist.

```
hermes_home = ~/.hermes/profiles/senna  (from $HERMES_HOME)
profile     = hermes_home / "profiles" / "senna"     →  ~/.hermes/profiles/senna/profiles/senna  ✗
```

## The Fix

**Explicitly pass the root hermes home**:

```bash
hermesd --hermes-home ~/.hermes --profile senna
```

**Shell function** (in real `~/.zshrc`, not profile sandbox `.zshrc`):

```zsh
hermesd() { command hermesd --hermes-home ~/.hermes --profile senna "$@"; }
```

**Environment variable** (alternative):

```bash
export HERMES_HOME=~/.hermes
```

## Why It Works

The real root hermes home is `~/.hermes/` (e.g., `~/.hermes`). Profiles live at `~/.hermes/profiles/senna/`. When `hermesd` gets the real root, it correctly finds `profiles/senna` as a subdirectory.

However, when the profile sandbox is active, `$HOME` may be the sandbox home (`~/.hermes/profiles/senna/home/`), and `HERMES_HOME` may already be set to the profile dir itself. The fix overrides `HERMES_HOME` with the actual root.

## Auto-loading the Active Profile

Once `--profile <name>` works, the user usually wants it to happen automatically — no flags needed every time.

**Shell function in the sandbox `.zshrc`** (inside `~/.hermes/profiles/<name>/home/`):

```zsh
# Auto-load the active profile in hermesd
hermesd() { command hermesd --profile senna "$@"; }
```

This is the cleanest approach because:
- The sandbox `.zshrc` only loads when the profile is active — no cross-contamination
- `"$@"` passes through any extra flags (e.g., `hermesd --snapshot`)
- No global config change needed

**Alternatives:**
- **Alias** (`alias hermesd='hermesd --profile senna'`) — same effect, slightly less flexible since bash aliases don't handle args as cleanly
- **Wrapper script** at `~/.hermes/profiles/<name>/scripts/hermesd` — more explicit but adds a layer
- **Environment variable** — there is no `HERMESD_PROFILE` env var; the only flag-based option is `--profile`

**Pitfall:** If a user has multiple profiles and switches between them, the shell function hardcodes one profile name. For multi-profile users, the better approach is a wrapper that reads the current profile name from `$HERMES_HOME` or a symlink.

## Upstream Opportunity

`hermesd/paths.py` could be patched to detect when `$HOME` or `$HERMES_HOME` points inside a Hermes profiles directory and walk up to find the real root. The logic: if the resolved profile path doesn't exist, try `Path(hermes_home).parent.parent` (walk up from `profiles/<name>`).

A second improvement: support a `HERMESD_DEFAULT_PROFILE` env var or read a `default_profile` from config.yaml so users don't need shell functions.
