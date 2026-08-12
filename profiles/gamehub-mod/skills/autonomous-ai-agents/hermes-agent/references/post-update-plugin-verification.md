# Post-Update Plugin Verification — Reference

## Session Context

2026-05-11: Hermes v0.13.0 update revealed that icarus and hermes-lcm plugins
were not being loaded after the update. The config still listed them in
`plugins.enabled`, but the plugin scanner couldn't find them. LCM context
engine silently fell back to the built-in compressor.

## Root Cause

When running under a profile (senna), `get_hermes_home()` returns
`~/.hermes/profiles/senna/` — NOT the global `~/.hermes/`. The plugin
scanner looks for user plugins at `HERMES_HOME/plugins/`, which was
`~/.hermes/profiles/senna/plugins/`. But the plugins (icarus, hermes-lcm)
had been installed globally at `~/.hermes/plugins/` before the profile was
created, so the scanner never found them.

## The Fix

Symlink the profile's plugins directory to the global plugins directory:

```bash
mv ~/.hermes/profiles/<profile>/plugins{~,.old}
ln -s ~/.hermes/plugins ~/.hermes/profiles/<profile>/plugins
```

This makes `~/.hermes/plugins/` the single canonical source. All profiles
share it. `hermes plugins install` from any profile writes there.

## State Before Fix

```
~/.hermes/profiles/senna/plugins/
├── hermes-achievements/    ← runtime state only, no plugin.yaml
├── web-search-plus/        ← git-installed, profile-only
└── mnemosyne → symlink     ← symlink to pip package (no plugin.yaml)

~/.hermes/plugins/          ← where the real plugins were
├── hermes-lcm/             ← had plugin.yaml, never scanned from profile
├── icarus/                 ← had plugin.yaml, never scanned from profile
└── gbrain/                 ← deprecated
```

## State After Fix

```
~/.hermes/profiles/senna/plugins → ~/.hermes/plugins/  (symlink)

~/.hermes/plugins/
├── hermes-lcm/             ← enabled, loading
├── icarus/                 ← enabled, loading
└── web-search-plus/        ← migrated from profile to global
```

## Migration Steps (For Next Time)

1. Move profile-only plugins to global first:
   ```bash
   cp -a ~/.hermes/profiles/senna/plugins/web-search-plus ~/.hermes/plugins/web-search-plus
   ```

2. Remove state-only directories (no plugin.yaml — will be recreated):
   ```bash
   # hermes-achievements had only scan_checkpoint.json etc.
   ```

3. Remove deprecated plugins:
   ```bash
   # gbrain was cleaned from config previously
   ```

4. Create symlink:
   ```bash
   mv ~/.hermes/profiles/senna/plugins{,.old}
   ln -s ~/.hermes/plugins ~/.hermes/profiles/senna/plugins
   ```

5. Verify:
   ```bash
   hermes plugins list              # should show icarus, hermes-lcm
   grep 'context engine' ~/.hermes/profiles/senna/logs/errors.log  # should NOT show fallback
   ```

## Sensitivity

The context engine fallback is totally silent — no TUI banner, no CLI
warning, no gateway notification. The only way to detect it is checking
the error log. Treat this as the canary in the coal mine for plugin
loading issues.
