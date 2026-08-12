# Notion Agent Integration Patterns

Reference for wiring Hermes agents to Notion databases. Each pattern includes the database schema (to create in Notion UI) and the agent-side integration.

---

## Pattern 1: Agent Logbook

Cron jobs, kanban workers, and subagents log summaries to a searchable database. One row per session/run.

### Database Schema

Create in Notion UI under any parent page:

| Property | Type | Purpose |
|----------|------|---------|
| Name | Title | Short summary (max ~80 chars) |
| Agent | Select | Options: hermes, kanban-worker, researcher, cron, github, system |
| Type | Select | Options: session, decision, research, task, error, config-change |
| Date | Date | Auto-set to run time |
| Status | Select | Options: completed, pending, failed |
| Tags | Multi-select | Freeform keywords for search |
| Cost | Number | Approximate API spend for the run (USD) |
| Summary | Rich text | Full summary, links, artifacts (property name varies — see below) |

**⚠️ Critical: Always verify property names before writing.** The schema above shows the standard names. The user's actual database may use different names — e.g. `Summary` instead of `Details`, or a custom title column name. Fetch the actual schema before every write:

```bash
source ~/.hermes/.env
DS_ID=$(curl -s "https://api.notion.com/v1/databases/{database_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" | jq -r '.data_sources[0].id')
curl -s "https://api.notion.com/v1/data_sources/$DS_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" | jq '.properties | keys'
```

### Write Entry via curl

```bash
#!/bin/bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "YOUR_DATABASE_ID"},
    "properties": {
      "Name": {"title": [{"text": {"content": "Cron: blogwatcher scan"}}]},
      "Agent": {"select": {"name": "cron"}},
      "Type": {"select": {"name": "task"}},
      "Date": {"date": {"start": "'$(date -u +%Y-%m-%d)'"}},
      "Status": {"select": {"name": "completed"}},
      "Tags": {"multi_select": [{"name": "blogwatcher"}, {"name": "automation"}]},
      "Cost": {"number": 0.04},
      "Summary": {"rich_text": [{"text": {"content": "Scanned 12 feeds. Found 3 new posts. Summarized in Obsidian."}}]}
    }
  }' | jq .
```

**⚠️ Property name note:** The title column is `"Name"` by default in API 2025-09-03. If you named it something else during database creation, use that name instead. Always verify: `curl -s "https://api.notion.com/v1/data_sources/{data_source_id}" | jq '.properties | keys'`.

**Adjust the rich text property name to match.** The user's database may call it `Summary`, `Details`, `Notes`, or something else. The `Summary` key used above is the actual name in the standard Agent Logbook schema — verify before writing.

**Alternative — using data_source_id as parent:** In API 2025-09-03, you can also use `"parent": {"type": "data_source_id", "data_source_id": "..."}` instead of `database_id`. This is the new-style parent reference and works identically for single-source databases.
```

### Wire to Cron

In the cron job's `execute` block (or `post_run` hook), add a step that calls the curl above with the run's summary, agent name, and cost. The cron job already has access to `~/.hermes/.env` for the API key.

### Wire to Kanban Worker

At the end of a kanban task's worker, before returning the final summary, write a log entry. Use `execute_code` to call the Notion API:

```python
from hermes_tools import terminal
import json, os

api_key = os.environ.get("NOTION_API_KEY")
db_id = "YOUR_DATABASE_ID_OR_ENV_VAR"

payload = {
    "parent": {"database_id": db_id},
    "properties": {
        "Name": {"title": [{"text": {"content": task_summary[:80]}}]},
        "Agent": {"select": {"name": "kanban-worker"}},
        "Type": {"select": {"name": "task"}},
        "Date": {"date": {"start": date_today}},
        "Status": {"select": {"name": "completed"}},
        "Cost": {"number": cost},
        "Summary": {"rich_text": [{"text": {"content": full_summary[:2000]}}]}
    }
}

result = terminal(f'''curl -s -X POST "https://api.notion.com/v1/pages" \\\n  -H "Authorization: Bearer {api_key}" \\\n  -H "Notion-Version: 2025-09-03" \\\n  -H "Content-Type: application/json" \\\n  -d '{json.dumps(payload)}' ''')

**Property name check:** The `Summary` key above matches the standard Agent Logbook schema. If the database uses `Details` instead, change the key before running.
```

---

## Pattern 2: Research Landing Zone

Subagent research results are written as structured Notion pages in a dedicated database. Each page = one research topic.

### Database Schema

| Property | Type | Purpose |
|----------|------|---------|
| Name | Title | Research question / topic |
| Source Agent | Select | Which subagent produced it |
| Status | Select | draft, reviewed, archived |
| Tags | Multi-select | Domain keywords |
| Date | Date | When research was done |
| URL | URL | Link to source(s) if applicable |
| Summary | Rich text | Key findings, verdict, recommendation |

### Usage Pattern

When delegating a research task via `delegate_task`, include in the context: "After returning your findings, write them to the Notion Research database. The database ID is X. Use the NOTION_API_KEY from your environment."

The subagent's final step should be a curl POST creating a page with the research title as a heading and the findings as rich text content.

---

## Pattern 3: Decision Log

Auto-log when config changes, model swaps, architecture decisions, or tool swaps occur. Each entry captures what changed, why, and the cost/trade-off impact.

### Database Schema

| Property | Type | Purpose |
|----------|------|---------|
| Name | Title | Summary of the decision |
| Decision Date | Date | When it was made |
| Category | Select | model, provider, architecture, config, tool, workflow |
| Rationale | Rich text | Why — reasoning, context, options considered |
| Cost Impact | Rich text | Pricing diff, tokens saved/lost, performance delta |
| Reversible | Checkbox | Can this be easily undone? |
| Status | Select | active, superseded, reverted |

### When to Log

Trigger on:
- Model/profile swap (`hermes config set profile.model...`)
- Provider change
- Fallback model change
- New cron job created
- Kanban board restructure
- Tool addition/removal
- Significant config change

The agent should log the decision *at the time of change*, before the user moves on.

---

## Pattern 4: Task Inbox

Central inbox where any input (GitHub issue, chat mention, verbal idea, Obsidian note) lands as a task row. Triaged from one place.

### Database Schema

| Property | Type | Purpose |
|----------|------|---------|
| Name | Title | Task description |
| Source | Select | github, chat, notion, obsidian, manual, cron |
| Priority | Select | low, medium, high, urgent |
| Status | Select | inbox, triaged, assigned, in-progress, done |
| Assigned To | Select | me, hermes, kanban, researcher |
| Created | Date | Auto-stamped |
| Tags | Multi-select | Labels for grouping |
| Notes | Rich text | Context, links, attachments |

### Feeding the Inbox

Three paths:
1. **Webhook** — GitHub webhook → Notion worker creates task page
2. **Manual** — User or agent creates entries directly via API
3. **Cron poll** — A cron job checks Obsidian inbox, GitHub issues, etc. and creates rows

---

## Pattern 5: External Agents API (Alpha)

Notion's alpha feature for embedding custom agents inside Notion. Your Hermes agent appears as an @mentionable teammate.

### Status

**Alpha — waitlisted.** Sign up at the External Agents waitlist page. Notion asks for:

- Name, email, workspace ID, user ID
- Role: Software/Agentic Engineer, Platform/DevOps Engineer, Operations/Workflow Manager, Engineering Leader, Founder, or Other
- Which agents you're interested in: Amplitude, Claude, Codex, Console, Cursor, Decagon, Devin, Flora, Recraft, Serval, Warp, or your own
- Whether you want to bring your own in-house agent (YES — relevant for Hermes)
- Top use case description

### API Surface

```
POST /sessions/{id}          — Start a conversation with your agent
POST /sessions/{id}/messages — Send a message to your agent
GET  /sessions/{id}/events   — Watch agent think, call tools, update
```

### Architecture

```
User @mentions your agent in a Notion page
        ↓
Notion sends POST /sessions/{id}/messages to your agent endpoint
        ↓
Your agent receives the message, processes it (reads Notion page, calls tools)
        ↓
Notion polls GET /sessions/{id}/events to show progress in real-time
        ↓
Agent responds → response appears in Notion as a reply
```

Notion handles: review/approval gates, rate limiting, event streaming to the UI.

### Wiring Hermes

Your Hermes gateway would need to expose an HTTP server that implements the three External Agents endpoints. Each session maps to a conversation with the agent. The gateway's existing platform abstraction layer maps naturally — it's a new platform adapter.

---

## Pattern 6: Notion MCP

Notion provides a hosted MCP server that gives AI tools full workspace access via the Model Context Protocol.

### Setup

1. Notion's MCP server is hosted (HTTP transport, not stdio) — uses OAuth for auth
2. Add to `~/.hermes/config.yaml` under `mcp_servers`
3. Requires the `mcp` Python package installed (`pip install mcp`)
4. Tools appear as `mcp_notion_*` in Hermes

### Capabilities

- Create/update/read Notion pages
- Search workspace content
- Manage databases
- Read/write comments
- File operations

See the `native-mcp` skill for full configuration details. This approach is best when you want full workspace access from multiple agents (Claude Code, Cursor, etc.) without managing API keys per agent.

---

## Checklist: Starting from Scratch

When a user wants to set up Notion agent integration for the first time:

1. [ ] Confirm they have a Notion account and workspace
2. [ ] They create an integration at https://notion.so/my-integrations → copy key
3. [ ] Store `NOTION_API_KEY` in `~/.hermes/.env`
4. [ ] **⚠️ Pitfall:** Verify the key is NOT commented out — `grep '^NOTION_API_KEY=' ~/.hermes/.env` should return the line, not `grep '^# NOTION_API_KEY='`. If the key was added by editing a template, it may still be prefixed with `# `. Check and uncomment if needed.
5. [ ] Pick the first use case (start with Agent Logbook — simplest)
6. [ ] Create the database (via Notion UI or via `POST /v1/databases` with `initial_data_source.properties` — see Create a Database in the main SKILL.md)
6. [ ] Share the database with the integration (page menu → Connect to)
7. [ ] Copy the database ID from the URL
8. [ ] Run a test entry via curl
9. [ ] Wire a cron job or kanban worker to write log entries
10. [ ] Verify the entry appears in Notion
11. [ ] Expand to additional patterns as needed
