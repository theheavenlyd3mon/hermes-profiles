# Channel ID Reference — Noctis Hub (guild <id>)

**Last updated:** 2026-06-12 (17-profile redesign)

## Categories

| Category ID | Name | Notes |
|---|---|---|
| <id> | Text Channels | Default |
| <id> | Voice Channels | Default |
| <id> | RESEARCH | Renamed from RESEARCHER |
| <id> | CODE | Renamed from CODER |
| <id> | CREATIVE | Renamed from ARCHITECT |
| <id> | KNOWLEDGE | Renamed from SECRETARY |
| <id> | INFRA | Renamed from FOREMAN |
| <id> | FINANCE | Renamed from ORACLE |
| <id> | SECURITY | New (2026-06-12) |

## Text Channels

| Channel ID | Name | Category | Bot | Topic |
|---|---|---|---|---|
| <id> | #your-orchestrator-channel | (none) | senna | Coordinator. Fleet management, routing, scheduling. @Senna for any request. |
| <id> | #engineering | CODE | code | All coding — implementation, debugging, review, testing. @Code for code tasks. |
| <id> | #design-studio | (none) | creative | Design, visual art, image gen, UI/UX, architecture diagrams. @Creative for design work. |
| <id> | #research-lab | RESEARCH | research | Investigation, data gathering, academic research, analysis. @Research for research tasks. |
| <id> | #market-intel | FINANCE | finance | Trading, market analysis, trade signals, portfolio tracking. @Finance for market tasks. |
| <id> | #security-ops | SECURITY | security | Security audits, vulnerability management, compliance, red+blue team. @Security for security tasks. |
| <id> | #writing-desk | KNOWLEDGE | knowledge | Obsidian vault, documentation, wiki, note organization. @Knowledge for doc tasks. |
| <id> | #operations | INFRA | infra | DevOps, deployment, CI/CD, containers, networking. @Infra for infra tasks. |
| <id> | #general | Text Channels | (none) | General chat, file drops, quick saves. Not monitored by bots. |
| <id> | #architecture | CREATIVE | (security bot lingering) | NEEDS MANUAL DELETE — bot token reuse from architect means security bot still has access. User must remove in Discord. |

## Pending Cleanup

| Channel ID | Name | Issue | Action |
|---|---|---|---|
| <id> | #architecture | Security bot reused architect's token, still linked here | User deletes channel in Discord (no agent-side CLI for channel management) |
