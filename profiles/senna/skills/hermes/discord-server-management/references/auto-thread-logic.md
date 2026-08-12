# Discord Adapter Auto-Thread Logic

**⚠️ CRITICAL — TWO copies of the Discord adapter exist. Patch the RIGHT one, not both.**

| File | When Used |
|---|---|
| `~/.hermes/profiles/<profile>/hermes-agent/gateway/platforms/discord.py` | **Default** — gateway loads this when no plugin overrides it. This is what all 7 bots use. |
| `~/.hermes/hermes-agent/plugins/platforms/discord/adapter.py` | **Plugin override** — only loaded if a profile adds `hermes-discord` to `plugins.enabled`. Has a `register()` function that takes over from the built-in. Currently NOT enabled for any profile. |

**Decision tree**: Check if any profile has `hermes-discord` in `plugins.enabled` → if yes, patch the plugin → if no, patch the built-in.

When using an **editable install** (`pip install -e .`), the gateway loads from `gateway/platforms/discord.py`, NOT from the plugins directory. Check `direct_url.json` in the venv's site-packages to confirm which source tree the editable install points to:

```bash
cat ~/.hermes/profiles/senna/hermes-agent/venv/lib/python3.*/site-packages/hermes_agent-*.dist-info/direct_url.json
# "url": "file://~/.hermes/profiles/senna/hermes-agent" → gateway/platforms/discord.py is used
```

**Pitfall (May 27, 2026)**: Patched only `plugins/platforms/discord/adapter.py` — bots kept creating threads in free_response_channels because the gateway used `gateway/platforms/discord.py` which had no `is_free_channel` check. Took a full debugging session to find.

**If the plugin is ever enabled** (`hermes-discord` in `plugins.enabled`): The plugin's `register()` function registers a platform entry via `platform_registry.register()`. The gateway checks plugin-registered platforms FIRST — if found, it uses the plugin adapter instead of the built-in. At that point, `plugins/platforms/discord/adapter.py` becomes the file to patch.

---

## Decision Flow (both files, same logic)

Source: `gateway/platforms/discord.py` (lines ~4220-4240) AND `plugins/platforms/discord/adapter.py` (lines ~4580-4600)

**PATCHED** (May 27, 2026): Built-in file patched; plugin already had similar logic.

```python
# Built-in (gateway/platforms/discord.py) — THE FILE THAT MATTERS for all 7 bots:
skip_thread = bool(channel_ids & no_thread_channels) or (is_free_channel and not mention_prefix)

# Plugin (plugins/platforms/discord/adapter.py) — already had this logic, but NOT currently used:
# Same line. Only matters if hermes-discord is added to plugins.enabled.
```

```python
# Auto-thread: when enabled, automatically create a thread for every
# @mention in a text channel so each conversation is isolated (like Slack).
# Messages already inside threads or DMs are unaffected.
auto_threaded_channel = None
if not is_thread and not isinstance(message.channel, discord.DMChannel):
    no_thread_channels_raw = os.getenv("DISCORD_NO_THREAD_CHANNELS", "")
    no_thread_channels = {ch.strip() for ch in no_thread_channels_raw.split(",") if ch.strip()}
    skip_thread = bool(channel_ids & no_thread_channels) or (is_free_channel and not mention_prefix)
    auto_thread = os.getenv("DISCORD_AUTO_THREAD", "true").lower() in {"true", "1", "yes"}
    is_reply_message = getattr(message, "type", None) == discord.MessageType.reply
    if auto_thread and not skip_thread and not is_voice_linked_channel and not is_reply_message:
        thread = await self._auto_create_thread(message)
        if thread:
            parent_channel_id = str(message.channel.id)
            is_thread = True
            thread_id = str(thread.id)
            auto_threaded_channel = thread
            self._threads.mark(thread_id)
```

## Skip Conditions (any ONE skips threading)

1. Already in a thread (`is_thread`)
2. DM channel
3. Channel is in `DISCORD_NO_THREAD_CHANNELS` env var
4. Channel is in `free_response_channels` AND bot was NOT @mentioned
5. Channel is voice-linked
6. Message is a reply (type == MessageType.reply)

## Patch History

**Original** (both files, pre-May 2026):
```python
# gateway/platforms/discord.py had:
skip_thread = bool(channel_ids & no_thread_channels)
# plugins/platforms/discord/adapter.py had:
skip_thread = bool(channel_ids & no_thread_channels) or is_free_channel
```
The built-in (gateway) had NO free_channel check at all — every message created a thread. The plugin version always skipped threads in free channels — even when @mentioned.

**Patched** (May 27, 2026 — built-in patched to match plugin's existing logic):

```python
# Both files now have:
skip_thread = bool(channel_ids & no_thread_channels) or (is_free_channel and not mention_prefix)
```

Free response channels skip threading only when NOT @mentioned. When @mentioned, a thread is created. This supports the multi-bot pattern: speak freely in home channel, create focused threads when specifically addressed.

**Key difference**: The plugin already had the `is_free_channel` check. The built-in had NONE — every message created a thread regardless of free_response_channels. The fix was adding the check to the built-in only.

## Config → Behavior Matrix

| `auto_thread` | `free_response_channels` | `@mentioned` | Behavior |
|---|---|---|---|
| true | includes channel | no | **Direct reply** (no thread) |
| true | includes channel | yes | **Thread created** |
| true | empty | yes | **Thread created** |
| true | empty | no | Ignored (require_mention: true) |
| false | any | any | **Direct reply** (no thread) |

## Key Insight

`free_response_channels` and `no_thread_channels` are **NOT equivalent** for threading purposes after the patch:
- `no_thread_channels` ALWAYS skips threading (regardless of mention)
- `free_response_channels` only skips threading when NOT @mentioned

## Thread Participation Tracking

Once a thread is created, the bot tracks it via `ThreadParticipationTracker`. Follow-up messages in that thread don't require @mention (the bot knows it's participating). This is persisted to disk so it survives restarts.

**However**, with `thread_require_mention: true`, this tracking is overridden — the bot requires @mention even in threads it participated in. This prevents bot-to-bot loops when multiple bots share a thread.

## `thread_require_mention` Behavior

Source: `adapter.py` line ~3712

```python
def _discord_thread_require_mention(self) -> bool:
    configured = self.config.extra.get("thread_require_mention")
    if configured is not None:
        if isinstance(configured, str):
            return configured.lower() not in {"false", "0", "no", "off"}
        return bool(configured)
    return os.getenv("DISCORD_THREAD_REQUIRE_MENTION", "false").lower() in {"true", "1", "yes", "on"}
```

When `thread_require_mention: true`:
- Follow-up messages in a bot's thread REQUIRE @mention
- Prevents bot-to-bot loops (Bot A creates thread → Bot B responds → Bot A responds to Bot B → infinite loop)
- Recommended for multi-bot setups where threads may involve multiple bots

When `thread_require_mention: false` (default):
- Follow-up messages in a bot's thread do NOT require @mention
- Bot responds to all messages in threads it participated in
- Fine for single-bot setups

## Debugging: Finding the Right Source File in Editable Installs

When a patch to a hermes-agent source file has no effect, the file you edited may not be the one the gateway loads. This is a general pattern for any hermes-agent editable install:

```bash
# Step 1: Find which source tree the editable install points to
cat ~/.hermes/profiles/senna/hermes-agent/venv/lib/python3.*/site-packages/hermes_agent-*.dist-info/direct_url.json
# → {"url": "file://~/.hermes/profiles/senna/hermes-agent", ...}

# Step 2: The source tree is ~/.hermes/profiles/senna/hermes-agent/
# Plugins are at <source-tree>/plugins/platforms/<name>/adapter.py
# Built-in adapters are at <source-tree>/gateway/platforms/<name>.py

# Step 3: Check if a plugin is registered (overrides built-in)
grep 'hermes-<platform>' ~/.hermes/profiles/<profile>/config.yaml
# If found under plugins.enabled → patch the plugin
# If NOT found → patch the built-in

# Step 4: Verify the patch is in the right file
grep -n "your_change" <the-file-you-patched>
```

**Key insight**: There are often TWO copies of platform adapters — one in `plugins/` (newer, feature-rich, opt-in) and one in `gateway/platforms/` (built-in, default). The plugin only overrides the built-in if explicitly enabled in the profile's config. When debugging, always check which one is actually loaded.

| Env Var | Default | Effect |
|---|---|---|
| `DISCORD_AUTO_THREAD` | `true` | Master toggle for auto-threading |
| `DISCORD_NO_THREAD_CHANNELS` | `""` | Comma-separated channel IDs to skip threading (always, even when @mentioned) |
| `DISCORD_THREAD_REQUIRE_MENTION` | `false` | Require @mention inside threads where bot is participating |
