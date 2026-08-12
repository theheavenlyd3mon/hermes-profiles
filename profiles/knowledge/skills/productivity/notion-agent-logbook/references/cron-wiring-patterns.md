# Cron Job Notion Wiring Patterns

Learned patterns from wiring 9 Hermes cron jobs to log to Notion databases.

## Core Pattern

For every LLM-driven cron job that should log to Notion:

1. **Attach the relevant notion-* skill(s)** to the job via `cronjob(action='update', skills=[...])` so the agent has the curl commands available
2. **Append a self-contained logging instruction** to the job's prompt that includes:
   - The database ID
   - The specific properties to set with example values
   - A reminder to use `NOTION_API_KEY` from environment

Example snippet for any cron prompt:

> After finishing, log to the Notion Agent Logbook (database_id: 9dc914a6-6736-40af-a0b9-d1af9fc5e8a1). Name="Task name: [date]", Agent="cron", Type="task", Date=today, Status="completed", Tags=["keyword"], Summary=what was done. Use NOTION_API_KEY from your environment.

## Multi-Database Pattern

When a single cron job should log to multiple databases (e.g. Agent Logbook + Research Vault + Cost Tracker), attach all relevant skills and include separate logging instructions for each. Example from overnight-wiki-research:

```
After finishing, log to three Notion databases:

1. Agent Logbook (db: xxx): ...
2. Research Vault (db: yyy): ...
3. Cost Tracker (db: zzz): ...
```

## Skills to Attach by Database

| Target Database | Skill to attach |
|----------------|----------------|
| Agent Logbook | `notion-agent-logbook` |
| Decision Log | `notion-decision-log` |
| Research Vault | `notion-research-zone` |
| Cost Tracker | `notion-cost-tracker` |
| Cron Registry | `notion-cron-registry` |
| Task Inbox | `notion-task-inbox` |
| Agent Inventory | `notion-agent-inventory` |

## Env Var Availability

The cron job sandbox does NOT have the user's `.env` sourced by default. Use `NOTION_API_KEY` from the environment. The key is stored at `~/.hermes/.env` on line 430. Terminal sessions inside the profile sandbox have `HOME=~/.hermes/profiles/senna/home` so sourcing `~/.hermes/.env` won't work — use absolute path: `source ~/.hermes/.env`.

## Working Implementation Pattern

For cron jobs that log via `execute_code` (the preferred pattern for agent-driven runs), see `references/cron-log-execute-code-pattern.md`. It covers:

- Schema fetch via temp Python script (avoids the piped-`python3 -c` silent-output problem)
- Log write via JSON payload file + `curl -d @/tmp/payload.json`
- Schema reference for the Agent Logbook database
- Assertion-based verification of the Notion API response
