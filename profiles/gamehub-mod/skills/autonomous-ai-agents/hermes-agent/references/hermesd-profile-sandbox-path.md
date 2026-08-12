# hermesd — Profile Sandbox $HOME Resolution

## Symptom

```
hermesd --profile senna
→ Error: Profile 'senna' does not exist
```

But the profile directory exists at `~/.hermes/profiles/senna/` and running `hermesd` without `--profile` works fine (shows gateway running, sessions, etc. from root).

## Root Cause

In the profile's terminal sandbox, `$HOME` is set to the profile's home directory:

```
~/.hermes/profiles/senna/home/
```

When `hermesd` calls `Path.home() / '.hermes'` to resolve the hermes home, it resolves to:

```
~/.hermes/profiles/senna/home/.hermes
```

…which does NOT contain `profiles/senna/` under it. The `HermesPaths.__post_init__` then checks if `profiles/senna` is a directory inside that broken path and correctly returns false.

This affects any code that implicitly uses `~/.hermes` (via `Path.home()`) while inside a profile sandbox where `$HOME` has been redirected.

## Fix

Pass the real hermes home explicitly:

```bash
hermesd --hermes-home ~/.hermes --profile senna
```

Or set the env var:

```bash
export HERMES_HOME=~/.hermes
hermesd --profile senna
```

### Shell alias for convenience

```bash
alias senna-dash='hermesd --hermes-home ~/.hermes --profile senna'
```

## Upstream Fix Opportunity

In `hermesd/paths.py`, `HermesPaths.__post_init__` resolves the hermes home via `Path.home() / '.hermes'`. When inside a profile sandbox where `$HOME` points into the profiles directory, this resolves to the wrong path. A fix could:

1. Detect when `Path.home()` is inside the hermes profiles tree and walk up.
2. Or pass `--hermes-home` automatically from the profile's known root.

The `--hermes-home` flag already exists and works correctly — it just needs to be wired up in user-facing workflows (launchd plists, aliases, profile env).
