# Plugin Audit Methodology

How to find misplaced plugins in the skills directory, detect stale config entries, and consolidate duplicates.

## Detection

### Step 1: Find all plugin.yaml files on disk

```bash
find ~/.hermes -name "plugin.yaml" -not -path "*/state-snapshots/*" -not -path "*/home/*" 2>/dev/null
```

Every result should be inside a `plugins/` directory (either `~/.hermes/plugins/` or `~/.hermes/profiles/<name>/plugins/`). Any result in `skills/` is a misplaced plugin.

### Step 2: Check for plugins in the skills directory

```bash
for skilldir in ~/.hermes/skills/*/; do
  if [ -d "$skilldir" ] && [ -f "${skilldir}plugin.yaml" ]; then
    echo "PLUGIN in skills/: ${skilldir}"
  fi
done
```

### Step 3: Check enabled plugins in config vs installed on disk

Read `~/.hermes/profiles/senna/config.yaml` and look under `plugins.enabled:`. For each listed plugin, verify a corresponding directory exists:

```bash
grep -A20 "^plugins:" ~/.hermes/profiles/senna/config.yaml | grep "^  - " | sed 's/  - //'
```

Then check if each exists:
```bash
for plugin in disk-cleanup hermes-lcm icarus web-search-plus; do
  found=$(find ~/.hermes/plugins ~/.hermes/profiles/senna/plugins -maxdepth 2 -name "plugin.yaml" 2>/dev/null | grep -i "$plugin")
  if [ -z "$found" ]; then
    echo "STALE: $plugin listed in config but no plugin files found"
  else
    echo "OK: $plugin → $found"
  fi
done
```

## Fixing Misplaced Plugins

### When there's a single copy (misplaced in skills/)

```bash
# 1. Move to plugins/
mv ~/.hermes/skills/<plugin-name> ~/.hermes/plugins/<plugin-name>

# 2. Install properly to register it
hermes plugins install <github-repo> --enable
```

### When there are duplicates (in both skills/ and plugins/)

```bash
# 1. Remove the skills/ copy (it's the misplaced one)
rm -rf ~/.hermes/skills/<plugin-name>

# 2. Remove the plugins/ orphan (if install created a fresh copy)
rm -rf ~/.hermes/plugins/<plugin-name>

# 3. Verify the profile's installed copy is clean
ls ~/.hermes/profiles/senna/plugins/<plugin-name>/plugin.yaml
```

### When a plugin appears in config but has no files anywhere

```bash
# Remove stale line from config.yaml
vim ~/.hermes/profiles/senna/config.yaml
# Delete the line under plugins.enabled:
```

## Special Case: Pip-Installed Entry-Point Plugins

Some plugins are installed as pip packages with Python entry points, not as git-cloned directories. These do NOT appear in any `find ... -name plugin.yaml` search and do NOT show up in `hermes plugins list`.

**Examples:** `rtk-hermes` (registers as `rtk-rewrite`)

**How they register:** The pip package's `entry_points.txt` uses the `hermes_agent.plugins` entry point group (underscore, not dot):

```
[hermes_agent.plugins]
rtk-rewrite = rtk_hermes
```

**How to verify they exist:**

```bash
# 1. Check the package is installed in the Hermes venv
~/.hermes/hermes-agent/venv/bin/python -c "import rtk_hermes; print(rtk_hermes.__version__)"

# 2. Check entry point registration
cat ~/.hermes/hermes-agent/venv/lib/python3.11/site-packages/rtk_hermes-*.dist-info/entry_points.txt

# 3. Confirm it's in config.yaml's plugins.enabled list
grep -A20 "^plugins:" ~/.hermes/profiles/senna/config.yaml | grep "^  - " | grep rtk
```

**Pitfall:** Do NOT flag these as stale config entries just because they have no `plugin.yaml` on disk. The config entry is valid and points to an entry point in the Hermes venv, not a directory.

## Behavioral Signals

A directory is a **plugin** (not a skill) if it has:

| Signal | What to look for |
|--------|------------------|
| Manifest | `plugin.yaml` instead of `SKILL.md` |
| Python code | `__init__.py`, `*.py` files in root of directory |
| Git repo | `.git/` subdirectory (cloned from GitHub) |
| CLI install | Can be installed via `hermes plugins install <repo>` |

A directory is a **skill** (correctly placed) if it has:

| Signal | What to look for |
|--------|------------------|
| Manifest | `SKILL.md` with YAML frontmatter |
| Content | Markdown methodology, guidelines, procedures |
| No Python | No `__init__.py` or top-level `.py` executables |
| No `.git/` | Installed as files, not cloned repos |

## Common Pitfalls

### After install, the old copy is orphaned

`hermes plugins install <repo>` clones a fresh copy into the profile's plugins
directory (`~/.hermes/profiles/senna/plugins/`). If you manually moved a copy to
`~/.hermes/plugins/` first, that old copy is now orphaned. Clean it up:

```bash
rm -rf ~/.hermes/plugins/<plugin-name>
```

### A plugin is "enabled" but tools don't appear

New plugins take effect only on the next session (`/reset` or restart Hermes).
The `hermes plugins install --enable` flag registers it in config but doesn't
inject tools mid-conversation.

### Bundled vs installed vs misplaced confusion

Hermes plugins can exist in three places:
- **Bundled:** `~/.hermes/hermes-agent/plugins/<name>/` (ships with Hermes, do not touch)
- **Installed (root):** `~/.hermes/plugins/<name>/` (user-installed, shared across profiles)
- **Installed (profile):** `~/.hermes/profiles/<name>/plugins/<name>/` (profile-specific install)
- **Misplaced:** `~/.hermes/skills/<name>/` (wrong directory — move or remove)
