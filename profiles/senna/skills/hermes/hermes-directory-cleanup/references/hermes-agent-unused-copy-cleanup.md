# ⚠️ DEPRECATED — DO NOT REMOVE ROOT HERMES-AGENT

> **WARNING:** This document previously recommended removing `~/.hermes/hermes-agent/`
> as an "unused copy." That advice is **wrong**. The root hermes-agent is the CLI
> backbone — `~/.local/bin/hermes` hard-codes the path to its venv. Removing it
> breaks the `hermes` command entirely.
>
> The correct consolidation approach is the **reverse**: keep root as canonical,
> symlink profile copies to root. See `hermes-agent-is-cli-backbone.md`.

# Consolidating Profile hermes-agent Copies (Symlink to Root)

## Context

In a multi-profile setup, the root `~/.hermes/hermes-agent/` is the canonical
install. The CLI, some gateways, and MCP server configs all depend on it.

Profile-level copies (e.g. `~/.hermes/profiles/senna/hermes-agent/`) should be
**symlinks to root**, not separate checkouts. This prevents version drift and
saves ~894 MB per copy.

## Why It Exists

- It may be the original install before profiles were set up
- It may be a separate `git clone` for development/testing
- It may have been updated independently (often newer than senna's copy)

## Before Removing — Check Dependencies

MCP servers configured in `~/.hermes/config.yaml` may reference the unused copy's venv:

```bash
grep "hermes/hermes-agent/venv" ~/.hermes/config.yaml
grep "hermes/hermes-agent/venv" ~/.hermes/profiles/*/config.yaml
```

Common MCP dependencies:
- `iknowkungfu-mcp` — from the `iknowkungfu` pip package
- Other custom MCP servers installed only in the unused venv

## Correct Migration Steps (Symlink Profile to Root)

1. **Verify root is at the same or newer commit** as the profile copy:
   ```bash
   cd ~/.hermes/hermes-agent && git log --oneline -1
   cd ~/.hermes/profiles/<name>/hermes-agent && git log --oneline -1
   # If profile is newer, update root: cd ~/.hermes/hermes-agent && git checkout <commit>
   ```

2. **Compare venv packages** — install any extras from profile into root:
   ```bash
   diff <(~/.hermes/hermes-agent/venv/bin/python -m pip list --format=freeze | sort) \
        <(~/.hermes/profiles/<name>/hermes-agent/venv/bin/python -m pip list --format=freeze | sort)
   # Install missing packages into root venv
   uv pip install --python ~/.hermes/hermes-agent/venv/bin/python <package>
   ```

3. **Replace profile copy with symlink**:
   ```bash
   rm -rf ~/.hermes/profiles/<name>/hermes-agent
   ln -s ~/.hermes/hermes-agent ~/.hermes/profiles/<name>/hermes-agent
   ```

4. **Verify**:
   ```bash
   hermes --version
   stat -f "%i" ~/.hermes/hermes-agent/
   stat -f "%i" ~/.hermes/profiles/<name>/hermes-agent/
   # Same inode = correct
   ```

## Pitfalls

- **NEVER remove `~/.hermes/hermes-agent/`** — it's the CLI backbone. The `hermes` command at `~/.local/bin/hermes` hard-codes this path.
- **pip may be missing** — bootstrap with `uv pip install --python <venv>/bin/python pip`
- **Binary paths are absolute** — MCP configs use full paths, not just command names
- **Check both config.yaml files** — root AND profile-level may reference MCP servers
- **After symlink, both paths resolve to same inode** — verify with `stat -f "%i"`
