# Discord Adapter: Built-in vs Plugin Comparison

Created: May 27, 2026

| | Built-in | Plugin |
|---|---|---|
| **Path** | `gateway/platforms/discord.py` | `plugins/platforms/discord/adapter.py` |
| **Lines** | 5,101 | 6,226 (+22%) |
| **Status** | Active (all 7 bots) | Not enabled |
| **Created** | Original | May 12, 2026 (commit `cc8e5ec2a`) |

## What the Plugin Adds

1. **Standalone cron delivery** — sends Discord messages via REST API without a live gateway. The built-in needs the gateway process running.
2. **Interactive setup wizard** — `hermes setup discord` walks through bot token, allowlist, home channel.
3. **YAML config bridge** (`_apply_yaml_config`) — translates config.yaml keys to env vars internally. Built-in relies on `gateway/config.py`.
4. **ClarifyChoiceView** — Discord UI component for multi-choice clarifications (button pick 1-4).
5. **Self-registration** — `register(ctx)` entry point via platform registry. Built-in uses hardcoded if/elif.
6. **`_define_discord_view_classes()`** — lazy view class factory pattern.

## What's Identical

- Message handling, threading, voice mode
- Channel skill bindings, role-based auth, user allowlists
- auto_thread / skip_thread logic (both patched to same behavior)
- Slash commands, reactions, history backfill

## When to Enable the Plugin

Enable if you need:
- Cron delivery to Discord when the gateway is down
- The interactive setup wizard
- Newer ClarifyChoiceView UI

To enable, add to profile's config.yaml:
```yaml
plugins:
  enabled:
    - hermes-discord
```

Then restart the gateway. The plugin's `register()` takes over — the built-in is bypassed.

**⚠️ If enabled, the plugin file becomes the one to patch** for any adapter changes. The built-in is ignored.

## How to Check Which Is Active

```bash
# Check if plugin is enabled
grep 'hermes-discord' ~/.hermes/profiles/<profile>/config.yaml

# If found under plugins.enabled → plugin is active, patch plugins/adapter.py
# If NOT found → built-in is active, patch gateway/platforms/discord.py
```
