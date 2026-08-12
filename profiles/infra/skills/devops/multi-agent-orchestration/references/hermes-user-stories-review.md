# Hermes User Stories Review (May 2026)

**Source:** https://hermes-agent.nousresearch.com/docs/user-stories

**Session context:** User asked to review all 237 community-contributed use cases across 15 categories from 11 sources. Used the **Parallel Research Review** pattern (extracted to shared [ADDRESS] → 6 kanban researcher tasks → poll → synthesize).

## Category Breakdown

| Category | Stories | Research Verdict [PERSON_NAME] | 60 | 5 critical finds: dogfooding scale, Skill Factory, 86.8% approval-gate violations, 73% token overhead, self-improving cron |
| Personal Assistant | 40 | 10 high-interest: family WhatsApp, ADHD PM, voice fitness coach, two-tier email pipeline |
| Integrations | 25 | Memory is the emerging battleground; cross-agent memory plugin at 95.2% R@5 |
| Creative | 18 | Research agent blueprint, [PERSON_NAME], autonomous video/game creation |
| Meta & Ecosystem | 18 | Platform maturity signals: Windows installer, ecosystem map, community admin tools |
| Business Ops | 13 | Real revenue: printing factory daily use, $100K automated, 297-day streak |
| Cost Optimization | 11 | $5 VPS playbook, 60-90% token cuts via RTK, smart routing tiers save $40/mo |
| Content Creation | 10 | Voice cloning, auto-documentary, YouTube title optimization |
| Enterprise | 9 | EU AI Act compliance, Vertex AI for GCP, [PERSON_NAME] pod-hop, Higress MCP infra |
| Research | 8 | Daily cross-platform research brief, drug discovery with Hermes, LaTeX TUI rendering [PERSON_NAME] | 8 | QQ, LINE, [ADDRESS] (27 tools), Android app, Discord approval gate for kids |
| Privacy & Self-Hosted | 6 | Edge GPU legal work, Tailscale, security eval patterns, AdGuard |
| General | 6 | Voice accessibility, Spanish guide, blind user addon, [ADDRESS] workshops |
| Trading & Markets | 3 | Polymarket parallel analysis, weather bot, crosschain trading |
| Marketing | 2 | UGC ad studio, Meta Ads Kit |

## Cross-Cutting Themes

1. **Memory is the hottest battleground** — 22k-line custom kernels, cross-agent memory plugins, temporal context graphs, competing memory systems (Mem0, Qdrant, Honcho, Mnemosyne)
2. **Cost optimization drives adoption** — 73% overhead measured, 60-90% token cuts via RTK, smart routing tiers
3. **Self-improvement is proven, not aspirational** — Skill Factory, cron-based skill audit, compile-skills-to-code patterns emerged independently across different users
4. **Real business revenue exists** — printing factory, $100K automated, sales pipelines — not just hobbyist tinkering
5. **Pattern: agents building agents** — [ADDRESS] runs 12 Hermes to build Hermes; multi-agent auto-build loops (plan→code→QA→ship) are the dominant workflow pattern

## Raw Data

The full structured dataset (237 entries with href, source, category, title, description) was saved to `/tmp/hermes-stories-categorized.json` during this session.