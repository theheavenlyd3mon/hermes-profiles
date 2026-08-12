# Notion Workers Platform Reference

Notion Workers are serverless TypeScript programs that extend Notion. Covers the **other direction** — code running *inside* Notion, not agents accessing Notion from outside.

## What Workers Are

- Small Node.js/TypeScript programs deployed via `ntn deploy worker`
- Hosted by Notion — no servers to manage
- Run in a sandboxed environment with HTTP access, secrets, and OAuth
- Designed to be built with AI coding agents (scaffold, describe what you want, deploy)

## Capabilities

| Capability | What it does | Trigger |
|------------|-------------|---------|
| **Sync** | Pull data from external APIs into Notion databases on a schedule | Cron (default 30m) |
| **Tool** | Custom functions callable by Notion Custom Agents | On-demand (agent calls it) |
| **Webhook** | Receive HTTP events from external services | HTTP POST |

### Workers vs Hermes

| | Notion Workers | Hermes Agent |
|--|---------------|--------------|
| Where it runs | Notion's infrastructure | User's machine |
| What it does | Sync/automate inside Notion | Reasoning + tool orchestration |
| Language | TypeScript/Node.js | Any (via terminal) |
| Scheduling | Built-in cron per sync | Hermes cron system |

## Key Concepts

- **Pacer** — Rate-limits outbound API calls to avoid third-party quotas
- **OAuth** — Handles auth flows for GitHub, Google, etc.
- **Secrets** — `ntn workers env set KEY=val` for secure env vars
- **CLI** — `ntn workers new` (scaffold), `ntn workers deploy` (deploy), `ntn workers webhooks list` (list webhook URLs)

## Example: Data Sync

```typescript
import { Worker, Schema } from "@notionhq/workers";

const worker = new Worker();
const tickets = worker.database("tickets", {
  type: "managed",
  initialTitle: "Support Tickets",
  primaryKeyProperty: "Tickets",
  schema: { properties: {
    "Tickets": Schema.title(),
    "CSAT score": Schema.select([{ name: "Very satisfied" }, ...]),
    "Feature tags": Schema.multiSelect([{ name: "Account access" }, ...]),
  }},
});

worker.sync("ticketsSync", {
  database: tickets,
  execute: async () => ({
    changes: (await zendesk.tickets.list()).map(t => ({
      type: "upsert",
      key: t.id,
      properties: { /* ... */ },
    })),
  }),
});
export default worker;
```

## When to Recommend Workers

Workers are useful when the user wants Notion-native automation that runs regardless of whether their Hermes agent is online. Not a replacement for Hermes — complementary for persistent sync tasks.
