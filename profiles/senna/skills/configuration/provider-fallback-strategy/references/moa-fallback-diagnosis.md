# MOA (Mixture of Agents) Run Failure — Diagnosis

Observed 2026-07-31. Symptom: user ran a turn with the `council` MOA preset
(banner shows `council via provider moa`), but the reply appeared to come from
somewhere else and the user could not see DeepSeek V4 Flash (a reference model)
work at all.

## The real story (what the logs showed)

1. **MOA presets live in the PROFILE config**, not root:
   `~/.hermes/profiles/<profile>/config.yaml` under `moa:`. A grep of
   `~/.hermes/config.yaml` for `moa` returns nothing. `hermes moa list` reads
   the profile config. The `council` preset here: references
   `deepseek:deepseek-v4-flash` (reasoning_effort: high) + `alibaba:qwen3.8-max-preview`,
   aggregator `kimi-coding:k3`, `degraded_reference_policy: loud`.

2. **Per-session model attribution lives in `state.db`** (SQLite, per profile):
   ```sql
   -- find the session and its ACTUAL model/provider:
   SELECT id, title, model, source,
          datetime(started_at,'unixepoch','localtime') AS started
   FROM sessions
   WHERE started_at > strftime('%s','YYYY-MM-DD')
   ORDER BY started_at DESC;
   -- then read what actually happened in that session:
   SELECT id, role, substr(replace(content, char(10), ' '), 1, 120),
          finish_reason, datetime(timestamp,'unixepoch','localtime') AS ts
   FROM messages WHERE session_id='<session_id>' ORDER BY id;
   ```

3. **The per-profile agent log is NOT `~/.hermes/logs/agent.log`** — that one
   is the default profile's. For a named profile the log is at
   `~/.hermes/profiles/<profile>/logs/agent.log`.

4. **Log signatures to look for, in order:**
   - `Auxiliary moa_reference: using deepseek (deepseek-v4-flash) at https://api.deepseek.com` — reference SELECTED (aux client created)
   - `Auxiliary moa_aggregator: using kimi-coding (k3)` — aggregator selected
   - `Streaming failed before delivery: 'types.SimpleNamespace' object is not iterable` — **the crash**
   - `API call failed (attempt 1/3) error_type=TypeError ... provider=moa base_url=moa://local model=council` — MOA facade failed
   - `Fallback activated: council → openrouter/free (openrouter)` — fallback fired
   - `API call #1: model=openrouter/free provider=openrouter ... latency=409.4s` — what ACTUALLY produced the visible answer

## Root cause

MOA's streaming path (`conversation_loop` `_use_streaming` → MoA facade
`create()` → `_call_prepared_aggregator` → `call_llm(stream=True)`) returned an
SDK-shaped response object (`SimpleNamespace`) where the caller iterated it as a
stream → `TypeError: 'types.SimpleNamespace' object is not iterable`.

- **Not a DeepSeek API failure**: the key is valid and direct DeepSeek calls
  succeed in the same session (later API calls show
  `model=deepseek-v4-flash provider=deepseek`).
- **Reproducible**: identical crash at 11:12:13 and 11:57:10 in two different
  sessions on the same day. Every MOA council run in TUI (which has stream
  consumers) crashes the same way.
- The **fallback target produced the visible answer**, so the configured
  references — including DeepSeek — never delivered anything. "What the user
  saw" ≠ "what was configured".

## Does `hermes update` fix it? — check the gap against the failing files

```bash
cd ~/.hermes/hermes-agent
git fetch origin
git diff --stat HEAD origin/main -- agent/moa_loop.py agent/chat_completion_helpers.py agent/conversation_loop.py
# empty = the gap touches NONE of the MOA files → update is hygiene, NOT a fix
git log --oneline HEAD..origin/main --grep="moa" -i
```

On 2026-07-31: 72 commits behind, but the gap touched zero MOA files. The
SimpleNamespace-tolerance fix that IS upstream (`7b65073dc fix(moa): tolerate
SDK-shaped tool_call entries in _render_tool_calls`) was already local. Verdict:
update anyway for hygiene, but do NOT promise it fixes MOA.

## Workarounds (in order of effort)

1. **Disable streaming**: `display.streaming: false` in profile config.yaml.
   The error handler itself suggests this ("To avoid this delay, set
   display.streaming: false in config.yaml"). MOA then takes the well-tested
   complete-response path and skips the broken stream iterator.
2. **Change the aggregator** away from a provider that returns SDK-shaped
   responses (kimi-coding:k3 was the suspect here) — e.g. an openrouter model.
3. **Patch the code**: make the stream-iteration site in `moa_loop.py`
   tolerate SimpleNamespace-shaped aggregator responses, mirroring
   `_render_tool_calls` (which already tolerates both dict- and
   SimpleNamespace-shaped tool_call entries).

## Verification after a fix attempt

Run one MOA turn (`/moa <prompt>` or set the model to the preset), then check
the per-profile agent.log: no `Streaming failed before delivery`, and each
`Auxiliary moa_reference` line is followed by real per-model `API call` lines
rather than an immediate `Fallback activated`.
