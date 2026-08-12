# `~/.hermes/hermes-agent/` Is the CLI Backbone — Never Move It

## The Chain

The `hermes` CLI command is a chain of hard-coded paths:

```
~/.local/bin/hermes                          (bash wrapper)
  -> exec ~/.hermes/hermes-agent/venv/bin/hermes   (Python entrypoint)
     -> #!~/.hermes/hermes-agent/venv/bin/python3   (venv python)
        -> imports hermes_cli.main from hermes-agent source
```

Additionally, the senna profile's PATH prepends
`~/.hermes/profiles/senna/home/.local/bin/` which contains another
wrapper pointing to the profile's venv. Both ultimately depend on
the hermes-agent source tree being present.

## What Breaks If You Move It

1. `~/.local/bin/hermes` still points to the OLD location -> `command not found`
2. Any venv scripts with hard-coded shebangs break
3. MCP server binaries in the venv become unreachable
4. Gateway processes can't start (they invoke `hermes gateway run`)
5. The API server can't start

The user will have to run the hermes installer to recover. Config,
.env, auth.json, and profiles survive (they live at `~/.hermes/`
level, not inside `hermes-agent/`), but all code state is lost.

## Correct Approach: Symlink Profile to Root

```
# Root stays put (CLI depends on it)
~/.hermes/hermes-agent/              <- REAL directory (894 MB)

# Profile points to root via symlink
~/.hermes/profiles/senna/hermes-agent/ -> ~/.hermes/hermes-agent/
```

Benefits:
- One source of truth, can't drift out of sync
- Saves ~894 MB per profile copy removed
- CLI, gateways, MCP servers all resolve through the symlink
- Both paths show the same inode (`stat -f "%i"` to verify)

## How to Consolidate After an Accidental Copy

If someone already copied hermes-agent into a profile:

```bash
# 1. Make sure root is at the same (or newer) commit
cd ~/.hermes/hermes-agent
git log --oneline -1
cd ~/.hermes/profiles/<name>/hermes-agent
git log --oneline -1
# If profile is newer: cd ~/.hermes/hermes-agent && git checkout <commit>

# 2. Compare venv packages (should be identical for hermes-agent)
diff <(~/.hermes/hermes-agent/venv/bin/pip list --format=freeze | sort) \
     <(~/.hermes/profiles/<name>/hermes-agent/venv/bin/pip list --format=freeze | sort)

# 3. If profile venv has extra packages, install them in root
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python <package>

# 4. Replace profile copy with symlink
rm -rf ~/.hermes/profiles/<name>/hermes-agent
ln -s ~/.hermes/hermes-agent ~/.hermes/profiles/<name>/hermes-agent

# 5. Verify
hermes --version
ls -la ~/.hermes/profiles/<name>/hermes-agent/venv/bin/hermes
stat -f "%i" ~/.hermes/hermes-agent/
stat -f "%i" ~/.hermes/profiles/<name>/hermes-agent/
# Both should show the same inode number
```

## The Reverse (Removing Root) Is WRONG

Some docs suggest the root `~/.hermes/hermes-agent/` is an unused
stale clone that can be deleted. This is INCORRECT. The root copy
is the CLI backbone. The `hermes` command, gateway launchers, and
MCP server configs all depend on it.

If you want to consolidate, keep root and symlink profiles to it.
Never the reverse.
