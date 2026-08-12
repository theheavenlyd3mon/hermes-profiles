# Worked Example: awesome-llm-apps Deep Dive

This reference documents the research approach used in a session evaluating
Shubhamsaboo/awesome-llm-apps (109k stars, 100+ templates).

## Navigation Techniques Used

### Finding subdirectory contents via web_extract

After reading the top-level README, used `web_extract` on:

```
https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/advanced_ai_agents/multi_agent_apps
```

This returned a directory listing with all subdirectory names, last commit
messages, and dates. More useful than trying each subdirectory's README
individually.

### Handling 404s on GitHub tree views

The README said "MCP Agents" existed, but
`https://github.com/.../tree/main/mcp_agents` returned 404. The actual
directory was at a different path. Resolution:

1. Searched web for the repo + "MCP agents" to find the correct path
2. Found the Mintlify docs site which had the MCP section under a different
   URL structure

### Discovering external docs sites

The repo's README didn't prominently link to its Mintlify site, but a web
search for the repo name + "MCP agents" surfaced:

```
https://shubhamsaboo-awesome-llm-apps.mintlify.app/
```

Mintlify pages are more structured than GitHub markdown and often have
sidebar navigation that reveals the full document tree. A page-not-found
on one URL showed the sidebar with all valid paths (e.g., `/rag/overview`,
`/rag/agentic-rag`, `/rag/advanced-techniques`).

### Reading raw markdown directly

Used `raw.githubusercontent.com` URLs to bypass GitHub's HTML rendering:

```
https://raw.githubusercontent.com/Shubhamsaboo/awesome-llm-apps/main/advanced_ai_agents/multi_agent_apps/devpulse_ai/README.md
```

This returns clean markdown without the GitHub page chrome, truncation, or
login wall.

## Key Patterns Discovered

1. **DevPulseAI architecture pattern** — agents only for reasoning tasks;
   deterministic operations are utilities. Clean separation of concerns
   with per-agent model tiering.

2. **Self-improving skills loop** — Executor → Analyst → Mutator with
   keep/revert. Same agentskills.io spec we use. The three-role pattern
   (run+score, diagnose, fix) is portable beyond the ADK dependency.

3. **Agentic RAG with structured routing** — Pydantic `RouteQuery` model
   routes between `vectorstore` and `web_search`. Clean guardrail pattern.

## Relevance Scoring for Our Stack

| Finding | Relevance | Why |
|---------|-----------|-----|
| DevPulseAI architecture | High | Directly applicable to agent team design |
| Self-improving skills loop | High | 900+ skills; optimization is a gap |
| MCP server configs | Medium | Hermes has native MCP client |
| Agentic RAG routing | Medium | Maps to wiki query patterns |
| Voice AI agents | Low | Don't use ADK or Streamlit for voice |
| Fine-tuning templates | Low | Separate workflows exist |
