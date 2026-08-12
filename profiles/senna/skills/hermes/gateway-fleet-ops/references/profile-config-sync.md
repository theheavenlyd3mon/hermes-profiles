# Profile Config Sync

## Failure Mode — Blind Bulk Overwrite

Syncing all `~/.hermes/profiles/*/config.yaml` from one canonical source is not a
safe default. Unique per-profile deltas can be destroyed: local model/provider
overrides, platform tweaks, gateway settings, or docs copy expectations.

## Required Sequence

1. Diff every target profile against the intended source config.
2. Record what is unique in each profile.
3. Ask the user before destroying diffs unless they explicitly say “do not preserve”.
4. If deltas exist, sync the base, then re-apply deltas at the exact same YAML locations.
5. Restart only Discord-running profiles; validate YAML parse first; verify `Connected as`.

## Verification

```bash
ruby -e "require 'yaml'; YAML.load_file('~/.hermes/profiles/<name>/config.yaml')"
```

## Restore Expectation

If unique deltas are found later, restore them from snapshots/state-snapshots/ or
Windows-side live configs, not from memory.
