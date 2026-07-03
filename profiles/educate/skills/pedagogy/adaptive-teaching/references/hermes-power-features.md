# Hermes Agent — Power Features Reference

Synthesized from the official Hermes docs during an advanced teaching session (2025-06-26).
Not a full mirror of upstream docs — signal only.

---

## 1. Skills System (Procedural Memory)

Skills = reusable workflows invoked as `/skill-name`.
Location: `~/.hermes/skills/` (profile-specific).

**Progressive disclosure (token-efficient):**
- Level 0: `skills_list()` → names + descriptions only (~3k tokens for all)
- Level 1: `skill_view(name)` → full SKILL.md on demand
- Level 2: `skill_view(name, file_path)` → specific reference/template/script

**`/learn` — create skill from any source**
```
/learn how I just deployed the staging server
/learn the REST client in ~/projects/acme-sdk, focus on auth
/learn https://docs.example.com/api/quickstart
```
Agent reads material, synthesizes, saves as SKILL.md. No hand-writing needed.

**Skill-backed cron:**
```python
cronjob(action="create", skills=["blogwatcher"],
        prompt="Check feeds, summarize new items",
        schedule="0 9 * * *", name="Morning feeds")
```
Skills load in order before the prompt runs.

**Conditional activation:**
Skills can hide/show based on tool availability:
```yaml
fallback_for_toolsets: [web]  # Hide when web toolset is available
requires_toolsets: [terminal]  # Only show when terminal is available
```

---

## 2. Subagent Delegation (Parallel Workers)

Tool: `delegate_task` — spawns isolated child agents with fresh conversations and terminals.

**Single task:**
```python
delegate_task(goal="Fix bug in handlers.py", context="line 47: TypeError...",
              toolsets=["terminal", "file"])
```

**Parallel batch (up to 3 concurrent, configurable):**
```python
delegate_task(tasks=[
    {"goal": "Research topic A", "toolsets": ["web"]},
    {"goal": "Research topic B", "toolsets": ["web"]},
])
```

**Critical rule:** Subagents know NOTHING about the parent conversation. Pass everything in `goal` + `context`.

**Cheaper subagents config:**
```yaml
delegation:
  model: "google/gemini-flash-2.0"
  max_concurrent_children: 5
  max_spawn_depth: 1  # Default — leaf agents can't delegate further
```

**Toolset narrowness → cheaper + faster:**
- Research → `["web"]`
- Code → `["terminal", "file"]`
- Full stack → `["terminal", "file", "web"]`
- Read-only review → `["file"]`

**⚠️ Self-reports, not verified:** Subagent summaries are what the agent *says* it did. For write operations, ask for verifiable handles (paths, exit codes, SHAs) and verify independently.

---

## 3. Scheduled Tasks (Cron)

Single `cronjob` tool manages full lifecycle: create, list, update, pause, resume, remove, run.

**No-agent mode** (zero LLM cost):
```bash
hermes cron create "every 10m" --no-agent --script ~/scripts/ping.sh
```
Script stdout → message. Empty stdout = silent. Non-zero exit = alert.

**Workdir (project-aware cron):**
```bash
hermes cron create "0 9 * * *" "Check PRs" --workdir /home/me/projects/acme
```
Loads AGENTS.md, .cursorrules from that directory. Path must be absolute and exist.

**Chained context:**
```python
cronjob(action="create", schedule="0 */2 * * *", name="collector",
        prompt="Scrape RSS feeds")
cronjob(action="create", schedule="15 */2 * * *", name="summarizer",
        context_from=["collector"],
        prompt="Summarize new articles from collector")
```

**Model pinning:** Jobs snapshot the model at creation. If global default changes later, unpinned jobs **fail closed** (skip run, send alert). Pin explicitly with `model=` on create/update.

**Delivery destinations:** `origin` (current chat), `local` (save only), `all` (fan out), or platform-specific (`telegram:-1001234567890:thread_id`).

---

## 4. Memory & Context Engineering

Two memory stores, both frozen at session start (preserves prompt cache):

| Store | Capacity | Purpose |
|-------|----------|---------|
| USER.md | ~1,375 chars (5-10 entries) | Who the user is — preferences, style, role |
| MEMORY.md | ~2,200 chars (8-15 entries) | Facts — environment, project structure, tool quirks |

**Batch operations** (all changes in one call):
```python
memory(action="add", target="memory",
    operations=[
        {"action": "remove", "old_text": "stale entry substring"},
        {"action": "add", "content": "New relevant fact"},
    ])
```
Use when memory is full — consolidate overlapping entries first.

**Context files:**
- `AGENTS.md` (project root) — architecture, conventions, test patterns
- `SOUL.md` (~/.hermes/) — global personality/tone
- `.cursorrules` + `.cursor/rules/*.mdc` — auto-read, no config

**Prompt caching tip:** Keep system prompt stable (same models, same context files, same memory) for cheaper cache hits on subsequent messages.

**Slash commands:**
- `/compress` — summarize conversation history, free tokens
- `/model` — switch model mid-session
- `/verbose` — cycle tool output visibility (off→new→all→verbose)
- `/title` — name the session (makes session_search useful later)
- `/usage` — check token usage

---

## 5. Tool System Mastery

**`execute_code`** — collapse multi-step pipelines:
```python
from hermes_tools import web_search, terminal, read_file, write_file, search_files, patch
# All in one script — no manual round-trips
```

**Terminal backends:**
```yaml
terminal:
  backend: local    # Default. Also: docker, ssh, modal, daytona, singularity
```
Docker backend = one persistent container per process. State survives `/new`, `/reset`, subagents.

**Desktop automation (computer_use):**
- Background mode — doesn't steal cursor
- Preferred: `capture(mode='som')` → click by numbered element index
- Profile: `app='Safari'` narrows capture to one app
- Never: type secrets, click permission dialogs, or `raise_window=true` without asking

**Windows-specific:** Install via `iex (irm https://hermes-agent.nousresearch.com/install.ps1)`. Docker backend works via Docker Desktop or WSL2. Run `hermes doctor` for health check.

---

## 6. Subagent context = everything

Most common mistake: passing minimal `goal` with no `context`.

| Wrong | Right |
|-------|-------|
| `goal="Fix the error"` | `goal="Fix TypeError in api/handlers.py:47"` with full traceback |
| No file paths | Absolute paths + project structure + test command |
| Generic ask | Specific constraints + expected output format |
