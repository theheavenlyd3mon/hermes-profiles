# RTK-Hermes Post-Update Recovery

## Symptoms

After `hermes update`, terminal commands are no longer being rewritten through RTK. The config still has `rtk-rewrite` in `plugins.enabled` but the plugin doesn't load.

## Root Cause

The update's `uv` cache cleanup removes pip-installed packages from the venv. `rtk-hermes` provides the `rtk-rewrite` plugin via Python entry points (not a directory symlink). When the package is wiped, the entry point disappears.

## Recovery Steps

### 1. Verify the problem
```bash
~/.hermes/hermes-agent/venv/bin/pip show rtk-hermes 2>&1
# Expected: "Package(s) not found"
```

### 2. Reinstall
```bash
# Standard pip install works fine:
~/.hermes/hermes-agent/venv/bin/pip install rtk-hermes

# Alternative (uv):
~/.local/bin/uv pip install --python ~/.hermes/hermes-agent/venv/bin/python --upgrade rtk-hermes
```

Both methods work. Use whichever is available.

### 3. Verify
```bash
~/.hermes/hermes-agent/venv/bin/python3 -c "
import importlib.metadata as md
try:
    dist = md.distribution('rtk-hermes')
    print(f'rtk-hermes {dist.metadata[\"Version\"]} installed')
    print(f'entry_points: {list(dist.entry_points)}')
except md.PackageNotFoundError:
    print('NOT INSTALLED')
"
```

### 4. Restart gateway
```bash
hermes gateway restart --profile senna
```

## Prerequisites

- RTK itself must be installed globally (via brew): `rtk --version` should show 0.39.0+
- The `rtk-rewrite` entry must be in `plugins.enabled` in the profile config

## Prevention

Add rtk-hermes verification to the post-update checklist alongside mnemosyne.
