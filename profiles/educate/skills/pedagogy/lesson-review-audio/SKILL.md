---
name: lesson-review-audio
description: Use when reviewing a past lesson to read aloud via TTS.
version: 1.0.0
platforms: [macos]
metadata:
  hermes:
    tags: [tts, pedagogy, audio, review, read-aloud]
    category: pedagogy
---

# Lesson Review + Read-Aloud

Revisit a previous lesson/session, verify it's still current, update the artifact, then read it aloud via TTS while the user works hands-free.

## When to Use

- User says "revisit/review a previous topic" or "read that lesson to me"
- User wants audio playback of educational material while they work
- A saved lesson/guide may be stale and needs refresh + narration

## Workflow

### Step 1 — Select the topic
- `session_search()` (no args) to browse recent sessions, or `session_search(query=...)` if the user named a topic.
- Present candidates via `clarify` (title + date + one-line hook each).
- Read the chosen material fully: `read_file` for saved artifacts, `session_search(session_id=..., around_message_id=...)` scrolling for chat-only lessons.

### Step 2 — Scope the listen
Ask via `clarify` how much to read: full / core-sections-only / core-plus-changes. This drives narration length (~160 wpm → minutes = words ÷ 160) and update depth.

### Step 3 — Verify currency (the differentiator)
Determine ground truth: source-repo commit (`git log --oneline -1`), live config (`hermes config get ...`), installed version (`hermes --version`).
- **Large document (5+ sections):** parallel `delegate_task` auditors — one per section cluster, each given an explicit claims list and told to answer CONFIRMED/STALE/CHANGED with `file:line` evidence.
- **Small document:** direct `execute_code` batches of ripgrep/sed checks.
- **Critical:** auditor summaries are SELF-REPORTS and auditors can be interrupted at the write-up stage. Always close gaps with your own direct source checks before trusting the audit. Live transcripts sit under `cache/delegation/live/<id>/task-N.log`.

### Step 4 — Update the lesson file
Rewrite the artifact: fix every stale claim, add new features, refresh the footer (date, version/commit, provider, model). Lead the user-facing summary with a "guide says X → actually Y" table.

### Step 5 — Choose the TTS provider (user's choice each time)
Check availability FIRST, then offer via `clarify`:

```bash
# API keys (presence only — never print values)
for k in ELEVENLABS_API_KEY OPENAI_API_KEY GEMINI_API_KEY XAI_API_KEY; do
  grep -q "$k" ~/.hermes/.env 2>/dev/null && echo "$k: PRESENT" || echo "$k: absent"
done
# Tooling
which edge-tts || pip3 list 2>/dev/null | grep -i edge-tts
```

| Provider | Cost | Quality | Voice examples | Notes |
|----------|------|---------|----------------|-------|
| `edge` (default) | Free, no key | Good neural | `en-US-AriaNeural` (news/narrator), `en-US-GuyNeural`, `en-US-JennyNeural` | `pip3 install edge-tts --break-system-packages` if missing |
| `openai` | Paid | High | `alloy`, `nova`, `shimmer`, `echo`, `sage`, `amber` | Needs OPENAI_API_KEY (check ~/.hermes/.env); use curl, not the python module |
| `elevenlabs` | Paid | Best | voice_id from config/env (`ELEVENLABS_VOICE_ID`) | Needs ELEVENLABS_API_KEY; use curl |
| `say` | Free offline | Robotic | `say -v '?' \| grep en_US` | Zero-dependency fallback |

**Pitfall:** the Hermes config `tts.provider` says nothing about what's callable from system Python — check keys/modules, not config. In this environment config says openai but the `openai` python module is absent; curl-based recipes work regardless.

### Step 6 — Write the narration script
Rewrite the updated lesson as SPOKEN PROSE (never read markdown aloud):
- No tables, code blocks, or symbols — expand them: `→` = "to", `~/.hermes` = "dot hermes", `A | B` = "A or B"
- Pronounce paths/commands in words so the listener can reconstruct them
- Add section intros ("Section two. Subagent delegation.") and a sign-off
- Front-load the "what changed since last time" summary
- Target: words ÷ 160 ≈ minutes; share the estimate before playing

### Step 7 — Play
```bash
python3 <skill-dir>/scripts/tts_read.py /tmp/narration.txt --provider edge --voice en-US-AriaNeural
```
- Run with `terminal(background=true, notify_on_complete=true)` — playback blocks for the full duration.
- The script chunks at ~3500 chars, synthesizes per provider, plays sequentially via `afplay`, prints progress, retries transient failures once.
- Before a long play, always do a one-line test: `edge-tts --voice V --text "Testing." --write-media /tmp/t.mp3 && afplay /tmp/t.mp3`

### Step 8 — Wrap up
- Session recap table (topic, audit findings, fixes, audio duration).
- Optional comprehension check: 3 recall questions with answers.
- Archive: copy narration + mp3s to `~/.hermes/profiles/<profile>/lessons/<date>-<topic>/` if the user may want a replay.

## Pitfalls

- **pip vs pip3:** macOS system Python has no `pip` alias — use `pip3 install --break-system-packages`.
- **edge-tts long-text failures:** keep chunks ≤ 3500 chars.
- **afplay is macOS-only**; this skill targets macOS.
- **/tmp is ephemeral:** persist anything reusable into the skill or profile dirs.
- **Subagent interruptions** during long audits are common — transcripts + direct follow-up checks close the gap.
- **Never read raw markdown aloud** — tables and symbols are gibberish in audio.

## Verification

1. Test-line playback confirmed before the long play (user hears it).
2. Narration word count → duration estimate shared with user.
3. Background process launched; first "▶ part 1/N playing" line in output.
4. Completion notification shows all N parts played, exit code 0.
