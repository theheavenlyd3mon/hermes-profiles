# Gateway Interruption Recovery — Multi-Profile Redesign

When running a long multi-profile redesign via Discord, the gateway can go down mid-work (hermes update, crash, manual shutdown). This documents what to save, where, and how to recover.

## Pre-Restart Save Checklist

Before any gateway-sensitive operation (hermes update, config change, manual restart):

### 1. Filesystem Artifacts (survive restart)
- [ ] All SOUL.md files written to `~/.hermes/profiles/<name>/SOUL.md`
- [ ] Strategy docs written to `~/.hermes/profiles/<coordinator>/cache/documents/`
  - `skill-curation-strategy.md`
  - `implementation-plan.md`
  - Any design decision docs
- [ ] Temp files consolidated (subagents write to scattered locations)

### 2. Memory (survive restart, injected into context)
- [ ] `memory(action='add')` — planning state, task progress, key decisions
- [ ] `mnemosyne_remember()` — same content for shared recall
- [ ] Include: which tasks are complete, which are pending, what decisions are locked vs deferred

### 3. Session State (recoverable via session_search)
- [ ] The session itself is preserved in the session DB
- [ ] But the ACTIVE todo list is NOT — it lives in the gateway's runtime state
- [ ] After restart, use `session_search()` to find the session and `lcm_load_session()` to read it

## Recovery After Gateway Comes Back

1. **Search for the session:** `session_search(query="profile redesign", sort="newest")`
2. **Load the last messages:** `lcm_load_session(session_id=..., limit=20, after_store_id=...)`
3. **Check memory:** Mnemosyne recall for planning state
4. **Check filesystem:** Verify all SOUL.md files and docs are in place
5. **Recreate todo list:** `todo(todos=[...])` from the saved state
6. **Resume from where you left off**

## Key Insight

The Discord session is ephemeral. The artifacts persist:
- Files on disk survive everything
- Mnemosyne/memory survive everything
- Session DB survives everything
- The todo list does NOT survive (runtime only)
- The conversation context does NOT survive (new session = fresh context)

**Always save the todo state to memory before a gateway restart.** The user can say "pick up where we left off" and the new session can reconstruct from memory + files + session_search.

## Recovery From CLI (Not Discord)

When the gateway is down, you can't resume in Discord. Use CLI instead:

1. **Check gateway status:** `hermes gateway status`
2. **Start gateway:** `hermes gateway start`
3. **Verify:** `tail -5 ~/.hermes/profiles/senna/logs/gateway.log`
4. **Resume from CLI** — the user will likely come to CLI first when Discord is down
5. **Load session context:** Use `session_search()` and `lcm_load_session()` to reconstruct the conversation
6. **Present status** — show what was done, what's pending, and offer to continue

**Pitfall: Don't assume the user knows the gateway is down.** They may think "the bot stopped responding" and not realize it's a gateway issue. Check status proactively when they report Discord problems.

## Actual Recovery: 2026-06-12

### What Happened
Gateway went down during Phase 3 (skill installation). User came to CLI and said "we were running a session in discord to clean up everything and then you shut the gateway down."

### Recovery Steps
1. `session_search(query="discord gateway shutdown cleanup")` — found nothing
2. `session_search(query="cleanup profiles memory skills")` — found the Discord session
3. `lcm_load_session(session_id="20260612_112837_01cd879f")` — loaded full conversation
4. Discovered: 9 tasks, 17 SOUL.md files drafted, implementation plan written
5. Verified filesystem: all 17 SOUL.md files at `~/.hermes/profiles/<name>/SOUL.md`
6. Verified strategy docs: `skill-curation-strategy.md` and `implementation-plan.md` in senna cache
7. `hermes gateway start` — restarted gateway
8. `tail -5 ~/.hermes/profiles/senna/logs/gateway.log` — confirmed Discord connected
9. Continued Phase 3 from CLI (skill installation)

### What Survived
- ✅ All 17 SOUL.md files (filesystem)
- ✅ Strategy and implementation docs (filesystem)
- ✅ Planning state (Mnemosyne + legacy memory)
- ✅ Session history (LCM + session DB)

### What Was Lost
- ❌ Todo list (runtime only — had to reconstruct)
- ❌ Conversation context (new session — had to reload from LCM)

### Time to Recover
~5 minutes of searching + loading + verification, then immediate resume.

## Prevention Tips

1. **Save todo state to memory** before any gateway-sensitive operation
2. **Write all drafted files** to filesystem before continuing
3. **Use `memory(action='add')`** to capture planning state
4. **Don't rely on conversation context** — it's ephemeral
5. **Check `hermes gateway status`** before starting long operations
