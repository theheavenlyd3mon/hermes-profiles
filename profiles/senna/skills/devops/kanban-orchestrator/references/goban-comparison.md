# Goban — Comparison with Hermes Kanban

Researched 2026-05-10 via [BubblegumTuning/goban](https://github.com/BubblegumTuning/goban) (1 star, 0 forks, 6 days old).

## What It Is

A standalone Kanban server written in Go (Fiber framework), GPLv3. A web app with drag-and-drop UI, REST API, and CLI tools. Designed explicitly as a human+AI collaboration surface with RBAC roles for agents.

## Key Features

- Go backend with Fiber, SQLite or PostgreSQL
- Web UI (Tailwind CSS, SPA with drag-and-drop)
- `goban-cli` (HTTP API client) + `goban-user-cli` (direct DB admin)
- RBAC: HUMAN_ADMIN, OVERSEER_AI, NORMAL_AI
- Boards named "human-to-ai" / "ai-to-human" convention
- Bearer token auth (API) + JWT session auth (web UI)
- SSE for real-time updates
- Subtasks, comments, priorities, labels, audit trail
- Activity logging (partial — some event types defined but not emitted)

## Comparison Matrix

| Dimension | Hermes Kanban | Goban |
|---|---|---|
| Worker spawning | Auto by dispatcher (spawns profile workers) | Manual — agent polls API or external scheduler |
| Task dependencies | `parents` list → auto-promotion on completion | Subtasks only — no cross-task dependency graph |
| Workspace isolation | scratch/dir/worktree per task, GC'd | No concept |
| Architecture | Embedded in gateway (no extra server) | Standalone HTTP server (port 8080) |
| Web UI | Dashboard (TUI / gateway panels) | Full drag-and-drop SPA |
| Agent integration | Native — kanban-worker skill auto-injected, env vars set | HTTP API — agent must poll and claim via REST |
| Maturity | Shipped, documented, production | 1 star, 6 days old, auth bypasses noted in README |
| DB backends | SQLite | SQLite + PostgreSQL |
| Extra features | — | Includes a Go (board game) engine |

## Assessment: Not a supplement

Goban solves the same problem from the opposite direction. Hermes Kanban is an **orchestration engine** (dispatcher → spawn → work → complete). Goban is a **collaboration surface** (visual board where humans and AIs both see and move cards). There is no integration point — you'd need to write a bridge.

For the user's setup (11 Hermes profiles, gateway-based dispatcher), Hermes Kanban is already the deeper system. Goban would add a web UI but lose auto-dispatch, workspace isolation, dependency-gated promotion, and native retry/reclaim.
